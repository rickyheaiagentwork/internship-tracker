#!/usr/bin/env bash
# TOAA delegation bridge (hub-and-spoke).
# Only TOAA uses this. Routes ONE task DOWN to a single cohort gateway and
# returns that cohort's reply UP to TOAA. Cohorts have no bridge and no
# knowledge of each other's state dirs, so they can only answer TOAA.
set -euo pipefail

COHORT="${1:-}"
shift || true
TASK="${*:-}"

if [[ -z "$COHORT" || -z "$TASK" ]]; then
  echo "usage: delegate.sh <BEYONDER|OBLIVION|TRIBUNAL|ETERNITY> <task...>" >&2
  exit 2
fi

case "${COHORT^^}" in
  BEYONDER)                                   ID=beyonder; DIR=/home/jarvis/.openclaw-beyonder ;;
  OBLIVION)                                   ID=oblivion; DIR=/home/jarvis/.openclaw-oblivion ;;
  TRIBUNAL|"LIVING TRIBUNAL"|LIVING_TRIBUNAL) ID=tribunal; DIR=/home/jarvis/.openclaw-tribunal ;;
  ETERNITY)                                   ID=eternity; DIR=/home/jarvis/.openclaw-eternity ;;
  *) echo "unknown cohort: $COHORT (allowed: BEYONDER, OBLIVION, TRIBUNAL, ETERNITY)" >&2; exit 3 ;;
esac

exec env OPENCLAW_STATE_DIR="$DIR" \
  OPENCLAW_CONFIG_PATH="$DIR/openclaw.json" \
  HOME=/home/jarvis \
  openclaw agent --agent "$ID" --message "$TASK" --json --timeout 1800
