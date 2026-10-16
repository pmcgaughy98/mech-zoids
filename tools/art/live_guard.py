"""Keeps hand-finished live art from being overwritten silently (Claude, 2026-10-15).

Codex finishes a machine by editing its live files (art/machines/<id>/views/*.png, art/machines/<id>/anim/<clip>/*.png).
Between 2026-10-14 and 2026-10-15 Claude's installs replaced those live files several times without carrying the
finish forward or flagging it, as docs/team/CODEX_TASKS_2026-10-13.md had promised. Codex's own copies survived in
docs/art/2d/<id>/*_codex/, but nothing told anyone the live finish was gone. Now import_views.py and export_anim.py:
  - after writing, record a hash of every file they wrote in <folder>/.installed_hashes.json;
  - before writing, call guard(): if any recorded file has changed since (someone finished it by hand), or there is
    no record yet but a Codex finish exists for the machine, the whole live folder is copied to
    docs/art/2d/<id>/live_backup_<kind>_<n>/ and a WARNING names the backup. Nothing is ever deleted.
  - while Codex is working on a machine it leaves art/machines/<id>/CODEX_IN_PROGRESS; guard() then stops the
    install outright (LIVE_GUARD_FORCE=1 overrides, only on Preston's say-so).
"""
import glob, hashlib, json, os, shutil

RECORD = ".installed_hashes.json"


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()


def record(folder, files):
    """Remember what this install wrote (paths relative to `folder`)."""
    json.dump({f: _sha(os.path.join(folder, f)) for f in files}, open(os.path.join(folder, RECORD), "w"), indent=1)


def guard(folder, mid, kind):
    """Back up `folder` before an install rewrites it, if it holds hand edits. Returns the backup path or None."""
    lock = os.path.join(os.path.dirname(folder), "CODEX_IN_PROGRESS")
    if os.path.exists(lock) and os.environ.get("LIVE_GUARD_FORCE") != "1":
        raise SystemExit("STOP: %s is marked CODEX_IN_PROGRESS (%s): Codex is finishing this machine's live art. Do not "
                         "install over it; wait for Codex's hand-over, or ask Preston (LIVE_GUARD_FORCE=1 overrides)." % (mid, lock))
    if not os.path.isdir(folder) or not os.listdir(folder):
        return None
    rec_path = os.path.join(folder, RECORD)
    if os.path.exists(rec_path):
        rec = json.load(open(rec_path))
        changed = [f for f, h in rec.items() if not os.path.exists(os.path.join(folder, f)) or _sha(os.path.join(folder, f)) != h]
        why = "%d file(s) changed since the last install (%s)" % (len(changed), ", ".join(changed[:4])) if changed else ""
    else:
        codex = glob.glob(os.path.join("docs", "art", "2d", mid, "*codex*"))
        why = "no install record and a Codex finish exists (%s)" % ", ".join(os.path.basename(c) for c in codex[:3]) if codex else ""
    if not why:
        return None
    n = 1
    while os.path.exists(os.path.join("docs", "art", "2d", mid, "live_backup_%s_%d" % (kind, n))):
        n += 1
    dst = os.path.join("docs", "art", "2d", mid, "live_backup_%s_%d" % (kind, n))
    shutil.copytree(folder, dst)
    print("WARNING: %s %s: %s. The live folder was copied to %s before this install replaced it; carry the finish "
          "forward or flag it (docs/team/CODEX_TASKS_2026-10-15.md)." % (mid, kind, why, dst))
    return dst
