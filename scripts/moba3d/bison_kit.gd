class_name BisonKit
extends Node
## The bison's kit on its rigged 3D body (game feel lane, 2026-11-14). Design: docs/plan/moba-kits.md, Bison, the
## Whistle Stop refine (Preston, 2026-11-14: "Whistle Stop"; rebuilt on his "Yes, rebuild it"). Effects: bison_fx.gd
## (the bison effects lane), cue contracts in docs/reference/bison-fx-synthesis-2026-11-13.md. Clips: the bison 3D lane's
## r6 (Haul is the hauling trot). Names and numbers are placeholders.
##
## - Basic, horn hook: Hook_Right and Hook_Left in turn. On the clip's "hit" event the nearest enemy (machines before
##   minions) within basic_range (the bison's centre to the enemy's edge) and hook_half_angle of the swing takes
##   hook_damage, x scorch_bonus when it is burning (scorched). With nothing in reach it still swings.
## - Passive, Scorch and Steam: the chain and the scald burn enemies (burn_dps, and they count as scorched). While it
##   hauls it builds steam: 0 to 1 over steam_build, walking at move_speed x speed_factor() (items and boosts count in
##   full) x 1 to steam_cap. The Haul clip plays at ground speed / haul_trot_speed.
## - 1, Coupling Chain: the Chain_Throw clip. On "fire" the nearest enemy within chain_range (centre to its edge) inside
##   chain_cone of the aim, with a clear line, is caught couple_delay later: chain_damage, and coupled for couple_time
##   (it burns and carries the meta "coupled_by"). Past chain_length the chain goes taut and tows it, so a dash or leap
##   goes only as far as the slack; chain_snap past that (a teleport) breaks it.
##   Recast to Haul (haul()): it turns toward the aim and hauls for up to chain_haul_time (a recast ends it early),
##   dragging the coupled enemy behind it. At the end the enemy hits the rear buffers: buffer_stun. A stun or knock-up
##   on the bison snaps the chain.
## - 2, Whistle Stop: the Whistle clip. On "blast" every ally whose edge is within whistle_radius runs whistle_boost
##   faster for whistle_time while it moves toward the bison, and every enemy within scald_radius (centre to its edge)
##   takes scald_damage and burns for scald_burn.
## - 3, Plow: the Plow clip. On "hit" every enemy within plow_reach (centre to its edge) and plow_half_angle of the sweep
##   takes plow_damage, is scorched, and is thrown plow_throw to the bison's left (the head sweeps right to left); a
##   coupled enemy is thrown to the far end of its chain instead.
## - 4, Freight: Freight_Brace, then Haul held. On "chains_out" one chain fires freight_line along the aim (cut short at
##   a wall) and every enemy within freight_width of the line (to its edge), with a clear line, joins freight_targets,
##   nose to tail (index 0 rides right behind the bison); couple_delay later each takes freight_damage and is coupled.
##   At "braced" the bison turns toward the move input (steer_to for bots and probes; away from the train with none)
##   and hauls for haul_time, turning at most haul_turn, the cars pulled into a line behind it (freight_length, then
##   freight_gap apart) and a continuous slag track laid behind it. A recast or the end brakes: the pile-up stuns
##   every car pile_stun. Not unstoppable: a stun or knock-up on the bison snaps the train (freight_snap, no pile-up).
##   With no car caught there is no haul.
##
## bison_fx.gd reads stack_slot, chain_target, chain_end, chain_length, plow_radius, plow_targets, freight_targets,
## slag_time, slag_spots, whistle_radius, scald_radius, scald_targets and steam, and the body's events. Keep these names.

signal impact(strength: float) ## something landed; KitFeel shakes the camera on it
signal used(slot: String) ## the director starts the slot's cooldown (MatchRules)
signal cue(name: String) ## whistle, scald (scald_targets); chain_fire, chain_couple, chain_miss, chain_break (chain_target, chain_end); haul, buffer_slam (chain_target); plow, plow_hit (plow_targets); freight, freight_chains (freight_targets), slag (slag_spots), pile_up, freight_snap

const FX_SCRIPT := "res://scripts/moba3d/bison_fx.gd"
const SPARK_UP := 0.9
const HAUL_CLIP := "Haul"

