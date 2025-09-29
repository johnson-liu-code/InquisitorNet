#!/usr/bin/env python3
"""
Phase 1 Acceptance Checklist for InquisitorNet

Usage:
  python phase1_acceptance_checklist.py \
      --db inquisitor_net_phase1.db \
      --config-dir config \
      --fixtures-dir fixtures \
      [--verbose]

This script inspects configs and the database created by the Phase 1 pipeline
and prints PASS/FAIL for each Definition of Done (DoD) item.
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

# Optional dependency: PyYAML. The script gracefully degrades if missing.
try:
    import yaml  # type: ignore
except Exception:
    yaml = None

def print_check(n: int, title: str, ok: bool, details: str = ""):
    status = "PASS" if ok else "FAIL"
    line = f"[{n:02d}] {title}: {status}"
    print(line)
    if details:
        for dl in details.strip().splitlines():
            print(f"      {dl}")
    if not ok:
        global overall_ok
        overall_ok = False

def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (table,)
    )
    return cur.fetchone() is not None

def table_has_columns(conn: sqlite3.Connection, table: str, required_cols):
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cur.fetchall()}
    missing = [c for c in required_cols if c not in cols]
    return (len(missing) == 0, missing)

def count_rows(conn: sqlite3.Connection, table: str, where: str = "") -> int:
    q = f"SELECT COUNT(*) FROM {table}"
    if where:
        q += f" WHERE {where}"
    cur = conn.execute(q)
    return int(cur.fetchone()[0])

def get_config_yaml(path: Path):
    if not path.exists():
        return None, f"File not found: {path}"
    if yaml is None:
        return None, "PyYAML not installed; cannot parse YAML."
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f), ""
    except Exception as e:
        return None, f"YAML parse error: {e}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="inquisitor_net_phase1.db")
    parser.add_argument("--config-dir", default="config")
    parser.add_argument("--fixtures-dir", default="fixtures")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    global overall_ok
    overall_ok = True

    config_dir = Path(args.config_dir)
    fixtures_dir = Path(args.fixtures_dir)
    db_path = Path(args.db)

    # ---------- Check 1: subreddits.yml exists & supports allow/avoid & fixtures
    subreddits_yaml = config_dir / "subreddits.yml"
    sub_cfg, sub_err = get_config_yaml(subreddits_yaml)
    ok1 = sub_cfg is not None and all(k in sub_cfg for k in ("allow", "avoid", "mode"))
    det1 = sub_err or ("" if ok1 else "Expect keys: allow, avoid, mode.")
    if ok1 and sub_cfg.get("mode") == "fixtures":
        # If fixtures mode, the path should exist
        fp = sub_cfg.get("fixtures_path") or (fixtures_dir / "reddit_sample.jsonl")
        if not Path(fp).exists():
            ok1 = False
            det1 = f"Fixtures mode set but fixtures file missing: {fp}"
    print_check(1, "Config: subreddits.yml present with allow/avoid/mode", ok1, det1)

    # ---------- Check 2: scraper_rules.yml exists and is loadable
    scr_yaml = config_dir / "scraper_rules.yml"
    scr_cfg, scr_err = get_config_yaml(scr_yaml)
    ok2 = scr_cfg is not None
    print_check(2, "Config: scraper_rules.yml present and parseable", ok2, scr_err)

    # ---------- Check 3: detector_rules.yml exists and is loadable
    det_yaml = config_dir / "detector_rules.yml"
    det_cfg, det_err = get_config_yaml(det_yaml)
    ok3 = det_cfg is not None
    print_check(3, "Config: detector_rules.yml present and parseable", ok3, det_err)

    # ---------- Check 4: Connect to DB (subsequent checks rely on this)
    if not db_path.exists():
        print_check(4, "DB exists (created by pipeline run)", False, f"Missing DB file: {db_path}")
        # If the DB is missing, remaining DB checks will all fail; exit early.
        print("\nNo database to inspect. Run the Phase 1 pipeline first.")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))

    # ---------- Check 5: Scraper pulled data (API or fixtures) → scrape_hits non-empty
    has_scrape_hits_table = table_exists(conn, "scrape_hits")
    rows_scrape = count_rows(conn, "scrape_hits") if has_scrape_hits_table else 0
    ok5 = has_scrape_hits_table and rows_scrape > 0
    det5 = "" if ok5 else "Table scrape_hits missing or empty."
    print_check(5, "Scraper populated scrape_hits (API or fixtures)", ok5, det5)

    # ---------- Check 6: Scraper discarded non-matches (keywords_hit non-empty for kept rows)
    ok6 = False
    det6 = ""
    if has_scrape_hits_table and rows_scrape > 0:
        try:
            # Count rows where keywords_hit looks empty or null
            # In SQLite, JSON likely stored as TEXT; treat '[]' or NULL/empty string as empty.
            q = "SELECT COUNT(*) FROM scrape_hits WHERE keywords_hit IS NULL OR TRIM(keywords_hit) IN ('', '[]')"
            empty_kw = count_rows(conn, "scrape_hits", "keywords_hit IS NULL OR TRIM(keywords_hit) IN ('', '[]')")
            ok6 = (empty_kw == 0)
            det6 = f"{empty_kw} kept rows have empty keywords_hit." if not ok6 else ""
        except Exception as e:
            det6 = f"Could not evaluate keywords_hit: {e}"
            ok6 = False
    else:
        det6 = "scrape_hits table missing or empty; cannot verify discard rule."
        ok6 = False
    print_check(6, "Scraper kept only 'of interest' rows (non-empty keywords_hit)", ok6, det6)

    # ---------- Check 7: scrape_hits has required columns & some non-null fields
    required_cols = [
        "item_id", "subreddit", "author_token", "body", "created_utc",
        "parent_id", "link_id", "permalink", "keywords_hit", "post_meta_json", "inserted_at"
    ]
    ok7 = False
    det7 = ""
    if has_scrape_hits_table:
        has_cols, missing = table_has_columns(conn, "scrape_hits", required_cols)
        ok7 = has_cols
        det7 = "" if ok7 else f"Missing columns: {missing}"
    else:
        det7 = "scrape_hits table missing."
    print_check(7, "scrape_hits schema contains required fields", ok7, det7)

    # ---------- Check 8: Detector processed new scrape_hits (coverage: marks+acquittals == hits)
    has_marks = table_exists(conn, "detector_marks")
    has_acq = table_exists(conn, "detector_acquittals")
    rows_marks = count_rows(conn, "detector_marks") if has_marks else 0
    rows_acq = count_rows(conn, "detector_acquittals") if has_acq else 0
    processed_item_ids = set()
    if has_marks:
        for (iid,) in conn.execute("SELECT item_id FROM detector_marks"):
            processed_item_ids.add(iid)
    if has_acq:
        for (iid,) in conn.execute("SELECT item_id FROM detector_acquittals"):
            processed_item_ids.add(iid)
    total_hits = rows_scrape
    ok8 = (total_hits > 0) and (len(processed_item_ids) == total_hits)
    det8 = f"Processed {len(processed_item_ids)} of {total_hits} scrape_hits." if not ok8 else ""
    print_check(8, "Detector processed all scrape_hits (marks or acquittals)", ok8, det8)

    # ---------- Check 9: Marked items include rationale + confidence in [0,1]
    ok9 = False
    det9 = ""
    if has_marks and rows_marks > 0:
        bad = count_rows(conn, "detector_marks",
                         "reasoning_for_mark IS NULL OR TRIM(reasoning_for_mark)='' "
                         "OR degree_of_confidence IS NULL "
                         "OR degree_of_confidence < 0 OR degree_of_confidence > 1")
        ok9 = (bad == 0)
        det9 = f"{bad} marked rows missing rationale/valid confidence." if not ok9 else ""
    else:
        det9 = "No rows in detector_marks to verify."
        ok9 = False
    print_check(9, "Marked items have rationale and valid confidence", ok9, det9)

    # ---------- Check 10: At least one row exists in detector_marks
    ok10 = has_marks and rows_marks > 0
    det10 = "" if ok10 else "No detector_marks rows found."
    print_check(10, "DB has detector_marks rows", ok10, det10)

    # ---------- Check 11: At least one row exists in detector_acquittals
    ok11 = has_acq and rows_acq > 0
    det11 = "" if ok11 else "No detector_acquittals rows found."
    print_check(11, "DB has detector_acquittals rows", ok11, det11)

    # ---------- Check 12: DB includes placeholders for later phases (tables exist)
    placeholder_tables = [
        "inquisitor_thoughts", "inquisitor_discussions", "inquisitor_actions", "summaries"
    ]
    missing_placeholders = [t for t in placeholder_tables if not table_exists(conn, t)]
    ok12 = (len(missing_placeholders) == 0)
    det12 = "" if ok12 else f"Missing tables: {missing_placeholders}"
    print_check(12, "DB includes placeholders for later phases", ok12, det12)

    # Summary
    print("\nSummary:", "PASS" if overall_ok else "FAIL")
    if not overall_ok:
        print("At least one item failed. Review details above.")

if __name__ == "__main__":
    main()
