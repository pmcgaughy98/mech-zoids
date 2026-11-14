#!/usr/bin/env python3
"""Gorilla (ape) ability sounds built from recorded sounds (Sonniss GDC 2026 bundle), in the direction of the rhino's
"Titan" ground pound (Preston's pick 2026-11-05): heavy, part machine, part energy.

  python tools/audio/gorilla_recorded.py                         render all 7 + listen page (game files untouched)
  python tools/audio/gorilla_recorded.py --install all           write every sound over audio/sfx/ape/<name>.wav
  python tools/audio/gorilla_recorded.py --install chest_hit,dome_slam   only those

Same names as the synthesised stand-ins from synth_kits.py, so kit_audio.gd needs no change. Each sound is levelled
to what its stand-in measures now. Sources stay in D:/dev/sound-library (never passed on, never into an AI tool).
"""
import html
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parent))  # shared helpers live next to this file
from pound_recorded import (LIB, SR, glue, hp, level, load, lp, mix, onset, stats, to_int16,  # noqa: E402
                            wav_b64)

PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "ape"
SCRATCH = Path(r"D:\dev\_scratch\sound\gorilla")
PAGE = PROJECT / "docs" / "listen" / "gorilla-recorded-2026-11-05.html"

F = {
    "burst": "Epic Stock Media - Fantasy Game 2 - Sound Kit for Enchanted Realms/UIAlert_Collect Scifi Futuristic Electronic Bass Burst Sweep Heavy 04_ESM_FG2.wav",
    "servo": "Epic Stock Media - Tower Defense Game/ROBTMvmt_Tower Deploy Hitech Robot Motor Dark Thump Servo Whine 04_ESM_TDG.wav",
    "sweep": "Cinematic Sound Design - Ultra Transitions & Impacts/Woosh Sweep Slide Infographics Basic.wav",
    "arc": "InMotionAudio - Arc/ELECArc_ArcDesign15_InMotionAudio_Arc.wav",
    "buzz": "InMotionAudio - Arc/ELECBuzz_Buzz27_InMotionAudio_Arc.wav",
    "elec": "Epic Stock Media - Elemental Mutation Whooshes and Impacts/ELECMisc_Impact Electric Tonal Deep Movement Motion Hiss Glitch 01_ESM_EMWI.wav",
    "glass": "Epic Stock Media - Elemental Mutation Whooshes and Impacts/GLASMvmt_Whoosh Glass Crystal Fragments Sharp Shards Dry 05_ESM_EMWI.wav",
    "chord": "Cinematic Sound Design - Ultra Transitions & Impacts/Impact Hit Rapid Chord Reverb.wav",
    "bang": "344 Audio - Haunting Ambiences Vol. 3/METLImpt_Metal Bangs, Metal Hits, Banging On Doors_344 Audio_Haunting Ambiences Vol 3.wav",
    "body": "344 Audio - Cinematic Fight Vol. 1/FGHTImpt_4 x Punch, Body 02_344 Audio_Cinematic Fight Vol 1.wav",
    "boom214": "Federico Soler - Effective Trailer Booms Vol. 2/EffectiveTrailer_Booms_Vol2_214.wav",
    "boom011": "Federico Soler - Effective Trailer Booms Vol. 2/EffectiveTrailer_Booms_Vol2_011.wav",
    "latch": "Epic Stock Media - HD Lock And Mechanism Sound Design Kit/MECHLtch_Click Deep Mechanism Latch Button Nearfield Thunk 02_ESM_HDLM.wav",
    "metwhoosh": "344 Audio - Elemental Palette Designed Vol. 1/METLMisc_Metal, Slow Whoosh, Rattle, Pass By x4 01_344 Audio_Elemental Palette Designed Vol 1.wav",
    "firewhoosh": "Epic Stock Media - Elemental Mutation Whooshes and Impacts/FIREWhsh_Whoosh Fire Deep Growl Monster Saturated Crisp 03_ESM_EMWI.wav",
    "metal": "The Noisery - Moaning Metal/DSGNImpt_Metal Hit Thud Thump Low Ring Geofon 1_The Noisery_Moaning Metal.wav",
    "crunch": "InMotionAudio - Sinister Textures 5/GOREMisc_Concrete_MetalPipe02_InMotionAudio_SinisterTextures5.wav",
    "debris": "Cinematic Sound Design - Colossal Impacts/Woosh Debris.wav",
    "drop": "344 Audio - Bass Drops & Downers Vol. 2/DSGNBass_Bass Drop & Downer Fast 12_344 Audio_Bass Drops & Downers Vol 2.wav",
}
_cache = {}


