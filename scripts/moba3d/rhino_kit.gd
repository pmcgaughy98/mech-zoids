class_name RhinoKit
extends Node
## The rhino's kit in the 3D slice (Claude, 2026-11-04; Preston: "build kit"). What each ability does is Preston's
## design in docs/plan/moba-kits.md, under its working names. Keys 1-4 in the field; the reveal calls the same
## functions. Every length below is a presentation placeholder so the abilities can be seen, not a balance number:
## the doc gives cooldowns only as short, medium and long, so there are no cooldowns or damage numbers yet.
##   Passive, front plating: hits from inside the front arc spark off the plates (take_hit returns true).
##   1 horn toss: a short dash, head down; the first target met is caught on the horn, held a beat (hitstop) and
##     flicked back over the rhino's back, landing behind it stunned (Preston, 2026-11-05: "a short dash forward then
##     pluck back").
##   2 ground pound: rears and slams, then keeps stomping in place; the big circle shakes and slows everyone in it
##     while it lasts and a moment after (Preston, 2026-11-05: "a bigger circle like cabrakan where its stomping on
##     the ground trembling and slowing those in the circle"). One damaging hit, on the first slam.
##   3 aftershock (Preston, 2026-11-20, replacing the brace; numbers from kit design, docs/plan/rhino-brace-replacement-
##     2026-11-20.md): a stomp after aftershock_windup sends a seismic wave along the aim, a cone that travels out. Each
##     enemy it passes is hit once: damage, a 30% slow and grounded (no dashes, leaps, rolls or blinks). It spends the
##     Seismic charge for more reach, damage and grounded time, and at full charge it also stuns. Machines in the air
##     when the front passes dodge it; held ones are still hit; walls and rocks between are cover.
##   4 stampede: a long charge that shoves every target in its path aside, ending in a pound that stuns the ring.
##   Basic attack, horn jab (Rhino session, 2026-11-05; Preston: "we need basic attacks. Rhino, gorilla will be
##     melee"): a short low-to-high jab at one target in reach. The director calls basic_attack() (game feel's hook).
## Impacts shake the camera through KitFeel for the player's own machine (game feel lane, 2026-11-05).
## The 3D body (game feel lane, 2026-11-10, on the rhino lane's v46 clips; Preston: "get the kit ready and effects so
## its on level on gorilla"): with a MechModel3D body that has the horn chain, every ability plays its own clip and
## lands on that clip's events (the rhino's profile in art/arena_models/authored_profiles.json) instead of the
## sprite's frames, and the basic becomes the chain hook, rip, gore. The sprite path stays for a machine without that
## body (the arena under a test script starts on the sprite).

signal impact(strength: float) ## something landed hard; cameras can shake on it
signal used(slot: String)
signal cue(name: String) ## named moments for the sound lane: dash_cast, horn_catch, toss_land, tremor_stomp, jab_swing, jab_hit,
## and Aftershock's aftershock_windup (the cast), aftershock_wave (the stomp: last_aftershock holds the wave), aftershock_hit
## (one per enemy; last_aftershock_hit is that enemy) and aftershock_end (the front reached its reach)

const TOSS_DASH_FRAME := 2 ## horn_toss frame 2, head down, is held through the dash
const TOSS_RELEASE_FRAME := 3 ## horn_toss frame 3 is the flick
const POUND_SLAM_FRAME := 4 ## ground_pound frame 4 is the slam (composite.py starts the ring on F4)
const POUND_RISE_FRAME := 5 ## ground_pound frame 5, the lift after the slam: each stomp of the tremor goes 5 then 4
## horn_jab frame 2 is the hit: the lunge, the horn furthest forward and the head lowest in every side-on view (attack
## lane, measured on all five drawn views, 2026-11-05). Frame 3 is the upward toss after contact.
const JAB_HIT_FRAME := 2
## The 3D body's basic chain, in order, with its feel per hit (agreed with the rhino lane 2026-11-10, pending
## Preston's eye): hitstop on both bodies, and KitFeel.basic_hit strength for the camera kick and the shove (the
## gorilla's swat is 1.0, its slam 1.5).
const CHAIN := ["horn_hook", "horn_rip", "horn_gore"]
const CHAIN_HITSTOP := [0.05, 0.07, 0.10]
const CHAIN_STRENGTH := [0.8, 1.0, 1.5]
const GORE_LAND_SHAKE := 0.3 ## a stomp is 0.35

@export_group("Placeholder lengths, not balance")
@export var front_arc_degrees := 100.0 ## hits from inside this arc in front land on the plating
@export var toss_dash_distance := 3.5
@export var toss_dash_speed := 14.0 ## the full dash takes 0.25 s
@export var toss_reach := 1.6 ## centre to centre: a target this close in front is caught on the horn
@export var toss_cone_degrees := 40.0
@export var toss_land_behind := 3.0
@export var toss_height := 2.2
@export var toss_air_time := 0.6
@export var hitstop := 0.08 ## the contact frame holds this long before the target flies
@export var stun_time := 1.6
@export var pound_radius := 4.0 ## the tremor circle (2.2 before 2026-11-05)
@export var tremor_stomps := 4 ## stomps after the first slam
@export var tremor_interval := 0.4
@export var tremor_linger := 0.8 ## the slow stays this long after the last stomp
@export var pound_slow_time := 1.2
@export var patch_time := 2.5 ## the stampede finale's cracks stay this long as a slow patch
@export var stampede_distance := 12.0
@export var stampede_speed := 9.0
@export var stampede_width := 1.8
@export var stampede_anim_speed := 1.8
@export var finale_radius := 3.4

