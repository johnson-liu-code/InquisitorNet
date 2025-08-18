
"""
Metrics Job (Phase 2)
---------------------
Aggregates labels from the last N days to compute precision/recall/F1 and
writes a row into `metrics_detector_daily` for the current day.
"""
from __future__ import annotations
from pathlib import Path
import argparse, datetime as dt, sqlite3

def get_conn(db_path: str|Path) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path))

def migrate(conn: sqlite3.Connection, sql_path: str|Path):
    with open(sql_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

def compute_metrics(conn: sqlite3.Connection, since_days: int=7):
    cur = conn.cursor()
    # Count labels since cutoff
    cutoff = (dt.date.today() - dt.timedelta(days=since_days)).isoformat()
    # labels table stores created_at TIMESTAMP default CURRENT_TIMESTAMP; SQLite compares strings lexicographically OK for ISO format.
    cur.execute("SELECT label, COUNT(*) FROM labels WHERE substr(created_at,1,10) >= ? GROUP BY label", (cutoff,))
    counts = {row[0]: int(row[1]) for row in cur.fetchall()}
    tp = counts.get("TP",0); fp = counts.get("FP",0); tn = counts.get("TN",0); fn = counts.get("FN",0)

    precision = tp / (tp + fp) if (tp+fp) else 0.0
    recall    = tp / (tp + fn) if (tp+fn) else 0.0
    f1 = (2*precision*recall)/(precision+recall) if (precision+recall) else 0.0
    return tp, fp, tn, fn, precision, recall, f1

def write_daily(conn: sqlite3.Connection, tp:int, fp:int, tn:int, fn:int, precision:float, recall:float, f1:float):
    day = dt.date.today().isoformat()
    cur = conn.cursor()
    cur.execute("""INSERT OR REPLACE INTO metrics_detector_daily
                   (day, precision, recall, f1, tp, fp, tn, fn)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (day, precision, recall, f1, tp, fp, tn, fn))
    conn.commit()

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="inquisitor_net_phase1.db")
    ap.add_argument("--migrations", default="migrations/002_phase2.sql")
    ap.add_argument("--since", type=int, default=7)
    args = ap.parse_args(argv)

    conn = get_conn(args.db)
    migrate(conn, args.migrations)

    tp, fp, tn, fn, precision, recall, f1 = compute_metrics(conn, args.since)
    write_daily(conn, tp, fp, tn, fn, precision, recall, f1)
    print(f"Wrote metrics for today: P={precision:.2f} R={recall:.2f} F1={f1:.2f} (tp={tp}, fp={fp}, tn={tn}, fn={fn})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
