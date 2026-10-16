extends SceneTree
## Every starter weapon's battle effects play, land and clean up (Claude, 2026-10-15). For each animated machine and
## each of its weapons, from both sides, as a hit and as a miss, opens the real battle scene against a partner, plays
## the attack through battle.gd's own _play_attack (the recipe in scripts/battle/vfx_recipes.gd, drawn by
## scripts/battle/vfx.gd) and checks:
## - the recipe names only effects vfx.gd has, and only frames the clip has;
## - the impact (when the number shows) comes before the step's hold ends;
## - a melee blow lands on the target: its contact point inside the target's art box;
## - each shot leaves from the attacker's art: an opaque pixel within 3 px of its "from" point;
## - the attacker stays on screen while it moves (its art's top row, frame by frame, at the window's field scale), and
##   its feet never go below the player's row (over the panel);
## - when the step ends the attacker is home and drawn at its normal depth, the target is home, the stage is still and
##   the background undimmed, and a second later every effect node has freed itself.
## The older drawn machines (no animation folder: lion_m, raptor_s, hawk_s) also fire each weapon (their weapon type's
## recipe), and take the gorilla's punch, whose blow must land inside their drawn box.
## Runs at each window size that gives a different field scale (1280x720, 1920x1080, and a bare 320x180 window where
## the field cannot zoom out; there the poses battle_fit_check.gd allows may lose the same rows), at 4x speed.
## Run: Godot --headless --path . --script res://tools/debug/vfx_check.gd

const Machines := preload("res://scripts/data/machines.gd")
const Recipes := preload("res://scripts/battle/vfx_recipes.gd")
const Vfx := preload("res://scripts/battle/vfx.gd")
const Stage := preload("res://scripts/battle/stage.gd")
const Fit := preload("res://tools/debug/battle_fit_check.gd")
const WINDOWS := [Vector2i(1280, 720), Vector2i(1920, 1080), Vector2i(320, 180)]

var fails := 0
var checked := 0


func _initialize() -> void:
	call_deferred("_run")


func fail(msg: String) -> void:
	fails += 1
	print("vfx_check: FAIL %s" % msg)


func _run() -> void:
	Engine.time_scale = 4.0
	var run = root.get_node("Run")
	run.new_game()
	run.save_path = "res://tools/debug/vfx_check_unused_save.tmp"
	var ids := []
	for id in Machines.MACHINES:
		if FileAccess.file_exists("res://art/machines/%s/anim/anim.json" % id):
			ids.append(id)
	ids.sort()
	_check_recipes(ids)
	for size in WINDOWS:
		root.size = size
		print("vfx_check: window %s, field scale %.3f" % [str(root.size), Stage.field_scale(Stage.window_scale(root.size))])
		await _all(ids, run)
	print("vfx_check: %d attacks checked" % checked)
	print("vfx_check: %s" % ("PASS" if fails == 0 else "FAIL (%d)" % fails))
	Engine.time_scale = 1.0
	quit(0 if fails == 0 else 1)


func _all(ids: Array, run) -> void:
	var older := []
	for id in Machines.MACHINES:
		if not id in ids:
			older.append(id)
	for id in older:
		for side in ["player", "enemy"]:
			var scene = await _open(run, id if side == "player" else "ape_l", "ape_l" if side == "player" else id)
			var ai: int = 0 if side == "player" else 1
			for w: Dictionary in Machines.MACHINES[id].weapons:
				await _attack(scene, id, side, ai, 1 - ai, w, "damage")
			# the gorilla's crossing punch into the drawn machine
			await _attack(scene, "ape_l", "enemy" if side == "player" else "player", 1 - ai, ai, Machines.MACHINES.ape_l.weapons[0], "damage")
	for id in ids:
		var partner: String = "hippo_m" if id != "hippo_m" else "ape_l"
		for side in ["player", "enemy"]:
			var req := {"player": [id] if side == "player" else [partner], "enemy": [partner] if side == "player" else [id],
				"enemy_deck": run.deck, "flag": "", "reward": "", "win_scene": "title"}
			var scene = await _open(run, req.player[0], req.enemy[0])
			var ai: int = 0 if side == "player" else 1
			var ti: int = 1 - ai
			var weapons: Array = Machines.MACHINES[id].weapons
			for w: Dictionary in weapons:
				for kind in ["damage", "miss"]:
					await _attack(scene, id, side, ai, ti, w, kind)


