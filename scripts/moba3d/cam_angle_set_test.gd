class_name CamAngleSetTest
extends CamAngleTest
## Second camera-angle test for Mech-Zoids (Claude, 2026-11-04, game feel lane): the drone with a complete set of
## views drawn from the camera's angle (the sprite factory's 35-degree redraw) on the tilted quad
## (DirectionalSprite3D.tilt_to_camera), next to today's upright drone. Three spots, each as close as a drone can
## stand (its body radius): open floor at the blue spawn, in front of the blue tower, and inside the blue base wall.
## The HUD's own minion bar (match_hud.gd: 1.3 m up, 30 x 4 px) is drawn into every frame and the art's top is
## measured against it, so a collision is a number as well as a picture.
## Run arena_play with "-- --cam-angle-set-test --drone-views=<dir> --out=<dir>". A test only: the views are read
## from their PNGs at run time, the approved frames are only read, and nothing in the game changes.

const BARS := {"drone": [1.3, 30, 4], "rhino": [1.9, 64, 6], "ape": [1.9, 64, 6], "fennec": [1.52, 64, 6], "wolf": [1.71, 64, 6], "hippo": [1.9, 64, 6], "kangaroo": [1.71, 64, 6], "lobster": [1.9, 64, 6], "chameleon": [1.71, 64, 6]} ## the HUD's bar today (match_hud.gd): metres up (1.9 x size scale; the fennec is S, 0.8), px wide, px thick
const MIN_GAP_PX := 2.0 ## the raised bar must clear the art's top by this much at every view and screen height
const RADIUS := {"drone": 0.35, "rhino": 0.0, "ape": 0.8, "fennec": 0.64, "wolf": 0.72, "hippo": 0.8, "kangaroo": 0.45, "lobster": 0.8, "chameleon": 0.6} ## body radius: TrainingDummy.BODY_R; the rhino's is read from the player
const LOOK := {"drone": 0.5, "rhino": 1.0, "ape": 0.9, "fennec": 0.6, "wolf": 0.8, "hippo": 1.0, "kangaroo": 0.8, "lobster": 1.0, "chameleon": 0.8}
## A view set drawn on another canvas than the game's frames: [canvas, feet edge row]. The gorilla's 35-degree views
## are 160 with the lowest foot on row 130 (fleet lane, 2026-11-04); its game frames are 192 / 161.
const VIEW_CANVAS := {"ape": [160, 131], "fennec": [160, 141]} ## fennec take B: feet row 140 (fleet lane) ## crop centre, metres up

var who := "drone"
var bar_h := 1.3
var bar_w := 30
var bar_t := 4
var body_r := 0.35
var cell := CELL
var views_dir := ""
var views_have: Array[String] = []
var spot_p := {} ## spot name -> ground point
var spot_yaw := {} ## spot name -> camera yaw that puts the tower or wall behind the drone
var facing := Vector3(0, 0, 1)
var moving_now := false
var installed := false ## --drone-views=installed: the machine's own frames, tilted where their tilt_anims meta says
var bar_tilted := 1.3
var _player: Node3D
var _tops := {} ## texture instance id -> the top row of its drawing


