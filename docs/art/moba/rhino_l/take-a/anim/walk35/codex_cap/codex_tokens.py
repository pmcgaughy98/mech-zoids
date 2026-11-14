"""Prints a Codex rollout's running token count the way `codex exec` reports "tokens used": input - cached + output."""
import json
import sys

last = None
with open(sys.argv[1], encoding="utf8") as fh:
    for line in fh:
        try:
            p = json.loads(line).get("payload", {})
        except ValueError:
            continue
        if p.get("type") == "token_count" and p.get("info"):
            last = p["info"]["total_token_usage"]
print(0 if not last else last["input_tokens"] - last.get("cached_input_tokens", 0) + last["output_tokens"])
