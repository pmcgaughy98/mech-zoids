extends SceneTree
## Chameleon camouflage check (chameleon lane, 2026-11-05). Renders the approved take-b e view through the tilted
## camouflage test shader, over the arena's lane grass at a 35-degree camera, and measures how much of the body each
## state shows: the share of body pixels that differ from the bare ground by more than 8% of the largest RGB distance.
## Targets for look B (Preston's pick): normal 95%+, hidden 0-3%, tell 8-30%, ally 45%+ with every eye pixel kept.
## Needs a window (the headless renderer draws nothing):
##   godot --path . --script res://tools/debug/chameleon_camo_check.gd -- <out_dir>

const VIEW := "docs/art/moba/chameleon_m/take-b/views/e.png"
const GROUND := "art/field/moba3d/arena/lane_grass.png"
const MAIN := "D:/dev/new-mech-rpg/" ## used when the files aren't inside this project
const SHADER := "res://scripts/moba3d/tilted_sprite_camo_3d.gdshader"
const TEXEL_M := 0.020
const CANVAS := 160
const FEET_EDGE := 141
const PITCH_DEG := 35.0
const SEEN := 0.08 * 1.7320508 ## RGB distance in 0..1 units
const CROP := Rect2i(280, 110, 400, 380)
const LENS := [Color("#ffd84a"), Color("#fff1a0"), Color("#fffbe6")]


func _initialize() -> void:
	_run()


func _image(rel: String) -> Image:
	var p := ProjectSettings.globalize_path("res://" + rel)
	if not FileAccess.file_exists(p):
		p = MAIN + rel
	var im := Image.load_from_file(p)
	assert(im != null, "missing " + p)
	return im


func _commonest(im: Image, n: int) -> Array:
	var count := {}
	for y in im.get_height():
		for x in im.get_width():
			var c := im.get_pixel(x, y)
			if c.a > 0.5:
				count[c] = count.get(c, 0) + 1
	var cols := count.keys()
	cols.sort_custom(func(a, b): return count[a] > count[b])
	return cols.slice(0, n)


func _dist(a: Color, b: Color) -> float:
	return Vector3(a.r - b.r, a.g - b.g, a.b - b.b).length()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var out_dir: String = args[0] if args.size() > 0 else OS.get_user_data_dir().path_join("camo_check")
	DirAccess.make_dir_recursive_absolute(out_dir)
	await process_frame # build the scene once the tree is running

	var world := Node3D.new()
	root.add_child(world)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(12, 12)
	ground.mesh = plane
	var gm := StandardMaterial3D.new()
	gm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	gm.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	gm.albedo_texture = ImageTexture.create_from_image(_image(GROUND))
	var reps := 12.0 / (32.0 * TEXEL_M) # a 32-texel tile at the sprite's own texel size (game scale not checked)
	gm.uv1_scale = Vector3(reps, reps, 1.0)
	ground.material_override = gm
	world.add_child(ground)

	var sprite := Sprite3D.new()
	sprite.texture = ImageTexture.create_from_image(_image(VIEW))
	sprite.pixel_size = TEXEL_M
	var lift := (FEET_EDGE - CANVAS / 2.0) * TEXEL_M
	sprite.position.y = lift
	var mat := ShaderMaterial.new()
	mat.shader = load(SHADER)
	mat.set_shader_parameter("tex", sprite.texture)
	mat.set_shader_parameter("lift", lift)
	mat.set_shader_parameter("camo_shimmer", 0.0)
	# The kit would sample the floor under the machine; here, the ground texture's three commonest colours.
	var floor_cols := _commonest(_image(GROUND), 3)
	for i in floor_cols.size():
		mat.set_shader_parameter("camo_floor_" + "abc"[i], floor_cols[i])
	print("floor colours: ", floor_cols.map(func(c: Color) -> String: return "#" + c.to_html(false)))
	sprite.material_override = mat
	world.add_child(sprite)

	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 3.2
	var pitch := deg_to_rad(PITCH_DEG)
	var aim := Vector3(0, 0.6, 0)
	world.add_child(cam)
	cam.look_at_from_position(aim + Vector3(0, sin(pitch), cos(pitch)) * 10.0, aim, Vector3.UP)
	cam.current = true

	var states := [
		["ground", {}, false],
		["normal", {"camo_hide": 0.0}, true],
		["halfway", {"camo_hide": 0.5}, true],
		["enemy_hidden", {"camo_hide": 1.0}, true],
		["enemy_tell", {"camo_hide": 1.0, "camo_tell": 1.0}, true],
		["ally", {"camo_hide": 1.0, "camo_ally_view": true}, true],
		["break_flash", {"camo_rim_flash": 1.0}, true],
	]
	var shots := {}
	for st in states:
		sprite.visible = st[2]
		mat.set_shader_parameter("camo_hide", 0.0)
		mat.set_shader_parameter("camo_tell", 0.0)
		mat.set_shader_parameter("camo_ally_view", false)
		mat.set_shader_parameter("camo_rim_flash", 0.0)
		for key in st[1]:
			mat.set_shader_parameter(key, st[1][key])
		for i in 4:
			await RenderingServer.frame_post_draw
		var im := root.get_texture().get_image().get_region(CROP)
		im.save_png(out_dir.path_join(String(st[0]) + ".png"))
		shots[st[0]] = im

	var g: Image = shots["ground"]
	var n: Image = shots["normal"]
	var body := 0
	var lens := 0
	var counts := {}
	var lens_kept := 0
	for key in ["normal", "halfway", "enemy_hidden", "enemy_tell", "ally"]:
		counts[key] = 0
	for y in CROP.size.y:
		for x in CROP.size.x:
			var gc := g.get_pixel(x, y)
			var nc := n.get_pixel(x, y)
			if _dist(nc, gc) < 0.02:
				continue
			body += 1
			for key in counts:
				if _dist((shots[key] as Image).get_pixel(x, y), gc) > SEEN:
					counts[key] += 1
			for lc in LENS:
				if _dist(nc, lc) < 0.04:
					lens += 1
					if _dist((shots["ally"] as Image).get_pixel(x, y), nc) < 0.02:
						lens_kept += 1
					break
	var share := {}
	for key in counts:
		share[key] = float(counts[key]) / max(body, 1)
	share["ally_lens_kept"] = float(lens_kept) / max(lens, 1)
	var targets := {"normal": [0.95, 1.0], "enemy_hidden": [0.0, 0.03], "enemy_tell": [0.08, 0.30],
			"ally": [0.45, 1.0], "ally_lens_kept": [1.0, 1.0]}
	var ok := body > 1000 and lens > 0 # an empty or eyeless view measures nothing, so it can't pass
	print("chameleon camo check: body %d screen px, lens %d px%s" % [body, lens, "" if ok else "  (too few to measure: FAIL)"])
	for key in share:
		var line := "  %-15s %5.1f%%" % [key, share[key] * 100.0]
		if targets.has(key):
			var pass_: bool = float(share[key]) >= targets[key][0] - 0.0001 and float(share[key]) <= targets[key][1] + 0.0001
			ok = ok and pass_
			line += "  target %d-%d%%  %s" % [roundi(targets[key][0] * 100), roundi(targets[key][1] * 100), "PASS" if pass_ else "FAIL"]
		print(line)
	print("RESULT ", "PASS" if ok else "FAIL")
	var f := FileAccess.open(out_dir.path_join("scores.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify({"share": share, "body_px": body, "lens_px": lens, "pass": ok}, "  "))
	f.close()
	quit(0 if ok else 1)
