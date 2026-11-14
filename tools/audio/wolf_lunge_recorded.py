"""Wolf, key 1 lunge (2026-11-05): lunge_cast (the leap starts), lunge_bite (the jaws land), lunge_miss (bites air).

WolfKit (scripts/moba3d/wolf_kit.gd) fires cue(name) at those moments: a 0.12 s crouch, then 0.28 s in the air,
then the bite with a 0.07 s hitstop. The wolf is a medium machine, so these sit lighter and quicker than the rhino.
Built from the Sonniss GDC 2026 bundle (D:\\dev\\sound-library, never into an AI tool).

  python -I tools/audio/wolf_lunge_recorded.py                 renders two options per sound and the listen page
  python -I tools/audio/wolf_lunge_recorded.py --install A,B,A writes audio/sfx/wolf/ with cast A, bite B, miss A
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
    "whip": "David Dumais Audio - Melee Weapons Sound Effects Pack 2/WEAPWhip_WHIP Snap Crack 05_DDUMAIS_MWP2.wav",
    "percsnap": "Cinematic Sound Design - Interface & Infographics/Interface Percussion Snap.wav",
    "spring": "Epic Stock Media - HD Lock And Mechanism Sound Design Kit/METLTonl_Item Spring Wire Impact Flick Top Clatter Light Tap Roll Handling Short 01_ESM_HDLM.wav",
})
take, pitch = g.take, fp.pitch
PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "wolf"
PAGE = PROJECT / "docs" / "listen" / "wolf-lunge-2026-11-05.html"
BITE_AT = 0.28  # air_time in wolf_kit.gd: the cast cue to the bite or miss cue


def cast_a():  # Pounce: the leg drives rev up short and a fast blade swish carries the leap
    return glue(mix(0.5, (hp(pitch(take("servo", 0, 1.0, 0.6, 0.15), 1.35), 150), 0.0, 0.7),
                    (hp(take("swish", 0, 1.0, 0.5, 0.2), 300), 0.03, 0.9)), drive=1.3, fade=0.15)


def cast_b():  # Spring: a sprung-steel flick and a latch release, then a quick slide whoosh
    return glue(mix(0.45, (take("spring", 0, 0.5, 0.3, 0.1), 0.0, 0.7),
                    (pitch(take("latch", 0, 0.5, 0.3, 0.1), 1.25), 0.0, 0.5),
                    (hp(take("sweep", 0, 0.5, 0.4, 0.15), 400), 0.04, 0.8)), drive=1.3, fade=0.15)


def bite_a():  # Steel jaws: a heavy clamp (the latch, pitched up), pipe crunch and a short metal ring
    ring = take("ring", 0, 0.4, 0.3, 0.15)
    return glue(mix(0.45, (pitch(take("latch", 0, 0.5, 0.35, 0.12), 1.15), 0.0, 0.9),
                    (hp(take("crunch", 0, 0.44, 0.35, 0.15), 200), 0.0, 0.7),
                    (hp(ring, 400), 0.005, 0.45), (lp(take("body", 0, 0.7, 0.25, 0.1), 500), 0.0, 0.5)),
                drive=1.6, fade=0.15)


def bite_b():  # Crunch: a crisp combat hit and the whip crack low under it, more snap than clamp
    return glue(mix(0.4, (take("punch", 0, 0.4, 0.3, 0.12), 0.0, 0.8),
                    (hp(take("crunch", 0, 0.44, 0.3, 0.12), 250), 0.0, 0.6),
                    (lp(pitch(take("whip", 0, 0.5, 0.35, 0.12), 0.8), 3000), 0.0, 0.5),
                    (lp(take("metal", 0, 0.4, 0.3, 0.12), 900), 0.0, 0.4)), drive=1.5, fade=0.12)


def miss_a():  # Air snap: the jaws snap shut on nothing, a whip crack and a light clack
    return glue(mix(0.42, (hp(pitch(take("whip", 0, 0.5, 0.3, 0.12), 1.1), 600), 0.0, 0.8),
                    (pitch(take("latch", 0, 0.5, 0.25, 0.1), 1.4), 0.0, 0.45)), drive=1.2, fade=0.1)


def miss_b():  # Clack: a dry percussive snap with a small swish tail through the empty air
    return glue(mix(0.4, (take("percsnap", 0, 0.4, 0.25, 0.1), 0.0, 0.8),
                    (pitch(take("latch", 0, 0.5, 0.25, 0.1), 1.5), 0.0, 0.4),
                    (hp(take("swish", 0, 1.0, 0.3, 0.15), 800), 0.02, 0.35)), drive=1.2, fade=0.1)


SOUNDS = {  # name: (target LUFS, {letter: (title, builder)}, what triggers it)
    "lunge_cast": (-18.0, {"A": ("Pounce", cast_a), "B": ("Spring", cast_b)}, "the leap starts"),
    "lunge_bite": (-15.0, {"A": ("Steel jaws", bite_a), "B": ("Crunch", bite_b)}, "the jaws land on a target"),
    "lunge_miss": (-20.0, {"A": ("Air snap", miss_a), "B": ("Clack", miss_b)}, "the bite finds nothing"),
}


def lvl(x, target):
    """level() for short sounds: ebur128 needs a 400 ms block, so pad to 0.5 s to measure, then trim back."""
    n = len(x)
    padded = np.concatenate([x, np.zeros(max(0, int(0.5 * SR) - n))])
    return level(padded, target)[:n]


def build():
    return {n: {k: lvl(f(), t) for k, (_, f) in opts.items()} for n, (t, opts, _) in SOUNDS.items()}


def seq(cast, end):
    x = mix(BITE_AT + len(end) / SR + 0.05, (cast, 0.0, 1.0), (end, BITE_AT, 1.0))
    return x / max(1.0, np.max(np.abs(x)) / 0.89)


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(to_int16(x).tobytes())


def page(b):
    together = []
    for k in "AB":
        together.append(fp.card(f"All {k}: lunge and bite", "cast, then the bite 0.28 s later", seq(b["lunge_cast"][k], b["lunge_bite"][k])))
        together.append(fp.card(f"All {k}: lunge and miss", "cast, then the miss 0.28 s later", seq(b["lunge_cast"][k], b["lunge_miss"][k])))
    one = []
    for n, (_, opts, note) in SOUNDS.items():
        one += [fp.card(f"{n} {k}: {title}", note, b[n][k]) for k, (title, _) in opts.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wolf Lunge Sounds</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Wolf lunge (key 1)</h1>
<p class="sub">Three moments: the leap, the bite, and a miss. Two options each, built from recorded sounds. The wolf is
a medium machine, so these are lighter and quicker than the rhino. Say "All A", "All B", or pick per sound.</p>
<h3>Together</h3>{''.join(together)}<h3>One by one</h3>{''.join(one)}</main></body></html>"""


def main():
    b = build()
    if "--install" in sys.argv:
        picks = sys.argv[sys.argv.index("--install") + 1].upper().split(",")
        GAME.mkdir(parents=True, exist_ok=True)
        for n, k in zip(SOUNDS, picks if len(picks) == 3 else picks * 3):
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