func setup_set(arena_play: Node, output_dir: String, drone_views: String, machine := "drone") -> void:
	out = output_dir
	who = machine
	bar_h = BARS[who][0]
	bar_w = BARS[who][1]
	bar_t = BARS[who][2]
	bar_tilted = bar_h
	body_r = RADIUS[who] if RADIUS[who] > 0.0 else float(arena_play.player.call("body_radius"))
	if who != "drone":
		cell = Vector2i(320, 250)
	views_dir = drone_views
	DirAccess.make_dir_recursive_absolute(out)
	var arena: Node3D = arena_play.arena
	_player = arena_play.player
	cam = arena.get_node("Camera")
	_player.visible = false
	_player.process_mode = Node.PROCESS_MODE_DISABLED
	installed = drone_views == "installed"
	for v in DRAWN:
		if installed or FileAccess.file_exists(ProjectSettings.globalize_path(views_dir.path_join(v + ".png"))):
			views_have.append(v)
	var base: SpriteFrames = frames_of(KINDS[who])
	for tilt in [false, true]:
		var s := _stand(who, false)  # built upright, then the tilted one gets its frames and its mode
		var d := s.get_node("Sprite") as DirectionalSprite3D
		if installed:  # the frames as installed tilt themselves; the upright one is a copy without the meta
			if not tilt:
				var plain := base.duplicate(true) as SpriteFrames
				if plain.has_meta("tilt_anims"):
					plain.remove_meta("tilt_anims")
				d.sprite_frames = plain
			elif not _tilt_override().is_empty():  # frames packed without the meta: simulate it, tilted stands only
				var sim := base.duplicate(true) as SpriteFrames
				sim.set_meta("tilt_anims", _tilt_override())
				d.sprite_frames = sim
		elif tilt:
			d.sprite_frames = _set_frames(base)
			d.tilt_to_camera = true
			if VIEW_CANVAS.has(who):  # set before the stand enters the tree, so its _ready sizes it
				d.canvas_height = VIEW_CANVAS[who][0]
				d.feet_edge_row = VIEW_CANVAS[who][1]
		arena.add_child(s)
		s.visible = false
		stands.append(s)
		names.append(who + ("_tilted_set" if tilt else "_upright_today"))
	spot_p["floor"] = _player.global_position
	spot_yaw["floor"] = cam.yaw_degrees
	var tw := arena.get_node("Markers/BlueTower") as Node3D
	var tp := Vector3(tw.global_position.x, 0.0, tw.global_position.z)
	var to_spawn := Vector3(spot_p["floor"].x - tp.x, 0.0, spot_p["floor"].z - tp.z).normalized()
	spot_p["tower"] = tp + to_spawn * (float(tw.get_meta("radius", 1.4)) + body_r)
	spot_yaw["tower"] = _yaw_toward(tp - spot_p["tower"])
	process_priority = 100
	_run_set.call_deferred(arena)


## The approved idle per view, with the new drawing in place of it where the set has one.
func _set_frames(base: SpriteFrames) -> SpriteFrames:
	var sf := SpriteFrames.new()
	for v in DRAWN:
		var a := StringName("idle_" + v)
		sf.add_animation(a)
		sf.set_animation_loop(a, true)
		if v in views_have:
			var img := Image.load_from_file(ProjectSettings.globalize_path(views_dir.path_join(v + ".png")))
			sf.add_frame(a, ImageTexture.create_from_image(img))
		else:
			sf.set_animation_speed(a, base.get_animation_speed(a))
			for i in base.get_frame_count(a):
				sf.add_frame(a, base.get_frame_texture(a, i), base.get_frame_duration(a, i))
	return sf


## The chase camera's yaw that looks along dir (its yaw 0 looks toward -Z).
func _yaw_toward(dir: Vector3) -> float:
	return rad_to_deg(atan2(-dir.x, -dir.z))


func _process(_delta: float) -> void:
	for s in stands:
		if s.visible:
			(s.get_node("Sprite") as DirectionalSprite3D).show_facing(facing, cam.global_basis, moving_now)


## The facing that shows view v from this camera (sector 0 = n, away from it; 4 = s, toward it).
func _facing_for(v: String) -> Vector3:
	var b := cam.global_basis
	var fwd := Vector3(-b.z.x, 0.0, -b.z.z).normalized()
	var right := Vector3(b.x.x, 0.0, b.x.z).normalized()
	var a := DirectionalSprite3D.VIEWS.find(v) * PI / 4.0
	return fwd * cos(a) + right * sin(a)


func _go(spot: String, yaw: float) -> void:
	_player.global_position = spot_p[spot]
	for s in stands:
		s.global_position = spot_p[spot]
	cam.yaw_degrees = yaw
	cam.snap()


