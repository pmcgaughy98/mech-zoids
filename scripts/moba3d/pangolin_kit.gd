class_name PangolinKit
extends Node
## The pangolin's kit on its rigged 3D body (game feel lane, 2026-11-12). Spec: docs/plan/pangolin-kit-fun-pass-2026-11-12.md,
## the kit redo Preston approved on 2026-11-12 (relayed by the pangolin effects lane: "Approved").
##
## Slice 1, slot 2, the iron ball: Curl_In, then Ball_Roll held while the kit rolls the machine. It starts at
## ball_start_speed and builds to ball_max_speed, steered by the move input (or steer_to for bots and probes) at ball_turn.
## Off a wall it bounces and keeps ball_bounce_keep of its speed (the spec: within 10 percent). Minions are bowled aside
## (bowl_push, bowl_damage) and do not stop it. The first enemy machine it reaches ends the roll: one kit hit plus up to
## ball_bonus_damage, and it is tossed up and stunned, higher and longer the faster the ball was going. Then Curl_Out.
## The wall test is the same sphere sweep every machine moves with (ArenaMotion.slide): where the sweep turns the move,
## the turn gives the wall's normal, and the roll is reflected about it.
##
## Slice 2 (Preston, 2026-11-12: "Yes, slice 2"), slot 1, salvage: the Salvage clip. At the cast the enemy machines in
## a short cone in front (salvage_range from the pangolin's middle, salvage_half_angle) are its salvage_targets; on the
## clip's "field" event each takes salvage_damage, loses its plates (takes salvage_shred more damage) and is magnetised,
## and the pangolin wears the plates (takes salvage_gain less per machine, down to salvage_gain_cap), all for
## salvage_time. Armour is machine_test_player's `armour`, a multiplier on every damage taken (set_armour).
## Magnetised: mag_time seconds. While the ball rolls, the nearest magnetised enemy ahead within mag_pull_range bends
## the roll toward it at mag_turn, on top of the steering (the spec: "magnetised enemies pull its path toward them").
## Near-field snap (Preston's pick, 2026-11-18): the bend rate is mag_turn x clamp((mag_snap_ref / d)^2, 1, mag_snap_cap),
## d the flat distance to it, so 1.6 rad/s out to 4 m, about 2.8 at 3 m, and the 4.8 rad/s lock from about 2.3 m in.
## Only the ball's path bends; nothing moves the enemy.
##
## Slice 3 (Preston, 2026-11-13: "Yes, slice 3"), slot 3, scale flare: the Scale_Flare clip. On its "flare" event every
## enemy within flare_radius of the pangolin takes flare_damage, and the scales stay up for flare_time: they block the
## next flare_block_count kit hits (take_hit: a blocked hit does MatchRules.blocked_share), and each attacker blocked is
## magnetised. Flared while rolling (key 3 mid-roll, no clip): the ball is spiked, and the hit that ends the roll also
## does flare_damage to every enemy within flare_radius of the target (cue spike_burst at spike_at). The scales are up
## for the rest of the roll too. flare_radius and flare_time match pangolin_fx FLARE_R and FLARE_LIFE.
##
## Bank-shot charge (Preston, 2026-11-14: "A, bank-shot charge"; docs/plan/pangolin-kit-roll-ideas-2026-11-14.md): each
## wall bounce of the iron ball adds a charge, up to ball_max_charges: charge_speed more speed and top speed, and
## charge_damage more on the crash (cue ball_charge, after charges rises). 2 again mid-roll pops: the ball uncurls early
## and every enemy within pop_radius takes pop_damage and is lifted pop_lift (cue ball_pop with pop_at, then ball_end).
## charges is back to 0 once the pangolin has uncurled.
## Basic, the "Pry" chain (2026-11-18, option A): left swipe, right swipe, then a two-claw pry that hits the whole arc
## and refreshes magnetise (see the basic section). Not built yet: the sharp-scales passive.
##
## pangolin_fx.gd (the effects lane) reads rolling, roll_speed, roll_dir, hit_speed, hit_at and the cues ball_start,
## ball_hit, ball_end. New for slot 2: cues ball_roll, ball_bounce (bounce_at), ball_bowl (bowl_at). Keep these names.

signal impact(strength: float) ## something landed; KitFeel shakes the camera on it
signal used(slot: String) ## the director starts the slot's cooldown (MatchRules)
signal cue(name: String) ## ball_start, ball_roll, ball_bounce, ball_bowl, ball_hit, ball_end, salvage, magnetise,
## flare_block, flare_end, ball_spiked, spike_burst; swipe (beat_target), pry (pry_targets), mag_refresh (refreshed),
## mag_snap (mag_snapped: the roll's bend first reaching mag_snap_cap on that target)

const FX_SCRIPT := "res://scripts/moba3d/pangolin_fx.gd"
const ROLL_CLIP_SPEED := 7.74 ## m/s that Ball_Roll is authored at (pangolin.events.json roll_speed; 7.67 before round 11)
const SPIKED_CLIP_SPEED := 8.42 ## Ball_Roll_Spiked: the same 0.50 s turn, riding on its spikes
const COMET_CLIP_SPEED := 8.63 ## Comet_Roll at normal size; the comet's rate also divides by comet_size
const SPARK_UP := 0.6 ## spark height on the target
const BOUNCE_MIN := 0.02 ## metres the sweep must turn a move by before it counts as a wall

