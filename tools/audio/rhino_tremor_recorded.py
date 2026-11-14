"""Rhino kit, 2026-11-05 rework: the tremor's stomps (key 2) and the horn dash and toss (key 1).

The tremor: a cast (pound_rear), the slam at 0.7 s (pound_slam, option D Titan), then 4 stomps about 0.43 s
apart in a 4 m circle that slows. Only the slam had a sound. Key 1: a 0.15 s head-down, a 3.5 m dash, a catch
with a 0.08 s hitstop, then the target thrown 3 m behind. It had no sound at all.

Built from the Sonniss GDC 2026 bundle (D:\\dev\\sound-library, never into an AI tool), with the helpers from the
other *_recorded.py scripts.

  python -I tools/audio/rhino_tremor_recorded.py               renders the options and the listen page
  python -I tools/audio/rhino_tremor_recorded.py --install A   writes tremor_stomp.wav (option A) and the three
                                                               key 1 sounds to audio/sfx/rhino/
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gorilla_recorded as g  # noqa: E402
import fennec_portal_recorded as fp  # noqa: E402  (adds its sources to g.F)
from pound_recorded import SR, SRC, hp, lp, load, mix, glue, level, stats, to_int16  # noqa: E402

g.F["ring"] = SRC["ring"]
take, pitch = g.take, fp.pitch
PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "rhino"
PAGE = PROJECT / "docs" / "listen" / "rhino-tremor-and-dash-2026-11-05.html"
SLAM_AT, STOMP_GAP = 0.70, 0.43  # from MATCH_NOTES: slam at 0.7 s, stomps measured 0.43 s apart
STOMP_LUFS = -21.0  # lighter than the slam (-19.1 over 1.9 s); four of them in a row


# ---- tremor stomp options -------------------------------------------------------------------------------------
def stomp_ground():  # a short trailer boom under a body thud, a little grit: the ground taking the weight
    return glue(mix(0.55, (lp(take("boom011", 0, 1.2, 0.55, 0.3), 180), 0.0, 1.0),
                    (lp(take("body", 0, 0.7, 0.3, 0.12), 300), 0.0, 0.6),
                    (hp(take("debris", 0.2, 1.4, 0.45, 0.25), 500), 0.02, 0.22)), drive=1.5, fade=0.2)


def stomp_foot():  # the steel foot: a low metal ring and the latch clank over a sub thump
    return glue(mix(0.55, (lp(take("metal", 0, 0.4, 0.55, 0.3), 1200), 0.0, 0.85),
                    (take("latch", 0, 0.5, 0.3, 0.1), 0.0, 0.45),
                    (lp(take("boom214", 0, 1.2, 0.55, 0.3), 150), 0.0, 0.8)), drive=1.4, fade=0.2)


def stomp_rumble():  # heavier and longer: each stomp's rumble runs into the next, so the circle trembles
    return glue(mix(0.75, (lp(take("boom011", 0, 1.2, 0.75, 0.45), 140), 0.0, 1.0),
                    (hp(take("crunch", 0, 0.44, 0.35, 0.15), 150), 0.0, 0.35),
                    (lp(take("drop", 0, 0.6, 0.75, 0.45), 200), 0.0, 0.45),
                    (hp(take("debris", 0.2, 1.4, 0.7, 0.4), 400), 0.05, 0.2)), drive=1.6, fade=0.35)


STOMPS = {
    "A": ("Ground", "a short boom under a body thud with a little grit: the ground taking the weight", stomp_ground),
    "B": ("Steel foot", "a low metal ring and a latch clank over a sub thump: the machine's foot", stomp_foot),
    "C": ("Rumble", "heavier, with a rumble that runs into the next stomp so the circle keeps trembling", stomp_rumble),
}


# ---- key 1: horn dash and toss (one each, a first pass) -------------------------------------------------------
def dash_cast():  # the head-down: a latch clunk, then the drive revs and a heavy metal whoosh as it charges
    servo = pitch(take("servo", 0, 1.0, 0.9, 0.2), 0.8)
    return glue(mix(0.7, (take("latch", 0, 0.5, 0.3, 0.1), 0.0, 0.6), (hp(servo, 120), 0.05, 0.6),
                    (hp(take("metwhoosh", 0, 1.0, 0.6, 0.25), 200), 0.12, 0.8)), drive=1.4, fade=0.2)


def horn_catch():  # the horn hooks the target: a metal hit with a ringing tail and a body punch, short for the hitstop
    return glue(mix(0.6, (take("ring", 0, 0.4, 0.6, 0.3), 0.0, 0.9), (take("body", 0, 0.7, 0.3, 0.12), 0.0, 0.7),
                    (take("punch", 0, 0.4, 0.25, 0.1), 0.0, 0.4)), drive=1.5, fade=0.2)


def toss_land():  # the thrown machine lands behind the rhino: a body thud, a small boom, some debris
    return glue(mix(0.8, (lp(take("body", 0, 0.7, 0.35, 0.12), 400), 0.0, 0.8),
                    (lp(take("boom214", 0, 1.2, 0.7, 0.4), 200), 0.0, 0.7),
                    (hp(take("debris", 0.2, 1.4, 0.6, 0.3), 400), 0.03, 0.35)), drive=1.5, fade=0.25)


DASH = {  # name: (builder, target LUFS, what triggers it)
    "dash_cast": (dash_cast, -18.0, "key 1 cast: the head-down and the charge"),
    "horn_catch": (horn_catch, -15.0, "key 1 catch: the horn hooks a target (impact 0.5)"),
    "toss_land": (toss_land, -16.0, "key 1: the thrown target lands behind (impact 0.4)"),
}


def build():
    stomps = {k: level(f(), STOMP_LUFS) for k, (_, _, f) in STOMPS.items()}
    dash = {n: level(f(), t) for n, (f, t, _) in DASH.items()}
    return stomps, dash


def game_wav(name):
    return load(GAME / f"{name}.wav")


def tremor_sequence(stomp):
    nudges = (1.0, 0.97, 1.03, 0.99)  # a small pitch nudge per stomp, so four in a row don't sound looped
    rear, slam = game_wav("pound_rear"), game_wav("pound_slam")
    layers = [(rear, 0.0, 1.0), (slam, SLAM_AT, 1.0)]
    layers += [(pitch(stomp, r), SLAM_AT + STOMP_GAP * (i + 1), 1.0) for i, r in enumerate(nudges)]
    end = SLAM_AT + STOMP_GAP * 4 + len(stomp) / SR + 0.1
    x = mix(max(end, SLAM_AT + len(slam) / SR), *layers)
    return x / max(1.0, np.max(np.abs(x)) / 0.89)


def dash_sequence(d):
    x = mix(1.5, (d["dash_cast"], 0.0, 1.0), (d["horn_catch"], 0.40, 1.0), (d["toss_land"], 0.95, 1.0))
    return x / max(1.0, np.max(np.abs(x)) / 0.89)


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(to_int16(x).tobytes())


def page(stomps, dash):
    seq = [fp.card(f"{k}. {name}, in the tremor", "the cast, the Titan slam at 0.7 s, then this stomp 4 times "
                   "0.43 s apart (rough timing)", tremor_sequence(stomps[k])) for k, (name, _, _) in STOMPS.items()]
    one = [fp.card(f"{k}. {name}, one stomp", note, stomps[k]) for k, (name, note, _) in STOMPS.items()]
    d = [fp.card("Key 1 together", "cast, catch at 0.4 s, landing at about 0.95 s (rough timing)", dash_sequence(dash))]
    d += [fp.card(n, note, dash[n]) for n, (_, _, note) in DASH.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rhino Tremor Sounds</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Rhino: tremor stomps and horn dash</h1>
<p class="sub">The tremor's 4 stomps had no sound. Only the first slam did. Key 1 (dash, catch, toss) had none at all.
All of these are built from recorded sounds. Pick a stomp letter. The key 1 sounds are one first pass each:
say "good" or name the ones to redo.</p>
<h3>Tremor, in order</h3>{''.join(seq)}<h3>Stomp, one by one</h3>{''.join(one)}
<h3>Key 1: horn dash and toss</h3>{''.join(d)}</main></body></html>"""


def main():
    stomps, dash = build()
    if "--install" in sys.argv:
        k = sys.argv[sys.argv.index("--install") + 1].upper()
        write_wav(GAME / "tremor_stomp.wav", stomps[k])
        print(f"tremor_stomp <- {k}  {stats(stomps[k])}")
        if "--no-dash" in sys.argv:  # the stomp only; key 1's sounds wait on his OK
            return
        for n, x in dash.items():
            write_wav(GAME / f"{n}.wav", x)
            print(f"{n}  {stats(x)}")
        return
    for k, x in stomps.items():
        print("stomp", k, STOMPS[k][0], stats(x))
    for n, x in dash.items():
        print(n, stats(x))
    PAGE.write_text(page(stomps, dash), encoding="utf-8")
    print("page", PAGE)


if __name__ == "__main__":
    main()
