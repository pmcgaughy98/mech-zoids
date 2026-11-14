class_name FennecKit
extends Node
## The fennec's kit in the 3D slice (Claude, 2026-11-04, game feel lane; Preston: "approve fennec kit build"). What each
## ability does is Preston's design in docs/plan/moba-kits.md (Fennec, a small control mage), under its working labels.
## Keys 1-4 in the field; the reveal and tools/debug/fennec3d_check.gd call the same functions. Every length is a
## presentation placeholder so the abilities can be seen, not a balance number: no cooldowns or damage numbers exist yet.
##   Passive, big ears: enemies (group "kit_target") moving within hear_radius show as sound pings at their feet, drawn
##     through walls (the slice has no fog or camouflage yet, so walls stand in for them).
##   1 sand kick: the paw throws sand across a cone ahead: enemies in it are hit and slowed.
##   2 blink gate (Preston, 2026-11-04: "Build blink gate", the Janus kit): blinks a short way toward the aim and leaves
##     a gate where it stood; pressing 2 again inside the window snaps it back through the gate. The gate is the small
##     gate (SmallGate, 2026-11-05), held open for the window. Ear burst (the old 2) stays as a function for the reveal
##     and its check, with no key.
##   basic attack (2026-11-05, Preston: "we need basic attacks"; the hook is the game feel lane's): Space or left click
##     in a match, or a bot's swing: a small violet dart toward the aim, on cast f2-f4 (basic_attack below).
##   5 two-faced shot (2026-11-05, effects spin-off; the 11-05 kit's slot 1): the 35-degree cast pose; on its f3 a bolt
##     flies forward and the small gate opens behind the fennec, and once the gate is open a second bolt flies backward
##     out of it. Each bolt strikes the first enemy in its line (a hit and a slow). On key 5 until the 11-05 abilities
##     replace the old ones. gate_cast() is the gate alone (its clip test).
##   3 tunnel: digs in here and comes up further on; allies who step into the entrance while it is open come out of
##     the exit.
##   4 sonic boom: after a short charge, a huge cone of sound ahead: enemies in it are hit and knocked back.
## Frames: Codex, packed by the animation lane (art/machines/fennec/fennec_frames.tres, 40 animations): S class on a
## 192 canvas, feet on row 160, all five views drawn for every move (sets C and D added se and ne). Effects:
## tools/art/draw_fennec_kit_fx.py. Every move goes through ArenaMotion, so arena walls stop it.

signal impact(strength: float) ## something landed hard; cameras can shake on it
signal used(slot: String)
signal cue(name: String) ## named moments for the sound lane: basic_cast, basic_hit

const FENNEC_FRAMES := preload("res://art/machines/fennec/fennec_frames.tres")
const CANVAS := 192
const FEET_EDGE_ROW := 161 ## the feet stand on row 160 (animation lane)
## The pace the drawn trot keeps its feet planted at (animation lane, 2026-11-04). The move speed itself is Preston's.
const STRIDE := 0.56
const KICK_FRAME := 3 ## sand_kick f3 (0.52 s): the paw throws the sand
const BURST_FRAME := 3 ## ear_burst f3 (0.49 s): the burst
const BOOM_CHARGE: Array[int] = [1, 2, 3] ## sonic_boom f1-f3: the charge, ears folded flat
const BOOM_BLAST_FRAME := 4 ## sonic_boom f4 (0.94 s): the blast
const DIG_GONE_FRAME := 5 ## dig f5 (0.71 s): under the ground
const POP_LAND_FRAME := 3 ## pop_out f3 (0.34 s): lands; f2 (0.21 s) is clear of the ground
const CAST_FRAME := 3 ## cast f3 (0.26 s): the brightest glow, where effects spawn (animation lane, 2026-11-05)
const BASIC_FROM := 2 ## the basic's swing starts at cast f2 (the arm coming forward) ...
const BASIC_WINDUP := 0.06 ## ... and fires on f3 this long after the press
const BASIC_RECOVER := 0.15 ## seconds after it fires that the swing ends (busy is let go): about cast f4
const BASIC_REACH_PAST := 1.2 ## metres the dart flies past basic_range, centre to centre (the two bodies' radii)
## The bolt by path, not by its class_name: a new class_name is unknown until the editor or an import refreshes
## the class cache, and naming it here broke this script (and arena_play with it) until then.
const Bolt := preload("res://scripts/moba3d/fennec_bolt.gd")
const Flash := preload("res://scripts/moba3d/blink_flash.gd") ## the blink flash, by path for the same reason
## Each effect texture's width over the length it is drawn for (tools/art/draw_fennec_kit_fx.py).
const RING_PAD := 1.02
const CHARGE_PAD := 1.033
const CORE_PAD := 1.05
const CONE_PAD := 1.011
const HOLE_M := 1.16 ## tunnel_hole.png, 58 texels at 50 a metre