@export var ball_start_speed := 4.0 ## m/s when the shell closes
@export var ball_max_speed := 12.0
@export var ball_accel := 5.0 ## m/s gained per second of rolling
@export var ball_time := 3.0 ## the longest roll, seconds
@export var ball_turn := 2.2 ## rad/s the roll turns toward the steering
@export var ball_bounce_keep := 0.95 ## share of the speed kept off a wall
@export var ball_max_charges := 3 ## bank-shot charges, one per wall bounce
@export var charge_speed := 1.5 ## m/s each charge adds to the roll and to its top speed
@export var charge_damage := 15.0 ## each charge adds this to the crash
@export var pop_radius := 2.2 ## the recast pop: metres from the pangolin's centre to an enemy's edge
@export var pop_damage := 30.0
@export var pop_lift := 1.5 ## metres, the knock-up
@export var pop_time := 0.5 ## seconds in the air
var charges := 0 ## the iron ball's bank-shot charges; pangolin_fx reads it
var hit_damage := 0.0 ## the last crash's damage on top of the toss's kit hit, for the checks
var pop_at := Vector3.ZERO
var pops := 0 ## enemies the last pop lifted, for the checks
var _pop := false
@export var ball_reach := 0.3 ## metres past the shell's edge that count as contact
@export var ball_bonus_damage := 40.0 ## on top of the toss's one kit hit, at full speed
@export var ball_lift_min := 0.6 ## toss height at the start speed
@export var ball_lift_max := 2.2 ## at full speed
@export var ball_stun_min := 0.4
@export var ball_stun_max := 1.0
@export var ball_toss_time := 0.55
@export var ball_toss_carry := 0.8 ## metres the tossed machine is carried along the roll
@export var bowl_push := 1.8 ## metres a minion is thrown aside
@export var bowl_damage := 20.0
@export var salvage_range := 4.0 ## the pangolin's middle to the target's edge (MatchTeams.edge_distance)
@export var salvage_half_angle := 40.0
@export var salvage_damage := 40.0
@export var salvage_shred := 1.15 ## a stripped machine takes this much damage
@export var salvage_gain := 0.1 ## the pangolin takes this much less per machine stripped
@export var salvage_gain_cap := 0.7 ## never below this share of the damage
@export var salvage_time := 4.0 ## seconds the plates stay stolen (pangolin_fx reads it)
@export var mag_time := 4.0 ## seconds an enemy stays magnetised (pangolin_fx reads it)
@export var mag_pull_range := 10.0 ## metres: a magnetised enemy this close bends the roll
@export var mag_turn := 1.6 ## rad/s the roll bends toward it, on top of the steering (from mag_snap_ref out)
@export var mag_snap_ref := 4.0 ## metres: closer than this the bend grows as (mag_snap_ref / d)^2
@export var mag_snap_cap := 3.0 ## the most it grows: 3 x 1.6 = 4.8 rad/s, reached at about 2.3 m (the snap)
@export var flare_damage := 50.0
@export var flare_radius := 2.5 ## metres from the pangolin's middle (or the spiked ball's target) to an enemy's edge; pangolin_fx FLARE_R
@export var flare_block_count := 2 ## kit hits the raised scales block
@export var flare_time := 3.0 ## seconds the scales stay up; pangolin_fx FLARE_LIFE
@export var fx_on := true

var current := "" ## the arena's swap guard reads this (arena_play)
var busy_with := ""
var rolling := false
var roll_speed := 0.0
var roll_dir := Vector3(0, 0, -1)
var hit_speed := 0.0
var hit_at := Vector3.ZERO
var hit_target: Node3D = null ## for the checks
var bounces := 0 ## this roll, for the checks
var bounce_at := Vector3.ZERO
var bowls := 0 ## this roll, for the checks
var bowl_at := Vector3.ZERO
var steer_to := Vector3.ZERO ## a bot or probe steers with this; zero: the move input
var salvage_targets: Array = [] ## the machines the last salvage cone took (pangolin_fx reads it on cue "salvage")
var plates_worn := 0 ## machines stripped by the last salvage, for the checks
var mag_target: Node3D = null ## the last enemy magnetised (pangolin_fx reads it on cue "magnetise")
var mag_pull: Node3D = null ## the magnetised enemy bending the roll this frame, for the checks
var mag_mult := 1.0 ## this frame's bend multiplier, 1 to mag_snap_cap (pangolin_fx can read it for the pull line's tautness)
var mag_snapped: Node3D = null ## the target the bend is at the cap on (cue "mag_snap" when it first gets there)
var _mag_until := {} ## enemy -> _clock time its mark runs out
var _clock := 0.0
var flared := false ## the scales are up and blocking
var flare_blocks := 0 ## blocks left (pangolin_fx reads it)
var block_at := Vector3.ZERO ## where the last blocked hit glanced off (pangolin_fx reads it on cue "flare_block")
var flare_hits := 0 ## enemies the last standing flare hit, for the checks
var spiked := false ## flared while rolling: the crash bursts
var spike_at := Vector3.ZERO ## the spiked crash's burst centre (cue "spike_burst")
var _flare_token := 0
## The basic, the "Pry" chain (option A of docs/plan/pangolin-basic-attack-2026-11-18.md; Preston, 2026-11-18: "The
## short reach is fine, build A"): left swipe, right swipe, pry. Reach is centre to edge (MatchTeams.edge_distance),
## measured in Blender (pangolin 3D lane, corrected 2026-11-18): the swipes' claw tips reach 1.29 m; at the pry's
## impact (r13 clip) the claws are 1.15 to 1.19 m out, about 1.48 m with the lunge. Preston kept 1.6 / 1.9 m (2026-11-18).
@export var basic_range := 1.6 ## the swipes' reach; the director and the bots read it
@export var basic_cooldown := 0.75 ## set per beat before each one starts (the director reads it after basic_attack)
@export var swipe_damage := 23.0 ## beats 1 and 2, the nearest enemy in the arc
@export var swipe_half_angle := 35.0
@export var swipe_gap := 0.75 ## seconds until the next beat after a swipe (0.50 s clip + 0.25 s to move)
@export var pry_range := 1.9 ## beat 3, including the 0.3 m lunge
@export var pry_lunge := 0.3 ## metres the body lunges forward on the drop (visual: the clip is built in place, the reach already counts it)
@export var pry_lunge_at := 0.27 ## seconds into Claw_Rake the drop starts; the lunge eases out from here to arrive with the impact
@export var pry_lunge_back := 0.3 ## seconds it eases back after the impact
@export var pry_half_angle := 60.0
@export var pry_damage := 30.0 ## every enemy in the arc
@export var pry_hit_time := 0.375 ## seconds into Claw_Rake: the r13 clip's one impact, both claws on the floor (r13 in the arena since 2026-11-19, sha 1d8c5cc6)
@export var pry_gap := 1.1 ## seconds until beat 1 after the pry (0.80 s clip + 0.30 s)
@export var chain_reset := 1.5 ## this long after the last beat swung (its hit time passed, hit or whiff), the chain starts over at beat 1
const CHAIN := ["Basic_Left", "Basic_Right", "Claw_Rake"]
var beat := 0 ## the next beat, 0 to 2 (the probes and pangolin_fx read it)
var beat_target: Node3D = null ## a swipe's victim, set before cue "swipe"
var pry_targets: Array = [] ## the pry's victims, set before cue "pry"
var refreshed: Array = [] ## magnetised enemies the pry refreshed, set before cue "mag_refresh"
var _last_hit := -1000.0
var _swing_token := 0
var _bowled: Array = []
var _ev_body: MechModel3D = null
var _got: Dictionary = {}
var _fx_hung := false

