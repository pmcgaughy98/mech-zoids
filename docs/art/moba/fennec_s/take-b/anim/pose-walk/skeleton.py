"""Fennec front and back trot skeletons for PixelLab animate_with_skeleton_v3 (Claude, animation lane, 2026-11-04).

Preston: "Yes, pose them", on redoing the fennec's front and back trot pose-guided from its side trot (the Codex front
and back trot legs barely move). Method from the rhino's retro-walk/pixellab/front_skeleton.py.

Rest joints are hand-measured on input/{front,back}_128.png: the Codex trot f0 cut from the 192 canvas at (32, 40),
so the feet sit on row 120. Front legs go on the arm chains (SHOULDER, ELBOW, ARM), hind legs on the leg chains
(HIP, KNEE, LEG), the head on nose, eyes, ears and neck. LEFT and RIGHT are the fennec's own sides: facing south its
right is on the viewer's left, facing north on the viewer's right.

Gait from the side trot (codex-set-a/walk/frames/side_f0-7, 10 fps): a trot in diagonal pairs. One front leg is up
on f1-f2 and down on f3, the other up on f5-f6 and down on f7. So the left front and right hind swing on f1-f2, the
right front and left hind on f5-f6. A swinging foot lifts 5 then 6 px; a planted foot slides 1 px a step from where
it lands to behind (down the screen to up it facing south, the other way facing north). The head sways 1 px toward
the planted front foot.
Usage: python skeleton.py   (writes front_keypoints.json and back_keypoints.json)
"""
import json
from pathlib import Path

S = 128
REST = {
    "front": {
        "NOSE": (64, 85), "NECK": (64, 90), "RIGHT EYE": (56, 79), "LEFT EYE": (72, 79),
        "RIGHT EAR": (48, 62), "LEFT EAR": (80, 62),
        "RIGHT SHOULDER": (51, 96), "RIGHT ELBOW": (51, 106), "RIGHT ARM": (52, 118),
        "LEFT SHOULDER": (77, 96), "LEFT ELBOW": (79, 106), "LEFT ARM": (77, 118),
        "RIGHT HIP": (57, 100), "RIGHT KNEE": (57, 109), "RIGHT LEG": (58, 116),
        "LEFT HIP": (71, 100), "LEFT KNEE": (71, 109), "LEFT LEG": (70, 116),
    },
    "back": {
        "NOSE": (64, 74), "NECK": (64, 86), "LEFT EYE": (60, 76), "RIGHT EYE": (68, 76),
        "LEFT EAR": (49, 62), "RIGHT EAR": (79, 62),
        "LEFT SHOULDER": (56, 92), "LEFT ELBOW": (57, 102), "LEFT ARM": (58, 114),
        "RIGHT SHOULDER": (72, 92), "RIGHT ELBOW": (71, 102), "RIGHT ARM": (70, 114),
        "LEFT HIP": (51, 98), "LEFT KNEE": (50, 108), "LEFT LEG": (50, 118),
        "RIGHT HIP": (77, 98), "RIGHT KNEE": (78, 108), "RIGHT LEG": (78, 118),
    },
}
HEAD = ("NOSE", "NECK", "RIGHT EYE", "LEFT EYE", "RIGHT EAR", "LEFT EAR")
# draw order: facing south the front legs are nearest, facing north the hind legs
Z = {"front": {"head": 12, "arm": 10, "leg": 2}, "back": {"head": 1, "arm": 2, "leg": 10}}
CHAINS = {"LF": (("LEFT SHOULDER", "LEFT ELBOW", "LEFT ARM"), 1), "RH": (("RIGHT HIP", "RIGHT KNEE", "RIGHT LEG"), 1),
          "RF": (("RIGHT SHOULDER", "RIGHT ELBOW", "RIGHT ARM"), 5), "LH": (("LEFT HIP", "LEFT KNEE", "LEFT LEG"), 5)}
SWING = {"top": (-1, -1), "mid": (-3, -4), "foot": (-5, -6)}  # y offsets on the two frames a leg is up
STANCE = (1, 1, 0, 0, -1, -1)  # facing south; reversed facing north


def zof(view, k):
    return Z[view]["head" if k in HEAD else "arm" if ("SHOULDER" in k or "ELBOW" in k or k.endswith("ARM")) else "leg"]


def pose(view, i):
    pts = {k: list(v) for k, v in REST[view].items()}
    stance = STANCE if view == "front" else STANCE[::-1]
    up = set()
    for name, (joints, start) in CHAINS.items():
        p = (i - start) % 8
        if p < 2:
            up.add(name)
            for k, part in zip(joints, ("top", "mid", "foot")):
                pts[k][1] += SWING[part][p]
        else:
            s = stance[p - 2]
            pts[joints[2]][1] += s
            pts[joints[1]][1] += s / 2
    sway = -1 if "LF" in up else 1 if "RF" in up else 0
    if view == "back":
        sway = -sway  # the fennec's left is on the viewer's left facing north
    for k in HEAD:
        pts[k][0] += sway
    return [{"label": k, "x": round(x / S, 4), "y": round(y / S, 4), "z_index": zof(view, k)} for k, (x, y) in pts.items()]


for view in REST:
    out = {"first": [{"label": k, "x": round(x / S, 4), "y": round(y / S, 4), "z_index": zof(view, k)}
                     for k, (x, y) in REST[view].items()],
           "frames": [pose(view, i) for i in range(8)]}
    Path(__file__).with_name(f"{view}_keypoints.json").write_text(json.dumps(out, separators=(",", ":")))
    print(view, "written")