func _open(run, player: String, enemy: String):
	run.battle_request = {"player": [player], "enemy": [enemy], "enemy_deck": run.deck, "flag": "", "reward": "", "win_scene": "title"}
	change_scene_to_file("res://scenes/battle.tscn")
	await process_frame
	while current_scene == null or not current_scene.has_method("_play_attack"):
		await process_frame
	var scene = current_scene
	scene.state = "check"   # nothing in battle.gd's _process runs while the check drives it
	for i in 5:
		await process_frame
	scene._clear_menu()
	return scene


func _check_recipes(ids: Array) -> void:
	for id in ids:
		var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://art/machines/%s/anim/anim.json" % id))
		for w: Dictionary in Machines.MACHINES[id].weapons:
			var clip: String = w.get("clip", "")
			if not meta.clips.has(clip):
				fail("%s/%s: no such clip" % [id, clip])
				continue
			var frames: int = meta.clips[clip].frames.size()
			var r := Recipes.find(id, clip, w.type)
			if not Recipes.BY_CLIP.has("%s/%s" % [id, clip]):
				fail("%s/%s: no recipe of its own (falls back to %s)" % [id, clip, w.type])
			var cues: Array = r.get("cues", []) + r.get("impact", []) + r.get("miss", [])
			if r.has("shot"):
				cues.append(r.shot)
				for sub in ["muzzle", "land"]:
					if r.shot.has(sub):
						cues.append(r.shot[sub])
			for c: Dictionary in cues:
				if not (c.fx in Vfx.EFFECTS or c.fx in Vfx.CUE_ONLY):
					fail("%s/%s: unknown effect %s" % [id, clip, c.fx])
				if c.has("frame") and int(c.frame) >= frames:
					fail("%s/%s: frame %d past the clip's %d" % [id, clip, c.frame, frames])
				for key in ["at", "to", "from"]:
					if c.get(key) is Dictionary and c[key].has("frame") and int(c[key].frame) >= frames:
						fail("%s/%s: %s frame %d past the clip's %d" % [id, clip, key, c[key].frame, frames])


