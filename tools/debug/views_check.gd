extends SceneTree
## Multi-view machines (scripts/machines/machine_views.gd) and the view lab (scenes/view_lab.tscn).
##   Godot --headless --path . --script res://tools/debug/views_check.gd
## Windowed (no --headless) it also saves Codex's guide sheets, docs/team/view-guides/<machine>.png (the eight
## placeholder views at the exact slot size, in slot order), and stills of the lab at four camera angles.

const Views := preload("res://scripts/machines/machine_views.gd")
const Machines := preload("res://scripts/data/machines.gd")
const ViewSprite := preload("res://scripts/machines/view_sprite.gd")
var fails := 0


func _initialize() -> void:
	_run.call_deferred()


func _ok(what: String, good: bool) -> void:
	print("  %s  %s" % ["ok  " if good else "FAIL", what])
	if not good:
		fails += 1


func _bounds(polys: Array) -> Rect2:
	var r := Rect2()
	var first := true
	for p in polys:
		for v in p[0]:
			if first:
				r = Rect2(v, Vector2.ZERO)
				first = false
			else:
				r = r.expand(v)
	return r


func _run() -> void:
	print("which view")
	_ok("facing east, camera 0: side view e (%s)" % Views.dir_for(0, 0), Views.dir_for(0, 0) == "e")
	_ok("facing south toward the camera: s (%s)" % Views.dir_for(270, 0), Views.dir_for(270, 0) == "s")
	_ok("facing east, camera turned 90: now facing the camera, s (%s)" % Views.dir_for(0, 90), Views.dir_for(0, 90) == "s")
	_ok("facing west, camera turned 45: nw (%s)" % Views.dir_for(180, 45), Views.dir_for(180, 45) == "nw")
	_ok("22 degrees still e, 23 turns to ne (%s, %s)" % [Views.dir_for(22, 0), Views.dir_for(23, 0)], Views.dir_for(22, 0) == "e" and Views.dir_for(23, 0) == "ne")
	var all := {}
	for k in 360:
		all[Views.dir_for(k, 0)] = true
	_ok("a full turn shows all eight views (%d)" % all.size(), all.size() == 8)

	print("art and fallbacks")
	var only_e := func(p: String) -> bool: return p.ends_with("/e.png")
	_ok("w with only e drawn: e mirrored", Views.resolve("lion_m", "w", only_e) == {"path": Views.slot_path("lion_m", "e"), "flip": true})
	_ok("e with only e drawn: e as is", Views.resolve("lion_m", "e", only_e) == {"path": Views.slot_path("lion_m", "e"), "flip": false})
	_ok("s with only e drawn: placeholder (fronts can't be mirrored from sides)", Views.resolve("lion_m", "s", only_e).path == "")

	print("placeholders")
	for id in Machines.MACHINES:
		var shapes := {}
		var side_w := 0.0
		var front_w := 0.0
		var inside := true
		for k in 8:
			var polys := Views.placeholder_polys(id, k * 45.0)
			var b := _bounds(polys)
			shapes[str(polys.map(func(p: Array) -> String: return str(p[0])))] = true
			if Views.DIRS[k] == "e": side_w = b.size.x
			if Views.DIRS[k] == "s": front_w = b.size.x
			if not Rect2(Vector2.ZERO, Vector2(Views.VIEW_SIZE)).encloses(b):
				print("    %s %s spills out: %s" % [id, Views.DIRS[k], b])
				inside = false
		_ok("%s: eight different views (%d)" % [id, shapes.size()], shapes.size() == 8)
		_ok("%s: the side view is longer than the front (%d vs %d px)" % [id, side_w, front_w], side_w > front_w + 6 or Machines.MACHINES[id].animal in ["bird", "ape", "shoebill", "hippo"])   # wings and shoulders are wide
		_ok("%s: every view fits the %dx%d slot" % [id, Views.VIEW_SIZE.x, Views.VIEW_SIZE.y], inside)

	print("view lab: the camera turns, the machines turn with it")
	var lab: Node = load("res://scenes/view_lab.tscn").instantiate()
	root.add_child(lab)
	current_scene = lab
	await process_frame
	var lion: Node = lab.actors[0][0]   # the first machine on the floor
	var seen: Array = []
	var x_order: Array = []
	for step in 4:
		seen.append(lion.dir)
		x_order.append(lab.actors[0][0].position.x < lab.actors[1][0].position.x)
		await _shot(lab, step)
		lab.turn(2)   # 90 degrees
		await create_timer(1.0).timeout   # let the camera finish turning (time, not frames: frame speed varies)
	_ok("the first machine's view at camera 0, 90, 180, 270: %s" % str(seen), seen == ["e", "s", "w", "n"])
	_ok("the first two machines swap sides of the screen as the camera goes round (%s)" % str(x_order), x_order[0] != x_order[2])
	var has_art: bool = FileAccess.file_exists("res://art/machines/%s/views/views.json" % lion.machine_id)
	_ok("%s shows %s (%s)" % [lion.machine_id, "its imported art" if has_art else "its placeholder", lion.source],
		(lion.source in ["art", "mirror"]) if has_art else lion.source == "placeholder")

	if DisplayServer.get_name() != "headless":
		await _guides()
	print("views_check: %s" % ("PASS" if fails == 0 else "%d FAILED" % fails))
	quit(1 if fails else 0)


func _shot(lab: Node, step: int) -> void:
	if DisplayServer.get_name() == "headless":
		return
	for k in 4:
		await process_frame
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://docs/team/view-guides"))
	var img := root.get_texture().get_image()
	img.resize(320, 180, Image.INTERPOLATE_NEAREST)
	img.save_png("res://docs/team/view-guides/lab_camera_%03d.png" % (step * 90))


## One sheet per machine: the eight placeholder views in slot order (e ne n nw / w sw s se), each cell exactly
## VIEW_SIZE with a mark at the feet point, built cell by cell into one PNG at native pixels for Codex.
func _guides() -> void:
	current_scene.queue_free()
	await process_frame
	var W := Views.VIEW_SIZE.x
	var H := Views.VIEW_SIZE.y
	for id in Machines.MACHINES:
		var sheet := Image.create(W * 4, (H + 10) * 2, false, Image.FORMAT_RGBA8)
		sheet.fill(Color("16181b"))
		for k in 8:
			var stage := Node2D.new()
			root.add_child(stage)
			var bg := ColorRect.new()
			bg.size = Vector2(W, H)
			bg.color = Color("23262b")
			stage.add_child(bg)
			var s := ViewSprite.new()
			s.machine_id = id
			s.facing_deg = k * 45.0
			s.position = Vector2(Views.ANCHOR)
			stage.add_child(s)
			for f in 4:
				await process_frame
			var shot := root.get_texture().get_image()
			shot.resize(320, 180, Image.INTERPOLATE_NEAREST)
			var cell := shot.get_region(Rect2i(0, 0, W, H))
			cell.set_pixelv(Views.ANCHOR, Color("ffd400"))   # the feet point
			sheet.blit_rect(cell, Rect2i(0, 0, W, H), Vector2i((k % 4) * W, (k / 4) * (H + 10) + 10))
			stage.queue_free()
			await process_frame
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://docs/team/view-guides"))
		sheet.save_png("res://docs/team/view-guides/%s.png" % id)
