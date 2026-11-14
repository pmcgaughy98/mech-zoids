class_name HippoKit
extends Node
## The hippo's kit on the rigged 3D body (game feel lane, port started 2026-11-12, Preston: "Yes, start it").
## Design: docs/plan/hippo-kit-pressure-2026-11-11.md (the source of truth) and docs/plan/moba-kits.md (Hippo).
## Clips and events: art/arena_models/hippo.events.json (hippo 3D lane, r11).
##
## Slice 1 (this file so far):
##   Basic, the bite chain: bite, Jaw_Swing, Stomp. Preston, 2026-11-05: "Melee bite". Each press plays the next clip
##     of the chain if it comes within chain_window of the last; the hit lands on the clip's "hit" event on the nearest
##     enemy in front within basic_range (edge to edge). Nothing in reach: the clip still plays and snaps the air.
##   1, Vent: the Yawn clip. On its "hit" event a toxic cone (vent_range, vent_half_angle) hits every enemy inside, then
##     a puddle lies at the cone's middle and ticks poison on anyone standing in it. Preston: "Make it the purple
##     liquid I want it to have a poisonous or toxic type effect. Or noxious." The look is the hippo effects lane's
##     hippo_vent_fx.gd, which reads the same clip events.
## Slice 2 (Preston, 2026-11-12: "Yes, slice 2"):
##   2, Piston Drop: the Belly_Flop clip. From push_off to hit the hippo arcs to the aimed spot (drop_range at most,
##     short of a wall), lands on "hit" (drop_damage around it), and erupt_delay later the ground there erupts:
##     erupt_damage and an erupt_stun on everyone inside drop_radius. Bacchus's delayed burp stun, moved to the dive.
##     drop_radius and erupt_delay match hippo_drop_fx.gd (radius_m 3.2, erupt_delay 0.5).
##   Vent in the air: pressed between push_off and the landing, Vent plays no Yawn. The spray goes down, and on the
##     landing vent_damage hits everyone within vent_air_radius and the puddle lies where the hippo lands (the
##     open question in the hippo kit doc, answered yes). Cues: vent_air on the press, vent on the landing.
## Slice 3 (Preston, 2026-11-12: "Yes, slice 3"):
##   3, Lockjaw: Lockjaw_Clamp; on "capture" the nearest enemy in front within lockjaw_reach is held (the held_by
##     meta: it cannot move or act) and bitten. Then Lockjaw_Carry for up to carry_time: the hippo walks at the clip's
##     carry_speed wherever the move keys steer, always facing the way it walks (turning at carry_turn), and stands
##     on the carry stance with no keys. A second press of 3 slams early. Lockjaw_Slam: on "slam" the machine takes
##     slam_damage and a short stun in front of the jaws, on "release" it is let go. Preston: "Drag them into the
##     lake": the puddle and, later, the flood's lake are where it gets dragged. No fling away (it would break the combo).
##     The short toss toward the aim is not built.
## Slice 4 (Preston, 2026-11-12: "Yes, slice 4"):
##   4, Toxic Flood: the Toxic_Flood clip. On "burst" every enemy within lake_radius takes flood_damage and is pushed
##     flood_push outward, then the lake lies lake_life: enemies in it take lake_damage per lake_tick, and the hippo
##     heals lake_heal per tick while within lake_heal_share of the radius. lake_radius 6, lake_life 4, the 0.5 s tick
##     and the 85% share match hippo_flood_fx.gd. The tanks are blown: drained.
##   Passive, Pressure Tanks: pressure fills by pressure_per_dealt of the damage the hippo deals (not the flood's)
##     and pressure_per_taken of the damage it takes. Full: overcharged (cue tanks_full); the next of slots 1 to 3 is
##     overcharged and the tanks drain (cue overcharge_spent). Overcharged: overcharge_bonus damage for boost_time,
##     and Vent's puddle lasts overcharge_puddle times longer and slows (the doc's Vent overcharge). The bonus on
##     Piston Drop and Lockjaw is a proposal: the doc only names Vent's. After the flood the hippo is drained: its
##     damage is drained_weak lower until the tanks are drained_until full again (the doc's "weak until they refill").
##   Effects read kit.pressure, pressure_max, overcharged and drained; cues tanks_full, overcharge_spent,
##     tanks_drained, tanks_refilled, flood_charge, flood_burst, flood_lake_end.
## The hippo effects lane's four observers (Vent, Piston Drop, Lockjaw, Toxic Flood) are hung on the player once, when
## the body first appears; each one watches the body's clip events by itself.
## Without a 3D body (the old sprite arena) the basic is the old held-still bite, and the slots do nothing.
## Every number under "Proposals" is a proposal for Preston, not balance.