@export_group("Basic attack, horn jab (picks for Preston to tune)")
@export var basic_range := 2.0 ## metres, edge to edge (MatchTeams.edge_distance); the director and the bots read it
@export var basic_cooldown := 0.9 ## seconds; the director sets it after each jab (the stand-in's 0.9)
@export var basic_damage := 30.0 ## the stand-in shot's 30 (MatchRules.basic_damage); front plating and shields still apply
@export var basic_cone_degrees := 50.0 ## with no target given, the jab takes the nearest enemy within this of the aim
@export var basic_hitstop := 0.05 ## the hit frame holds this long on contact
@export var jab_assist := true ## Space with nothing where the mouse aims: the jab turns to the nearest enemy in reach
@export var jab_anim_speed := 2.0 ## horn_jab is 9 ticks at 10 fps: at 2x it plays in 0.45 s, the hit at 0.20 s
@export_group("Seismic charge (drafts for Preston, rhino lane slice 1, 2026-11-11)")
@export var seismic_gap := 0.5 ## one charge per attacker at most this often
@export var seismic_hold := 5.0 ## no gain this long and the charge starts to drain
@export var seismic_decay_every := 2.0 ## then one charge drains this often
@export_group("Aftershock, slot 3 (Preston, 2026-11-20; kit design's numbers)")
@export var aftershock_windup := 0.35 ## the stomp: the wave sets off this long after the cast (the clip to come hits at about 0.35 s)
@export var aftershock_recover := 0.45 ## the rhino is busy this long after the stomp (about 0.8 s in all)
@export var aftershock_length := 8.0 ## metres the wave runs, plus aftershock_length_per a charge spent
@export var aftershock_length_per := 1.0
@export var aftershock_half_angle := 20.0 ## degrees each side of the aim
@export var aftershock_speed := 16.0 ## m/s: the front reaches 8 m in 0.5 s
@export var aftershock_damage := 30.0 ## plus aftershock_damage_per a charge, once per enemy
@export var aftershock_damage_per := 6.0
@export var aftershock_slow := 0.7 ## speed factor: slowed 30%
@export var aftershock_slow_time := 1.5
@export var aftershock_grounded := 2.0 ## seconds, plus aftershock_grounded_per a charge
@export var aftershock_grounded_per := 0.2
@export var aftershock_stun := 0.75 ## only at full charge (SEISMIC_MAX), alongside the grounded
@export_group("Tremor charge, the stampede rework (drafts for Preston, rhino lane slice 2, 2026-11-11)")
@export var tremor_distance := 16.0 ## the longest run, metres
@export var tremor_speed_start := 9.0 ## m/s, rising to tremor_speed_end over tremor_ramp seconds
@export var tremor_speed_end := 12.0
@export var tremor_ramp := 1.0
@export var tremor_steer_deg := 50.0 ## degrees a second the run turns toward the aim
@export var tremor_pulse_every := 3.0 ## metres between tremor pulses
@export var tremor_pulse_radius := 2.2
@export var tremor_pulse_damage := 8.0
@export var tremor_pulse_slow := 1.0 ## seconds (the slow itself is MatchRules.slow_mult)
@export var tremor_charge_every := 4.0 ## metres run per Seismic charge
@export var tremor_stop_after := 0.5 ## a second press this long into the run ends it there
@export var tremor_finale_grow := 0.6 ## finale radius: finale_radius + this x (run / tremor_distance) + per charge
@export var tremor_finale_per_charge := 0.12
@export var tremor_stun := 0.8 ## finale stun: this + tremor_stun_grow x (run / tremor_distance) + per charge
@export var tremor_stun_grow := 0.4
@export var tremor_stun_per_charge := 0.08
@export var tremor_carry := true ## slice 3 (Preston, 2026-11-11): enemy machines the run's front touches ride along and take the finale
@export var tremor_carry_ahead := 2.4 ## where a carried machine is held, metres ahead of the rhino (2.4 clears the head; rhino lane's video, 2026-11-11)
@export var tremor_carry_spread := 1.2 ## how far to the side one carried machine may sit; two or more are spread side by side, clear of each other
@export var tremor_drop_forward := 0.4 ## v51 horn lift: on the finale's drop event the carried machines hop this far forward
@export var tremor_drop_height := 1.4 ## and this high, landing just before the slam (Preston, 2026-11-11: a bigger flick)
@export var tremor_carry_settle := 7.0 ## m/s a caught machine slides to its place on the horn, so the catch does not jump
@export_group("Basic attack, horn jab (picks for Preston to tune)")
@export var chain_reset := 1.5 ## 3D body: this long after a basic ends, the next one starts the chain over at the hook

var braced := false ## always false now: Aftershock replaced the brace (2026-11-20); rhino_release_fx and machine_test_player._braced read it
var current := "" ## the ability whose animation is playing, or ""
var last_aftershock := {} ## the last wave: origin, dir, reach, charge, half_angle, speed, hits (the effects and checks read it)
var last_aftershock_hit: Node3D = null ## the enemy the last aftershock_hit cue was for
var _chain := 0 ## the next hit of the 3D body's chain (index into CHAIN)
var _chain_end := -1000.0 ## seconds (ticks) when the last basic ended
var _got := {} ## "clip/event" -> true: the body's events since that clip last started
const SEISMIC_MAX := 5
const LOOK := preload("res://scripts/moba3d/mech_look.gd")
var seismic := 0 ## Seismic charge, 0 to SEISMIC_MAX: plating blocks and the Tremor run fill it; Aftershock and the Tremor finale spend it
var _clock := 0.0 ## seconds of game time this kit has run (gates and decay use it, not the wall clock)
var _seismic_from := {} ## attacker (or "?") -> _clock of its last charge
var _seismic_last := -1000.0
var _seismic_decay := 0.0
var _glow_flash := 0.0 ## the release flash, seconds left
var _glow_set := -1.0
var tremor_pulses := 0 ## pulses fired since the kit started (the checks read it)
var tremor_gone := 0.0 ## metres the current or last Tremor charge ran
var last_finale_r := 0.0 ## the last Tremor charge finale's radius and stun (the checks read them)
var last_finale_stun := 0.0
var last_walled := false
var _tremor_running := false
var _tremor_stop := false
var _tremor_t := 0.0
var _carried: Array = [] ## the machines the Tremor run is carrying (slice 3), held with the held_by meta until the finale's slam
var _carry_side := {} ## each carried machine's place to the side of the run
var _carry_now := {} ## where each carried machine is now, [ahead, side], easing to its place
var last_carried := 0 ## how many machines the last Tremor run caught (the checks read it)
var _run_shoved: Array = [] ## every unit the Tremor run shoved aside; the finale hits them wherever they are (Preston, 2026-11-11)
var _glow_floor := 0.0 ## the wind-up ramps the drum ring up to 5.5 and the run holds it there
var _finale_r := -1.0 ## one finale's radius and stun, set by the Tremor charge; -1 uses finale_radius and stun_time
var _finale_stun := -1.0
var _ev_body: MechModel3D = null ## the body whose events are connected

