extends SceneTree
## Battle effects capture (Claude, 2026-10-15): opens the battle scene windowed at 1280x720 (the default window, field
## scale 0.75) and records each starter weapon's attack frame by frame, so the effects can be judged without sitting
## at the keyboard. Every attack is a forced hit (or a miss with HT_MISS=1), played through battle.gd's _play_attack.
##   Godot --path . --script res://tools/debug/vfx_capture.gd
## Env: HT_OUT (folder, default the session scratchpad passed in), HT_ONLY ("ape_l/punch,wolf_m/howl"), HT_SIDE
## ("enemy" to attack from the right), HT_FPS (frames per second captured, default 15), HT_EVENT ("charge", "repair" or
## "destroyed": that step's effects on each machine instead of its weapons; HT_ONLY then lists machine ids).
## Writes <out>/<machine>_<clip>[_enemy][_miss]/<nnn>.png and <out>/index.json (impact time and frame times per attack).
## tools/art/vfx_sheets.py turns the frames into contact sheets and GIFs.

const Machines := preload("res://scripts/data/machines.gd")

var out := ""


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	out = OS.get_environment("HT_OUT")
	if out == "":
		out = "res://docs/art/2d/vfx_frames"
	DirAccess.make_dir_recursive_absolute(out)
	var only := OS.get_environment("HT_ONLY")
	var side := OS.get_environment("HT_SIDE") if OS.get_environment("HT_SIDE") != "" else "player"
	var miss := OS.get_environment("HT_MISS") == "1"
	var fps := float(OS.get_environment("HT_FPS")) if OS.get_environment("HT_FPS") != "" else 15.0
	var run = root.get_node("Run")
	run.new_game()
	run.save_path = "res://tools/debug/vfx_capture_unused_save.tmp"
	root.size = Vector2i(1280, 720)
	root.content_scale_size = Vector2i(320, 180)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	var index := {}
	var ids := []
	for id in Machines.MACHINES:
		if FileAccess.file_exists("res://art/machines/%s/anim/anim.json" % id):
			ids.append(id)
	ids.sort()
	for id in ids:
		var partner: String = "hippo_m" if id != "hippo_m" else "ape_l"
		if id == "hippo_m":
			partner = "kangaroo_m"
		var event := OS.get_environment("HT_EVENT")
		var list: Array = Machines.MACHINES[id].weapons if event == "" else [{"clip": event, "name": event, "type": ""}]
		for w: Dictionary in list:
			var key: String = "%s/%s" % [id, w.clip] if event == "" else id
			if only != "" and not key in only.split(","):
				continue
			run.battle_request = {"player": [id] if side == "player" else [partner], "enemy": [partner] if side == "player" else [id],
				"enemy_deck": run.deck, "flag": "", "reward": "", "win_scene": "title"}
			run.battle_seed = 11
			change_scene_to_file("res://scenes/battle.tscn")
			await process_frame
			while current_scene == null or not current_scene.has_method("_play_attack"):
				await process_frame
			var scene = current_scene
			scene.state = "capture"
			for i in 20:   # let the idle settle
				await process_frame
			scene._clear_menu()
			var ai: int = 0 if side == "player" else 1
			var snap := []
			for u in scene.logic.units:
				snap.append([u.hp, u.ep])
			snap[1 - ai][0] = int(snap[1 - ai][0] * 0.7)
			scene.message.text = "%s uses %s" % [scene.logic.units[ai].name, w.name]
			var step := {"kind": "miss" if miss else "damage", "text": "", "unit": 1 - ai, "actor": ai, "clip": w.clip,
				"wtype": w.type, "value": 27, "snap": snap}
			var tag := "%s_%s%s%s" % [id, w.clip, "_enemy" if side == "enemy" else "", "_miss" if miss else ""]
			DirAccess.make_dir_recursive_absolute("%s/%s" % [out, tag])
			var start := Time.get_ticks_msec()
			var hold := 0.0
			var me: Node2D = scene.sprites[ai]
			if event == "charge":
				scene.message.text = "%s braces and charges energy (+30)" % scene.logic.units[ai].name
				scene.fx.charging(me)
				hold = 1.0
			elif event == "repair":
				scene.message.text = "%s uses Repair Kit: +40 HP" % scene.logic.units[ai].name
				scene.fx.repaired(me)
				scene._pop_text(ai, "+40", Color("7cff9a"))
				hold = 1.0
			elif event == "destroyed":
				scene.message.text = "%s is down!" % scene.logic.units[ai].name
				scene._step_down(me, "death", 0.0, true)
				MachineAnim.play(me, "death")
				hold = scene.fx.destroyed(me) + 1.2
			else:
				hold = scene._play_attack(step)
			var times := []
			var n := int(ceil((hold + 0.2) * fps))
			for k in n:
				var due := start + int(k * 1000.0 / fps)
				while Time.get_ticks_msec() < due:
					await process_frame
				await RenderingServer.frame_post_draw
				times.append((Time.get_ticks_msec() - start) / 1000.0)
				root.get_texture().get_image().save_png("%s/%s/%03d.png" % [out, tag, k])
			index[tag] = {"weapon": w.name, "type": w.type, "hold": hold, "fps": fps, "times": times,
				"impact": scene.fx.last.get("impact", -1.0), "field_scale": scene.field_s}
			print("vfx_capture: %s %d frames" % [tag, n])
	var f := FileAccess.open("%s/index.json" % out, FileAccess.WRITE)
	f.store_string(JSON.stringify(index, "  "))
	f.close()
	quit(0)