@onready var player = get_parent() ## machine_test_player.gd


## Turns a field Player into the pangolin. Loaded by path, not by class_name (the fennec kit's note on the class cache).
static func install(p: Node3D) -> Node:
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var spr: Variant = p.get("sprite")
	if spr != null and spr.has_method("stop_action"):
		spr.stop_action()
	var kit: Node = load("res://scripts/moba3d/pangolin_kit.gd").new()
	kit.name = "Kit"
	p.add_child(kit)
	return kit


static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


func _process(delta: float) -> void:
	_clock += delta


## The next machine is never left busy by a roll cut short.
func _exit_tree() -> void:
	comet = false
	rolling = false
	spiked = false
	flared = false
	if is_instance_valid(player) and busy_with != "":
		player.busy = false
	busy_with = ""
	current = ""


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo or not is_instance_valid(player) or player.get("bot"):
		return
	if k.physical_keycode < KEY_1 or k.physical_keycode > KEY_4:
		return
	if k.physical_keycode == KEY_2 and pop():
		return  # 2 again mid-roll: the recast pop, free
	if player.has_method("slot_ready") and not player.slot_ready(str(k.physical_keycode - KEY_0)):
		return  # in a match a slot waits out its cooldown (MatchRules)
	match k.physical_keycode:
		KEY_4:
			scrap_comet()
		KEY_1:
			salvage()
		KEY_2:
			iron_ball()
		KEY_3:
			scale_flare()  # mid-roll it spikes the ball


# ---- the 3D body ---------------------------------------------------------------------------------------------------

## The rigged body once the match has attached it (use_model runs after install), or null. Hangs the effects once.
func _body() -> MechModel3D:
	var b: Variant = player.get("body") if is_instance_valid(player) else null
	if not (b is MechModel3D) or not is_instance_valid(b) or not b.has_clip("Ball_Roll"):
		return null
	if _ev_body != b:
		_ev_body = b
		b.event.connect(_on_body_event.bind(b))
	if fx_on and not _fx_hung:
		_fx_hung = true
		var script: Variant = load(FX_SCRIPT) if ResourceLoader.exists(FX_SCRIPT) else null
		if script is Script and script.can_instantiate():  # an effects file that fails to compile is skipped, not fatal
			var fx: Node = script.new()
			fx.name = "PangolinFx"
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


## Waits for the body's clip to fire event n. False when the clip ended or was replaced first, or the pangolin died.
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
	return d.normalized()


func _hit(victim: Node3D, damage: float, dir: Vector3, shake: float) -> void:
	var r: float = victim.radius() if victim.has_method("radius") else 0.0
	if damage > 0.5:
		victim.hit(player, damage / MatchRules.kit_hit_damage)
	Fx3D.spawn(player.get_parent(), "hit_spark", victim.global_position - dir * r + Vector3.UP * SPARK_UP, 0.0)
	impact.emit(shake)


# ---- basic: the "Pry" chain -----------------------------------------------------------------------------------------
## Quick, quick, heavy. Each beat plays its clip toward the target (a bot's pick) or the aim and lands on its hit time:
## the swipes on the clip's "hit" event (0.20 s), the pry at pry_hit_time. Only a landed hit moves the chain on.
## Moving before the hit stops the clip and the beat is lost (the next basic tries the same beat); moving after it
## cuts the recovery and keeps the chain. A whiff (nobody in the arc) still moves the chain on, as a swing at the air.
## The pry refreshes magnetise on every magnetised enemy it hits, back to the full mag_time; it never applies it
## (Salvage stays the only way to magnetise) and it does not touch the stolen plates.