func _attack(scene, id: String, side: String, ai: int, ti: int, w: Dictionary, kind: String) -> void:
	var clip: String = w.get("clip", "")
	var tag := "%.2f %s/%s %s %s" % [scene.field_s, id, w.get("clip", w.name), side, "hit" if kind == "damage" else "miss"]
	var actor: Node2D = scene.sprites[ai]
	var target: Node2D = scene.sprites[ti]
	var snap := []
	for u in scene.logic.units:
		snap.append([u.hp, u.ep])
	var step := {"kind": kind, "text": "", "unit": ti, "actor": ai, "clip": w.get("clip", ""), "wtype": w.type, "value": 23, "snap": snap}
	var home_a := actor.position
	var home_t := target.position
	var order := actor.get_index()
	var fx: Vfx = scene.fx
	var hold: float = scene._play_attack(step)
	var impact := -1.0
	var r := Recipes.find(id, w.get("clip", ""), w.type)
	# the shot's muzzle, measured on the frame it fires from
	if r.has("shot") and r.shot.get("from") is Dictionary:
		var spec: Dictionary = r.shot.from
		var p: Vector2 = fx.anchor(spec, actor, target, clip) - Vector2(float(spec.get("dx", 0)) * actor.scale.x, float(spec.get("dy", 0)))
		var tex: Texture2D = fx.frame_tex(actor, clip, int(spec.get("frame", -1)))
		var local := Vector2((p.x - actor.position.x) * actor.scale.x, p.y - actor.position.y)
		if tex != null and not _opaque_near(fx, tex, local, 3):   # drawn machines have no image to test
			fail("%s: shot leaves from %s, not on the art" % [tag, str(local.round())])
	var contact: Vector2 = fx.last.get("contact", Vector2.INF)
	# the number shows at the impact: battle.gd queues it on fx.after; find when by watching the digits appear
	var t := 0.0
	var labels_before: int = _labels(scene)
	var worst_top := INF
	var worst_feet := -INF
	var a := actor.get_node_or_null("anim") as AnimatedSprite2D
	while t < hold:
		await process_frame
		t += root.get_process_delta_time()   # game seconds (already scaled by Engine.time_scale)
		if impact < 0.0 and _labels(scene) > labels_before:
			impact = t
		if a != null:
			var top: int = MachineAnim._top_row(a.sprite_frames.get_frame_texture(a.animation, a.frame))
			worst_top = minf(worst_top, (actor.position.y + top) * scene.field_s)
			worst_feet = maxf(worst_feet, (actor.position.y + float(actor.get_meta("feet_y"))) * scene.field_s)
	checked += 1
	if worst_feet > Stage.PLAYER_FEET_Y + 1.0:
		fail("%s: the attacker's feet reach row %.1f, below the player's row %d (over the panel)" % [tag, worst_feet, Stage.PLAYER_FEET_Y])
	var allowed: int = Fit.ALLOWED.get("%s/%s" % [id, clip], 0) if scene.field_s >= 1.0 else 0
	if worst_top < -allowed - 0.5:
		fail("%s: the attacker's top goes %.1f rows above the screen (allowed %d)" % [tag, -worst_top, allowed])
	if impact < 0.0:
		fail("%s: no number or Miss shown within the %.2f s hold" % [tag, hold])
	if contact != Vector2.INF and kind == "damage":
		var box := _art_box(fx, target)
		if not box.grow(4).has_point(contact):
			fail("%s: the blow lands at %s, outside the target's art %s" % [tag, str(contact.round()), str(box)])
	if actor.position.distance_to(home_a) > 1.0 or actor.get_index() != order:
		fail("%s: attacker not home (%s, was %s) or not back in its draw order" % [tag, str(actor.position), str(home_a)])
	if target.position.distance_to(home_t) > 1.0:
		fail("%s: target not home (%s, was %s)" % [tag, str(target.position), str(home_t)])
	if scene.stage_root.position != Vector2.ZERO:
		fail("%s: the stage is still shaking at %s" % [tag, str(scene.stage_root.position)])
	if fx.background.modulate != Color.WHITE:
		fail("%s: the background is still dimmed" % tag)
	await create_timer(1.0).timeout
	var left := fx.front.get_child_count() + fx.back.get_child_count()
	if left > 0:
		fail("%s: %d effect nodes still alive a second after the step" % [tag, left])
	print("vfx_check: %-33s impact %.2f s, hold %.2f s, top row %3d, contact %s" % [tag, impact, hold, int(worst_top) if worst_top != INF else -1, "-" if contact == Vector2.INF else str(contact.round())])


func _labels(scene) -> int:
	var n := 0
	for c in scene.get_children():
		if c is Label and c.position.y < 124 and c.text != "":
			n += 1
	return n


func _art_box(fx: Vfx, node: Node2D) -> Rect2:
	var r: Rect2i = fx.rect_of(node, fx.frame_tex(node, "", -1))
	var x0 := node.position.x + r.position.x * node.scale.x
	var x1 := node.position.x + r.end.x * node.scale.x
	return Rect2(Vector2(minf(x0, x1), node.position.y + r.position.y), Vector2(absf(x1 - x0), r.size.y))


func _opaque_near(fx: Vfx, tex: Texture2D, local: Vector2, d: int) -> bool:
	fx.art_rect(tex)
	var img: Image = fx._images.get(tex)
	if img == null:
		return false
	for y in range(roundi(local.y) - d, roundi(local.y) + d + 1):
		for x in range(roundi(local.x) - d, roundi(local.x) + d + 1):
			if x >= 0 and y >= 0 and x < img.get_width() and y < img.get_height() and img.get_pixel(x, y).a > 0.5:
				return true
	return false
