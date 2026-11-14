#!/usr/bin/env python3
"""Machine AI voice treatment. Every voice line in the game goes through this one script.

Preston's call (2026-11-04): each machine's own onboard AI speaks its lines. The raw voice comes
from ElevenLabs (a designed voice per machine); this script turns it into a mecha beast, the same
way every time. His reference for the feel (structure only, never their audio): SMITE's G.E.B. 1
and Tremor Tech Cabrakan skins, a real voice underneath with the machine clearly on top.

Usage (from the project folder):
    python tools/audio/mech_voice.py <input file> <machine> <line name> [--amount 1.0] [--out file]
    python tools/audio/mech_voice.py take.mp3 rhino ability_2
writes audio/voice/rhino/ability_2.ogg (res://audio/voice/rhino/ability_2.ogg)

The chain, in order:
  1. clean: mono 48 kHz, cut rumble below 90 Hz and hiss above 9 kHz
  2. size: big machines sit lower, small ones higher (pitch only, timing unchanged)
  3. four layers, each matched in loudness to the voice before mixing, so the blend is predictable:
       voice   the designed voice itself, which carries the words
       robot   the same voice resynthesised as a buzz at a fixed pitch (the classic robot voice)
       sub     the voice an octave down, under 400 Hz: the beast's chest
       ring    ring modulation: the synthetic edge that says "not a person"
  4. metal: two resonant peaks (1.15 and 2.7 kHz) and two very short echoes, a voice inside a hull
  5. growl: drive into a soft clipper, then a light bitcrush blended under it
  6. glue: compressor, then every line set to the same loudness (-16 LUFS) with a peak limiter
  7. tidy: trim silence at both ends, 5 ms fade in, 40 ms fade out
--amount scales the machine (layers, metal, growl): 0.6 light (the default, Preston's pick for the
rhino), 1.0 standard, 1.5 heavy. Voice lines are generated on eleven_v3, the model the voices are
designed on; eleven_v4 drifted away from the designed rhino voice.
Tune a size class in SIZES; every machine of that size follows.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import istft, stft

PROJECT = Path(__file__).resolve().parents[2]
SR = 48000

# Size class from the roster ids in docs/plan/moba-kits.md (rhino_l, kangaroo_m, fennec_s ...).
MACHINES = {
    "rhino": "L", "ape": "L", "hippo": "L", "lobster": "L",
    "kangaroo": "M", "pangolin": "M", "wolf": "M", "shoebill": "M", "falcon": "M", "chameleon": "M",
    "squirrel": "S", "hummingbird": "S", "fennec": "S",
    "announcer": "PA",  # the foundry overseer (2026-11-05): the plant AI on the PA, not a machine body
}
ALIASES = {"gorilla": "ape"}

SIZES = {
    # pitch: 1.0 = unchanged. robot_hz: pitch of the robot buzz. ring_hz: ring mod carrier.
    # ring / robot / sub: layer level against the voice (1.0 = as loud as the voice).
    # metal_db: height of the two resonant peaks. drive_db: push into the soft clipper.
    # hull_ms / hull_decay: the two short echoes. bits / grit: bitcrush depth and blend.
    "L": {"pitch": 0.84, "robot_hz": 82, "ring_hz": 34, "ring": 0.22, "robot": 0.55, "sub": 0.40,
          "metal_db": 3.5, "drive_db": 5, "hull_ms": (9, 17), "hull_decay": (0.32, 0.22), "bits": 9, "grit": 0.20},
    "M": {"pitch": 1.00, "robot_hz": 125, "ring_hz": 52, "ring": 0.18, "robot": 0.45, "sub": 0.15,
          "metal_db": 3.0, "drive_db": 4, "hull_ms": (6, 11), "hull_decay": (0.28, 0.18), "bits": 10, "grit": 0.16},
    "S": {"pitch": 1.10, "robot_hz": 190, "ring_hz": 78, "ring": 0.15, "robot": 0.40, "sub": 0.0,
          "metal_db": 2.5, "drive_db": 3, "hull_ms": (4, 7), "hull_decay": (0.24, 0.15), "bits": 11, "grit": 0.12},
    # PA: the announcer. Preston: "a good base", so no pitch change and thin machine layers. band: a loudspeaker
    # horn (cuts lows and highs). hall: the PA bouncing off the foundry walls (delays ms, decays), after the glue.
    "PA": {"pitch": 1.00, "robot_hz": 110, "ring_hz": 45, "ring": 0.10, "robot": 0.30, "sub": 0.0,
           "metal_db": 2.0, "drive_db": 2, "hull_ms": (5, 9), "hull_decay": (0.20, 0.12), "bits": 12, "grit": 0.08,
           "band": (220, 6500), "hall": ("170|330|540", "0.20|0.12|0.07")},
}

CLEAN = "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=mono,highpass=f=90,lowpass=f=9000"


def run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-2000:])
    return r


def ff(*args):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args])


def has_rubberband():
    r = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
    return " rubberband " in r.stdout


def shift(ratio, rubberband):
    if ratio == 1.0:
        return "anull"
    if rubberband:
        return f"rubberband=pitch={ratio}"
    return f"asetrate={SR * ratio:.0f},aresample={SR},atempo={1 / ratio:.4f}"  # fallback, keeps timing


def loudness(path):
    """Integrated loudness in LUFS, or None when the clip is too short to measure."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                        "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True)
    found = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(found[-1]) if found else None


