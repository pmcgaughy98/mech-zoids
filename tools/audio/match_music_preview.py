"""In-match music candidates from Patch's asset search (2026-11-14). Preston: "Patch gap-fill".

The game has a menu theme (audio/music/main_theme.ogg, Suno) and no music during a match. Patch found free tracks
that fit an industrial mech arena. Each was pulled into scratch with `pch assets add` (D:\\dev\\_scratch\\patch-gg-try,
credits in its CREDITS.md). This renders a 60 s excerpt of each, levelled to -16 LUFS so they compare fairly, plus the
menu theme for reference, into one listen page. Nothing goes into the game until Preston picks.

  python -I tools/audio/match_music_preview.py
"""
import base64
import html
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
SCRATCH = Path(r"D:\dev\_scratch\patch-gg-try\assets\music")
PAGE = PROJECT / "docs" / "listen" / "match-music-patch-2026-11-14.html"

TRACKS = [  # (file, title, credit line, licence, start s, note)
    (SCRATCH / "industrialCinematic.ogg", "Industrial Cinematic", "Kevin MacLeod (incompetech.com)", "CC BY 4.0", 30,
     "4:04. Slow, heavy and mechanical, cinematic. Credit required."),
    (SCRATCH / "industrialRevolution.ogg", "Industrial Revolution", "Kevin MacLeod (incompetech.com)", "CC BY 4.0", 20,
     "2:26. Driving percussion and machine rhythm, the most action-like. Credit required."),
    (SCRATCH / "crusadeHeavyIndustry.ogg", "Crusade - Heavy Industry", "Kevin MacLeod (incompetech.com)", "CC BY 4.0", 60,
     "9:17. Long and slow-building, so it rarely repeats in a match. Credit required."),
    (SCRATCH / "epicBossBattle.ogg", "Epic boss battle", "Juhani Junkala (OpenGameArt.org)", "CC0", 10,
     "2:03, made to loop seamlessly. Orchestral and urgent, closest to the menu theme's style. No credit required."),
    (PROJECT / "audio" / "music" / "main_theme.ogg", "Menu theme (for reference)", "Suno take 1, yours", "-", 0,
     "Already in the game for the menu. Here to compare styles, not a candidate."),
]


def excerpt(src, start, dur=60):
    """A dur-second Ogg excerpt from start, levelled to -16 LUFS, with short fades."""
    af = f"afade=t=in:d=1.5,afade=t=out:st={dur - 3}:d=3,loudnorm=I=-16:TP=-1.5:LRA=11"
    return subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", str(src), "-af", af,
                           "-ar", "44100", "-c:a", "libvorbis", "-q:a", "3", "-f", "ogg", "-"],
                          capture_output=True, check=True).stdout


def card(title, credit, lic, note, ogg):
    b64 = base64.b64encode(ogg).decode()
    return (f'<section><h2>{html.escape(title)}</h2><p class="lbl">{html.escape(credit)} | {html.escape(lic)}</p>'
            f'<p>{html.escape(note)}</p><audio controls preload="none" src="data:audio/ogg;base64,{b64}"></audio></section>')


def main():
    cards = []
    for src, title, credit, lic, start, note in TRACKS:
        ogg = excerpt(src, start)
        print(f"{title}: {len(ogg) / 1e6:.1f} MB excerpt from {start} s")
        cards.append(card(title, credit, lic, note, ogg))
    PAGE.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Match Music Picks</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Music during a match</h1>
<p class="sub">The game has a menu theme but plays no music in a match. These free tracks came from Patch's asset search:
each excerpt is 60 s, levelled the same so you can compare them. CC BY tracks need a credit line in the game's credits;
CC0 needs none. None is in the game yet. Pick one, or none.</p>
{''.join(cards)}
<h3>Credits (if used)</h3><p class="lbl">Kevin MacLeod tracks: "Title" Kevin MacLeod (incompetech.com), licensed under Creative
Commons: By Attribution 4.0, creativecommons.org/licenses/by/4.0/. Epic boss battle: Juhani Junkala, CC0, via OpenGameArt.org.</p>
</main></body></html>""", encoding="utf-8")
    print("page", PAGE, f"{PAGE.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
