# InquisitorNet

## Phase-2/3 Updates (scaffolded)
- Policy gate moved to `phase2/gate.py` with CLI wrapper `phase2/gate_cli.py`.
- `config/policy_gate.yml` expanded with IP/PII/safety/OoU checks.
- Labelling CLI now interactive: `python -m phase2.label_cli --db inquisitor_net.db --limit 20`.
- Metrics job parameterized; reports written under `reports/metrics/`. Optional scheduler at `tools/schedule_metrics.py`.
- Phase-3 stubs: `phase3/inquisitor_cli.py`, `phase3/bots/base.py`, and new tables in `migrations/003_phase3.sql`.
