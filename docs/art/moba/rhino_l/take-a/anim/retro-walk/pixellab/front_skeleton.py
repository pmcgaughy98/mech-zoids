"""Skeletons for PixelLab animate_with_skeleton_v3, front view (Claude, 2026-11-04). Preston: "try 1 on front first".
Rest pose measured from input/front_128.png (128 px): front legs on the arm chains (shoulder plate, knee disc,
foot), hind legs on the leg chains (hidden behind, inside and a little higher), head on nose/eyes/ears/neck.
Character sides: facing south, its RIGHT is the viewer's left.
Gait from the Retro side walk: left front swings f1-f3, right front f5-f7, left hind f3-f5, right hind f7-f1.
Swing: foot up 4, 7, 3 px, knee up 3, 4, 1, shoulder up 1, 2, 0. Stance (5 frames): foot slides from 2 px
forward (lower on screen) to 2 px back. The head sways 1 px toward the planted front foot.
Writes pixellab/front_keypoints.json: {"first": [...], "frames": [[...] x 8]}.
"""
import json
from pathlib import Path

REST = {
    "NOSE": (63.5, 90), "NECK": (63.5, 74), "RIGHT EYE": (52.5, 79), "LEFT EYE": (74.5, 79),
    "RIGHT EAR": (46, 75.5), "LEFT EAR": (82, 75.5),
    "RIGHT SHOULDER": (38, 80), "RIGHT ELBOW": (38.5, 90.5), "RIGHT ARM": (39.5, 105),
    "LEFT SHOULDER": (90, 80), "LEFT ELBOW": (90, 90.5), "LEFT ARM": (87.5, 106),
    "RIGHT HIP": (52, 84), "RIGHT KNEE": (52, 95), "RIGHT LEG": (52, 104),
    "LEFT HIP": (76, 84), "LEFT KNEE": (76, 95), "LEFT LEG": (76, 104),
}
Z = {k: (12 if k in ("NOSE", "NECK") or "EYE" in k or "EAR" in k else 10 if any(s in k for s in ("SHOULDER", "ELBOW", "ARM")) else 2)
     for k in REST}
CHAINS = {  # rhino leg -> (top, mid, foot) joints, swing start frame
    "LF": (("LEFT SHOULDER", "LEFT ELBOW", "LEFT ARM"), 1),
    "RF": (("RIGHT SHOULDER", "RIGHT ELBOW", "RIGHT ARM"), 5),
    "LH": (("LEFT HIP", "LEFT KNEE", "LEFT LEG"), 3),
    "RH": (("RIGHT HIP", "RIGHT KNEE", "RIGHT LEG"), 7),
}
SWING = {"top": (-1, -2, 0), "mid": (-3, -4, -1), "foot": (-4, -7, -3)}  # posed bigger than life, per the tool docs
STANCE = (2, 1, 0, -1, -2)
HEAD = ("NOSE", "NECK", "RIGHT EYE", "LEFT EYE", "RIGHT EAR", "LEFT EAR")


def pose(i):
    pts = {k: list(v) for k, v in REST.items()}
    for leg, ((top, mid, foot), start) in CHAINS.items():
        p = (i - start) % 8
        if p < 3:
            pts[top][1] += SWING["top"][p]
            pts[mid][1] += SWING["mid"][p]
            pts[foot][1] += SWING["foot"][p]
        else:
            s = STANCE[p - 3]
            pts[foot][1] += s
            pts[mid][1] += s / 2
    lf_up = (i - 1) % 8 < 3
    rf_up = (i - 5) % 8 < 3
    sway = -1 if lf_up else 1 if rf_up else 0  # LF is on the viewer's right, weight goes left
    for k in HEAD:
        pts[k][0] += sway
    return [{"label": k, "x": round(x / 128, 4), "y": round(y / 128, 4), "z_index": Z[k]} for k, (x, y) in pts.items()]


out = {"first": [{"label": k, "x": round(x / 128, 4), "y": round(y / 128, 4), "z_index": Z[k]} for k, (x, y) in REST.items()],
       "frames": [pose(i) for i in range(8)]}
Path(__file__).with_name("front_keypoints.json").write_text(json.dumps(out, separators=(",", ":")))
print(json.dumps(out["first"], separators=(",", ":")))
print(json.dumps(out["frames"], separators=(",", ":")))
