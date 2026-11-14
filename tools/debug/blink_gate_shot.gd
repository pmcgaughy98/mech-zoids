extends SceneTree
## A short clip of the fennec's blink gate (Claude, 2026-11-04, game feel lane) for the hub and Preston: blink, snap
## back through the gate, then blink again and let the window run out. Saves one PNG per frame; ffmpeg makes the clip.
## Run (windowed, not headless): Godot --path . --resolution 1280x720 --fixed-fps 30
##   --script res://tools/debug/blink_gate_shot.gd -- --out=<dir>

const SCENE := preload("res://scenes/moba3d/arena_play.tscn")

var out := ""
var frame := 0
var top: Node3D


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out)
	_run.call_deferred()


func _grab(n: int) -> void:
	for i in n:
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(out.path_join("f%04d.png" % frame))
		frame += 1


func _run() -> void:
	top = SCENE.instantiate()
	top.sandbox = true
	root.add_child(top)
	for i in 10:
		await process_frame
	top.swap()
	top.swap()
	var player = top.player
	var kit = player.get_node("Kit")
	player.facing = Vector3.RIGHT
	for i in 30:
		await process_frame
	var p0: Vector3 = player.global_position
	await _grab(20)
	kit.blink_gate(p0 + Vector3.RIGHT * 10.0)
	print("blink 1 at frame %d: %s -> %s" % [frame, p0, player.global_position])
	await _grab(30)
	kit.gate_back()
	print("snap back at frame %d: now %s, %.3f m from the start" % [frame, player.global_position,
		Vector3(player.global_position.x - p0.x, 0, player.global_position.z - p0.z).length()])
	await _grab(25)
	player.facing = Vector3.LEFT
	var p1: Vector3 = player.global_position
	kit.blink_gate(p1 + Vector3.LEFT * 10.0)
	print("blink 2 at frame %d: %s -> %s" % [frame, p1, player.global_position])
	var closed_at := -1
	for i in int(kit.gate_window * 30.0) + 25:
		await _grab(1)
		if closed_at < 0 and not kit.gate_open:
			closed_at = frame
	print("gate closed by itself at frame %d; frames %d" % [closed_at, frame])
	quit()
