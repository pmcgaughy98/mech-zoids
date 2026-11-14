class_name BisonKit
extends Node
## The bison's kit on its rigged 3D body (game feel lane, 2026-11-14; Preston: "Yes, start it"). Design:
## docs/plan/moba-kits.md, Bison (approved 2026-11-13: "Yes, with your picks"). Effects: bison_fx.gd (the bison effects
## lane), cue contracts in docs/reference/bison-fx-synthesis-2026-11-13.md. Names and numbers are placeholders.
##
## Slice 1:
## - Basic, horn hook: Hook_Right and Hook_Left in turn. On the clip's "hit" event the nearest enemy (machines before
##   minions) within basic_range (the bison's centre to the enemy's edge) and hook_half_angle of the swing takes hook_damage, x scorch_bonus
##   when scorched. With nothing in reach it still swings.
## - Passive, Scorch and Slag (part): scorch marks an enemy for scorch_time. Slag pools scorch anyone standing in them
##   and burn slag_dps. The chains and the plow scorch in later slices.
## - 2, Eruption: the Eruption clip. eruption_points (four Vector3 on the diagonals at eruption_radius, in erupt order
##   fl, rr, fr, rl, pulled in short of walls) are set at the cast. On "roar" every ally whose edge is within
##   eruption_radius (the bison too) is rallied: machine_test_player.set_rally (rally_damage harder, basic cooldown
##   divided by rally_rate, rally_time, each hit on an enemy machine stretches it by rally_stretch up to rally_max). Each
##   erupt_* event sends a bomb that lands bomb_flight later: bomb_damage to enemies within bomb_radius of the point
##   (to their edge), scorched, and a slag pool for slag_time.
##
## Slice 2 (Preston: "Yes, slice 2"):
## - 1, Coupling Chain: the Chain_Throw clip. On "fire" the nearest enemy within chain_range (centre to its edge) inside
##   chain_cone of the aim, with a clear line, is caught couple_delay later: chain_damage, scorched, and coupled for
##   couple_time (it burns couple_dps and carries the meta "coupled_by"). Past chain_length the chain goes taut and tows
##   it wherever the bison walks; chain_snap past that (a throw, a teleport) breaks it. While one enemy is coupled, one
##   more chain fires free (no cooldown); a chain at a coupled enemy is a refire and holds it couple_time again.
## - 3, Plow: the Plow clip. On "hit" every enemy within plow_reach (the bison's centre to the enemy's edge) and plow_half_angle of the sweep
##   takes plow_damage, is scorched, and is thrown plow_throw to the bison's left (the head sweeps right to left); a
##   coupled enemy is thrown to the far end of its chain instead.
## Slice 3 (Preston: "Yes, Freight"):
## - 4, Freight: Freight_Brace, then Freight_Haul held. From the cast to the brace's "braced" event the bison is braced
##   (machine_test_player._braced: no stun, toss or shove lands). On "chains_out" every enemy within freight_radius of
##   the bison's centre (to its edge), with a clear line, is in freight_targets (cue freight_chains); couple_delay later
##   each takes freight_damage and is coupled (scorched, burning) until the haul ends. At "braced" the haul starts: the
##   bison walks haul_speed for haul_time, turning at most haul_turn toward the move input (steer_to for bots and probes),
##   and pulls the coupled into a line behind it like rail cars (freight_length behind, then freight_gap apart, at
##   car_pull). Every haul_slag_every it drops a slag patch (haul_slag_radius) behind it, set in slag_spots before a
##   "slag" cue. A stun or knock-up on the hauler snaps it: freight_snap, then chain_break with a null target, which
##   also ends any chain from slot 1. The haul's end is the same chain_break.
## Not built: "can't dash or leap" while coupled (no kit reads "coupled_by" yet; the tow pulls a dash back), the bots'
## plan (the bison joins BOT_ROSTER after its kit). Enemies in front of the bison are pulled through it to the line.
##
## bison_fx.gd reads eruption_radius, slag_time, eruption_points, stack_slot, chain_target, chain_end, plow_radius,
## plow_targets and freight_targets, and the body's events. Keep these names.

signal impact(strength: float) ## something landed; KitFeel shakes the camera on it
signal used(slot: String) ## the director starts the slot's cooldown (MatchRules)
signal cue(name: String) ## eruption, rally, bomb_land (bomb_at); chain_fire, chain_couple, chain_miss, chain_break (chain_target, chain_end); plow, plow_hit (plow_targets)

const FX_SCRIPT := "res://scripts/moba3d/bison_fx.gd"
const SPARK_UP := 0.9
const ERUPT_ORDER := ["fl", "rr", "fr", "rl"] ## the stacks in the order the Eruption clip fires them

