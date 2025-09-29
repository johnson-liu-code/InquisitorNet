#!/usr/bin/env python3
"""
generate_agent_markdown_report.py

Generates a well-structured Markdown file summarizing inputs and outputs
for Phase 1 (Scraper Agents) and Phase 2 (Detector Agents, Gate Agents)
by reading the existing SQLite database and the policy gate config.

Output structure:

# Phase 1

## Scraper Agents
### ScraperAgent1
```python
# Input:
<scraperagent1_input>
# Output:
<scraperagent1_output>
```

# Phase 2

## Detector Agents
### DetectorAgent1
```python
# Input:
<detectoragent1_input>
# Output:
<detectoragent1_output>
```

## Gate Agents
### GateAgent1
```python
# Input:
<gateagent1_input>
# Output:
<gateagent1_output>
```

Usage:
  python generate_agent_markdown_report.py \
      --db inquisitor_net_phase1.db \
      --config-dir config \
      --out agent_report.md \
      --max 10
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

# Optional: PyYAML for reading policy_gate config (not required to run)
try:
    import yaml  # type: ignore
except Exception:
    yaml = None

# ---------------- Utilities ----------------

def pjson(obj: Any) -> str:
    """Pretty-print Python/JSON-serializable object, falling back to str()."""
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(obj)

def ensure_code_block(s: str) -> str:
    """Wrap a string in a Python code fence for markdown."""
    return f"```python\n{s}\n```"

def parse_json_field(maybe_json: Any) -> Any:
    """Attempt to parse DB JSON fields stored as TEXT."""
    if maybe_json is None:
        return None
    if isinstance(maybe_json, (dict, list)):
        return maybe_json
    try:
        return json.loads(maybe_json)
    except Exception:
        return maybe_json

def load_policy_checks(config_dir: Path) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Load policy gate YAML from config_dir, supporting policy_gate.yml or .yaml.
    Returns (config or None, error string).
    """
    if yaml is None:
        return None, "PyYAML not installed; policy checks omitted."
    for name in ("policy_gate.yml", "policy_gate.yaml"):
        p = config_dir / name
        if p.exists():
            try:
                with p.open("r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}, ""
            except Exception as e:
                return None, f"YAML parse error in {p}: {e}"
    return None, "No policy_gate.yml/.yaml found."

# ---------------- DB helpers ----------------

def open_db(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(str(path))

def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,)
    )
    return cur.fetchone() is not None

