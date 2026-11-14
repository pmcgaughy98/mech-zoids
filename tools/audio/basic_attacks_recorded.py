"""Basic attacks for the fennec (a gate-light dart) and the wolf (a short melee bite), 2026-11-05.

Preston: "we need basic attacks... have them message the sessions they need". Both kits fire cue(name):
  fennec_kit.gd  basic_cast  on the press (every 0.9 s): a quick zip or tick, under about 150 ms
                 basic_hit   the dart strikes (up to 6.5 m): a small crystal spark, not a thud; no miss cue
  wolf_kit.gd    basic_bite  a hit (every 0.8 s, after a 0.08 s wind-up): a short jaw snap, smaller than lunge_bite
                 basic_whiff the jaws snap air
The fennec uses the portal palette (glassy snap, sci-fi ping, crystal), and the wolf uses smaller, quicker cuts of its
lunge sounds. Built from the Sonniss GDC 2026 bundle (D:\\dev\\sound-library, never into an AI tool).

  python -I tools/audio/basic_attacks_recorded.py                       renders the options and the listen page
  python -I tools/audio/basic_attacks_recorded.py --install fennec A,B  writes audio/sfx/fennec/ with cast A, hit B
  python -I tools/audio/basic_attacks_recorded.py --install wolf A      writes audio/sfx/wolf/ with both A
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wolf_lunge_recorded as w  # noqa: E402  (adds its sources to g.F, and brings the gorilla and fennec helpers)
import gorilla_recorded as g  # noqa: E402
import fennec_portal_recorded as fp  # noqa: E402
from pound_recorded import SR, hp, lp, mix, glue, level, stats, to_int16  # noqa: E402

take, pitch = g.take, fp.pitch
PROJECT = Path(__file__).resolve().parents[2]
PAGE = PROJECT / "docs" / "listen" / "basic-attacks-fennec-wolf-2026-11-05.html"


def cut(x, sec, fade=0.03):
    """Trim to sec with a short fade, for the tight repeating sounds."""
    y = x[:int(sec * SR)].copy()
    n = int(fade * SR)
    y[-n:] *= np.linspace(1, 0, n) ** 2
    return y


# ---- fennec: a violet dart of gate light ------------------------------------------------------------------------
def f_cast_a():  # Glass tick: the glassy snap, high and tiny, with a sci-fi ping flicked upward
    return cut(glue(mix(0.15, (hp(pitch(take("snap", 0, 0.2, 0.2, 0.08), 1.3), 1500), 0.0, 0.9),
                        (hp(pitch(take("ping", 0, 0.3, 0.2, 0.08), 1.6), 2000), 0.0, 0.4)), drive=1.2, fade=0.06), 0.14)


def f_cast_b():  # Zip: an electric arc tick and a fast high swish, like light leaving
    return cut(glue(mix(0.15, (hp(take("arc", 0, 0.4, 0.15, 0.06), 1500), 0.0, 0.6),
                        (hp(pitch(take("swish", 0, 1.0, 0.25, 0.08), 1.6), 2500), 0.0, 0.7)), drive=1.2, fade=0.06), 0.14)


def f_hit_a():  # Crystal spark: shard fragments and a small glassy snap, a little electric bite
    return glue(mix(0.32, (hp(take("glass", 0.2, 0.8, 0.3, 0.15), 2500), 0.0, 0.8),
                    (pitch(take("snap", 0, 0.2, 0.25, 0.1), 1.15), 0.0, 0.6),
                    (hp(take("elec", 0, 0.4, 0.2, 0.1), 1200), 0.0, 0.25)), drive=1.2, fade=0.12)


def f_hit_b():  # Chime spark: a short bright shimmer and a ping, lighter and more musical
    return glue(mix(0.32, (hp(take("shimmer", 0, 0.5, 0.3, 0.15), 1500), 0.0, 0.7),
                    (hp(pitch(take("ping", 0, 0.3, 0.25, 0.1), 1.3), 1500), 0.0, 0.5),
                    (hp(take("glass", 0.2, 0.8, 0.2, 0.1), 3000), 0.0, 0.3)), drive=1.2, fade=0.12)


# ---- wolf: a short melee bite -------------------------------------------------------------------------------------
def w_bite_a():  # Small steel jaws: the lunge's Steel jaws, quicker and higher
    return cut(pitch(w.bite_a(), 1.15), 0.3)


def w_bite_b():  # Small crunch: the lunge's Crunch, quicker and higher
    return cut(pitch(w.bite_b(), 1.15), 0.3)


def w_whiff_a():  # Small air snap: the lunge's miss, tighter
    return cut(pitch(w.miss_a(), 1.12), 0.25)


def w_whiff_b():  # Small clack: the lunge's other miss, tighter
    return cut(pitch(w.miss_b(), 1.12), 0.25)


def w_bite_c():  # Snap trap: made for the basic, not cut from the lunge: a sharp latch, a dry percussive snap, a bit of crunch
    return cut(glue(mix(0.3, (pitch(take("latch", 0, 0.5, 0.25, 0.08), 1.3), 0.0, 0.9),
                        (take("percsnap", 0, 0.4, 0.2, 0.08), 0.0, 0.6),
                        (hp(take("crunch", 0, 0.44, 0.2, 0.08), 400), 0.0, 0.45)), drive=1.4, fade=0.08), 0.25)


def w_whiff_c():  # Click: the jaws click shut on nothing, a light snap and a thin swish
    return cut(glue(mix(0.25, (pitch(take("percsnap", 0, 0.4, 0.2, 0.08), 1.1), 0.0, 0.7),
                        (hp(take("swish", 0, 1.0, 0.2, 0.08), 1500), 0.0, 0.35)), drive=1.2, fade=0.06), 0.2)


MECHS = {  # mech: (dir, {sound: (target LUFS, {letter: (title, builder)}, note)}, preview gap s, hit delay s)
    "fennec": ("fennec", {
        "basic_cast": (-22.0, {"A": ("Glass tick", f_cast_a), "B": ("Zip", f_cast_b)}, "the press: the dart leaves, every 0.9 s"),
        "basic_hit": (-18.0, {"A": ("Crystal spark", f_hit_a), "B": ("Chime spark", f_hit_b)}, "the dart strikes, a small spark"),
    }, 0.9, 0.3),
    "wolf": ("wolf", {
        "basic_bite": (-17.0, {"A": ("Small steel jaws", w_bite_a), "B": ("Small crunch", w_bite_b), "C": ("Snap trap", w_bite_c)}, "a hit, every 0.8 s"),
        "basic_whiff": (-21.0, {"A": ("Small air snap", w_whiff_a), "B": ("Small clack", w_whiff_b), "C": ("Click", w_whiff_c)}, "the jaws snap air"),
    }, 0.8, None),
}


def lvl(x, target):
    """level() for short sounds: ebur128 needs a 400 ms block, so pad to 0.5 s to measure, then trim back."""
    n = len(x)
    return level(np.concatenate([x, np.zeros(max(0, int(0.5 * SR) - n))]), target)[:n]


def build():
    return {m: {n: {k: lvl(f(), t) for k, (_, f) in opts.items()} for n, (t, opts, _) in sounds.items()}
            for m, (_, sounds, _, _) in MECHS.items()}


def preview(m, b, k):
    """Three attacks in a row with small pitch nudges: fennec cast+hit, cast+hit, cast (out of range); wolf bite, bite, whiff."""
    _, sounds, gap, delay = MECHS[m]
    names = list(sounds)
    layers = []
    for i, r in enumerate((1.0, 1.02, 0.98)):
        if m == "fennec":
            layers.append((pitch(b[m][names[0]][k], r), i * gap, 1.0))
            if i < 2:
                layers.append((pitch(b[m][names[1]][k], r), i * gap + delay, 1.0))
        else:
            layers.append((pitch(b[m][names[0 if i < 2 else 1]][k], r), i * gap, 1.0))
    x = mix(2 * gap + 0.6, *layers)
    return x / max(1.0, np.max(np.abs(x)) / 0.89)


def card(title, note, x):
    """fp.card, but labelled by length and peak: ebur128 can't measure under 400 ms, so LUFS would read -70."""
    import html
    from pound_recorded import wav_b64
    lbl = f"{len(x) / SR * 1000:.0f} ms, peak {20 * np.log10(np.max(np.abs(x)) + 1e-9):.1f} dBFS"
    return (f'<section><h2>{html.escape(title)}</h2><p>{html.escape(note)}</p><p class="lbl">{lbl}</p>'
            f'<audio controls preload="none" src="data:audio/wav;base64,{wav_b64(x)}"></audio></section>')