@export var basic_range := 2.2 ## metres from the bison's centre to the target's edge (MatchTeams.edge_distance; the director reads it)
@export var basic_cooldown := 1.1 ## seconds (the director reads it)
@export var hook_half_angle := 60.0
@export var hook_damage := 40.0
@export var scorch_bonus := 1.3 ## a hook on a burning (scorched) enemy
@export var scorch_time := 3.0
@export var burn_dps := 10.0 ## a burning enemy (the chain, the scald) loses this a second
@export var steam_build := 2.0 ## seconds of hauling to full steam
@export var steam_cap := 1.4 ## the haul's walk at full steam, x the bison's move speed
@export var haul_trot_speed := 3.407 ## m/s the Haul clip is authored at (bison 3D lane, r6)
@export var haul_turn := 50.0 ## degrees a second
@export var car_pull := 8.0 ## m/s a hauled enemy is pulled toward its place behind the bison
@export var freight_length := 2.6 ## metres from the bison's centre back to the first car's
@export var freight_gap := 1.7 ## metres between cars
@export var chain_range := 9.0 ## metres from the bison's centre to the target's edge (MatchTeams.edge_distance)
@export var chain_cone := 35.0 ## degrees, the whole cone the chain picks in
@export var chain_length := 9.0 ## metres centre to centre; past it the chain goes taut and tows
@export var chain_snap := 4.0 ## metres past chain_length that break the chain
@export var couple_delay := 0.09 ## seconds from fire to the catch (bison_fx's reach)
@export var couple_time := 3.0 ## seconds a slot 1 chain holds unless it is hauled
@export var chain_damage := 25.0
@export var chain_haul_time := 1.5 ## the longest slot 1's Haul runs
@export var buffer_stun := 0.8
@export var whistle_radius := 9.0 ## metres from the bison's centre to an ally's edge (bison_fx reads it)
@export var whistle_boost := 1.3
@export var whistle_time := 3.0
@export var scald_radius := 3.0 ## metres from the bison's centre to an enemy's edge (bison_fx reads it)
@export var scald_damage := 40.0
@export var scald_burn := 3.0 ## seconds a scald burns
@export var plow_reach := 3.0 ## metres from the bison's centre to the target's edge: the scorch band's outer edge (bison_fx, measured)
@export var plow_half_angle := 70.0
@export var plow_damage := 55.0
@export var plow_throw := 2.5 ## metres to the bison's left
@export var plow_throw_time := 0.32
@export var plow_chain_throw_time := 0.5 ## a coupled enemy flies to the far end of its chain
@export var freight_line := 12.0 ## metres along the aim from the bison's centre
@export var freight_width := 1.0 ## metres from the line to an enemy's edge
@export var freight_damage := 30.0 ## each car's catch
@export var haul_time := 2.0 ## the longest Freight hauls (Preston, 2026-11-16: "Cut to 2 s"; 4 s dragged a train about 18 m)
@export var pile_stun := 1.0
@export var slag_time := 4.5 ## bison_fx reads it
@export var slag_dps := 12.0
@export var haul_slag_every := 0.6 ## seconds between laid segments of Freight's track (a "slag" cue each)
@export var haul_slag_radius := 0.6 ## metres either side of the track's centre line: the strip is 1.2 m wide
@export var fx_on := false ## bison_fx is hung by the effects lane's installer (arena_play.tscn); this stays off

## Each stack belongs to one ability and goes dark while it cools; bison_fx reads this with the player's cooldowns.
var stack_slot := {"fl": "1", "fr": "2", "rl": "3", "rr": "4"}
var current := "" ## the arena's swap guard reads this (arena_play)
var busy_with := ""
var slag: Array = [] ## live track segments: {"from": Vector3, "at": Vector3, "until": float, "r": float}, a capsule from "from" to "at"
var chain_target: Node3D = null
var chain_end := Vector3.ZERO
var plow_radius := 2.4
var plow_targets: Array = []
var freight_targets: Array = [] ## nose to tail: index 0 rides right behind the bison
var scald_targets: Array = []
var whistled_last: Array = [] ## the allies the last whistle called, for the checks
var coupled := {} ## enemy -> _clock time its chain breaks
var braced := false ## always false now (machine_test_player._braced reads it): Freight is no longer unstoppable
var hauling := false
var haul_kind := "" ## "haul" (slot 1) or "freight" while hauling
var steam := 0.0 ## 0 to 1 while hauling; bison_fx speeds the chuff with it
var steer_to := Vector3.ZERO ## bots and probes steer a haul with this; the player with the move input
var slag_spots: Array = [] ## the end of the segment just laid, set before a "slag" cue
var _slag_live = null ## the segment still being laid: its "at" follows the bison's rear until it is laid down
var hook_side := "" ## the last hook's clip, for the checks
var hook_target: Node3D = null ## the last hook's victim, for the checks
var _freight := {} ## hauled enemy -> its place in the line (0 first)
var _stop := false ## a recast brakes the haul
var _whistled := {} ## ally -> _clock time the call ends
var _burn_until := {} ## enemy -> _clock time its burn ends
var _hook_right := false
var _scorch_until := {} ## enemy -> _clock time the scorch runs out
var _clock := 0.0
var _ev_body: MechModel3D = null
var _got: Dictionary = {}
var _fx_hung := false

