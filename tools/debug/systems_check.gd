extends SceneTree
## Checks the pieces that are not scene changes: saving and loading, the deck rules, Continue on the title.
## Run: Godot --headless --path . --script res://tools/debug/systems_check.gd

const Commands := preload("res://scripts/data/commands.gd")

var fails := 0
var frame := 0
var run: Node


func _process(_delta: float) -> bool:
	frame += 1
	if frame == 1:
		run = root.get_node_or_null("Run")
		if run == null:
			run = load("res://scripts/run.gd").new()
			run.name = "Run"
			root.add_child(run)
		return false
	if frame > 2:  # a script error stopped the tests part way: fail instead of looping
		print("systems_check: FAIL (stopped by an error)")
		quit(1)
		return true
	run.save_path = "user://systems_check_save.json"  # never touch the real save
	DirAccess.remove_absolute(ProjectSettings.globalize_path(run.save_path))

	print("deck rules")
	run.new_game()
	_ok("new game equips the starter deck", run.deck == Commands.STARTER_DECK)
	_ok("taking a command out works", run.toggle_deck("mine_field") and not run.deck.has("mine_field"))
	_ok("putting it back works", run.toggle_deck("mine_field") and run.deck.has("mine_field"))
	for i in Commands.DECK_LIMIT:
		run.owned.append("x%d" % i)
	for id in run.owned:
		if not run.deck.has(id):
			run.toggle_deck(id)
	_ok("the deck stops at %d" % Commands.DECK_LIMIT, run.deck.size() == Commands.DECK_LIMIT)
	run.new_game()
	run.give_command("air_lock")
	_ok("a reward command is owned and equipped", run.owned.has("air_lock") and run.deck.has("air_lock"))

	print("saving")
	_ok("no save at first", not run.has_save())
	run.set_flag("opening_seen")
	run.set_flag("first_battle_won")
	run.location = "field"
	run.toggle_deck("shield_wall")
	var before := {"deck": run.deck.duplicate(), "owned": run.owned.duplicate(), "flags": run.flags.duplicate()}
	_ok("save writes a file", run.save_game() and run.has_save())
	run.new_game()
	_ok("load reads it back", run.load_game())
	_ok("deck survives save and load", run.deck == before.deck)
	_ok("owned commands survive", run.owned == before.owned)
	_ok("story flags survive", run.flags == before.flags)
	_ok("location survives (Continue goes to the field)", run.location == "field")

	print("title")
	var title: Node = load("res://scenes/title.tscn").instantiate()
	root.add_child(title)
	_ok("title offers Continue when a save exists", title.choices.has("Continue"))
	title.queue_free()
	DirAccess.remove_absolute(ProjectSettings.globalize_path(run.save_path))

	print("\nsystems_check: %s" % ("PASS" if fails == 0 else "FAIL (%d)" % fails))
	quit(1 if fails > 0 else 0)
	return true


func _ok(what: String, good: bool) -> void:
	print("  %s  %s" % ["ok  " if good else "FAIL", what])
	if not good:
		fails += 1
