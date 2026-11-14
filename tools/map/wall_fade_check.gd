extends SceneTree
## Wall fade check. Map design lane, 2026-11-04. Needs a window, since the headless renderer draws nothing:
## Godot --fixed-fps 60 --path . -s res://tools/map/wall_fade_check.gd
## Stands the rhino 1 m from a lane wall in the arena blockout and turns the chase camera so it looks at the
## machine through that wall. Then it renders twice:
## - with machine_pos published by the player script (fade on);
## - with publishing off and machine_pos parked far away (fade off).
## Passes when the pixels round the machine change a lot between the two renders and a patch of the same wall
## 2.5 m away does not. That proves wall_fade.gdshader reads game feel's machine_pos and fades only round the
## machine. It saves no images.

const SCENE := "res://scenes/moba3d/arena_blockout.tscn"
const SPOT := Vector3(6.0, 0, 44) ## east side of the lane, 1 m from the wall face at x = 7
const AWAY := Vector3(0, -1000, 0)

var fails := 0


func _initialize() -> void:
	var arena: Node3D = load(SCENE).instantiate()
	root.add_child(arena)
	await process_frame
	var player = arena.get_node("Player")
	var cam = arena.get_node("Camera")
	# The tower's range ring reads machine_pos too (it shows as the player comes near), so it would count as a
	# change. This check is about the walls: the dressing (rings, crystals, bushes, banners) is hidden throughout.
	arena.get_node("Built/Dressing").visible = false
	player.global_position = SPOT
	for yaw in [90.0, -90.0]:
		cam.yaw_degrees = yaw
		cam.snap()
		if cam.global_position.x > 8.5:
			break
	print("  camera at %s, machine at %s" % [cam.global_position, SPOT])
	_ok(cam.global_position.x > 8.5, "the camera stands behind the wall (x > 8.5)")
	for i in 15:
		await process_frame # the player script eases machine_hidden up over 0.15 s once the wall cuts its view
	_ok(player.machine_hidden > 0.99, "the player script reports the machine hidden behind the wall (machine_hidden %.2f)" % player.machine_hidden)
	var on: Image = await _grab()
	player.publish_machine_pos = false # from here this check writes both globals itself
	RenderingServer.global_shader_parameter_set("machine_hidden", 1.0)
	RenderingServer.global_shader_parameter_set("machine_pos", SPOT)
	var direct: Image = await _grab() # set here, not by the player script: tells a shader fault from a publish fault
	RenderingServer.global_shader_parameter_set("machine_pos", AWAY)
	var off: Image = await _grab()
	var built: Node3D = arena.get_node("Built")
	built.visible = false
	var bare: Image = await _grab() # walls hidden: proves the capture and the box both work
	built.visible = true
	var mat_kind := "none"
	for n in built.get_children():
		if n is MeshInstance3D and n.mesh is BoxMesh:
			mat_kind = n.mesh.material.get_class()
			break
	print("  frame %d x %d, wall material %s" % [on.get_width(), on.get_height(), mat_kind])
	# unproject_position answers in the 320 x 180 base viewport; the captured frame is the window's size
	var to_px := Vector2(on.get_size()) / root.get_visible_rect().size
	var body: Vector2 = cam.unproject_position(SPOT + Vector3(0, 1, 0)) * to_px
	var wall: Vector2 = cam.unproject_position(Vector3(8.2, 2.0, SPOT.z + 2.5)) * to_px
	print("  machine on screen at %s, mean colour there: fade on %s, fade off %s, no walls %s" % [body, _mean(on, body, 40), _mean(off, body, 40), _mean(bare, body, 40)])
	_ok(_diff(bare, off, body, 40) > 0.3, "sanity: hiding the walls changes the pixels round the machine")
	var near_direct := _diff(direct, off, body, 40)
	var near := _diff(on, off, body, 40)
	var far := _diff(on, off, wall, 16)
	_ok(near_direct > 0.3, "machine_pos set by this check: %.0f%% of pixels round the machine change" % (near_direct * 100.0))
	_ok(near > 0.3, "machine_pos published by the player script: %.0f%% change" % (near * 100.0))
	_ok(far < 0.02, "a patch of the same wall 2.5 m away changes %.1f%%" % (far * 100.0))
	# The other way round: camera on the lane side, the same wall 1 m beyond the machine. Nothing should fade,
	# not even the wall beside and above the body (game feel saw a dither patch there, 2026-11-04).
	var against := Vector3(6.6, 0, 44) # feet 0.4 m from the wall face: pressed against it
	player.global_position = against
	cam.yaw_degrees = -cam.yaw_degrees
	cam.snap()
	_ok(cam.global_position.x < 5.0, "camera turned round to the lane side, the wall beyond the machine")
	player.visible = false # only the walls can change now; the sprite's idle animation would add its own pixels
	var beyond: float = await _beyond(cam, built, against, to_px, 0.6, 0.4) # the shader's defaults
	_ok(beyond < 0.0001, "a wall just beyond the machine stays solid: %.2f%% of pixels round it change" % (beyond * 100.0))
	# Game feel's frame, 2.8 s into the arena_play demo: the rhino against the plaza ring, which curves toward the
	# camera beside it. The old ease (eased right up to the body) left a dither patch on the ring there.
	var ring := Vector3(-10.8, 0, -5.7)
	player.global_position = ring
	cam.yaw_degrees = 0.0
	cam.snap()
	var ring_old: float = await _beyond(cam, built, ring, to_px, 0.0, 1.0, 220) # wide: the patch sat about 1.8 m to the side
	var ring_new: float = await _beyond(cam, built, ring, to_px, 0.6, 0.4, 220)
	_ok(ring_new <= ring_old, "plaza ring, cone alone (machine_hidden held at 1): the old ease cut %.2f%% of the pixels round the machine, the new one %.2f%%" % [ring_old * 100.0, ring_new * 100.0])
	# Now with game feel's gate: the player script finds the machine in plain view and closes the cut altogether.
	player.publish_machine_pos = true
	for i in 15:
		await process_frame
	var gated_on: Image = await _grab()
	var seen_hidden: float = player.machine_hidden
	player.publish_machine_pos = false
	RenderingServer.global_shader_parameter_set("machine_pos", AWAY)
	var gated_off: Image = await _grab()
	player.visible = true
	var gated := _diff(gated_on, gated_off, cam.unproject_position(ring + Vector3(0, 1, 0)) * to_px, 220)
	_ok(seen_hidden < 0.01 and gated < 0.0001, "plaza ring with the gate: machine_hidden %.2f in plain view, %.2f%% of the pixels round the machine cut" % [seen_hidden, gated * 100.0])
	print("wall_fade_check: %d failed" % fails)
	quit(1 if fails > 0 else 0)