@export_group("Placeholder lengths, not balance")
## Preston: "Also faster for sure" (2026-11-04, no number yet), so this is a placeholder. The trot is drawn planted at
## STRIDE (0.56 m/s) at 10 fps; the kit plays it faster to match (the player's full_speed_walk_rate = walk_speed /
## STRIDE, the animation lane's suggestion), so the feet stay planted: 1.0 m/s plays it at about 18 fps.
@export var walk_speed := 1.0
@export var hear_radius := 9.0
@export var ping_every := 0.6 ## seconds between pings on one moving enemy
@export var kick_range := 3.5 ## sand_cone is drawn for 3.5 m
@export var kick_half_angle := 35.0 ## degrees either side of the facing; sand_cone is drawn for 35
@export var kick_slow := 2.0 ## seconds slowed
@export var burst_range := 6.0
@export var burst_radius := 2.0 ## sound_ring is drawn for 2 m
@export var burst_core := 0.8 ## the centre that hits harder; burst_core.png is drawn for 0.8 m
@export var tunnel_length := 8.0
@export var tunnel_travel := 0.5 ## seconds underground
@export var tunnel_time := 4.0 ## seconds the tunnel stays open for allies once the fennec is out
@export var hole_radius := 0.7 ## an ally this close to the entrance drops in
@export var boom_range := 7.0 ## boom_wave is drawn for 7 m
@export var boom_half_angle := 40.0 ## boom_wave is drawn for 40
@export var boom_knock := 3.0
@export var cast_time := 0.5 ## only for an ability whose frames a sheet lacks
## Blink gate. PLACEHOLDERS, not Preston's numbers (the kit gives tiers only: cooldown short-medium, in MatchRules).
@export var blink_range := 4.0 ## metres
@export var gate_window := 3.0 ## seconds the gate stays open for the snap back
@export var bot_return_after := 1.5 ## seconds: a bot snaps back this long after blinking
## Gate cast. PLACEHOLDERS, not Preston's numbers.
@export var gate_behind := 1.1 ## metres behind the fennec the gate opens
@export var gate_hold := 0.8 ## seconds it stays open before closing
@export var bolt_speed := 12.0 ## metres a second
@export var bolt_reach := 7.0 ## metres
@export var bolt_slow := 1.5 ## seconds a struck enemy is slowed
@export var bolt_up := 0.45 ## metres off the floor the forward bolt leaves at (the backward one leaves the gate's middle)
## The basic attack. Every number here is a placeholder: range, cooldown and damage are the stand-in shot's it replaces
## (6 m edge to edge, 0.9 s, 30 a hit), so the fennec plays as it did until Preston sets its own.
@export var basic_range := 6.0 ## metres edge to edge (MatchTeams.edge_distance); the director and bots read it
@export var basic_cooldown := 0.9 ## seconds; the director sets it after each basic
@export var basic_damage := 30.0
@export var basic_speed := 14.0 ## metres a second

