class_name GateClipTest
extends Node
## The fennec's effect clips (Claude, 2026-11-05, game feel lane, effects spin-off): the fennec in the field at the game
## camera, playing the real kit path from the s, e and n views, saving every frame and a log, then checking it.
##   Default: the small gate alone (FennecKit.gate_cast: the cast pose, the gate on cast f3), cropped round the pair.
##   --shot: the two-faced shot (FennecKit.two_faced_shot, key 5): a bolt forward on cast f3 and one backward out of the
##     gate once it is open, with a dummy in each bolt's path; whole frames, since the bolts fly out of a small crop.
##   --blink: the blink gate (FennecKit.blink_gate, key 2) and its recast 1.2 s later, with the blink flash at both ends
##     of each jump; whole frames, since the camera follows the jump.
##   --arrival: the arrival shield (ArrivalShield, the great gate's arrival) on the fennec (S) from s, e and n, then on
##     the rhino (L) from s and e: it arrives, walks 1 s in a test speed burst leaving afterimages, stands, and the shield
##     expires at 2 s; then it arrives again in place and a hit 1 s later shatters it. Whole frames.
##   --basic: the basic attack (FennecKit.basic_attack, as a bot calls it with its target) at a training dummy from s, e
##     and n, twice, 0.9 s apart (the director's cooldown), with a press while busy that must be refused.
## Run (not headless, it reads the screen): Godot --path . --resolution 1280x720 --fixed-fps 30 --position 20000,20000
##   res://scenes/moba3d/arena_play.tscn -- --gate-clip-test [--shot | --blink | --arrival | --basic] --out=<dir>

const VIEWS: Array[String] = ["s", "e", "n"]
const CLIP := Vector2i(400, 300) ## game pixels
const IDLE := 6 ## frames before the key press
## --shot: metres from the fennec to the dummy ahead, and from the gate to the dummy past it, per view; -1 is no dummy.
## The bolt toward the camera gets none: the chase camera keeps the fennec above the middle, so a dummy far enough away
## to see the bolt fly stands under the screen's edge, and one close enough to see hides the strike. That bolt flies its
## whole reach and leaves the bottom of the screen, as it would in a match.
const SHOT_DUMMIES := {"s": [-1.0, 3.5], "e": [4.5, 3.5], "n": [4.5, -1.0]}
## --blink: metres it blinks, per view. Toward the camera (s) is short, or it lands under the screen's edge.
const BLINK_TO := {"s": 2.0, "e": 4.0, "n": 4.0}
const RECAST_AFTER := 36 ## frames from the blink to the recast (1.2 s; the bot rule would snap back at 1.5 s)
## --arrival: [machine, view] per pass; the rhino passes Tab round to the rhino (the rotation grows as machines join).
const ARRIVAL_PASSES := [["fennec", "s"], ["fennec", "e"], ["fennec", "n"], ["rhino", "s"], ["rhino", "e"]]
const WALK := [8, 38] ## frames after the arrival it walks between
const AGAIN := 75 ## frames after the first arrival: the second
const HIT_AFTER := 30 ## frames after the second arrival: the hit
const BURST := 1.5 ## the test's speed burst on speed_mult, for its 1.2 s (a placeholder: the great gate's number)
## --arrival saves the middle of the screen only, where the chase camera keeps the machine: whole frames ran past 8 min.
const ARRIVAL_REGION := Rect2i(320, 120, 640, 460)
## --basic: metres to the dummy, per view; toward the camera (s) only about 3 m of floor show below the fennec.
const BASIC_TO := {"s": 2.5, "e": 4.5, "n": 4.5}
const BASIC_AGAIN := 27 ## frames between the two basics (0.9 s, the cooldown)
const BASIC_REGION := Rect2i(160, 120, 960, 560) ## wider and taller than the arrival's: the dummy 4.5 m east and the hit 2.5 m south are in the frame
const Arrival := preload("res://scripts/moba3d/arrival_shield.gd") ## by path: its class_name is new (playbook 11)

