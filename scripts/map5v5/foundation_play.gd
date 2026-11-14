extends "res://scripts/moba3d/arena_play.gd"
## Separate traversal/training foundation. No five-player match rules or economy implied.
const MAP = preload("res://scripts/map5v5/foundation_map.gd")
const DIRECTOR = preload("res://scripts/map5v5/foundation_director.gd")
const HUD = preload("res://scripts/map5v5/foundation_hud.gd")

func _ready() -> void:
	# Reuse the current authored player and approved camera nodes, without running the old map builder.
	arena.free()
	arena = load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	# Remove old markers before entering the tree, so ambience never queues beds for freed markers.
	for marker in arena.get_node("Markers").get_children(): marker.free()
	arena.set_script(MAP)
	arena.name = "Arena"
	add_child(arena)
	for kind in ROSTER.kinds():
		if not MACHINES.has(kind): MACHINES.append(kind)
	player = arena.get_node("Player")
	player.global_position = arena.spawn_slots("blue")[0]
	player.facing = Vector3.FORWARD
	director = DIRECTOR.new()
	director.name = "FoundationTraining"
	add_child(director)
	director.setup(arena, player)
	hud = HUD.new()
	hud.director = director
	add_child(hud)
	_build_roster_menu.call_deferred()
	set_machine.call_deferred("gorilla")
	arena.get_node("Camera").snap()

func _unhandled_key_input(event: InputEvent) -> void:
	super._unhandled_key_input(event)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_F6:
			# Move the nine passive training bodies to the player for current combat/hold testing.
			var i := 0
			for m in director.machines:
				if m == player: continue
				var offset := Vector3((i % 3 - 1) * 4.0, 0, -4.0 - floori(i / 3.0) * 4.0)
				var at: Vector3 = player.global_position + offset
				if not ArenaMotion.blocked(m, at, 1.0): m.global_position = at
				i += 1