var current := "" ## the ability in progress, or ""
var heard := {} ## enemy -> how many times it has been pinged (the checks read it)
var last := {} ## what each ability reached the last time it was used, by ability name (the checks read it)
var tunnel_in := Vector3.ZERO
var tunnel_out := Vector3.ZERO
var tunnel_open := 0.0 ## seconds left that allies can travel through
var carried := [] ## allies the tunnel has brought through (the checks read it)
var _tunnel_live := false
var _holes := []
var _moves := {} ## enemy -> [where it was last frame, seconds since its last ping]
var _carrying := {}
var _was_shown := {} ## what was showing before it went underground
var _speed_before := -1.0
var _stride_before := -1.0
var _rate_before := -1.0
var gate_open := false ## the blink gate is up and a recast will snap back
var gate_pos := Vector3.ZERO ## where the blink started
var gate_left := 0.0 ## seconds left in the window
var _gate: Node3D = null ## the placeholder gate marker

@onready var player = get_parent() ## machine_test_player.gd
@onready var sprite: DirectionalSprite3D = get_parent().get_node("Sprite")


## Turns a field Player into the fennec: the fennec frames at size S, and this kit in place of whatever kit it had.
static func install(p: Node3D) -> FennecKit:
	var spr: DirectionalSprite3D = p.get_node("Sprite")
	spr.stop_action()
	spr.sprite_frames = FENNEC_FRAMES
	spr.canvas_height = CANVAS
	spr.feet_edge_row = FEET_EDGE_ROW
	spr.size_class = "S"
	spr.play(StringName("idle_" + spr.view))
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var kit := FennecKit.new()
	kit.name = "Kit"
	p.add_child(kit)
	if p.has_method("apply_size_class"):
		p.apply_size_class()
	return kit


static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


func _ready() -> void:
	if not ("move_speed" in player):  # a kit on its own (the sound lane's audio check): no machine to pace
		return
	_speed_before = player.move_speed
	_stride_before = player.stride_speed
	_rate_before = player.full_speed_walk_rate
	player.move_speed = walk_speed
	player.stride_speed = STRIDE
	player.full_speed_walk_rate = walk_speed / STRIDE


## The next machine gets its own pace back, and the fennec is never left hidden underground.
func _exit_tree() -> void:
	if _speed_before >= 0.0 and is_instance_valid(player):
		player.move_speed = _speed_before
		player.stride_speed = _stride_before
		player.full_speed_walk_rate = _rate_before
	if is_instance_valid(player):
		_set_shown(true)
	_close_tunnel()
	_close_gate()


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if k.physical_keycode == KEY_2 and gate_open and not player.get("bot"):
		gate_back()  # the recast: the slot's cooldown started with the blink, so it is not asked again
		return
	if k.physical_keycode == KEY_5 and not player.get("bot"):
		two_faced_shot()  # a preview key, outside the match's four slots and their cooldowns
		return
	if player.get("bot") or (player.has_method("slot_ready") and not player.slot_ready(str(k.physical_keycode - KEY_0))):
		return  # a bot's kit ignores the keyboard; in a match a slot waits out its cooldown (MatchRules)
	match k.physical_keycode:
		KEY_1:
			sand_kick()
		KEY_2:
			blink_gate()
		KEY_3:
			tunnel()
		KEY_4:
			sonic_boom()


func world() -> Node:
	return player.get_parent()


func targets() -> Array:
	return MatchTeams.enemies_of(player)


func allies() -> Array:
	return MatchTeams.allies_of(player).filter(func(a): return a != player)


func feet() -> Vector3:
	return player.global_position


func ahead() -> Vector3:
	var f: Vector3 = player.facing
	return Vector3(f.x, 0.0, f.z).normalized()


func _process(delta: float) -> void:
	if not (player is Node3D):  # a kit on its own (the sound lane's audio check) has no machine to listen from
		return
	_listen(delta)
	_tunnel_step(delta)
	_gate_step(delta)


# ---- passive, big ears ---------------------------------------------------------------------------------------------

## Pings each enemy that moved this frame within hear_radius, at most once every ping_every seconds.
func _listen(delta: float) -> void:
	for e in _moves.keys():
		if not is_instance_valid(e):
			_moves.erase(e)
	for e in targets():
		var rec: Array = _moves.get(e, [e.global_position, ping_every])
		var moved := flat(e.global_position - rec[0]).length() > 0.0005
		rec[0] = e.global_position
		rec[1] += delta
		if moved and rec[1] >= ping_every and flat(e.global_position - feet()).length() <= hear_radius and e.visible:
			rec[1] = 0.0
			heard[e] = heard.get(e, 0) + 1
			_flat_once("sound_ring", 6, e.global_position + Vector3.UP * 0.05, 1.4 * RING_PAD, 0.45, Vector3.ZERO, true)
		_moves[e] = rec


