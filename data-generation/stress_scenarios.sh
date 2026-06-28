#!/usr/bin/env bash
# stress_scenarios.sh — Run stress-ng scenarios and log timestamps to experiments_log.csv
#
# Usage:
#   ./stress_scenarios.sh [EXPERIMENTS_LOG] [DURATION_SEC]
#
# Environment / defaults:
#   EXPERIMENTS_LOG  — path to CSV log (default: data/raw/experiments_log.csv)
#   DURATION         — duration per scenario in seconds (default: 60)

set -euo pipefail

EXPERIMENTS_LOG="${1:-${EXPERIMENTS_LOG:-data/raw/experiments_log.csv}}"
DURATION="${2:-${DURATION:-60}}"

mkdir -p "$(dirname "$EXPERIMENTS_LOG")"

# Write CSV header if file does not exist
if [ ! -f "$EXPERIMENTS_LOG" ]; then
    echo "start_time,end_time,scenario_type" > "$EXPERIMENTS_LOG"
fi

log_scenario() {
    local scenario_type="$1"
    shift
    local start_time
    start_time="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    echo "[*] Starting scenario: $scenario_type at $start_time (${DURATION}s)"
    "$@"

    local end_time
    end_time="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    # Atomic append via flock
    (
        flock -x 200
        echo "$start_time,$end_time,$scenario_type" >> "$EXPERIMENTS_LOG"
    ) 200>"${EXPERIMENTS_LOG}.lock"

    echo "[*] Finished scenario: $scenario_type at $end_time"
}

# --- Scenario 1: CPU stress (all cores, high load) ---
log_scenario "cpu_high" \
    stress-ng --cpu 0 --cpu-load 90 --timeout "${DURATION}s" --metrics-brief

# Cooldown between scenarios
echo "[*] Cooldown 30s..."
sleep 30

# --- Scenario 2: Memory stress (80% of available RAM) ---
log_scenario "memory_high" \
    stress-ng --vm 2 --vm-bytes 80% --timeout "${DURATION}s" --metrics-brief

sleep 30

# --- Scenario 3: Disk I/O stress ---
log_scenario "disk_io" \
    stress-ng --hdd 2 --hdd-bytes 512M --timeout "${DURATION}s" --metrics-brief

sleep 30

# --- Scenario 4: Combined CPU + Memory (simulates realistic incident) ---
log_scenario "cpu_memory_combined" \
    stress-ng --cpu 0 --cpu-load 70 --vm 2 --vm-bytes 60% --timeout "${DURATION}s" --metrics-brief

sleep 30

# --- Scenario 5: Low-intensity CPU (negative class — borderline normal) ---
log_scenario "cpu_low" \
    stress-ng --cpu 1 --cpu-load 20 --timeout "${DURATION}s" --metrics-brief

echo ""
echo "[*] All scenarios complete. Log: $EXPERIMENTS_LOG"