def take(key, lo=0.0, hi=1.0, dur=1.0, fade_out=0.12, back=0.3, reverse=False):
    """One hit from a source, starting on its transient, peak-normalised. reverse=True flips it into a swell."""
    if key not in _cache:
        _cache[key] = load(LIB / F[key])
    x = _cache[key]
    s = max(0, onset(x, lo, hi, back) - int(0.002 * SR))
    y = x[s:s + int(dur * SR)].copy()
    fi, fo = int(0.002 * SR), int(min(fade_out, dur / 2) * SR)
    y[:fi] *= np.linspace(0, 1, fi)
    y[-fo:] *= np.linspace(1, 0, fo) ** 2
    if reverse:
        y = y[::-1].copy()
    return y / np.max(np.abs(y))


def ramp(y, a=0.0, b=1.0):
    return y * np.linspace(a, b, len(y))


# ---- the seven sounds ---------------------------------------------------------------------------------------
def shield_wind():  # cast of the hex shield: the arm winds up as the emitter charges
    return glue(mix(0.42, (lp(take("servo", 0, 0.5, 0.42, 0.1, 0.25), 6000), 0.0, 0.45),
                    (take("sweep", 0, 0.5, 0.42, 0.12), 0.0, 0.5),
                    (take("burst", 0, 0.3, 0.31, 0.08), 0.03, 1.0),
                    (hp(take("arc", 0, 0.5, 0.3, 0.1), 1500), 0.12, 0.25)), drive=1.2, fade=0.06)


def shield_up():  # the throw frame: green hex panels snap into place, glassy and charged
    return glue(mix(1.1, (take("elec", 0, 0.4, 1.1, 0.4), 0.0, 1.0),
                    (hp(take("glass", 0.2, 0.8, 0.9, 0.35), 1500), 0.02, 0.55),
                    (hp(take("chord", 0.1, 0.6, 1.1, 0.45), 300), 0.0, 0.4)), drive=1.3, fade=0.2)


def chest_hit():  # one beat on the armoured chest: steel bang, a body thud, a little sub
    return glue(mix(0.55, (hp(take("bang", 22.5, 23.5, 0.55, 0.15), 50), 0.0, 1.0),
                    (take("body", 0, 0.7, 0.3, 0.1), 0.0, 0.7),
                    (lp(take("boom214", 0, 1.2, 0.55, 0.2), 140, 4), 0.0, 0.6)), drive=1.6, fade=0.1)


def bound_leap():  # push-off: a deep clunk, the frame rattling through the air on a deep whoosh
    return glue(mix(0.7, (take("latch", 0, 0.2, 0.3, 0.1), 0.0, 0.6),
                    (lp(take("body", 0, 0.7, 0.3, 0.1), 800), 0.0, 0.5),
                    (lp(take("servo", 0, 0.5, 0.6, 0.12, 0.25), 6000), 0.0, 0.35),
                    (take("metwhoosh", 0, 0.5, 0.65, 0.2), 0.04, 0.9),
                    (lp(take("firewhoosh", 0, 0.6, 0.65, 0.2, 0.25), 3000), 0.05, 0.5)), drive=1.3, fade=0.12)


def bound_land():  # the landing: a smaller cousin of the rhino's Titan slam
    return glue(mix(1.4, (lp(take("boom011", 0, 1.2, 1.4, 0.5), 260), 0.0, 1.0),
                    (hp(take("metal", 0, 0.4, 1.4, 0.5), 60), 0.0, 0.8),
                    (take("body", 0, 0.7, 0.35, 0.12), 0.0, 0.6),
                    (hp(take("crunch", 0, 0.44, 0.42, 0.15), 150), 0.002, 0.6),
                    (hp(take("debris", 0.2, 1.4, 1.0, 0.4), 400), 0.04, 0.4)), drive=1.6, fade=0.15)