# ---- 1, sand kick --------------------------------------------------------------------------------------------------

func sand_kick() -> void:
	if not _begin("sand_kick"):
		return
	used.emit("1")
	await _at_frame("sand_kick", KICK_FRAME)
	var dir := ahead()
	_flat_once("sand_cone", 4, feet() + Vector3.UP * 0.04, kick_range * 2.0 * CONE_PAD, 0.45, dir)
	for k in [0.3, 0.6, 0.9]:  # billboards too, so the spray reads from a low camera
		Fx3D.spawn(world(), "dust_trail" if k < 0.5 else "impact_puff", feet() + dir * kick_range * k, 0.0)
	var hit := _in_cone(kick_range, kick_half_angle)
	for e in hit:
		e.hit(player)
		if e.has_method("slow"):
			e.slow(kick_slow)
		Fx3D.spawn(world(), "hit_spark", e.global_position + Vector3.UP * 0.7, 0.3)
	last["sand_kick"] = hit
	impact.emit(0.2)
	await _wait_end("sand_kick")
	_end()


# ---- 2, ear burst --------------------------------------------------------------------------------------------------

## at: the spot to burst; null picks the nearest enemy within burst_range, else burst_range ahead. A wall in between
## brings the spot back to the near side of it.
func ear_burst(at: Variant = null) -> void:
	if not _begin("ear_burst"):
		return
	used.emit("2")
	var spot: Vector3
	if at != null:
		spot = at
	else:
		var e := _nearest(targets(), burst_range)
		spot = e.global_position if e != null else feet() + ahead() * burst_range
	var d := flat(spot - feet())
	if d.length() > burst_range:
		d = d.normalized() * burst_range
	if d.length() > 0.05:
		player.facing = d.normalized()
	spot = feet() + d
	var wall := ArenaMotion.ray(player, feet() + Vector3.UP * 0.6, spot + Vector3.UP * 0.6)
	if not wall.is_empty():
		spot = flat(wall.position) - d.normalized() * 0.3 + Vector3.UP * feet().y
	await _at_frame("ear_burst", BURST_FRAME)
	_flat_once("sound_ring", 6, feet() + Vector3.UP * 0.05, 1.6 * RING_PAD, 0.3)  # the snap at the ears
	_flat_once("sound_ring", 6, spot + Vector3.UP * 0.05, burst_radius * 2.0 * RING_PAD, 0.5)
	Fx3D.ground_decal(world(), "burst_core.png", spot, burst_core * 2.0 * CORE_PAD, 0.7, 0.06)
	var core := []
	var edge := []
	for e in targets():
		var r := flat(e.global_position - spot).length()
		if r <= burst_core:
			core.append(e)
		elif r <= burst_radius:
			edge.append(e)
	for e in core + edge:
		e.hit(player)
		var s := Fx3D.spawn(world(), "hit_spark", e.global_position + Vector3.UP * 0.7, 0.3)
		if e in core:
			s.scale = Vector3.ONE * 1.6  # the harder hit
	last["ear_burst"] = {"spot": spot, "core": core, "edge": edge}
	impact.emit(0.35)
	await _wait_end("ear_burst")
	_end()


# ---- 2, blink gate -------------------------------------------------------------------------------------------------