signal impact(strength: float) ## something landed; KitFeel shakes the camera on it
signal used(slot: String) ## the director starts the slot's cooldown (MatchRules)
signal cue(name: String) ## sound: bite, bite_whiff, jaw_swing, stomp, vent, vent_puddle

const HIPPO_FRAMES := preload("res://art/machines/hippo/hippo_frames.tres")
const CANVAS := 192
const FEET_EDGE_ROW := 161
const STRIDE := 0.48 ## m/s the old sprite walk is drawn planted at
const REACH_SLACK := 0.3 ## a target that drifts this far past basic_range during the wind-up is still bitten
const JAW_AHEAD := 1.3 ## metres from the hippo's centre to its jaws, for the whiff puff
const SPARK_UP := 0.6 ## spark height on the target
const CHAIN := ["bite", "Jaw_Swing", "Stomp"]
const CHAIN_CUES := ["bite", "jaw_swing", "stomp"]
const FX_SCRIPTS := [
	"res://scripts/moba3d/hippo_vent_fx.gd",
	"res://scripts/moba3d/hippo_drop_fx.gd",
	"res://scripts/moba3d/hippo_lockjaw_fx.gd",
	"res://scripts/moba3d/hippo_flood_fx.gd",
]

@export_group("Proposals, not balance")
@export var basic_range := 2.2 ## the hippo's middle to the target's edge (MatchTeams.edge_distance)
@export var basic_cooldown := 1.0
@export var bite_damage := 40.0 ## every link of the chain
@export var bite_half_angle := 60.0 ## degrees either side of the aim that the bite can reach
@export var bite_windup := 0.1 ## the old sprite bite: seconds from the key to the snap
@export var chain_window := 1.6 ## seconds after a basic in which the next press plays the next link
@export var hitstop := 0.05 ## the contact frame holds this long
@export var bite_shake := 0.2 ## impact strength for KitFeel on a hit; a whiff doesn't shake
@export var vent_range := 5.5 ## the cone's reach from the hippo's centre (matches hippo_vent_fx range_m)
@export var vent_half_angle := 30.0 ## a 60 degree cone (matches hippo_vent_fx half_angle_deg)
@export var vent_damage := 70.0
@export var vent_shake := 0.25
@export var puddle_radius := 1.6
@export var puddle_life := 3.0 ## seconds the puddle ticks (the effect's puddle shrinks away over its own 1.6 s)
@export var puddle_tick := 0.5
@export var puddle_damage := 8.0 ## per tick
@export var drop_range := 8.0 ## farthest landing from the take-off, centre to centre
@export var drop_height := 2.2 ## top of the arc
@export var drop_radius := 3.2 ## landing and eruption circle (hippo_drop_fx radius_m)
@export var drop_damage := 50.0 ## the landing
@export var drop_shake := 0.45
@export var erupt_delay := 0.5 ## Preston: Bacchus has "about a half second before burp stuns" (hippo_drop_fx erupt_delay)
@export var erupt_damage := 40.0
@export var erupt_stun := 0.8
@export var erupt_shake := 0.35
@export var vent_air_radius := 2.6 ## Vent pressed in the air: the downward spray's circle on the landing
@export var lockjaw_reach := 1.8 ## the hippo's middle to the target's edge (MatchTeams.edge_distance)
@export var lockjaw_half_angle := 50.0
@export var lockjaw_damage := 40.0 ## the clamp
@export var lockjaw_shake := 0.25
@export var carry_time := 1.0 ## Preston's plan: "walks about 1 s with them held"
@export var carry_speed := 1.75 ## m/s the carry moves at (the clip plays at carry_speed / the profile's carry pace)
@export var carry_turn := 3.0 ## rad/s the hippo can turn while carrying
@export var hold_gap := 0.15 ## metres between the jaws' reach and the held machine's edge
@export var slam_damage := 60.0
@export var slam_stun := 0.5
@export var slam_shake := 0.4
@export var flood_damage := 120.0 ## the burst
@export var flood_push := 3.0 ## metres outward
@export var flood_push_time := 0.35
@export var flood_shake := 0.6
@export var lake_radius := 6.0 ## hippo_flood_fx lake_radius
@export var lake_life := 4.0 ## hippo_flood_fx lake_life
@export var lake_tick := 0.5 ## hippo_flood_fx HEAL_TICK
@export var lake_damage := 15.0 ## per tick to each enemy in the lake
@export var lake_heal := 12.0 ## per tick while the hippo stands in its lake
@export var lake_heal_share := 0.85 ## of lake_radius (hippo_flood_fx)
@export var pressure_max := 100.0
@export var pressure_per_dealt := 0.3 ## pressure per point of damage dealt
@export var pressure_per_taken := 0.2 ## pressure per point of damage taken
@export var overcharge_bonus := 0.25 ## damage bonus on the overcharged skill
@export var boost_time := 2.5 ## seconds the overcharge bonus lasts (covers Lockjaw's clamp, carry and slam)
@export var overcharge_puddle := 2.0 ## Vent overcharged: the puddle lasts this many times longer, and slows
@export var drained_weak := 0.2 ## damage lost while drained
@export var drained_until := 0.5 ## share of full tanks that ends drained
@export var fx_on := true ## hang the hippo effects lane's observers on the player