@export var basic_range := 2.2 ## metres from the bison's centre to the target's edge (MatchTeams.edge_distance; the director reads it)
@export var basic_cooldown := 1.1 ## seconds (the director reads it)
@export var hook_half_angle := 60.0
@export var hook_damage := 40.0
@export var scorch_bonus := 1.3 ## a hook on a scorched enemy
@export var scorch_time := 3.0
@export var eruption_radius := 3.5 ## bison_fx reads it
@export var bomb_flight := 0.72 ## seconds from the stack to the landing (bison_fx's flight)
@export var bomb_radius := 1.2 ## metres from the landing point to an enemy's edge
@export var bomb_damage := 35.0
@export var slag_time := 4.5 ## bison_fx reads it
@export var slag_radius := 0.95 ## metres; bison_fx's scorch is 1.9 m across
@export var slag_dps := 12.0
@export var rally_damage := 1.2
@export var rally_rate := 1.25
@export var rally_time := 4.0
@export var rally_stretch := 0.5
@export var rally_max := 7.0 ## the longest a rally can run from the roar
@export var chain_range := 9.0 ## metres from the bison's centre to the target's edge (MatchTeams.edge_distance)
@export var chain_cone := 35.0 ## degrees, the whole cone the chain picks in (the effects stub's guess)
@export var chain_length := 9.0 ## metres centre to centre; past it the chain goes taut and tows
@export var chain_snap := 4.0 ## metres past chain_length that break the chain
@export var couple_delay := 0.09 ## seconds from fire to the catch (bison_fx's reach)
@export var couple_time := 3.0 ## seconds a chain holds after its last couple or refire
@export var chain_damage := 25.0
@export var couple_dps := 10.0
@export var plow_reach := 3.0 ## metres from the bison's centre to the target's edge (MatchTeams.edge_distance): the scorch band's outer edge (bison_fx, measured)
@export var plow_half_angle := 70.0
@export var plow_damage := 55.0
@export var plow_throw := 2.5 ## metres to the bison's left
@export var plow_throw_time := 0.32
@export var plow_chain_throw_time := 0.5 ## a coupled enemy flies to the far end of its chain
@export var freight_radius := 6.0 ## metres from the bison's centre to an enemy's edge the brace chains
@export var freight_damage := 30.0 ## each car's catch
@export var freight_length := 2.6 ## metres from the bison's centre back to the first car's (bison_fx's stand-in)
@export var freight_gap := 1.7 ## metres between cars (bison_fx's stand-in)
@export var car_pull := 6.0 ## m/s a car is pulled toward its place in the line
@export var haul_speed := 0.518 ## m/s, the Freight_Haul stride (bison_fx's stand-in)
@export var haul_time := 4.0
@export var haul_turn := 50.0 ## degrees a second
@export var haul_slag_every := 0.6 ## seconds between slag patches (bison_fx logs a landing every 0.60 s)
@export var haul_slag_radius := 0.6 ## metres; bison_fx's patch is 1.2 m across
@export var fx_on := false ## bison_fx is hung by the effects lane's installer on Preston's "turn on" (its doc, item 7)

## Each stack belongs to one ability and goes dark while it cools; bison_fx reads this with the player's cooldowns.
var stack_slot := {"fl": "1", "fr": "2", "rl": "3", "rr": "4"}
var current := "" ## the arena's swap guard reads this (arena_play)
var busy_with := ""
var eruption_points: Array = []
var bomb_at := Vector3.ZERO
var bomb_hits := 0 ## enemies the last bomb hit, for the checks
var rallied_last: Array = [] ## the machines the last roar rallied, for the checks
var slag: Array = [] ## live pools: {"at": Vector3, "until": float}
## Read by bison_fx; the chain, the plow and Freight set them in later slices.
var chain_target: Node3D = null
var chain_end := Vector3.ZERO
var plow_radius := 2.4
var plow_targets: Array = []
var freight_targets: Array = []
var coupled := {} ## enemy -> _clock time its chain breaks
var braced := false ## Freight's brace: machine_test_player takes no stun, toss or shove
var hauling := false
var steer_to := Vector3.ZERO ## bots and probes steer the haul with this; the player with the move input
var slag_spots: Array = [] ## the last haul patch, set before a "slag" cue
var _freight := {} ## car -> its place in the line (0 first)
var _free_chain := false ## one more chain fires free while an enemy is coupled
var hook_side := "" ## the last hook's clip, for the checks
var hook_target: Node3D = null ## the last hook's victim, for the checks
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