func basic_attack(target: Node3D = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or player.busy or not player.alive \
			or player.has_meta("held_by") or b.action != "":
		return false
	if _clock - _last_hit > chain_reset:
		beat = 0
	var dir := _aim(target)
	var clip: String = CHAIN[beat]
	basic_cooldown = pry_gap if beat == 2 else swipe_gap
	player.facing = dir
	_swing_token += 1
	_play(b, clip)
	_beat(b, clip, beat, dir, target, _swing_token)
	return true


func _beat(b: MechModel3D, clip: String, n: int, dir: Vector3, target: Node3D, token: int) -> void:
	var t0 := _clock
	var lunged := false
	while true:  # the wind-up: wait for the hit, and moving before it loses the beat
		await get_tree().process_frame
		if token != _swing_token or not is_instance_valid(b) or not player.alive or b.action != clip:
			return
		if _moving():
			b.stop_action()
			return
		if n == 2 and not lunged and _clock - t0 >= pry_lunge_at:
			lunged = true
			b.lunge(dir * pry_lunge, pry_hit_time - (_clock - t0), pry_lunge_back)  # the lunge on the drop
		if (n == 2 and _clock - t0 >= pry_hit_time) or (n < 2 and int(_got.get(clip + "/hit", 0)) >= 1):
			break
	beat = (n + 1) % CHAIN.size()
	_last_hit = _clock
	if n < 2:
		beat_target = target if MatchTeams.hittable(target) and _in_arc(target, dir, basic_range, swipe_half_angle) \
				else _arc_pick(dir, basic_range, swipe_half_angle)
		if beat_target != null:
			_basic_hit(beat_target, swipe_damage, dir, 0.6)
		cue.emit("swipe")
	else:
		pry_targets = []
		refreshed = []
		for e in MatchTeams.enemies_of(player):
			if is_instance_valid(e) and MatchTeams.hittable(e) and _in_arc(e, dir, pry_range, pry_half_angle):
				pry_targets.append(e)
				if is_magnetised(e):
					_mag_until[e] = _clock + mag_time
					refreshed.append(e)
		for e in pry_targets:
			_basic_hit(e, pry_damage, dir, 1.0)
		cue.emit("pry")
		if not refreshed.is_empty():
			cue.emit("mag_refresh")
	while is_instance_valid(b) and b.action == clip and player.alive and token == _swing_token:
		if _moving():
			b.stop_action()  # moving after the hit cuts the recovery; the chain stays
			return
		await get_tree().process_frame


func _moving() -> bool:
	return player.has_method("move_dir") and (player.move_dir() as Vector3).length() > 0.1


func _in_arc(e: Node3D, dir: Vector3, reach: float, half_angle: float) -> bool:
	if MatchTeams.edge_distance(player, e) > reach:
		return false
	var to := flat(e.global_position - player.global_position)
	return to.length() < 0.3 or to.normalized().dot(dir) >= cos(deg_to_rad(half_angle))


## The nearest enemy in the arc, machines before minions.
func _arc_pick(dir: Vector3, reach: float, half_angle: float) -> Node3D:
	var best: Node3D = null
	var best_key := INF
	for e in MatchTeams.enemies_of(player):
		if not is_instance_valid(e) or not MatchTeams.hittable(e) or not _in_arc(e, dir, reach, half_angle):
			continue
		var key: float = MatchTeams.edge_distance(player, e) + (100.0 if e.get("kind") == "minion" else 0.0)
		if key < best_key:
			best_key = key
			best = e
	return best


## Machines take a kit hit (plating, shields and stolen plates apply); towers and cores take the damage straight.
func _basic_hit(t: Node3D, damage: float, dir: Vector3, strength: float) -> void:
	if t.has_method("hit"):
		t.hit(player, damage / MatchRules.kit_hit_damage)
	elif t.has_method("take_damage"):
		t.take_damage(damage, player)
	KitFeel.basic_hit(player, t, dir, strength)


# ---- 2, iron ball --------------------------------------------------------------------------------------------------

## Curls up and rolls toward the target (a Node3D, a point, or the mouse aim). True if it started.
func iron_ball(target: Variant = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or not player.alive or player.has_meta("held_by"):
		return false
	used.emit("2")
	var dir := _aim(target)
	_start("Iron_Ball", dir)
	roll_dir = dir
	roll_speed = 0.0
	hit_target = null
	bounces = 0
	bowls = 0
	charges = 0
	_pop = false
	_bowled.clear()
	mag_pull = null
	mag_mult = 1.0
	mag_snapped = null
	cue.emit("ball_start")
	_play(b, "Curl_In")
	await _event(b, "Curl_In", "closed")
	var crashed := false
	if _can_roll(b):
		rolling = true
		roll_speed = ball_start_speed
		b.play_hold("Ball_Roll", roll_speed / _roll_clip_speed("Ball_Roll"))
		cue.emit("ball_roll")
		var left := ball_time
		while left > 0.0:
			await get_tree().process_frame
			if not _can_roll(b) or _pop or _grounded():
				break  # grounded (Aftershock): the roll ends here into its Curl_Out, no refund
			var dt := get_process_delta_time()
			left -= dt
			_steer(dt)
			roll_speed = minf(roll_speed + ball_accel * dt, ball_max_speed + charge_speed * charges)
			var clip := _roll_clip(b)
			if b.action != clip:
				_swap_roll(b, clip)  # spiked mid-roll, or a hit react cut in: back to rolling
			b.set_action_rate(roll_speed / _roll_clip_speed(clip))
			var nb := bounces
			_roll_step(dt)
			if bounces > nb:
				_charge()
			player.facing = roll_dir
			var foe := _contact()
			if foe != null:
				_crash(foe)
				crashed = true
				break
		rolling = false
		if _pop and is_instance_valid(player) and player.alive:
			_do_pop()
	spiked = false
	if not crashed:
		cue.emit("ball_end")
	if is_instance_valid(b) and is_instance_valid(player) and player.alive:
		_play(b, "Curl_Out")
		await _clip_end(b, "Curl_Out")
	charges = 0
	_pop = false
	_finish("Iron_Ball")
	return true


func _can_roll(b: MechModel3D) -> bool:
	return is_instance_valid(b) and is_instance_valid(player) and player.alive and not player.has_meta("held_by") \
			and float(player.get("stunned")) <= 0.0


## Grounded by the rhino's Aftershock (2026-11-20): the ball and the comet stop rolling into their normal ending.
func _grounded() -> bool:
	return is_instance_valid(player) and float(player.get("grounded")) > 0.0


func _steer(dt: float, rate := -1.0) -> void:
	if rate < 0.0:
		rate = ball_turn
	var want := steer_to
	if want == Vector3.ZERO and player.has_method("move_dir"):
		want = player.move_dir()
	want = flat(want)
	if want.length() >= 0.1:
		var turn := clampf(roll_dir.signed_angle_to(want.normalized(), Vector3.UP), -rate * dt, rate * dt)
		roll_dir = roll_dir.rotated(Vector3.UP, turn).normalized()
	mag_pull = _nearest_magnetised()
	if mag_pull == null:
		mag_mult = 1.0
		mag_snapped = null
		return
	var to := flat(mag_pull.global_position - player.global_position)
	mag_mult = clampf(pow(mag_snap_ref / maxf(to.length(), 0.01), 2.0), 1.0, mag_snap_cap)
	if mag_mult < mag_snap_cap:
		mag_snapped = null
	elif mag_snapped != mag_pull:
		mag_snapped = mag_pull
		cue.emit("mag_snap")
	var pull_rate := mag_turn * mag_mult  # _steer's own `rate` is the steering's
	var bend := clampf(roll_dir.signed_angle_to(to.normalized(), Vector3.UP), -pull_rate * dt, pull_rate * dt)
	roll_dir = roll_dir.rotated(Vector3.UP, bend).normalized()


## One frame of rolling through the arena's walls. A move the sweep turned means a wall: the turn's direction is the
## wall's normal (the slide removes the move's part into the wall), and the roll reflects about it.
func _roll_step(dt: float, r := -1.0) -> void:
	if r < 0.0:
		r = player.radius()  # the iron ball; the scrap comet passes its bigger radius
	var from: Vector3 = player.global_position
	var want := roll_dir * roll_speed * dt
	var to: Vector3 = ArenaMotion.slide(player, from, want, r)
	var turned := flat(to - from) - want
	if turned.length() > BOUNCE_MIN:
		var n := turned.normalized()
		if roll_dir.dot(n) < 0.0:
			roll_dir = (roll_dir - 2.0 * roll_dir.dot(n) * n).normalized()
			roll_speed *= ball_bounce_keep
			bounces += 1
			bounce_at = to - n * r
			cue.emit("ball_bounce")
			impact.emit(0.25)
	player.global_position = to


## The first enemy machine the shell reaches, ahead of it. Minions on the way are bowled aside instead.
func _contact() -> Node3D:
	var r: float = player.radius()
	for e in MatchTeams.enemies_of(player):
		if not is_instance_valid(e) or not MatchTeams.hittable(e):
			continue
		if MatchTeams.edge_distance(player, e) - r > ball_reach:
			continue  # edge_distance is the pangolin's middle to the target's edge
		if e.get("kind") == "minion":
			if not _bowled.has(e):
				_bowl(e)
			continue
		if flat(e.global_position - player.global_position).dot(roll_dir) < 0.0:
			continue  # behind the shell: it rolled away from it
		return e
	return null


func _bowl(m: Node3D) -> void:
	_bowled.append(m)
	var side := roll_dir.cross(Vector3.UP).normalized()
	if flat(m.global_position - player.global_position).dot(side) < 0.0:
		side = -side
	_hit(m, bowl_damage, roll_dir, 0.1)
	if m.has_method("knock_aside"):
		m.knock_aside(side * bowl_push + roll_dir * 0.4, 0.25, false)
	bowls += 1
	bowl_at = m.global_position
	cue.emit("ball_bowl")


func _crash(e: Node3D) -> void:
	var frac := clampf((roll_speed - ball_start_speed) / maxf(ball_max_speed - ball_start_speed, 0.01), 0.0, 1.0)
	hit_speed = roll_speed
	hit_at = e.global_position
	hit_target = e
	hit_damage = ball_bonus_damage * frac + charge_damage * charges  # each bank-shot charge adds charge_damage
	_hit(e, hit_damage, roll_dir, 0.45 + 0.4 * frac + 0.1 * charges)
	if e.has_method("toss_to"):
		var r: float = e.radius() if e.has_method("radius") else 0.5
		var land: Vector3 = ArenaMotion.slide(e, e.global_position, roll_dir * ball_toss_carry, r)
		MatchTeams.caster = player  # toss_to lands one kit hit from the caster
		e.toss_to(land, lerpf(ball_lift_min, ball_lift_max, frac), ball_toss_time, lerpf(ball_stun_min, ball_stun_max, frac))
	cue.emit("ball_hit")
	if spiked:  # flared mid-roll: the crash also does the flare's damage around the target
		spike_at = hit_at
		for x in _in_circle(spike_at, flare_radius):
			_hit(x, flare_damage, flat(x.global_position - spike_at).normalized(), 0.0)
		cue.emit("spike_burst")


## One bank-shot charge off a wall: more speed now and a higher top speed, more damage on the crash.
func _charge() -> void:
	if charges >= ball_max_charges:
		return
	charges += 1
	roll_speed += charge_speed
	cue.emit("ball_charge")


## 2 again mid-roll: the roll will end this frame and pop. True if it will.
func pop() -> bool:
	if not rolling or busy_with != "Iron_Ball" or _pop:
		return false
	_pop = true
	return true


## The pop: every enemy within pop_radius takes pop_damage and is lifted pop_lift in place.
func _do_pop() -> void:
	pop_at = player.global_position
	pops = 0
	for e in MatchTeams.enemies_of(player):
		if not MatchTeams.hittable(e) or MatchTeams.edge_distance(player, e) > pop_radius:
			continue
		var away := flat(e.global_position - pop_at)
		_hit(e, pop_damage, away.normalized() if away.length() > 0.01 else roll_dir, 0.0)
		if MatchTeams.hittable(e) and e.has_method("toss_to"):
			e.toss_to(e.global_position, pop_lift, pop_time, 0.0, false)  # the lift only; the damage is above
		pops += 1
	impact.emit(0.3)
	cue.emit("ball_pop")


# ---- 1, salvage, and the magnetised mark ---------------------------------------------------------------------------

## The field tears the plates off the enemy machines in a short cone in front and the pangolin wears them; each one
## stripped is magnetised. True if it fired (with or without anyone in the cone).
func salvage(target: Variant = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or not player.alive or player.has_meta("held_by"):
		return false
	used.emit("1")
	var dir := _aim(target)
	_start("Salvage", dir)
	salvage_targets = _in_cone(dir)
	plates_worn = 0
	cue.emit("salvage")  # pangolin_fx times the field and the plates from here (clip time 0)
	_play(b, "Salvage")
	if await _event(b, "Salvage", "field"):
		for e in salvage_targets:
			if not is_instance_valid(e) or not MatchTeams.hittable(e):
				continue
			_hit(e, salvage_damage, dir, 0.2)
			if e.has_method("set_armour"):
				e.set_armour(salvage_shred, salvage_time)
			magnetise(e)
			plates_worn += 1
		if plates_worn > 0 and player.has_method("set_armour"):
			player.set_armour(maxf(1.0 - salvage_gain * plates_worn, salvage_gain_cap), salvage_time)
	await _clip_end(b, "Salvage")
	_finish("Salvage")
	return true


## The enemy machines (not minions) inside the cone: the pangolin's middle to their edge within salvage_range.
func _in_cone(dir: Vector3) -> Array:
	var out: Array = []
	var min_dot := cos(deg_to_rad(salvage_half_angle))
	for e in MatchTeams.enemies_of(player):
		if not is_instance_valid(e) or not MatchTeams.hittable(e) or e.get("kind") == "minion":
			continue
		if MatchTeams.edge_distance(player, e) > salvage_range:
			continue
		var to := flat(e.global_position - player.global_position)
		if to.length() > 0.3 and to.normalized().dot(dir) < min_dot:
			continue
		out.append(e)
	return out


## Marks an enemy for mag_time (a second mark refreshes it). The effects hang the ring on cue "magnetise".
func magnetise(e: Node3D) -> void:
	_mag_until[e] = _clock + mag_time
	mag_target = e
	cue.emit("magnetise")


func is_magnetised(e: Variant) -> bool:
	return is_instance_valid(e) and float(_mag_until.get(e, -1.0)) > _clock


## The nearest magnetised enemy ahead of the roll (within 90 degrees of it) and within mag_pull_range, or null.
func _nearest_magnetised() -> Node3D:
	var best: Node3D = null
	var best_d := mag_pull_range
	for e in _mag_until.keys():
		if not is_magnetised(e) or not MatchTeams.hittable(e):
			continue
		var to := flat(e.global_position - player.global_position)
		var d := to.length()
		if d <= best_d and (d < 0.3 or to.normalized().dot(roll_dir) > 0.0):
			best_d = d
			best = e
	return best


# ---- 3, scale flare, and the spiked ball ---------------------------------------------------------------------------

## Standing: the Scale_Flare clip, damage around the pangolin on "flare", then the scales block. Mid-roll: no clip, the
## ball is spiked (cue ball_spiked) and the scales are up. True if it fired.
func scale_flare(_target: Variant = null) -> bool:
	if not is_instance_valid(player) or not player.alive or player.has_meta("held_by"):
		return false
	if comet:
		return false  # the comet's shell is the scrap plates: nothing to flare
	if rolling:
		if spiked:
			return false
		used.emit("3")
		spiked = true
		_flare_up()
		cue.emit("ball_spiked")
		return true
	var b := _body()
	if b == null or busy_with != "":
		return false
	used.emit("3")
	_start("Scale_Flare", flat(player.facing).normalized())
	flare_blocks = flare_block_count  # pangolin_fx reads the count on the clip's "flare" event, before the kit wakes
	flare_hits = 0
	_play(b, "Scale_Flare")
	if await _event(b, "Scale_Flare", "flare"):
		_flare_up()
		for e in _in_circle(player.global_position, flare_radius):
			_hit(e, flare_damage, flat(e.global_position - player.global_position).normalized(), 0.15)
			flare_hits += 1
		impact.emit(0.3)
	await _clip_end(b, "Scale_Flare")
	_finish("Scale_Flare")
	return true


func _flare_up() -> void:
	flared = true
	flare_blocks = flare_block_count
	_flare_token += 1
	var token := _flare_token
	await get_tree().create_timer(flare_time).timeout
	if token == _flare_token:
		_flare_down()


func _flare_down() -> void:
	if not flared:
		return
	flared = false
	flare_blocks = 0
	cue.emit("flare_end")


## machine_test_player.hit() asks the kit first: true blocks the hit (it then does MatchRules.blocked_share). While the
## scales are up they block flare_block_count hits, and each enemy blocked is magnetised.
func take_hit(from: Vector3, by: Node3D = null) -> bool:
	if not flared or flare_blocks <= 0 or not is_instance_valid(player):
		return false
	flare_blocks -= 1
	var d := flat(from - player.global_position)
	d = d.normalized() if d.length() > 0.05 else flat(player.facing).normalized()
	block_at = player.global_position + d * player.radius() + Vector3.UP * SPARK_UP
	if by != null and is_instance_valid(by) and MatchTeams.is_enemy(by, player):
		magnetise(by)
	cue.emit("flare_block")
	if flare_blocks <= 0:
		_flare_down()
	return true


## Every hittable enemy (minions too) whose edge is within r of the point.
func _in_circle(at: Vector3, r: float) -> Array:
	var out: Array = []
	for e in MatchTeams.enemies_of(player):
		if not is_instance_valid(e) or not MatchTeams.hittable(e):
			continue
		var er: float = e.radius() if e.has_method("radius") else 0.0
		if flat(e.global_position - at).length() - er <= r:
			out.append(e)
	return out


# ---- 4, scrap comet (the ultimate) ---------------------------------------------------------------------------------
## Pulls its stolen plates onto the shell and rolls as a ball comet_start_size times its size. It does not stop on
## hits: each enemy machine it runs over is tossed aside into the air and the ball grows; minions are bowled; walls
## bounce it. After comet_time it bursts, throwing the plates outward (more damage per stolen plate). Scrap off wrecks
## is not built: the arena has no wrecks yet.
## Cues: comet_start (plates fly on, ~0.35 s; reads comet_plates), comet_roll, comet_hit (comet_hit_at, comet_size),
## ball_bounce, ball_bowl, comet_burst (comet_burst_at, comet_radius).

@export var comet_start_size := 2.0 ## the ball against the pangolin's own size (the body is scaled by it)
@export var comet_grow := 0.15 ## size gained per enemy machine flattened
@export var comet_max_size := 2.6
@export var comet_time := 4.0 ## seconds rolling before it bursts
@export var comet_speed := 6.0 ## m/s when the shell closes
@export var comet_max_speed := 9.0
@export var comet_accel := 3.0 ## m/s gained per second
@export var comet_turn := 1.6 ## rad/s, heavier than the iron ball
@export var comet_hit_damage := 60.0 ## per machine run over, on top of the toss's kit hit
@export var comet_lift := 1.8
@export var comet_stun := 0.8
@export var comet_toss_time := 0.55
@export var comet_radius := 4.0 ## the burst: the ball's middle to an enemy's edge
@export var comet_burst_damage := 80.0
@export var comet_plate_damage := 20.0 ## burst damage added per stolen plate on the shell
@export var comet_burst_push := 2.5

var comet := false ## the scrap comet is running (pangolin_fx reads it)
var comet_size := 1.0 ## the ball's size against the pangolin's
var comet_plates := 0 ## stolen plates pulled onto the shell at the cast
var comet_hit_at := Vector3.ZERO ## the last machine run over (cue "comet_hit")
var comet_burst_at := Vector3.ZERO ## the burst's centre (cue "comet_burst")
var flattened: Array = [] ## machines run over this comet, for the checks
var burst_hits := 0 ## enemies the last burst hit, for the checks
var _comet_scale := Vector3.ONE  # the body's scale before the comet
var _comet_built := false  # the body has Comet_Gather, Comet_Roll and Comet_Burst (round 11 on)
var _comet_clip_speed := 8.63  # the comet's roll loop at 1x for this body
const SHELL_RADIUS := 0.6835 ## the scrap shell's ball radius at scale 1 (pangolin.events.json "scrap_shell", round 13)
const SHELL_CLIP_SPEED := 8.59 ## Comet_Roll with the separate shell: 4.295 m a turn at shell scale 1

## The clip speeds and SHELL_RADIUS above are fallbacks: the kit reads the live numbers from pangolin.events.json (game
## feel lane, 2026-11-14, after round 14 moved ball_radius to 0.6716 and Comet_Roll to 8.44), so a new model round
## needs no code change.
const EVENTS_FILE := "res://art/arena_models/pangolin.events.json"
static var _events: Dictionary = {}


## A number from pangolin.events.json: a clip's field by its short name (e.g. "Comet_Roll", "roll_speed"), or the scrap
## shell's when clip is "scrap_shell". fallback when the file or the field is missing.
static func _model_num(clip: String, field: String, fallback: float) -> float:
	if _events.is_empty() and FileAccess.file_exists(EVENTS_FILE):
		var d: Variant = JSON.parse_string(FileAccess.get_file_as_string(EVENTS_FILE))
		if d is Dictionary:
			_events = d
	if clip == "scrap_shell":
		var sh: Variant = _events.get("scrap_shell", {})
		return float(sh.get(field, fallback)) if sh is Dictionary else fallback
	for v in _events.values():
		if v is Dictionary:
			for k in v:
				var e: Variant = v[k]
				if (str(k) == clip or str(k).ends_with("_" + clip)) and e is Dictionary and e.has(field):
					return float(e[field])
	return fallback


## The scrap shell's ball radius at scale 1, metres (pangolin.events.json "scrap_shell").
static func shell_radius() -> float:
	return _model_num("scrap_shell", "ball_radius", SHELL_RADIUS)


func scrap_comet(target: Variant = null) -> bool:
	var b := _body()
	if b == null or busy_with != "" or not is_instance_valid(player) or not player.alive or player.has_meta("held_by"):
		return false
	used.emit("4")
	var dir := _aim(target)
	_start("Scrap_Comet", dir)
	roll_dir = dir
	roll_speed = 0.0
	bounces = 0
	bowls = 0
	_bowled.clear()
	flattened.clear()
	burst_hits = 0
	mag_pull = null  # as at the ball's start, so a comet that locks the ball's last target still cues mag_snap
	mag_mult = 1.0
	mag_snapped = null
	comet = true
	comet_size = comet_start_size
	comet_plates = plates_worn if float(player.get("armour")) < 1.0 else 0  # plates still worn from salvage
	_comet_scale = b.scale
	_comet_built = b.has_clip("Comet_Gather") and b.has_clip("Comet_Roll") and b.has_clip("Comet_Burst")  # round 11 model
	_comet_clip_speed = (_model_num("Comet_Roll", "roll_speed", SHELL_CLIP_SPEED if _shell(b) != null else COMET_CLIP_SPEED) if _comet_built else _roll_clip_speed("Ball_Roll"))
	cue.emit("comet_start")
	_play(b, "Curl_In")
	if not _comet_built:
		_grow(b, comet_size, 0.35)
	await _event(b, "Curl_In", "closed")
	if _comet_built and _can_roll(b):
		_play(b, "Comet_Gather")  # the plates slam onto the shell at "plates_on" (0.32 s); the ball swells with them
		_grow(b, comet_size, 0.32)
		await _clip_end(b, "Comet_Gather")
	var roll_clip := "Comet_Roll" if _comet_built else "Ball_Roll"
	var whole := false  # rolled all of comet_time
	if _can_roll(b):
		rolling = true
		roll_speed = comet_speed
		b.play_hold(roll_clip, _comet_rate())
		cue.emit("comet_roll")
		var left := comet_time
		var stopped := false
		while left > 0.0:
			await get_tree().process_frame
			if not _can_roll(b):
				break
			if _grounded():
				stopped = true  # grounded: the comet's own Comet_Burst ending where it is, no refund
				break
			var dt := get_process_delta_time()
			left -= dt
			_steer(dt, comet_turn)
			roll_speed = minf(roll_speed + comet_accel * dt, comet_max_speed)
			if b.action != roll_clip:
				b.play_hold(roll_clip, _comet_rate())
			b.set_action_rate(_comet_rate())
			_roll_step(dt, _comet_r())
			player.facing = roll_dir
			_run_over()
		whole = left <= 0.0 or stopped
		rolling = false
	if _comet_built and whole:
		_play(b, "Comet_Burst")  # the plates fly off at "burst" (0.04 s); the ball is plain again by "clear" (0.30 s)
		var on_time: bool = await _event(b, "Comet_Burst", "burst")
		_comet_burst()
		_grow(b, 1.0, 0.2, 0.06)  # the clip drops the ball between 0.10 and 0.30 s
		if on_time:
			await _clip_end(b, "Comet_Burst")
		else:
			_plates_off(b)
	else:
		_comet_burst()  # cut short (stunned, held) or the old model: it bursts where it stopped
		_plates_off(b)
		_grow(b, 1.0, 0.25)
	if is_instance_valid(b) and is_instance_valid(player) and player.alive:
		_play(b, "Curl_Out")
		await _clip_end(b, "Curl_Out")
	comet = false
	_finish("Scrap_Comet")
	return true


func _comet_r() -> float:
	return player.radius() * comet_size


## The roll loop's authored speed at 1x; a ball comet_size times bigger covers that many times more per turn.
func _comet_rate() -> float:
	return roll_speed / (_comet_clip_speed * comet_size)


## The comet's scrap shell (round 13 on: a MeshInstance3D on the root bone, origin at the ball's centre), or null.
func _shell(b: MechModel3D) -> Node3D:
	return b.find_child("scrap_shell", true, false) as Node3D if is_instance_valid(b) else null


## Grows the scrap ball to size over secs, after delay. With a scrap_shell only the shell scales: the pangolin stays 1x
## and is lifted by (size - 1) x SHELL_RADIUS so the bigger shell rests on the floor (Preston, 2026-11-13: the scrap
## ball is the big part, the pangolin seen inside at its normal size). Without one the whole body scales.
func _grow(b: MechModel3D, size: float, secs: float, delay := 0.0) -> void:
	if not is_instance_valid(b):
		return
	var t := create_tween()
	if delay > 0.0:
		t.tween_interval(delay)
	var shell := _shell(b)
	if shell != null:
		t.tween_property(shell, "scale", Vector3.ONE * size, secs)
		t.parallel().tween_property(b, "lift", (size - 1.0) * shell_radius(), secs)
	else:
		t.tween_property(b, "scale", _comet_scale * size, secs)


func _run_over() -> void:
	var r := _comet_r()
	for e in MatchTeams.enemies_of(player):
		if not is_instance_valid(e) or not MatchTeams.hittable(e):
			continue
		if MatchTeams.edge_distance(player, e) - r > ball_reach:
			continue
		if e.get("kind") == "minion":
			if not _bowled.has(e):
				_bowl(e)
			continue
		if not flattened.has(e):
			_flatten(e)


## Runs a machine over: damage, tossed into the air off to the side so the ball rolls on, and the ball grows.
func _flatten(e: Node3D) -> void:
	flattened.append(e)
	comet_hit_at = e.global_position
	_hit(e, comet_hit_damage, roll_dir, 0.5)
	if e.has_method("toss_to"):
		var er: float = e.radius() if e.has_method("radius") else 0.5
		var side := roll_dir.cross(Vector3.UP).normalized()
		if flat(e.global_position - player.global_position).dot(side) < 0.0:
			side = -side
		var land: Vector3 = ArenaMotion.slide(e, e.global_position, side * (_comet_r() + er) + roll_dir, er)
		MatchTeams.caster = player  # toss_to lands one kit hit from the caster
		e.toss_to(land, comet_lift, comet_toss_time, comet_stun)
	comet_size = minf(comet_size + comet_grow, comet_max_size)
	_grow(_body(), comet_size, 0.15)
	cue.emit("comet_hit")
	impact.emit(0.35)


func _comet_burst() -> void:
	if not comet or not is_instance_valid(player) or not player.alive:
		return
	comet_burst_at = player.global_position
	var damage := comet_burst_damage + comet_plate_damage * comet_plates
	burst_hits = 0
	for e in _in_circle(comet_burst_at, comet_radius):
		var away := flat(e.global_position - comet_burst_at)
		away = away.normalized() if away.length() > 0.05 else roll_dir
		_hit(e, damage, away, 0.0)
		if e.has_method("knock_aside"):
			e.knock_aside(away * comet_burst_push, 0.3, false)
		burst_hits += 1
	plates_worn = 0  # thrown outward
	cue.emit("comet_burst")
	impact.emit(0.6)


## The scrap plates are a second mesh driven only by the ball and comet clips: a comet cut short leaves them on.
func _plates_off(b: MechModel3D) -> void:
	if not is_instance_valid(b):
		return
	var m := b.find_child("scrap_shell", true, false) as MeshInstance3D  # round 13 on
	if m == null:
		m = b.find_child("scrap_plates", true, false) as MeshInstance3D  # round 11
	if m == null:
		return
	for s in ["Plates_On", "Plates_Out"]:
		var i := m.find_blend_shape_by_name(s)
		if i >= 0:
			m.set_blend_shape_value(i, 0.0)


# ---- the roll loops --------------------------------------------------------------------------------------------------

func _roll_clip(b: MechModel3D) -> String:
	return "Ball_Roll_Spiked" if spiked and b.has_clip("Ball_Roll_Spiked") else "Ball_Roll"


func _roll_clip_speed(clip: String) -> float:
	return _model_num(clip, "roll_speed", SPIKED_CLIP_SPEED if clip == "Ball_Roll_Spiked" else ROLL_CLIP_SPEED)


## Swaps the held roll loop at the same clip time (the loops share one 0.50 s turn), so the body does not jump. From
## anything else (a hit react cut in) it starts the loop over.
func _swap_roll(b: MechModel3D, clip: String) -> void:
	var on_loop: bool = b.action == "Ball_Roll" or b.action == "Ball_Roll_Spiked"
	var at: float = b.anim.current_animation_position if on_loop else 0.0
	b.play_hold(clip, roll_speed / _roll_clip_speed(clip), 0.0 if on_loop else 0.06)
	if on_loop:
		b.anim.seek(at, true)
