extends SceneTree
## Looks at game feel's playable arena from the chase camera. Map design lane, 2026-11-04. Needs a window.
## Run it twice; the second run adds its shot to the sheet the first one saved:
##   Godot --fixed-fps 60 --path . -s res://tools/map/arena_play_look.gd -- --demo
##   Godot --fixed-fps 60 --path . -s res://tools/map/arena_play_look.gd
## With --demo it plays game feel's scripted walk-through (real kit calls, real camera) and grabs it at 2.8 s and
## 3.6 s (rhino against the plaza wall, where game feel saw a dither patch) and at 10 s. The demo quits the game
## at its end, so the edge shot is a run of its own: the machine 1.5 m from the east cliff with the camera turned
## to face inward, to show the edge clamp. Sheet: docs/plan/moba-arena-play-look-2026-11-04.png. Edits nothing.

const SCENE := "res://scenes/moba3d/arena_play.tscn"
const OUT := "res://docs/plan/moba-arena-play-look-2026-11-04.png"
const TIMES := [2.8, 3.6, 10.0]

var sheet: Image


func _initialize() -> void:
	var demo := "--demo" in OS.get_cmdline_user_args()
	var play: Node3D = load(SCENE).instantiate()
	root.add_child(play)
	var cam = play.get_node("Arena/Camera")
	var player: Node3D = play.get_node("Arena/Player")
	sheet = null if demo else Image.load_from_file(ProjectSettings.globalize_path(OUT))
	if sheet == null:
		sheet = Image.create(1280, 720, false, Image.FORMAT_RGB8)
	sheet.convert(Image.FORMAT_RGB8)
	if demo:
		var frame := 0
		for i in TIMES.size():
			while frame < int(TIMES[i] * 60.0):
				await process_frame
				frame += 1
			await _shot(i, "%.1f s of the demo" % (frame / 60.0), player, cam)
	else:
		for f in 10:
			await process_frame
		player.global_position = Vector3(40.5, 0, 28)
		cam.yaw_degrees = 90.0 # camera to the east, looking west into the map
		cam.snap()
		for f in 6:
			await process_frame
		await _shot(3, "edge clamp", player, cam)
	quit(0)


func _shot(i: int, what: String, player: Node3D, cam) -> void:
	await RenderingServer.frame_post_draw
	var img: Image = root.get_texture().get_image()
	print("  shot %d, %s: machine at %s, camera at %s" % [i + 1, what, player.global_position.snapped(Vector3.ONE * 0.1), cam.global_position.snapped(Vector3.ONE * 0.01)])
	img.convert(Image.FORMAT_RGB8)
	img.resize(640, 360, Image.INTERPOLATE_BILINEAR)
	sheet.blit_rect(img, Rect2i(0, 0, 640, 360), Vector2i((i % 2) * 640, (i / 2) * 360))
	sheet.save_png(ProjectSettings.globalize_path(OUT)) # after every shot, so a demo that quits early keeps them