func _run_set(arena: Node3D) -> void:
	await _frames(6)
	_find_wall(arena)
	log_lines.append("machine %s, body radius %.2f m, bar %.2f m" % [who, body_r, bar_h])
	if installed:
		log_lines.append("installed tilt_anims: %s%s" % [(stands[1].get_node("Sprite") as DirectionalSprite3D).sprite_frames.get_meta("tilt_anims", "none"), " (SIMULATED by --tilt-anims; not in the packed .tres)" if not _tilt_override().is_empty() else ""])
	log_lines.append("views in the set: %s (others fall back on the approved view)" % [views_have])
	log_lines.append("spots: " + str(spot_p) + " yaw " + str(spot_yaw))
	_size_bar()
	var spots := ["floor", "floor", "tower", "wall"]
	var pick := [0, 1, 1, 1]
	var cols := ["floor_upright", "floor_tilted", "tower_tilted", "wall_tilted"]
	for v in DRAWN:  # the board: the camera holds still and the drone turns to each drawn view
		for c in cols.size():
			_go(spots[c], spot_yaw[spots[c]])
			_show_only(pick[c])
			facing = _facing_for(v)
			await _frames(4)
			var img := _grab()
			var gap := _bar_onto(img, stands[pick[c]], pick[c] == 1)
			_crop(img, _px(spot_p[spots[c]] + Vector3.UP * LOOK[who], img), cell).save_png(out.path_join("cell_%s_%s.png" % [v, cols[c]]))
			log_lines.append("%s %s: bar gap %.1f px (negative = bar on the art)" % [v, cols[c], gap])
	for c in cols.size():  # the clip: Q for a full turn, a pause, E for half a turn back, the drone facing still
		_go(spots[c], spot_yaw[spots[c]])
		_show_only(pick[c])
		facing = _facing_for("s")
		await _frames(3)
		var at := _px(spot_p[spots[c]] + Vector3.UP * LOOK[who], _grab())
		DirAccess.make_dir_recursive_absolute(out.path_join(cols[c]))
		var worst := INF
		var total := STILL + TURN_Q + PAUSE + TURN_E + PAUSE + (60 if installed else 0)
		for f in total:
			moving_now = f >= STILL + TURN_Q + PAUSE + TURN_E + PAUSE and f < STILL + TURN_Q + PAUSE + TURN_E + PAUSE + 30
			if f == STILL:
				_key(KEY_Q, true)
			elif f == STILL + TURN_Q:
				_key(KEY_Q, false)
			elif f == STILL + TURN_Q + PAUSE:
				_key(KEY_E, true)
			elif f == STILL + TURN_Q + PAUSE + TURN_E:
				_key(KEY_E, false)
			if f > STILL and f < STILL + TURN_Q:
				_key(KEY_Q, true)  # held: pressed again each frame, so a lost window focus can't release it early
			elif f > STILL + TURN_Q + PAUSE and f < STILL + TURN_Q + PAUSE + TURN_E:
				_key(KEY_E, true)
			await RenderingServer.frame_post_draw
			var img := _grab()
			worst = minf(worst, _bar_onto(img, stands[pick[c]], pick[c] == 1))
			_crop(img, at, CLIP).save_png(out.path_join(cols[c]).path_join("f%04d.png" % f))
		log_lines.append("clip %s: yaw at end %.1f, smallest bar gap %.1f px" % [cols[c], cam.yaw_degrees, worst])
	if installed:
		await _walk_feet(arena)
		await _actions_clip()
	var fa := FileAccess.open(out.path_join("log.txt"), FileAccess.WRITE)
	fa.store_string("\n".join(log_lines) + "\n")
	fa.close()
	print("cam_angle_set_test done: ", out)
	get_tree().quit()