## Blinks up to blink_range toward at (a spot or a node; null is straight ahead) and leaves a gate where it stood.
## The move is a wall-sliding shape cast (ArenaMotion), so it stops short of a wall and never lands in one.
## Returns false when it can't start (another ability running, or a gate already open).
func blink_gate(at: Variant = null) -> bool:
	if current != "" or gate_open:
		return false
	var start := feet()
	var want: Vector3 = start + ahead() * blink_range
	if at is Node3D:
		want = (at as Node3D).global_position
	elif at is Vector3:
		want = at
	var d := flat(want - start)
	if d.length() < 0.05:
		d = ahead() * blink_range
	d = d.limit_length(blink_range)
	player.facing = d.normalized()
	var r: float = player.body_radius() if player.has_method("body_radius") else 0.3
	var dest := ArenaMotion.slide(player, start, d, r)
	used.emit("2")
	var away: Node3D = Flash.play(world(), start, Flash.OUT, sprite)  # before the move: its ghost is the body here
	player.global_position = dest
	var land: Node3D = Flash.play(world(), dest, Flash.IN, sprite)
	gate_pos = start
	gate_left = gate_window
	gate_open = true
	_gate = _gate_marker(start, d.normalized())
	last["blink_gate"] = {"from": start, "to": dest, "wanted": d.length(), "flashes": [away, land]}
	impact.emit(0.2)
	return true


## The recast: inside the window, back through the gate to where the blink started. Once the window is over (or
## during another ability) it does nothing and returns false.
func gate_back() -> bool:
	if not gate_open or current != "":
		return false
	var from := feet()
	var away: Node3D = Flash.play(world(), from, Flash.OUT, sprite)
	player.global_position = Vector3(gate_pos.x, player.global_position.y, gate_pos.z)
	var land: Node3D = Flash.play(world(), feet(), Flash.IN, sprite)
	last["gate_back"] = {"from": from, "to": feet(), "flashes": [away, land]}
	_close_gate()
	impact.emit(0.2)
	return true


func _gate_step(delta: float) -> void:
	if not gate_open:
		return
	gate_left -= delta
	if player.get("bot") and gate_window - gate_left >= bot_return_after:
		gate_back()
	elif gate_left <= 0.0:
		_close_gate()


func _close_gate() -> void:
	gate_open = false
	gate_left = 0.0
	if is_instance_valid(_gate):
		_gate.close()  # plays its close, then frees itself
	_gate = null


## The small gate at the start point, held open until the recast or the window's end closes it. It faces the camera
## (SmallGate), so the blink's direction no longer turns it.
func _gate_marker(at: Vector3, _dir: Vector3) -> SmallGate:
	var g := SmallGate.open_at(world(), at, -1.0)
	g.name = "BlinkGate"
	g.set_meta("blink_gate", true)
	return g


# ---- 5, gate cast (preview of the 11-05 kit's gate) ----------------------------------------------------------------

## The cast pose; on its f3 the small gate opens gate_behind metres behind the fennec (short of a wall), holds gate_hold
## and closes by itself. at: a spot for the gate instead. last["gate_cast"] keeps the gate, its spot and the cast frame
## it opened on (the clip test reads them).
func gate_cast(at: Variant = null) -> void:
	if not _begin("cast"):
		return
	var t0 := Engine.get_process_frames()
	await _at_frame("cast", CAST_FRAME)
	var g := _gate_behind(at)
	last["gate_cast"] = {"gate": g, "at": g.global_position, "cast_frame": sprite.frame,
		"after_frames": Engine.get_process_frames() - t0}
	await _wait_end("cast")
	_end()


## The small gate gate_behind metres behind the fennec, short of a wall (or at a given spot), on the floor.
func _gate_behind(at: Variant = null) -> SmallGate:
	var spot: Vector3 = at if at is Vector3 else ArenaMotion.slide(player, feet(), -ahead() * gate_behind, 0.3)
	return SmallGate.open_at(world(), Vector3(spot.x, feet().y, spot.z), gate_hold)


# ---- 5, two-faced shot (the 11-05 kit's slot 1) ----------------------------------------------------------------------

