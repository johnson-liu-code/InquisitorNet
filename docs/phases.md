
# phases.md

## Phase 1: Foundations - Ingestion and Detection (completed)
- **Goals:** Implement Set-1 scrapers and Set-2 detectors; store kept items, marks, and acquittals.
- **Main Features:** YAML-driven configs; fixtures mode; SQLite migrations; CLI runner.
- **Implementation Details:** `phase1/cli.py` orchestrates DB migration, scraper, detector; rules and thresholds live in YAML.
- **Agreed Specifications:** `scrape_hits`, `detector_marks`, `detector_acquittals` tables defined in `migrations/001_init.sql`.
- **Notable Considerations:** Redaction/retention deferred; acquittals optional in early data.

## Phase 2: Detector Calibration and Policy Gate (in progress)
- **Goals:** Improve detector quality; add a dry-run Policy Gate; establish labeling and metrics.
- **Main Features:** `phase2.gate_cli` writes to `policy_checks`; `phase2.label_cli` writes to `labels`; `phase2.metrics_job` writes to `metrics_detector_daily`.
- **Implementation Details:** Regex checks loaded from `config/policy_gate.yml`; decision policy supports `block_if` and flags; migrations in `migrations/002_phase2.sql`.
- **Agreed Specifications:** No public posting; all outputs are internal and auditable.
- **Notable Considerations:** LLM calls are stubbed; SA integration is deferred and toggled via config when available.
