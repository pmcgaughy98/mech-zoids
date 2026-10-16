extends RefCounted
## Story event scripts (Claude, 2026-10-13). DRAFT: every line, name and beat here is a placeholder to show the
## runner working (scripts/events/event_runner.gd); Preston writes the story. Command list: see event_runner.gd.

const EVENTS := {
	# A town visit: the lab's first welcome, a choice, a gift, a shop offer.
	"town_lab_welcome": [
		["if_flag", "lab_welcomed", "already"],
		["text", "Lab Chief", "(draft) You're the new pilot? We can rebuild machines here, if you bring a core."],
		["choice", ["Tell me about cores.", "Maybe later."]],
		["if_choice", 1, "later"],
		["text", "Lab Chief", "(draft) Every machine line has a core. Find one, unlock its data, and we'll build it."],
		["unlock_data", "pangolin_m"],
		["give_core", "pangolin_m", 1],
		["text", "Lab Chief", "(draft) Here, a Scale-line core to start you off."],
		["label", "later"],
		["give_item", "items", "repair_kit", 2],
		["set_flag", "lab_welcomed"],
		["choice", ["Open the lab.", "Leave."]],
		["if_choice", 1, "done"],
		["mode", "lab"],
		["label", "already"],
		["text", "Lab Chief", "(draft) Back again? The bench is ready."],
		["mode", "lab"],
		["label", "done"],
		["end"],
	],
	# An arena challenge from a script: the battle takes over, its result sets the flag.
	"arena_first_bout": [
		["text", "Arena Host", "(draft) First bout! One machine a side."],
		["battle", {"enemy": ["pangolin_m"], "rule": "solo", "purse": 400, "core": "", "flag": "arena_bout_1",
			"reward": "", "win_scene": "base"}],
	],
}
