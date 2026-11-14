"""Rhino horn chain, the gore's landing (2026-11-10): game feel and the hub asked for "a heavy landing thud after the gore".

On the 3D body the basic is a chain: hook, rip, gore (rhino_kit.gd CHAIN). Each hit plays jab_swing and jab_hit. When the
gore lands, the front feet crash down about 0.27 s after its hit (horn_gore clip: hit 0.533, feet 0.80) and the kit fires
cue("gore_land"). It ends the chain, so it is heavier than a tremor stomp (-21) but under the pound slam. Built from the
Sonniss GDC 2026 bundle (D:\\dev\\sound-library, never into an AI tool).

  python -I tools/audio/rhino_gore_recorded.py               renders two options and the listen page
  python -I tools/audio/rhino_gore_recorded.py --install A   writes audio/sfx/rhino/gore_land.wav
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import basic_attacks_recorded as ba  # noqa: E402  (brings the gorilla and fennec sources and helpers)
import rhino_jab_recorded  # noqa: E402,F401  (adds "ring")
import gorilla_recorded as g  # noqa: E402
import fennec_portal_recorded as fp  # noqa: E402
from pound_recorded import SR, hp, lp, mix, glue, level, stats, to_int16, load  # noqa: E402

take, pitch = g.take, fp.pitch
PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "rhino"
PAGE = PROJECT / "docs" / "listen" / "rhino-gore-land-2026-11-10.html"
HIT_AT, FEET_AT = 0.533, 0.80  # horn_gore clip events (rhino 3D lane, review build v43)
TARGET = -16.0


def land_a():  # Feet crash: both front feet come down, a deep trailer boom under a body thud, low metal and grit
    return glue(mix(0.7, (lp(take("boom214", 0, 1.2, 0.7, 0.35), 180), 0.0, 1.0),
                    (lp(take("body", 0, 0.7, 0.4, 0.15), 700), 0.0, 0.8),
                    (lp(take("metal", 0, 0.4, 0.45, 0.2), 1200), 0.0, 0.5),
                    (hp(take("debris", 0, 1.0, 0.5, 0.3), 400), 0.03, 0.25)), drive=1.7, fade=0.25)


def land_b():  # Steel feet: armoured feet ring on the ground, a heavy latch clank pitched down, a shorter boom
    return glue(mix(0.65, (lp(take("ring", 0, 0.4, 0.5, 0.25), 1500), 0.0, 0.7),
                    (pitch(take("latch", 0, 0.5, 0.4, 0.15), 0.7), 0.0, 0.8),
                    (lp(take("boom011", 0, 1.2, 0.6, 0.3), 200), 0.0, 0.8)), drive=1.6, fade=0.22)


OPTIONS = {"A": ("Feet crash", land_a), "B": ("Steel feet", land_b)}


def lvl(x, target):
    """level() for short sounds: ebur128 needs a 400 ms block, so pad to 0.5 s to measure, then trim back."""
    n = len(x)
    return level(np.concatenate([x, np.zeros(max(0, int(0.5 * SR) - n))]), target)[:n]


def chain(land):
    """The three chain hits with the installed jab sounds (hook at 0, rip at 0.7 s, gore at 1.6 s), then the gore's land."""
    swing, hit = (load(GAME / f"{n}.wav") for n in ("jab_swing", "jab_hit"))
    layers = []
    for at, h in ((0.0, 0.20), (0.7, 0.333), (1.6, HIT_AT)):
        layers += [(swing, at, 1.0), (hit, at + h, 1.0)]  # the kit fires jab_swing as each clip starts
    layers.append((land, 1.6 + FEET_AT, 1.0))
    x = mix(1.6 + FEET_AT + 0.9, *layers)
    return x / max(1.0, np.max(np.abs(x)) / 0.89)


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(to_int16(x).tobytes())


def page(b):
    parts = ["<h3>In the chain</h3>"] + [ba.card(f"Chain with {k}: {OPTIONS[k][0]}", "hook, rip, gore, then the feet crash 0.27 s after the gore hit", chain(b[k]))
                                         for k in OPTIONS]
    parts.append("<h3>On its own</h3>")
    parts += [ba.card(f"gore_land {k}: {title}", "the gore's front feet crash down", b[k]) for k, (title, _) in OPTIONS.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rhino Gore Landing</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Rhino horn chain: the gore's landing</h1>
<p class="sub">The third hit of the 3D rhino's basic chain ends with its front feet crashing down. The chain previews use
the jab sounds already in the game, at the review clip's times. A is in the game now as a placeholder. Pick A or B.</p>
{''.join(parts)}</main></body></html>"""


def main():
    b = {k: lvl(f(), TARGET) for k, (_, f) in OPTIONS.items()}
    if "--install" in sys.argv:
        k = sys.argv[sys.argv.index("--install") + 1].upper()
        write_wav(GAME / "gore_land.wav", b[k])
        print(f"gore_land <- {k}  {len(b[k]) / SR * 1000:.0f} ms  {stats(b[k])}")
        return
    for k, x in b.items():
        print("gore_land", k, f"{len(x) / SR * 1000:.0f} ms", stats(x))
    PAGE.write_text(page(b), encoding="utf-8")
    print("page", PAGE)


if __name__ == "__main__":
    main()
