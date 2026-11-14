extends SceneTree
## Aim check (game feel lane, 2026-11-05; Preston: "B: aim at the mouse"). Opens the arena, puts the aim on four
## screen points around the player's machine (aim_screen_override stands in for the mouse), presses key 1 at each and
## checks the angle between the machine's facing and the aim. Windowed, it also saves a frame 0.3 s after each press
## and logs the view the sprite shows (or the 3D body's heading). Headless it skips the frames.
## 2026-11-10: points moved for the SMITE-fit chase camera (pitch 13, distance 12, look_height 3.2; camera lane): the
## feet sit about 71% down the screen, so the near point is 0.2 of the height below them, not 0.3 (that left the
## screen). Pass --gorilla to aim the 3D gorilla instead of the rhino sprite.
## Run: godot --path . --resolution 1280x720 --fixed-fps 30 -s res://tools/debug/aim_check.gd -- --out=<dir> [--gorilla]
## or headless: godot --headless --path . --fixed-fps 30 -s res://tools/debug/aim_check.gd [-- --gorilla]
const MAX_ERR_DEG := 5.0
var out := "user://aim_check"
var gorilla := false
var fails := 0


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
		elif a == "--gorilla":
			gorilla = true
	DirAccess.make_dir_recursive_absolute(out)
	change_scene_to_file("res://scenes/moba3d/arena_play.tscn")
	_run.call_deferred()


func _wait(n: int) -> void:
	for i in n:
		await process_frame


func _key(code: Key, down: bool) -> void:
	var ev := InputEventKey.new()
	ev.physical_keycode = code
	ev.keycode = code
	ev.pressed = down
	Input.parse_input_event(ev)


func _run() -> void:
	await _wait(45)
	if gorilla:
		current_scene.set_machine("gorilla")
		await _wait(5)
	var p = current_scene.get("player")
	var headless := DisplayServer.get_name() == "headless"
	var lines := PackedStringArray()
	var k := 0
	var vs := root.get_visible_rect().size
	lines.append("viewport %s, machine %s%s" % [vs, current_scene.machine, " (headless: no frames)" if headless else ""])
	for f in [Vector2(0.25, 0.0), Vector2(0.0, -0.3), Vector2(-0.25, 0.1), Vector2(0.12, 0.2)]:  # right, away, left and near, toward the camera
		var off: Vector2 = f * vs
		k += 1
		p.cooldowns.clear()  # each press casts: the check is about aim, not cooldowns
		var cam := root.get_camera_3d()
		var c := cam.unproject_position(p.global_position)
		var at := c + off
		var on_screen := Rect2(Vector2.ZERO, vs).has_point(at)
		p.aim_screen_override = at
		await _wait(3)
		var want: Vector3 = p.aim_dir()
		var before: Vector3 = p.facing
		_key(KEY_1, true)
		await _wait(1)
		var got: Vector3 = p.facing
		_key(KEY_1, false)
		var err := absf(rad_to_deg(Vector2(want.x, want.z).angle_to(Vector2(got.x, got.z))))
		await _wait(9)
		if not headless:
			var img := root.get_texture().get_image()
			if img != null:
				img.save_png(out.path_join("aim%d.png" % k))
		var b = p.get("body")
		var shows := ("body heading %.0f deg, action %s" % [rad_to_deg(b.model_root().rotation.y), b.action]) if b != null else ("sprite view %s%s, action %s" % [p.sprite.view, " mirrored" if p.sprite.mirrored else "", p.sprite.action])
		var ok := on_screen and err <= MAX_ERR_DEG
		if not ok:
			fails += 1
		lines.append("%s aim %d: screen %s (machine at %s, %.0f%% down)%s, aim dir (%.2f, %.2f), facing before (%.2f, %.2f) after (%.2f, %.2f), error %.1f deg, %s" % ["PASS" if ok else "FAIL", k, at.round(), c.round(), 100.0 * c.y / vs.y, "" if on_screen else " OFF SCREEN", want.x, want.z, before.x, before.z, got.x, got.z, err, shows])
		await _wait(150)
	lines.append("aim_check: %d failures" % fails)
	var fa := FileAccess.open(out.path_join("log.txt"), FileAccess.WRITE)
	if fa != null:
		fa.store_string("\n".join(lines) + "\n")
		fa.close()
	print("\n".join(lines))
	quit(1 if fails > 0 else 0)
