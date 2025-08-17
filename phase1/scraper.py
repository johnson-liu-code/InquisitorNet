from __future__ import annotations
from pathlib import Path
import json, re, time
from typing import Dict, Any, List, Iterable

def regex_list(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p) for p in patterns]

def item_matches(body: str, include: List[re.Pattern], exclude: List[re.Pattern], policy: str='any') -> (bool, List[str]):
    """Check if the item body matches the include/exclude patterns.

    Args:
        body (str): The item body text to check.
        include (List[re.Pattern]): List of regex patterns to include.
        exclude (List[re.Pattern]): List of regex patterns to exclude.
        policy (str, optional): The matching policy ('any' or 'all'). Defaults to 'any'.

    Returns:
        (bool, List[str]): A tuple indicating if the item matches and the list of matching patterns.
    """

    hits = []
    inc_hit = any(p.search(body) for p in include) if include else True
    all_hit = all(p.search(body) for p in include) if include else True
    exc_hit = any(p.search(body) for p in exclude) if exclude else False
    if policy == 'any':
        ok = inc_hit and not exc_hit
    else:
        ok = all_hit and not exc_hit
    if ok:
        for p in include:
            if p.search(body):
                hits.append(p.pattern)
    return ok, hits

def iter_fixtures(fixtures_path: str|Path) -> Iterable[Dict[str, Any]]:
    """Iterate over JSONL fixtures.

    Args:
        fixtures_path (str | Path): Path to the fixtures file.

    Yields:
        Iterable[Dict[str, Any]]: An iterable of JSON objects from the fixtures.
    """
    with open(fixtures_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def run_scraper_to_db(settings, conn):
    """Run the scraper and store results in the database.

    Args:
        settings (_type_): Scraper settings.
        conn (_type_): Database connection object.

    Raises:
        NotImplementedError: If the API mode is not implemented.

    Returns:
        ok (int): The number of items kept.
    """
    from sqlite3 import IntegrityError
    cfg = settings.scraper
    include = regex_list(cfg.get('keywords', {}).get('include', []))
    exclude = regex_list(cfg.get('keywords', {}).get('exclude', []))
    policy = cfg.get('match_policy', 'any')
    mode = settings.subreddits.get('mode', 'fixtures')
    fixtures_path = settings.subreddits.get('fixtures_path', 'fixtures/reddit_sample.jsonl')

    cur = conn.cursor()

    if mode == 'fixtures':
        stream = iter_fixtures(fixtures_path)
    else:
        raise NotImplementedError('API mode not wired in Phase 1 scaffold.')

    kept = 0
    for item in stream:
        body = item.get('body','')
        if any(rule.startswith('len(') for rule in cfg.get('discard_if', [])):
            # Very simple eval for len(body) style conditions
            local_vars = {'body': body}
            for rule in cfg['discard_if']:
                try:
                    if eval(rule, {}, local_vars):
                        body = None
                        break
                except Exception:
                    pass
            if body is None:
                continue

        ok, hits = item_matches(body, include, exclude, policy)
        if not ok:
            continue

        row = (
            item['id'],
            item.get('subreddit',''),
            '[USER-REDACTED]',
            body,
            item.get('created_utc',''),
            item.get('parent_id',''),
            item.get('link_id',''),
            item.get('permalink',''),
            json.dumps(hits),
            json.dumps(item.get('post_meta', {})),
        )
        try:
            cur.execute('''
                INSERT INTO scrape_hits (item_id, subreddit, author_token, body, created_utc, parent_id, link_id, permalink, keywords_hit, post_meta_json)
                VALUES (?,?,?,?,?,?,?,?,?,?);
            ''', row)
            kept += 1
        except IntegrityError:
            pass
    conn.commit()
    return kept
