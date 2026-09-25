#!/usr/bin/env bash
# Statistics and report refresh after confirmations were published; picks the command sequence per dataset
# (the "statistics / report refresh" row of the parameter table in SKILL.md section 10).
# Usage: bash scripts/refresh_stats.sh <dataset>     dataset is bigvul | primevul | megavul | diversevul
# Note: every command walks all sample directories of the dataset; on NFS BigVul takes about 15 minutes and
# MegaVul about 20. Do not run it when nothing was published.
set -euo pipefail
cd "$(dirname "$0")"
REPO="$(cd ../../../.. && pwd)"
DATASET="${1:-}"
[ -n "$DATASET" ] || { echo "usage: $0 <dataset>" >&2; exit 2; }
cd "$REPO"
run() { if [ -f "$1" ]; then echo "== $* ($(date -u +%T))"; python3 "$@"; else echo "== $1 does not exist (unreadable), skipped"; fi; }
case "$DATASET" in
  bigvul)
    run tasks/bigvul_reports/compute_bigvul_dynamic_status_statistics.py
    run tasks/bigvul_reports/refresh_current_bigvul_reports.py
    run tasks/bigvul_reports/compute_bigvul_outcome_taxonomy.py --quiet
    run tasks/bigvul_reports/build_current_dynamic_method_worklist.py
    run tasks/bigvul_reports/evidence_repair/recompute_current_repair_audit.py
    run tasks/bigvul_reports/check_zh_en_report_numbers_agree.py
    SNAP="tasks/bigvul_reports/BIGVUL_LOOP_PROMPT.md" ;;
  primevul)
    run tasks/primevul_reports/compute_primevul_dynamic_status_statistics.py
    run tasks/primevul_reports/refresh_current_primevul_reports.py
    run tasks/primevul_reports/evidence_repair/recompute_current_repair_audit.py
    SNAP="tasks/primevul_reports/LOOP_PROMPT.md" ;;
  megavul)
    run tasks/megavul_reports/compute_megavul_dynamic_status_statistics.py
    run tasks/megavul_reports/refresh_current_megavul_reports.py
    run tasks/megavul_reports/build_megavul_inconclusive_deferred_worklist.py
    SNAP="tasks/megavul_reports/LOOP_PROMPT.md" ;;
  diversevul)
    run tasks/diversevul_reports/compute_diversevul_dynamic_status_statistics.py
    run tasks/diversevul_reports/refresh_current_diversevul_reports.py
    SNAP="tasks/diversevul_reports/LOOP_PROMPT.md" ;;
  *) echo "unknown dataset: $DATASET" >&2; exit 2 ;;
esac
echo "== done ($(date -u +%T)); remember to update the CURRENT-SNAPSHOT block in $SNAP by hand from the new *_dynamic_status_latest.json (the MegaVul refresh script rewrites its own snapshot block automatically)"