def fetchall_dict(conn: sqlite3.Connection, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    cur = conn.execute(query, params)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

# ---------------- Section builders ----------------

def build_phase1_section(conn: sqlite3.Connection, max_items: int) -> Tuple[str, int]:
    """
    Build Phase 1 section with Scraper Agents.
    Uses rows from scrape_hits; approximates scraper input from stored fields
    and shows output as the stored row.
    """
    out: List[str] = ["# Phase 1", "", "## Scraper Agents"]
    total = 0

    if not table_exists(conn, "scrape_hits"):
        out.append("_No data: table `scrape_hits` not found._")
        return "\n".join(out) + "\n", 0

    rows = fetchall_dict(conn, """
        SELECT item_id, subreddit, author_token, body, created_utc,
               parent_id, link_id, permalink, keywords_hit, post_meta_json, inserted_at
        FROM scrape_hits
        ORDER BY inserted_at DESC
        LIMIT ?
    """, (max_items,))

    for i, r in enumerate(rows, 1):
        total += 1
        out.append(f"### ScraperAgent{i}")
        scraper_input = {
            "subreddit": r.get("subreddit"),
            "author_token": r.get("author_token"),
            "body": r.get("body"),
            "created_utc": r.get("created_utc"),
            "parent_id": r.get("parent_id"),
            "link_id": r.get("link_id"),
            "permalink": r.get("permalink"),
        }
        scraper_output = dict(r)
        scraper_output["keywords_hit"] = parse_json_field(scraper_output.get("keywords_hit"))
        scraper_output["post_meta_json"] = parse_json_field(scraper_output.get("post_meta_json"))
        block = f"# Input:\n{pjson(scraper_input)}\n# Output:\n{pjson(scraper_output)}"
        out.append(ensure_code_block(block))

    if total == 0:
        out.append("_No kept items found in `scrape_hits`._")

    return "\n".join(out) + "\n", total

def build_phase2_detector_section(conn: sqlite3.Connection, max_items: int) -> Tuple[str, int]:
    """
    Build Phase 2 Detector Agents from detector_marks and detector_acquittals.
    Shows the original scrape_hit as input and the detector row as output.
    """
    parts: List[str] = ["## Detector Agents"]
    total = 0

    # Marks
    if table_exists(conn, "detector_marks"):
        marks = fetchall_dict(conn, """
            SELECT dm.id, dm.item_id, dm.subreddit, dm.comment_text, dm.post_meta_json,
                   dm.reasoning_for_mark, dm.degree_of_confidence
            FROM detector_marks dm
            ORDER BY dm.id DESC
            LIMIT ?
        """, (max_items,))
        for idx, m in enumerate(marks, 1):
            total += 1
            parts.append(f"### DetectorAgent{idx}")
            src = fetchall_dict(conn, "SELECT * FROM scrape_hits WHERE item_id = ? LIMIT 1", (m["item_id"],))
            detector_input = src[0] if src else {"note": "Original scrape_hit not found for this item_id."}
            if isinstance(detector_input, dict):
                detector_input["keywords_hit"] = parse_json_field(detector_input.get("keywords_hit"))
                detector_input["post_meta_json"] = parse_json_field(detector_input.get("post_meta_json"))
            detector_output = dict(m)
            detector_output["post_meta_json"] = parse_json_field(detector_output.get("post_meta_json"))
            block = f"# Input:\n{pjson(detector_input)}\n# Output:\n{pjson(detector_output)}"
            parts.append(ensure_code_block(block))
    else:
        parts.append("_No data: table `detector_marks` not found._")

    # Acquittals (optional)
    if table_exists(conn, "detector_acquittals"):
        acqs = fetchall_dict(conn, """
            SELECT da.id, da.item_id, da.subreddit, da.comment_text, da.post_meta_json,
                   da.reasoning_for_acquittal, da.degree_of_confidence
            FROM detector_acquittals da
            ORDER BY da.id DESC
            LIMIT ?
        """, (max_items,))
        for j, a in enumerate(acqs, 1):
            total += 1
            parts.append(f"### DetectorAgentAcquittal{j}")
            src = fetchall_dict(conn, "SELECT * FROM scrape_hits WHERE item_id = ? LIMIT 1", (a["item_id"],))
            detector_input = src[0] if src else {"note": "Original scrape_hit not found for this item_id."}
            if isinstance(detector_input, dict):
                detector_input["keywords_hit"] = parse_json_field(detector_input.get("keywords_hit"))
                detector_input["post_meta_json"] = parse_json_field(detector_input.get("post_meta_json"))
            detector_output = dict(a)
            detector_output["post_meta_json"] = parse_json_field(detector_output.get("post_meta_json"))
            block = f"# Input:\n{pjson(detector_input)}\n# Output:\n{pjson(detector_output)}"
            parts.append(ensure_code_block(block))
    else:
        parts.append("_Note: table `detector_acquittals` not found (optional in early data)._")

    if total == 0:
        parts.append("_No detector outputs available; ensure detector ran on scrape_hits._")

    return "\n\n".join(parts) + "\n", total

def build_phase2_gate_section(conn: sqlite3.Connection, config_dir: Path, max_items: int) -> Tuple[str, int]:
    """
    Build Phase 2 Gate Agents from policy_checks.
    Input includes the draft text and current checks from the policy config (if found).
    Output is the stored decision (allow/flags/reasons/raw_match).
    """
    parts: List[str] = ["## Gate Agents"]
    total = 0

    conf, err = load_policy_checks(config_dir)
    checks_list = [] if conf is None else conf.get("checks", [])
    checks_info = {"note": err} if conf is None else {"checks": checks_list}

    if table_exists(conn, "policy_checks"):
        rows = fetchall_dict(conn, """
            SELECT id, draft_scope, draft_text, allow, flags, reasons, raw_match, created_at
            FROM policy_checks
            ORDER BY id DESC
            LIMIT ?
        """, (max_items,))
        for idx, r in enumerate(rows, 1):
            total += 1
            parts.append(f"### GateAgent{idx}")
            gate_input = {
                "checks": checks_info.get("checks", checks_list),
                "draft": {"scope": r.get("draft_scope"), "text": r.get("draft_text")},
            }
            gate_output = {
                "id": r.get("id"),
                "allow": bool(r.get("allow")),
                "flags": parse_json_field(r.get("flags")),
                "reasons": r.get("reasons"),
                "raw_match": parse_json_field(r.get("raw_match")),
                "created_at": r.get("created_at"),
            }
            block = f"# Input:\n{pjson(gate_input)}\n# Output:\n{pjson(gate_output)}"
            parts.append(ensure_code_block(block))
    else:
        parts.append("_No data: table `policy_checks` not found. Run the Policy Gate CLI to generate records._")

    if total == 0:
        parts.append("_No gate outputs available; ensure Phase 2 Policy Gate has been executed._")

    return "\n\n".join(parts) + "\n", total

# ---------------- Main ----------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Generate a Markdown summary of agent inputs/outputs for Phase 1 and Phase 2.")
    ap.add_argument("--db", default="inquisitor_net_phase1.db", help="Path to SQLite DB.")
    ap.add_argument("--config-dir", default="config", help="Path to config directory for policy_gate.yml.")
    ap.add_argument("--out", default="agent_report.md", help="Output markdown file path.")
    ap.add_argument("--max", type=int, default=10, help="Max number of agents to include per section.")
    args = ap.parse_args(argv)

    # Console checklist (conceptual)
    checklist = [
        "Load DB and policy gate config",
        "Collect Phase 1 scraper kept items",
        "Collect Phase 2 detector marks/acquittals",
        "Collect Phase 2 policy gate decisions",
        "Render Markdown with code blocks for inputs/outputs",
        "Validate counts and annotate missing sections"
    ]
    print("\nChecklist:")
    for i, item in enumerate(checklist, 1):
        print(f"  {i}. {item}")

    db_path = Path(args.db)
    config_dir = Path(args.config_dir)
    out_path = Path(args.out)

    if not db_path.exists():
        # Generate skeleton with annotations
        skeleton = [
            "# Phase 1", "",
            "## Scraper Agents",
            "_No database available; cannot display results._",
            "",
            "# Phase 2", "",
            "## Detector Agents",
            "_No database available; cannot display results._",
            "",
            "## Gate Agents",
            "_No database available; cannot display results._",
            "",
            "---",
            "Validation summary: scrapers=0, detectors=0, gate=0",
            "- Note: Database not found; run Phase 1/2 pipelines first.",
        ]
        out_path.write_text("\n".join(skeleton), encoding="utf-8")
        print(f"Report written (skeleton): {out_path}")
        return 2

    conn = open_db(db_path)

    # Build sections
    phase1_md, n_scrapers = build_phase1_section(conn, args.max)
    det_md, n_detectors = build_phase2_detector_section(conn, args.max)
    gate_md, n_gate = build_phase2_gate_section(conn, config_dir, args.max)

    # Assemble full markdown
    md_parts = [phase1_md, "# Phase 2", det_md, gate_md]
    markdown = "\n".join(md_parts)

    # Validation summary
    summary_lines = [
        "---",
        f"Validation summary: scrapers={n_scrapers}, detectors={n_detectors}, gate={n_gate}"
    ]
    if n_scrapers == 0:
        summary_lines.append("- Note: No scraper agents found; ensure Phase 1 pipeline executed.")
    if n_detectors == 0:
        summary_lines.append("- Note: No detector agents found; ensure detector ran on scrape_hits.")
    if n_gate == 0:
        summary_lines.append("- Note: No gate agents found; run policy gate CLI to generate checks.")

    out_path.write_text(markdown + "\n" + "\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"Report written: {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
