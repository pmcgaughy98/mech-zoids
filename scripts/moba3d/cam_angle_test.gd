class_name CamAngleTest
extends Node
## Camera-angle test for Mech-Zoids (Claude, 2026-11-04, game feel lane). Preston: "lets try keeping 2D sprites but
## with that" (views drawn from the camera's angle, so the machines stop reading as paper from above).
## Run arena_play with "-- --cam-angle-test --out=<dir>". No match starts. Four stand-ins take turns on the player's
## spot: the drone and the rhino, each as today's upright billboard (approved views) and as the tilted quad
## (DirectionalSprite3D.tilt_to_camera) showing the sprite factory's views drawn from 30 degrees (views_cam30).
## Views with no cam30 drawing show the approved view on the tilted quad, which is the case the test asks about.
## 1. Board: the chase camera stops at each drawn view (s, se, e, ne, n) and a crop round each stand-in is saved.
## 2. Clip: per stand-in, Q is held for a full turn and E for half a turn back (real key events), frames saved.
## A test only: the cam30 PNGs live in docs/ and are read at run time; the approved frames are only read.

const FACING := Vector3(0, 0, -1) ## every stand-in faces down the lane
const DRAWN: Array[String] = ["s", "se", "e", "ne", "n"]
const CAM30_DIR := {
	"drone": "res://docs/art/moba/minion_s/take-a/views_cam30/",
	"rhino": "res://docs/art/moba/rhino_l/take-a/views_cam30/",
}
const CAM30_VIEWS := {"drone": ["s", "se"], "rhino": ["s", "se", "ne", "n"]} ## the rhino's e failed, so it is left out
const KINDS := {
	"drone": {"frames": "res://art/machines/minion/minion_blue_frames.tres", "canvas": 96, "feet": 88, "size": "S"},
	"rhino": {"frames": "res://art/machines/rhino/rhino_frames.tres", "canvas": 192, "feet": 161, "size": "L"},
	"ape": {"frames": "res://art/machines/ape/ape_frames.tres", "canvas": 192, "feet": 161, "size": "L"},
	"fennec": {"frames": "res://art/machines/fennec/fennec_frames.tres", "canvas": 192, "feet": 161, "size": "S"},
	"wolf": {"views": "res://docs/art/moba/wolf_m/take-b/fixed", "canvas": 192, "feet": 161, "size": "M"}, ## no installed frames yet: the approved take B views
	"hippo": {"frames": "res://art/machines/hippo/hippo_frames.tres", "canvas": 192, "feet": 161, "size": "L"}, ## the game frames (pack_hippo_3d.py, the shade1 views Preston kept), 2026-11-05
	"lobster": {"views": "res://docs/art/moba/lobster_l/take-g/views", "canvas": 192, "feet": 161, "size": "L"}, ## no installed frames yet: the approved take G views (2026-11-05)
	"chameleon": {"views": "res://docs/art/moba/chameleon_m/take-b/views", "canvas": 160, "feet": 141, "size": "M"}, ## no kit yet: the approved take B views (2026-11-06)
	"kangaroo": {"views": "res://docs/art/moba/kangaroo_m/take-a/fixed", "canvas": 160, "feet": 141, "size": "M"}, ## no installed frames yet: the approved take A views (fixed, 2026-11-03)
}
const CELL := Vector2i(256, 200) ## board crop, game pixels
const CLIP := Vector2i(640, 360) ## clip crop, game pixels
const STILL := 30 ## frames held before turning
const TURN_Q := 120 ## 360 degrees at the camera's 90 degrees a second, 30 fps
const PAUSE := 15
const TURN_E := 60

var out := ""
var cam: Camera3D
var spot := Vector3.ZERO
var stands: Array[Node3D] = []
var names: Array[String] = []
var log_lines: PackedStringArray = []


func setup(arena_play: Node, output_dir: String) -> void:
	out = output_dir
	DirAccess.make_dir_recursive_absolute(out)
	var arena: Node3D = arena_play.arena
	var player: Node3D = arena_play.player
	cam = arena.get_node("Camera")
	spot = player.global_position
	player.visible = false
	player.process_mode = Node.PROCESS_MODE_DISABLED
	cam.process_mode = Node.PROCESS_MODE_ALWAYS
	for who in ["drone", "rhino"]:
		for tilt in [false, true]:
			var s := _stand(who, tilt)
			arena.add_child(s)
			s.global_position = spot
			s.visible = false
			stands.append(s)
			names.append(who + ("_tilted_cam30" if tilt else "_upright_today"))
	process_priority = 100  # after the camera has snapped, so the view matches this frame's camera
	_run.call_deferred()


func _stand(who: String, tilt: bool) -> Node3D:
	var k: Dictionary = KINDS[who]
	var base: SpriteFrames = frames_of(k)
	var root := Node3D.new()
	var d := DirectionalSprite3D.new()
	d.name = "Sprite"
	d.sprite_frames = _cam30_frames(base, who) if tilt else base
	d.canvas_height = k["canvas"]
	d.feet_edge_row = k["feet"]
	d.size_class = k["size"]
	d.tilt_to_camera = tilt
	root.add_child(d)
	var shadow := MeshInstance3D.new()  # the same soft contact shadow under both, so the feet can be judged
	var m := CylinderMesh.new()
	var r := 0.55 * d.size_scale()
	m.top_radius = r
	m.bottom_radius = r
	m.height = 0.01
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = Color(0, 0, 0, 0.35)
	m.material = mat
	shadow.mesh = m
	shadow.position.y = 0.01
	root.add_child(shadow)
	return root