def dome_rise():  # cast of the hex dome: reversed impacts swell up into the slam, a buzz climbs under them
    r = take("chord", 0.1, 0.6, 1.2, 0.5, reverse=True)[-int(0.9 * SR):]
    e = take("elec", 0, 0.4, 1.0, 0.4, reverse=True)[-int(0.9 * SR):]
    return glue(mix(0.9, (hp(r, 200), 0.0, 1.0), (hp(e, 150), 0.0, 0.6),
                    (ramp(hp(take("buzz", 1.5, 2.5, 0.9, 0.1), 800), 0.0, 1.0), 0.0, 0.3),
                    (lp(take("servo", 0, 0.5, 0.5, 0.12, 0.25), 5000), 0.0, 0.3)), drive=1.2, fade=0.02)


def dome_slam():  # both fists down and the dome goes up: Titan's weight plus a charged, glassy field
    return glue(mix(2.0, (lp(take("boom214", 0, 1.2, 2.0, 0.6), 300), 0.0, 1.0),
                    (hp(take("metal", 0, 0.4, 1.8, 0.6), 50), 0.0, 0.85),
                    (take("body", 0, 0.7, 0.35, 0.12), 0.0, 0.6),
                    (hp(take("crunch", 0, 0.44, 0.42, 0.15), 150), 0.002, 0.6),
                    (hp(take("elec", 0, 0.4, 1.4, 0.5), 200), 0.02, 0.6),
                    (hp(take("glass", 0.2, 0.8, 0.9, 0.35), 2000), 0.06, 0.35),
                    (lp(take("drop", 0, 0.5, 1.4, 0.5), 120, 4), 0.0, 0.5)), drive=1.7, fade=0.2)


SOUNDS = {  # name: (builder, what triggers it)
    "shield_wind": (shield_wind, "1 hex shield, cast"),
    "shield_up": (shield_up, "1 hex shield, the throw frame"),
    "chest_hit": (chest_hit, "2 chest beat, every beat"),
    "bound_leap": (bound_leap, "3 bound, cast"),
    "bound_land": (bound_land, "3 bound, the landing"),
    "dome_rise": (dome_rise, "4 hex dome, cast"),
    "dome_slam": (dome_slam, "4 hex dome, both fists down"),
}


def page(rows):
    cards = []
    for name, trig, a, b in rows:
        cards.append(f"""<section><h2>{html.escape(name)}</h2><p>{html.escape(trig)}</p><div class="two">
<div><p class="lbl">A stand-in &middot; {stats(a)}</p><audio controls preload="none" src="data:audio/wav;base64,{wav_b64(a)}"></audio></div>
<div><p class="lbl">B recorded &middot; {stats(b)}</p><audio controls preload="none" src="data:audio/wav;base64,{wav_b64(b)}"></audio></div></div></section>""")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gorilla Ability Sounds</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} .sub{{color:var(--mute);margin:0 0 20px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 14px}}
h2{{font-size:1.1rem;margin:0 0 2px;font-family:ui-monospace,monospace}} p{{margin:0 0 8px}} .lbl{{color:var(--mute);font-size:.85rem;margin:8px 0 4px}}
audio{{width:100%}} .two{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} @media (max-width:560px){{.two{{grid-template-columns:1fr}}}}
</style></head><body><main><h1>Gorilla ability sounds</h1>
<p class="sub">A is the synthesised stand-in in the game now; B is layered from recorded sounds in the rhino Titan's direction.
Each pair is matched in loudness. Say "all B", or name the ones to keep as A or redo.</p>
{''.join(cards)}</main></body></html>"""


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    Path(r"D:\dev\_scratch\sound\pound").mkdir(parents=True, exist_ok=True)  # pound_recorded.lufs uses it
    install = None
    if len(sys.argv) == 3 and sys.argv[1] == "--install":
        install = list(SOUNDS) if sys.argv[2] == "all" else sys.argv[2].split(",")
    rows = []
    for name, (build, trig) in SOUNDS.items():
        if install is not None and name not in install:
            continue
        a = load(GAME / f"{name}.wav")
        from pound_recorded import lufs
        b = level(build(), lufs(a))
        if install is not None:
            wavfile.write(GAME / f"{name}.wav", SR, to_int16(b))
            print(f"audio/sfx/ape/{name}.wav  {stats(b)}")
            continue
        wavfile.write(SCRATCH / f"{name}_B.wav", SR, to_int16(b))
        rows.append((name, trig, a, b))
        print(f"{name:12s} A {stats(a)} | B {stats(b)}")
    if install is None:
        PAGE.write_text(page(rows), encoding="utf-8")
        print(f"page: {PAGE} ({PAGE.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