## The cast; on its f3 a bolt forward and the gate behind; when the gate is open, a bolt backward out of it, the way
## the fennec faced at f3. last["two_faced_shot"] keeps the gate, the bolts, what they struck and the cast frame.
func two_faced_shot() -> void:
	if not _begin("cast"):
		return
	await _at_frame("cast", CAST_FRAME)
	var fwd := ahead()
	var g := _gate_behind()
	var rec := {"gate": g, "cast_frame": sprite.frame, "bolts": [], "struck": [], "ends": {}}
	last["two_faced_shot"] = rec
	rec["bolts"].append(_bolt(feet() + fwd * 0.35 + Vector3.UP * bolt_up, fwd, rec))
	g.opened.connect(func():
		if is_instance_valid(g) and is_instance_valid(player):
			rec["bolts"].append(_bolt(g.global_position + Vector3.UP * SmallGate.MID_UP, -fwd, rec)), CONNECT_ONE_SHOT)
	await _wait_end("cast")
	_end()


## A bolt that hits and slows what it strikes, and notes it in rec (ends: bolt number -> "target", "wall" or "reach").
func _bolt(from: Vector3, dir: Vector3, rec: Dictionary) -> Bolt:
	var b: Bolt = Bolt.fire(world(), from, dir, targets(), bolt_speed, bolt_reach)
	var i: int = rec["bolts"].size()
	b.ended.connect(func(_at: Vector3, why: String): rec["ends"][i] = why)
	b.struck.connect(func(e: Node3D):
		if not is_instance_valid(e):
			return
		e.hit(player)
		if e.has_method("slow"):
			e.slow(bolt_slow)
		rec["struck"].append(e)
		impact.emit(0.15))
	return b  # no used signal: slot 1's sounds are still the sand kick's (KitAudio)


# ---- basic attack (Preston, 2026-11-05: "we need basic attacks") -------------------------------------------------------

## The basic attack: a small violet dart toward the aim (the player: the mouse, else its facing; a bot: its target).
## Its swing is cast f2-f4 of the cast pose, a stand-in until the attack lane draws a basic of its own. The match
## director keeps the gates and the cooldown; this says no only while an ability is running or nothing gives an aim.
## last["basic_attack"] keeps the dart, what it struck and how it ended (the checks read it).
func basic_attack(target: Node3D) -> bool:
	if current != "" or not is_instance_valid(player):
		return false
	var dir := Vector3.ZERO
	if target != null and is_instance_valid(target):
		dir = flat(target.global_position - player.global_position)
	elif player.has_method("aim_dir"):
		dir = player.aim_dir()
	if dir.length() < 0.01 and "facing" in player:
		dir = flat(player.facing)
	if dir.length() < 0.01:
		return false
	dir = dir.normalized()
	current = "basic"
	player.busy = true
	if "facing" in player:
		player.facing = dir
	if _framed("cast"):
		sprite.play_action("cast")
		sprite.frame = BASIC_FROM
	cue.emit("basic_cast")
	_basic(dir)  # not awaited: it fires a moment later and lets go of busy on its own
	return true


func _basic(dir: Vector3) -> void:
	var rec := {"dart": null, "struck": [], "why": ""}
	last["basic_attack"] = rec
	await get_tree().create_timer(BASIC_WINDUP).timeout
	if not is_instance_valid(player) or current != "basic":
		return
	if _framed("cast") and sprite.action == "cast":
		sprite.frame = CAST_FRAME
	var d = Bolt.fire(world(), feet() + dir * 0.35 + Vector3.UP * bolt_up, dir, targets(), basic_speed,
		basic_range + BASIC_REACH_PAST, true)
	rec["dart"] = d
	d.ended.connect(func(_at: Vector3, why: String): rec["why"] = why)
	d.struck.connect(func(e: Node3D):
		if not is_instance_valid(e):
			return
		e.hit(player, basic_damage / MatchRules.kit_hit_damage)
		rec["struck"].append(e)
		cue.emit("basic_hit"))  # no impact shake: a ranged basic lands too often for one
	await get_tree().create_timer(BASIC_RECOVER).timeout
	if is_instance_valid(player) and current == "basic":
		_end()


# ---- 3, tunnel -----------------------------------------------------------------------------------------------------