@onready var player = get_parent() ## machine_test_player.gd


## Turns a field Player into the bison. Loaded by path, not by class_name (the fennec kit's note on the class cache).
static func install(p: Node3D) -> Node:
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var spr: Variant = p.get("sprite")
	if spr != null and spr.has_method("stop_action"):
		spr.stop_action()
	var kit: Node = load("res://scripts/moba3d/bison_kit.gd").new()
	kit.name = "Kit"
	p.add_child(kit)
	return kit


static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


## Slag patches, burns and the whistle's call.
func _process(delta: float) -> void:
	_clock += delta
	if not is_instance_valid(player):
		return
	var hot := {}
	for i in range(slag.size() - 1, -1, -1):
		var s: Dictionary = slag[i]
		if _clock >= float(s.until):
			slag.remove_at(i)
			continue
		for e in MatchTeams.enemies_of(player):
			if not hot.has(e) and is_instance_valid(e) and MatchTeams.hittable(e) and _on_slag(s, e.global_position, _r(e)):
				hot[e] = true
	for e in hot:  # once a frame however many segments touch it, so a joint does not burn double
		scorch(e)
		if e.has_method("take_damage"):
			e.take_damage(slag_dps * delta, player)
	for e in _burn_until.keys():
		if not MatchTeams.hittable(e) or _clock >= float(_burn_until[e]):
			_burn_until.erase(e)
			continue
		scorch(e)
		if e.has_method("take_damage"):
			e.take_damage(burn_dps * delta, player)
	for m in _whistled.keys():
		if not is_instance_valid(m) or not m.get("alive") or _clock >= float(_whistled[m]):
			_whistled.erase(m)
			continue
		var to := flat(player.global_position - m.global_position)
		var go: Vector3 = flat(m.move_dir()) if m.has_method("move_dir") else Vector3.ZERO
		if to.length() > 0.5 and go.length() > 0.1 and go.normalized().dot(to.normalized()) > 0.0:
			m.boost(whistle_boost, 0.15, &"whistle_stop")  # refreshed while it heads in, gone 0.15 s after it turns away


## Chains: break on time, death or a snap; tow past chain_length; pull hauled enemies into line; burn the coupled.
func _physics_process(delta: float) -> void:
	if coupled.is_empty():
		return
	if not is_instance_valid(player) or not player.alive:
		_break_all()
		return
	for t in coupled.keys():
		if not MatchTeams.hittable(t) or _clock >= float(coupled[t]):
			_break(t)
			continue
		var to := flat(t.global_position - player.global_position)
		var d := to.length()
		if d > chain_length + chain_snap:
			_break(t)
			continue
		if hauling and _freight.has(t):
			if not _thrown(t):  # pulled toward its place in the line behind the hauler
				var back := flat(player.facing).normalized()
				var spot: Vector3 = player.global_position - back * (freight_length + float(_freight[t]) * freight_gap)
				var go := flat(spot - t.global_position)
				var step := minf(go.length(), car_pull * delta)
				if step > 0.005:
					t.global_position = ArenaMotion.slide(t, t.global_position, go.normalized() * step, _r(t))
		elif d > chain_length and not _thrown(t):  # taut: a dash or leap goes only as far as the slack
			t.global_position = ArenaMotion.slide(t, t.global_position, -to.normalized() * (d - chain_length), _r(t))
		burn(t, 0.1)


## The next machine is never left busy by a cast cut short, and no enemy stays coupled.
func _exit_tree() -> void:
	if is_instance_valid(player) and busy_with != "":
		player.busy = false
	busy_with = ""
	current = ""
	hauling = false
	for t in coupled.keys():
		if is_instance_valid(t) and t.has_meta("coupled_by"):
			t.remove_meta("coupled_by")
	coupled.clear()


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo or not is_instance_valid(player) or player.get("bot"):
		return
	if k.physical_keycode < KEY_1 or k.physical_keycode > KEY_4:
		return
	var slot := str(k.physical_keycode - KEY_0)
	if hauling and ((slot == "1" and haul_kind == "haul") or (slot == "4" and haul_kind == "freight")):
		brake()  # the recast brakes
		return
	if player.has_method("slot_ready") and not player.slot_ready(slot) and not (slot == "1" and haul_ready()):
		return  # in a match a slot waits out its cooldown (MatchRules); the Haul recast does not
	match k.physical_keycode:
		KEY_1:
			chain()
		KEY_2:
			whistle()
		KEY_3:
			plow()
		KEY_4:
			freight()