## The base wall straight behind the blue core, found by a ray (the wall's inner face), and the drone's spot against it.
func _find_wall(arena: Node3D) -> void:
	var core := arena.get_node("Markers/BlueCore") as Node3D
	var cp := Vector3(core.global_position.x, 0.0, core.global_position.z)
	var away := Vector3(cp.x, 0.0, cp.z).normalized()  # from the map's middle out through the core: the back of the base
	var k: Dictionary = arena.get_script().get_script_constant_map()
	var face: float = k["BASE_R"] - k["WALL_THICK"] * 0.5
	var q := PhysicsRayQueryParameters3D.create(cp + away * 5.0 + Vector3.UP, cp + away * 30.0 + Vector3.UP)
	var hit := arena.get_world_3d().direct_space_state.intersect_ray(q)
	if not hit.is_empty():
		face = Vector3(hit.position.x - cp.x, 0.0, hit.position.z - cp.z).length()
		log_lines.append("base wall found by ray at %.2f m behind the core (%s)" % [face, hit.collider])
	else:
		log_lines.append("no ray hit; base wall face taken from BASE_R - WALL_THICK / 2 = %.2f m" % face)
	spot_p["wall"] = cp + away * (face - body_r)
	spot_yaw["wall"] = _yaw_toward(away)


## The top row of a frame's drawing, cached.
func _top_row(tex: Texture2D) -> int:
	var id := tex.get_instance_id()
	if not _tops.has(id):
		_tops[id] = tex.get_image().get_used_rect().position.y
	return _tops[id]


## The art's top and the bar, in image pixels, for a drone standing at its stand's spot now.
func _art_top_y(stand: Node3D, img_size: Vector2) -> float:
	var d := stand.get_node("Sprite") as DirectionalSprite3D
	var tex := d.sprite_frames.get_frame_texture(d.animation, d.frame)
	var length := (d.feet_edge_row - _top_row(tex)) * d.pixel_size
	var up := cam.global_basis.y if d.tilted_now() else Vector3.UP  # a tilted quad's up is the camera's up
	var k := img_size / get_viewport().get_visible_rect().size
	return (cam.unproject_position(stand.global_position + up * length) * k).y


func _bar_y(stand: Node3D, h: float, img_size: Vector2) -> Vector2:
	var k := img_size / get_viewport().get_visible_rect().size
	return cam.unproject_position(stand.global_position + Vector3.UP * h) * k


## Draws the HUD's minion bar into img (the raised one on a tilted drone, with today's height outlined in red) and
## returns the gap from the bar's bottom up to the art's top, in pixels.
func _bar_onto(img: Image, stand: Node3D, tilted: bool) -> float:
	var sz := Vector2(img.get_size())
	var h := bar_tilted if tilted else bar_h
	var sp := _bar_y(stand, h, sz)
	var r := Rect2i(int(sp.x) - bar_w / 2, int(sp.y), bar_w, bar_t)
	img.fill_rect(r.grow(1), Color(0.05, 0.05, 0.08))
	img.fill_rect(r, MatchTeams.COLOURS["blue"])
	if tilted and bar_tilted != bar_h:
		var o := _bar_y(stand, bar_h, sz)
		var ro := Rect2i(int(o.x) - bar_w / 2, int(o.y), bar_w, bar_t)
		for x in range(ro.position.x, ro.end.x):
			img.set_pixel(x, ro.position.y, Color.RED)
			img.set_pixel(x, ro.end.y - 1, Color.RED)
	return _art_top_y(stand, sz) - (sp.y + bar_t)


