#!/usr/bin/env bash
# Start N parallel Codex workers on the shared CH01 location-image queue (Draft 02, 27 records).
#   bash run_codex_workers.sh [N=4] [samples|full]
# Each worker is a separate `codex exec` process using Codex's built-in image_gen.
# They coordinate through bg.py (atomic claims), so they never make the same record.
# Logs: output/_logs/W<n>.log (full event log) and W<n>.last.txt (final report).
# Watch progress in another terminal with:  python3 bg.py status [--set samples]
set -euo pipefail

N="${1:-4}"
SET="${2:-full}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$DIR/skills/chandrush-backgrounds/WORKER-PROMPT.md"
LOGS="$DIR/output/_logs"
mkdir -p "$LOGS"

case "$SET" in samples|full) ;; *) echo "second argument must be samples or full" >&2; exit 2 ;; esac
command -v codex >/dev/null || { echo "codex CLI not found on PATH" >&2; exit 2; }

python3 "$DIR/bg.py" check >/dev/null || { echo "bg.py check failed: run it to see why" >&2; exit 1; }

# Default lanes (preferences only; idle workers take any ready job). Samples use no lanes.
LANES=("LB" "TB,KB,HR" "MR" "CP,LS,GT,FS" "" "" "" "")

pids=()
for i in $(seq 1 "$N"); do
  W="W$i"
  PREF=""
  [ "$SET" = "full" ] && PREF="${LANES[$((i-1))]:-}"
  PROMPT="$(sed -e "s/{WORKER}/$W/g" -e "s/{SET}/$SET/g" -e "s/{PREFER}/$PREF/g" \
                -e "s/{ROUTE}/Codex built-in image_gen (view_image every reference first; for mode: edit jobs edit Image 1; copy the savedPath it reports)/g" \
                "$TEMPLATE")"
  echo "starting $W (set=$SET, prefer=${PREF:-any}) -> $LOGS/$W.log"
  codex exec -C "$DIR" --skip-git-repo-check -s workspace-write --approve-for-me \
    -o "$LOGS/$W.last.txt" "$PROMPT" >"$LOGS/$W.log" 2>&1 &
  pids+=("$!")
  sleep 4   # stagger starts so the first claims spread across lanes
done

echo "waiting for ${#pids[@]} workers ..."
fail=0
for pid in "${pids[@]}"; do wait "$pid" || fail=1; done
python3 "$DIR/bg.py" status --set "$SET"
[ "$fail" = 0 ] || echo "one or more workers exited with an error: see $LOGS" >&2
echo "If ready jobs remain, run this script again. When done: python3 bg.py sheet${SET:+ --set $SET}"