# ---- the 3D body ---------------------------------------------------------------------------------------------------

## The rigged body once the match has attached it (use_model runs after install), or null. Hangs the effects once.
func _body() -> MechModel3D:
	var b: Variant = player.get("body") if is_instance_valid(player) else null
	if not (b is MechModel3D) or not is_instance_valid(b) or not b.has_clip(HAUL_CLIP):
		return null
	if _ev_body != b:
		_ev_body = b
		b.event.connect(_on_body_event.bind(b))
	if fx_on and not _fx_hung:
		_fx_hung = true
		var script: Variant = load(FX_SCRIPT) if ResourceLoader.exists(FX_SCRIPT) else null
		if script is Script and script.can_instantiate():  # an effects file that fails to compile is skipped, not fatal
			var fx: Node = script.new()
			fx.name = "BisonFx"
			player.add_child(fx)
			if fx.has_method("setup"):
				fx.setup(self, player)
	return b


func _on_body_event(clip: String, n: String, _damage: bool, b: MechModel3D) -> void:
	if b == _ev_body:
		_got[clip + "/" + n] = int(_got.get(clip + "/" + n, 0)) + 1


func _play(b: MechModel3D, clip: String, speed := 1.0) -> void:
	for k in _got.keys():
		if String(k).begins_with(clip + "/"):
			_got.erase(k)
	b.play_action(clip, speed)


## Waits for the body's clip to fire event n. False when the clip ended or was replaced first, or the bison died.
func _event(b: MechModel3D, clip: String, n: String) -> bool:
	while is_instance_valid(b) and player.alive and int(_got.get(clip + "/" + n, 0)) < 1:
		if b.action != clip:
			return false
		await get_tree().process_frame
	return is_instance_valid(b) and player.alive and int(_got.get(clip + "/" + n, 0)) >= 1


func _clip_end(b: MechModel3D, clip: String) -> void:
	while is_instance_valid(b) and b.action == clip and player.alive:
		await get_tree().process_frame


func _start(clip: String, dir: Vector3) -> void:
	busy_with = clip
	current = clip
	player.busy = true
	player.facing = dir


func _finish(clip: String) -> void:
	if busy_with == clip:
		busy_with = ""
		current = ""
		if is_instance_valid(player):
			player.busy = false


## True when the bison can start a cast now.
func _free() -> bool:
	return busy_with == "" and is_instance_valid(player) and player.alive and not player.has_meta("held_by") \
			and float(player.get("stunned")) <= 0.0


func _aim(target: Variant) -> Vector3:
	var d := Vector3.ZERO
	if target is Node3D and is_instance_valid(target):
		d = flat(target.global_position - player.global_position)
	elif target is Vector3:
		d = flat(target - player.global_position)
	elif player.has_method("aim_dir"):
		d = player.aim_dir()
	if d.length() < 0.01:
		d = flat(player.facing)
	return d.normalized() if d.length() > 0.01 else Vector3.FORWARD


func _r(e: Node3D) -> float:
	return float(e.radius()) if e.has_method("radius") else 0.5


func _hit(victim: Node3D, damage: float, dir: Vector3, shake: float) -> void:
	if damage > 0.5:
		if victim.has_method("hit"):
			victim.hit(player, damage / MatchRules.kit_hit_damage)
		elif victim.has_method("take_damage"):
			victim.take_damage(damage, player)
	Fx3D.spawn(player.get_parent(), "hit_spark", victim.global_position - dir * _r(victim) + Vector3.UP * SPARK_UP, 0.0)
	impact.emit(shake)


func _stun(e: Node3D, t: float) -> void:
	if MatchTeams.hittable(e) and e.has_method("stun"):
		e.stun(t)


# ---- passive: scorch and steam -------------------------------------------------------------------------------------

## Marks an enemy as scorched (burning, for the hook's bonus) for scorch_time; a second mark refreshes it.
func scorch(e: Node3D) -> void:
	_scorch_until[e] = _clock + scorch_time


func scorched(e: Node3D) -> bool:
	return is_instance_valid(e) and _clock < float(_scorch_until.get(e, -1.0))


## Burns an enemy for t seconds at burn_dps (a longer burn already running is kept).
func burn(e: Node3D, t: float) -> void:
	_burn_until[e] = maxf(float(_burn_until.get(e, 0.0)), _clock + t)
	scorch(e)


