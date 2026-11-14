#!/usr/bin/env python3
"""Fennec portal-kit sounds built from recorded sounds (Sonniss GDC 2026 bundle).

Built for the abilities that are the same in the kit Preston took on 2026-11-05 (utility mage, portals) and in the
redraft waiting on his "Take it": 1 two-faced shot, 2 pocket gates, 3 far gates, 4 great gate. rift_boom is only in
the redraft and is marked that way. The game's current 8 fennec sounds belong to the old sand/ears kit and are left
alone (hub hold, 2026-11-05); these new names get hooked up when the portal kit's script exists.

One portal motif runs through every gate: a glassy snap, a sci-fi liquid hit, a deep electric hum.
  python tools/audio/fennec_portal_recorded.py                  render all + listen page
  python tools/audio/fennec_portal_recorded.py --install all    copy into audio/sfx/fennec/portal/ (not hooked up)
Sources stay in D:/dev/sound-library (never passed on, never into an AI tool).
"""
import html
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gorilla_recorded as g  # noqa: E402  (shared source list and take())
from pound_recorded import SR, glue, hp, level, load, lp, mix, stats, to_int16, wav_b64, LIB  # noqa: E402

PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "fennec" / "portal"
SCRATCH = Path(r"D:\dev\_scratch\sound\fennec")
PAGE = PROJECT / "docs" / "listen" / "fennec-portal-recorded-2026-11-05.html"

g.F.update({
    "snap": "Cinematic Sound Design - Interface & Infographics/Interface Accept Glassy Snap.wav",
    "ping": "Cinematic Sound Design - System & UI Feedback Elements/Interface Sci-Fi Ping Down.wav",
    "deny": "Cinematic Sound Design - System & UI Feedback Elements/Interface Deny Low Fat Dark.wav",
    "arpdown": "Cinematic Sound Design - System & UI Feedback Elements/Interface Arp Reveal Down Long.wav",
    "liquid": "344 Audio - Elemental Palette Designed Vol. 1/WATRMisc_Water, Liquid Impact, Bubble, Sci Fi, Hit 04_344 Audio_Elemental Palette Designed Vol 1.wav",
    "submerge": "Epic Stock Media - Elemental Mutation Whooshes and Impacts/WATRImpt_Impact Water Deep Submerge Bubble Drown Ship Hit 05_ESM_EMWI.wav",
    "hum": "Jake Fielding - Fridge Hums Vol.2/MACHAppl_Deep Fridge Hum, Buzz, Electric Tone, Deep_Jake Fielding_Fridge Hums Pt2.wav",
    "rhythm": "Jake Fielding - Fridge Hums Vol.2/MACHAppl_Rhythmic Electric Fridge Hum, Buzz, Static,_Jake Fielding_Fridge Hums Pt2.wav",
    "punch": "Epic Stock Media - Anime Game/FGHTImpt_Combat Punch Impact Light Hit Delay Crunchy Vintage Quick Smack 05_ESM_AG.wav",
    "shimmer": "Epic Stock Media - Anime Game/DSGNStngr_Power Up Bright Positive Successful Light Saturation Crash Shimmer 05_ESM_AG.wav",
    "wobble": "Epic Stock Media - Anime Game/DSGNMisc_Misc Monster Tentacle Modulated Creature Shadow Abstract Swept Wobble Lfo 02_ESM_AG.wav",
    "bright": "Epic Stock Media - Fantasy Game 2 - Sound Kit for Enchanted Realms/MAGAngl_Magic Light Spell Enchantment Potion Effect Tonal Bright 03_ESM_FG2.wav",
    "powerup": "InMotionAudio - Arc/ELECArc_ArcPowerUpDesign04_InMotionAudio_Arc.wav",
})
take = g.take


def seg(key, start, dur, fade=0.05):
    """A fixed slice of a long, steady source (hums), peak-normalised with short fades."""
    if key not in g._cache:
        g._cache[key] = load(LIB / g.F[key])
    y = g._cache[key][int(start * SR):int((start + dur) * SR)].copy()
    n = int(fade * SR)
    y[:n] *= np.linspace(0, 1, n)
    y[-n:] *= np.linspace(1, 0, n)
    return y / np.max(np.abs(y))


def pitch(y, r):
    """Resample: r > 1 is higher and shorter."""
    return np.interp(np.arange(0, len(y) - 1, r), np.arange(len(y)), y)


def ramp(y, a=0.0, b=1.0, power=1.0):
    return y * np.linspace(a, b, len(y)) ** power


def tail(y, sec):
    return y[-int(sec * SR):]


