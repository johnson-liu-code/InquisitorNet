
"""
Policy Gate CLI (Phase 2)
-------------------------
Reads drafts (JSONL) and evaluates them against regex checks configured in
config/policy_gate.yml (or .yaml). Optionally invokes a light LLM (stubbed here)
to produce a brief reason string.

Writes results to the `policy_checks` table.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Tuple
import argparse, json, re, sqlite3, sys

try:
    import yaml
except Exception:
    yaml = None

# ----------------------- Utilities -----------------------

def load_yaml_any(path_yml: Path, path_yaml: Path) -> Dict[str, Any]:
    """Load YAML from .yml or .yaml, preferring .yml if both exist."""
    if yaml is None:
        raise RuntimeError("PyYAML is required but not installed.")
    if path_yml.exists():
        with path_yml.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    if path_yaml.exists():
        with path_yaml.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    raise FileNotFoundError("policy_gate.yml/.yaml not found in config/.")

def compile_checks(conf: Dict[str, Any]) -> List[Tuple[str, str, str, re.Pattern]]:
    """Compile regex checks.
    Returns list of tuples: (id, name, action, pattern)
    """
    checks = []
    for c in conf.get("checks", []):
        pid = c.get("id","UNK")
        name = c.get("name","")
        action = c.get("action","flag")
        pattern = re.compile(c.get("pattern",""), re.IGNORECASE)
        checks.append((pid, name, action, pattern))
    return checks

def run_regex_checks(text: str, checks: List[Tuple[str,str,str,re.Pattern]]) -> Dict[str, List[str]]:
    """Return mapping of check_id -> matched strings (possibly empty list)."""
    hits = {}
    for pid, _name, _action, pat in checks:
        found = [m.group(0) for m in pat.finditer(text)]
        if found:
            hits[pid] = found
    return hits

def llm_reason_stub(allow: bool, flags: List[str]) -> str:
    """Stub for LLM reasoning; keep neutral tone and cite flags."""
    if not flags:
        return "No policy flags matched; allow."
    flag_str = ", ".join(flags)
    if allow:
        return f"Flags present ({flag_str}) but not blocking; allow with flags."
    return f"Blocking checks present ({flag_str}); block."

def decision_from_hits(conf: Dict[str, Any], hits: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
    """Apply decision policy: block_if subset, else allow with flags if any."""
    block_if = set(conf.get("decision_policy", {}).get("block_if", []))
    flags = list(hits.keys())
    if block_if.intersection(hits.keys()):
        return False, flags
    return True, flags

# ----------------------- DB -----------------------

def get_conn(db_path: str|Path) -> sqlite3.Connection:
    db_path = str(db_path)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)

def migrate(conn: sqlite3.Connection, sql_path: str|Path):
    with open(sql_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

def insert_policy_check(conn: sqlite3.Connection, scope: str, text: str, allow: bool, flags: List[str], reasons: str, raw: Dict[str, List[str]]):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO policy_checks (draft_scope, draft_text, allow, flags, reasons, raw_match) VALUES (?,?,?,?,?,?)",
        (scope, text, 1 if allow else 0, json.dumps(flags), reasons, json.dumps(raw))
    )
    conn.commit()

# ----------------------- CLI -----------------------

def main(argv: List[str]|None=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="inquisitor_net_phase1.db")
    ap.add_argument("--config-dir", default="config")
    ap.add_argument("--migrations", default="migrations/002_phase2.sql")
    ap.add_argument("--input", default="fixtures/drafts.jsonl")
    args = ap.parse_args(argv)

    # Load config
    conf = load_yaml_any(Path(args.config_dir)/"policy_gate.yml", Path(args.config_dir)/"policy_gate.yaml")
    checks = compile_checks(conf)

    # DB and migration
    conn = get_conn(args.db)
    migrate(conn, args.migrations)

    # Process drafts
    draft_path = Path(args.input)
    if not draft_path.exists():
        print(f"Input file not found: {draft_path}", file=sys.stderr)
        return 2

    processed = 0
    with draft_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            scope = obj.get("scope","fixture_draft")
            text = obj.get("text","")
            hits = run_regex_checks(text, checks)
            allow, flags = decision_from_hits(conf, hits)
            reasons = llm_reason_stub(allow, flags)  # placeholder for LLM
            insert_policy_check(conn, scope, text, allow, flags, reasons, hits)
            processed += 1
    print(f"Processed {processed} drafts into policy_checks.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
