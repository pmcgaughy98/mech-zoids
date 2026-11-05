extends SceneTree
## Frames of a side pit being taken, in a running arena_play. Map design lane, 2026-11-05. Needs a window and no
## other Godot: Godot --fixed-fps 60 --path . -s res://tools/map/pit_shot.gd -- <out.png>
## Saves two 1280 x 720 frames stacked: the player standing in the other team's pit with the fill held at 60%
## (ring, HUD marker and its fill line), then a moment after the take (flash fading, ring and light in the owner's
## colour, the feed line). Those states are set for the picture only. Edits nothing.


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var out: String = args[0] if args.size() > 0 else OS.get_user_data_dir() + "/pit_shot.png"
	var play: Node = load("res://scenes/moba3d/arena_play.tscn").instantiate()
	root.add_child(play)
	for i in 2:
		await process_frame
	var d = play.director
	for i in 600:
		if d.ready_to_play:
			break
		await physics_frame
	var p = play.player
	var pit: ArenaPit = null
	for n in get_nodes_in_group("arena_pits"):
		if n.home_team != p.team:
			pit = n
	if pit == null:
		print("pit_shot: no pit found")
		quit(1)
		return
	pit.set_physics_process(false)
	p.global_position = pit.global_position + Vector3(0, 0, 1.5)
	for i in 50:
		await physics_frame
	pit.capturing = p.team
	pit.progress = 0.6
	pit._t = 0.1
	pit._show()
	await process_frame
	var a := await _grab()
	pit._take(p.team)
	for i in 9:
		pit._physics_process(1.0 / 60.0)
		await physics_frame
	var b := await _grab()
	print("pit_shot: owner=", pit.owner_team, " locked=", snappedf(pit.locked_left, 0.1), " feed=", play.hud.feed_lines())

	var sheet := Image.create(1280, 1440, false, Image.FORMAT_RGB8)
	sheet.blit_rect(a, Rect2i(0, 0, 1280, 720), Vector2i.ZERO)
	sheet.blit_rect(b, Rect2i(0, 0, 1280, 720), Vector2i(0, 720))
	sheet.save_png(out)
	print("pit_shot: saved ", out)
	quit(0)


func _grab() -> Image:
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	if img.get_size() != Vector2i(1280, 720):
		img.resize(1280, 720, Image.INTERPOLATE_NEAREST)
	return img