var busy_with := "" ## the clip a kit move is playing, or ""
var chain_step := 0
var last_puddle := Vector3.ZERO ## for the checks
var puddle_hits := 0 ## ticks that landed, for the checks
var airborne := false ## between the Piston Drop's push_off and its landing
var last_landing := Vector3.ZERO ## for the checks
var last_peak := 0.0 ## metres above take-off at the arc's top, for the checks
var last_erupt := [] ## machines the last eruption stunned, for the checks
var _vent_air := false
var _ground_y := 0.0
var held: Node3D = null ## the machine in the jaws
var carry_to: Variant = null ## a bot's haul point (Vector3); null: the move keys steer
var carried_m := 0.0 ## metres walked in the last carry, for the checks
var last_slam_at := Vector3.ZERO ## for the checks
var _slam_now := false
var pressure := 0.0 ## the tanks, 0 to pressure_max
var overcharged := false
var drained := false
var boosted_slot := "" ## the slot the last overcharge went to, for the checks
var lake_at := Vector3.ZERO ## for the checks
var lake_hits := 0 ## for the checks
var heal_total := 0.0 ## healed in the last lake, for the checks
var _boost_until := -1.0 ## read by hippo_vent_fx via get(), with _clock, puddle_life and overcharge_puddle: keep these names
var _held_y := 0.0
var _last_basic := -100.0
var _clock := 0.0
var _rate_before := -1.0
var _ev_body: MechModel3D = null
var _got: Dictionary = {}
var _fx_on_player := false

@onready var player = get_parent() ## machine_test_player.gd


## Turns a field Player into the hippo: the old frames for the sprite arena, and this kit in place of any other.
## Loaded by path, not by class_name (the fennec kit's note on the class cache).
static func install(p: Node3D) -> Node:
	var spr: Node3D = p.get_node("Sprite")
	spr.stop_action()
	spr.sprite_frames = HIPPO_FRAMES
	spr.canvas_height = CANVAS
	spr.feet_edge_row = FEET_EDGE_ROW
	spr.size_class = "L"
	spr.play(StringName("idle_" + spr.view))
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var kit: Node = load("res://scripts/moba3d/hippo_kit.gd").new()
	kit.name = "Kit"
	p.add_child(kit)
	if p.has_method("apply_size_class"):
		p.apply_size_class()
	return kit


static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


## The body's scale against the 1.0 body the reach numbers were set on. The hippo 3D lane re-registered it at 1.25
## (2026-11-12, Preston asked for a bigger hippo): the jaws sit that much farther out, so the reaches follow it.
func _size() -> float:
	var b: Variant = player.get("body") if is_instance_valid(player) else null
	if b is MechModel3D and is_instance_valid(b):
		var row: Variant = b.get("_row")
		if row is Dictionary:
			return float(row.get("scale", 1.0))
	return 1.0


## Lockjaw_Carry's playback rate: the kit carries at carry_speed; the clip's feet are planted at the profile's
## carry_speed (2.1875 at scale 1.25), so it plays slower and the feet don't slide.
func _carry_rate(b: MechModel3D) -> float:
	var row: Variant = b.get("_row") if is_instance_valid(b) else null
	var pace: float = float(row.get("carry_speed", carry_speed)) if row is Dictionary else carry_speed
	return carry_speed / pace if pace > 0.01 else 1.0


func _ready() -> void:
	if player.has_signal("damaged"):
		player.damaged.connect(_on_damaged)
	if "full_speed_walk_rate" in player:
		_rate_before = player.full_speed_walk_rate


