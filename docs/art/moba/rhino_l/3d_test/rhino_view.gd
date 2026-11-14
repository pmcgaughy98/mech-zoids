extends SceneTree
## Rhino 3D test shots (Claude, 3D test lane, 2026-11-04). Not part of the game; nothing here is loaded by it.
## Copied from minion_s/take-a/3d_test/drone_view.gd. Renders the rhino the way the arena would show it: the arena's sun, ambient, sky and fog (nature theme),
## the chase camera's numbers (fov 60, 6.5 m back, 30 degrees pitch, aimed 1.2 m up), a 1280 x 720 frame (the
## game's window), nearest filtering. The rhino stands where the chased player would stand.
## Subjects: the game's billboard (the approved view at pixel_size 0.020, feet row 161) and the part-built voxel rhino
## (rhino_parts.glb, unlit like the billboards), loaded at runtime through GLTFDocument (docs/ is .gdignore'd).
## Run (needs a window, not headless):
##   Godot --path D:/dev/new-mech-rpg --script res://docs/art/moba/rhino_l/3d_test/rhino_view.gd

const BASE := "res://docs/art/moba/rhino_l/take-a/"
const HERE := "res://docs/art/moba/rhino_l/3d_test/"
const OUT := HERE + "godot_shots/"
const NAMES := ["s", "se", "e", "ne", "n"]
const YAWS := [0.0, 45.0, 90.0, 135.0, 180.0]
const TEXEL := 0.020

var vp: SubViewport
var cam: Camera3D
var holder: Node3D
var shots: Array = []
var idx := 0
var wait := 0
var lines := PackedStringArray()


func _initialize() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	vp = SubViewport.new()
	vp.size = Vector2i(1280, 720)
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.own_world_3d = true
	root.add_child(vp)
	_world()
	shots.append({"kind": "empty", "name": "frame", "yaw": 0.0, "t": -1.0})
	for kind in ["sprite", "parts"]:
		for k in 5:
			shots.append({"kind": kind, "name": NAMES[k], "yaw": YAWS[k], "t": -1.0})
	_setup(shots[0])


func _process(_delta: float) -> bool:
	wait += 1
	if wait < 5:
		return false
	_capture(shots[idx])
	idx += 1
	if idx >= shots.size():
		var f := FileAccess.open(OUT + "godot_log.txt", FileAccess.WRITE)
		f.store_string("\n".join(lines) + "\n")
		print("\n".join(lines))
		return true
	_setup(shots[idx])
	wait = 0
	return false


func _world() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var psm := ProceduralSkyMaterial.new()
	psm.sky_top_color = Color(0.26, 0.48, 0.85)
	psm.sky_horizon_color = Color(0.78, 0.86, 0.93)
	psm.ground_horizon_color = Color(0.78, 0.86, 0.93)
	psm.ground_bottom_color = Color(0.2, 0.32, 0.18)
	sky.sky_material = psm
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.66, 0.72, 0.84)
	env.ambient_light_energy = 0.85
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.fog_enabled = true
	env.fog_light_color = Color(0.72, 0.8, 0.88)
	env.fog_density = 0.004
	env.fog_sky_affect = 0.5
	var we := WorldEnvironment.new()
	we.environment = env
	vp.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.transform = str_to_var("Transform3D(0.866, 0, -0.5, -0.383, 0.643, -0.663, 0.321, 0.766, 0.557, 0, 10, 0)")
	sun.light_color = Color(1.0, 0.93, 0.8)
	sun.light_energy = 1.15
	sun.shadow_enabled = true
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	sun.directional_shadow_max_distance = 48.0
	sun.shadow_bias = 0.04
	sun.shadow_normal_bias = 1.2
	sun.light_angular_distance = 0.0
	vp.add_child(sun)
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(60, 60)
	ground.mesh = pm
	var gm := StandardMaterial3D.new()
	gm.albedo_color = Color(0.4, 0.56, 0.3)
	gm.roughness = 1.0
	ground.material_override = gm
	vp.add_child(ground)
	cam = Camera3D.new()
	cam.fov = 60.0
	cam.far = 200.0
	vp.add_child(cam)
	var focus := Vector3(0, 1.2, 0)
	var pitch := deg_to_rad(30.0)
	var at := focus + Vector3(0, 0, 1) * 6.5 * cos(pitch) + Vector3.UP * 6.5 * sin(pitch)
	cam.transform = Transform3D(Basis.looking_at(focus - at, Vector3.UP), at)
	cam.current = true
	holder = Node3D.new()
	vp.add_child(holder)
	lines.append("camera at %s, fov 60, looking at %s" % [cam.position, focus])


func _load_glb(file: String) -> Node3D:
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	var err := doc.append_from_file(ProjectSettings.globalize_path(HERE + file), st)
	if err != OK:
		lines.append("LOAD FAILED %s err %d" % [file, err])
		return Node3D.new()
	return doc.generate_scene(st) as Node3D


func _meshes(n: Node, out: Array) -> Array:
	if n is MeshInstance3D:
		out.append(n)
	for c in n.get_children():
		_meshes(c, out)
	return out


func _bounds(n: Node3D) -> AABB:
	var box := AABB()
	var first := true
	for mi in _meshes(n, []):
		var b: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box


func _setup(s: Dictionary) -> void:
	for c in holder.get_children():
		c.free()
	var kind: String = s.kind
	if kind == "empty":
		return
	if kind == "sprite":
		var sp := Sprite3D.new()
		var img := Image.load_from_file(ProjectSettings.globalize_path(BASE + "views/" + s.name + ".png"))
		sp.texture = ImageTexture.create_from_image(img)
		sp.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
		sp.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		sp.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		sp.shaded = false
		sp.pixel_size = TEXEL
		sp.position.y = (161 - 96) * TEXEL
		holder.add_child(sp)
		return
	var m := _load_glb("rhino_parts.glb")
	holder.add_child(m)
	for mi in _meshes(m, []):
		var src: Material = (mi as MeshInstance3D).mesh.surface_get_material(0)
		var mat := (src as BaseMaterial3D).duplicate() as BaseMaterial3D
		mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		(mi as MeshInstance3D).set_surface_override_material(0, mat)
	m.rotation_degrees.y = s.yaw
	if idx == 6:
		var box := _bounds(m)
		lines.append("rhino model bounds %s size %s" % [box.position, box.size])


func _capture(s: Dictionary) -> void:
	var img := vp.get_texture().get_image()
	var c := cam.unproject_position(Vector3(0, 0.68, 0))
	var r := Rect2i(int(c.x) - 128, int(c.y) - 100, 256, 200)
	img.get_region(r).save_png(OUT + "%s_%s.png" % [s.kind, s.name])
	if idx == 1:
		img.save_png(OUT + "full_frame_sprite_s.png")
		var top := cam.unproject_position(Vector3(0, 1.36, 0))
		var bot := cam.unproject_position(Vector3(0, 0.0, 0))
		lines.append("a 1.36 m upright span covers %.1f px on screen at 1280x720 (%.2f px per texel)" % [bot.y - top.y, (bot.y - top.y) / 68.0])
	if idx == 6:
		img.save_png(OUT + "full_frame_parts_s.png")