@onready var player = get_parent() ## machine_test_player.gd
@onready var sprite: DirectionalSprite3D = get_parent().get_node("Sprite")


func _ready() -> void:
	impact.connect(_shake)


func _shake(strength: float) -> void:
	if not player.get("bot"):
		KitFeel.shake(self, strength)


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if player.get("bot") or (player.has_method("slot_ready") and not player.slot_ready(str(k.physical_keycode - KEY_0)) and not (_tremor_running and k.physical_keycode == KEY_4)):
		return  # a bot's kit ignores the keyboard; in a match a slot waits out its cooldown (MatchRules)
	match k.physical_keycode:
		KEY_1:
			horn_toss()
		KEY_2:
			ground_pound()
		KEY_3:
			aftershock()
		KEY_4:
			stampede()


func world() -> Node:
	return player.get_parent()


func targets() -> Array:
	return MatchTeams.enemies_of(player)


func feet() -> Vector3:
	return player.global_position


func ahead() -> Vector3:
	var f: Vector3 = player.facing
	return Vector3(f.x, 0.0, f.z).normalized()


static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


## Passive, front plating. Call when anything hits the rhino; true when the plating takes it.
func take_hit(from: Vector3, by: Node3D = null) -> bool:
	var to := flat(from - feet()).normalized()
	var blocked := rad_to_deg(ahead().angle_to(to)) <= front_arc_degrees * 0.5
	if blocked:
		_gain_seismic(by)
	Fx3D.spawn(world(), "deflect_spark" if blocked else "hit_spark", feet() + to * 0.9 + Vector3.UP * 0.9, 0.3)
	if not blocked:
		var pb: Variant = player.get("body")
		if pb is MechModel3D:
			pb.flash()  # the sprite is hidden under a 3D body
		else:
			sprite.modulate = Color(2.0, 2.0, 2.0)
			create_tween().tween_property(sprite, "modulate", Color.WHITE, 0.15)
	impact.emit(0.1 if blocked else 0.25)
	return blocked


## The basic attack, a horn jab. The director calls it on space or left click with target null (the jab goes where
## the mouse aims, else where the rhino faces) and for the bots with their pick, already in reach. The director keeps
## the gates and sets basic_cooldown; this returns true when the jab starts. A jab at the air counts, so the player's
## key always gets a swing. Synchronous on purpose: the swing itself runs in _jab() without being awaited.
func basic_attack(target: Node3D) -> bool:
	if current != "":
		return false
	var dir := Vector3.ZERO
	if target != null:
		if _reach_of(target) > basic_range + 0.5:
			return false
		dir = flat(target.global_position - feet()).normalized()
	elif player.has_method("aim_dir"):
		dir = player.aim_dir()
	if dir == Vector3.ZERO:
		dir = ahead()
	if target == null and jab_assist and _jab_pick(dir) == null:
		var near := _jab_pick(dir, 180.0)  # nothing where it aims: turn to whoever is in reach
		if near != null:
			dir = flat(near.global_position - feet()).normalized()
	player.facing = dir
	_jab(target, dir)
	return true


func _jab(target: Node3D, dir: Vector3) -> void:
	var b := _body()
	if b != null:
		_horn_chain(b, target, dir)
		return
	if not _begin("horn_jab"):
		return
	sprite.speed_scale = jab_anim_speed
	cue.emit("jab_swing")
	await _wait_frame("horn_jab", JAB_HIT_FRAME)
	if sprite.action != "horn_jab":  # something else took the sprite (death): no hit, and leave its animation alone
		sprite.speed_scale = 1.0
		current = ""
		player.busy = false
		return
	var t: Node3D = target
	if t == null or not MatchTeams.hittable(t) or _reach_of(t) > basic_range + 0.5:
		t = _jab_pick(dir)  # the given target died or moved out of reach during the wind-up: take whoever is there
	if t != null:
		sprite.hold_frame(JAB_HIT_FRAME)
		if t.has_method("hit"):
			t.hit(player, basic_damage / MatchRules.kit_hit_damage)  # machines: plating and shields apply
		elif t.has_method("take_damage"):
			t.take_damage(basic_damage, player)  # towers and cores
		Fx3D.spawn(world(), "hit_spark", t.global_position + Vector3.UP * 1.0, 0.3)
		cue.emit("jab_hit")
		impact.emit(0.2)
		await get_tree().create_timer(basic_hitstop).timeout
		sprite.release_from(JAB_HIT_FRAME)
		sprite.speed_scale = jab_anim_speed  # release_from() puts the speed back to 1
	await _wait_end("horn_jab")
	sprite.speed_scale = 1.0
	_end()


## The basic on the 3D body: hook, rip, gore in turn (rhino lane's clips; Preston accepted the chain "for now",
## 2026-11-10), each landing on its clip's hit event. chain_reset after a basic ends, the chain starts over at the
## hook. Every hit deals basic_damage, as the jab did: the chain changes the feel (hitstop, kick, which way the target
## is shoved), not the numbers. Both bodies hold for the hitstop. The gore's land shakes a little, only when the
## local player is the rhino or the one it hit.
func _horn_chain(b: MechModel3D, target: Node3D, dir: Vector3) -> void:
	if Time.get_ticks_msec() / 1000.0 - _chain_end > chain_reset:
		_chain = 0
	var i := _chain
	_chain = (_chain + 1) % CHAIN.size()
	var clip: String = CHAIN[i]
	current = clip
	player.busy = true
	_play(b, clip)
	cue.emit("jab_swing")
	var t: Node3D = null
	var landed: bool = await _event(b, clip, "hit")
	if landed:
		t = target
		if t == null or not MatchTeams.hittable(t) or _reach_of(t) > basic_range + 0.5:
			t = _jab_pick(dir)  # the given target died or moved out of reach during the wind-up: take whoever is there
		if t != null:
			if t.has_method("hit"):
				t.hit(player, basic_damage / MatchRules.kit_hit_damage)  # machines: plating and shields apply
			elif t.has_method("take_damage"):
				t.take_damage(basic_damage, player)  # towers and cores
			var f := ahead()
			var push: Vector3 = [Vector3.UP.cross(f), (f.cross(Vector3.UP) + f).normalized(), f][i]  # hook to the rhino's left, rip to its right and on, gore straight
			KitFeel.basic_hit(player, t, push, CHAIN_STRENGTH[i])
			cue.emit("jab_hit")
			b.freeze(CHAIN_HITSTOP[i])
			var tb: Variant = t.get("body")
			if tb is MechModel3D:
				tb.freeze(CHAIN_HITSTOP[i])
	if landed and clip == "horn_gore":
		var down: bool = await _event(b, clip, "land")
		if down:
			cue.emit("gore_land")
			if not player.get("bot") or (is_instance_valid(t) and KitFeel._is_local_player(t)):
				KitFeel.shake(self, GORE_LAND_SHAKE)
	await _clip_end(b, clip)
	_chain_end = Time.get_ticks_msec() / 1000.0
	if current == clip:
		_end()