var out := ""
var player: Node3D
var cam: Camera3D
var kit: FennecKit
var log_lines: PackedStringArray = []
var fails := 0
var shot := "--shot" in OS.get_cmdline_user_args()
var blink := "--blink" in OS.get_cmdline_user_args()
var arrival := "--arrival" in OS.get_cmdline_user_args()
var basic := "--basic" in OS.get_cmdline_user_args()
var arena: Node


func setup(arena_play: Node, output_dir: String) -> void:
	out = output_dir
	arena = arena_play
	player = arena_play.player
	cam = arena_play.arena.get_node("Camera")
	kit = FennecKit.install(player)
	player.set("bot", true)  # hides the mouse aim marker (machine_test_player.gd), so the frames show the effect only
	DirAccess.make_dir_recursive_absolute(out)
	_run.call_deferred()


func _check(ok: bool, what: String) -> void:
	log_lines.append(("ok   " if ok else "FAIL ") + what)
	if not ok:
		fails += 1


## The facing that shows view v from this camera (sector 0 = n, away from it; 4 = s, toward it).
func _facing_for(v: String) -> Vector3:
	var b := cam.global_basis
	var fwd := Vector3(-b.z.x, 0.0, -b.z.z).normalized()
	var right := Vector3(b.x.x, 0.0, b.x.z).normalized()
	var a := DirectionalSprite3D.VIEWS.find(v) * PI / 4.0
	return fwd * cos(a) + right * sin(a)


func _frames(n: int) -> void:
	for k in n:
		await RenderingServer.frame_post_draw


func _grab() -> Image:
	return get_viewport().get_texture().get_image()


func _px(p: Vector3, img: Image) -> Vector2i:
	var k := Vector2(img.get_size()) / get_viewport().get_visible_rect().size
	return Vector2i(cam.unproject_position(p) * k)


func _crop(img: Image, centre: Vector2i) -> Image:
	var r := Rect2i(centre - CLIP / 2, CLIP)
	r.position = r.position.clamp(Vector2i.ZERO, img.get_size() - CLIP)
	return img.get_region(r)


func _run() -> void:
	await _frames(10)
	if shot:
		await _run_shot()
	elif blink:
		await _run_blink()
	elif arrival:
		await _run_arrival()
	elif basic:
		await _run_basic()
	else:
		await _run_gate()
	log_lines.append("gate_clip_test: %d fail" % fails)
	var fa := FileAccess.open(out.path_join("log.txt"), FileAccess.WRITE)
	fa.store_string("\n".join(log_lines) + "\n")
	fa.close()
	print("gate_clip_test: %d fail, %s" % [fails, out])
	get_tree().quit()