## How high the tilted drone's bar must sit so it clears the art at every view, with the drone anywhere from just
## under the camera to well up the screen. Measured with the camera's own projection, no rendering needed.
func _size_bar() -> void:
	var s := stands[1]
	var d := s.get_node("Sprite") as DirectionalSprite3D
	var sz := Vector2(get_viewport().get_texture().get_size())
	_go("floor", spot_yaw["floor"])
	var b := cam.global_basis
	var fwd := Vector3(-b.z.x, 0.0, -b.z.z).normalized()
	var worst_today := INF
	var h := bar_h
	while h < 3.0:
		var worst := INF
		for v in DRAWN:
			facing = _facing_for(v)
			d.show_facing(facing, cam.global_basis, false)
			for off in range(-4, 15):
				s.global_position = spot_p["floor"] + fwd * off
				var y := _bar_y(s, h, sz).y
				if y < 0.0 or y > sz.y:
					continue
				worst = minf(worst, _art_top_y(s, sz) - (y + bar_t))
		if is_equal_approx(h, bar_h):
			worst_today = worst
		if worst >= MIN_GAP_PX:
			break
		h += 0.05
	bar_tilted = snappedf(h, 0.05)
	var h_near := bar_h  # the same, but only from the player's own spot outward (none of it nearer the camera)
	while h_near < 3.0:
		var w2 := INF
		for v in DRAWN:
			facing = _facing_for(v)
			d.show_facing(facing, cam.global_basis, false)
			for off in range(0, 15):
				s.global_position = spot_p["floor"] + fwd * off
				w2 = minf(w2, _art_top_y(s, sz) - (_bar_y(s, h_near, sz).y + bar_t))
		if w2 >= MIN_GAP_PX:
			break
		h_near += 0.05
	log_lines.append("from the player's spot outward only, the tilted bar would need %.2f m" % snappedf(h_near, 0.05))
	var u := stands[0]
	var worst_up := INF
	for v in DRAWN:
		facing = _facing_for(v)
		(u.get_node("Sprite") as DirectionalSprite3D).show_facing(facing, cam.global_basis, false)
		for off in range(-4, 15):
			u.global_position = spot_p["floor"] + fwd * off
			var y := _bar_y(u, bar_h, sz).y
			if y >= 0.0 and y <= sz.y:
				worst_up = minf(worst_up, _art_top_y(u, sz) - (y + bar_t))
	s.global_position = spot_p["floor"]
	u.global_position = spot_p["floor"]
	log_lines.append("bar at %.2f m: upright clears by at least %.1f px; tilted %.1f px" % [bar_h, worst_up, worst_today])
	log_lines.append("tilted bar raised to %.2f m (clears by >= %.0f px at every view, drone 4 m nearer to 14 m farther)"
		% [bar_tilted, MIN_GAP_PX])
	log_lines.append("tilted leans back %.2f m at its tallest view (top %.2f m up the quad x sin 30)" % [
		_lean_back(d), _lean_back(d) / 0.5])


func _lean_back(d: DirectionalSprite3D) -> float:
	var longest := 0.0
	for v in DRAWN:
		var tex := d.sprite_frames.get_frame_texture(StringName("idle_" + v), 0)
		longest = maxf(longest, (d.feet_edge_row - _top_row(tex)) * d.pixel_size)
	return longest * sin(deg_to_rad(cam.pitch_degrees))