## The haul's walk: the bison's move speed with every speed change on it (items count in full), x the steam.
func haul_speed() -> float:
	var f: float = player.speed_factor() if player.has_method("speed_factor") else 1.0
	return float(player.get("move_speed")) * f * lerpf(1.0, steam_cap, steam)


## Hauls for up to time seconds: steam builds, the bison walks haul_speed() along its facing, steered by steer_to or
## the move input (at most haul_turn a second), and Freight drops slag. Ends early on a brake(). True if a stun or a
## knock-up on the bison snapped it.
func _run_haul(b: MechModel3D, kind: String, time: float) -> bool:
	hauling = true
	haul_kind = kind
	steam = 0.0
	_stop = false
	b.play_hold(HAUL_CLIP, haul_speed() / haul_trot_speed)
	var left := time
	var on := 0.0
	var next_slag := haul_slag_every * 0.25
	var snapped := false
	if kind == "freight":
		_slag_start()
	while left > 0.0 and not _stop:
		await get_tree().process_frame
		if not is_instance_valid(player) or not player.alive:
			break
		if float(player.get("stunned")) > 0.0 or (player.has_method("_forced") and player._forced()):
			snapped = true
			break
		if kind == "freight" and float(player.get("grounded")) > 0.0:
			break  # grounded (the rhino's Aftershock, 2026-11-20): Freight stops as if it ran out; the Chain haul goes on
		var dt := get_process_delta_time()
		left -= dt
		on += dt
		steam = minf(1.0, steam + dt / steam_build)
		var v := haul_speed()
		_haul_step(dt, v)
		if is_instance_valid(b) and b.action == HAUL_CLIP:
			b.set_action_rate(v / haul_trot_speed)
		if kind == "freight":
			_slag_follow()
			if on >= next_slag:
				next_slag += haul_slag_every
				_haul_slag()
	if kind == "freight":
		_slag_end()
	hauling = false
	haul_kind = ""
	steam = 0.0
	_stop = false
	if is_instance_valid(b) and b.action == HAUL_CLIP:
		b.stop_action()  # bison_fx: ends the chuff
	return snapped


func _haul_step(dt: float, v: float) -> void:
	var want := _steer()
	var f := flat(player.facing).normalized()
	if want.length() >= 0.1:
		var cap := deg_to_rad(haul_turn) * dt
		f = f.rotated(Vector3.UP, clampf(f.signed_angle_to(want.normalized(), Vector3.UP), -cap, cap)).normalized()
	player.facing = f
	player.global_position = ArenaMotion.slide(player, player.global_position, f * v * dt, _r(player))


func _steer() -> Vector3:
	var want := steer_to
	if want == Vector3.ZERO and player.has_method("move_dir"):
		want = player.move_dir()
	return flat(want)


## Ends a haul early (the recast of 1 during the Haul, of 4 during Freight). True if a haul was running.
func brake() -> bool:
	if not hauling:
		return false
	_stop = true
	return true


# ---- basic: horn hook ------------------------------------------------------------------------------------------------

