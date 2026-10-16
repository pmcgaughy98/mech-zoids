extends SceneTree
## Battle test capture (animation pass 3, 2026-10-12): opens the battle scene windowed, lets the player's machine
## use its third weapon, and saves screenshots through the attack so the staging and animation can be judged
## without sitting at the keyboard. Run windowed (the capture reads the window's texture):
##   Godot --path . --script res://tools/debug/battle_capture.gd
## Writes docs/art/2d/battle_capture_<n>.png and a contact sheet docs/art/2d/battle_capture.png.

const TIMES := [0.05, 0.45, 0.8, 1.0, 1.15, 1.35, 1.7, 2.2]


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	var run = root.get_node("Run")
	run.new_game()
	run.save_path = "res://tools/debug/battle_capture_unused_save.tmp"
	run.battle_request = {}
	var player_id := OS.get_environment("HT_PLAYER")   # optional (2026-10-13): any starter, enemy and weapon
	var tag := "battle_capture"
	if player_id != "":
		var enemy_id := OS.get_environment("HT_ENEMY") if OS.get_environment("HT_ENEMY") != "" else "hippo_m"
		run.battle_request = {"player": Array(player_id.split(",")), "enemy": Array(enemy_id.split(",")), "enemy_deck": run.deck, "flag": "", "reward": "", "win_scene": "title"}
		tag = "battle_%s_vs_%s" % [player_id.replace(",", "+"), enemy_id.replace(",", "+")]   # comma lists field several a side
	root.size = Vector2i(1280, 720)
	root.content_scale_size = Vector2i(320, 180)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	change_scene_to_file("res://scenes/battle.tscn")
	for i in 600:
		await process_frame
		if current_scene != null and current_scene.state == "menu":
			break
	await RenderingServer.frame_post_draw
	var shots: Array = []
	shots.append(root.get_texture().get_image())
	var scene = current_scene
	var weapon: int = int(OS.get_environment("HT_WEAPON")) if OS.get_environment("HT_WEAPON") != "" else 0   # weapon 0 costs no energy, so it always fires
	if scene.logic.valid_targets(scene.current, scene.current.weapons[weapon]).size() > 1:   # the target menu
		scene._open_targets(weapon)
		scene.cursor = 1
		scene._draw_menu()
		for i in 3:
			await process_frame
		await RenderingServer.frame_post_draw
		shots.append(root.get_texture().get_image())
	scene._clear_menu()
	scene.logic.do_action(scene.current, {"kind": "attack", "weapon": weapon, "target": scene.menu_items[scene.cursor].act.get("target", -1) if scene.state == "targets" else -1})
	scene._play_then("next")
	var t := 0.0
	for target_t in TIMES:
		await create_timer(target_t - t).timeout
		t = target_t
		await RenderingServer.frame_post_draw
		shots.append(root.get_texture().get_image())
	var w: int = shots[0].get_width()
	var h: int = shots[0].get_height()
	var cols := 3
	var rows := int(ceil(shots.size() / float(cols)))
	var sheet := Image.create(w * cols, h * rows, false, Image.FORMAT_RGBA8)
	for i in shots.size():
		shots[i].save_png("res://docs/art/2d/%s_%d.png" % [tag, i])
		sheet.blit_rect(shots[i], Rect2i(0, 0, w, h), Vector2i((i % cols) * w, (i / cols) * h))
	sheet.save_png("res://docs/art/2d/%s.png" % tag)
	print("battle_capture: %d shots, state %s" % [shots.size(), scene.state])
	quit(0)
