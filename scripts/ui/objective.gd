extends RefCounted
## What to do next, worked out from the story flags. One short line for the screen and a longer one for a
## menu page. Hollowtide's lesson: tell the player where to go from the first minute.

static func current(flags: Dictionary) -> Dictionary:
	if not flags.get("opening_seen", false):
		return _goal("", "")
	if not flags.get("first_battle_won", false):
		return _goal("Go out the east door. Win your first battle.",
			"The field is east of the hangar. A rival machine waits in the grass.")
	if not flags.get("canyon_battle_won", false):
		return _goal("Take the road east into the canyon.",
			"Something flies over the canyon. Your new command, Air Lock, makes your weapons anti-air.")
	return _goal("Next: the town past the canyon (not built yet).",
		"Placeholder for the goal after the canyon.")


static func _goal(short: String, long: String) -> Dictionary:
	return {"short": short, "long": long}
