"""Skeletons for PixelLab animate_with_skeleton_v3, back (north) and back three-quarter (north-east)
(Claude, 2026-11-04). Preston: "yes run back and ne that looks great though" (about the posed front walk).
Rest poses hand-measured from input/{back,ne}_128.png (knee discs, feet, horn). Same step order as the front
(front_skeleton.py): left front swings f1-f3, left hind f3-f5, right front f5-f7, right hind f7-f1, so all the
posed views agree with each other.
- back: hind legs near (leg chains, z 10), front legs far and inside (arm chains, z 2), head hidden behind the
  body at the horn tip (z 1). A stance foot slides from 2 px up (forward, away) to 2 px down; swing lifts it
  and carries it back up.
- ne: forward on screen is up and to the right. Near side is the rhino's right (PixelLab: facing east the RIGHT
  limbs are near). Stance feet slide back along that line 3 px, swing feet lift and carry forward.
Usage: python skeleton_views.py back|ne  -> prints {"first": [...], "frames": [...]} and writes {view}_keypoints.json
"""
import json
import sys
from pathlib import Path

VIEWS = {
    "back": {
        "rest": {
            "NOSE": (64, 38), "NECK": (64, 52), "LEFT EYE": (58, 44), "RIGHT EYE": (70, 44),
            "LEFT EAR": (54, 46), "RIGHT EAR": (74, 46),
            "LEFT HIP": (41, 78), "LEFT KNEE": (41, 89), "LEFT LEG": (42, 106),
            "RIGHT HIP": (86, 78), "RIGHT KNEE": (86, 89), "RIGHT LEG": (85, 106),
            "LEFT SHOULDER": (54, 80), "LEFT ELBOW": (54, 94), "LEFT ARM": (54, 103),
            "RIGHT SHOULDER": (74, 80), "RIGHT ELBOW": (74, 94), "RIGHT ARM": (74, 103),
        },
        "z": {"head": 1, "front": 2, "hind": 10},
        "fwd": (0.0, -1.0),  # forward on screen per px of stride
        "stride": 2.0,
    },
    "ne": {
        "rest": {
            "NOSE": (96, 56), "NECK": (78, 58), "LEFT EYE": (84, 47), "RIGHT EYE": (90, 50),
            "LEFT EAR": (80, 42), "RIGHT EAR": (88, 43),
            "LEFT HIP": (36, 76), "LEFT KNEE": (32, 88), "LEFT LEG": (34, 105),
            "RIGHT HIP": (56, 76), "RIGHT KNEE": (56, 86), "RIGHT LEG": (56, 106),
            "LEFT SHOULDER": (68, 74), "LEFT ELBOW": (65, 88), "LEFT ARM": (66, 104),
            "RIGHT SHOULDER": (88, 75), "RIGHT ELBOW": (88, 89), "RIGHT ARM": (86, 103),
        },
        "z": {"head": 6, "front": 3, "hind": 4, "near_front": 10, "near_hind": 9},
        "fwd": (0.8, -0.6),
        "stride": 3.0,
    },
}
CHAINS = {"LF": (("LEFT SHOULDER", "LEFT ELBOW", "LEFT ARM"), 1), "LH": (("LEFT HIP", "LEFT KNEE", "LEFT LEG"), 3),
          "RF": (("RIGHT SHOULDER", "RIGHT ELBOW", "RIGHT ARM"), 5), "RH": (("RIGHT HIP", "RIGHT KNEE", "RIGHT LEG"), 7)}
LIFT = {"top": (-1, -2, 0), "mid": (-3, -4, -1), "foot": (-4, -7, -3)}
STANCE_S = (1, 0.5, 0, -0.5, -1)   # along forward, times stride: lands forward, slides back
SWING_S = (-0.6, 0, 0.6)          # carried from back to front while lifted
HEAD = ("NOSE", "NECK", "LEFT EYE", "RIGHT EYE", "LEFT EAR", "RIGHT EAR")


def zof(view, k):
    z = VIEWS[view]["z"]
    if k in HEAD:
        return z["head"]
    front = any(s in k for s in ("SHOULDER", "ELBOW", "ARM"))
    if view == "ne" and k.startswith("RIGHT"):
        return z["near_front"] if front else z["near_hind"]
    return z["front"] if front else z["hind"]


def pose(view, i):
    cfg = VIEWS[view]
    fx, fy = cfg["fwd"]
    S = cfg["stride"]
    pts = {k: list(v) for k, v in cfg["rest"].items()}
    for leg, ((top, mid, foot), start) in CHAINS.items():
        p = (i - start) % 8
        if p < 3:
            s = SWING_S[p] * S
            pts[top][1] += LIFT["top"][p]
            pts[mid][0] += fx * s / 2
            pts[mid][1] += fy * s / 2 + LIFT["mid"][p]
            pts[foot][0] += fx * s
            pts[foot][1] += fy * s + LIFT["foot"][p]
        else:
            s = STANCE_S[p - 3] * S
            pts[mid][0] += fx * s / 2
            pts[mid][1] += fy * s / 2
            pts[foot][0] += fx * s
            pts[foot][1] += fy * s
    # head leans 1 px away from a swinging hind leg (weight onto the planted side)
    lh_up, rh_up = (i - 3) % 8 < 3, (i - 7) % 8 < 3
    sway = (1 if lh_up else -1 if rh_up else 0) * (1 if view == "back" else 0.5)
    for k in HEAD:
        pts[k][0] += sway
    return [{"label": k, "x": round(x / 128, 4), "y": round(y / 128, 4), "z_index": zof(view, k)} for k, (x, y) in pts.items()]


if __name__ == "__main__":
    view = sys.argv[1]
    rest = VIEWS[view]["rest"]
    out = {"first": [{"label": k, "x": round(x / 128, 4), "y": round(y / 128, 4), "z_index": zof(view, k)} for k, (x, y) in rest.items()],
           "frames": [pose(view, i) for i in range(8)]}
    Path(__file__).with_name(f"{view}_keypoints.json").write_text(json.dumps(out, separators=(",", ":")))
    print(json.dumps(out["first"], separators=(",", ":")))
    print(json.dumps(out["frames"], separators=(",", ":")))