func _process(delta: float) -> void:
	_clock += delta
	if slag.is_empty() or not is_instance_valid(player):
		return
	for i in range(slag.size() - 1, -1, -1):
		var s: Dictionary = slag[i]
		if _clock >= float(s.until):
			slag.remove_at(i)
			continue
		for e in MatchTeams.enemies_of(player):
			if is_instance_valid(e) and MatchTeams.hittable(e) and flat(e.global_position - s.at).length() <= float(s.get("r", slag_radius)) + _r(e):
				scorch(e)
				if e.has_method("take_damage"):
					player.set("dot_tick", true)  # a slag tick does not stretch a rally
					e.take_damage(slag_dps * delta, player)
					player.set("dot_tick", false)


## Chains: break on time, death or a snap; tow past chain_length; burn and scorch the coupled.
func _physics_process(delta: float) -> void:
	if coupled.is_empty():
		return
	if not is_instance_valid(player) or not player.alive:
		for t in coupled.keys():
			_break(t)
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
			if not _thrown(t):  # a car: pulled toward its place in the line behind the hauler
				var back := flat(player.facing).normalized()
				var spot: Vector3 = player.global_position - back * (freight_length + float(_freight[t]) * freight_gap)
				var go := flat(spot - t.global_position)
				var step := minf(go.length(), car_pull * delta)
				if step > 0.005:
					t.global_position = ArenaMotion.slide(t, t.global_position, go.normalized() * step, _r(t))
		elif d > chain_length and not _thrown(t):
			t.global_position = ArenaMotion.slide(t, t.global_position, -to.normalized() * (d - chain_length), _r(t))
		scorch(t)
		if t.has_method("take_damage"):
			player.set("dot_tick", true)  # a burn tick does not stretch a rally
			t.take_damage(couple_dps * delta, player)
			player.set("dot_tick", false)


## The next machine is never left busy by a cast cut short, and no enemy stays coupled.
func _exit_tree() -> void:
	if is_instance_valid(player) and busy_with != "":
		player.busy = false
	busy_with = ""
	current = ""
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
	if player.has_method("slot_ready") and not player.slot_ready(slot) and not (slot == "1" and free_chain_ready()):
		return  # in a match a slot waits out its cooldown (MatchRules); the free second chain does not
	match k.physical_keycode:
		KEY_1:
			chain()
		KEY_2:
			eruption()
		KEY_3:
			plow()
		KEY_4:
			freight()


# ---- the 3D body ---------------------------------------------------------------------------------------------------

## The rigged body once the match has attached it (use_model runs after install), or null. Hangs the effects once.
func _body() -> MechModel3D:
	var b: Variant = player.get("body") if is_instance_valid(player) else null
	if not (b is MechModel3D) or not is_instance_valid(b) or not b.has_clip("Eruption"):
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


# ---- passive: scorch -------------------------------------------------------------------------------------------------

## Marks an enemy as scorched for scorch_time (a second mark refreshes it).
func scorch(e: Node3D) -> void:
	_scorch_until[e] = _clock + scorch_time


func scorched(e: Node3D) -> bool:
	return is_instance_valid(e) and _clock < float(_scorch_until.get(e, -1.0))


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


# ---- 2, Eruption -----------------------------------------------------------------------------------------------------

