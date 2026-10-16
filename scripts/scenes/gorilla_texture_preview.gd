extends "res://scripts/scenes/model_lab_3d.gd"
## Separate review scene. Reads the finished snapshot without installing it.

func _ready() -> void:
	super._ready()
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	var path := ProjectSettings.globalize_path("res://docs/art/3d/gorilla-texture-2026-10-13/after/ape_l.glb")
	var error := document.append_from_file(path, state)
	if error != OK:
		push_error("Texture preview could not load: " + error_string(error))
		return
	remove_child(model)
	model.free()
	model = document.generate_scene(state)
	add_child(model)
	var environment := find_children("*", "WorldEnvironment", true, false)[0] as WorldEnvironment
	var sun := find_children("*", "DirectionalLight3D", true, false)[0] as DirectionalLight3D
	finish_count = metal_finish(model, environment.environment, sun)
	play_walk()
	play_clip("idle")
	camera_deg = -35.0
	target_deg = -35.0

func _process(delta: float) -> void:
	super._process(delta)
	_hud.text = "TEXTURE PREVIEW (SEPARATE)   " + _hud.text

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_6:
			play_clip("slam")
		elif event.keycode == KEY_7:
			play_clip("throw")
		elif event.keycode == KEY_8:
			play_clip("gait")
	super._unhandled_input(event)