## to: where the exit should be; null digs tunnel_length ahead. The route runs where the fennec could walk, so an arena
## wall stops it short (ArenaMotion).
func tunnel(to: Variant = null) -> void:
	if current != "":
		return
	current = "tunnel"
	player.busy = true
	used.emit("3")
	_close_tunnel()
	var start := feet()
	var want: Vector3 = to if to != null else start + ahead() * tunnel_length
	var d := flat(want - start)
	if d.length() > 0.05:
		player.facing = d.normalized()
	if _framed("dig"):
		sprite.play_action("dig")
	_holes.append(Fx3D.ground_decal(world(), "tunnel_hole.png", start, HOLE_M, 999.0, 0.03))
	Fx3D.spawn(world(), "dust_trail", start + ahead() * 0.3, 0.2)
	await _at_frame("dig", DIG_GONE_FRAME)
	_set_shown(false)
	Fx3D.spawn(world(), "impact_puff", start, 0.3)
	var t := 0.0
	var puff := 0.0
	while t < tunnel_travel:  # underground: a line of dust where it runs
		await get_tree().process_frame
		var dt := get_process_delta_time()
		t += dt
		puff += dt
		var p := start.lerp(start + d, minf(t / tunnel_travel, 1.0))
		player.global_position = ArenaMotion.slide(player, player.global_position, p - player.global_position, player.body_radius())
		if puff >= 0.06:
			puff = 0.0
			Fx3D.spawn(world(), "dust_trail", player.global_position, 0.0)
	var exit := feet()
	_holes.append(Fx3D.ground_decal(world(), "tunnel_hole.png", exit, HOLE_M, 999.0, 0.03))
	_set_shown(true)
	if _framed("pop_out"):
		sprite.play_action("pop_out")
	await _at_frame("pop_out", POP_LAND_FRAME)
	Fx3D.spawn(world(), "impact_puff", exit + ahead() * 0.3, 0.3)
	impact.emit(0.4)
	tunnel_in = start
	tunnel_out = exit
	tunnel_open = tunnel_time
	_tunnel_live = true
	last["tunnel"] = {"in": start, "out": exit}
	await _wait_end("pop_out")
	_end()


func _tunnel_step(delta: float) -> void:
	if not _tunnel_live:
		return
	tunnel_open -= delta
	if tunnel_open <= 0.0:
		_close_tunnel()
		return
	for a in allies():
		if not _carrying.has(a) and flat(a.global_position - tunnel_in).length() <= hole_radius:
			_carry(a)


## An ally drops into the entrance and comes up beside the exit, a step further on.
func _carry(a: Node3D) -> void:
	_carrying[a] = true
	if a.has_method("halt"):
		a.halt()
	Fx3D.spawn(world(), "impact_puff", tunnel_in, 0.2)
	a.visible = false
	var from := tunnel_in
	var to := tunnel_out
	await get_tree().create_timer(tunnel_travel).timeout
	if not is_instance_valid(a):
		return
	var on := flat(to - from).normalized() * 0.9
	a.global_position = ArenaMotion.slide(a, to, on, 0.35)
	a.visible = true
	Fx3D.spawn(world(), "impact_puff", to, 0.2)
	carried.append(a)
	_carrying.erase(a)


func _close_tunnel() -> void:
	_tunnel_live = false
	tunnel_open = 0.0
	for h in _holes:
		if is_instance_valid(h):
			var m: StandardMaterial3D = (h.mesh as PlaneMesh).material
			var tw: Tween = h.create_tween()
			tw.tween_property(m, "albedo_color:a", 0.0, 0.4)
			tw.tween_callback(h.queue_free)
	_holes.clear()


## Underground: the sprite, ring and shadow hide; coming up, each goes back to how it was (a reveal hides the ring).
func _set_shown(v: bool) -> void:
	if not v:
		_was_shown = {}
		for n in ["Sprite", "Ring", "Shadow"]:
			var m := player.get_node_or_null(n) as Node3D
			if m != null:
				_was_shown[n] = m.visible
				m.visible = false
		return
	for n in _was_shown:
		var m := player.get_node_or_null(n) as Node3D
		if m != null:
			m.visible = _was_shown[n]
	_was_shown = {}


# ---- 4, sonic boom -------------------------------------------------------------------------------------------------

