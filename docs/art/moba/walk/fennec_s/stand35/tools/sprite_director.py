"""Sprite director (Claude, 2026-10-31; Preston: "so i don't have to tell you what needs fixed you just understand it on a
level of a professional for each profession that would normally work on this to complete the finished product").

Reads every creature and move effect the way each job on a sprite team would, then writes one ordered worklist, so faults
are found before anyone has to name them. It only measures and writes reports, it never touches art. Numbers can't see
taste, so `--look` also cuts strips of the worst cases to view by eye. How to use it: .claude/skills/sprite-director.

  animator    a body that carries its step, walk rhythm, the snap from walking to standing, attack beats, hurt, sleep, state size
  sprite art  lone pixels, colour counts, dark bodies that vanish on the floor
  art direct  look-alikes across the roster, the eight views against each other
  VFX         opaque blocks, effects cut by their canvas, no build-up or fade, flicker, dim effects
  tech art    cut-off frames, soft alpha, feet off the ground row, shadows that leave a body floating, empty frames
  QA          drawn states per creature, diagonals that copy the side view
  game feel   the game's timing constants against published ranges

Measures taken from what was studied on 2026-10-31, in our own code, none of theirs: the loop seam against the clip's pace
(Ludo toolbox), motion and identity scoring (PerfectPixel), the hit near 40 percent of an attack and feet, edge and identity
gates (agent-sprite-forge), beat and frame-count tables (claude-dev-suite). The REF numbers were measured on 20 walkers from
PMDCollab's sprite data on 2026-10-31 (numbers only, no pixels kept), with this same code where it says so. The other
thresholds are rules of thumb, set against this roster's own spread. Sources: docs/art/pro-sprite-standards-2026-10-31.md.

REGRESSIONS below are faults Preston caught by eye. Every run must find them again without being told, or it says MISSED.

  python tools/art/sprite_director.py [name ...] [--look] [--selftest]
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).parent))
import anim_audit  # noqa: E402
import sheet_judge  # noqa: E402
import walk_audit  # noqa: E402

ART = Path("assets/sprites/arena")
OUT = Path("docs/creatures/sprite-director")
FACINGS = ["s", "se", "e", "ne", "n", "nw", "w", "sw"]
SIDE = ["s", "se", "e", "ne", "n"]               # west walks and actions are flips of the east side
AXIS = {"s": (0, 1), "se": (.7, .7), "e": (1, 0), "ne": (.7, -.7), "n": (0, -1)}
ACTS = ["attack", "hurt", "sleep"]
SHOWN = [0, 2, 4, 6]                             # the drawings dungeon.gd plays in a walk
DELIBERATE_POP = {"preostmar", "troughspine"}    # their attack pops are effect bursts (anim_audit, 2026-10-31)

BOIL, LIMBS, STRAY, GROUND = 0.62, 0.45, 0.10, 2     # walk_audit numbers worth a look
SEAM_RATIO, SEAM_MIN = 1.7, 0.25                 # the last-to-first jump against the clip's usual step
SNAP_FIT = 0.55                                  # a stand pose overlapping its best walk drawing less than this snaps
WEAK_REACH, WEAK_CHANGE = 2.0, 0.20              # px past the stand pose, share of the body changed
FAR_FROM_STILL = 0.50                            # a first or last drawing this far from the stand pose pops
HURT_WEAK, HURT_LATE = 0.12, 3                   # a reaction peaks on one of the first three drawings
SLEEP_STILL, SLEEP_BOIL = 0.01, 0.30
SCALE_LOW, SCALE_HIGH = 0.78, 1.28
LONE_HIGH = 0.33                                 # share of a view's pixels with no neighbour of a similar colour
COLOURS_HIGH = 40
DARK_BODY = 0.60                                 # share of a body near black, which sinks into a dark floor
LOOKALIKE = 0.80
BAND_ROWS, BAND_FRAMES = 3, 4                    # edge-to-edge opaque rows, a sheet's background left in
EDGE_PIXELS, EDGE_FRAMES = 6, 4
NO_ONSET, NO_FADE = 0.70, 0.55                   # share of the peak area on the first and last drawing
FLAT_LIFE = 1.5                                  # the biggest frame against the smallest
FLICKER = 0.62                                   # the share of an effect that fails to overlap the next frame
DIM = 0.45                                       # brightness of the peak frame's top pixels

# How much of a body travels as one solid piece each step. REF 0.48 to 0.78 on 14 short-limbed walkers, this same code.
# Kithflare, the walk Preston kept, is 0.46, which is why the line sits a little under the reference.
CARRIED_LOW = 0.40
STILL_BODY = 0.05                                # sway plus bob of the body's core against its height, under this it stands still
LEG_SHORT, ARM_SHORT = 0.22, 0.30                # limb reach past the body's core against height, under both it should waddle
COVER_LOW = 0.15                                 # share of the oval hidden by the body. REF median 0.23 to 0.70 on 20 walkers
BELOW_HIGH = 0.75                                # share of the oval showing under one drawing's feet. REF up to 0.63, usually under 0.40
BELOW_REF = 0.38                                 # the usual top of that range, for the game-wide row
OVAL_OFF = 0.18                                  # oval centre off the body's, against its width. REF 0.11 at most
AREA_JUMP, HEIGHT_JUMP = 0.25, 0.20              # neighbouring views. REF 0.03 to 0.20 and 0.03 to 0.13 (Machamp's area 0.33)
COLOUR_MATCH = 0.70                              # colour share two neighbouring views have in common. REF 0.80 at the lowest
VIEW_DIP = 0.85                                  # a diagonal this much narrower than both neighbours is out of order
FRONT_BACK = 0.60                                # front and back outlines cover each other less than this: a turned view or another body
FRONT_BACK_NEW = 0.80                            # what a new sheet must reach. Drembit passes, and Kithflare's replaced fronts did not
CLEARED = {("windcut", "view_order"): "a kite seen from above, a diagonal is narrower by nature, cleared by eye 2026-10-31"}
FOOTPRINT_SHADOW = {"troughspine", "archroot"}   # dungeon.gd sizes these per pose
OWN_SHADOW = {"warden"}                          # bosses and escorts keep _size_up's whole-body shadow

# Faults Preston caught by eye. creature, the check that must fire, what he said.
REGRESSIONS = [
    ("tallowroot", "walk_tips_only", "2026-10-31, paws curl and move up and down rather than a waddle"),
    ("archroot", "walk_tips_only", "2026-10-28, walk turned down, a rooted body needs a regenerated walk"),
    ("sparkwick", "view_turned", "2026-10-28, its north points northeast"),
    ("sparkwick", "view_order", "2026-10-31, north and the back diagonals sit in each other's slots"),
    ("sparkwick", "view_outline", "2026-10-31, its views just don't look consistent to front"),
    ("skimlet", "walk_ground", "2026-10-28, keeps water round its legs"),
]

# kind: (job, how bad 3 to 1, what's wrong, why it matters, cost, the fix)
KINDS = {
    "vfx_block": ("VFX", 3, "Opaque rectangle left in the effect", "The player sees a box on every hit", "free", "Cut the background from the canvas edge inwards in Aseprite"),
    "view_turned": ("Art direction", 3, "A view faces the wrong way", "The creature moons the wrong direction when it turns", "paid", "Regenerate that view, check for a slot swap first"),
    "walk_facing": ("Animator", 3, "A walk faces a different way than its stand pose", "The creature snaps round when it stops", "free", "Swap the walk files, or flip the mirror side"),
    "cut_off": ("Tech art", 3, "Art cut off by the canvas", "A flat edge on the sprite", "free", "Rebuild the frame on a bigger canvas"),
    "empty_frame": ("Tech art", 3, "Empty or near empty frame", "The creature blinks out", "free", "Copy a neighbour drawing, or redraw"),
    "attack_none": ("QA", 3, "No attack, hurt or sleep drawings", "The stand pose stands in for the whole action", "paid", "rd_action.py, one creature at a time"),
    "stand_snap": ("Animator", 2, "Stand pose doesn't match the walk", "A visible snap on every stop", "free", "Flip it with pose_fix.py, or regenerate the walk if no pose fits"),
    "walk_tips_only": ("Animator", 3, "Short-limbed body stands still, only its feet or paws change", "It paddles in place. A stubby body waddles: the trunk rolls side to side, the arms ride with it and swing fore and aft", "paid", "Regenerate the walk. Nudging the still's pixels was rejected twice"),
    "walk_body_still": ("Animator", 2, "Little of the body travels with the step", "The trunk is left behind, so it reads as limbs twitching", "paid", "Regenerate the walk"),
    "shadow_cover": ("Tech art", 2, "Body hides little of its shadow", "The oval reads as a separate shape, so the creature floats above it", "free", "Widen or lift the shadow in feet_fit, or add it to FOOTPRINT_SHADOW"),
    "shadow_gap": ("Tech art", 2, "Feet leave the shadow on some walk drawings", "The creature hops off the ground it stands on", "free", "Set that drawing's foot row, or shift the frames"),
    "shadow_off": ("Tech art", 2, "Shadow off-centre under the body", "The body overhangs one side", "free", "Centre the oval on the body"),
    "view_order": ("Art direction", 3, "A diagonal is narrower than the views either side of it", "The turn runs out of order, likely views in each other's slots", "free", "Check the slots, swap the stand pose and walk files together"),
    "view_outline": ("Art direction", 3, "Front and back outlines don't match", "They are two sides of one body, so a turned view or a different build shows as it turns", "paid", "Check the slots first, then regenerate the whole sheet, not one view"),
    "view_size": ("Art direction", 2, "Size jumps between neighbouring views", "The creature swells or shrinks as it turns", "paid", "Regenerate the odd view, or rescale it if the shape agrees"),
    "view_colour": ("Art direction", 2, "Colours change between neighbouring views", "It stops being the same creature as it turns", "free", "Recolour the odd view to the shared palette"),
    "walk_boil": ("Animator", 2, "Walk shimmers, the body is redrawn each frame", "Reads as noise, not a step", "paid", "Regenerate the walk. Rebuilding from the still was rejected twice"),
    "walk_limbs": ("Animator", 2, "Upper body moves too much in the walk", "Parts that should hold still flap", "paid", "Regenerate the walk"),
    "walk_stray": ("Animator", 2, "Walk has colours the stand pose doesn't", "Smears or stray specks follow the creature", "free", "Repaint the strays in Aseprite"),
    "walk_ground": ("Tech art", 2, "Walk's feet sit off the stand pose's foot row", "The creature hops up or down when it starts", "free", "Shift the walk frames to the foot row"),
    "walk_uneven": ("Animator", 2, "Uneven step in the walk the game shows", "A limp or hitch in the loop", "free", "Try WALK_POSE pairs or a free frame swap, else regenerate"),
    "attack_no_windup": ("Animator", 2, "Attack hits on its first drawing", "No tell, so the blow has no weight", "paid", "Regenerate the attack with a wind-up"),
    "attack_no_recovery": ("Animator", 2, "Attack ends on the hit pose", "It snaps back to standing", "paid", "Regenerate, or add a recovery drawing"),
    "attack_weak": ("Animator", 2, "Attack barely moves", "It doesn't read at game size", "paid", "Regenerate with a bigger pose"),
    "action_pop": ("Animator", 2, "First or last drawing is far from the stand pose", "A pop going in or out of the action", "free", "Add an in-between in Aseprite, or retime"),
    "hurt_weak": ("Animator", 2, "Hurt barely reacts", "A hit doesn't land", "paid", "Regenerate the hurt"),
    "hurt_late": ("Animator", 2, "Hurt peaks late", "The reaction lags the blow", "free", "Reorder or retime the frames"),
    "sleep_boil": ("Animator", 2, "Sleep shimmers", "A sleeper shouldn't crawl", "free", "Hold fewer drawings, or slow the loop"),
    "state_scale": ("Animator", 2, "Changes size between states", "The creature swells on an action", "free", "Rescale the action to the stand pose"),
    "dark_body": ("Sprite art", 2, "Body is close to black", "It sinks into a dark floor, silhouette lost", "free", "Lift the darkest ramp, keeping its colour family"),
    "lone_pixels": ("Sprite art", 2, "Speckled, many lone pixels", "Reads as noise, not clusters", "free", "Clean with pixel_correction or a smaller shared palette"),
    "soft_alpha": ("Tech art", 2, "Partly see-through pixels", "Fringes under the outline shader", "free", "Threshold alpha to 0 or 255"),
    "frozen": ("Tech art", 2, "All frames of an action are the same picture", "An action that doesn't play", "paid", "Regenerate"),
    "diagonal_copy": ("QA", 2, "Diagonal action copies the side view", "A diagonal attack shows a side body", "paid", "Generate the diagonal facings"),
    "vfx_edge": ("VFX", 2, "Effect is cut by its canvas", "A hard straight edge in the effect", "free", "Pad the canvas, fade the edge"),
    "vfx_no_onset": ("VFX", 2, "Effect starts at full size", "No build-up into the hit", "free", "Drop or scale the first frames"),
    "vfx_no_fade": ("VFX", 2, "Effect ends big, then vanishes", "It cuts off instead of dissipating", "free", "Add a fade on the tail in the shared draw, or trim frames"),
    "vfx_flat": ("VFX", 2, "Effect stays one size throughout", "No shape to its life", "paid", "Redraw with a build, peak and fade"),
    "vfx_flicker": ("VFX", 2, "Effect flickers frame to frame", "Reads as noise", "free", "Play every second frame, or redraw"),
    "vfx_loop": ("VFX", 2, "Projectile loop has a jump", "A hitch while it flies", "free", "Cut the loop at a matching frame"),
    "vfx_empty": ("VFX", 1, "Effect has empty frames", "A gap, unless it's a deliberate fade", "free", "Check by eye, trim"),
    "vfx_dim": ("VFX", 1, "Effect is dim", "Weak on dark floors", "free", "Brighten the core"),
    "pop": ("Animator", 1, "Frame swells or shrinks", "Reads as a flash", "free", "Check by eye"),
    "sleep_still": ("Animator", 1, "Sleep doesn't breathe", "It looks paused", "free", "Add a 1 px breath in Aseprite"),
    "sleep_standing": ("Animator", 1, "Sleep pose is as tall as standing", "May not read as asleep", "paid", "Check by eye, redraw if so"),
    "many_colours": ("Sprite art", 1, "Too many colours in a view", "Busy compared with the house look", "free", "Reduce to a shared palette"),
    "lookalike": ("Art direction", 1, "Two creatures read alike at game size", "Hard to tell apart in a fight", "his call", "Check by eye; same-line pairs are fine"),
}
FINISHED_ORDER = {"free": 0, "his call": 1, "paid": 2}


def load(path):
    return np.array(Image.open(path).convert("RGBA")).astype(np.int16)


def frames(base, action, facing):
    paths = sorted(base.glob(f"{action}_{facing}_f*.png"), key=lambda p: int(p.stem.rsplit("f", 1)[1]))
    return [load(p) for p in paths]


def mask(a):
    return a[..., 3] > 0


def height(a):
    rows = np.nonzero(mask(a).any(1))[0]
    return int(rows.max() - rows.min() + 1) if len(rows) else 0


def lum(a):
    return (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]) / 255.0


def changed(a, b):
    """Share of the pixels either picture fills that differ between them."""
    ma, mb = mask(a), mask(b)
    union = ma | mb
    if not union.any():
        return 0.0
    colour = np.abs(a[..., :3] - b[..., :3]).sum(-1) > 45
    return float(((ma ^ mb) | (ma & mb & colour)).sum() / union.sum())


def fit(a, b, reach_px=3):
    """Best silhouette overlap of two pictures, sliding one a few pixels."""
    ma, mb = mask(a), mask(b)
    best = 0.0
    for dy in range(-reach_px, reach_px + 1):
        for dx in range(-reach_px, reach_px + 1):
            m = np.roll(np.roll(mb, dy, 0), dx, 1)
            best = max(best, float((ma & m).sum() / max(1, (ma | m).sum())))
    return best


def solid(a):
    return a[..., 3] > 127


def core(m):
    """The trunk of a body, with thin parts like tails, lures and feelers worn away."""
    worn = ndi.binary_erosion(m, iterations=2)
    if not worn.any():
        worn = ndi.binary_erosion(m)
    if not worn.any():
        worn = m
    parts, n = ndi.label(worn)
    if n > 1:
        worn = parts == 1 + int(np.argmax(ndi.sum(worn, parts, range(1, n + 1))))
    return worn


def carried(seq, reach_px=3, size=2):
    """Share of a body that travels as one solid piece between drawings, block matching each drawing to the next."""
    shapes = [solid(a) for a in seq]
    union = np.any(shapes, 0)
    rows = np.nonzero(union.any(1))[0]
    top = rows.min() + int((rows.max() - rows.min() + 1) * .25)
    wide = 2 * size + 1
    shifts = sorted(((dy, dx) for dy in range(-reach_px, reach_px + 1) for dx in range(-reach_px, reach_px + 1)),
                    key=lambda s: abs(s[0]) + abs(s[1]))
    h, w = union.shape
    count = 0
    for i, a in enumerate(seq):
        after = (i + 1) % len(seq)
        costs = []
        for dy, dx in shifts:
            other = np.roll(seq[after][..., :3], (-dy, -dx), (0, 1))
            shape = np.roll(shapes[after], (-dy, -dx), (0, 1))
            c = np.abs(a[..., :3] - other).sum(-1) * (shapes[i] & shape) + 200 * (shapes[i] ^ shape)
            costs.append(np.rint(ndi.uniform_filter(c.astype(float), wide, mode="constant") * wide ** 2))
        costs = np.array(costs)
        for y in range(max(size, top), min(h - size, rows.max() + 1)):
            for x in range(size, w - size):
                block = shapes[i][y - size:y + size + 1, x - size:x + size + 1]
                if block.mean() < .5 or a[y - size:y + size + 1, x - size:x + size + 1, :3][block].std() < 12:
                    continue
                k = int(costs[:, y, x].argmin())
                if k != 0 and costs[k, y, x] <= .7 * costs[0, y, x]:
                    count += 1
    return count / max(1, union.sum()) / len(seq)


def body_motion(seq):
    """How far the trunk sways and bobs through a walk, against the body's height."""
    shapes = [solid(a) for a in seq]
    rows = np.nonzero(np.any(shapes, 0).any(1))[0]
    tall = rows.max() - rows.min() + 1
    places = [ndi.center_of_mass(core(m)) for m in shapes]
    return (max(p[1] for p in places) - min(p[1] for p in places)) / tall, (max(p[0] for p in places) - min(p[0] for p in places)) / tall


