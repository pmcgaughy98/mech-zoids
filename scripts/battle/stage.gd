extends RefCounted
## Where battle machines stand on the 320x180 screen (Claude, 2026-10-15). Legacy-style staging (animation pass 3,
## 2026-10-12): the player's machine front-left and low, the enemy back-right and higher, the two overlapping in the
## middle like the reference's diagonal formation.
##
## The field is zoomed out (Preston, 2026-10-15: "the perspective is too close"). Machines, their effects and the
## ground they stand on live in a field node drawn at field_scale(): about ZOOM of full size, rounded so every art
## pixel covers a whole number of screen pixels at the window's integer scale (at 1280x720 three screen pixels instead
## of four, at 1920x1080 four instead of six). A fixed 0.75 would draw uneven pixels at 1920x1080; 0.5 is even
## everywhere but small. Positions below are in field units (art pixels); screen rows divide by the scale.
##
## A machine too tall for its slot stands lower, just enough to keep the clips it holds between moves on screen (its
## home row), and steps down further only while a taller clip plays (staying down for death); never past the player's
## row, so an enemy never steps in front. At the zoomed-out scale few machines need it; at a 320x180 window (scale 1)
## five of the six did. scripts/scenes/battle.gd places machines through these functions and
## tools/debug/battle_fit_check.gd checks every frame through the same ones.

const Anim := preload("res://scripts/ui/machine_anim.gd")

const PLAYER_FEET_Y := 121            # screen rows
const ENEMY_FEET_Y := 101
const MARGIN := 4                     # screen pixels between a machine's canvas and the screen edge
const ENEMY_LANE := 150               # art narrower than this (art pixels) stays near the middle of its lane
const ZOOM := 0.7                     # the field's target size; field_scale() rounds it per window
const HOLD_CLIPS := ["idle", "hit"]   # what battle.gd shows between moves
const STEP_TIME := 0.12               # seconds a step down takes (linear)

static var zoom_override := 0.0       # tools only (battle_capture.gd's HT_FIELD_ZOOM): a fixed scale


## The integer scale the window draws the 320x180 screen at (the project's stretch mode is canvas_items, integer).
static func window_scale(window_size: Vector2i) -> int:
	return maxi(1, mini(window_size.x / 320, window_size.y / 180))


## The field's scale for a window drawn at integer scale `k`: ZOOM rounded to whole screen pixels per art pixel.
static func field_scale(k: int) -> float:
	if zoom_override > 0.0:
		return zoom_override
	return maxf(1.0, roundf(k * ZOOM)) / k


## The field's size in field units.
static func field_size(s: float) -> Vector2:
	return Vector2(320.0, 180.0) / s


static func feet_row(is_player: bool) -> int:
	return PLAYER_FEET_Y if is_player else ENEMY_FEET_Y


## The x of the machine node's origin: the player's canvas at the left edge, the enemy's (mirrored, so placed by its
## right edge) at the right, small enemy art nearer the middle of its lane.
static func home_x(node: Node2D, is_player: bool, s: float) -> float:
	if is_player:
		return MARGIN / s
	var x := (320.0 - MARGIN) / s
	var w: int = node.get_meta("width")
	if w < ENEMY_LANE:
		x -= (ENEMY_LANE - w) / 2
	return x


## The y of the machine node's origin between moves.
static func home_y(node: Node2D, is_player: bool, s: float) -> int:
	return _fit(node, feet_row(is_player), Anim.clips_top(node, HOLD_CLIPS), s)


## The y while `clip` plays: home, or lower when the clip reaches higher than the home row allows.
static func clip_y(node: Node2D, is_player: bool, clip: String, s: float) -> int:
	return maxi(home_y(node, is_player, s), _fit(node, feet_row(is_player), Anim.clip_top(node, clip), s))


## The field y of the machine's visible top between moves (for the damage numbers).
static func art_top(node: Node2D) -> float:
	return node.position.y + Anim.clips_top(node, HOLD_CLIPS)


static func _fit(node: Node2D, row: int, top: int, s: float) -> int:
	var feet: int = node.get_meta("feet_y")
	var y := roundi(row / s) - feet
	if y + top < 0:
		y = mini(-top, roundi(PLAYER_FEET_Y / s) - feet)
	return y
