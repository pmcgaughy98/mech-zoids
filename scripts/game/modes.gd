extends RefCounted
## The game's modes: every screen the game can be in, and the scene that runs it (Claude, 2026-10-13).
##
## Structure from Zoids Legacy's game state machine (jmacato/ZoidsLegacyDecomp, src/game/run_game_state_machine.c,
## read for structure only): one current mode, each mode a self-contained screen, every handover by setting the next
## mode. Ours keeps the same list so the game has a home for every system from the start; modes not built yet open
## the generic menu scene in its "stub" state, so the wiring can be walked end to end.
##
## status: "built" (its own scene), "menu" (the data-driven menu scene, working), "stub" (menu scene placeholder).
## Change modes through Run.go_mode(mode, args).

const MODES := {
	"intro": {"scene": "opening", "status": "built", "zl": "intro"},
	"title": {"scene": "title", "status": "built", "zl": "title menu"},
	"field": {"scene": "base", "status": "built", "zl": "field (our base, field, field2 scenes)"},
	"pause_menu": {"scene": "", "status": "built", "zl": "pause menu (an overlay in our field scenes)"},
	"battle": {"scene": "battle", "status": "built", "zl": "battle"},
	"item_shop": {"scene": "menu_mode", "status": "menu", "zl": "item shop"},
	"parts_shop": {"scene": "menu_mode", "status": "menu", "zl": "weapon and armor shops"},
	"lab": {"scene": "menu_mode", "status": "menu", "zl": "machine lab: build from data and cores, customise loadout"},
	"database": {"scene": "menu_mode", "status": "menu", "zl": "database: machines, pilots and parts seen"},
	"arena": {"scene": "menu_mode", "status": "menu", "zl": "challenge menu: battles under rules"},
	"team_setup": {"scene": "menu_mode", "status": "menu", "zl": "team setup: pilots into machines, six slots"},
	"town_map": {"scene": "menu_mode", "status": "stub", "zl": "town map: travel between places"},
	"battle_scene": {"scene": "menu_mode", "status": "stub", "zl": "battle scene: scripted story cut-in"},
	"form_change": {"scene": "menu_mode", "status": "stub", "zl": "form change scene"},
	"options": {"scene": "menu_mode", "status": "stub", "zl": "options"},
	"credits": {"scene": "menu_mode", "status": "stub", "zl": "credits"},
}


static func scene_of(mode: String) -> String:
	return MODES.get(mode, {}).get("scene", "")
