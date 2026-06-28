"""
locust_scenarios.py — Locust load-testing scenarios for generating latency-based incidents.

Runs against a target HTTP endpoint (configurable via --host or TARGET_HOST env var).
Logs scenario timestamps to experiments_log.csv for precise incident labeling.

Usage:
    # As a standalone runner (no locust CLI needed):
    python locust_scenarios.py [--host TARGET_HOST] [--duration SECONDS] [--users NUM] [--log EXPERIMENTS_LOG]

    # Or via locust CLI for interactive mode:
    locust -f locust_scenarios.py --host http://target:8080
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from locust import HttpUser, between, events, task


# ---------------------------------------------------------------------------
# Locust user classes (used by both CLI and programmatic runner)
# ---------------------------------------------------------------------------

class NormalUser(HttpUser):
    """Simulates normal traffic — light, steady requests."""
    wait_time = between(1, 3)
    weight = 1

    @task
    def get_root(self):
        self.client.get("/", name="normal_get")


class SpikeUser(HttpUser):
    """Simulates spike traffic — rapid-fire requests to overload the target."""
    wait_time = between(0.05, 0.2)
    weight = 3

    @task(3)
    def get_root(self):
        self.client.get("/", name="spike_get")

    @task(1)
    def post_data(self):
        self.client.post(
            "/",
            json={"payload": "x" * 1024},
            name="spike_post",
        )


# ---------------------------------------------------------------------------
# Timestamp logging helpers
# ---------------------------------------------------------------------------

def _ensure_log_header(log_path: Path) -> None:
    if not log_path.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["start_time", "end_time", "scenario_type"])


def _append_log(log_path: Path, start: str, end: str, scenario_type: str) -> None:
    try:
        import fcntl
        has_fcntl = True
    except ImportError:
        has_fcntl = False

    with open(log_path, "a", newline="") as f:
        if has_fcntl:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            writer = csv.writer(f)
            writer.writerow([start, end, scenario_type])
            f.flush()
            os.fsync(f.fileno())
        finally:
            if has_fcntl:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Programmatic runner — no locust CLI required
# ---------------------------------------------------------------------------

def run_scenario(
    host: str,
    duration: int,
    users: int,
    scenario_type: str,
    log_path: Path,
) -> None:
    """Run a Locust scenario programmatically and log timestamps."""
    try:
        import gevent
        from locust.env import Environment
        from locust.log import setup_logging
        from locust import stats as locust_stats
    except ImportError:
        print("ERROR: locust and gevent must be installed.", file=sys.stderr)
        sys.exit(1)

    setup_logging("WARNING")

    user_class = SpikeUser if "spike" in scenario_type else NormalUser

    env = Environment(user_classes=[user_class], host=host)
    env.create_local_runner()

    _ensure_log_header(log_path)
    start_ts = _utcnow_iso()
    print(f"[*] Starting locust scenario: {scenario_type} at {start_ts} ({duration}s, {users} users)")

    env.runner.start(users, spawn_rate=users)
    gevent.sleep(duration)
    env.runner.quit()

    end_ts = _utcnow_iso()
    _append_log(log_path, start_ts, end_ts, scenario_type)
    print(f"[*] Finished locust scenario: {scenario_type} at {end_ts}")


def main():
    parser = argparse.ArgumentParser(description="Run locust load scenarios with timestamp logging")
    parser.add_argument("--host", default=os.getenv("TARGET_HOST", "http://localhost:8080"),
                        help="Target host URL (default: $TARGET_HOST or http://localhost:8080)")
    parser.add_argument("--duration", type=int, default=int(os.getenv("DURATION", "60")),
                        help="Duration per scenario in seconds (default: 60)")
    parser.add_argument("--users", type=int, default=int(os.getenv("LOCUST_USERS", "10")),
                        help="Number of concurrent users (default: 10)")
    parser.add_argument("--log", default=os.getenv("EXPERIMENTS_LOG", "data/raw/experiments_log.csv"),
                        help="Path to experiments log CSV")
    args = parser.parse_args()

    log_path = Path(args.log)

    # Scenario 1: normal traffic (negative class)
    run_scenario(args.host, args.duration, max(2, args.users // 5), "locust_normal", log_path)
    print("[*] Cooldown 30s...")
    time.sleep(30)

    # Scenario 2: spike traffic (positive class — incident trigger)
    run_scenario(args.host, args.duration, args.users, "locust_spike", log_path)
    print("[*] Cooldown 30s...")
    time.sleep(30)

    # Scenario 3: heavy spike (positive class — severe incident)
    run_scenario(args.host, args.duration, args.users * 3, "locust_heavy_spike", log_path)

    print(f"\n[*] All locust scenarios complete. Log: {log_path}")


if __name__ == "__main__":
    main()