func _process(delta: float) -> void:
	_clock += delta
	if not is_instance_valid(player):
		return
	var b := _body()
	if b == null and _rate_before >= 0.0 and player.move_speed > 0.0:
		player.full_speed_walk_rate = player.move_speed / STRIDE  # the old sprite walk only


## The next machine gets its walk rate back, and the hippo is never left busy by a move cut short.
func _exit_tree() -> void:
	if not is_instance_valid(player):
		return
	if _rate_before >= 0.0:
		player.full_speed_walk_rate = _rate_before
	if airborne:
		airborne = false  # cut mid-dive: back down to the take-off height where it is
		player.global_position.y = _ground_y
	_let_go()
	if busy_with != "":
		player.busy = false
		busy_with = ""


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo or not is_instance_valid(player) or player.get("bot"):
		return
	if k.physical_keycode < KEY_1 or k.physical_keycode > KEY_4:
		return
	if k.physical_keycode == KEY_3 and busy_with == "Lockjaw_Carry":
		release_lockjaw()  # the second press slams early; the slot is already on cooldown, so this comes first
		return
	if player.has_method("slot_ready") and not player.slot_ready(str(k.physical_keycode - KEY_0)):
		return  # in a match a slot waits out its cooldown (MatchRules)
	match k.physical_keycode:
		KEY_1:
			vent()
		KEY_2:
			piston_drop()
		KEY_3:
			lockjaw()
		KEY_4:
			toxic_flood()


# ---- the 3D body ---------------------------------------------------------------------------------------------------

## The rigged body once the match has attached it (use_model runs after install), or null. Hangs the effects once.
func _body() -> MechModel3D:
	var b: Variant = player.get("body") if is_instance_valid(player) else null
	if not (b is MechModel3D) or not is_instance_valid(b) or not b.has_clip("Yawn"):
		return null
	if _ev_body != b:
		_ev_body = b
		b.event.connect(_on_body_event.bind(b))
	if fx_on and not _fx_on_player:
		_fx_on_player = true
		for path: String in FX_SCRIPTS:
			var script: Variant = load(path) if ResourceLoader.exists(path) else null
			if script is Script and script.can_instantiate():  # an effects file that fails to compile is skipped, not fatal
				var fx: Node = script.new()
				fx.name = path.get_file().get_basename().to_pascal_case()
				player.add_child(fx)
				if fx.has_method("setup"):
					fx.setup(player)
	return b


func _on_body_event(clip: String, n: String, _damage: bool, b: MechModel3D) -> void:
	if b == _ev_body:
		_got[clip + "/" + n] = int(_got.get(clip + "/" + n, 0)) + 1


func _play(b: MechModel3D, clip: String, speed := 1.0) -> void:
	for k in _got.keys():
		if String(k).begins_with(clip + "/"):
			_got.erase(k)
	b.play_action(clip, speed)


## Waits for the body's clip to fire event n. False when the clip ended or was replaced first, or the hippo died.
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
	player.busy = true
	player.facing = dir


func _finish(clip: String) -> void:
	if busy_with == clip:
		busy_with = ""
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
	return d.normalized()


func _hit(victim: Node3D, damage: float, dir: Vector3, shake: float, fill := true) -> void:
	var r: float = victim.radius() if victim.has_method("radius") else 0.0
	var d := damage * _out_scale()
	victim.hit(player, d / MatchRules.kit_hit_damage)
	if fill:
		_fill(d * pressure_per_dealt)
	Fx3D.spawn(player.get_parent(), "hit_spark", victim.global_position - dir * r + Vector3.UP * SPARK_UP, 0.0)
	impact.emit(shake)


# ---- basic, the bite chain -----------------------------------------------------------------------------------------

## Called by the director (Space or left click with target null, aimed with the mouse; a bot passes its target).
## True when the basic fired, hit or whiff; false when a bot's target is out of reach or the hippo is mid-move.
func basic_attack(target: Node3D) -> bool:
	if busy_with != "" or not is_instance_valid(player):
		return false
	var dir := _aim(target)
	var victim: Node3D = target
	if victim != null:
		if MatchTeams.edge_distance(player, victim) > basic_range * _size() + REACH_SLACK:
			return false
	else:
		victim = _pick(dir)
	var b := _body()
	if b == null:
		_bite_still(victim, dir)
	else:
		_chain(b, victim, dir)
	return true


