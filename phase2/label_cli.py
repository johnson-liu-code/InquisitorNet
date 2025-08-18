
"""
Labeling CLI (Phase 2)
----------------------
Samples recent items from detector_marks and near-threshold candidates
to record TP/FP/TN/FN labels for calibration. Interactive mode is optional.

Writes to the `labels` table.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
import argparse, random, sqlite3, sys

def get_conn(db_path: str|Path) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path))

def migrate(conn: sqlite3.Connection, sql_path: str|Path):
    with open(sql_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

def sample_item_ids(conn: sqlite3.Connection, sample: int=20) -> List[Tuple[str, str]]:
    """Return list of (item_id, source_table) from detector_marks (and later near-threshold pool)."""
    cur = conn.cursor()
    ids = [(row[0], "detector_marks") for row in cur.execute("SELECT item_id FROM detector_marks ORDER BY id DESC LIMIT 200")]
    random.shuffle(ids)
    return ids[:sample]

def add_label(conn: sqlite3.Connection, item_id: str, label: str, notes: str=""):
    cur = conn.cursor()
    cur.execute("INSERT INTO labels (item_id, label, notes) VALUES (?,?,?)", (item_id, label, notes))
    conn.commit()

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="inquisitor_net_phase1.db")
    ap.add_argument("--migrations", default="migrations/002_phase2.sql")
    ap.add_argument("--sample", type=int, default=20)
    ap.add_argument("--mode", choices=["interactive","auto-skip"], default="auto-skip",
                    help="interactive prompts for labels; auto-skip only checks wiring.")
    args = ap.parse_args(argv)

    conn = get_conn(args.db)
    migrate(conn, args.migrations)

    items = sample_item_ids(conn, args.sample)
    if not items:
        print("No items available to label. Ensure detector_marks has rows.", file=sys.stderr)
        return 1

    if args.mode == "auto-skip":
        # Just record placeholder TN for wiring test
        for item_id, _src in items:
            add_label(conn, item_id, "TN", "auto-skip placeholder")
        print(f"Wrote {len(items)} placeholder labels (TN).")
        return 0

    # interactive
    print("Press T/F/N/B for TP/FP/TN/FN; ENTER to skip; 'q' to quit.")
    for item_id, source in items:
        print(f"\nItem: {item_id} from {source}")
        key = input("[T]P/[F]P/[N]T/[B]FN/[Enter]=skip/[q]uit: ").strip().lower()
        m = {"t":"TP","f":"FP","n":"TN","b":"FN"}
        if key == "q":
            break
        label = m.get(key)
        if label:
            add_label(conn, item_id, label)
            print(f" -> Labeled {item_id} as {label}")
        else:
            print(" -> Skipped.")
    print("Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())