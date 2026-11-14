#!/bin/sh
# Runs Codex on rhino walk35 run 1 and stops it if its token count (Codex's "tokens used": input - cached + output,
# checked against walk4's rollout: 116,093) reaches the cap. Preston approved run 1 at 135k-210k.
A="D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim/walk35"
CAP=200000
S="$(cd "$(dirname "$0")" && pwd)"  # this folder (was the session scratchpad)
touch "$A/.start-run1"
cd "C:/Users/pmcga/dev/hollowtide" || exit 1
codex exec --sandbox workspace-write --add-dir "D:\dev\new-mech-rpg\docs\art\moba" --skip-git-repo-check \
  < "$A/brief_run1.txt" > "$A/codex-log-run1.txt" 2>&1 &
CPID=$!
WPID=$(cat /proc/$CPID/winpid 2>/dev/null)
echo "codex pid $CPID win $WPID" > "$A/token-watch-run1.txt"
F=""
while kill -0 $CPID 2>/dev/null; do
  sleep 20
  if [ -z "$F" ]; then
    F=$(find ~/.codex/sessions -name 'rollout-*.jsonl' -newer "$A/.start-run1" -exec grep -l "walk35" {} + 2>/dev/null | head -1)
  fi
  [ -n "$F" ] || continue
  T=$(python "$S/codex_tokens.py" "$F")
  echo "$(date +%T) $T" >> "$A/token-watch-run1.txt"
  if [ "${T:-0}" -ge $CAP ]; then
    echo "$(date +%T) STOP at $T (cap $CAP)" >> "$A/token-watch-run1.txt"
    taskkill //T //F //PID "$WPID" >> "$A/token-watch-run1.txt" 2>&1
    break
  fi
done
wait $CPID
echo "exit $?"
tail -4 "$A/token-watch-run1.txt"
grep -A1 "tokens used" "$A/codex-log-run1.txt" | tail -1