func _beyond(cam, built: Node3D, at: Vector3, to_px: Vector2, depth: float, ramp: float, half := 80) -> float:
	for mi in built.find_children("*", "MeshInstance3D", true, false):
		for i in mi.mesh.get_surface_count(): # the foundry towers' bodies are ArrayMeshes with two surfaces
			var m: Material = mi.get_active_material(i)
			if m is ShaderMaterial:
				m.set_shader_parameter("body_depth", depth)
				m.set_shader_parameter("body_ramp", ramp)
	RenderingServer.global_shader_parameter_set("machine_hidden", 1.0) # the cone alone, gate held open
	RenderingServer.global_shader_parameter_set("machine_pos", at)
	var a: Image = await _grab()
	RenderingServer.global_shader_parameter_set("machine_pos", AWAY)
	var b: Image = await _grab()
	return _diff(a, b, cam.unproject_position(at + Vector3(0, 1, 0)) * to_px, half)


func _grab() -> Image:
	for i in 4:
		await process_frame
	await RenderingServer.frame_post_draw
	return root.get_texture().get_image()


func _diff(a: Image, b: Image, c: Vector2, half: int) -> float:
	var changed := 0
	var total := 0
	for y in range(int(c.y) - half, int(c.y) + half):
		for x in range(int(c.x) - half, int(c.x) + half):
			if x < 0 or y < 0 or x >= a.get_width() or y >= a.get_height():
				continue
			total += 1
			var d := a.get_pixel(x, y) - b.get_pixel(x, y)
			if absf(d.r) + absf(d.g) + absf(d.b) > 0.06:
				changed += 1
	return float(changed) / maxi(total, 1)


func _mean(img: Image, c: Vector2, half: int) -> String:
	var sum := Color(0, 0, 0, 0)
	var n := 0
	for y in range(int(c.y) - half, int(c.y) + half): # every pixel: a stride of 4 would land on one dither cell
		for x in range(int(c.x) - half, int(c.x) + half):
			if x >= 0 and y >= 0 and x < img.get_width() and y < img.get_height():
				sum += img.get_pixel(x, y)
				n += 1
	if n == 0:
		return "off screen"
	return "(%.2f %.2f %.2f)" % [sum.r / n, sum.g / n, sum.b / n]


func _ok(cond: bool, what: String) -> void:
	if cond:
		print("  ok   ", what)
	else:
		fails += 1
		print("  FAIL ", what)