## Installed frames only: every walk frame at every drawn view on the open floor, the camera still, captured four ways
## (everything, everything but the machine, the machine alone, nothing). A pixel the machine draws when alone but
## doesn't change in the full scene is hidden by the floor, so a toe sinking below the pivot is a count, not a guess.
func _walk_feet(arena: Node3D) -> void:
	var s := stands[1]
	var d := s.get_node("Sprite") as DirectionalSprite3D
	_go("floor", spot_yaw["floor"])
	_show_only(1)
	DirAccess.make_dir_recursive_absolute(out.path_join("walk_feet"))
	var others: Array[Node3D] = []
	for n in arena.get_children():
		if n is Node3D and n != s and n != cam and (n as Node3D).visible:
			others.append(n)
	for v in DRAWN:
		facing = _facing_for(v)
		moving_now = true
		set_process(true)
		await _frames(3)
		set_process(false)  # no show_facing while the frames are stepped by hand
		d.pause()
		var feet := _px(spot_p["floor"], _grab())
		for i in d.sprite_frames.get_frame_count(d.animation):
			d.frame = i
			var shots: Array[Image] = []
			for mode in 4:  # 0 everything, 1 all but the machine, 2 the machine alone, 3 nothing
				s.visible = mode == 0 or mode == 2
				for o in others:
					o.visible = mode < 2
				await RenderingServer.frame_post_draw
				shots.append(_grab())
			s.visible = true
			for o in others:
				o.visible = true
			var drawn := 0
			var hidden := 0
			var lowest := -1
			var r := Rect2i(Vector2i(feet) - Vector2i(140, 60), Vector2i(280, 140))
			for y in range(r.position.y, r.end.y):
				for x in range(r.position.x, r.end.x):
					if shots[2].get_pixel(x, y) != shots[3].get_pixel(x, y):
						drawn += 1
						lowest = maxi(lowest, y)
						if shots[0].get_pixel(x, y) == shots[1].get_pixel(x, y):
							hidden += 1
			log_lines.append("walk %s frame %d: %d machine px near the feet, lowest %d px below the anchor, %d hidden by the floor" % [d.animation, i, drawn, lowest - int(feet.y), hidden])
			_crop(shots[0], feet + Vector2i(0, 5), Vector2i(280, 130)).save_png(out.path_join("walk_feet").path_join("%s_%d.png" % [v, i]))
	moving_now = false
	set_process(true)


## Installed frames only: each action beyond idle and walk (tilted or not), played once at every drawn view on the open
## floor, the camera still, for a clip (actions/f####.png). The log gives each action's first clip frame.
func _actions_clip() -> void:
	var s := stands[1]
	var d := s.get_node("Sprite") as DirectionalSprite3D
	_go("floor", spot_yaw["floor"])
	_show_only(1)
	var dir := out.path_join("actions")
	DirAccess.make_dir_recursive_absolute(dir)
	var at := _px(spot_p["floor"] + Vector3.UP * LOOK[who], _grab())
	var n := 0
	var acts: Array[String] = []  # every action drawn, tilted or not, so an idle-to-action pop shows too
	for name in d.sprite_frames.get_animation_names():
		var pre := String(name).rsplit("_", true, 1)[0]
		if pre != "idle" and pre != "walk" and not pre in acts:
			acts.append(pre)
	acts.sort()
	for a in acts:
		for v in DRAWN:
			var anim := StringName(String(a) + "_" + v)
			if not d.sprite_frames.has_animation(anim):
				continue
			facing = _facing_for(v)
			moving_now = false
			d.stop_action()
			await _frames(6)
			var idle_from := n  # 6 idle frames captured first, same camera, so the idle-to-action switch is in the clip
			for f in 6:
				await RenderingServer.frame_post_draw
				_crop(_grab(), at, CLIP).save_png(dir.path_join("f%04d.png" % n))
				n += 1
			d.play_action(String(a))
			var played := d.animation
			var count := d.sprite_frames.get_frame_count(anim)
			var len_f := int(ceil(count / d.sprite_frames.get_animation_speed(anim) * 30.0)) + 12
			var act_from := n
			var back := -1  # first captured frame after the sprite left the action
			var back_to := "none"
			for f in len_f:
				if f == len_f - 12:
					d.stop_action()  # the kit ends an ability this way; the sprite has no return to idle of its own
				await RenderingServer.frame_post_draw
				if back < 0 and d.animation != played:
					back = n
					back_to = String(d.animation)
				_crop(_grab(), at, CLIP).save_png(dir.path_join("f%04d.png" % n))
				n += 1
			log_lines.append("action %s at %s: clip frames %d to %d, %d drawn frames, playing %s; idle from %d, action from %d, back to %s at %d" % [a, v, idle_from, n - 1, count, played, idle_from, act_from, back_to, back])
	d.stop_action()


## --tilt-anims=idle,walk on the command line: a simulated tilt_anims meta on the installed frames, tilted stands only,
## for frames packed without it. The log says when it is in use.
func _tilt_override() -> Array:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--tilt-anims="):
			return Array(a.trim_prefix("--tilt-anims=").split(","))
	return []

