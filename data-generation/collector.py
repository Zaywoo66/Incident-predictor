"""
collector.py — Pull metrics from Prometheus and label them using experiments_log.csv.

Reads the experiment log to determine exact stress/load intervals, queries
Prometheus for infrastructure metrics over those periods (plus surrounding
normal-operation windows), and writes a labeled CSV dataset.

Usage:
    python collector.py [OPTIONS]

Options (also settable via environment variables):
    --prometheus-url    PROMETHEUS_URL      (default: http://prometheus:9090)
    --experiments-log   EXPERIMENTS_LOG     (default: data/raw/experiments_log.csv)
    --output            OUTPUT_CSV          (default: data/raw/metrics_labeled.csv)
    --step              STEP_SECONDS        (default: 15)
    --context-minutes   CONTEXT_MINUTES     (default: 10)
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests


# ---------------------------------------------------------------------------
# Prometheus query helpers
# ---------------------------------------------------------------------------

METRIC_QUERIES = {
    "cpu": '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)',
    "ram": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
    "latency": "avg(rate(node_network_transmit_errs_total[1m]))",
    "disk_io": "sum(rate(node_disk_read_bytes_total[1m]) + rate(node_disk_written_bytes_total[1m]))",
    "network_io": "sum(rate(node_network_receive_bytes_total[1m]) + rate(node_network_transmit_bytes_total[1m]))",
}


def query_prometheus_range(
    base_url: str,
    query: str,
    start: datetime,
    end: datetime,
    step: int,
) -> list[dict[str, Any]]:
    """Query Prometheus range API and return list of {timestamp, value} dicts."""
    url = f"{base_url}/api/v1/query_range"
    params = {
        "query": query,
        "start": start.timestamp(),
        "end": end.timestamp(),
        "step": f"{step}s",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    if data["status"] != "success":
        raise RuntimeError(f"Prometheus query failed: {data}")

    results = data["data"]["result"]
    if not results:
        return []

    # Take the first result series (aggregated queries return a single series)
    values = results[0]["values"]
    return [{"timestamp": float(ts), "value": float(val)} for ts, val in values]


# ---------------------------------------------------------------------------
# Experiment log parsing
# ---------------------------------------------------------------------------

def load_experiments_log(log_path: Path) -> pd.DataFrame:
    """Load experiments_log.csv and parse timestamps."""
    df = pd.read_csv(log_path)
    required_cols = {"start_time", "end_time", "scenario_type"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"experiments_log.csv must have columns: {required_cols}, got: {set(df.columns)}")

    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df["end_time"] = pd.to_datetime(df["end_time"], utc=True)
    return df


def is_incident_timestamp(ts: datetime, experiments: pd.DataFrame) -> int:
    """Return 1 if timestamp falls within any experiment interval, 0 otherwise.

    Only scenarios that represent actual stress/incidents are labeled as 1.
    Normal-traffic scenarios (e.g., locust_normal, cpu_low) are excluded.
    """
    normal_scenarios = {"locust_normal", "cpu_low"}
    for _, row in experiments.iterrows():
        if row["scenario_type"] in normal_scenarios:
            continue
        if row["start_time"] <= ts <= row["end_time"]:
            return 1
    return 0


# ---------------------------------------------------------------------------
# Deploy flag heuristic
# ---------------------------------------------------------------------------

def compute_deploy_flag(experiments: pd.DataFrame, timestamps: list[datetime]) -> list[int]:
    """Heuristic: set deploy_flag=1 for timestamps near experiment boundaries.

    In a real setup this would come from a CI/CD webhook. Here we approximate
    it by flagging the 2-minute window around each scenario start.
    """
    flags = []
    for ts in timestamps:
        flag = 0
        for _, row in experiments.iterrows():
            delta = abs((ts - row["start_time"]).total_seconds())
            if delta <= 120:  # within 2 minutes of scenario start
                flag = 1
                break
        flags.append(flag)
    return flags


# ---------------------------------------------------------------------------
# Main collection logic
# ---------------------------------------------------------------------------

def determine_collection_window(
    experiments: pd.DataFrame,
    context_minutes: int,
) -> tuple[datetime, datetime]:
    """Determine the full time window to query: earliest experiment minus context
    to latest experiment plus context."""
    earliest = experiments["start_time"].min()
    latest = experiments["end_time"].max()
    margin = timedelta(minutes=context_minutes)
    return earliest - margin, latest + margin


def collect_metrics(
    prometheus_url: str,
    start: datetime,
    end: datetime,
    step: int,
) -> pd.DataFrame:
    """Query all metrics from Prometheus and build a single DataFrame."""
    all_data: dict[str, dict[float, float]] = {}

    for metric_name, query in METRIC_QUERIES.items():
        print(f"  Querying {metric_name}...")
        points = query_prometheus_range(prometheus_url, query, start, end, step)
        for pt in points:
            ts = pt["timestamp"]
            if ts not in all_data:
                all_data[ts] = {}
            all_data[ts][metric_name] = pt["value"]

    if not all_data:
        print("WARNING: No data returned from Prometheus. Is the exporter running?", file=sys.stderr)
        return pd.DataFrame(columns=["timestamp", "cpu", "ram", "latency", "disk_io", "network_io"])

    rows = []
    for ts in sorted(all_data.keys()):
        row = {"timestamp": ts}
        for metric_name in METRIC_QUERIES:
            row[metric_name] = all_data[ts].get(metric_name, 0.0)
        rows.append(row)

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    return df


def label_dataset(
    metrics_df: pd.DataFrame,
    experiments: pd.DataFrame,
) -> pd.DataFrame:
    """Add incident_label and deploy_flag columns based on experiment timestamps."""
    metrics_df["deploy_flag"] = compute_deploy_flag(
        experiments, metrics_df["timestamp"].tolist()
    )
    metrics_df["incident_label"] = metrics_df["timestamp"].apply(
        lambda ts: is_incident_timestamp(ts, experiments)
    )
    return metrics_df


def main():
    parser = argparse.ArgumentParser(description="Collect Prometheus metrics and label with experiment data")
    parser.add_argument(
        "--prometheus-url",
        default=os.getenv("PROMETHEUS_URL", "http://prometheus:9090"),
        help="Prometheus base URL",
    )
    parser.add_argument(
        "--experiments-log",
        default=os.getenv("EXPERIMENTS_LOG", "data/raw/experiments_log.csv"),
        help="Path to experiments_log.csv",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("OUTPUT_CSV", "data/raw/metrics_labeled.csv"),
        help="Output CSV path",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=int(os.getenv("STEP_SECONDS", "15")),
        help="Query step in seconds (default: 15)",
    )
    parser.add_argument(
        "--context-minutes",
        type=int,
        default=int(os.getenv("CONTEXT_MINUTES", "10")),
        help="Minutes of normal-operation context before/after experiments (default: 10)",
    )
    args = parser.parse_args()

    # 1. Load experiment log
    log_path = Path(args.experiments_log)
    if not log_path.exists():
        print(f"ERROR: Experiments log not found at {log_path}", file=sys.stderr)
        print("Run stress_scenarios.sh and/or locust_scenarios.py first.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Loading experiments log: {log_path}")
    experiments = load_experiments_log(log_path)
    print(f"    Found {len(experiments)} experiment(s)")

    # 2. Determine time window
    start, end = determine_collection_window(experiments, args.context_minutes)
    print(f"[*] Collection window: {start.isoformat()} → {end.isoformat()}")

    # 3. Query Prometheus
    print(f"[*] Querying Prometheus at {args.prometheus_url} (step={args.step}s)")
    metrics_df = collect_metrics(args.prometheus_url, start, end, args.step)
    print(f"    Collected {len(metrics_df)} data points")

    if metrics_df.empty:
        print("ERROR: Empty dataset — cannot produce labeled CSV.", file=sys.stderr)
        sys.exit(1)

    # 4. Label dataset
    print("[*] Labeling dataset from experiment intervals...")
    labeled_df = label_dataset(metrics_df, experiments)

    incident_count = labeled_df["incident_label"].sum()
    normal_count = len(labeled_df) - incident_count
    print(f"    Labels: incident={incident_count}, normal={normal_count}")

    if incident_count == 0 or normal_count == 0:
        print("WARNING: Dataset has only one class — model training may fail.", file=sys.stderr)

    # 5. Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure column order matches contract
    column_order = ["timestamp", "cpu", "ram", "latency", "disk_io", "network_io", "deploy_flag", "incident_label"]
    labeled_df = labeled_df[column_order]
    labeled_df.to_csv(output_path, index=False)
    print(f"[*] Dataset written to {output_path} ({len(labeled_df)} rows)")


if __name__ == "__main__":
    main()
