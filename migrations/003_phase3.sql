-- migrations/003_phase3.sql
CREATE TABLE IF NOT EXISTS planned_actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id TEXT NOT NULL,
  type TEXT NOT NULL, -- 'post' | 'dossier' | 'log'
  payload_json TEXT NOT NULL,
  status TEXT DEFAULT 'queued',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dossiers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject_token TEXT,
  markdown TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  visibility TEXT DEFAULT 'private'
);
