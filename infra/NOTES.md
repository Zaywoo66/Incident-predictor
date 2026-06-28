# infra/ — Notes

## Deviations from contract

None.

## Notes for downstream modules

- Docker network `incident-net` is created by `infra/docker-compose.yml`. Other modules should reference it as `external: true`.
- Prometheus datasource UID in Grafana is `prometheus` — use this if referencing from other dashboards.
- cAdvisor mounts host paths (`/`, `/var/run`, `/sys`, `/var/lib/docker`) read-only. On Windows with Docker Desktop (WSL2 backend), these map to the Linux VM filesystem, not the Windows host.
- The "latency" panel currently shows network errors as a proxy metric. A proper latency source (e.g., blackbox_exporter) can be added later by the data-generation stage.

## Static verification — 2026-06-28

1. `docker compose config --quiet` — OK, YAML valid
2. Image pins match ARCHITECTURE.md — OK (v2.53.0, 11.1.0, v1.8.1, v0.49.1)
3. `python -m json.tool infra-overview.json` — OK, valid JSON, 7 panels present
4. Named volumes (prometheus_data, grafana_data) and network (incident-net) — OK, declared as per contract
