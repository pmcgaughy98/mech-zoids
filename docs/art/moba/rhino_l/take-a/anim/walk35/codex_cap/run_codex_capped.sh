#!/bin/sh
# Runs Codex on a brief and stops it when its token count (input - cached + output, Codex's "tokens used") reaches CAP.
# Usage: sh run_codex_capped.sh <out dir> <brief file> <log name> <cap> <unique text from the brief, to find its rollout>
A="$1"; BRIEF="$2"; LOG="$3"; CAP="$4"; KEY="$5"
S="$(cd "$(dirname "$0")" && pwd)"  # this folder (was the session scratchpad)
W="$A/token-watch-$LOG.txt"
touch "$A/.start-$LOG"
mkdir -p "D:/dev/_scratch/codex-cwd"  # 2026-11-05: was C:/Users/pmcga/dev/hollowtide, which blocked moving hollowtide to D:
cd "D:/dev/_scratch/codex-cwd" || exit 1  # an empty folder: Codex can write only here and in --add-dir
codex exec --sandbox workspace-write --add-dir "D:\dev\new-mech-rpg\docs\art\moba" --skip-git-repo-check \
  < "$BRIEF" > "$A/codex-log-$LOG.txt" 2>&1 &
CPID=$!
WPID=$(cat /proc/$CPID/winpid 2>/dev/null)
echo "codex pid $CPID win $WPID cap $CAP" > "$W"
F=""
while kill -0 $CPID 2>/dev/null; do
  sleep 20
  if [ -z "$F" ]; then
    F=$(find ~/.codex/sessions -name 'rollout-*.jsonl' -newer "$A/.start-$LOG" -exec grep -l "$KEY" {} + 2>/dev/null | head -1)
  fi
  [ -n "$F" ] || continue
  T=$(python "$S/codex_tokens.py" "$F")
  echo "$(date +%T) $T" >> "$W"
  if [ "${T:-0}" -ge "$CAP" ]; then
    echo "$(date +%T) STOP at $T (cap $CAP)" >> "$W"
    taskkill //T //F //PID "$WPID" >> "$W" 2>&1
    break
  fi
done
wait $CPID
echo "exit $?"
tail -3 "$W"
grep -A1 "tokens used" "$A/codex-log-$LOG.txt" | tail -1