## A kind's frames: its installed SpriteFrames, or one idle frame per drawn view from a folder when none is installed.
static func frames_of(k: Dictionary) -> SpriteFrames:
	if k.has("frames"):
		return load(k["frames"])
	var sf := SpriteFrames.new()
	for v in DRAWN:
		var a := StringName("idle_" + v)
		sf.add_animation(a)
		sf.set_animation_loop(a, true)
		var img := Image.load_from_file(ProjectSettings.globalize_path(String(k["views"]).path_join(v + ".png")))
		sf.add_frame(a, ImageTexture.create_from_image(img))
	return sf


## The approved idle per view, with the cam30 drawing in place of it where one exists.
func _cam30_frames(base: SpriteFrames, who: String) -> SpriteFrames:
	var sf := SpriteFrames.new()
	for v in DRAWN:
		var a := StringName("idle_" + v)
		sf.add_animation(a)
		sf.set_animation_loop(a, true)
		if v in CAM30_VIEWS[who]:
			var img := Image.load_from_file(ProjectSettings.globalize_path(CAM30_DIR[who] + v + ".png"))
			sf.add_frame(a, ImageTexture.create_from_image(img))
		else:
			sf.set_animation_speed(a, base.get_animation_speed(a))
			for i in base.get_frame_count(a):
				sf.add_frame(a, base.get_frame_texture(a, i), base.get_frame_duration(a, i))
	return sf


func _process(_delta: float) -> void:
	for s in stands:
		if s.visible:
			(s.get_node("Sprite") as DirectionalSprite3D).show_facing(FACING, cam.global_basis, false)


func _run() -> void:
	await _frames(10)
	var yaw := {}
	for i in 8:  # which camera yaw shows which view
		var y := i * 45.0
		cam.yaw_degrees = y
		cam.snap()
		var sec := DirectionalSprite3D.sector(FACING, cam.global_basis)
		if (sec >= 0 or sec == -4) and not yaw.has(DirectionalSprite3D.VIEWS[absi(sec)]):
			yaw[DirectionalSprite3D.VIEWS[absi(sec)]] = y
	log_lines.append("yaw per view: " + str(yaw))
	for v in DRAWN:
		for i in stands.size():
			_show_only(i)
			cam.yaw_degrees = yaw[v]
			await _frames(4)
			var spr := stands[i].get_node("Sprite") as DirectionalSprite3D
			var img := _grab()
			var at := _px(spot + Vector3.UP * (0.45 if names[i].begins_with("drone") else 0.9), img)
			_crop(img, at, CELL).save_png(out.path_join("cell_%s_%s.png" % [v, names[i]]))
			if v == "s" or v == "se":
				img.save_png(out.path_join("full_%s_%s.png" % [v, names[i]]))
			log_lines.append("%s %s: view %s anim %s billboard %d node y %.3f offset y %.1f" % [v, names[i], spr.view,
				spr.animation, spr.billboard, spr.position.y, spr.offset.y])
	for i in stands.size():  # the clip: Q for a full turn, a pause, E for half a turn back
		_show_only(i)
		cam.yaw_degrees = yaw["s"]
		await _frames(3)
		var at := _px(spot + Vector3.UP * 0.6, _grab())
		DirAccess.make_dir_recursive_absolute(out.path_join(names[i]))
		var total := STILL + TURN_Q + PAUSE + TURN_E + PAUSE
		for f in total:
			if f == STILL:
				_key(KEY_Q, true)
			elif f == STILL + TURN_Q:
				_key(KEY_Q, false)
			elif f == STILL + TURN_Q + PAUSE:
				_key(KEY_E, true)
			elif f == STILL + TURN_Q + PAUSE + TURN_E:
				_key(KEY_E, false)
			await RenderingServer.frame_post_draw
			_crop(_grab(), at, CLIP).save_png(out.path_join(names[i]).path_join("f%04d.png" % f))
			if f == STILL + TURN_Q - 1:
				log_lines.append("%s: yaw after Q %.1f (start %.1f)" % [names[i], cam.yaw_degrees, yaw["s"]])
		log_lines.append("%s: yaw at end %.1f" % [names[i], cam.yaw_degrees])
	var fa := FileAccess.open(out.path_join("log.txt"), FileAccess.WRITE)
	fa.store_string("\n".join(log_lines) + "\n")
	fa.close()
	print("cam_angle_test done: ", out)
	get_tree().quit()


func _show_only(i: int) -> void:
	for j in stands.size():
		stands[j].visible = j == i


func _frames(n: int) -> void:
	for k in n:
		await RenderingServer.frame_post_draw


func _grab() -> Image:
	return get_viewport().get_texture().get_image()


## A world point in the grabbed image's pixels (the 3D renders at the window size; unproject uses the 2D view size).
func _px(p: Vector3, img: Image) -> Vector2i:
	var k := Vector2(img.get_size()) / get_viewport().get_visible_rect().size
	return Vector2i(cam.unproject_position(p) * k)


func _crop(img: Image, centre: Vector2i, size: Vector2i) -> Image:
	var r := Rect2i(centre - size / 2, size)
	r.position = r.position.clamp(Vector2i.ZERO, img.get_size() - size)
	return img.get_region(r)


func _key(code: Key, down: bool) -> void:
	var e := InputEventKey.new()
	e.physical_keycode = code
	e.keycode = code
	e.pressed = down
	Input.parse_input_event(e)