func _run_gate() -> void:
	var sprite := player.get_node("Sprite") as DirectionalSprite3D
	log_lines.append("camera pitch %.1f, yaw %.1f; fennec at %s" % [cam.get("pitch_degrees"), cam.get("yaw_degrees"), player.global_position])
	for v in VIEWS:
		var dir := out.path_join(v)
		DirAccess.make_dir_recursive_absolute(dir)
		player.facing = _facing_for(v)
		kit.last.erase("gate_cast")
		await _frames(8)
		# crop centre: halfway between the fennec and where the gate will stand, 0.45 m up
		var mid: Vector3 = player.global_position - kit.ahead() * kit.gate_behind * 0.5 + Vector3.UP * 0.45
		var at := _px(mid, _grab())
		var n := 0
		var seen := {"open": -1, "hold": -1, "close": -1, "gone": -1}
		var total := 200
		var gate: SmallGate = null
		var got := false  # a freed gate compares equal to null, so a flag says whether it was ever picked up
		while n < total:
			if n == IDLE:
				kit.gate_cast()
			await RenderingServer.frame_post_draw
			_crop(_grab(), at).save_png(dir.path_join("f%04d.png" % n))
			var g: Dictionary = kit.last.get("gate_cast", {})
			if not got and not g.is_empty():
				gate = g["gate"]
				got = true
			var ph := "none"
			if got:
				ph = gate.phase if is_instance_valid(gate) else "gone"
				if seen[ph] < 0:
					seen[ph] = n
					if ph == "gone":
						total = n + 6
			log_lines.append("%s f%04d: sprite %s frame %d, gate %s%s" % [v, n, sprite.animation, sprite.frame, ph,
				(" frame %d" % gate.frame) if got and is_instance_valid(gate) else ""])
			n += 1
		var g: Dictionary = kit.last.get("gate_cast", {})
		_check(not g.is_empty() and g["cast_frame"] == FennecKit.CAST_FRAME,
			"%s: the gate opened on cast f%s (want f%d), %s frames after the key" % [v, g.get("cast_frame", "?"), FennecKit.CAST_FRAME, g.get("after_frames", "?")])
		_check(seen["open"] >= 0 and seen["hold"] > seen["open"] and seen["close"] > seen["hold"] and seen["gone"] > seen["close"],
			"%s: open at clip frame %d, hold %d, close %d, gone %d" % [v, seen["open"], seen["hold"], seen["close"], seen["gone"]])
		if not g.is_empty():
			var back: float = (FennecKit.flat(g["at"] - player.global_position)).length()
			_check(absf(back - kit.gate_behind) < 0.05, "%s: the gate stood %.2f m behind the fennec" % [v, back])
		_check(kit.current == "" and sprite.action == "", "%s: the cast ended and the sprite went back to idle" % v)


## The two-faced shot from each view, 6 m into the open floor in front of the spawn, a dummy ahead and one past the gate
## (SHOT_DUMMIES).
func _run_shot() -> void:
	var sprite := player.get_node("Sprite") as DirectionalSprite3D
	player.global_position += Vector3(0.0, 0.0, -6.0)
	if cam.has_method("snap"):
		cam.snap()
	await _frames(10)
	log_lines.append("shot: camera pitch %.1f, yaw %.1f; fennec at %s; bolt %.1f m/s, reach %.1f m" % [cam.get("pitch_degrees"),
		cam.get("yaw_degrees"), player.global_position, kit.bolt_speed, kit.bolt_reach])
	for v in VIEWS:
		var dir := out.path_join("shot_" + v)
		DirAccess.make_dir_recursive_absolute(dir)
		player.facing = _facing_for(v)
		kit.last.erase("two_faced_shot")
		await _frames(4)
		var fwd := kit.ahead()
		var dist: Array = SHOT_DUMMIES[v]
		var front: TrainingDummy = _dummy_at(player.global_position + fwd * dist[0]) if dist[0] > 0.0 else null
		var back: TrainingDummy = _dummy_at(player.global_position - fwd * (kit.gate_behind + dist[1])) if dist[1] > 0.0 else null
		var dummies := [front, back].filter(func(e): return e != null)
		await _frames(8)
		var n := 0
		var total := 150
		var at := {"bolt1": -1, "bolt2": -1, "hold": -1, "done": -1}
		var slowed := {"front": 0.0, "back": 0.0}
		while n < total:
			if n == IDLE:
				kit.two_faced_shot()
			await RenderingServer.frame_post_draw
			_grab().save_png(dir.path_join("f%04d.png" % n))
			var r: Dictionary = kit.last.get("two_faced_shot", {})
			var bolts: Array = r.get("bolts", [])
			var alive := bolts.filter(func(b): return is_instance_valid(b)).size()
			var ph := "none"
			if r.has("gate"):
				ph = r["gate"].phase if is_instance_valid(r["gate"]) else "gone"
			if at["bolt1"] < 0 and bolts.size() >= 1:
				at["bolt1"] = n
			if at["bolt2"] < 0 and bolts.size() >= 2:
				at["bolt2"] = n
			if at["hold"] < 0 and ph == "hold":
				at["hold"] = n
			if at["done"] < 0 and bolts.size() == 2 and alive == 0 and ph == "gone":
				at["done"] = n
				total = n + 8
			if front != null:
				slowed["front"] = maxf(slowed["front"], front.slowed)
			if back != null:
				slowed["back"] = maxf(slowed["back"], back.slowed)
			log_lines.append("shot %s f%04d: sprite %s frame %d, gate %s, bolts fired %d alive %d, struck %d, fwd %s back %s" % [v,
				n, sprite.animation, sprite.frame, ph, bolts.size(), alive, (r.get("struck", []) as Array).size(), _state(bolts, 0),
				_state(bolts, 1)])
			n += 1
		var r: Dictionary = kit.last.get("two_faced_shot", {})
		var struck: Array = r.get("struck", [])
		_check(not r.is_empty() and r["cast_frame"] == FennecKit.CAST_FRAME and at["bolt1"] >= 0,
			"%s: the forward bolt and the gate came on cast f%s (want f%d), clip frame %d" % [v, r.get("cast_frame", "?"),
			FennecKit.CAST_FRAME, at["bolt1"]])
		_check(at["bolt2"] > at["bolt1"] and at["bolt2"] == at["hold"],
			"%s: the backward bolt left the gate as it finished opening (clip frame %d, gate open at %d)" % [v, at["bolt2"], at["hold"]])
		var ends: Dictionary = r.get("ends", {})
		var want := ["target" if front != null else "reach", "target" if back != null else "reach"]
		_check(struck.size() == dummies.size() and dummies.all(func(e): return e in struck) and ends.get(0) == want[0]
			and ends.get(1) == want[1], "%s: forward bolt ended at its %s (want %s), backward at its %s (want %s); %d of %d dummies struck" % [v,
			ends.get(0, "?"), want[0], ends.get(1, "?"), want[1], struck.size(), dummies.size()])
		_check((front == null or slowed["front"] > 0.0) and (back == null or slowed["back"] > 0.0), "%s: every dummy struck was slowed" % v)
		_check(at["done"] >= 0, "%s: both bolts and the gate were gone by clip frame %d" % [v, at["done"]])
		_check(kit.current == "" and sprite.action == "", "%s: the cast ended and the sprite went back to idle" % v)
		for e in dummies:
			e.queue_free()
		await _frames(2)


