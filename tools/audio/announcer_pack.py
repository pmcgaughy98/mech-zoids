"""The announcer pack: the foundry overseer (ElevenLabs voice NnhluA0QQcnSYL6ng49e, eleven_v3).

All lines are generated as one take, with each line in its own paragraph. v3 reads them almost back to back
(gaps of 50 to 100 ms), so a silence split fails. Instead, the take goes through ElevenLabs Scribe (word start
and end times, 0 credits), and this script cuts at the quietest 5 ms between one line's last word and the
next line's first. It then treats each piece with mech_voice's PA preset (light, 0.6) and writes
audio/voice/announcer/<name>.ogg plus a listen page.

  python -I tools/audio/announcer_pack.py <take.mp3> <scribe words.json>
"""
import base64
import html
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mech_voice as mv  # noqa: E402

SR = 48000
PROJECT = Path(__file__).resolve().parents[2]
OUT = PROJECT / "audio" / "voice" / "announcer"
SCRATCH = Path(r"D:\dev\_scratch\sound\announcer")
PAGE = PROJECT / "docs" / "listen" / "announcer-2026-11-05.html"
AMOUNT = 0.6  # light, Preston's pick for the machine voices; he called this voice "a good base"

LINES = [  # (file name, text, when); order matches the take
    ("match_start", "Foundry systems online.", "match start"),
    ("wave_warning", "Thirty seconds until the first wave.", "30 s before wave 1"),
    ("first_wave", "Production line active. Minions deployed.", "first wave"),
    ("victory", "Shift complete. Victory.", "you win"),
    ("defeat", "Shift failed. Defeat.", "you lose"),
    ("enemy_tower", "Enemy tower destroyed.", "your team kills a tower"),
    ("ally_tower", "Your tower has been destroyed.", "you lose a tower"),
    ("core_attack", "Warning: your core is under attack.", "your core takes damage"),
    ("core_exposed", "Enemy core exposed.", "last tower before their core"),
    ("pit_secured", "Pit secured.", "your team takes a pit"),
    ("pit_lost", "Pit lost.", "the enemy takes a pit"),
    ("first_blood", "First blood.", "first kill of the match"),
    ("enemy_down", "Enemy unit destroyed.", "your team kills a mech"),
    ("ally_down", "Unit lost.", "your team loses a mech"),
    ("double_kill", "Double kill.", "two quick kills"),
    ("triple_kill", "Triple kill.", "three quick kills"),
    ("team_wipe", "Team wipe.", "whole enemy team down"),
    ("shutdown", "Shutdown.", "you kill a player on a streak"),
    ("respawn", "Unit rebuilt.", "you respawn"),
    ("you_died", "Your unit has been destroyed.", "you die"),
    ("low_armor", "Low armor.", "your health under 25%"),
]


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def split(x, n_cuts):
    """Cut at the n_cuts longest interior silences (10 ms frames 40 dB under the loudest frame)."""
    hop = SR // 100
    frames = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[:frames * hop].reshape(frames, hop) ** 2).mean(1)) + 1e-9)
    quiet = db < db.max() - 40
    runs, i = [], 0
    while i < frames:
        if quiet[i]:
            j = i
            while j < frames and quiet[j]:
                j += 1
            if i > 0 and j < frames:  # interior only
                runs.append((j - i, i, j))
            i = j
        else:
            i += 1
    if len(runs) < n_cuts:
        sys.exit(f"only {len(runs)} interior silences, need {n_cuts}")
    longest = sorted(sorted(runs, reverse=True)[:n_cuts], key=lambda r: r[1])
    shortest_cut = min(r[0] for r in longest) * 10
    next_gap = sorted(runs, reverse=True)[n_cuts][0] * 10 if len(runs) > n_cuts else 0
    edges = [0] + [(a + b) // 2 * hop for _, a, b in longest] + [len(x)]
    return [x[edges[k]:edges[k + 1]] for k in range(len(edges) - 1)], shortest_cut, next_gap


def split_words(x, words_path):
    """Cut the take into LINES using Scribe word times; checks the words match the line texts first."""
    import json
    import re
    d = json.loads(Path(words_path).read_text(encoding="utf-8"))
    words = [w for w in (d["words"] if isinstance(d, dict) else d) if w.get("type") == "word"]
    norm = lambda s: re.sub(r"[^a-z]", "", s.lower())  # noqa: E731
    spans, i = [], 0
    for _, text, _ in LINES:
        n = len(text.split())
        got = [norm(w["text"]) for w in words[i:i + n]]
        if got != [norm(s) for s in text.split()]:
            sys.exit(f"transcript does not match line {text!r}: {got}")
        spans.append((words[i]["start"], words[i + n - 1]["end"]))
        i += n
    hop = SR // 200  # 5 ms
    e = np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, "same"))
    cuts = [0]
    for (_, end), (start, _) in zip(spans, spans[1:]):
        lo, hi = int((end - 0.10) * SR), int((start + 0.02) * SR)
        cuts.append(lo + int(np.argmin(e[lo:hi])))
    cuts.append(len(x))
    pieces = []
    for a, b in zip(cuts, cuts[1:]):
        y = x[a:b].copy()
        f = int(0.008 * SR)
        y[:f] *= np.linspace(0, 1, f)
        y[-f:] *= np.linspace(1, 0, f)
        pieces.append(y)
    gaps = [round((s - e2) * 1000) for (_, e2), (s, _) in zip(spans, spans[1:])]
    return pieces, min(gaps), max(gaps)