## The nearest enemy in reach within basic_cone_degrees of dir. In a match that includes towers, cores and camp
## monsters (targets() leaves buildings out for the abilities); in the field test, the kit targets.
func _jab_pick(dir: Vector3, cone := -1.0) -> Node3D:
	if cone < 0.0:
		cone = basic_cone_degrees
	var pool: Array = targets()
	if MatchTeams.team_of(player) != "":
		pool = get_tree().get_nodes_in_group("match_unit").filter(func(u: Node) -> bool:
			return u != player and MatchTeams.is_enemy(u, player) and MatchTeams.hittable(u))
	var best: Node3D = null
	var best_d := basic_range
	for t: Node3D in pool:
		var d := _reach_of(t)
		var to := flat(t.global_position - feet())
		# cone 180 means all round: skip the angle, which reads a hair over 180 for a target straight behind
		if d <= best_d and (cone >= 180.0 or to.length() < 0.01 or rad_to_deg(dir.angle_to(to.normalized())) <= cone):
			best = t
			best_d = d
	return best


func _reach_of(t: Node3D) -> float:
	return MatchTeams.edge_distance(player, t)


func horn_toss() -> void:
	if not _begin("horn_toss"):
		return
	used.emit("1")
	var b := _body()
	if b != null:
		_play(b, "horn_toss")
		await _event(b, "horn_toss", "dash_start")  # the head is down: the kit moves the rhino, the clip stays in place
	else:
		sprite.speed_scale = 2.0  # a quick head-down, then the dash
		await _wait_frame("horn_toss", TOSS_DASH_FRAME)
		sprite.hold_frame(TOSS_DASH_FRAME)
	var dir := ahead()
	Fx3D.spawn(world(), "impact_puff", feet() - dir * 0.9, 0.2)
	cue.emit("dash_cast")
	var t = _first_in_front(toss_reach)
	var gone := 0.0
	var dust := 0.0
	while t == null and gone < toss_dash_distance:
		await get_tree().process_frame
		var step := minf(toss_dash_speed * get_process_delta_time(), toss_dash_distance - gone)
		player.global_position = ArenaMotion.slide(player, player.global_position, dir * step, player.body_radius())
		gone += step
		dust -= step
		if dust <= 0.0:
			dust = 0.9
			Fx3D.spawn(world(), "dust_trail", feet() - dir * 0.9)
		t = _first_in_front(toss_reach)
	if t != null and b != null:
		await _event(b, "horn_toss", "catch")  # the clip's catch: the horn comes up under the target
		if is_instance_valid(t) and MatchTeams.hittable(t):
			_horn_catch(t)
			b.freeze(hitstop)
			var tb: Variant = t.get("body")
			if tb is MechModel3D:
				tb.freeze(hitstop)
			await _event(b, "horn_toss", "release")
			if is_instance_valid(t):
				_toss(t, dir)
	elif t != null:
		sprite.hold_frame(TOSS_RELEASE_FRAME)  # caught: the flick frame holds for the hitstop
		_horn_catch(t)
		await get_tree().create_timer(hitstop).timeout
		_toss(t, dir)
		sprite.release_from(TOSS_RELEASE_FRAME + 1)
	elif b == null:
		sprite.release_from(TOSS_RELEASE_FRAME)  # a miss still flicks the horn at the air
	if b != null:
		await _clip_end(b, "horn_toss")
	else:
		await _wait_end("horn_toss")
	_end()


func _horn_catch(t) -> void:
	Fx3D.spawn(world(), "hit_spark", t.global_position + Vector3.UP * 1.0, 0.4)
	cue.emit("horn_catch")
	impact.emit(0.5)


func _toss(t, dir: Vector3) -> void:
	var land := feet() - dir * toss_land_behind
	t.toss_to(land, toss_height, toss_air_time, stun_time)
	get_tree().create_timer(toss_air_time).timeout.connect(_toss_landed.bind(land))


func _toss_landed(land: Vector3) -> void:
	Fx3D.spawn(world(), "impact_puff", land, 0.3)
	cue.emit("toss_land")
	impact.emit(0.4)


