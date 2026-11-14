"""Falcon basic attack (2026-11-06): a ranged dart. Preston: "Yes, falcon".

falcon_kit.gd fires cue(name):
  dart_fire  every shot, up to once per 0.9 s: light and short, it repeats all fight
  dart_hit   the dart lands (24 m/s, within 7 m, so 0.05 to 0.3 s after the shot)
  dart_keen  instead of dart_hit when the hit is at 90% of full range or more (keen eye's top bonus, with a small
             shake): a sharper crack, the shot to reward
  dart_miss  nothing, or a wall
Built to read apart from the hummingbird's tiny steel beak: more air and whip, a heavier landing, and a ringing crack
for the keen shot. Built from the Sonniss GDC 2026 bundle (D:\\dev\\sound-library, never into an AI tool).

  python -I tools/audio/falcon_dart_recorded.py               renders two options per sound and the listen page
  python -I tools/audio/falcon_dart_recorded.py --install A   writes audio/sfx/falcon/ with every A
  python -I tools/audio/falcon_dart_recorded.py --install A,B,A,A   one letter per sound, in SOUNDS order
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import basic_attacks_recorded as ba  # noqa: E402  (brings the wolf, gorilla and fennec sources and helpers)
import rhino_jab_recorded  # noqa: E402,F401  (adds "ring")
import gorilla_recorded as g  # noqa: E402
import fennec_portal_recorded as fp  # noqa: E402
from pound_recorded import SR, hp, mix, glue, level, stats, to_int16  # noqa: E402

take, pitch, cut = g.take, fp.pitch, ba.cut
PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "falcon"
PAGE = PROJECT / "docs" / "listen" / "falcon-dart-2026-11-06.html"


def fire_a():  # Talon flick: a thin whip crack and a fast metal whoosh
    return cut(glue(mix(0.22, (hp(pitch(take("whip", 0, 0.5, 0.2, 0.08), 1.3), 1500), 0.0, 0.7),
                        (hp(pitch(take("metwhoosh", 0, 1.0, 0.25, 0.1), 1.6), 1200), 0.0, 0.6)), drive=1.2, fade=0.06), 0.2)


def fire_b():  # Air cut: a quick sweep through the air, a small latch click as it leaves
    return cut(glue(mix(0.22, (hp(pitch(take("sweep", 0, 0.5, 0.25, 0.1), 1.5), 1500), 0.0, 0.8),
                        (hp(pitch(take("latch", 0, 0.5, 0.15, 0.06), 1.3), 800), 0.0, 0.4)), drive=1.2, fade=0.06), 0.2)


def hit_a():  # Thunk: a light punch on a small metal hit, a touch of crunch
    return glue(mix(0.3, (hp(take("punch", 0, 0.4, 0.25, 0.1), 300), 0.0, 0.8),
                    (hp(take("metal", 0, 0.4, 0.25, 0.12), 400), 0.0, 0.5),
                    (hp(take("crunch", 0, 0.44, 0.15, 0.06), 800), 0.0, 0.25)), drive=1.4, fade=0.1)


def hit_b():  # Spike: a metal bang and a wire tap, drier
    return glue(mix(0.3, (hp(take("bang", 0, 0.5, 0.25, 0.1), 400), 0.0, 0.7),
                    (hp(pitch(take("spring", 0, 0.4, 0.2, 0.08), 1.2), 1200), 0.0, 0.5)), drive=1.4, fade=0.1)


def keen_a():  # Crack: a full whip crack on a ringing metal hit, a punch under it
    return glue(mix(0.45, (hp(take("whip", 0, 0.5, 0.3, 0.12), 400), 0.0, 1.0),
                    (hp(take("ring", 0, 0.4, 0.4, 0.2), 300), 0.0, 0.6),
                    (hp(take("punch", 0, 0.4, 0.2, 0.08), 300), 0.0, 0.5)), drive=1.5, fade=0.15)


def keen_b():  # Ring out: the ringing hit leads, a glassy snap and a bright shimmer on top
    return glue(mix(0.55, (hp(take("ring", 0, 0.4, 0.5, 0.25), 250), 0.0, 0.9),
                    (hp(pitch(take("snap", 0, 0.2, 0.2, 0.08), 1.1), 1500), 0.0, 0.5),
                    (hp(take("shimmer", 0, 0.5, 0.4, 0.2), 2000), 0.0, 0.25)), drive=1.4, fade=0.18)


def miss_a():  # Whistle off: the whoosh trails away
    return cut(fp.ramp(hp(pitch(take("metwhoosh", 0, 1.0, 0.35, 0.15), 1.8), 2000), 1, 0, 1.5), 0.28)


def miss_b():  # Wall tick: a high dry snap on a faint metal knock
    return glue(mix(0.25, (hp(pitch(take("percsnap", 0, 0.4, 0.2, 0.08), 1.6), 2000), 0.0, 0.6),
                    (hp(take("bang", 0, 0.5, 0.15, 0.06), 1500), 0.0, 0.3)), drive=1.1, fade=0.08)


SOUNDS = {  # name: (target LUFS, {letter: (title, builder)}, what triggers it)
    "dart_fire": (-21.0, {"A": ("Talon flick", fire_a), "B": ("Air cut", fire_b)}, "every shot, up to once per 0.9 s"),
    "dart_hit": (-18.0, {"A": ("Thunk", hit_a), "B": ("Spike", hit_b)}, "the dart lands"),
    "dart_keen": (-15.5, {"A": ("Crack", keen_a), "B": ("Ring out", keen_b)}, "a hit at 90%+ of full range: the shot to reward"),
    "dart_miss": (-24.0, {"A": ("Whistle off", miss_a), "B": ("Wall tick", miss_b)}, "nothing, or a wall"),
}


def lvl(x, target):
    """level() for short sounds: ebur128 needs a 400 ms block, so pad to 0.5 s to measure, then trim back."""
    n = len(x)
    return level(np.concatenate([x, np.zeros(max(0, int(0.5 * SR) - n))]), target)[:n]


def build():
    return {n: {k: lvl(f(), t) for k, (_, f) in opts.items()} for n, (t, opts, _) in SOUNDS.items()}


def fight(b, k):
    """Three shots 0.9 s apart, each with a small pitch nudge: a near hit, a full-range keen hit, a miss."""
    x = mix(2.7, (b["dart_fire"][k], 0.0, 1.0), (b["dart_hit"][k], 0.12, 1.0),
            (pitch(b["dart_fire"][k], 1.02), 0.9, 1.0), (b["dart_keen"][k], 1.18, 1.0),
            (pitch(b["dart_fire"][k], 0.98), 1.8, 1.0), (b["dart_miss"][k], 2.1, 1.0))
    return x / max(1.0, np.max(np.abs(x)) / 0.89)


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(to_int16(x).tobytes())


def page(b):
    parts = ["<h3>In a fight</h3>"] + [ba.card(f"All {k}", "three shots: a near hit, a full-range keen hit, a miss", fight(b, k))
                                       for k in "AB"]
    parts.append("<h3>One by one</h3>")
    for n, (_, opts, note) in SOUNDS.items():
        parts += [ba.card(f"{n} {k}: {title}", note, b[n][k]) for k, (title, _) in opts.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Falcon Dart Sounds</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Falcon basic attack: dart</h1>
<p class="sub">A ranged dart with more air and whip than the hummingbird's beak. The keen hit (full range) is the loud,
ringing one, so a long shot sounds like a reward. Every A is in the game now as a placeholder. Pick a letter per sound, or
"all A" / "all B".</p>
{''.join(parts)}</main></body></html>"""


def main():
    b = build()
    if "--install" in sys.argv:
        picks = sys.argv[sys.argv.index("--install") + 1].upper().split(",")
        picks = picks if len(picks) == len(SOUNDS) else picks * len(SOUNDS)
        GAME.mkdir(parents=True, exist_ok=True)
        for n, k in zip(SOUNDS, picks):
            write_wav(GAME / f"{n}.wav", b[n][k])
            print(f"{n} <- {k}  {len(b[n][k]) / SR * 1000:.0f} ms  {stats(b[n][k])}")
        return
    for n, opts in b.items():
        for k, x in opts.items():
            print(n, k, f"{len(x) / SR * 1000:.0f} ms", stats(x))
    PAGE.write_text(page(b), encoding="utf-8")
    print("page", PAGE)


if __name__ == "__main__":
    main()