## The nearest hittable enemy within reach and inside the bite's arc.
func _pick(dir: Vector3) -> Node3D:
	var best: Node3D = null
	var best_d := INF
	var min_dot := cos(deg_to_rad(bite_half_angle))
	for e in MatchTeams.enemies_of(player):
		if not (e is Node3D):
			continue
		var reach := MatchTeams.edge_distance(player, e)
		if reach > basic_range * _size():
			continue
		var to := flat(e.global_position - player.global_position)
		if to.length() > 0.3 and to.normalized().dot(dir) < min_dot:
			continue
		if reach < best_d:
			best_d = reach
			best = e
	return best


func _chain(b: MechModel3D, victim: Node3D, dir: Vector3) -> void:
	chain_step = (chain_step + 1) % CHAIN.size() if _clock - _last_basic <= chain_window else 0
	var clip: String = CHAIN[chain_step]
	if not b.has_clip(clip):
		clip = "bite"
	_start(clip, dir)
	_play(b, clip)
	if await _event(b, clip, "hit"):
		if victim != null and is_instance_valid(victim) and MatchTeams.hittable(victim) \
				and MatchTeams.edge_distance(player, victim) <= basic_range * _size() + REACH_SLACK:
			_hit(victim, bite_damage, dir, bite_shake)
			cue.emit(CHAIN_CUES[chain_step])
			b.freeze(hitstop)
		else:
			Fx3D.spawn(player.get_parent(), "impact_puff", player.global_position + dir * JAW_AHEAD * _size() + Vector3.UP * SPARK_UP, 0.0)
			cue.emit("bite_whiff")
	_last_basic = _clock
	await _event(b, clip, "recover")  # the director's own cooldown paces presses; the hippo moves again at recover
	_finish(clip)


## The old sprite arena (no body): the body holds still and the snap shows as a spark.
func _bite_still(victim: Node3D, dir: Vector3) -> void:
	_start("bite_still", dir)
	await get_tree().create_timer(bite_windup).timeout
	if not is_instance_valid(player):
		return
	if victim != null and is_instance_valid(victim) and MatchTeams.hittable(victim) \
			and MatchTeams.edge_distance(player, victim) <= basic_range * _size() + REACH_SLACK:
		_hit(victim, bite_damage, dir, bite_shake)
		cue.emit("bite")
		await get_tree().create_timer(hitstop).timeout
	else:
		Fx3D.spawn(player.get_parent(), "impact_puff", player.global_position + dir * JAW_AHEAD * _size() + Vector3.UP * SPARK_UP, 0.0)
		cue.emit("bite_whiff")
	_finish("bite_still")


# ---- 1, Vent -------------------------------------------------------------------------------------------------------

## The toxic cone. The player aims with the mouse; a bot may pass a target or a point. True if it fired.
func vent(target: Variant = null) -> bool:
	var b := _body()
	if b == null or not is_instance_valid(player) or not player.alive:
		return false
	if airborne and busy_with == "Belly_Flop" and not _vent_air:
		_vent_air = true  # the spray goes down; the Piston Drop's landing fires it
		_use("1")
		cue.emit("vent_air")
		return true
	if busy_with != "":
		return false
	var dir := _aim(target)
	_use("1")
	_start("Yawn", dir)
	_play(b, "Yawn")
	if await _event(b, "Yawn", "hit"):
		var hits := 0
		for e in _in_cone(dir):
			_hit(e, vent_damage, dir, vent_shake)
			hits += 1
		cue.emit("vent")
		_puddle(player.global_position + dir * vent_range * 0.6)
	await _clip_end(b, "Yawn")
	_finish("Yawn")
	return true


func _in_cone(dir: Vector3) -> Array:
	var out: Array = []
	var min_dot := cos(deg_to_rad(vent_half_angle))
	for e in MatchTeams.enemies_of(player):
		if not (e is Node3D):
			continue
		var to := flat(e.global_position - player.global_position)
		if MatchTeams.edge_distance(player, e) > vent_range:  # edge_distance is the hippo's middle to e's edge
			continue
		if to.length() > 0.3 and to.normalized().dot(dir) < min_dot:
			continue
		out.append(e)
	return out


## The puddle the spray leaves: poison ticks on enemies standing in it for puddle_life.
func _puddle(at: Vector3) -> void:
	last_puddle = flat(at)
	cue.emit("vent_puddle")
	var boosted := _clock < _boost_until  # overcharged Vent: a longer puddle that slows
	var left := puddle_life * (overcharge_puddle if boosted else 1.0)
	while left > 0.0:
		await get_tree().create_timer(puddle_tick).timeout
		left -= puddle_tick
		if not is_instance_valid(player):
			return
		for e in MatchTeams.enemies_of(player):
			if e is Node3D and flat(e.global_position - at).length() <= puddle_radius:
				var d := puddle_damage * _out_scale()
				e.hit(player, d / MatchRules.kit_hit_damage)
				_fill(d * pressure_per_dealt)
				if boosted and e.has_method("slow"):
					e.slow(puddle_tick + 0.1)
				puddle_hits += 1


