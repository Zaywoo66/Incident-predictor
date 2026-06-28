# data-generation/ — Notes

## Deviations from contract

None.

## Design decisions

- **Timestamp logging**: Both `stress_scenarios.sh` and `locust_scenarios.py` write to the same `experiments_log.csv` (columns: `start_time, end_time, scenario_type`). The collector uses exact interval matching — a metric row is labeled `incident_label=1` only if its timestamp falls within a stress scenario interval.
- **Normal-traffic exclusion**: Scenarios named `locust_normal` and `cpu_low` are intentionally excluded from incident labeling even though they appear in the experiment log — they represent baseline traffic, not incidents.
- **deploy_flag heuristic**: In absence of a real CI/CD webhook, `deploy_flag=1` is set for timestamps within 2 minutes of a scenario start. This approximates deployment-triggered incidents.
- **Context window**: The collector adds a configurable margin (default: 10 minutes) before the earliest and after the latest experiment to capture normal-operation baseline data around incidents.