# ---- the portal motif -----------------------------------------------------------------------------------------
def gate(dur=0.8, swell=0.22, size=1.0):
    """A gate opening: a reversed glass swell, the glassy snap, a liquid hit, the gate's hum settling."""
    sw = tail(take("glass", 0.2, 0.8, 0.6, 0.2, reverse=True), swell)
    liquid = pitch(take("liquid", 0, 0.4, 0.7, 0.25), 1.0 / size)
    hum = hp(lp(seg("hum", 91.0, dur - swell + 0.05), 2500), 60)
    return mix(dur, (hp(sw, 1200), 0.0, 0.45), (take("snap", 0, 0.2, 0.44, 0.15), swell, 0.8),
               (liquid, swell, 0.85), (hp(take("elec", 0, 0.4, 0.6, 0.25), 400), swell, 0.35),
               (ramp(hum, 1.0, 0.2), swell, 0.35))


# ---- the sounds --------------------------------------------------------------------------------------------
def shot_cast():  # 1: a small gate snaps open behind it, one bolt fires forward and one back
    p = take("ping", 0, 0.3, 0.45, 0.15)
    return glue(mix(0.5, (take("snap", 0, 0.2, 0.44, 0.15), 0.0, 0.6), (p, 0.0, 0.9), (pitch(p, 1.12), 0.06, 0.7),
                    (take("burst", 0, 0.3, 0.31, 0.08), 0.0, 0.55), (hp(take("arc", 0, 0.5, 0.3, 0.1), 2000), 0.0, 0.3)),
                drive=1.3, fade=0.08)


def shot_hit():  # 1: a bolt lands: a crisp hit, an electric bite, a dark downward tone for the slow
    return glue(mix(0.55, (take("punch", 0, 0.3, 0.4, 0.12), 0.0, 0.7), (hp(take("elec", 0, 0.4, 0.5, 0.2), 300), 0.0, 0.8),
                    (hp(take("arc", 0, 0.5, 0.35, 0.12), 1500), 0.0, 0.4), (take("deny", 0, 0.3, 0.55, 0.2), 0.02, 0.5)),
                drive=1.4, fade=0.1)


def gate_open_small():  # 2: pocket gates open (at its feet and a short way off)
    return glue(gate(0.8), drive=1.2, fade=0.12)


def gate_through():  # 2/3/4: stepping or jumping through a gate
    return glue(mix(0.6, (take("sweep", 0, 0.5, 0.5, 0.15), 0.0, 0.8),
                    (hp(take("submerge", 0, 0.5, 0.6, 0.25), 120), 0.0, 0.6),
                    (hp(take("glass", 0.2, 0.8, 0.5, 0.2), 2500), 0.1, 0.3),
                    (take("burst", 0, 0.3, 0.31, 0.08), 0.0, 0.4)), drive=1.3, fade=0.12)


def gate_open_far():  # 3: the entrance gate here, then the exit gate far away, deeper
    return glue(mix(1.2, (gate(0.8), 0.0, 1.0), (pitch(gate(0.85, size=1.18), 0.85), 0.35, 0.7)), drive=1.2, fade=0.15)


def great_charge():  # 4: the charge before the ring opens: reversed impacts, a climbing arp, a hum swelling
    ch = tail(take("chord", 0.1, 0.6, 1.8, 0.5, reverse=True), 1.5)
    el = tail(take("elec", 0, 0.4, 1.6, 0.5, reverse=True), 1.5)
    arp = take("arpdown", 0, 0.3, 1.17, 0.2, reverse=True)  # reversed, the arp climbs
    return glue(mix(1.5, (hp(ch, 200), 0.0, 1.0), (hp(el, 150), 0.0, 0.6), (hp(arp, 600), 0.33, 0.35),
                    (ramp(hp(seg("rhythm", 3.0, 1.5), 100), 0.0, 1.0, 1.5), 0.0, 0.45),
                    (ramp(hp(seg("powerup", 0.0, 1.5), 800), 0.0, 1.0, 2.0), 0.0, 0.3)), drive=1.2, fade=0.03)


def great_open():  # 4: the ring opens under the team and pulls them in: the gate motif, big and low
    big = pitch(gate(1.6, swell=0.05, size=1.4), 0.75)
    return glue(mix(2.0, (big, 0.0, 1.0), (hp(take("chord", 0.1, 0.6, 1.6, 0.5), 250), 0.0, 0.55),
                    (lp(take("boom011", 0, 1.2, 1.6, 0.5), 200), 0.0, 0.5),
                    (hp(take("submerge", 0, 0.5, 0.8, 0.3), 100), 0.15, 0.6),
                    (hp(take("glass", 0.2, 0.8, 0.9, 0.35), 2000), 0.05, 0.35)), drive=1.5, fade=0.25)


def great_arrive():  # 4: the team arrives with a shield and a burst of speed
    return glue(mix(1.2, (take("snap", 0, 0.2, 0.44, 0.15), 0.0, 0.6), (take("liquid", 0, 0.4, 0.7, 0.25), 0.0, 0.6),
                    (take("shimmer", 0, 0.5, 1.2, 0.4), 0.02, 0.7), (hp(take("bright", 0, 0.4, 1.0, 0.4), 500), 0.05, 0.4),
                    (take("sweep", 0, 0.5, 0.5, 0.15), 0.0, 0.5)), drive=1.3, fade=0.2)