def b64(path, mime):
    return f"data:{mime};base64,{base64.b64encode(Path(path).read_bytes()).decode()}"


def page(rows, compare):
    cards = "".join(
        f'<section><h2>{html.escape(t)}</h2><p class="lbl">{html.escape(n)}.ogg, {html.escape(w)}, {s:.2f} s</p>'
        f'<audio controls preload="none" src="{b64(OUT / f"{n}.ogg", "audio/ogg")}"></audio></section>'
        for n, t, w, s in rows)
    comp = "".join(f'<section><h2>{html.escape(lbl)}</h2><audio controls preload="none" src="{src}"></audio></section>'
                   for lbl, src in compare)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Foundry Overseer Announcer</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:0 0 10px}}
h2{{font-size:1.02rem;margin:0 0 2px}} .lbl{{color:var(--mute);font-size:.85rem;margin:0 0 6px}} audio{{width:100%}}
</style></head><body><main><h1>Foundry overseer</h1>
<p class="sub">The announcer pack: preview 3, eleven_v3, one take. Each line has the light machine treatment plus a PA
horn and the echo of the foundry hall. Say which lines to redo, or what to change about the treatment.</p>
<h3>Treatment amount, one line</h3>{comp}<h3>All 21 lines (light)</h3>{cards}</main></body></html>"""


def main():
    take = Path(sys.argv[1])
    SCRATCH.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    x = load(take)
    pieces, gmin, gmax = split_words(x, sys.argv[2])
    print(f"take {len(x) / SR:.1f} s; gaps between lines {gmin} to {gmax} ms (Scribe word times)")
    rows = []
    for (name, text, when), y in zip(LINES, pieces):
        raw = SCRATCH / f"{name}_raw.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "1", "-i", "-", str(raw)],
                       input=y.tobytes(), check=True)
        mv.treat(raw, OUT / f"{name}.ogg", mv.SIZES["PA"], AMOUNT, -16.0)
        loud = np.flatnonzero(np.abs(y) > np.abs(x).max() * 10 ** (-40 / 20))
        secs = (loud[-1] - loud[0]) / SR  # spoken length, without the silence around it
        rate = secs / len(text)
        flag = "  <-- check" if not 0.035 < rate < 0.12 else ""
        print(f"{name:13s} {secs:5.2f} s  {rate * 1000:4.0f} ms/char  {text}{flag}")
        rows.append((name, text, when, secs))
    compare = [("Raw (no treatment)", b64(SCRATCH / "victory_raw.wav", "audio/wav"))]
    with tempfile.TemporaryDirectory() as tmp:
        for amt, lbl in ((0.4, "0.4, lighter"), (AMOUNT, "0.6, light (installed)"), (1.0, "1.0, standard")):
            o = Path(tmp) / f"v{amt}.ogg"
            mv.treat(SCRATCH / "victory_raw.wav", o, mv.SIZES["PA"], amt, -16.0)
            compare.append((f'"Shift complete. Victory." at {lbl}', b64(o, "audio/ogg")))
    PAGE.write_text(page(rows, compare), encoding="utf-8")
    print("page", PAGE)


if __name__ == "__main__":
    main()