def write_wav(path, x):
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(to_int16(x).tobytes())


def page(b):
    parts = []
    for m, (_, sounds, _, _) in MECHS.items():
        parts.append(f"<h3>{m.capitalize()}: in a fight</h3>")
        parts += [card(f"All {k}", "three attacks in a row", preview(m, b, k)) for k in sorted(b[m][next(iter(sounds))])]
        parts.append(f"<h3>{m.capitalize()}: one by one</h3>")
        for n, (_, opts, note) in sounds.items():
            parts += [card(f"{n} {k}: {title}", note, b[m][n][k]) for k, (title, _) in opts.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fennec and Wolf Basics</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Basic attacks: fennec and wolf</h1>
<p class="sub">The fennec's gate-light dart (a tiny tick, then a crystal spark), and the wolf's short bite (smaller cuts of its
lunge, plus a C made just for the bite). Option A is in the game now as a placeholder for both. Pick a letter per sound, or "all A" / "all B" per mech.</p>
{''.join(parts)}</main></body></html>"""


def main():
    b = build()
    if "--install" in sys.argv:
        i = sys.argv.index("--install")
        m, picks = sys.argv[i + 1], sys.argv[i + 2].upper().split(",")
        d, sounds, _, _ = MECHS[m]
        out = PROJECT / "audio" / "sfx" / d
        for n, k in zip(sounds, picks if len(picks) == len(sounds) else picks * len(sounds)):
            write_wav(out / f"{n}.wav", b[m][n][k])
            print(f"{m} {n} <- {k}  {stats(b[m][n][k])}")
        return
    for m, sounds in b.items():
        for n, opts in sounds.items():
            for k, x in opts.items():
                print(m, n, k, f"{len(x) / SR * 1000:.0f} ms", stats(x))
    PAGE.write_text(page(b), encoding="utf-8")
    print("page", PAGE)


if __name__ == "__main__":
    main()
