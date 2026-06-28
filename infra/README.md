# infra/

Monitoring stack: Prometheus, node_exporter, cAdvisor, Grafana.

## Quick start

```bash
cd infra/
docker compose up -d
```

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / admin)
- node_exporter: http://localhost:9100
- cAdvisor: http://localhost:8080

Dashboard and datasource are provisioned automatically — no manual setup needed.