func _dummy_at(p: Vector3) -> TrainingDummy:
	var d := TrainingDummy.new()
	player.get_parent().add_child(d)
	d.global_position = p
	return d


## "-" not fired yet, "fly", or "done".
func _state(bolts: Array, i: int) -> String:
	if bolts.size() <= i:
		return "-"
	return "fly" if is_instance_valid(bolts[i]) else "done"


## The blink gate and its recast from each view, 6 m into the open floor: a blink of BLINK_TO toward the facing, the
## recast RECAST_AFTER frames later. The camera follows the fennec, as in a match.
func _run_blink() -> void:
	var sprite := player.get_node("Sprite") as DirectionalSprite3D
	player.global_position += Vector3(0.0, 0.0, -6.0)
	if cam.has_method("snap"):
		cam.snap()
	await _frames(10)
	var home: Vector3 = player.global_position
	var w: Node = kit.world()
	log_lines.append("blink: camera pitch %.1f, yaw %.1f; fennec at %s" % [cam.get("pitch_degrees"), cam.get("yaw_degrees"), home])
	for v in VIEWS:
		var dir := out.path_join("blink_" + v)
		DirAccess.make_dir_recursive_absolute(dir)
		player.global_position = home
		if cam.has_method("snap"):
			cam.snap()
		player.facing = _facing_for(v)
		kit.last.erase("blink_gate")
		kit.last.erase("gate_back")
		await _frames(8)
		var start: Vector3 = kit.feet()
		var aim: Vector3 = start + _facing_for(v) * float(BLINK_TO[v])
		var n := 0
		var total := 120
		var at := {"blink": -1, "back": -1, "clear": -1}
		var seen := {"blink": [], "back": []} ## [flashes, ghosts showing] on the frame after each jump
		var hidden := {"blink": 0, "back": 0} ## frames the sprite was hidden after each jump
		var ok := {"blink": false, "back": false}
		while n < total:
			if n == IDLE:
				ok["blink"] = kit.blink_gate(aim)
				at["blink"] = n
			if n == IDLE + RECAST_AFTER:
				ok["back"] = kit.gate_back()
				at["back"] = n
			await RenderingServer.frame_post_draw
			_grab().save_png(dir.path_join("f%04d.png" % n))
			var flashes := w.find_children("*BlinkFlash*", "", true, false).filter(func(f): return not f.is_queued_for_deletion())
			var ghosts := w.find_children("*BlinkGhost*", "", true, false).filter(func(g): return g.visible and not g.is_queued_for_deletion())
			var leg := "back" if at["back"] >= 0 else "blink"
			if at[leg] == n:
				seen[leg] = [flashes.size(), ghosts.size()]
			if at["blink"] >= 0 and not sprite.visible:
				hidden[leg] += 1
			if at["back"] >= 0 and at["clear"] < 0 and flashes.is_empty():
				at["clear"] = n
				total = n + 16  # the gate's close
			log_lines.append("blink %s f%04d: fennec %s, sprite %s %s, flashes %d, ghosts %d" % [v, n, kit.feet(),
				"shown" if sprite.visible else "hidden", sprite.animation, flashes.size(), ghosts.size()])
			n += 1
		var b: Dictionary = kit.last.get("blink_gate", {})
		var g: Dictionary = kit.last.get("gate_back", {})
		var went: float = FennecKit.flat(b.get("to", start) - start).length()
		_check(ok["blink"] and absf(went - float(BLINK_TO[v])) < 0.1, "%s: blinked %.2f m (want %.1f)" % [v, went, BLINK_TO[v]])
		_check(seen["blink"] == [2, 1] and seen["back"] == [2, 1],
			"%s: each jump left a flash at both ends, with the fennec's ghost where it left (blink %s, recast %s: [flashes, ghosts])" % [v, seen["blink"], seen["back"]])
		_check(hidden["blink"] >= 1 and hidden["blink"] <= 3 and hidden["back"] >= 1 and hidden["back"] <= 3,
			"%s: the body showed out of the light, hidden %d frames after the blink and %d after the recast (want 1-3)" % [v, hidden["blink"], hidden["back"]])
		_check(ok["back"] and FennecKit.flat(kit.feet() - start).length() < 0.05, "%s: the recast put it back where it started" % v)
		_check(at["clear"] >= 0 and sprite.visible and w.find_children("*BlinkGhost*", "", true, false).is_empty(),
			"%s: every flash and ghost was gone by clip frame %d and the body was showing" % [v, at["clear"]])
	player.global_position = home


