"""pit_taken.wav: a team takes a side pit. A lock clunk, then a rising tone, foundry style.

Built from the Sonniss GDC 2026 bundle (D:\\dev\\sound-library, never into an AI tool), with the helpers from
pound_recorded, gorilla_recorded and fennec_portal_recorded.

  python -I tools/audio/pit_taken_recorded.py              renders the options and the listen page
  python -I tools/audio/pit_taken_recorded.py --install A  writes audio/sfx/map/pit_taken.wav from option A
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gorilla_recorded as g  # noqa: E402
import fennec_portal_recorded as fp  # noqa: E402
from pound_recorded import SR, SRC, hp, lp, mix, glue, level, stats, to_int16  # noqa: E402

g.F["ring"] = SRC["ring"]
take, seg, ramp = g.take, fp.seg, fp.ramp
PROJECT = Path(__file__).resolve().parents[2]
OUT = PROJECT / "audio" / "sfx" / "map" / "pit_taken.wav"
PAGE = PROJECT / "docs" / "listen" / "pit-taken-2026-11-05.html"
TARGET = -15.0  # between tower_hit (-15) and camp_aggro (-16); tower_down is -13


def glide(y, r0, r1, dur):
    """Pitch that climbs from rate r0 to r1 over dur seconds (r > 1 is higher)."""
    idx = np.cumsum(np.linspace(r0, r1, int(dur * SR)))
    idx = idx[idx < len(y) - 1]
    return np.interp(idx, np.arange(len(y)), y)


def clunk(weight=1.0):
    """The lock: the deep latch thunk, a short low metal ring under it, a little body."""
    return mix(0.5, (take("latch", 0, 0.5, 0.4, 0.12), 0.0, 1.0),
               (lp(take("metal", 0, 0.4, 0.5, 0.2), 900), 0.0, 0.45 * weight),
               (lp(take("body", 0, 0.7, 0.3, 0.1), 300), 0.0, 0.35 * weight))


def a_ring():  # the metal ring's own tail climbs, a bright shimmer caps it
    ring = take("ring", 0, 0.4, 2.4, 0.4)[int(0.08 * SR):]
    rise = ramp(hp(glide(ring, 0.9, 2.2, 0.9), 200), 0.25, 1.0, 1.5)
    return glue(mix(1.4, (clunk(), 0.0, 1.0), (rise, 0.10, 0.75),
                    (hp(take("shimmer", 0, 0.5, 0.5, 0.3), 1500), 0.88, 0.35)), drive=1.3, fade=0.3)


def b_servo():  # the tower servo whines upward like a winch locking home, a sci-fi bass burst pays it off
    servo = take("servo", 0, 1.0, 0.9, 0.2)  # the source is 1.04 s, its whine about 0.1 to 0.6 s
    rise = ramp(hp(glide(servo, 0.8, 1.4, 0.6), 150), 0.5, 1.0)
    return glue(mix(1.4, (clunk(1.2), 0.0, 1.0), (hp(take("bang", 0, 0.5, 0.25, 0.1), 300), 0.0, 0.3),
                    (rise, 0.06, 0.75), (take("burst", 0, 0.6, 0.6, 0.25), 0.6, 0.55)), drive=1.4, fade=0.25)


def c_hum():  # a deep plant hum spins up through the lock, an arc power-up climbs with it
    hum = hp(lp(seg("hum", 91.0, 3.0), 4000), 80)
    rise = ramp(glide(hum, 1.0, 3.0, 0.9), 0.2, 1.0, 1.3)
    return glue(mix(1.4, (clunk(), 0.0, 1.0), (rise, 0.06, 0.6),
                    (hp(take("powerup", 0, 1.0, 1.0, 0.3), 400), 0.1, 0.4),
                    (hp(take("snap", 0, 0.2, 0.4, 0.15), 800), 0.95, 0.3)), drive=1.5, fade=0.3)


OPTIONS = {
    "A": ("Ring", "the lock's own metal ring climbs, a bright shimmer on top", a_ring),
    "B": ("Winch", "a servo whines up like a winch locking home, a bass burst pays it off", b_servo),
    "C": ("Spin-up", "a deep plant hum spins up through the lock with an electric climb", c_hum),
}


def build():
    return {k: level(f(), TARGET) for k, (_, _, f) in OPTIONS.items()}


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(to_int16(x).tobytes())


def page(built):
    cards = [fp.card(f"{k}. {name}", note, built[k]) for k, (name, note, _) in OPTIONS.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pit Taken Sound</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Pit taken</h1>
<p class="sub">Plays at the pit when a team captures it, with a light flash and a small camera shake. Each one is a
lock clunk, then a rising tone, built from recorded sounds and levelled to {TARGET:.0f} LUFS like the other map
events. Pick a letter.</p>{''.join(cards)}</main></body></html>"""


def main():
    built = build()
    if "--install" in sys.argv:
        k = sys.argv[sys.argv.index("--install") + 1].upper()
        write_wav(OUT, built[k])
        print(f"installed {k} -> {OUT}  {stats(built[k])}")
        return
    for k, x in built.items():
        print(k, OPTIONS[k][0], stats(x))
    PAGE.write_text(page(built), encoding="utf-8")
    print("page", PAGE)


if __name__ == "__main__":
    main()
