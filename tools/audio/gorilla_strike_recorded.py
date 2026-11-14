"""Gorilla basic attack (2026-11-05): a heavy melee fist, meant to read differently from the rhino's horn jab.

ape_kit.gd fires cue("strike_swing") as the swing starts and cue("strike_hit") on contact about 0.22 s later
(only when something is hit). The rhino's jab is metal-on-metal; this one is weight: a big arm through the air
and a fist that thuds. Built from the Sonniss GDC 2026 bundle (D:\\dev\\sound-library, never into an AI tool).

  python -I tools/audio/gorilla_strike_recorded.py               renders two options per sound and the listen page
  python -I tools/audio/gorilla_strike_recorded.py --install A,B writes audio/sfx/ape/ with swing A, hit B
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gorilla_recorded as g  # noqa: E402
import fennec_portal_recorded as fp  # noqa: E402  (adds its sources to g.F)
from pound_recorded import SR, hp, lp, mix, glue, level, stats, to_int16  # noqa: E402

g.F["swish"] = ("Epic Stock Media - Tower Defense Game/DSGNStngr_Action Deploy Units Sword Slice Special Move "
                "Layered Swish 04_ESM_TDG.wav")
take, pitch = g.take, fp.pitch
PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "ape"
PAGE = PROJECT / "docs" / "listen" / "gorilla-strike-2026-11-05.html"
HIT_AT, EVERY = 0.22, 1.0  # contact time from the Gorilla session; attack interval assumed about 1 s


def swing_a():  # Haymaker: a big arm through the air, the metal whoosh pitched down for mass
    return glue(mix(0.45, (hp(pitch(take("metwhoosh", 0, 1.0, 0.45, 0.15), 0.8), 120), 0.0, 1.0),
                    (lp(take("sweep", 0, 0.5, 0.35, 0.12), 2500), 0.02, 0.35)), drive=1.3, fade=0.12)


def swing_b():  # Servo arm: the shoulder drive whirs and a low swish follows the fist
    return glue(mix(0.45, (hp(pitch(take("servo", 0, 1.0, 0.4, 0.12), 0.9), 120), 0.0, 0.55),
                    (hp(pitch(take("swish", 0, 1.0, 0.45, 0.15), 0.7), 200), 0.03, 0.85)), drive=1.3, fade=0.12)


def hit_a():  # Fist: a heavy body punch on a short low boom, a little crunch; deeper than the rhino's plate
    return glue(mix(0.45, (take("body", 0, 0.7, 0.35, 0.12), 0.0, 1.0),
                    (lp(take("boom214", 0, 1.2, 0.45, 0.25), 220), 0.0, 0.75),
                    (hp(take("crunch", 0, 0.44, 0.2, 0.08), 300), 0.0, 0.25)), drive=1.6, fade=0.15)


def hit_b():  # Knuckle plates: the armoured knuckles bang, a crisp combat hit and the body thud under them
    return glue(mix(0.45, (hp(take("bang", 0, 0.5, 0.3, 0.12), 150), 0.0, 0.7),
                    (take("punch", 0, 0.4, 0.25, 0.1), 0.0, 0.6),
                    (lp(take("body", 0, 0.7, 0.35, 0.12), 600), 0.0, 0.8)), drive=1.5, fade=0.15)


SOUNDS = {  # name: (target LUFS, {letter: (title, builder)}, what triggers it)
    "strike_swing": (-20.0, {"A": ("Haymaker", swing_a), "B": ("Servo arm", swing_b)}, "the swing starts"),
    "strike_hit": (-15.5, {"A": ("Fist", hit_a), "B": ("Knuckle plates", hit_b)}, "the fist connects, about 0.22 s later"),
}


def lvl(x, target):
    """level() for short sounds: ebur128 needs a 400 ms block, so pad to 0.5 s to measure, then trim back."""
    n = len(x)
    return level(np.concatenate([x, np.zeros(max(0, int(0.5 * SR) - n))]), target)[:n]


def build():
    return {n: {k: lvl(f(), t) for k, (_, f) in opts.items()} for n, (t, opts, _) in SOUNDS.items()}


def fight(swing, hit):
    """Three strikes about 1 s apart, the last one a miss, each with a small pitch nudge as KitAudio plays them."""
    layers = []
    for i, r in enumerate((1.0, 1.02, 0.98)):
        layers.append((pitch(swing, r), i * EVERY, 1.0))
        if i < 2:
            layers.append((pitch(hit, r), i * EVERY + HIT_AT, 1.0))
    x = mix(2 * EVERY + 0.5, *layers)
    return x / max(1.0, np.max(np.abs(x)) / 0.89)


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(to_int16(x).tobytes())


def page(b):
    pairs = [("A", "A"), ("B", "B"), ("A", "B"), ("B", "A")]
    together = [fp.card(f"Swing {s} + hit {h}", "three strikes about 1 s apart: hit, hit, miss",
                        fight(b["strike_swing"][s], b["strike_hit"][h])) for s, h in pairs]
    one = []
    for n, (_, opts, note) in SOUNDS.items():
        one += [fp.card(f"{n} {k}: {title}", note, b[n][k]) for k, (title, _) in opts.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gorilla Strike Sounds</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Gorilla basic attack: heavy fist</h1>
<p class="sub">Built to sound different from the rhino's metal horn jab: more arm and more body. A and A are in the game
now as placeholders. Pick a swing letter and a hit letter.</p>
<h3>In a fight</h3>{''.join(together)}<h3>One by one</h3>{''.join(one)}</main></body></html>"""


def main():
    b = build()
    if "--install" in sys.argv:
        picks = sys.argv[sys.argv.index("--install") + 1].upper().split(",")
        for n, k in zip(SOUNDS, picks if len(picks) == 2 else picks * 2):
            write_wav(GAME / f"{n}.wav", b[n][k])
            print(f"{n} <- {k}  {stats(b[n][k])}")
        return
    for n, opts in b.items():
        for k, x in opts.items():
            print(n, k, stats(x))
    PAGE.write_text(page(b), encoding="utf-8")
    print("page", PAGE)


if __name__ == "__main__":
    main()