func _run_arrival() -> void:
	var sprite := player.get_node("Sprite") as DirectionalSprite3D
	player.global_position += Vector3(0.0, 0.0, -6.0)
	if cam.has_method("snap"):
		cam.snap()
	await _frames(10)
	var home: Vector3 = player.global_position
	log_lines.append("arrival: camera pitch %.1f, yaw %.1f; at %s" % [cam.get("pitch_degrees"), cam.get("yaw_degrees"), home])
	for pass_ in ARRIVAL_PASSES:
		var who: String = pass_[0]
		var v: String = pass_[1]
		if who == "rhino" and str(sprite.get("size_class")) != "L":
			arena.set("machine", "fennec")  # the test put the fennec's kit on itself
			for k in 6:  # Tab round to the rhino, an L machine (the wolf joined after the fennec, 2026-11-05)
				arena.swap()
				if arena.get("machine") == "rhino":
					break
			sprite = player.get_node("Sprite") as DirectionalSprite3D
		var dir := out.path_join("arrival_%s_%s" % [who, v])
		DirAccess.make_dir_recursive_absolute(dir)
		player.global_position = home
		player.facing = _facing_for(v)
		if cam.has_method("snap"):
			cam.snap()
		await _frames(8)
		var clock := {"n": 0}
		var why := {} ## "first" / "second" -> [why, clip frame]
		var first: Node3D = null
		var second: Node3D = null
		var size_ok := false
		var hold_ok := false
		var spawned := -1
		var trail_max := 0
		var trails_after := -1
		var total := IDLE + AGAIN + HIT_AFTER + 20
		while clock["n"] < total:
			var n: int = clock["n"]
			if n == IDLE:
				first = Arrival.play(player)
				first.ended.connect(func(e: String) -> void: why["first"] = [e, clock["n"]])
				player.set("speed_mult", BURST)
				size_ok = first.size == ("l" if who == "rhino" else "s") and is_equal_approx(first.px, sprite.pixel_size)
			if n == IDLE + WALK[0]:
				player.set("move_override", _facing_for(v))
			if n == IDLE + WALK[1]:
				player.set("move_override", null)
			if n == IDLE + 36:
				player.set("speed_mult", 1.0)  # the burst's 1.2 s
			if n == IDLE + AGAIN:
				player.global_position = home  # in place, where the camera was set
				second = Arrival.play(player)
				second.ended.connect(func(e: String) -> void: why["second"] = [e, clock["n"]])
			if n == IDLE + AGAIN + HIT_AFTER:
				second.hit()
			await RenderingServer.frame_post_draw
			_grab().get_region(ARRIVAL_REGION).save_png(dir.path_join("f%04d.png" % n))
			var live: Node3D = Arrival.on(player)
			var tr := get_tree().get_nodes_in_group("arrival_trail").filter(func(t): return not t.is_queued_for_deletion())
			trail_max = maxi(trail_max, tr.size())
			if n == IDLE + 10:
				hold_ok = live == first and live.part == Arrival.HOLD and live.is_up()
			if n == IDLE + 50:
				spawned = first.trails if is_instance_valid(first) else -1
			if n == IDLE + 52:
				trails_after = tr.size()
			log_lines.append("arrival %s %s f%04d: at %s, sprite %s %s, shield %s, trails %d" % [who, v, n,
				player.global_position, "shown" if sprite.visible else "hidden", sprite.animation,
				"part %d frame %d" % [live.part, live.frame] if live != null else "none", tr.size()])
			clock["n"] = n + 1
		var f1: Array = why.get("first", ["", -1])
		var f2: Array = why.get("second", ["", -1])
		var tag := "%s %s" % [who, v]
		_check(size_ok, "%s: the shield is the %s size, at the machine's texel (%.3f m)" % [tag, "l" if who == "rhino" else "s", sprite.pixel_size])
		_check(hold_ok, "%s: it formed and was holding 10 frames after the arrival" % tag)
		_check(spawned >= 8 and spawned <= 20 and trail_max >= 3,
			"%s: it left %d afterimages walking in the burst, up to %d at once (want 8-20, 3 or more)" % [tag, spawned, trail_max])
		_check(trails_after == 0, "%s: no afterimages once the burst was over (%d)" % [tag, trails_after])
		_check(f1[0] == "expire" and f1[1] >= IDLE + 62 and f1[1] <= IDLE + 74,
			"%s: the shield expired at its 2 s (%s at clip frame %d, want %d-%d)" % [tag, f1[0], f1[1], IDLE + 62, IDLE + 74])
		var hit_at := IDLE + AGAIN + HIT_AFTER
		_check(f2[0] == "break" and f2[1] - hit_at <= 10, "%s: the hit shattered the second (%s, %d frames after the hit)" % [tag, f2[0], f2[1] - hit_at])
		_check(Arrival.on(player) == null and get_tree().get_nodes_in_group("arrival_trail").is_empty() and sprite.visible
			and is_equal_approx(float(player.get("speed_mult")), 1.0), "%s: nothing left after, the body showing" % tag)
	player.global_position = home


