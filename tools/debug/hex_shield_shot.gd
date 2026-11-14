extends SceneTree
## Renders the gorilla's hex shield and hex dome in the dressed field (Claude, 2026-11-04). The gorilla plays its packed
## Codex frames (art/machines/ape/ape_frames.tres, from tools/art/pack_ape_3d.py). Saves three shots next to the
## gorilla art.
## Run with a window: Godot --path . --resolution 1280x720 --position 20000,20000 -s res://tools/debug/hex_shield_shot.gd

const SCENE := preload("res://scenes/moba3d/field_test.tscn")
const APE_FRAMES := preload("res://art/machines/ape/ape_frames.tres")
const OUT := "res://docs/art/moba/ape_l/take-a/anim/"


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	DisplayServer.window_set_size(Vector2i(1280, 720))
	var scene := SCENE.instantiate()
	root.add_child(scene)
	await process_frame
	var player := scene.get_node("Player")
	var sprite: DirectionalSprite3D = player.get_node("Sprite")
	sprite.sprite_frames = APE_FRAMES
	sprite.canvas_height = 192
	sprite.feet_edge_row = 161  # the packed frames' feet stand on row 160
	sprite.position.y = (sprite.feet_edge_row - sprite.canvas_height / 2.0) * sprite.pixel_size
	sprite.play(&"idle_e")
	player.global_position = Vector3.ZERO
	player.facing = Vector3(1.0, 0.0, -0.35).normalized()
	var ally: Node3D = scene.get_node("Dummy1")
	ally.global_position = Vector3(2.6, 0.0, -1.6)
	for d in ["Dummy2", "Dummy3", "Dummy4"]:
		scene.get_node(d).visible = false
	for i in 20:
		await process_frame
	HexShield.shield(player, 99.0)
	HexShield.shield(ally, 99.0)
	for i in 30:
		await process_frame
	root.get_texture().get_image().save_png(OUT + "hex-shield-shot-a.png")
	for i in 24:
		await process_frame
	root.get_texture().get_image().save_png(OUT + "hex-shield-shot-b.png")
	for s in player.get_children() + ally.get_children():
		if s is HexShield:
			s.queue_free()
	HexShield.raise_dome(scene, Vector3(1.3, 0.0, -0.8), 3.2, 99.0)
	for i in 30:
		await process_frame
	root.get_texture().get_image().save_png(OUT + "hex-dome-shot.png")
	print("hex shield shots saved")
	quit()
