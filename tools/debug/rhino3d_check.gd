extends SceneTree
## Checks the 3D slice (Claude, 2026-11-04): with the camera fixed, the rhino turned through eight headings shows
## the right view and mirror (sw, w and nw are se, e and ne flipped); its feet stand on the ground; every walk has
## 8 frames and every view an idle; sprites and world share 50 texels per metre.
## Run: Godot --headless --fixed-fps 60 --path . --script res://tools/debug/rhino3d_check.gd
## With a window, add "-- --shot" to also walk the rhino and save two screenshots next to the walk art.

const SCENE := preload("res://scenes/moba3d/field_test.tscn") # the dressed field (rhino_walk_test.tscn is bare)
const SHOT_DIR := "res://docs/art/moba/rhino_l/take-a/anim/"

var fails := 0


func _initialize() -> void:
	_run.call_deferred()


func _check(ok: bool, what: String) -> void:
	print(("PASS " if ok else "FAIL ") + what)
	if not ok:
		fails += 1


func _run() -> void:
	var shot := OS.get_cmdline_user_args().has("--shot")
	if shot:
		DisplayServer.window_set_size(Vector2i(1280, 720))
	var scene := SCENE.instantiate()
	root.add_child(scene)
	await process_frame
	var player := scene.get_node("Player")
	var sprite: DirectionalSprite3D = player.get_node("Sprite")
	var cam: Camera3D = scene.get_node("Camera")
	var frames := sprite.sprite_frames
	for v in ["s", "se", "e", "ne", "n"]:
		_check(frames.has_animation("walk_" + v) and frames.get_frame_count("walk_" + v) == 8, "walk_%s has 8 frames" % v)
		_check(frames.has_animation("idle_" + v), "idle_%s exists" % v)
	_check(sprite.animation == &"idle_n", "starts on the back view, facing away from the camera")
	var b := cam.global_basis
	var fwd := Vector3(-b.z.x, 0.0, -b.z.z).normalized()
	var right := Vector3(b.x.x, 0.0, b.x.z).normalized()
	var expect := [[0, "n", false], [45, "ne", false], [90, "e", false], [135, "se", false], [180, "s", false],
		[-135, "se", true], [-90, "e", true], [-45, "ne", true], [20, "n", false], [-160, "s", false]]
	for e in expect:
		var a := deg_to_rad(float(e[0]))
		sprite.show_facing(fwd * cos(a) + right * sin(a), b, true)
		var ok: bool = sprite.view == e[1] and sprite.flip_h == e[2] and sprite.animation == StringName("walk_" + e[1])
		_check(ok, "heading %d deg shows walk_%s%s (got %s, flip %s)" % [e[0], e[1], " mirrored" if e[2] else "",
			sprite.animation, sprite.flip_h])
	var feet_y := sprite.global_position.y - (sprite.feet_edge_row - sprite.canvas_height / 2.0) * sprite.pixel_size
	_check(absf(feet_y - player.global_position.y) < 0.001, "feet stand on the ground (%.4f m)" % feet_y)
	_check(is_equal_approx(sprite.pixel_size, 0.02), "sprite at 50 texels per metre")
	for a in ["horn_toss", "ground_pound", "brace", "stampede"]:
		for v in ["s", "se", "e", "ne", "n"]:
			_check(frames.has_animation("%s_%s" % [a, v]), "%s_%s exists" % [a, v])
	for v in ["s", "e", "n"]:
		_check(frames.has_animation("brace_shuffle_" + v), "brace_shuffle_%s exists" % v)
	# The kit (run with --fixed-fps 60 so these frame counts are real time).
	var kit: RhinoKit = player.get_node("Kit")
	var d1 = scene.get_node("Dummy1")
	player.global_position = Vector3.ZERO
	player.facing = Vector3(0, 0, -1)
	kit.horn_toss()
	for i in 90:
		await process_frame
	_check(d1.global_position.z > 1.5 and d1.stunned > 0.0,
		"horn toss throws the dummy ahead over the back, stunned (z %.2f, stun %.2f)" % [d1.global_position.z, d1.stunned])
	var d2 = scene.get_node("Dummy2")
	player.global_position = d2.global_position + Vector3(0, 0, 1.8)
	kit.ground_pound()
	for i in 60:
		await process_frame
	_check(d2.slowed > 0.0, "ground pound slows a dummy inside the ring (slow %.2f)" % d2.slowed)
	var waited := 0
	while kit.current != "" and waited < 300:  # the tremor stomps about 2.8 s in all (game feel lane, 2026-11-05)
		await process_frame
		waited += 1
	_check(not player.busy and sprite.action == "", "the rhino is free again after the pound (%.2f s after the slow check)" % (waited / 60.0))
	# The braced-walk checks are retired: Aftershock replaced Brace on slot 3, 2026-11-20 (game feel lane).
	# Aftershock is covered by D:/dev/_scratch/game_feel/probe/aftershock_probe.gd.
	# The own-view rule, on a made-up action drawn only in s, e and n (every real action has se and ne now).
	var sheet := sprite.sprite_frames
	var test_sheet: SpriteFrames = sheet.duplicate()
	for v in ["s", "e", "n"]:
		test_sheet.add_animation(StringName("test_act_" + v))
	sprite.sprite_frames = test_sheet
	sprite.view = "se"
	sprite.action = "test_act"
	_check(sprite.action_anim() == &"test_act_e",
		"an action with no se drawing shows its side view in se (got %s)" % sprite.action_anim())
	test_sheet.add_animation(&"test_act_se")
	_check(sprite.action_anim() == &"test_act_se",
		"an action drawn in se plays its own se frames (got %s)" % sprite.action_anim())
	_check(not sheet.has_animation(&"test_act_e"), "the test animations stayed off the real sheet")
	sprite.sprite_frames = sheet
	sprite.action = "brace"
	_check(sprite.shuffle_anim() == &"brace_shuffle_e", "braced in se, the shuffle falls back on e (got %s)" % sprite.shuffle_anim())
	sprite.action = ""
	sprite.view = "n"
	# Size classes (Preston, option B): L 0.020, M 0.018, S 0.016 m a texel; the feet stay on the ground on any canvas.
	_check(sprite.size_class == "L" and is_equal_approx(sprite.size_scale(), 1.0), "the rhino is class L at scale 1.0")
	for c in [["M", 0.018, 131], ["S", 0.016, 141]]:
		var holder := Node3D.new()
		var t := DirectionalSprite3D.new()
		t.name = "Sprite"
		t.canvas_height = 160
		t.feet_edge_row = c[2]
		t.size_class = c[0]
		holder.add_child(t)
		scene.add_child(holder)
		var fy: float = t.global_position.y - (t.feet_edge_row - t.canvas_height / 2.0) * float(c[1])
		_check(is_equal_approx(t.pixel_size, c[1]) and absf(fy) < 0.001,
			"class %s on a 160 canvas: %.3f m a texel, feet on the ground (%.4f m)" % [c[0], t.pixel_size, fy])
		var hs := HexShield.shield(holder, 1.0)
		_check(is_equal_approx(hs.radius, 1.1 * t.size_scale()),
			"a hex shield on a class %s machine is sized to it (%.3f m, scale %.2f)" % [c[0], hs.radius, t.size_scale()])
		holder.queue_free()
	var ring: Node3D = player.get_node("Ring")
	var ring_l := ring.scale.x
	sprite.size_class = "M"
	player.apply_size_class()
	var k_m := sprite.size_scale()
	_check(is_equal_approx(ring.scale.x, ring_l * k_m), "the ground ring follows the class (M %.3f vs L %.3f)" % [ring.scale.x, ring_l])
	sprite.size_class = "L"
	player.apply_size_class()
	var back_y := sprite.global_position.y - (sprite.feet_edge_row - sprite.canvas_height / 2.0) * 0.02
	_check(is_equal_approx(sprite.pixel_size, 0.02) and is_equal_approx(ring.scale.x, ring_l) and absf(back_y - player.global_position.y) < 0.001,
		"back to L, the rhino and its ring are as before")
	player.global_position = Vector3.ZERO
	if shot:
		player.input_override = Vector2(0.6, -0.8)  # forward and a little right: the reel's view from behind
		for i in 75:
			await process_frame
		root.get_texture().get_image().save_png(SHOT_DIR + "rhino3d-slice-behind.png")
		player.input_override = Vector2(1.0, 0.0)  # strafe right: the side walk
		cam.yaw_degrees = 25.0
		for i in 60:
			await process_frame
		root.get_texture().get_image().save_png(SHOT_DIR + "rhino3d-slice-side.png")
		print("saved screenshots")
	print("rhino3d_check: %d failures" % fails)
	quit(1 if fails else 0)