func _run_basic() -> void:
	var sprite := player.get_node("Sprite") as DirectionalSprite3D
	player.global_position += Vector3(0.0, 0.0, -6.0)
	if cam.has_method("snap"):
		cam.snap()
	await _frames(10)
	var home: Vector3 = player.global_position
	log_lines.append("basic: camera pitch %.1f, yaw %.1f; fennec at %s" % [cam.get("pitch_degrees"), cam.get("yaw_degrees"), home])
	for v in VIEWS:
		var dir := out.path_join("basic_" + v)
		DirAccess.make_dir_recursive_absolute(dir)
		player.global_position = home
		player.facing = _facing_for(v)
		if cam.has_method("snap"):
			cam.snap()
		var dummy := _dummy_at(home + _facing_for(v) * float(BASIC_TO[v]))
		await _frames(8)
		var presses := [IDLE, IDLE + BASIC_AGAIN]
		var said := [] ## what basic_attack returned at each press
		var busy_refused := false
		var fired_at := [] ## clip frame each dart showed up
		var free_at := [] ## clip frame the kit let go after each press
		var hit_at := [] ## clip frame the dart's hit burst first showed after each press
		var recs := []
		var n := 0
		var total := IDLE + BASIC_AGAIN + 24
		while n < total:
			if n in presses:
				dummy.last_hit_scale = 1.0
				said.append(kit.basic_attack(dummy))
				recs.append(kit.last.get("basic_attack", {}))
				if n == IDLE:
					busy_refused = not kit.basic_attack(dummy)  # pressed again while the swing runs
			await RenderingServer.frame_post_draw
			_grab().get_region(BASIC_REGION).save_png(dir.path_join("f%04d.png" % n))
			var r: Dictionary = recs.back() if not recs.is_empty() else {}
			if not r.is_empty() and r.get("dart") != null and fired_at.size() < recs.size():
				fired_at.append(n)
			if not recs.is_empty() and free_at.size() < recs.size() and kit.current == "" and not player.busy:
				free_at.append(n)
			var darts := kit.world().find_children("*", "", true, false).filter(func(c): return c.get("dart") == true and not c.is_queued_for_deletion())
			var hit_bursts := kit.world().find_children("*", "", true, false).filter(func(c): return c.get("rows") == 1 and c.get("ms") != null)
			if not hit_bursts.is_empty() and hit_at.size() < recs.size():
				hit_at.append(n)
			log_lines.append("basic %s f%04d: sprite %s frame %d, kit %s, busy %s, darts %d, dummy scale %.2f, hit bursts %d" % [v, n,
				sprite.animation, sprite.frame, kit.current if kit.current != "" else "-", player.busy, darts.size(), dummy.last_hit_scale, hit_bursts.size()])
			n += 1
		for i in recs.size():
			var r: Dictionary = recs[i]
			var p: int = presses[i]
			_check(said[i] == true and fired_at.size() > i and fired_at[i] - p <= 3,
				"%s basic %d: fired %d frames after the press (want 1-3)" % [v, i + 1, (fired_at[i] - p) if fired_at.size() > i else -1])
			_check(r.get("why", "") == "target" and dummy in r.get("struck", []),
				"%s basic %d: the dart struck the dummy %.1f m away (%s)" % [v, i + 1, BASIC_TO[v], r.get("why", "")])
			_check(hit_at.size() > i and hit_at[i] > p, "%s basic %d: the dart's hit burst showed (clip frame %d)" % [v, i + 1, hit_at[i] if hit_at.size() > i else -1])
			_check(free_at.size() > i and free_at[i] - p <= 8, "%s basic %d: the swing let go %d frames after the press (want 8 or fewer)" % [v, i + 1, (free_at[i] - p) if free_at.size() > i else -1])
		_check(is_equal_approx(dummy.last_hit_scale, 0.5), "%s: each hit carried scale %.2f (30 of the kit hit's 60)" % [v, dummy.last_hit_scale])
		_check(busy_refused, "%s: a second press during the swing was refused" % v)
		dummy.queue_free()
	player.global_position = home