def read(path, n=None):
    x = wavfile.read(path)[1].astype(np.float64)
    if n is not None:
        x = np.pad(x, (0, max(0, n - len(x))))[:n]
    return x


def rms(x):
    return float(np.sqrt(np.mean(x ** 2))) + 1e-12


def robotize(x, hz):
    """Keep the voice's spectrum, throw away its pitch: every frame becomes one pulse, so the
    voice buzzes at a fixed pitch (frames per second = hz). The (-1)^k phase centres each pulse
    in its window so nothing is lost at the window edges."""
    hop = int(round(SR / hz))
    win = hop * 4
    _, _, z = stft(x, SR, window="hann", nperseg=win, noverlap=win - hop)
    k = np.arange(z.shape[0])[:, None]
    _, y = istft(np.abs(z) * (-1.0) ** k, SR, window="hann", nperseg=win, noverlap=win - hop)
    return np.pad(y, (0, max(0, len(x) - len(y))))[:len(x)]


def treat(src, out, p, amount, target):
    rb = has_rubberband()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        ff("-i", src, "-af", f"{CLEAN},{shift(p['pitch'], rb)}", "-c:a", "pcm_f32le", tmp / "voice.wav")
        voice = read(tmp / "voice.wav")
        n = len(voice)
        mix = voice.copy()
        if p["sub"] > 0:
            ff("-i", tmp / "voice.wav", "-af", f"{shift(0.5, rb)},lowpass=f=400", "-c:a", "pcm_f32le", tmp / "sub.wav")
            sub = read(tmp / "sub.wav", n)
            mix += p["sub"] * amount * sub * rms(voice) / rms(sub)
        robot = robotize(voice, p["robot_hz"])
        mix += p["robot"] * amount * robot * rms(voice) / rms(robot)
        ring = voice * np.sin(2 * np.pi * p["ring_hz"] * np.arange(n) / SR)
        mix += p["ring"] * amount * ring * rms(voice) / rms(ring)
        wavfile.write(tmp / "mix.wav", SR, (0.5 * mix / np.max(np.abs(mix))).astype(np.float32))

        d1, d2 = p["hull_ms"]
        k1, k2 = p["hull_decay"]
        metal = p["metal_db"] * amount
        post = ",".join([
            f"equalizer=f=1150:t=q:w=4:g={metal:.2f}",
            f"equalizer=f=2700:t=q:w=5:g={metal * 0.75:.2f}",
            f"aecho=0.9:0.85:{d1}|{d2}:{k1}|{k2}",
            f"volume={p['drive_db'] * amount:.2f}dB,asoftclip=type=tanh:oversample=2",
            f"acrusher=bits={p['bits']}:mix={min(1.0, p['grit'] * amount):.2f}:mode=log:aa=0.5",
            "acompressor=threshold=0.1:ratio=3:attack=5:release=80:makeup=2",
            *([f"highpass=f={p['band'][0]},lowpass=f={p['band'][1]}"] if "band" in p else []),
            *([f"apad=pad_dur=0.6,aecho=1.0:1.0:{p['hall'][0]}:{p['hall'][1]}"] if "hall" in p else []),
            "silenceremove=start_periods=1:start_threshold=-45dB",
            "areverse,silenceremove=start_periods=1:start_threshold=-45dB,afade=t=in:d=0.04,areverse",
            "afade=t=in:d=0.005",
        ])
        ff("-i", tmp / "mix.wav", "-af", post, "-c:a", "pcm_f32le", tmp / "post.wav")
        lufs = loudness(tmp / "post.wav")
        gain = target - lufs if lufs is not None and lufs > -60 else 0.0
        codec = ["-c:a", "libvorbis", "-q:a", "6"] if out.suffix == ".ogg" else ["-c:a", "pcm_s16le"]
        ff("-i", tmp / "post.wav", "-af", f"volume={gain:.2f}dB,alimiter=limit=0.84:level=false",
           "-ar", SR, *codec, out)
    return n / SR, gain


def main():
    ap = argparse.ArgumentParser(description="Machine AI voice treatment")
    ap.add_argument("input", help="any audio file ffmpeg can read (ElevenLabs mp3, a recording)")
    ap.add_argument("machine", help="rhino, ape (gorilla), fennec ... or a roster id like rhino_l")
    ap.add_argument("name", help="line name, e.g. ability_2, intro_1, kill_3")
    # Preston picked light for the rhino (2026-11-04): "light is best".
    ap.add_argument("--amount", type=float, default=0.6, help="how much machine: 0.6 light (default), 1.0 standard, 1.5 heavy")
    ap.add_argument("--target", type=float, default=-16.0, help="loudness in LUFS (default -16)")
    ap.add_argument("--out", help="write here instead of audio/voice/<machine>/<name>.ogg (.ogg or .wav)")
    a = ap.parse_args()

    machine = a.machine.lower().split("_")[0]
    machine = ALIASES.get(machine, machine)
    if machine not in MACHINES:
        sys.exit(f"unknown machine '{a.machine}'; known: {', '.join(MACHINES)}")
    out = Path(a.out) if a.out else PROJECT / "audio" / "voice" / machine / f"{a.name}.ogg"
    out.parent.mkdir(parents=True, exist_ok=True)
    seconds, gain = treat(Path(a.input).resolve(), out, SIZES[MACHINES[machine]], a.amount, a.target)
    print(f"{Path(a.input).name} -> {out.name}  ({machine}, size {MACHINES[machine]}, "
          f"amount {a.amount}, {seconds:.2f} s, gain {gain:+.1f} dB)")


if __name__ == "__main__":
    main()
