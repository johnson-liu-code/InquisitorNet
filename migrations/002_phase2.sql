
-- Policy gate results
CREATE TABLE IF NOT EXISTS policy_checks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  draft_scope TEXT,
  draft_text TEXT,
  allow BOOLEAN,
  flags TEXT,         -- JSON string array
  reasons TEXT,
  raw_match TEXT,     -- JSON object of check_id -> [matches]
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Labeling
CREATE TABLE IF NOT EXISTS labels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id TEXT NOT NULL,
  label TEXT CHECK (label IN ('TP','FP','TN','FN')),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Metrics aggregates
CREATE TABLE IF NOT EXISTS metrics_detector_daily (
  day TEXT PRIMARY KEY,     -- ISO date string YYYY-MM-DD
  precision REAL, recall REAL, f1 REAL,
  tp INTEGER, fp INTEGER, tn INTEGER, fn INTEGER
);