def rift_boom():  # 4, redraft only: the ring tears open with a boom that knocks enemies back off it
    return glue(mix(2.0, (lp(take("boom011", 0, 1.2, 2.0, 0.6), 300), 0.0, 1.0),
                    (lp(take("drop", 0, 0.5, 1.4, 0.5), 120, 4), 0.0, 0.6),
                    (hp(take("elec", 0, 0.4, 1.4, 0.5), 150), 0.0, 0.8),
                    (hp(take("glass", 0.2, 0.8, 0.9, 0.35), 1500), 0.03, 0.5),
                    (hp(take("chord", 0.1, 0.6, 1.4, 0.5), 300), 0.0, 0.4),
                    (hp(take("wobble", 0, 0.5, 1.2, 0.4), 200), 0.05, 0.3)), drive=1.7, fade=0.25)


SOUNDS = {  # name: (builder, target LUFS, what it is)
    "shot_cast": (shot_cast, -18, "1 two-faced shot: small gate snaps open, a bolt forward and one back"),
    "shot_hit": (shot_hit, -15, "1 two-faced shot: a bolt hits (damage and a slow)"),
    "gate_open_small": (gate_open_small, -18, "2 pocket gates: the two gates open"),
    "gate_through": (gate_through, -17, "2, 3 and 4: stepping or jumping through a gate"),
    "gate_open_far": (gate_open_far, -17, "3 far gates: the entrance here, the exit far away"),
    "great_charge": (great_charge, -18, "4 great gate: the charge"),
    "great_open": (great_open, -14, "4 great gate: the ring opens under the team"),
    "great_arrive": (great_arrive, -15, "4 great gate: arrival, shield and speed"),
    "rift_boom": (rift_boom, -13, "REDRAFT ONLY, 4 rift boom: the ring tears open and knocks enemies back"),
}
SEQUENCES = [  # (title, [(name, start seconds)]): rough timing, to hear the pieces together
    ("Two-faced shot: cast, then a hit", [("shot_cast", 0.0), ("shot_hit", 0.35)]),
    ("Pocket gates: open, then the fennec jumps through", [("gate_open_small", 0.0), ("gate_through", 0.9)]),
    ("Great gate: charge, open, arrive", [("great_charge", 0.0), ("great_open", 1.5), ("great_arrive", 3.1)]),
    ("Redraft: charge, then rift boom", [("great_charge", 0.0), ("rift_boom", 1.5)]),
]


def card(title, note, x):
    return (f'<section><h2>{html.escape(title)}</h2><p>{html.escape(note)}</p><p class="lbl">{stats(x)}</p>'
            f'<audio controls preload="none" src="data:audio/wav;base64,{wav_b64(x)}"></audio></section>')


def page(built):
    seq = []
    for title, parts in SEQUENCES:
        end = max(t + len(built[n]) / SR for n, t in parts)
        x = mix(end, *[(built[n], t, 1.0) for n, t in parts])
        seq.append(card(title, "rough timing, to hear the pieces together", x / max(1.0, np.max(np.abs(x)) / 0.89)))
    one = [card(n, note, built[n]) for n, (_, _, note) in SOUNDS.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fennec Portal Sounds</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Fennec portal sounds</h1>
<p class="sub">New sounds for the portal kit, built from recorded sounds. Every gate shares one motif (a glassy snap, a sci-fi
liquid hit, a deep electric hum). These are new, so there is no stand-in to compare. The game's current fennec sounds
belong to the old sand and ears kit and are untouched. Say "all good", or name the ones to redo.</p>
<h3>Together</h3>{''.join(seq)}<h3>One by one</h3>{''.join(one)}</main></body></html>"""


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    Path(r"D:\dev\_scratch\sound\pound").mkdir(parents=True, exist_ok=True)
    built = {}
    for name, (build, target, _) in SOUNDS.items():
        built[name] = level(build(), target)
        wavfile.write(SCRATCH / f"{name}.wav", SR, to_int16(built[name]))
        print(f"{name:16s} {stats(built[name])}")
    if len(sys.argv) == 3 and sys.argv[1] == "--install":
        GAME.mkdir(parents=True, exist_ok=True)
        names = list(SOUNDS) if sys.argv[2] == "all" else sys.argv[2].split(",")
        for n in names:
            wavfile.write(GAME / f"{n}.wav", SR, to_int16(built[n]))
            print(f"installed audio/sfx/fennec/portal/{n}.wav")
        return
    PAGE.write_text(page(built), encoding="utf-8")
    print(f"page: {PAGE} ({PAGE.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
