#!/bin/bash
# Before a commit from a cloud session (Claude, 2026-10-16): files that were CRLF in HEAD and got rewritten with LF
# on Linux go back to CRLF, so the diff shows the real change instead of every line.
#   bash tools/cloud/restore_eol.sh
cd "$(dirname "$0")/../.."
git diff --name-only | while read -r f; do
  [ -f "$f" ] || continue
  if git show "HEAD:$f" 2>/dev/null | head -c 20000 | grep -q $'\r'; then
    if ! head -c 20000 "$f" | grep -q $'\r'; then sed -i 's/$/\r/' "$f"; echo "CRLF restored: $f"; fi
  fi
done