def limbs(a):
    """How far legs and arms reach past the trunk, against height. Thin parts up top, like lures, don't count as arms."""
    m = solid(a)
    trunk = ndi.binary_dilation(core(m), iterations=2) & m
    ys, xs = np.nonzero(m)
    ty, tx = np.nonzero(trunk)
    tall = ys.max() - ys.min() + 1
    low = ys >= ys.min() + tall * .3
    return (ys.max() - ty.max()) / tall, max(xs[low].max() - tx.max(), tx.min() - xs[low].min()) / tall


def foot_row(a):
    """dungeon.gd's _count_foot_row: the bottom edge of the lowest row with four or more pixels."""
    rows = np.nonzero((a[..., 3] > 25).sum(1) >= 4)[0]
    return float(rows.max() + 1) if len(rows) else float(a.shape[0])


def planted_row(seq):
    """dungeon.gd's ground line for a walk: the lowest foot row within 4 px of the median, over the drawings it plays."""
    rows = sorted(foot_row(a) for a in seq)
    return max(x for x in rows if x <= rows[len(rows) // 2] + 4)


def raised(ry):
    """dungeon.gd's lift of the oval above the foot line, so the feet stand inside it."""
    return min(2.0, float(np.floor(ry * .5 + .5)))


def oval(still):
    """dungeon.gd's feet_fit: the shadow's centre column and half sizes for a stand pose, and the row it centres on."""
    ys, xs = np.nonzero(mask(still))
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    used_w, used_h = x1 - x0, y1 - y0
    low = np.nonzero(still[y1 - max(3, used_h // 4):y1, x0:x1, 3].max(0) > 127)[0] + x0
    left, right = (low.min(), low.max()) if len(low) else (x1, x0)
    rx, mid = (right - left + 1) * .5, (left + right + 1) * .5
    if rx < used_w * .3:
        rx, mid = used_w * .3, x0 + used_w * .5
    rx = max(5.0, rx)
    ry = min(5.5, rx * .36)
    return float(mid), float(rx), ry, foot_row(still) - raised(ry)


def contact(picture, mid, rx, ry, foot):
    """Share of the oval the picture hides, and share of it showing below the lowest pixel. The floor runs past the canvas."""
    h, w = picture.shape[:2]
    y, x = np.mgrid[:h + 12, :w]
    ellipse = ((x + .5 - mid) / rx) ** 2 + ((y + .5 - foot) / ry) ** 2 <= 1
    shown = np.zeros(ellipse.shape, bool)
    shown[:h] = solid(picture)
    rows = np.nonzero(shown.any(1))[0]
    return float((ellipse & shown).sum() / ellipse.sum()), float((ellipse & (y > rows.max())).sum() / ellipse.sum())


def histogram(a):
    pixels = a[mask(a)][:, :3] // 32
    keys, counts = np.unique(pixels[:, 0] * 64 + pixels[:, 1] * 8 + pixels[:, 2], return_counts=True)
    return dict(zip(keys.tolist(), (counts / counts.sum()).tolist()))


def view_jumps(views):
    """The worst step between neighbouring views around the circle: area, height, and the colour they share."""
    area = [int(mask(v).sum()) for v in views]
    tall = [height(v) for v in views]
    prints = [histogram(v) for v in views]
    worst = {"area": (0.0, 0), "height": (0.0, 0), "colour": (1.0, 0)}
    for i in range(len(views)):
        j = (i + 1) % len(views)
        worst["area"] = max(worst["area"], (abs(area[i] - area[j]) / max(area[i], area[j]), i))
        worst["height"] = max(worst["height"], (abs(tall[i] - tall[j]) / max(tall[i], tall[j]), i))
        shared = sum(min(v, prints[j].get(k, 0.0)) for k, v in prints[i].items())
        worst["colour"] = min(worst["colour"], (shared, i))
    return worst


def view_dips(views):
    """Diagonals narrower than both neighbours. A turn widens smoothly to the side view, so a dip means a view out of order."""
    wide = [int(np.ptp(np.nonzero(mask(v).any(0))[0])) + 1 for v in views]
    return [i for i in (1, 3, 5, 7) if wide[i] < VIEW_DIP * min(wide[i - 1], wide[(i + 1) % 8])]


def outline_fit(a, b, slide=6):
    """How much two outlines cover each other, feet on one row, slid sideways to their best fit. 1.0 is the same shape."""
    a, b = mask(a), mask(b)
    foot = lambda m: np.nonzero(m.sum(1) >= 4)[0].max()
    b = np.roll(b, foot(a) - foot(b), axis=0)
    return max(float((a & c).sum() / (a | c).sum()) for c in (np.roll(b, x, axis=1) for x in range(-slide, slide + 1)))


def front_back(views):
    """One body seen from opposite sides has the same outline mirrored, so front and flipped back should nearly cover each other."""
    return outline_fit(views[FACINGS.index("s")], views[FACINGS.index("n")][:, ::-1])


def seam(seq):
    """The jump from the last drawing back to the first, against the clip's usual step."""
    steps = [changed(seq[i], seq[i + 1]) for i in range(len(seq) - 1)]
    last = changed(seq[-1], seq[0])
    return last / max(0.001, float(np.median(steps))), last


def reach(a, axis):
    ys, xs = np.nonzero(mask(a))
    return float((xs * axis[0] + ys * axis[1]).max()) if len(xs) else 0.0


def beats(seq, still, axis):
    """Where an attack's strongest pose falls: pushed furthest along the facing, or the biggest change if it stays put."""
    base = reach(still, axis)
    ext = [reach(a, axis) - base for a in seq]
    change = [changed(a, still) for a in seq]
    hit = int(np.argmax(ext)) if max(ext) >= WEAK_REACH else int(np.argmax(change))
    return {"hit": hit, "ext": ext, "change": change}


def attack_faults(seq, still, axis):
    b = beats(seq, still, axis)
    out = []
    if max(b["ext"]) < WEAK_REACH and max(b["change"]) < WEAK_CHANGE:
        return ["attack_weak"]
    if b["hit"] == 0:
        out.append("attack_no_windup")
    if b["hit"] == len(seq) - 1:
        out.append("attack_no_recovery")
    if b["change"][0] > FAR_FROM_STILL or b["change"][-1] > FAR_FROM_STILL:
        out.append("action_pop")
    return out


def hurt_faults(seq, still):
    change = [changed(a, still) for a in seq]
    out = []
    if max(change) < HURT_WEAK:
        return ["hurt_weak"]
    if int(np.argmax(change)) >= HURT_LATE:
        out.append("hurt_late")
    if change[0] > FAR_FROM_STILL + 0.2 or change[-1] > FAR_FROM_STILL:
        out.append("action_pop")
    return out


def sleep_faults(seq, still):
    steps = [changed(seq[i], seq[(i + 1) % len(seq)]) for i in range(len(seq))]
    out = []
    if max(steps) < SLEEP_STILL:
        out.append("sleep_still")
    if float(np.median(steps)) > SLEEP_BOIL:
        out.append("sleep_boil")
    tall = float(np.median([height(a) for a in seq]))
    if tall >= 0.97 * height(still):
        out.append("sleep_standing")
    return out


def lone_share(a):
    m = mask(a)
    same = np.zeros(m.shape, bool)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        rgb = np.roll(a[..., :3], (dy, dx), (0, 1))
        same |= np.roll(m, (dy, dx), (0, 1)) & (np.abs(a[..., :3] - rgb).sum(-1) < 30)
    return float((m & ~same).sum() / max(1, m.sum()))


def effect_faults(seq, projectile=False):
    """The life of a move effect: a clean shape that builds, peaks and fades inside its canvas."""
    out = []
    h, w = seq[0].shape[:2]
    area = [int(mask(a).sum()) for a in seq]
    peak = max(area) or 1
    bands = sum(1 for a in seq if max((mask(a).sum(1) >= w * .9).sum(), (mask(a).sum(0) >= h * .9).sum()) >= BAND_ROWS)
    if bands >= BAND_FRAMES:
        out.append("vfx_block")
    edge = sum(1 for a in seq if mask(a)[[0, -1], :].sum() + mask(a)[:, [0, -1]].sum() >= EDGE_PIXELS)
    if edge >= EDGE_FRAMES:
        out.append("vfx_edge")
    if sum(1 for x in area if x < peak * .01) >= 3:
        out.append("vfx_empty")
    alive = [x for x in area if x >= peak * .01]
    if projectile:
        if seam(seq)[0] > SEAM_RATIO and seam(seq)[1] > SEAM_MIN:
            out.append("vfx_loop")
    else:
        if alive[0] / peak > NO_ONSET:
            out.append("vfx_no_onset")
        if alive[-1] / peak > NO_FADE:
            out.append("vfx_no_fade")
        if peak / max(1, min(alive)) < FLAT_LIFE:
            out.append("vfx_flat")
    gaps = []
    for i in range(len(seq) - 1):
        ma, mb = mask(seq[i]), mask(seq[i + 1])
        if ma.any() and mb.any():
            gaps.append(1 - (ma & mb).sum() / (ma | mb).sum())
    if gaps and float(np.median(gaps)) > FLICKER:
        out.append("vfx_flicker")
    top = seq[int(np.argmax(area))]
    if float(np.percentile(lum(top)[mask(top)], 95)) < DIM:
        out.append("vfx_dim")
    return out


class Report:
    def __init__(self):
        self.found = defaultdict(lambda: defaultdict(list))   # kind, who, details
        self.ground = []                                      # below, cover: every walk drawing the game shows on a plain oval
        self.look = {}                                        # kind: [picture paths] of its first case

    def add(self, kind, who, detail="", look=None):
        if (who, kind) in CLEARED:
            return
        self.found[kind][who].append(detail)
        if look and kind not in self.look:
            self.look[kind] = (who, detail, look)


def read_creature(name, r):
    base = ART / name / "dungeon"
    fights = base.is_dir()
    if not fights:
        base = ART / name / "town"
    still = {f: load(base / f"{f}.png") for f in FACINGS}
    # QA: what exists at all
    have = {a: bool(frames(base, a, "s") or frames(base, a, "e")) for a in ACTS}
    if fights and not all(have.values()):
        r.add("attack_none", name, "/".join(a for a in ACTS if not have[a]))
    for act in ACTS:
        for d, side in (("se", "e"), ("ne", "e")):
            a, b = frames(base, act, d), frames(base, act, side)
            if a and len(a) == len(b) and all(np.array_equal(x, y) for x, y in zip(a, b)):
                r.add("diagonal_copy", name, act)
                break
    # Animator: the walk
    if fights:
        w = walk_audit.audit(name)
        if w["boil"] > BOIL:
            r.add("walk_boil", name, f'{w["boil"]:.2f}')
        if w["limbs"] > LIMBS:
            r.add("walk_limbs", name, f'{w["limbs"]:.2f}')
        if w["stray"] > STRAY:
            r.add("walk_stray", name, f'{w["stray"]:.2f}')
        if abs(w["ground"]) > GROUND:
            r.add("walk_ground", name, f'{w["ground"]:+.0f} px')
    for f in SIDE:
        seq = frames(base, "walk", f)
        if len(seq) < 8:
            continue
        shown = [seq[i] for i in SHOWN]
        ratio, jump = seam(shown)
        if fights and ratio > SEAM_RATIO and jump > SEAM_MIN:
            r.add("walk_uneven", name, f, base.glob(f"walk_{f}_f*.png"))
        best = max(fit(still[f], a) for a in shown)
        if best < SNAP_FIT:
            r.add("stand_snap", name, f"{f} {best:.2f}", base.glob(f"walk_{f}_f*.png"))
    if fights:
        read_gait(name, base, r)
    # Animator: actions
    for f in SIDE:
        a = frames(base, "attack", f)
        if a:
            for k in attack_faults(a, still[f], AXIS[f]):
                r.add(k, name, f"attack {f}", base.glob(f"attack_{f}_f*.png"))
        a = frames(base, "hurt", f)
        if a:
            for k in hurt_faults(a, still[f]):
                r.add(k, name, f"hurt {f}", base.glob(f"hurt_{f}_f*.png"))
        a = frames(base, "sleep", f)
        if a:
            for k in sleep_faults(a, still[f]):
                r.add(k, name, f"sleep {f}", base.glob(f"sleep_{f}_f*.png"))
        tall = height(still[f])
        for act in ("attack", "hurt"):
            a = frames(base, act, f)
            if a:
                ratio = float(np.median([height(x) for x in a])) / tall
                if not SCALE_LOW <= ratio <= SCALE_HIGH:
                    r.add("state_scale", name, f"{act} {f} {ratio:.2f}", base.glob(f"{act}_{f}_f*.png"))
    # Tech art: frames against the canvas
    if fights:
        report = anim_audit.audit(name, "dungeon") or {"faults": []}
        for row in report["faults"]:
            tag = f'{row["action"]} {row["facing"]}'
            if row["clip"]:
                r.add("cut_off", name, tag, base.glob(f'{row["action"]}_{row["facing"]}_f*.png'))
            if row["empty"]:
                r.add("empty_frame", name, tag)
            if row["soft"]:
                r.add("soft_alpha", name, tag)
            if row["frozen"]:
                r.add("frozen", name, tag)
            if row["pop"] > 0.45 and name not in DELIBERATE_POP:
                r.add("pop", name, tag)
            if row["action"] == "walk" and "looks" in row:
                r.add("walk_facing", name, f'{row["facing"]} looks {row["looks"]}')
    # Sprite art and art direction: the stand poses
    for set_name in ("dungeon", "town", "small"):
        folder = ART / name / set_name
        if not (folder / "s.png").exists():
            continue
        views = [load(folder / f"{f}.png") for f in FACINGS]
        lone = float(np.mean([lone_share(v) for v in views]))
        if lone > LONE_HIGH:
            r.add("lone_pixels", name, f"{set_name} {lone:.2f}", [folder / f"{f}.png" for f in FACINGS])
        colours = int(np.median([len(np.unique(v[mask(v)][:, :3], axis=0)) for v in views]))
        if colours > COLOURS_HIGH:
            r.add("many_colours", name, f"{set_name} {colours}")
    body = np.concatenate([lum(still[f])[mask(still[f])] for f in FACINGS])
    if float((body < 0.2).mean()) > DARK_BODY:
        r.add("dark_body", name, f"{(body < 0.2).mean():.2f}", [base / "s.png", base / "e.png"])
    judged = sheet_judge.judge(str(base))
    for d, fails in judged["fails"].items():
        if any("turned" in x for x in fails):
            r.add("view_turned", name, d, [base / f"{d}.png"])
    views = [still[f] for f in FACINGS]
    worst = view_jumps(views)
    pair = lambda i: f"{FACINGS[i]} to {FACINGS[(i + 1) % 8]}"
    for i in view_dips(views):
        r.add("view_order", name, FACINGS[i], [base / f"{f}.png" for f in FACINGS])
    if front_back(views) < FRONT_BACK:
        r.add("view_outline", name, f"{front_back(views):.2f}", [base / "s.png", base / "n.png"])
    if worst["area"][0] > AREA_JUMP or worst["height"][0] > HEIGHT_JUMP:
        which = worst["area"] if worst["area"][0] > AREA_JUMP else worst["height"]
        r.add("view_size", name, f"{pair(which[1])} {which[0]:.2f}", [base / f"{f}.png" for f in FACINGS])
    if worst["colour"][0] < COLOUR_MATCH:
        r.add("view_colour", name, f'{pair(worst["colour"][1])} {worst["colour"][0]:.2f}', [base / f"{f}.png" for f in FACINGS])
    if fights and name not in FOOTPRINT_SHADOW | OWN_SHADOW:
        read_shadow(name, base, still, r)


def read_gait(name, base, r):
    """Does the body carry the step? Measured on the front and the side, the drawings the game plays."""
    views = {f: frames(base, "walk", f) for f in ("s", "e")}
    if any(len(v) < 8 for v in views.values()):
        return
    shown = {f: [v[i] for i in SHOWN] for f, v in views.items()}
    share = {f: carried(s) for f, s in shown.items()}
    if min(share.values()) >= CARRIED_LOW:
        return
    detail = " ".join(f"{f} {v:.2f}" for f, v in share.items())
    picture = base.glob("walk_e_f*.png") if share["e"] < share["s"] else base.glob("walk_s_f*.png")
    sway, bob = body_motion(shown["s"])
    leg, arm = limbs(load(base / "s.png"))
    if sway + bob < STILL_BODY and leg < LEG_SHORT and arm < ARM_SHORT:
        r.add("walk_tips_only", name, f"{detail}, trunk moves {sway + bob:.2f}", picture)
    else:
        r.add("walk_body_still", name, detail, picture)


def read_shadow(name, base, still, r):
    """Does the creature stand on its shadow? The oval is measured the way dungeon.gd draws it, on stills and walk drawings."""
    covers = []
    for f in FACINGS:
        mid, rx, ry, foot = oval(still[f])
        covers.append(contact(still[f], mid, rx, ry, foot)[0])
        width = np.nonzero(mask(still[f]).any(0))[0]
        wide = width.max() - width.min() + 1
        centre = (width.max() + width.min() + 1) * .5
        if abs(round(mid) - centre) / wide > OVAL_OFF:
            r.add("shadow_off", name, f"{f} {abs(round(mid) - centre) / wide:.2f}", [base / f"{f}.png"])
        seq = frames(base, "walk", f)
        if len(seq) == 8:
            line = planted_row([seq[i] for i in SHOWN]) - raised(ry)
            meets = [contact(seq[i], mid, rx, ry, line) for i in SHOWN]
            r.ground += [(m[1], m[0]) for m in meets]
            below = max(m[1] for m in meets)
            if below > BELOW_HIGH:
                r.add("shadow_gap", name, f"{f} {below:.2f}", base.glob(f"walk_{f}_f*.png"))
    if float(np.median(covers)) < COVER_LOW:
        r.add("shadow_cover", name, f"{float(np.median(covers)):.2f}", [base / "s.png", base / "e.png"])


def signature(name):
    """A small silhouette and colour print of the front view, to compare across the roster."""
    base = ART / name / ("dungeon" if (ART / name / "dungeon").is_dir() else "town")
    a = load(base / "s.png")
    m = mask(a)
    ys, xs = np.nonzero(m)
    crop = Image.fromarray((m[ys.min():ys.max() + 1, xs.min():xs.max() + 1] * 255).astype(np.uint8)).resize((32, 32), Image.NEAREST)
    hist = np.histogramdd(a[m][:, :3] / 256.0, bins=(4, 4, 4), range=((0, 1),) * 3)[0].ravel()
    return np.array(crop) > 127, hist / hist.sum()


def read_roster(names, r):
    prints = {n: signature(n) for n in names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ma, ha = prints[a]
            mb, hb = prints[b]
            score = 0.5 * (ma & mb).sum() / (ma | mb).sum() + 0.5 * float(np.minimum(ha, hb).sum())
            if score > LOOKALIKE:
                r.add("lookalike", f"{a} / {b}", f"{score:.2f}")


def read_effects(r):
    text = Path("scripts/dungeon/dungeon.gd").read_text(encoding="utf-8")
    flying = set(re.findall(r'"proj": "(\w+)"', text))
    for folder in sorted(p for p in (ART / "vfx").iterdir() if p.is_dir()):
        paths = sorted(folder.glob("f*.png"))
        seq = [load(p) for p in paths]
        for k in effect_faults(seq, folder.name in flying):
            r.add(k, folder.name, "", paths)


def read_timing(r):
    """The game's timing against published ranges and 16 Mystery Dungeon walkers. A range is a reference, not a rule."""
    text = Path("scripts/dungeon/dungeon.gd").read_text(encoding="utf-8")

    def value(pattern):
        got = re.search(pattern, text)
        return float(got.group(1)) if got else None

    rows = [("Walk step", value(r"const STEP_TIME := ([\d.]+)"), (0.1, 0.3), "Sky measures 24 frames a step at 60 fps, 0.4 s; walkers hold drawings unevenly, usually 8, 10, 8, 10 ticks"),
            ("Attack", value(r'"attack": ([\d.]+)'), (0.3, 0.5), "Walkers: 10 to 15 drawings, 0.32 to 0.50 s, uneven holds, hit 7 to 56 percent in. Ours: 6 even drawings. Sky in play, Tackle: wind-up 10, lunge 8, held on the target 7, return 4 frames"),
            ("Hurt", value(r'"hurt": ([\d.]+)'), (0.1, 0.2), "All 16 walkers: 2 drawings, 0.17 s. Sky in play then holds the last hurt drawing with sweat drops about 40 frames"),
            ("Sleep loop", value(r"const SLEEP_LOOP := ([\d.]+)"), (1.0, 1.2), "Walkers: 2 drawings, about 1.1 s. Ours: 4 drawings"),
            ("Hit-stop", value(r"var _stop := ([\d.]+)"), (0.05, 0.17), "Medium to heavy hit. Sky in play freezes nothing: the attacker holds its lunge about 7 frames while a 9-frame impact plays. Emerald Arena freezes the screen 4 frames and flashes the target pale about 15"),
            ("Move effect, every one", value(r"const FX_SECONDS := ([\d.]+)"), (0.2, 1.0), "Sparks 0.05 to 0.15, splash 0.2 to 0.4, smoke 0.6 to 0.7, explosion 0.5 to 1.0")]
    if r.ground:
        rows.append(("Oval showing under the feet in a walk, share", round(float(np.median([g[0] for g in r.ground])), 2), (0.0, BELOW_REF),
                     f"Walkers usually under {BELOW_REF}. Was 0.50 before the oval was raised on 2026-10-31"))
        rows.append(("Oval hidden by the body in a walk, share", round(float(np.median([g[1] for g in r.ground])), 2), (0.23, 0.7), "Median per walker. Was 0.17 before the oval was raised on 2026-10-31"))
    return [(n, v, lo, hi, note, "ok" if v is not None and lo <= v <= hi else "outside") for n, v, (lo, hi), note in rows]


def strip(paths, out, scale=4):
    pics = [Image.open(p).convert("RGBA") for p in paths][:16]
    w, h = pics[0].size
    sheet = Image.new("RGBA", ((w * scale + 4) * len(pics), h * scale), (58, 52, 46, 255))
    for i, p in enumerate(pics):
        big = p.resize((w * scale, h * scale), Image.NEAREST)
        sheet.paste(big, (i * (w * scale + 4), 0), big)
    sheet.save(out)


def write_report(r, names, timing, look):
    OUT.mkdir(parents=True, exist_ok=True)
    order = sorted(r.found, key=lambda k: (-KINDS[k][1], FINISHED_ORDER[KINDS[k][4]], -len(r.found[k])))
    lines = ["# Sprite worklist", "", "Written by `tools/art/sprite_director.py`, which measures and changes no art. "
             "Ordered by how bad, then free before paid, then how many. Thresholds are rules of thumb: anything here is a "
             "lead for the eye, and Preston has the last word.", "",
             "| # | Job | What's wrong | Why it matters | How many | Cost | Fix |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for i, k in enumerate(order, 1):
        job, _, what, why, cost, fix = KINDS[k]
        lines.append(f"| {i} | {job} | {what} | {why} | {len(r.found[k])} | {cost} | {fix} |")
    lines += ["", "## Game-wide numbers against published ranges and measured walkers", "", "| What | Game | Range | Note | |", "| --- | --- | --- | --- | --- |"]
    for n, v, lo, hi, note, verdict in timing:
        lines.append(f"| {n} | {v} | {lo} to {hi} | {note} | {verdict} |")
    lines += ["", "## Who, by fault", ""]
    for k in order:
        lines.append(f"**{KINDS[k][2]}** ({len(r.found[k])})")
        for who, details in sorted(r.found[k].items()):
            shown = ", ".join(sorted(set(d for d in details if d))[:6])
            lines.append(f"- {who}" + (f": {shown}" if shown else ""))
        lines.append("")
    lines += ["## Roster, what each creature needs to be finished", "", "| Creature | Drawn states | Faults to fix, bad | Faults, polish | Status |", "| --- | --- | --- | --- | --- |"]
    for n in names:
        bad = [k for k in r.found if n in r.found[k] and KINDS[k][1] >= 2 and k != "attack_none"]
        minor = [k for k in r.found if n in r.found[k] and KINDS[k][1] == 1]
        missing = r.found.get("attack_none", {}).get(n)
        town = not (ART / n / "dungeon").is_dir()
        states = "town only" if town else ("walk only" if missing and len(missing[0].split("/")) == 3 else ("all" if not missing else f"no {missing[0]}"))
        status = "Needs drawing" if missing else ("Needs fixes" if bad else "Passes the numbers, needs an eye")
        lines.append(f"| {n} | {states} | {len(bad)} | {len(minor)} | {status} |")
    (OUT / "WORKLIST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "findings.json").write_text(json.dumps({k: dict(v) for k, v in r.found.items()}, indent=1, default=str), encoding="utf-8")
    if look:
        folder = OUT / "look"
        folder.mkdir(exist_ok=True)
        for k, (who, detail, paths) in r.look.items():
            strip(sorted(paths, key=lambda p: (len(str(p)), str(p))), folder / f"{KINDS[k][1]}_{k}.png")
            print(f"  look {k}: {who} {detail}")


def selftest():
    """Each check must fire on a bad case and stay quiet on a good one: a test that passes can still be testing nothing."""
    def disc(radius, cx=24, cy=24, size=48, colour=(220, 120, 40)):
        y, x = np.ogrid[:size, :size]
        a = np.zeros((size, size, 4), np.int16)
        on = (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2
        a[on] = (*colour, 255)
        return a

    still = disc(12)
    east = AXIS["e"]
    middle = [disc(12, 21), disc(12, 21), disc(12, 30), disc(12, 27), disc(12, 25), disc(12, 24)]
    first = [disc(12, 30), disc(12, 28), disc(12, 26), disc(12, 25), disc(12, 24), disc(12, 24)]
    last = [disc(12, 24), disc(12, 24), disc(12, 25), disc(12, 26), disc(12, 28), disc(12, 30)]
    good_life = [disc(r) for r in (3, 4, 6, 10, 14, 18, 20, 18, 14, 10, 7, 5, 4, 3, 3, 3)]
    boxed = [g.copy() for g in good_life]
    for a in boxed:
        a[30:, :] = (20, 30, 90, 255)
    tailed = disc(0)
    tailed[30:41, 10:43] = tailed[6:30, 36:43] = (220, 120, 40, 255)
    results = {
        "good attack quiet": attack_faults(middle, still, east) == [],
        "hit on first drawing fires": "attack_no_windup" in attack_faults(first, still, east),
        "hit on last drawing fires": "attack_no_recovery" in attack_faults(last, still, east),
        "still attack fires": attack_faults([still] * 6, still, east) == ["attack_weak"],
        "good effect quiet": effect_faults(good_life) == [],
        "opaque band fires": "vfx_block" in effect_faults(boxed),
        "no build-up fires": "vfx_no_onset" in effect_faults(good_life[6:]),
        "no fade fires": "vfx_no_fade" in effect_faults(good_life[:7]),
        "flat life fires": "vfx_flat" in effect_faults([disc(14)] * 16),
        "flicker fires": "vfx_flicker" in effect_faults([disc(4, 8 + 32 * (i % 2), 8 + 16 * (i % 3)) for i in range(16)]),
        "smooth loop quiet": seam([disc(12, 20 + i) for i in (0, 2, 4, 2)])[0] < SEAM_RATIO,
        "jumping loop fires": seam([disc(12, 12 + i) for i in (0, 1, 2, 3, 4, 22)])[0] > SEAM_RATIO,
        "late hurt fires": "hurt_late" in hurt_faults([still, disc(12, 25), disc(12, 26), disc(12, 28), disc(12, 34), disc(12, 26)], still),
        "dead sleep fires": "sleep_still" in sleep_faults([still] * 4, still),
        "feet on the shadow quiet": contact(still, *oval(still))[1] < BELOW_HIGH,
        "feet off the shadow fires": contact(disc(12, cy=16), *oval(still))[1] > BELOW_HIGH,
        "matching views quiet": view_jumps([still] * 8)["area"][0] == 0 and view_jumps([still] * 8)["colour"][0] > .99,
        "smooth turn quiet": view_dips([disc(r) for r in (10, 12, 14, 12, 10, 12, 14, 12)]) == [],
        "out of order turn fires": view_dips([disc(r) for r in (10, 12, 14, 8, 12, 12, 14, 12)]) == [3],
        "matching outlines quiet": front_back([still] * 8) > .99,
        "other body fires": front_back([still] * 4 + [disc(6)] + [still] * 3) < FRONT_BACK,
        "tail on the same side fires": front_back([tailed] * 8) < FRONT_BACK,
        "shrunken view fires": view_jumps([still] * 7 + [disc(7)])["area"][0] > AREA_JUMP,
        "recoloured view fires": view_jumps([still] * 7 + [disc(12, colour=(40, 90, 220))])["colour"][0] < COLOUR_MATCH,
    }
    bad = [k for k, ok in results.items() if not ok]
    print(f"selftest: {len(results) - len(bad)} of {len(results)} passed" + (f", failed: {bad}" if bad else ""))
    return not bad


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    if not selftest():
        sys.exit("selftest failed, so the worklist can't be trusted")
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    every = not names
    names = names or sorted(p.name for p in ART.iterdir() if (p / "s.png").exists())
    r = Report()
    for n in names:
        read_creature(n, r)
        print(".", end="", flush=True)
    print()
    if every:
        read_roster(names, r)
        read_effects(r)
    timing = read_timing(r)
    write_report(r, names, timing, "--look" in sys.argv)
    total = sum(len(v) for v in r.found.values())
    print(f"{len(names)} creatures, {len(r.found)} kinds of fault, {total} cases: {OUT / 'WORKLIST.md'}")
    for who, kind, said in REGRESSIONS:
        if who in names:
            print(f"  {'found ' if who in r.found.get(kind, {}) else 'MISSED'} {who}: {said}")


if __name__ == "__main__":
    main()
