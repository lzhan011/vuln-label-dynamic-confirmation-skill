#!/usr/bin/env bash
# Re-copy the files in references/ from the repository originals and write their origin path and sha256
# into references/SOURCE.json.
# Usage: bash scripts/sync_references.sh   (callable from any directory; never modifies the originals,
# only this skill folder). Assumes the skill folder sits at tasks/skills/<skill>/ inside the repository.
set -euo pipefail
cd "$(dirname "$0")"
SKILL_DIR="$(cd .. && pwd)"
REPO="$(cd ../../../.. && pwd)"             # tasks/skills/<skill>/scripts -> repository root
[ -d "$REPO/tasks/bigvul_reports" ] || { echo "could not locate the repository root: $REPO" >&2; exit 2; }
mkdir -p "$SKILL_DIR/references"
NAMES=(BIGVUL_LOOP_PROMPT.md PRIMEVUL_LOOP_PROMPT.md MEGAVUL_LOOP_PROMPT.md DIVERSEVUL_LOOP_PROMPT.md PROJECT_AGENT_BRIEF.md CONFIRMATION_SCOPE.md primevul_outcome_taxonomy.py)
declare -A SRC=(
  [BIGVUL_LOOP_PROMPT.md]="tasks/bigvul_reports/BIGVUL_LOOP_PROMPT.md"
  [PRIMEVUL_LOOP_PROMPT.md]="tasks/primevul_reports/LOOP_PROMPT.md"
  [MEGAVUL_LOOP_PROMPT.md]="tasks/megavul_reports/LOOP_PROMPT.md"
  [DIVERSEVUL_LOOP_PROMPT.md]="tasks/diversevul_reports/LOOP_PROMPT.md"
  [PROJECT_AGENT_BRIEF.md]="tasks/bigvul_reports/evidence_repair/PROJECT_AGENT_BRIEF.md"
  [CONFIRMATION_SCOPE.md]="tasks/bigvul_reports/evidence_repair/CONFIRMATION_SCOPE.md"
  [primevul_outcome_taxonomy.py]="tasks/primevul_reports/primevul_outcome_taxonomy.py"
)
{
  echo "{"
  echo "  \"synced_utc\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"note\": \"references/ are copies of the repository originals; the original wins on any conflict; run scripts/sync_references.sh to re-sync\","
  echo "  \"files\": {"
  first=1
  for name in "${NAMES[@]}"; do
    src="$REPO/${SRC[$name]}"
    [ -f "$src" ] || { echo "original not found: $src" >&2; exit 3; }
    cp -f "$src" "$SKILL_DIR/references/$name"
    sha="$(sha256sum "$src" | cut -d' ' -f1)"
    [ $first -eq 1 ] || echo ","
    first=0
    printf '    "%s": {"source": "%s", "sha256": "%s", "bytes": %s}' "$name" "${SRC[$name]}" "$sha" "$(stat -c %s "$src")"
  done
  echo
  echo "  }"
  echo "}"
} > "$SKILL_DIR/references/SOURCE.json"
echo "synced ${#NAMES[@]} references -> $SKILL_DIR/references/SOURCE.json"
