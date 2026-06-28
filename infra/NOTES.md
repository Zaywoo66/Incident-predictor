# infra/ — Notes

## Deviations from contract

None.

## Notes for downstream modules

- Docker network `incident-net` is created by `infra/docker-compose.yml`. Other modules should reference it as `external: true`.
- Prometheus datasource UID in Grafana is `prometheus` — use this if referencing from other dashboards.
- cAdvisor mounts host paths (`/`, `/var/run`, `/sys`, `/var/lib/docker`) read-only. On Windows with Docker Desktop (WSL2 backend), these map to the Linux VM filesystem, not the Windows host.
- The "latency" panel currently shows network errors as a proxy metric. A proper latency source (e.g., blackbox_exporter) can be added later by the data-generation stage.