## Swings a horn hook toward the target (a bot's pick) or the aim. True if it swung; the director keeps the cooldown.
func basic_attack(target: Node3D = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or player.busy or not player.alive \
			or player.has_meta("held_by") or b.action != "":
		return false
	var dir := _aim(target)
	_hook_right = not _hook_right
	var clip := "Hook_Right" if _hook_right else "Hook_Left"
	hook_side = clip
	hook_target = null
	player.facing = dir
	_play(b, clip)
	_swing(b, clip, dir, target)
	return true


func _swing(b: MechModel3D, clip: String, dir: Vector3, target: Node3D) -> void:
	if not await _event(b, clip, "hit"):
		return
	var t: Node3D = target if MatchTeams.hittable(target) and _in_hook(target, dir) else _hook_pick(dir)
	hook_target = t
	if t != null:
		_hit(t, hook_damage * (scorch_bonus if scorched(t) else 1.0), dir, 0.25)


func _in_hook(e: Node3D, dir: Vector3) -> bool:
	if MatchTeams.edge_distance(player, e) > basic_range:
		return false
	var to := flat(e.global_position - player.global_position)
	return to.length() < 0.3 or to.normalized().dot(dir) >= cos(deg_to_rad(hook_half_angle))


## The nearest enemy in the hook's arc, machines before minions.
func _hook_pick(dir: Vector3) -> Node3D:
	var best: Node3D = null
	var best_key := INF
	for e in MatchTeams.enemies_of(player):
		if not is_instance_valid(e) or not MatchTeams.hittable(e) or not _in_hook(e, dir):
			continue
		var key: float = MatchTeams.edge_distance(player, e) + (100.0 if e.get("kind") == "minion" else 0.0)
		if key < best_key:
			best_key = key
			best = e
	return best


# ---- 1, Coupling Chain, then Haul ----------------------------------------------------------------------------------

## True while the recast would Haul: an enemy is on a slot 1 chain and the bison is free.
func haul_ready() -> bool:
	return _free() and not hauling and _haul_target() != null


func _haul_target() -> Node3D:
	for t in coupled.keys():
		if MatchTeams.hittable(t):
			return t
	return null


## Throws the red-hot chain toward the target (a bot's pick) or the aim; with an enemy coupled it Hauls instead. True if
## it started.
func chain(target: Variant = null) -> bool:
	if haul_ready():
		return haul(target)
	var b := _body()
	if b == null or not _free():
		return false
	used.emit("1")
	var dir := _aim(target)
	_start("Chain_Throw", dir)
	_play(b, "Chain_Throw")
	_chain_rest(b, dir)
	return true


func _chain_rest(b: MechModel3D, dir: Vector3) -> void:
	if await _event(b, "Chain_Throw", "fire"):
		var t := _chain_pick(dir)
		chain_target = t
		chain_end = t.global_position if t != null else player.global_position + dir * (chain_range + _r(player))
		cue.emit("chain_fire")
		await get_tree().create_timer(couple_delay).timeout
		if MatchTeams.hittable(t) and is_instance_valid(player) and player.alive:
			_couple(t, dir)
		else:
			chain_target = null
			cue.emit("chain_miss")
	await _clip_end(b, "Chain_Throw")
	_finish("Chain_Throw")


## The nearest enemy in the chain's cone and reach with a clear line, or null.
func _chain_pick(dir: Vector3) -> Node3D:
	var best: Node3D = null
	var best_d := INF
	var cos_cone := cos(deg_to_rad(chain_cone * 0.5))
	for e in MatchTeams.enemies_of(player):
		if not MatchTeams.hittable(e):
			continue
		var d: float = MatchTeams.edge_distance(player, e)
		var to := flat(e.global_position - player.global_position)
		if d > chain_range or (to.length() > 0.3 and to.normalized().dot(dir) < cos_cone):
			continue
		if d < best_d and MatchTeams.clear_line(player, player.global_position, e.global_position):
			best_d = d
			best = e
	return best


func _couple(t: Node3D, dir: Vector3) -> void:
	coupled[t] = _clock + couple_time
	t.set_meta("coupled_by", player)
	chain_target = t
	burn(t, 0.1)
	_hit(t, chain_damage, dir, 0.2)
	cue.emit("chain_couple")


## The recast: turns toward the target (a bot's pick) or the aim and hauls the coupled enemy, then the buffer slam.
## True if it started.
func haul(target: Variant = null) -> bool:
	var b := _body()
	var t := _haul_target()
	if b == null or t == null or not _free() or hauling:
		return false
	_start("Haul", _aim(target))
	coupled[t] = INF  # held for the whole haul
	_freight = {t: 0}
	chain_target = t
	cue.emit("haul")
	_haul_rest(b, t)
	return true


func _haul_rest(b: MechModel3D, t: Node3D) -> void:
	var snapped := await _run_haul(b, "haul", chain_haul_time)
	_freight.clear()
	if not snapped and coupled.has(t) and MatchTeams.hittable(t) and is_instance_valid(player) and player.alive:
		var back := flat(player.facing).normalized()
		var spot: Vector3 = player.global_position - back * (_r(player) + _r(t) + 0.1)
		t.global_position = ArenaMotion.slide(t, t.global_position, flat(spot - t.global_position), _r(t))
		_stun(t, buffer_stun)
		chain_target = t
		_hit(t, 0.0, -back, 0.35)
		cue.emit("buffer_slam")
	if coupled.has(t):
		_break(t)
	_finish("Haul")


func _break(t: Variant) -> void:
	coupled.erase(t)
	_freight.erase(t)
	var ok := is_instance_valid(t)
	if ok and t.has_meta("coupled_by"):
		t.remove_meta("coupled_by")
	if ok or coupled.is_empty():
		chain_target = t if ok else null  # null: bison_fx ends every chain
		cue.emit("chain_break")


## Ends every chain at once (bison_fx: chain_break with a null target drops them all).
func _break_all() -> void:
	var had := not coupled.is_empty()
	for t in coupled.keys():
		if is_instance_valid(t) and t.has_meta("coupled_by"):
			t.remove_meta("coupled_by")
	coupled.clear()
	_freight.clear()
	if had:
		chain_target = null
		cue.emit("chain_break")


## True while a knock or toss tween is moving the unit (the tow waits for it).
func _thrown(t: Node) -> bool:
	var tw: Variant = t.get("_move_tw")
	return tw is Tween and tw.is_valid() and tw.is_running()


# ---- 2, Whistle Stop -----------------------------------------------------------------------------------------------

## The whistle and the four steam columns: allies near run in faster, enemies close are scalded. True if it started.
func whistle(_target: Variant = null) -> bool:
	var b := _body()
	if b == null or not _free():
		return false
	used.emit("2")
	var dir := flat(player.facing)
	_start("Whistle", dir.normalized() if dir.length() > 0.01 else Vector3.FORWARD)
	scald_targets = []
	whistled_last = []
	cue.emit("whistle")  # bison_fx times the columns from the clip's events (inhale, blast, plume_end)
	_play(b, "Whistle")
	_whistle_rest(b)
	return true


func _whistle_rest(b: MechModel3D) -> void:
	if await _event(b, "Whistle", "blast"):
		var here: Vector3 = player.global_position
		for m in player.get_parent().get_children():
			if m == player or not (m is Node3D) or not m.has_method("boost") or m.get("team") != player.team \
					or not m.get("alive"):
				continue
			if flat(m.global_position - here).length() - _r(m) <= whistle_radius:
				_whistled[m] = _clock + whistle_time
				whistled_last.append(m)
		for e in MatchTeams.enemies_of(player):
			if MatchTeams.hittable(e) and MatchTeams.edge_distance(player, e) <= scald_radius:
				scald_targets.append(e)
		for e in scald_targets:
			var to := flat(e.global_position - here)
			_hit(e, scald_damage, to.normalized() if to.length() > 0.01 else Vector3.FORWARD, 0.0)
			burn(e, scald_burn)
		impact.emit(0.3)
		cue.emit("scald")
	await _clip_end(b, "Whistle")
	_finish("Whistle")


# ---- 3, Plow ---------------------------------------------------------------------------------------------------------

## The hump-powered head sweep toward the target (a bot's pick) or the aim. True if it started.
func plow(target: Variant = null) -> bool:
	var b := _body()
	if b == null or not _free():
		return false
	used.emit("3")
	var dir := _aim(target)
	_start("Plow", dir)
	plow_targets = []
	cue.emit("plow")
	_play(b, "Plow")
	_plow_rest(b, dir)
	return true


func _plow_rest(b: MechModel3D, dir: Vector3) -> void:
	if await _event(b, "Plow", "hit"):
		plow_targets = _plow_pick(dir)
		cue.emit("plow_hit")
		var left := Vector3.UP.cross(dir).normalized()  # the head sweeps right to left (bison_fx, measured)
		for e in plow_targets:
			var on_chain := coupled.has(e)
			_hit(e, plow_damage, dir, 0.35)
			scorch(e)
			if on_chain:
				_throw(e, player.global_position + left * (chain_length - 0.2), plow_chain_throw_time)
			else:
				_throw(e, e.global_position + left * plow_throw, plow_throw_time)
	await _clip_end(b, "Plow")
	_finish("Plow")


func _plow_pick(dir: Vector3) -> Array:
	var out: Array = []
	var cos_arc := cos(deg_to_rad(plow_half_angle))
	for e in MatchTeams.enemies_of(player):
		if not MatchTeams.hittable(e) or MatchTeams.edge_distance(player, e) > plow_reach:
			continue
		var to := flat(e.global_position - player.global_position)
		if to.length() < 0.3 or to.normalized().dot(dir) >= cos_arc:
			out.append(e)
	return out


func _throw(e: Node3D, land: Vector3, time: float) -> void:
	if not is_instance_valid(e) or not e.has_method("knock_aside"):
		return
	var from := e.global_position
	var to: Vector3 = ArenaMotion.slide(e, from, flat(land - from), _r(e))
	e.knock_aside(flat(to - from), time, false)


# ---- 4, Freight ------------------------------------------------------------------------------------------------------

## Fires one long chain in a line along the target (a bot's pick) or the aim, couples a train, hauls it, and brakes for
## the pile-up. True if it started.
func freight(target: Variant = null) -> bool:
	var b := _body()
	if b == null or not _free():
		return false
	used.emit("4")
	var dir := _aim(target)
	_start("Freight", dir)
	freight_targets = []
	cue.emit("freight")
	_play(b, "Freight_Brace")
	_freight_rest(b, dir)
	return true


func _freight_rest(b: MechModel3D, dir: Vector3) -> void:
	if await _event(b, "Freight_Brace", "chains_out"):
		var from: Vector3 = player.global_position
		chain_end = ArenaMotion.slide(player, from, dir * freight_line, 0.3)
		freight_targets = _freight_pick(dir, flat(chain_end - from).length())
		cue.emit("freight_chains")  # bison_fx fires the line chain and couples each car nose to tail
		await get_tree().create_timer(couple_delay).timeout
		for t in freight_targets:
			if MatchTeams.hittable(t) and is_instance_valid(player) and player.alive:
				_couple_car(t, dir)
	var ok: bool = await _event(b, "Freight_Brace", "braced")
	var snapped := not ok and not _freight.is_empty()  # a stun or knock-up during the brace
	if ok and not _freight.is_empty():
		freight_targets = freight_targets.filter(func(t: Variant) -> bool: return _freight.has(t))
		for i in freight_targets.size():
			_freight[freight_targets[i]] = i
		var want := _steer()
		player.facing = want.normalized() if want.length() >= 0.1 else -dir  # away from the train with no input
		snapped = await _run_haul(b, "freight", haul_time)
		if not snapped:
			for t in freight_targets:
				if coupled.has(t):
					_stun(t, pile_stun)
			impact.emit(0.4)
			cue.emit("pile_up")
	elif ok:
		await _clip_end(b, "Freight_Brace")
	if snapped:
		cue.emit("freight_snap")
	_break_all()
	_finish("Freight")


## Every enemy within freight_width of the line (to its edge) out to reach, with a clear line, nearest first.
func _freight_pick(dir: Vector3, reach: float) -> Array:
	var out: Array = []
	var from: Vector3 = player.global_position
	for e in MatchTeams.enemies_of(player):
		if not MatchTeams.hittable(e):
			continue
		var to := flat(e.global_position - from)
		var along := to.dot(dir)
		if along < -_r(e) or along > reach + _r(e) or (to - dir * along).length() - _r(e) > freight_width:
			continue
		if MatchTeams.clear_line(player, from, e.global_position):
			out.append(e)
	out.sort_custom(func(x: Node3D, y: Node3D) -> bool:
		return flat(x.global_position - from).dot(dir) < flat(y.global_position - from).dot(dir))
	return out


func _couple_car(t: Node3D, dir: Vector3) -> void:
	coupled[t] = INF  # held until the haul ends
	_freight[t] = 0
	t.set_meta("coupled_by", player)
	burn(t, 0.1)
	_hit(t, freight_damage, dir, 0.15)


## Freight's slag is one continuous track (Preston, 2026-11-18: "Yes, continuous"; spaced patches read as droppings
## and left 1.1 to 1.75 m gaps that did not burn). A live segment runs from the last laid point to under the bison's
## rear and follows it each frame; every haul_slag_every it is laid down (its slag_time starts, "slag" cue) and the
## next one starts from its end, so the hitbox is the whole path. Damage stays slag_dps, once a frame (see _process).
func _rear() -> Vector3:
	return player.global_position - flat(player.facing).normalized() * (_r(player) + 0.5)


func _slag_start() -> void:
	var at := _rear()
	_slag_live = {"from": at, "at": at, "until": INF, "r": haul_slag_radius}
	slag.append(_slag_live)


func _slag_follow() -> void:
	if _slag_live != null and is_instance_valid(player):
		_slag_live.at = _rear()


func _lay_slag() -> void:
	if is_instance_valid(player):
		_slag_live.at = _rear()
	_slag_live.until = _clock + slag_time
	slag_spots = [_slag_live.at]
	cue.emit("slag")


func _haul_slag() -> void:
	if _slag_live == null:
		_slag_start()
	_lay_slag()
	_slag_start()


func _slag_end() -> void:
	if _slag_live != null:
		_lay_slag()
		_slag_live = null


## True when a body of radius r at pos touches segment s: a flat capsule from s.from to s.at, radius s.r.
func _on_slag(s: Dictionary, pos: Vector3, r: float) -> bool:
	var a: Vector3 = flat(s.get("from", s.at))
	var d: Vector3 = flat(s.at) - a
	var q: Vector3 = flat(pos) - a
	var t: float = 0.0 if d.length_squared() < 0.0001 else clampf(q.dot(d) / d.length_squared(), 0.0, 1.0)
	return (q - d * t).length() <= float(s.r) + r


## True when a body of radius r at pos is on any live slag (probes read it).
func on_slag(pos: Vector3, r := 0.0) -> bool:
	for s in slag:
		if _clock < float(s.until) and _on_slag(s, pos, r):
			return true
	return false
