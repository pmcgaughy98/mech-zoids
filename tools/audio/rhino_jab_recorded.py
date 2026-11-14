"""Rhino basic attack (2026-11-05): a melee horn jab. Preston: "we need basic attacks. Rhino, gorilla will be melee".

rhino_kit.gd fires cue("jab_swing") as the swing starts (about every 0.9 s in a fight, so short and light) and
cue("jab_hit") on contact 0.25 s later, with a 0.05 s hitstop, on machines, minions, monsters and towers. A miss
gets only the swing. Built from the Sonniss GDC 2026 bundle (D:\\dev\\sound-library, never into an AI tool).

  python -I tools/audio/rhino_jab_recorded.py               renders two options per sound and the listen page
  python -I tools/audio/rhino_jab_recorded.py --install A,B writes audio/sfx/rhino/ with swing A, hit B
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gorilla_recorded as g  # noqa: E402
import fennec_portal_recorded as fp  # noqa: E402  (adds its sources to g.F)
from pound_recorded import SR, SRC, hp, lp, mix, glue, level, stats, to_int16  # noqa: E402

g.F.update({
    "ring": SRC["ring"],
    "swish": "Epic Stock Media - Tower Defense Game/DSGNStngr_Action Deploy Units Sword Slice Special Move Layered Swish 04_ESM_TDG.wav",
})
take, pitch = g.take, fp.pitch
PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "rhino"
PAGE = PROJECT / "docs" / "listen" / "rhino-jab-2026-11-05.html"
HIT_AT, EVERY = 0.25, 0.9


def swing_a():  # Heavy air: the horn pushes a short, low metal whoosh, a servo tick at the start
    return glue(mix(0.42, (hp(take("metwhoosh", 0, 1.0, 0.35, 0.15), 250), 0.0, 0.9),
                    (hp(pitch(take("servo", 0, 1.0, 0.25, 0.1), 1.2), 200), 0.0, 0.3)), drive=1.2, fade=0.12)


def swing_b():  # Blade: a fast swish pitched down for weight, a light latch tick
    return glue(mix(0.42, (hp(pitch(take("swish", 0, 1.0, 0.4, 0.15), 0.8), 300), 0.0, 0.85),
                    (pitch(take("latch", 0, 0.5, 0.2, 0.08), 1.3), 0.0, 0.25)), drive=1.2, fade=0.12)


def hit_a():  # Plate: a low metal hit and a body punch with a little crunch, short tail so jabs don't pile up
    return glue(mix(0.42, (hp(take("metal", 0, 0.4, 0.4, 0.2), 120), 0.0, 0.8),
                    (take("body", 0, 0.7, 0.3, 0.1), 0.0, 0.7),
                    (hp(take("crunch", 0, 0.44, 0.25, 0.1), 250), 0.0, 0.3)), drive=1.5, fade=0.15)


def hit_b():  # Ring: the metal-on-metal hit with its resonant ring cut short, a crisp punch under it
    return glue(mix(0.42, (take("ring", 0, 0.4, 0.4, 0.2), 0.0, 0.85),
                    (take("punch", 0, 0.4, 0.25, 0.1), 0.0, 0.5),
                    (lp(take("body", 0, 0.7, 0.25, 0.1), 400), 0.0, 0.5)), drive=1.5, fade=0.15)


SOUNDS = {  # name: (target LUFS, {letter: (title, builder)}, what triggers it)
    "jab_swing": (-20.0, {"A": ("Heavy air", swing_a), "B": ("Blade", swing_b)}, "the swing starts, about every 0.9 s"),
    "jab_hit": (-16.0, {"A": ("Plate", hit_a), "B": ("Ring", hit_b)}, "the horn connects, 0.25 s later"),
}


def lvl(x, target):
    """level() for short sounds: ebur128 needs a 400 ms block, so pad to 0.5 s to measure, then trim back."""
    n = len(x)
    return level(np.concatenate([x, np.zeros(max(0, int(0.5 * SR) - n))]), target)[:n]


def build():
    return {n: {k: lvl(f(), t) for k, (_, f) in opts.items()} for n, (t, opts, _) in SOUNDS.items()}


def fight(swing, hit):
    """Three jabs 0.9 s apart, the last one a miss, each with a small pitch nudge as KitAudio plays them."""
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
    together = [fp.card(f"Swing {s} + hit {h}", "three jabs 0.9 s apart: hit, hit, miss",
                        fight(b["jab_swing"][s], b["jab_hit"][h])) for s, h in pairs]
    one = []
    for n, (_, opts, note) in SOUNDS.items():
        one += [fp.card(f"{n} {k}: {title}", note, b[n][k]) for k, (title, _) in opts.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rhino Jab Sounds</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Rhino basic attack: horn jab</h1>
<p class="sub">The swing plays on every jab (about every 0.9 s), so it stays short and light. The hit plays on contact.
A and A are in the game now as placeholders. Pick a swing letter and a hit letter.</p>
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