func sonic_boom() -> void:
	if not _begin("sonic_boom"):
		return
	used.emit("4")
	for f in BOOM_CHARGE:  # the charge: rings drawn in to the ears
		await _at_frame("sonic_boom", f)
		_charge_ring()
	await _at_frame("sonic_boom", BOOM_BLAST_FRAME)
	var dir := ahead()
	var life := 0.5
	_flat_once("boom_wave", 6, feet() + Vector3.UP * 0.05, boom_range * 2.0 * CONE_PAD, life, dir)
	var hit := _in_cone(boom_range, boom_half_angle)
	var c := feet()
	for e in hit:  # each is hit as the wave reaches it
		var away := flat(e.global_position - c)
		var push := (away.normalized() if away.length() > 0.05 else dir) * boom_knock
		get_tree().create_timer(life * away.length() / boom_range).timeout.connect(func():
			if is_instance_valid(e):
				e.knock_aside(push, 0.35)
				Fx3D.spawn(world(), "hit_spark", e.global_position + Vector3.UP * 0.7, 0.3))
	last["sonic_boom"] = hit
	impact.emit(0.8)
	await _wait_end("sonic_boom")
	_end()


func _charge_ring() -> void:
	var f = Fx3D.spawn_flat(world(), "charge_ring", 1, feet() + Vector3.UP * 0.05, 2.4 * CHARGE_PAD)
	f.mat.albedo_color.a = 0.0
	var tw: Tween = f.create_tween().set_parallel()
	tw.tween_property(f, "scale", Vector3.ONE * 0.25, 0.22)
	tw.tween_property(f.mat, "albedo_color:a", 1.0, 0.1)
	tw.chain().tween_callback(f.queue_free)


# ---- shared --------------------------------------------------------------------------------------------------------

## A flat effect that plays its frames once over `life`, then frees itself. dir turns a cone to point that way;
## through_walls draws it over everything (the passive's pings).
func _flat_once(anim: String, count: int, pos: Vector3, width: float, life: float, dir := Vector3.ZERO,
		through_walls := false) -> Node3D:
	var f = Fx3D.spawn_flat(world(), anim, count, pos, width, count / life)
	if dir != Vector3.ZERO:
		f.rotation.y = atan2(-dir.x, -dir.z)  # the texture opens toward the plane's -z
	if through_walls:
		f.mat.no_depth_test = true
		f.mat.render_priority = 1
	var tw: Tween = f.create_tween()
	tw.tween_interval(life)
	tw.tween_callback(f.queue_free)
	return f


## Enemies inside the cone ahead (reach r, half_deg either side) with no arena wall between.
func _in_cone(r: float, half_deg: float) -> Array:
	var out := []
	var min_dot := cos(deg_to_rad(half_deg))
	for e in targets():
		var d := flat(e.global_position - feet())
		if d.length() > r:
			continue
		if d.length() > 0.05 and d.normalized().dot(ahead()) < min_dot:
			continue
		if ArenaMotion.ray(player, feet() + Vector3.UP * 0.6, e.global_position + Vector3.UP * 0.6).is_empty():
			out.append(e)
	return out


func _nearest(list: Array, r: float) -> Node3D:
	var best: Node3D = null
	var best_d := r
	for a in list:
		var d := flat(a.global_position - feet()).length()
		if d <= best_d:
			best = a
			best_d = d
	return best


func _framed(anim: String) -> bool:
	return sprite.sprite_frames.has_animation(anim + "_s")


func _begin(anim: String) -> bool:
	if current != "":
		return false
	current = anim
	player.busy = true
	if _framed(anim):
		sprite.play_action(anim)
	return true


func _end() -> void:
	current = ""
	player.busy = false
	sprite.stop_action()


## Until frame f of the action, or cast_time when the sheet has no frames for it.
func _at_frame(anim: String, f: int) -> void:
	if _framed(anim):
		while sprite.action == anim and sprite.frame < f and sprite.is_playing():
			await get_tree().process_frame
	else:
		await get_tree().create_timer(cast_time).timeout


func _wait_end(anim: String) -> void:
	while sprite.action == anim and sprite.is_playing():
		await get_tree().process_frame