## The tremor. The stampede's finale passes true: one heavy slam that stuns, without the stomping.
func ground_pound(finale := false) -> void:
	if not _begin("ground_pound"):
		return
	if not finale:
		used.emit("2")
	var b := _body()
	var clip := "ground_pound_finale" if finale else "ground_pound"
	if b != null:
		_play(b, clip)
		if finale and not _carried.is_empty() and _clip_time(b, clip, "drop") >= 0.0:
			var hang := clampf(_clip_time(b, clip, "slam") - _clip_time(b, clip, "drop") - 0.03, 0.05, 0.4)
			if await _event(b, clip, "drop"):
				_pop_carried(hang)  # v51: the horn flicks the carried machines off at the top of the lift
		var slammed: bool = await _event(b, clip, "slam")
		if not slammed:
			_drop_carried()
			_end()  # the clip was cut (death, a swap) before the slam: no slam
			return
	else:
		await _wait_frame("ground_pound", POUND_SLAM_FRAME)
		sprite.hold_frame(POUND_SLAM_FRAME)
	var r := (_finale_r if _finale_r > 0.0 else finale_radius) if finale else pound_radius
	if finale:
		_glow_flash = 0.4  # the drum ring flashes on the slam
	var c := feet() + ahead() * 0.5 if finale else feet()
	var stomps := 0 if finale else tremor_stomps
	var life := stomps * tremor_interval + (patch_time if finale else tremor_linger)
	Fx3D.spawn(world(), "gp_ring", c, 0.6)
	KitFeel.ground_wave(world(), c, r, 0.45)
	Fx3D.spawn(world(), "impact_puff", c + ahead() * 0.5, 0.8)
	Fx3D.ground_decal(world(), "slow_disc.png", c, r * 2.0, life, 0.012)
	Fx3D.ground_decal(world(), "cracks.png", c, r * 1.7, life, 0.02)
	impact.emit(1.0 if finale else 0.7)
	var caught: Array = (_carried + _run_shoved) if finale else []  # carried and shoved units always take the finale
	if finale:
		_run_shoved = []
	_drop_carried()  # slice 3: the carried machines drop as the finale slams, inside its ring
	for t in targets():
		if flat(t.global_position - c).length() <= r or caught.has(t):
			t.hit(player)
			if finale:
				t.stun(_finale_stun if _finale_stun > 0.0 else stun_time)
			else:
				t.slow(pound_slow_time)
	_slow_patch(c, r, life)
	if b != null:
		b.freeze(hitstop)
		for i in stomps:  # the clip stomps on the tremor's beat (tremor_interval), so each stomp lands on its event
			var stomped: bool = await _event(b, clip, "stomp_%d" % (i + 1))
			if not stomped:
				break
			_stomp(c, r)
		await _clip_end(b, clip)
		_end()
		return
	await get_tree().create_timer(hitstop).timeout
	for i in stomps:  # timed here, not by the art: the art holds its rear (frame 3) 0.3 s, too slow to repeat
		var wait := tremor_interval - 0.12 - (hitstop if i == 0 else 0.0)
		await get_tree().create_timer(maxf(wait, 0.0)).timeout
		sprite.hold_frame(POUND_RISE_FRAME)  # a short lift, then down again
		await get_tree().create_timer(0.12).timeout
		sprite.hold_frame(POUND_SLAM_FRAME)
		_stomp(c, r)
	sprite.release_from(POUND_RISE_FRAME)
	await _wait_end("ground_pound")
	_end()


## One stomp of the tremor: a ring, dust kicked up across the circle and under everyone in it, and a smaller shake.
func _stomp(c: Vector3, r: float) -> void:
	KitFeel.ground_wave(world(), c, r)
	for i in 4:
		var a := randf() * TAU
		var d := sqrt(randf()) * r * 0.9
		var puff := Fx3D.spawn(world(), "impact_puff", c + Vector3(cos(a), 0.0, sin(a)) * d)
		puff.scale = Vector3.ONE * 0.6
	for t in targets():
		if flat(t.global_position - c).length() <= r:
			Fx3D.spawn(world(), "dust_trail", t.global_position, 0.3)
	cue.emit("tremor_stomp")
	impact.emit(0.35)


## Aftershock (slot 3). at: a point to aim at (the bots pass the nearest enemy's position); without one the aim, else
## the facing. The cast spends the cooldown; a stun or a hold during the wind-up cuts it with no refund. After the
## stomp the wave runs on its own while the rhino recovers. The 3D clip comes later from the rhino 3D lane (about
## 0.8 s, the stomp at about 0.35 s): until then the kit times it and plays an "aftershock" clip only if the body has one.
func aftershock(at: Variant = null) -> void:
	if current != "":
		return
	current = "aftershock"  # no drawn sprite action, so not _begin()
	player.busy = true
	used.emit("3")
	var dir := Vector3.ZERO
	if at is Vector3:
		dir = flat(at - feet())
	elif player.has_method("aim_dir"):
		dir = flat(player.aim_dir())
	if dir.length() < 0.1:
		dir = ahead()
	dir = dir.normalized()
	player.facing = dir
	var b := _body()
	if b != null and b.has_clip("aftershock"):
		_play(b, "aftershock")
	cue.emit("aftershock_windup")
	var t := 0.0
	while t < aftershock_windup:
		await get_tree().process_frame
		if not (is_instance_valid(player) and player.alive and float(player.get("stunned")) <= 0.0 and not player.has_meta("held_by")):
			_end()
			return
		t += get_process_delta_time()
	_aftershock_wave(feet(), dir)  # a coroutine left running: the wave travels while the rhino recovers
	t = 0.0
	while t < aftershock_recover and player.alive:
		await get_tree().process_frame
		t += get_process_delta_time()
	_end()


func stampede() -> void:
	if _tremor_running:
		if _tremor_t >= tremor_stop_after:
			_tremor_stop = true  # the second press ends the run here
		return
	if not _begin("stampede"):
		return
	used.emit("4")
	var tb := _body()
	if tb != null and tb.has_clip("stampede_windup"):
		await _tremor_charge(tb)
		return
	sprite.speed_scale = stampede_anim_speed
	var b := _body()
	if b != null:  # the charge loop held at the stampede's pace; the finale's pound replaces it
		var run := float(b.get("_run_speed"))
		b.play_hold("charge", stampede_speed / run if run > 0.0 else stampede_anim_speed)
	var dir := ahead()
	var side := dir.cross(Vector3.UP)
	var shoved := {}
	var gone := 0.0
	var dust := 0.0
	while gone < stampede_distance and float(player.get("grounded")) <= 0.0:  # grounded: into the pound where it is
		await get_tree().process_frame
		var step := minf(stampede_speed * get_process_delta_time(), stampede_distance - gone)
		player.global_position = ArenaMotion.slide(player, player.global_position, dir * step, player.body_radius())
		gone += step
		dust -= step
		if dust <= 0.0:
			dust = 0.8
			Fx3D.spawn(world(), "dust_trail", feet() - dir * 1.0)
		for t in targets():
			if shoved.has(t):
				continue
			var d := flat(t.global_position - feet())
			var across := d.dot(side)
			if d.dot(dir) > -0.5 and d.dot(dir) < 1.5 and absf(across) < stampede_width:
				shoved[t] = true
				t.knock_aside(side * (1.0 if across >= 0.0 else -1.0) * 2.6 + dir * 1.4, 0.4)
				Fx3D.spawn(world(), "hit_spark", t.global_position + Vector3.UP * 1.0, 0.4)
				impact.emit(0.4)
	current = ""
	sprite.speed_scale = 1.0
	await ground_pound(true)