## Head up, a roar (the rally), and four bombs from the stacks that land on the diagonals and leave slag. True if it
## started.
func eruption(_target: Variant = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or not player.alive or player.has_meta("held_by"):
		return false
	used.emit("2")
	var dir := flat(player.facing)
	dir = dir.normalized() if dir.length() > 0.01 else Vector3.FORWARD
	_start("Eruption", dir)
	eruption_points = _ring(dir)
	rallied_last.clear()
	cue.emit("eruption")  # bison_fx times the stacks from the clip's events
	_play(b, "Eruption")
	_eruption_rest(b)
	return true


func _eruption_rest(b: MechModel3D) -> void:
	if await _event(b, "Eruption", "roar"):
		_rally()
		for i in ERUPT_ORDER.size():
			if not await _event(b, "Eruption", "erupt_" + ERUPT_ORDER[i]):
				break
			_bomb(eruption_points[i])
	await _clip_end(b, "Eruption")
	_finish("Eruption")


## The four landing points in erupt order (fl, rr, fr, rl), each pulled in short of any wall on the way out.
func _ring(dir: Vector3) -> Array:
	var right := dir.cross(Vector3.UP).normalized()
	var c := eruption_radius * sqrt(0.5)
	var from: Vector3 = player.global_position
	var out: Array = []
	for corner in [dir - right, -dir + right, dir + right, -dir - right]:
		out.append(ArenaMotion.slide(player, from, corner * c, 0.3))
	return out


## Every ally whose edge is within eruption_radius of the bison, the bison too.
func _rally() -> void:
	var here: Vector3 = player.global_position
	for m in player.get_parent().get_children():
		if not (m is Node3D) or not m.has_method("set_rally") or m.get("team") != player.team or not m.get("alive"):
			continue
		if m != player and flat(m.global_position - here).length() - _r(m) > eruption_radius:
			continue
		m.set_rally(rally_damage, rally_rate, rally_time, rally_stretch, rally_max)
		rallied_last.append(m)
	cue.emit("rally")


func _bomb(at: Vector3) -> void:
	await get_tree().create_timer(bomb_flight).timeout
	if not is_instance_valid(player):
		return
	bomb_at = at
	bomb_hits = 0
	for e in MatchTeams.enemies_of(player):
		if not is_instance_valid(e) or not MatchTeams.hittable(e):
			continue
		var to := flat(e.global_position - at)
		if to.length() - _r(e) > bomb_radius:
			continue
		_hit(e, bomb_damage, to.normalized() if to.length() > 0.01 else Vector3.FORWARD, 0.0)
		scorch(e)
		bomb_hits += 1
	slag.append({"at": at, "until": _clock + slag_time})
	impact.emit(0.15)
	cue.emit("bomb_land")


# ---- 1, Coupling Chain -----------------------------------------------------------------------------------------------

## True while one more chain would fire free (an enemy is coupled and the free chain is unused).
func free_chain_ready() -> bool:
	return _free_chain and not coupled.is_empty() and busy_with == "" and is_instance_valid(player) and player.alive \
			and not player.has_meta("held_by") and float(player.get("stunned")) <= 0.0


## Throws the red-hot chain toward the target (a bot's pick) or the aim. True if it threw.
func chain(target: Variant = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or not player.alive or player.has_meta("held_by") \
			or float(player.get("stunned")) > 0.0:
		return false
	var free := free_chain_ready()
	if free:
		_free_chain = false
	else:
		used.emit("1")
	var dir := _aim(target)
	_start("Chain_Throw", dir)
	_play(b, "Chain_Throw")
	_chain_rest(b, dir, not free)
	return true


func _chain_rest(b: MechModel3D, dir: Vector3, paid: bool) -> void:
	if await _event(b, "Chain_Throw", "fire"):
		var t := _chain_pick(dir)
		chain_target = t
		chain_end = t.global_position if t != null else player.global_position + dir * (chain_range + _r(player))
		cue.emit("chain_fire")  # bison_fx: a fire at a coupled target is a refire
		await get_tree().create_timer(couple_delay).timeout
		if MatchTeams.hittable(t) and is_instance_valid(player) and player.alive:
			_couple(t, dir, paid)
		elif t == null or coupled.is_empty():
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


func _couple(t: Node3D, dir: Vector3, paid: bool) -> void:
	var refire := coupled.has(t)
	coupled[t] = _clock + couple_time
	t.set_meta("coupled_by", player)
	scorch(t)
	chain_target = t
	if refire:
		return  # a heat pulse along the held chain (bison_fx), the hold renewed
	_hit(t, chain_damage, dir, 0.2)
	cue.emit("chain_couple")
	if paid:
		_free_chain = true


func _break(t: Variant) -> void:
	coupled.erase(t)
	var ok := is_instance_valid(t)
	if ok and t.has_meta("coupled_by"):
		t.remove_meta("coupled_by")
	if coupled.is_empty():
		_free_chain = false
	if ok or coupled.is_empty():
		chain_target = t if ok else null  # null: bison_fx ends every chain
		cue.emit("chain_break")


## True while a knock or toss tween is moving the unit (the tow waits for it).
func _thrown(t: Node) -> bool:
	var tw: Variant = t.get("_move_tw")
	return tw is Tween and tw.is_valid() and tw.is_running()


# ---- 3, Plow ---------------------------------------------------------------------------------------------------------

## The hump-powered head sweep toward the target (a bot's pick) or the aim. True if it started.
func plow(target: Variant = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or not player.alive or player.has_meta("held_by") \
			or float(player.get("stunned")) > 0.0:
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


# ---- 4, Freight ------------------------------------------------------------------------------------------------------

## Chains to every enemy around it, braces, and hauls them off in a line. True if it started.
func freight(_target: Variant = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or not player.alive or player.has_meta("held_by") \
			or float(player.get("stunned")) > 0.0:
		return false
	used.emit("4")
	var dir := flat(player.facing)
	_start("Freight", dir.normalized() if dir.length() > 0.01 else Vector3.FORWARD)
	braced = true
	freight_targets = []
	cue.emit("freight")
	_play(b, "Freight_Brace")
	_freight_rest(b)
	return true


func _freight_rest(b: MechModel3D) -> void:
	if await _event(b, "Freight_Brace", "chains_out"):
		freight_targets = _freight_pick()
		cue.emit("freight_chains")  # bison_fx throws a chain to each; each couples couple_delay later on its own
		await get_tree().create_timer(couple_delay).timeout
		for t in freight_targets:
			if MatchTeams.hittable(t) and is_instance_valid(player) and player.alive:
				_couple_car(t)
	var ok: bool = await _event(b, "Freight_Brace", "braced")
	braced = false
	var snapped := false
	if ok:
		var cars: Array = _freight.keys().filter(func(t: Variant) -> bool: return is_instance_valid(t))
		cars.sort_custom(func(x: Node3D, y: Node3D) -> bool:
			return MatchTeams.edge_distance(player, x) < MatchTeams.edge_distance(player, y))
		for i in cars.size():
			_freight[cars[i]] = i
		hauling = true
		b.play_hold("Freight_Haul", 1.0)
		var left := haul_time
		var next_slag := haul_slag_every * 0.25
		var on := 0.0
		while left > 0.0:
			await get_tree().process_frame
			if not is_instance_valid(player) or not player.alive:
				break
			if float(player.get("stunned")) > 0.0 or (player.has_method("_forced") and player._forced()):
				snapped = true  # a stun or knock-up on the hauler
				break
			var dt := get_process_delta_time()
			left -= dt
			on += dt
			_haul_step(dt)
			if on >= next_slag:
				next_slag += haul_slag_every
				_haul_slag()
		hauling = false
		if is_instance_valid(b) and b.action == "Freight_Haul":
			b.stop_action()  # bison_fx: ends the haul's fire and smoke
	if snapped:
		cue.emit("freight_snap")
	_break_all()
	_finish("Freight")


## Every enemy within freight_radius with a clear line, nearest first.
func _freight_pick() -> Array:
	var out: Array = []
	for e in MatchTeams.enemies_of(player):
		if MatchTeams.hittable(e) and MatchTeams.edge_distance(player, e) <= freight_radius \
				and MatchTeams.clear_line(player, player.global_position, e.global_position):
			out.append(e)
	out.sort_custom(func(x: Node3D, y: Node3D) -> bool:
		return MatchTeams.edge_distance(player, x) < MatchTeams.edge_distance(player, y))
	return out


func _couple_car(t: Node3D) -> void:
	coupled[t] = INF  # held until the haul ends
	_freight[t] = 0
	t.set_meta("coupled_by", player)
	scorch(t)
	var to := flat(t.global_position - player.global_position)
	_hit(t, freight_damage, to.normalized() if to.length() > 0.01 else Vector3.FORWARD, 0.15)


func _haul_step(dt: float) -> void:
	var want := steer_to
	if want == Vector3.ZERO and player.has_method("move_dir"):
		want = player.move_dir()
	want = flat(want)
	var f := flat(player.facing).normalized()
	if want.length() >= 0.1:
		var cap := deg_to_rad(haul_turn) * dt
		f = f.rotated(Vector3.UP, clampf(f.signed_angle_to(want.normalized(), Vector3.UP), -cap, cap)).normalized()
	player.facing = f
	player.global_position = ArenaMotion.slide(player, player.global_position, f * haul_speed * dt, _r(player))


func _haul_slag() -> void:
	var spot: Vector3 = player.global_position - flat(player.facing).normalized() * (_r(player) + 0.5)
	slag.append({"at": spot, "until": _clock + slag_time, "r": haul_slag_radius})
	slag_spots = [spot]
	cue.emit("slag")


## Ends every chain at once (bison_fx: chain_break with a null target drops them all).
func _break_all() -> void:
	var had := not coupled.is_empty()
	for t in coupled.keys():
		if is_instance_valid(t) and t.has_meta("coupled_by"):
			t.remove_meta("coupled_by")
	coupled.clear()
	_freight.clear()
	_free_chain = false
	if had:
		chain_target = null
		cue.emit("chain_break")


func _throw(e: Node3D, land: Vector3, time: float) -> void:
	if not is_instance_valid(e) or not e.has_method("knock_aside"):
		return
	var from := e.global_position
	var to: Vector3 = ArenaMotion.slide(e, from, flat(land - from), _r(e))
	e.knock_aside(flat(to - from), time, false)