# ---- 2, Piston Drop ------------------------------------------------------------------------------------------------

## The dive. The player aims with the mouse; a bot passes a target node or a point. True if it fired.
func piston_drop(target: Variant = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or not player.alive:
		return false
	var start: Vector3 = player.global_position
	var aim: Vector3 = start + flat(player.facing) * drop_range
	if target is Node3D and is_instance_valid(target):
		aim = target.global_position
	elif target is Vector3:
		aim = target
	elif player.has_method("aim_point"):
		aim = player.aim_point()
	var reach := flat(aim - start)
	if reach.length() > drop_range:
		reach = reach.normalized() * drop_range
	var dir := reach.normalized() if reach.length() > 0.05 else flat(player.facing).normalized()
	var land: Vector3 = ArenaMotion.slide(player, start, reach, player.radius())  # short of a wall
	land.y = start.y
	var times := {}
	for e in b.events_of("Belly_Flop"):
		times[e[0]] = float(e[1])
	var flight: float = maxf(float(times.get("hit", 0.72)) - float(times.get("push_off", 0.22)), 0.1)
	_use("2")
	_start("Belly_Flop", dir)
	_vent_air = false
	last_peak = 0.0
	_ground_y = start.y
	_play(b, "Belly_Flop")
	if not await _event(b, "Belly_Flop", "push_off"):
		_finish("Belly_Flop")
		return true
	airborne = true
	cue.emit("drop_push")
	var s := 0.0
	while is_instance_valid(b) and player.alive and b.action == "Belly_Flop" and int(_got.get("Belly_Flop/hit", 0)) < 1:
		s = minf(s + get_process_delta_time() / flight, 1.0)
		var up := 4.0 * drop_height * s * (1.0 - s)
		last_peak = maxf(last_peak, up)
		player.global_position = start.lerp(land, s) + Vector3.UP * up
		await get_tree().process_frame
	airborne = false
	if not is_instance_valid(player):
		return true
	var landed: bool = is_instance_valid(b) and player.alive and int(_got.get("Belly_Flop/hit", 0)) >= 1
	player.global_position = land if landed else Vector3(player.global_position.x, start.y, player.global_position.z)
	if not landed:
		_vent_air = false
		_finish("Belly_Flop")
		return true
	last_landing = land
	for e in _in_circle(land, drop_radius):
		_hit(e, drop_damage, dir, 0.0)
	impact.emit(drop_shake)
	cue.emit("drop_land")
	if _vent_air:
		_vent_air = false
		for e in _in_circle(land, vent_air_radius):
			_hit(e, vent_damage, dir, 0.0)
		cue.emit("vent")
		_puddle(land)
	_erupt(land, dir)
	await _clip_end(b, "Belly_Flop")
	_finish("Belly_Flop")
	return true


## erupt_delay after the landing the ground there erupts and stuns. It goes off even if the hippo is hit meanwhile.
func _erupt(at: Vector3, dir: Vector3) -> void:
	await get_tree().create_timer(erupt_delay).timeout
	if not is_instance_valid(player):
		return
	last_erupt = []
	for e in _in_circle(at, drop_radius):
		_hit(e, erupt_damage, dir, 0.0)
		if e.has_method("stun") and MatchTeams.hittable(e):
			e.stun(erupt_stun)
		last_erupt.append(e)
	impact.emit(erupt_shake)
	cue.emit("drop_erupt")


## Hittable enemies whose edge is within r of the point.
func _in_circle(at: Vector3, r: float) -> Array:
	var out: Array = []
	for e in MatchTeams.enemies_of(player):
		if not (e is Node3D):
			continue
		var er: float = e.radius() if e.has_method("radius") else 0.0
		if flat(e.global_position - at).length() - er <= r:
			out.append(e)
	return out


# ---- 3, Lockjaw ----------------------------------------------------------------------------------------------------

## Clamp one enemy in front, carry it up to carry_time, slam it down. The player aims with the mouse and steers the
## carry with the move keys; a bot passes a target, and may set carry_to (a point) to haul it there. True if it fired.
func lockjaw(target: Variant = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or not player.alive:
		return false
	var dir := _aim(target)
	var victim: Node3D = target if target is Node3D and is_instance_valid(target) else _pick_jaws(dir)
	_use("3")
	_slam_now = false
	_start("Lockjaw_Clamp", dir)
	_play(b, "Lockjaw_Clamp")
	if not await _event(b, "Lockjaw_Clamp", "capture"):
		_finish("Lockjaw_Clamp")
		return true
	if victim == null or not is_instance_valid(victim) or not MatchTeams.hittable(victim) or victim.has_meta("held_by") \
			or MatchTeams.edge_distance(player, victim) > lockjaw_reach * _size() + REACH_SLACK:
		Fx3D.spawn(player.get_parent(), "impact_puff", player.global_position + dir * JAW_AHEAD * _size() + Vector3.UP * SPARK_UP, 0.0)
		cue.emit("lockjaw_whiff")
		await _clip_end(b, "Lockjaw_Clamp")
		_finish("Lockjaw_Clamp")
		return true
	held = victim
	victim.set_meta("held_by", player)  # it cannot move or act; bots and minions pause (machine_test_player, MatchBot)
	_held_y = victim.global_position.y
	_hit(victim, lockjaw_damage, dir, lockjaw_shake)
	if victim.has_method("held_pose"):
		victim.held_pose()
	cue.emit("lockjaw_clamp")
	while _holding(b) and b.action == "Lockjaw_Clamp":
		_keep_in_jaws()
		await get_tree().process_frame
	# the carry: the hippo always faces the way it walks, so the forward Carry clip fits (hippo 3D lane, 2026-11-12)
	busy_with = "Lockjaw_Carry"
	if _holding(b):
		b.play_hold("Lockjaw_Carry", _carry_rate(b))
		cue.emit("lockjaw_carry")
	var t := 0.0
	carried_m = 0.0
	while _holding(b) and t < carry_time and not _slam_now:
		var dt := get_process_delta_time()
		t += dt
		var steer := _carry_steer()
		if steer.length() > 0.1:
			var face := flat(player.facing).normalized()
			var ang := face.signed_angle_to(steer.normalized(), Vector3.UP)
			face = face.rotated(Vector3.UP, clampf(ang, -carry_turn * dt, carry_turn * dt))
			player.facing = face
			var was: Vector3 = player.global_position
			player.global_position = ArenaMotion.slide(player, was, face * carry_speed * dt, player.radius())
			carried_m += flat(player.global_position - was).length()
			b.set_action_rate(_carry_rate(b))
		else:
			b.set_action_rate(0.0)  # standing: the carry stance holds still
		_keep_in_jaws()
		await get_tree().process_frame
	if is_instance_valid(b):
		b.set_action_rate(1.0)
	if not _holding(b):
		_let_go()
		_finish("Lockjaw_Carry")
		return true
	# the slam: down where it stands, in front of the jaws
	busy_with = "Lockjaw_Slam"
	_play(b, "Lockjaw_Slam")
	if await _event(b, "Lockjaw_Slam", "slam") and is_instance_valid(held):
		_keep_in_jaws()
		_hit(held, slam_damage, flat(player.facing).normalized(), slam_shake)
		if held.has_method("stun") and MatchTeams.hittable(held):
			held.stun(slam_stun)
		last_slam_at = flat(held.global_position)
		cue.emit("lockjaw_slam")
	await _event(b, "Lockjaw_Slam", "release")
	_let_go()
	await _clip_end(b, "Lockjaw_Slam")
	_finish("Lockjaw_Slam")
	return true


## The second press of 3 during the carry: slam now.
func release_lockjaw() -> void:
	if busy_with == "Lockjaw_Carry":
		_slam_now = true


## The nearest hittable enemy within lockjaw_reach and inside the jaws' arc.
func _pick_jaws(dir: Vector3) -> Node3D:
	var best: Node3D = null
	var best_d := INF
	var min_dot := cos(deg_to_rad(lockjaw_half_angle))
	for e in MatchTeams.enemies_of(player):
		if not (e is Node3D) or e.has_meta("held_by"):
			continue
		var reach := MatchTeams.edge_distance(player, e)
		if reach > lockjaw_reach * _size():
			continue
		var to := flat(e.global_position - player.global_position)
		if to.length() > 0.3 and to.normalized().dot(dir) < min_dot:
			continue
		if reach < best_d:
			best_d = reach
			best = e
	return best


func _holding(b: MechModel3D) -> bool:
	return is_instance_valid(b) and is_instance_valid(player) and player.alive and float(player.get("stunned")) <= 0.0 \
			and is_instance_valid(held) and held.get("alive") != false and held.has_meta("held_by") \
			and held.get_meta("held_by") == player


## Where the steer comes from: carry_to for a bot (a point), else the player's move keys (camera relative).
func _carry_steer() -> Vector3:
	if carry_to is Vector3:
		var to := flat(carry_to - player.global_position)
		return to if to.length() > 0.4 else Vector3.ZERO
	return flat(player.move_dir()) if player.has_method("move_dir") else Vector3.ZERO


## Keeps the held machine in front of the jaws, on the floor, short of a wall.
func _keep_in_jaws() -> void:
	if not is_instance_valid(held):
		return
	var r: float = held.radius() if held.has_method("radius") else 0.5
	var want: Vector3 = player.global_position + flat(player.facing).normalized() * ((player.radius() + hold_gap) * _size() + r)
	want.y = _held_y
	held.global_position = ArenaMotion.slide(held, held.global_position, want - held.global_position, r)


func _let_go() -> void:
	if is_instance_valid(held) and held.has_meta("held_by") and held.get_meta("held_by") == player:
		held.remove_meta("held_by")
	held = null
	carry_to = null


# ---- 4, Toxic Flood ------------------------------------------------------------------------------------------------

## Blows all three tanks. On the clip's "burst" every enemy inside lake_radius takes flood_damage and is pushed outward;
## then the lake lies lake_life: enemies inside take lake_damage every lake_tick, and the hippo heals lake_heal per tick
## while it stands within lake_heal_share of the radius. The tanks are emptied (drained). True if it fired.
func toxic_flood(_target: Variant = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or not player.alive:
		return false
	used.emit("4")  # not _use(): the flood spends no overcharge, it blows the tanks
	_start("Toxic_Flood", flat(player.facing).normalized())
	_play(b, "Toxic_Flood")
	cue.emit("flood_charge")
	if await _event(b, "Toxic_Flood", "burst"):
		lake_at = player.global_position
		for e in _in_circle(lake_at, lake_radius):
			var away := flat(e.global_position - lake_at)
			away = away.normalized() if away.length() > 0.05 else flat(player.facing).normalized()
			_hit(e, flood_damage, away, 0.0, false)
			if e.has_method("knock_aside") and e.get_method_argument_count("knock_aside") >= 3:
				e.knock_aside(away * flood_push, flood_push_time, false)
		impact.emit(flood_shake)
		cue.emit("flood_burst")
		_drain()
		_lake(lake_at)
	await _clip_end(b, "Toxic_Flood")
	_finish("Toxic_Flood")
	return true


func _lake(at: Vector3) -> void:
	lake_hits = 0
	heal_total = 0.0
	var left := lake_life
	while left > 0.0:
		await get_tree().create_timer(lake_tick).timeout
		left -= lake_tick
		if not is_instance_valid(player):
			return
		for e in _in_circle(at, lake_radius):
			e.hit(player, lake_damage / MatchRules.kit_hit_damage)  # the lake is the ult's own: never weakened, fills nothing
			lake_hits += 1
		if player.alive and flat(player.global_position - at).length() <= lake_radius * lake_heal_share \
				and player.has_method("heal"):
			heal_total += player.heal(lake_heal, player)
	cue.emit("flood_lake_end")


# ---- passive, Pressure Tanks ---------------------------------------------------------------------------------------

func _on_damaged(amount: float, _by: Node3D) -> void:
	if amount > 0.0:
		_fill(amount * pressure_per_taken)


func _fill(amount: float) -> void:
	if amount <= 0.0:
		return
	pressure = minf(pressure + amount, pressure_max)
	if drained and pressure >= pressure_max * drained_until:
		drained = false
		cue.emit("tanks_refilled")
	if not overcharged and pressure >= pressure_max:
		overcharged = true
		cue.emit("tanks_full")


## The flood empties the tanks: the hippo is weak (drained_weak) until they are drained_until full again.
func _drain() -> void:
	pressure = 0.0
	overcharged = false
	drained = true
	cue.emit("tanks_drained")


## A slot fires: start its cooldown, and with full tanks this skill is the overcharged one (then the tanks drain).
func _use(slot: String) -> void:
	used.emit(slot)
	if overcharged:
		overcharged = false
		pressure = 0.0
		_boost_until = _clock + boost_time
		boosted_slot = slot
		cue.emit("overcharge_spent")


func _out_scale() -> float:
	var s := 1.0
	if _clock < _boost_until:
		s *= 1.0 + overcharge_bonus
	if drained:
		s *= 1.0 - drained_weak
	return s