func _slow_patch(c: Vector3, r: float, time: float) -> void:
	var left := time
	while left > 0.0:
		for t in targets():
			if flat(t.global_position - c).length() <= r:
				t.slow(0.25)
		await get_tree().process_frame
		left -= get_process_delta_time()


func _first_in_front(reach: float):
	var best = null
	var best_d := reach
	for t in targets():
		var d := flat(t.global_position - feet())
		if d.length() <= best_d and rad_to_deg(ahead().angle_to(d.normalized())) <= toss_cone_degrees:
			best = t
			best_d = d.length()
	return best


func _begin(anim: String) -> bool:
	if current != "":
		return false
	current = anim
	player.busy = true
	sprite.play_action(anim)
	return true


func _end() -> void:
	current = ""
	player.busy = false
	sprite.stop_action()


func _wait_frame(anim: String, f: int) -> void:
	while sprite.action == anim and sprite.frame < f and sprite.is_playing():
		await get_tree().process_frame


func _wait_end(anim: String) -> void:
	while sprite.action == anim and sprite.is_playing():
		await get_tree().process_frame


func _process(delta: float) -> void:
	_clock += delta
	_seismic_tick(delta)


## Seismic charge (rhino lane slice 1): one per blocked hit, at most one per attacker every seismic_gap; gate false for
## gains that are not hits (the Tremor charge's run).
func _gain_seismic(by: Variant = null, n := 1, gate := true) -> void:
	if gate:
		var key: Variant = by if by != null and is_instance_valid(by) else "?"
		if _clock - float(_seismic_from.get(key, -1000.0)) < seismic_gap:
			return
		_seismic_from[key] = _clock
	seismic = mini(seismic + n, SEISMIC_MAX)
	_seismic_last = _clock
	_seismic_decay = 0.0


## Drains one charge every seismic_decay_every once seismic_hold passes with no gain, and shows the charge on the drum
## ring: glow 1.6 + 1.1 a charge, the release flash to 9 easing back over 0.4 s.
func _seismic_tick(delta: float) -> void:
	if seismic > 0 and _clock - _seismic_last >= seismic_hold:
		_seismic_decay += delta
		if _seismic_decay >= seismic_decay_every:
			_seismic_decay = 0.0
			seismic -= 1
	var e := maxf(1.6 + 1.1 * seismic, _glow_floor)
	if _glow_flash > 0.0:
		_glow_flash = maxf(_glow_flash - delta, 0.0)
		var k := _glow_flash / 0.4
		e = lerpf(e, 9.0, k * k)
	if absf(e - _glow_set) > 0.01:
		var b: Variant = player.get("body")
		if b != null and is_instance_valid(b):
			LOOK.set_glow(b, e)
		_glow_set = e


## Aftershock's wave: the stomp spends the charge, and the front runs out from origin at aftershock_speed to the reach
## (aftershock_length + aftershock_length_per a charge). An enemy is hit when this frame's sweep of the front (last
## frame's front to this one) overlaps its body inside the cone, once, with a clear line from the stomp (walls are
## cover, as for Freight). One in the air while the front crosses it dodges, and the front does not come back for it;
## a held one is still hit. Nothing is pushed. The charge is spent here, so a cast cut in its wind-up keeps it.
func _aftershock_wave(origin: Vector3, dir: Vector3) -> void:
	var c := seismic
	seismic = 0
	_glow_flash = 0.4
	var reach := aftershock_length + aftershock_length_per * c
	var tan_half := tan(deg_to_rad(aftershock_half_angle))
	var hits: Array = []
	var dodged: Array = []
	last_aftershock = {"origin": origin, "dir": dir, "reach": reach, "charge": c, "half_angle": aftershock_half_angle,
			"speed": aftershock_speed, "front": 0.0, "hits": hits, "dodged": dodged}
	cue.emit("aftershock_wave")
	impact.emit(0.4 + 0.1 * c)
	var front := 0.0
	var dust := 0.0
	while front < reach:
		await get_tree().process_frame
		if not is_instance_valid(player):
			return
		var prev := front
		front = minf(front + aftershock_speed * get_process_delta_time(), reach)
		last_aftershock["front"] = front
		dust -= front - prev
		if dust <= 0.0:
			dust = 1.0
			Fx3D.spawn(world(), "dust_trail", origin + dir * front, 0.3)  # a stand-in until rhino effects draws the wave
		for e in targets():
			if not is_instance_valid(e) or hits.has(e):
				continue
			var d := flat(e.global_position - origin)
			var along := d.dot(dir)
			var r := _radius_of(e)
			if along <= 0.0 or along + r < prev or along - r > front:
				continue  # behind the stomp, or the front is not crossing it this frame
			if (d - dir * along).length() > along * tan_half + r:
				continue  # outside the cone
			if not MatchTeams.clear_line(player, origin, e.global_position):
				continue  # a wall or rock in between is cover (kit design, 2026-11-20); a cobra inside a wall is never reached
			if not e.has_meta("held_by") and e.has_method("is_airborne") and e.is_airborne():
				if not dodged.has(e):
					dodged.append(e)
				continue  # off the ground as the front passes: it dodges
			hits.append(e)
			_shock(e, c)
	cue.emit("aftershock_end")


## One enemy the wave reached: the damage, then (if it lives) the 30% slow and grounded on a machine, the plain slow
## on anything else that slows, and at full charge the stun.
func _shock(e: Node3D, c: int) -> void:
	var dmg := aftershock_damage + aftershock_damage_per * c
	if e.has_method("hit"):
		e.hit(player, dmg / MatchRules.kit_hit_damage)
	else:
		e.take_damage(dmg, player)
	last_aftershock_hit = e
	Fx3D.spawn(world(), "hit_spark", e.global_position + Vector3.UP * 0.8, 0.4)
	cue.emit("aftershock_hit")
	if e.get("alive") == false:
		return
	if e.has_method("ground"):
		e.slow(aftershock_slow_time, aftershock_slow)
		e.ground(aftershock_grounded + aftershock_grounded_per * c)
	elif e.has_method("slow"):
		e.slow(aftershock_slow_time)
	if c >= SEISMIC_MAX and e.has_method("stun"):
		e.stun(aftershock_stun)


