#!/usr/bin/env bash
# deploy_scenarios.py — Simulate deployments and log timestamps to experiments_log.csv
#
# Restarts a target container (or simulates restart via sleep) to mimic
# a deployment event. Logs scenario_type=deploy so collector.py can set
# deploy_flag=1 for the corresponding interval.
#
# Usage:
#   ./deploy_scenarios.sh [EXPERIMENTS_LOG] [CONTAINER_NAME]
#
# Environment / defaults:
#   EXPERIMENTS_LOG  — path to CSV log (default: data/raw/experiments_log.csv)
#   TARGET_CONTAINER — container to restart (default: target-service)

set -euo pipefail

EXPERIMENTS_LOG="${1:-${EXPERIMENTS_LOG:-data/raw/experiments_log.csv}}"
TARGET_CONTAINER="${2:-${TARGET_CONTAINER:-target-service}}"

mkdir -p "$(dirname "$EXPERIMENTS_LOG")"

# Write CSV header if file does not exist
if [ ! -f "$EXPERIMENTS_LOG" ]; then
    echo "start_time,end_time,scenario_type" > "$EXPERIMENTS_LOG"
fi

log_deploy() {
    local deploy_type="$1"
    local start_time
    start_time="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    echo "[*] Starting deploy scenario: $deploy_type at $start_time"

    if docker inspect "$TARGET_CONTAINER" > /dev/null 2>&1; then
        docker restart "$TARGET_CONTAINER"
        echo "[*] Container $TARGET_CONTAINER restarted"
    else
        echo "[*] Container $TARGET_CONTAINER not found — simulating restart with 10s sleep"
        sleep 10
    fi

    # Wait for service to stabilize
    sleep 5

    local end_time
    end_time="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    # Atomic append via flock
    (
        flock -x 200
        echo "$start_time,$end_time,$deploy_type" >> "$EXPERIMENTS_LOG"
    ) 200>"${EXPERIMENTS_LOG}.lock"

    echo "[*] Finished deploy scenario: $deploy_type at $end_time"
}

# --- Deploy scenario 1: simple restart ---
log_deploy "deploy_restart"

echo "[*] Cooldown 60s before next deploy..."
sleep 60

# --- Deploy scenario 2: rolling restart (simulate version bump) ---
log_deploy "deploy_rolling"

echo "[*] Cooldown 60s..."
sleep 60

# --- Deploy scenario 3: restart under load (most realistic incident trigger) ---
log_deploy "deploy_under_load"

echo ""
echo "[*] All deploy scenarios complete. Log: $EXPERIMENTS_LOG"
