"""Hippo basic attack (2026-11-05): a melee bite. A large machine, so big heavy jaws, not the wolf's quick snap.

hippo_kit.gd fires cue("bite") on contact, 0.1 s after the key (with impact 0.2), and cue("bite_whiff") when the
jaws close on air. There is no swing sound: the bite is the whole attack. Built from the Sonniss GDC 2026 bundle
(D:\\dev\\sound-library, never into an AI tool).

  python -I tools/audio/hippo_bite_recorded.py               renders two options per sound and the listen page
  python -I tools/audio/hippo_bite_recorded.py --install A,B writes audio/sfx/hippo/ with bite A, whiff B
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gorilla_recorded as g  # noqa: E402
import fennec_portal_recorded as fp  # noqa: E402  (adds its sources to g.F)
from pound_recorded import SR, hp, lp, mix, glue, level, stats, to_int16  # noqa: E402

take, pitch = g.take, fp.pitch
PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "hippo"
PAGE = PROJECT / "docs" / "listen" / "hippo-bite-2026-11-05.html"
EVERY = 1.0  # attack interval assumed about 1 s for the preview


def bite_a():  # Crusher: the latch clamp pitched down into a pipe crunch, a short low boom for the jaw's weight
    return glue(mix(0.5, (pitch(take("latch", 0, 0.5, 0.4, 0.12), 0.8), 0.0, 1.0),
                    (hp(take("crunch", 0, 0.44, 0.35, 0.15), 150), 0.0, 0.7),
                    (lp(take("boom214", 0, 1.2, 0.5, 0.25), 200), 0.0, 0.6),
                    (lp(take("body", 0, 0.7, 0.3, 0.1), 500), 0.0, 0.5)), drive=1.6, fade=0.15)


def bite_b():  # Iron jaws: a low metal hit and a door-bang clash of armoured jaws, crunch under it
    return glue(mix(0.5, (lp(take("metal", 0, 0.4, 0.45, 0.2), 1500), 0.0, 0.85),
                    (hp(take("bang", 0, 0.5, 0.3, 0.12), 150), 0.0, 0.6),
                    (hp(take("crunch", 0, 0.44, 0.3, 0.12), 200), 0.0, 0.5)), drive=1.5, fade=0.15)


def whiff_a():  # Heavy clap: the jaws slam shut on nothing, a deep clack and the air they push
    return glue(mix(0.45, (pitch(take("latch", 0, 0.5, 0.3, 0.1), 0.85), 0.0, 0.8),
                    (lp(pitch(take("metwhoosh", 0, 1.0, 0.35, 0.15), 0.85), 3000), 0.0, 0.5)), drive=1.3, fade=0.12)


def whiff_b():  # Snap shut: a sharper metal clap, lighter, with a low swish
    return glue(mix(0.45, (hp(take("bang", 0, 0.5, 0.25, 0.1), 300), 0.0, 0.7),
                    (pitch(take("latch", 0, 0.5, 0.25, 0.1), 1.0), 0.0, 0.5),
                    (hp(pitch(take("sweep", 0, 0.5, 0.3, 0.12), 0.8), 300), 0.0, 0.35)), drive=1.3, fade=0.12)


SOUNDS = {  # name: (target LUFS, {letter: (title, builder)}, what triggers it)
    "bite": (-15.0, {"A": ("Crusher", bite_a), "B": ("Iron jaws", bite_b)}, "the jaws land, 0.1 s after the key"),
    "bite_whiff": (-19.0, {"A": ("Heavy clap", whiff_a), "B": ("Snap shut", whiff_b)}, "the jaws close on air"),
}


def lvl(x, target):
    """level() for short sounds: ebur128 needs a 400 ms block, so pad to 0.5 s to measure, then trim back."""
    n = len(x)
    return level(np.concatenate([x, np.zeros(max(0, int(0.5 * SR) - n))]), target)[:n]


def build():
    return {n: {k: lvl(f(), t) for k, (_, f) in opts.items()} for n, (t, opts, _) in SOUNDS.items()}


def fight(bite, whiff):
    """Bite, bite, whiff about 1 s apart, each with a small pitch nudge as KitAudio plays them."""
    x = mix(2 * EVERY + 0.5, (bite, 0.0, 1.0), (pitch(bite, 1.02), EVERY, 1.0), (pitch(whiff, 0.98), 2 * EVERY, 1.0))
    return x / max(1.0, np.max(np.abs(x)) / 0.89)


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(to_int16(x).tobytes())


def page(b):
    pairs = [("A", "A"), ("B", "B")]
    together = [fp.card(f"Bite {s} + whiff {h}", "bite, bite, whiff about 1 s apart",
                        fight(b["bite"][s], b["bite_whiff"][h])) for s, h in pairs]
    one = []
    for n, (_, opts, note) in SOUNDS.items():
        one += [fp.card(f"{n} {k}: {title}", note, b[n][k]) for k, (title, _) in opts.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hippo Bite Sounds</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Hippo basic attack: bite</h1>
<p class="sub">Big, heavy jaws, slower and lower than the wolf. A and A are in the game now as placeholders. Pick a bite
letter and a whiff letter.</p>
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
