extends SceneTree
## Plays the whole start on autopilot through the real scene changes and reports each handoff.
## The first battle is lost on purpose (towed home, objective unchanged, try again). After that the autopilot
## plays properly and may need retries, which is part of the test. Then the canyon: the first win's reward
## command goes into the deck, the flyer is fought, and the canyon talk plays.
## Run: Godot --headless --fixed-fps 60 --path . --script res://tools/debug/start_chain_check.gd

const Objective := preload("res://scripts/ui/objective.gd")

const OPENING := ["title", "opening", "base"]
const FRAME_LIMIT := 30000

var run: Node
var seen: Array = []
var frames := 0
var fails := 0
var started := false
var lose_checked := false


func _process(_delta: float) -> bool:
	frames += 1
	if not started:
		started = true
		run = root.get_node_or_null("Run")
		if run == null:
			run = load("res://scripts/run.gd").new()
			run.name = "Run"
			root.add_child(run)
		run.autopilot = true
		run.autopilot_lose = true
		run.save_path = "user://chain_check_save.json"  # never touch the real save
		change_scene_to_file("res://scenes/title.tscn")
		return false
	var cs := current_scene
	if cs != null and cs.scene_file_path != "":
		var name := cs.scene_file_path.get_file().get_basename()
		if seen.size() == 0 or seen[-1] != name:
			seen.append(name)
			print("handoff %d: %-8s frame %5d   objective: %s" % [seen.size(), name, frames,
				Objective.current(run.flags).short])
	if seen.size() == 6 and not lose_checked:
		lose_checked = true
		_ok("first battle was lost", run.battles.size() == 1 and run.battles[0].winner == "enemy")
		_ok("losing leaves the story where it was", not run.has_flag("first_battle_won"))
		_ok("objective still says win the first battle", Objective.current(run.flags).short.begins_with("Go out"))
		run.autopilot_lose = false
	if run.has_flag("canyon_battle_won_debriefed"):
		return _finish()
	if frames > FRAME_LIMIT:
		print("stuck after %d frames in '%s'" % [frames, seen[-1] if seen.size() > 0 else "?"])
		fails += 1
		return _finish()
	return false


func _finish() -> bool:
	print("")
	# Rebuild the route the handoffs should have taken from the battles that happened.
	var expected := OPENING.duplicate()
	for b in run.battles:
		var canyon: bool = b.flag == "canyon_battle_won"
		expected.append_array(["field", "field2", "battle"] if canyon else ["field", "battle"])
		expected.append(("field2" if canyon else "base") if b.winner == "player" else "base")
	_ok("handoffs in order: %s" % " > ".join(seen), seen == expected and run.battles.size() >= 3)
	_ok("opening was seen", run.has_flag("opening_seen"))
	var wins: Array = run.battles.filter(func(b): return b.winner == "player")
	_ok("exactly two wins, first battle then canyon (%d battles in all)" % run.battles.size(),
		wins.size() == 2 and wins[0].flag == "first_battle_won" and wins[1].flag == "canyon_battle_won")
	_ok("deck commands were played in both won battles", wins.all(func(b): return b.commands > 0))
	_ok("first win gave Air Lock and it went into the deck", run.owned.has("air_lock") and run.deck.has("air_lock"))
	_ok("mechanic's talk played at base after the first win", run.has_flag("first_battle_won_debriefed"))
	_ok("canyon talk played in the canyon", run.has_flag("canyon_battle_won_debriefed"))
	_ok("objective moved on to the next goal", Objective.current(run.flags).short.begins_with("Next:"))
	print("\nstart_chain_check: %s" % ("PASS" if fails == 0 else "FAIL (%d)" % fails))
	quit(1 if fails > 0 else 0)
	return true


func _ok(what: String, good: bool) -> void:
	print("  %s  %s" % ["ok  " if good else "FAIL", what])
	if not good:
		fails += 1
