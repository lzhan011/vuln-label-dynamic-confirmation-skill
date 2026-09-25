#!/usr/bin/env bash
# Run the sign-off checkers in one go (SKILL.md section 7).
# Usage: bash scripts/run_checkers.sh <dataset> <project> [ids: a,b,c]
# dataset is bigvul or primevul (they have evidence_repair checkers). megavul and diversevul have no checkers yet;
# for them the script says so explicitly and exits with code 4, which must not be read as a pass.
# Read-only checks; output goes to the terminal and to
# tasks/<dataset>_reports/evidence_repair/_run_checkers_<project>_<timestamp>.log.
set -uo pipefail
cd "$(dirname "$0")"
REPO="$(cd ../../../.. && pwd)"
DATASET="${1:-}"; PROJECT="${2:-}"; IDS="${3:-}"
[ -n "$DATASET" ] && [ -n "$PROJECT" ] || { echo "usage: $0 <dataset> <project> [ids]" >&2; exit 2; }
case "$DATASET" in
  bigvul|primevul) ;;
  megavul|diversevul) echo "$DATASET has no sign-off checkers of its own yet (the BigVul checkers hard-code the dataset path). No checker was run; sign off by deleting the build artifacts and re-running repro.sh, reconcile against the statistics script, and say so in the RUNLOG." >&2; exit 4 ;;
  *) echo "unknown dataset: $DATASET (bigvul|primevul|megavul|diversevul)" >&2; exit 2 ;;
esac
ER="$REPO/tasks/${DATASET}_reports/evidence_repair"
[ -d "$ER" ] || { echo "not found: $ER" >&2; exit 3; }
LOG="$ER/_run_checkers_${PROJECT}_$(date -u +%Y%m%dT%H%M%SZ).log"
cd "$ER"
{
  echo "== run_checkers dataset=$DATASET project=$PROJECT ids=${IDS:-<none>} at $(date -u +%FT%TZ)"
  if [ -n "$IDS" ] && [ -f verify_batch.py ]; then echo "== verify_batch.py --ids $IDS"; python3 verify_batch.py --ids "$IDS"; echo "rc=$?"; fi
  for s in check_loop_prompt_compliance.py check_loop_prompt_FULL.py; do
    if [ -f "$s" ]; then echo "== $s $PROJECT"; python3 "$s" "$PROJECT"; echo "rc=$?"; else echo "== $s does not exist (unreadable)"; fi
  done
  for s in locate_evidence.py recompute_current_repair_audit.py; do
    if [ -f "$s" ]; then echo "== $s"; python3 "$s"; echo "rc=$?"; else echo "== $s does not exist (unreadable)"; fi
  done
} 2>&1 | tee "$LOG"
echo "log: $LOG"
