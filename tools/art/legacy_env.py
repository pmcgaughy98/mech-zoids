"""Prints `export K=V` lines for a machine's Legacy-look render settings (tools/art/legacy_look.json); the round
scripts eval it. Nothing when LEGACY_LOOK=0. Claude, 2026-10-14."""
import json, os, sys
if os.environ.get("LEGACY_LOOK") != "0":
    d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "legacy_look.json"), encoding="utf-8"))
    for k, v in d.get(sys.argv[1], d["default"]).items():
        if k not in os.environ:   # a value set by hand for one run wins
            print("export %s=%s" % (k, v))