static func _radius_of(e: Node3D) -> float:
	if e.has_method("body_radius"):
		return float(e.call("body_radius"))
	if e.has_method("radius"):
		return float(e.call("radius"))
	return 0.5


## The Tremor charge (rhino lane slice 2): the wind-up paws twice and ramps the drum ring, then on "go" the rhino runs
## up to tremor_distance, speeding up and steering toward the aim, shoving enemies aside as the old stampede did. A
## tremor pulse every tremor_pulse_every metres slows and damages around it, every tremor_charge_every metres adds a
## Seismic charge. It ends at full distance, on a second press, or against a wall, in the finale pound, which grows
## with the run and the charge and spends it.
func _tremor_charge(b: MechModel3D) -> void:
	_play(b, "stampede_windup")
	var w := 0.0
	while not _got.has("stampede_windup/go"):
		if not is_instance_valid(b) or b.action != "stampede_windup" or not player.alive:
			_glow_floor = 0.0
			_end()
			return
		await get_tree().process_frame
		w += get_process_delta_time()
		_glow_floor = lerpf(1.6, 5.5, clampf(w / 0.5, 0.0, 1.0))
	_glow_floor = 5.5
	var run := float(b.get("_run_speed"))
	run = run if run > 0.0 else 6.091
	b.play_hold("charge", tremor_speed_start / run, 0.1)
	var dir := ahead()
	var shoved := {}
	var dust := 0.0
	var next_pulse := tremor_pulse_every
	var next_charge := tremor_charge_every
	tremor_gone = 0.0
	last_walled = false
	_tremor_t = 0.0
	_tremor_stop = false
	_tremor_running = true
	_drop_carried()
	last_carried = 0
	_run_shoved = []
	while tremor_gone < tremor_distance - 0.01 and not _tremor_stop and player.alive and float(player.get("grounded")) <= 0.0:  # grounded: the finale where it is
		await get_tree().process_frame
		var dt := get_process_delta_time()
		_tremor_t += dt
		var v := lerpf(tremor_speed_start, tremor_speed_end, clampf(_tremor_t / tremor_ramp, 0.0, 1.0))
		var aim: Vector3 = flat(player.aim_dir()) if player.has_method("aim_dir") else Vector3.ZERO
		if aim.length() > 0.1:
			var turn := dir.signed_angle_to(aim.normalized(), Vector3.UP)
			var most := deg_to_rad(tremor_steer_deg) * dt
			dir = dir.rotated(Vector3.UP, clampf(turn, -most, most)).normalized()
		player.facing = dir
		if is_instance_valid(b):
			b.set_action_rate(v / run)
		var step := minf(v * dt, tremor_distance - tremor_gone)
		var was: Vector3 = player.global_position
		player.global_position = ArenaMotion.slide(player, was, dir * step, player.body_radius())
		var moved := flat(player.global_position - was).length()
		tremor_gone += moved
		if step > 0.001 and moved < step * 0.3:
			last_walled = true  # a wall stops the run: straight into the finale
			break
		if _hold_carried(dir):
			last_walled = true  # a carried machine met a wall: the run stops there
			break
		while tremor_gone >= next_pulse - 0.01:
			next_pulse += tremor_pulse_every
			_tremor_pulse()
		while tremor_gone >= next_charge - 0.01:
			next_charge += tremor_charge_every
			_gain_seismic(null, 1, false)
		dust -= moved
		if dust <= 0.0:
			dust = 0.8
			Fx3D.spawn(world(), "dust_trail", feet() - dir * 1.0)
		var side := dir.cross(Vector3.UP)
		for t in targets():
			if shoved.has(t) or not is_instance_valid(t):
				continue
			var d := flat(t.global_position - feet())
			var across := d.dot(side)
			if d.dot(dir) > -0.5 and d.dot(dir) < (1.5 if _carried.is_empty() else tremor_carry_ahead + 1.0) and absf(across) < stampede_width:
				shoved[t] = true
				if tremor_carry and _carriable(t):
					if t._braced():
						last_walled = true  # a braced machine is not carried: it stops the run like a wall
						_tremor_stop = true
						Fx3D.spawn(world(), "hit_spark", t.global_position + Vector3.UP * 1.0, 0.4)
						impact.emit(0.6)
						break
					_catch(t, across)
					continue
				_run_shoved.append(t)
				if t.get_method_argument_count("knock_aside") >= 3:
					t.knock_aside(side * (1.0 if across >= 0.0 else -1.0) * 2.6 + dir * 1.4, 0.4, false)  # push only; the run's damage is the pulses and the finale
				else:
					t.knock_aside(side * (1.0 if across >= 0.0 else -1.0) * 2.6 + dir * 1.4, 0.4)
				Fx3D.spawn(world(), "hit_spark", t.global_position + Vector3.UP * 1.0, 0.4)
				impact.emit(0.4)
	_tremor_running = false
	_tremor_stop = false
	_glow_floor = 0.0
	var k := clampf(tremor_gone / tremor_distance, 0.0, 1.0)
	_finale_r = finale_radius + tremor_finale_grow * k + tremor_finale_per_charge * seismic
	_finale_stun = tremor_stun + tremor_stun_grow * k + tremor_stun_per_charge * seismic
	last_finale_r = _finale_r
	last_finale_stun = _finale_stun
	seismic = 0  # the finale spends the charge
	current = ""
	sprite.speed_scale = 1.0
	if player.alive:
		await ground_pound(true)
	else:
		_drop_carried()
		_end()
	_drop_carried()
	_finale_r = -1.0
	_finale_stun = -1.0


## Slice 3: whether the Tremor run carries this target: an enemy machine (not a minion or a structure) nobody else holds.
func _carriable(t: Node) -> bool:
	return t.has_method("_braced") and t.has_method("stun") and t.get("alive") != false and not t.has_meta("held_by")


