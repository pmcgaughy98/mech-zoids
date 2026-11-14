extends SceneTree
## Per-animation tilt check (Claude, 2026-11-04, game feel lane): a SpriteFrames meta "tilt_anims" tilts only the listed
## animations, the node never moves, and frames with no meta stay upright as in the game.
## Run: godot --headless --path . --script res://tools/debug/tilt_check.gd

var fails := 0


func _initialize() -> void:
	_run.call_deferred()


func _ok(c: bool, what: String) -> void:
	print(("PASS " if c else "FAIL ") + what)
	if not c:
		fails += 1


func _run() -> void:
	await process_frame
	var base: SpriteFrames = load("res://art/machines/rhino/rhino_frames.tres")
	var sf := base.duplicate(true) as SpriteFrames
	sf.set_meta("tilt_anims", ["idle"])
	var d := DirectionalSprite3D.new()
	d.sprite_frames = sf
	root.add_child(d)
	await process_frame
	var y0 := d.position.y
	d.play(&"idle_s")
	_ok(d.tilted_now() and d.material_override is ShaderMaterial, "idle plays tilted")
	_ok(d.material_override != null and d.material_override.get_shader_parameter("tex") is Texture2D,
		"the tilted material has the frame's texture")
	_ok(d.material_override != null and is_equal_approx(float(d.material_override.get_shader_parameter("lift")), y0),
		"the shader's pivot is the feet row")
	d.play(&"walk_s")
	_ok(not d.tilted_now() and d.material_override == null, "walk plays upright")
	_ok(is_equal_approx(d.position.y, y0), "the node stays put")
	d.play(&"idle_e")
	_ok(d.material_override != null, "back to idle tilts again")
	_ok(d.tilts_any(), "tilts_any is true with the meta")
	var plain_sf := base.duplicate(true) as SpriteFrames  # the rhino's own frames carry the meta since its cam35 idle
	if plain_sf.has_meta("tilt_anims"):
		plain_sf.remove_meta("tilt_anims")
	var plain := DirectionalSprite3D.new()
	plain.sprite_frames = plain_sf
	root.add_child(plain)
	await process_frame
	plain.play(&"idle_s")
	_ok(plain.material_override == null and not plain.tilts_any(), "no meta: upright, as in the game")
	_ok(plain.billboard == BaseMaterial3D.BILLBOARD_FIXED_Y, "upright turns round the vertical axis (Y billboard)")
	print("tilt_check: %d fail" % fails)
	quit()
