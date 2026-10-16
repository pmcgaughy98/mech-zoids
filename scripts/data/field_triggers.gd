extends RefCounted
## Where story events start in each field scene (Claude, 2026-10-13). DRAFT placements.
##
## Structure from Zoids Legacy's event commands (event_if_player_in_rect, event_if_player_interaction,
## event_if_interacted_actor; read for structure only): a script starts when the player walks into an area or
## interacts with something. Ours, per trigger:
##   kind  "talk" (Z within reach of `rect`) or "touch" (walking into `rect`)
##   event a script id in scripts/data/events.gd
##   label shown at the spot ("" for none);  once: fires one time (sets "trig_<id>");
##   if_flag / if_not_flag: only while that story flag is (not) set;  autopilot: touch triggers fire on autopilot
##   only when this is true, so the start-chain check walks the story path unchanged.

const TRIGGERS := {
	"base": [
		{"id": "lab_terminal", "kind": "talk", "rect": Rect2(24, 34, 22, 18), "event": "town_lab_welcome",
			"label": "LAB", "once": false},
	],
	"field2": [],
	"field": [],
}


static func for_scene(scene: String) -> Array:
	return TRIGGERS.get(scene, [])


## Whether a trigger can fire now.
static func active(run, t: Dictionary) -> bool:
	if t.get("once", false) and run.has_flag("trig_" + t.id):
		return false
	if t.has("if_flag") and not run.has_flag(t.if_flag):
		return false
	if t.has("if_not_flag") and run.has_flag(t.if_not_flag):
		return false
	return true
