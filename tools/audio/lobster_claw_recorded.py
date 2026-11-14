"""Lobster basic attack (2026-11-06): a melee claw snap from a big hydraulic claw. Preston: "Melee claw snap".

lobster_kit.gd (LobsterKit) fires cue("basic_snap") when the big claw lands and cue("basic_whiff") when it closes on air.
The Lobster session asked for heavy and mechanical: a short clamp crunch on the hit, a lighter hiss-clack on the whiff.
The hiss is a jet blast's top end (the bundle has no pneumatic hiss). Built from the Sonniss GDC 2026 bundle
(D:\\dev\\sound-library, never into an AI tool).

  python -I tools/audio/lobster_claw_recorded.py               renders two options per sound and the listen page
  python -I tools/audio/lobster_claw_recorded.py --install A,B writes audio/sfx/lobster/ with snap A, whiff B
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gorilla_recorded as g  # noqa: E402
import fennec_portal_recorded as fp  # noqa: E402  (adds its sources to g.F)
from pound_recorded import SR, hp, lp, mix, glue, level, stats, to_int16  # noqa: E402

g.F.update({
    "jet": "344 Audio - Air Designed/AEROJet_Blast Off Clean_344 Audio_Air Designed.wav",
    "percsnap": "Cinematic Sound Design - Interface & Infographics/Interface Percussion Snap.wav",
})
take, pitch = g.take, fp.pitch
PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "lobster"
PAGE = PROJECT / "docs" / "listen" / "lobster-claw-2026-11-06.html"
EVERY = 1.0  # attack interval assumed about 1 s for the preview


def hiss(dur, cutoff=3000):
    """A pneumatic-style hiss: the top of the jet blast, shaped to a quick release."""
    y = hp(take("jet", 0, 2.0, dur, dur / 2), cutoff)
    return y * np.linspace(1, 0, len(y)) ** 1.5


def snap_a():  # Hydraulic clamp: a deep latch clamp and pipe crunch, low metal, then the pressure lets go with a hiss
    return glue(mix(0.5, (pitch(take("latch", 0, 0.5, 0.4, 0.12), 0.75), 0.0, 1.0),
                    (hp(take("crunch", 0, 0.44, 0.35, 0.15), 150), 0.0, 0.75),
                    (lp(take("metal", 0, 0.4, 0.4, 0.2), 1200), 0.0, 0.5),
                    (hiss(0.3), 0.06, 0.3)), drive=1.6, fade=0.15)


def snap_b():  # Vice crush: armoured jaws bang shut on a heavy crunch with a short low boom, no hiss
    return glue(mix(0.45, (hp(take("bang", 0, 0.5, 0.3, 0.12), 150), 0.0, 0.75),
                    (hp(take("crunch", 0, 0.44, 0.35, 0.15), 120), 0.0, 0.85),
                    (lp(take("boom214", 0, 1.2, 0.45, 0.25), 200), 0.0, 0.6)), drive=1.6, fade=0.15)


def whiff_a():  # Hiss-clack: the claw clacks shut on air and vents a short hiss
    return glue(mix(0.42, (pitch(take("latch", 0, 0.5, 0.3, 0.1), 0.9), 0.0, 0.7),
                    (hiss(0.3, 2500), 0.02, 0.6)), drive=1.2, fade=0.12)


def whiff_b():  # Dry clack: a lighter metal clap and a percussive snap, no hiss
    return glue(mix(0.42, (hp(take("bang", 0, 0.5, 0.25, 0.1), 400), 0.0, 0.6),
                    (pitch(take("percsnap", 0, 0.4, 0.25, 0.1), 0.8), 0.0, 0.6)), drive=1.2, fade=0.12)


SOUNDS = {  # name: (target LUFS, {letter: (title, builder)}, what triggers it)
    "basic_snap": (-15.0, {"A": ("Hydraulic clamp", snap_a), "B": ("Vice crush", snap_b)}, "the big claw lands"),
    "basic_whiff": (-19.0, {"A": ("Hiss-clack", whiff_a), "B": ("Dry clack", whiff_b)}, "the claw closes on air"),
}


def lvl(x, target):
    """level() for short sounds: ebur128 needs a 400 ms block, so pad to 0.5 s to measure, then trim back."""
    n = len(x)
    return level(np.concatenate([x, np.zeros(max(0, int(0.5 * SR) - n))]), target)[:n]


def build():
    return {n: {k: lvl(f(), t) for k, (_, f) in opts.items()} for n, (t, opts, _) in SOUNDS.items()}


def fight(snap, whiff):
    """Snap, snap, whiff about 1 s apart, each with a small pitch nudge as KitAudio plays them."""
    x = mix(2 * EVERY + 0.5, (snap, 0.0, 1.0), (pitch(snap, 1.02), EVERY, 1.0), (pitch(whiff, 0.98), 2 * EVERY, 1.0))
    return x / max(1.0, np.max(np.abs(x)) / 0.89)


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(to_int16(x).tobytes())


def page(b):
    together = [fp.card(f"All {k}", "snap, snap, whiff about 1 s apart", fight(b["basic_snap"][k], b["basic_whiff"][k]))
                for k in "AB"]
    one = []
    for n, (_, opts, note) in SOUNDS.items():
        one += [fp.card(f"{n} {k}: {title}", note, b[n][k]) for k, (title, _) in opts.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lobster Claw Sounds</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Lobster basic attack: claw snap</h1>
<p class="sub">A big hydraulic claw. A is heavy with a pressure hiss, as the Lobster session asked. B is the same weight
without the hiss. A and A are in the game now as placeholders. Pick a snap letter and a whiff letter.</p>
<h3>In a fight</h3>{''.join(together)}<h3>One by one</h3>{''.join(one)}</main></body></html>"""


def main():
    b = build()
    if "--install" in sys.argv:
        picks = sys.argv[sys.argv.index("--install") + 1].upper().split(",")
        GAME.mkdir(parents=True, exist_ok=True)
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
