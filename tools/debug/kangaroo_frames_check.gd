extends SceneTree
## Kangaroo frames check (Claude, kangaroo session, 2026-11-05): the packed frames are the accepted 35-degree stills,
## every view the sprite can ask for exists standing and moving, and KangarooKit.install sets the M canvas.
## Run: godot --headless --path . --script res://tools/debug/kangaroo_frames_check.gd

const FRAMES := "res://art/machines/kangaroo/kangaroo_frames.tres"
const SRC := "res://docs/art/moba/kangaroo_m/take-a/cam35/take2/fixed/"
const VIEWS := ["s", "se", "e", "ne", "n"]

var fails := 0


func _initialize() -> void:
	_run.call_deferred()


func _ok(c: bool, what: String) -> void:
	print(("PASS " if c else "FAIL ") + what)
	if not c:
		fails += 1


func _lowest_row(img: Image) -> int:
	for y in range(img.get_height() - 1, -1, -1):
		for x in img.get_width():
			if img.get_pixel(x, y).a > 0.0:
				return y
	return -1


## Pixels that differ as shown: alpha anywhere, colour only where alpha > 0. The import's fix_alpha_border (on, as for
## the hippo) fills the colour of fully clear pixels, which no one sees, so raw bytes never match.
func _shown_diff(a: Image, b: Image) -> int:
	var n := 0
	for y in a.get_height():
		for x in a.get_width():
			var p := a.get_pixel(x, y)
			var q := b.get_pixel(x, y)
			if not is_equal_approx(p.a, q.a) or (q.a > 0.0 and not p.is_equal_approx(q)):
				n += 1
	return n


func _run() -> void:
	await process_frame
	var sf: SpriteFrames = load(FRAMES)
	_ok(sf != null, "frames load")
	if sf == null:
		quit(1)
		return
	_ok(sf.get_animation_names().size() == 10, "10 animations (%d)" % sf.get_animation_names().size())
	_ok(Array(sf.get_meta("tilt_anims", [])) == ["idle", "walk"], "tilt_anims idle and walk")
	_ok((sf.get_meta("feet", {}) as Dictionary).size() == 4, "feet meta has 4 numbers")
	for v in VIEWS:
		var src := Image.load_from_file(ProjectSettings.globalize_path(SRC + v + ".png"))
		src.convert(Image.FORMAT_RGBA8)
		for a in ["idle", "walk"]:
			var n := StringName(a + "_" + v)
			if not sf.has_animation(n):
				_ok(false, "%s exists" % n)
				continue
			var img := sf.get_frame_texture(n, 0).get_image()
			img.convert(Image.FORMAT_RGBA8)
			_ok(sf.get_frame_count(n) == 1 and img.get_size() == Vector2i(160, 160) and _lowest_row(img) == 140,
				"%s: 1 frame, 160 cell, feet row 140 (row %d)" % [n, _lowest_row(img)])
			_ok(_shown_diff(img, src) == 0, "%s is the accepted still: alpha everywhere and colour where seen (%d px off)"
				% [n, _shown_diff(img, src)])
	var p := Node3D.new()
	var spr := DirectionalSprite3D.new()
	spr.name = "Sprite"
	p.add_child(spr)
	root.add_child(p)
	var kit := KangarooKit.install(p)
	_ok(p.get_node("Kit") == kit, "install adds the kit")
	_ok(spr.sprite_frames == sf and spr.canvas_height == 160 and spr.feet_edge_row == 141 and spr.size_class == "M",
		"install sets frames, canvas 160, feet edge 141, size M")
	_ok(is_equal_approx(spr.size_scale(), 0.75), "size scale 0.75 of the L rhino (%.3f)" % spr.size_scale())
	_ok(kit.get("current") == null, "no `current`, so the bot leaves the kit alone")
	var cam := Basis.from_euler(Vector3(deg_to_rad(-35.0), 0.0, 0.0))
	var seen := {}
	for i in 8:
		var a := TAU * i / 8.0
		for moving in [false, true]:
			spr.show_facing(Vector3(sin(a), 0.0, cos(a)), cam, moving)
			seen[str(spr.animation) + ("m" if spr.flip_h else "")] = true
			_ok(sf.has_animation(spr.animation), "facing %d deg, %s: plays %s%s" % [
				i * 45, "moving" if moving else "standing", spr.animation, " mirrored" if spr.flip_h else ""])
	_ok(seen.size() == 16, "8 facings x standing and moving give 16 distinct pictures (%d)" % seen.size())
	print("kangaroo_frames_check: %d fail(s)" % fails)
	quit(1 if fails else 0)
