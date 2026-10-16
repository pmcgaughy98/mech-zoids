extends RefCounted
## Runs story event scripts (Claude, 2026-10-13).
##
## Structure from Zoids Legacy's event system (src/events/run_event_scripts.c and its 117 commands, read for
## structure only): a script is a list of commands run in order; each command does one thing (show text, offer a
## choice, test or set a flag, give items, start a battle, open a shop) and the blocking ones (text, choice, wait,
## battle, a mode change) hold the script until they finish. Ours: commands are arrays, scripts live in
## scripts/data/events.gd, text and choices go out as signals for whatever UI shows them; with `auto` on (headless
## checks, autopilot) text advances itself and choices take `auto_answers` in order (else the first option).
##
## Commands:
##   ["label", name]                 ["jump", name]                  ["end"]
##   ["text", speaker, line]         ["choice", [options...]]        (sets `last_choice`)
##   ["if_choice", i, label]         ["if_flag", flag, label]        ["if_not_flag", flag, label]
##   ["set_flag", flag]              ["clear_flag", flag]            ["wait", seconds]
##   ["give_money", n]               ["give_item", "items"|"parts", id, n]   ["give_core", machine_id, n]
##   ["unlock_data", machine_id]     ["unlock_command", id]          ["add_pilot", id]   ["add_machine", id]
##   ["battle", {enemy, purse, core, rule, flag, reward, win_scene}]  (ends the script; the battle takes over)
##   ["mode", mode, args]            (ends the script; Run.go_mode)

signal say(speaker: String, line: String)
signal ask(options: Array)
signal finished(result: String)

const Roster := preload("res://scripts/game/roster.gd")
const Items := preload("res://scripts/data/items.gd")

var run                     # the Run autoload, or a stand-in for checks
var auto := false
var auto_answers: Array = []
var last_choice := -1
var log: Array = []         # what ran, for checks
var _advance := false
var _chosen := -1


func _init(run_ref, auto_mode := false) -> void:
	run = run_ref
	auto = auto_mode


## The UI calls these when the player advances text or picks an option.
func advance() -> void:
	_advance = true


func choose(i: int) -> void:
	_chosen = i


## Runs a script to its end (await it). Returns "end", "battle" or "mode".
func run_script(script: Array) -> String:
	var labels := {}
	for i in script.size():
		if script[i][0] == "label":
			labels[script[i][1]] = i
	var pc := 0
	while pc < script.size():
		var c: Array = script[pc]
		pc += 1
		log.append(c[0])
		match c[0]:
			"label":
				pass
			"end":
				break
			"jump":
				pc = labels[c[1]]
			"text":
				say.emit(c[1], c[2])
				if not auto:
					_advance = false
					while not _advance:
						await Engine.get_main_loop().process_frame
			"choice":
				ask.emit(c[1])
				if auto:
					last_choice = auto_answers.pop_front() if not auto_answers.is_empty() else 0
				else:
					_chosen = -1
					while _chosen < 0:
						await Engine.get_main_loop().process_frame
					last_choice = _chosen
			"if_choice":
				if last_choice == c[1]:
					pc = labels[c[2]]
			"if_flag":
				if run.has_flag(c[1]):
					pc = labels[c[2]]
			"if_not_flag":
				if not run.has_flag(c[1]):
					pc = labels[c[2]]
			"set_flag":
				run.set_flag(c[1])
			"clear_flag":
				run.flags.erase(c[1])
			"wait":
				if not auto:
					await Engine.get_main_loop().create_timer(float(c[1])).timeout
			"give_money":
				run.money = min(Items.MONEY_LIMIT, run.money + int(c[1]))
			"give_item":
				var bag: Dictionary = run.items if c[1] == "items" else run.parts
				bag[c[2]] = min(Items.QUANTITY_LIMIT, int(bag.get(c[2], 0)) + int(c[3]))
			"give_core":
				run.cores[c[1]] = min(Items.QUANTITY_LIMIT, int(run.cores.get(c[1], 0)) + int(c[2]))
			"unlock_data":
				if not run.unlocked_data.has(c[1]):
					run.unlocked_data.append(c[1])
			"unlock_command":
				run.give_command(c[1])
			"add_pilot":
				Roster.add_pilot(run, c[1])
			"add_machine":
				run.roster.append(Roster.new_machine_record(run, c[1]))
			"battle":
				if not auto:
					run.start_story_battle(c[1])
				finished.emit("battle")
				return "battle"
			"mode":
				if not auto:
					run.go_mode(c[1], c[2] if c.size() > 2 else {})
				finished.emit("mode")
				return "mode"
	finished.emit("end")
	return "end"