## Catches a machine on the horn: it is held (held_by, so it cannot move or act) until the finale's slam.
func _catch(t: Node, across: float) -> void:
	t.set_meta("held_by", player)
	if t.has_method("halt"):
		t.halt()
	_carried.append(t)
	_carry_side[t] = clampf(across, -tremor_carry_spread, tremor_carry_spread)
	_carry_now[t] = Vector2(flat(t.global_position - feet()).dot(ahead()), across)
	_spread()
	last_carried += 1
	Fx3D.spawn(world(), "hit_spark", t.global_position + Vector3.UP * 1.0, 0.5)
	impact.emit(0.5)
	cue.emit("horn_catch")
	if t.has_method("held_pose"):
		t.held_pose()


## Two or more carried machines sit side by side, in the order they were caught across the run, a body apart.
func _spread() -> void:
	var n := _carried.size()
	if n < 2:
		return  # one machine keeps its own side
	var order := _carried.duplicate()
	order.sort_custom(func(x, y) -> bool: return float(_carry_side.get(x, 0.0)) < float(_carry_side.get(y, 0.0)))
	var gap := 0.0
	for t in order:
		gap = maxf(gap, 2.0 * (t.body_radius() if t.has_method("body_radius") else 0.8) + 0.3)
	for i in n:
		_carry_side[order[i]] = (i - (n - 1) / 2.0) * gap


## v51 horn lift (rhino lane; Preston, "Yes, add it"): on the finale's drop event the carried machines leave the horn in a
## short hop, up and a little forward, landing just before the slam. They stay held until the slam, which always hits them.
func _pop_carried(hang: float) -> void:
	var f := ahead()
	for t in _carried:
		if not is_instance_valid(t):
			continue
		var r: float = t.body_radius() if t.has_method("body_radius") else 0.8
		var p0: Vector3 = t.global_position
		var p1: Vector3 = ArenaMotion.slide(t, p0, f * tremor_drop_forward, r)
		create_tween().tween_method(_pop_step.bind(t, p0, p1), 0.0, 1.0, hang)


func _pop_step(s: float, t: Node3D, p0: Vector3, p1: Vector3) -> void:
	if is_instance_valid(t) and _carried.has(t):
		var at := p0.lerp(p1, s)
		at.y = p0.y + 4.0 * tremor_drop_height * s * (1.0 - s)
		t.global_position = at


## The time of a clip's event on the body, or -1 when the clip has no such event.
func _clip_time(b: MechModel3D, clip: String, n: String) -> float:
	for e in b.events_of(clip):
		if e is Array and e.size() >= 2 and str(e[0]) == n:
			return float(e[1])
	return -1.0


## Holds each carried machine tremor_carry_ahead metres ahead of the rhino. True when one of them is stopped by a wall.
func _hold_carried(dir: Vector3) -> bool:
	var side := dir.cross(Vector3.UP)
	var blocked := false
	for t in _carried.duplicate():
		if not is_instance_valid(t) or t.get("alive") == false:
			_let_go(t)
			continue
		var r: float = t.body_radius() if t.has_method("body_radius") else 0.8
		var place := Vector2(maxf(tremor_carry_ahead, player.body_radius() + r + 0.4), float(_carry_side.get(t, 0.0)))
		var now: Vector2 = _carry_now.get(t, place)
		now = now.move_toward(place, tremor_carry_settle * get_process_delta_time())
		_carry_now[t] = now
		var want: Vector3 = feet() + dir * now.x + side * now.y
		var at: Vector3 = t.global_position
		t.global_position = ArenaMotion.slide(t, at, flat(want - at), r)
		if flat(want - t.global_position).length() > 0.6:
			blocked = true
	return blocked


func _let_go(t) -> void:
	if is_instance_valid(t) and t.has_meta("held_by") and t.get_meta("held_by") == player:
		t.remove_meta("held_by")
	_carried.erase(t)
	_carry_side.erase(t)
	_carry_now.erase(t)


func _drop_carried() -> void:
	for t in _carried.duplicate():
		_let_go(t)


## One tremor pulse of the run: everyone within tremor_pulse_radius takes the damage once and is slowed.
func _tremor_pulse() -> void:
	var c := feet()
	for t in targets():
		if not is_instance_valid(t) or (flat(t.global_position - c).length() > tremor_pulse_radius and not _carried.has(t)):
			continue
		if t.has_method("hit"):
			t.hit(player, tremor_pulse_damage / MatchRules.kit_hit_damage)
		else:
			t.take_damage(tremor_pulse_damage, player)
		if t.get("alive") != false and t.has_method("slow"):
			t.slow(tremor_pulse_slow)
	tremor_pulses += 1
	_glow_flash = 0.4
	KitFeel.ground_wave(world(), c, tremor_pulse_radius, 0.3)
	cue.emit("tremor_pulse")
	impact.emit(0.25)


func _body() -> MechModel3D:
	var b: Variant = player.get("body")
	if not (b is MechModel3D) or not is_instance_valid(b) or not b.has_clip("horn_hook"):
		return null
	if _ev_body != b:
		_ev_body = b
		b.event.connect(_on_body_event.bind(b))
	return b


func _on_body_event(clip: String, n: String, _damage: bool, b: MechModel3D) -> void:
	if b == _ev_body:
		_got[clip + "/" + n] = true


## Plays clip on the body with its events counted afresh.
func _play(b: MechModel3D, clip: String, speed := 1.0) -> void:
	for k in _got.keys():
		if String(k).begins_with(clip + "/"):
			_got.erase(k)
	b.play_action(clip, speed)


## Waits until the body's clip passes event n. False when the clip ended or was replaced first, or the rhino died.
func _event(b: MechModel3D, clip: String, n: String) -> bool:
	while is_instance_valid(b) and player.alive and not _got.has(clip + "/" + n):
		if b.action != clip:
			return false
		await get_tree().process_frame
	return is_instance_valid(b) and player.alive and _got.has(clip + "/" + n)


func _clip_end(b: MechModel3D, clip: String) -> void:
	while is_instance_valid(b) and b.action == clip and player.alive:
		await get_tree().process_frame
