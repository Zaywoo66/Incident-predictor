# data-generation/

Generates a labeled dataset of infrastructure metrics for training the incident prediction model.

## Components

- `stress_scenarios.sh` — stress-ng scenarios (CPU, RAM, disk I/O) with timestamp logging
- `locust_scenarios.py` — Locust HTTP load scenarios with timestamp logging
- `collector.py` — pulls metrics from Prometheus, labels by experiment intervals

## Quick start

```bash
# 1. Install Python deps
pip install -r requirements.txt

# 2. Make sure infra/ stack is running (Prometheus on :9090)

# 3. Run stress scenarios (requires stress-ng installed)
bash stress_scenarios.sh

# 4. Run locust scenarios
python locust_scenarios.py --host http://target:8080

# 5. Collect and label metrics
python collector.py --prometheus-url http://localhost:9090
```

Output: `data/raw/metrics_labeled.csv`

## Target service

`target_service/` is a lightweight FastAPI app that Locust sends requests to.
It simulates realistic latency (10–300 ms) and CPU load.

### Running the target service

| Environment | Host flag for `locust_scenarios.py` |
|---|---|
| **Docker Compose** (recommended) | `--host http://target-service:8080` (container name inside `incident-net`) |
| **Local** (outside Docker) | `--host http://localhost:8081` (mapped port on the host) |

> **Note:** Inside `docker-compose.yml` the host port is `8081` because cAdvisor
> already occupies `8080`. Within the Docker network containers reach the service
> at `target-service:8080`.
