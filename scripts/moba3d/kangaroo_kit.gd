class_name KangarooKit
extends Node
## Kangaroo kit on the rigged 3D body (kangaroo-3d session, 2026-11-11; Preston: "kit time").
## DRAFT for the game feel lane to install over scripts/moba3d/kangaroo_kit.gd. When installed, add
##     class_name KangarooKit
## as the first line (arena_play and KitAudio use that name). It is left off here so the draft can be loaded from
## scratch beside the sprite kit, which still owns the name. Built to the game feel lane's shape (2026-11-11):
## install(), basic_attack(), basic_range, basic_cooldown, impact / used / cue signals, `current` with _begin/_end,
## the rhino kit's body helpers (_body, _play, _event, _clip_end), keys 1 to 4 behind player.slot_ready().
##
## The design is the Kangaroo section of docs/plan/moba-kits.md (ode to Ravana). The basic attack's numbers are the
## ones Preston approved for the sprite kit (2026-11-05, "Yes, build it"). Every ability number is a PROPOSAL: the
## kit doc gives cooldowns as words and no damage, distance, radius or time.
##
## Passive, rhythm: a landed hit adds a stack; at rhythm_max the next basic is the tail kick, which knocks back.
## Basic: the three-beat chain Preston approved (2026-11-11): Jab_Left, Jab_Right_Quick, Hook_Right. The clip
##        lengths are the beat lengths (medium, quick, heavy), so the next beat starts as its clip ends, or at a
##        "recover" event if the clip ever gets one. chain_reset after a basic ends, it starts over at the left jab.
## Slots 1 to 3 were reworked on Preston's ideas of 2026-11-11 (docs/reference/kangaroo-combat-references-2026-11-10.md,
## section 3e, has what was read for each):
## 1, hop and jab: aimed at a machine in range it leaps to it. An enemy: lands in front, four fast punches. An ally:
##        lands beside it, no punches, both marked "kangaroo_cover" (the damage cut is a rule for the player's hit()).
##        Nobody under the aim: the short hop forward and four punches.
## 2, tail kick: leans back on its tail and double-kicks. The nearest enemy is launched; if a wall or another
##        machine stops it, it takes a burst and is stunned, and so is the machine it landed on.
## 3, guard: raises its gloves; every hit while they are up is blocked (the match's block rule: it still does
##        blocked_share) and counted. A second press, or the time running out, throws the counter at every enemy
##        close by: harder for each blocked hit, with a stun if anything was blocked.
## 4, title bout (Preston's pick, 2026-11-11: "A title bout"; an ode to Ne Zha's ultimate that keeps the arena):
##        aimed at an enemy machine in range it leaps to it and touches gloves; a small ring goes up around the pair
##        and nobody outside can touch either of them (both carry the meta "untouchable": the rule is the player's
##        can_be_hit()). Four punches land on a beat; pressing attack as a punch winds up makes it a crit. A tail
##        kick then launches the enemy out through the ropes with slot 2's slam rule, and the ring drops.
##        Bob and weave (Preston, 2026-11-12): after each of the first three punches the kangaroo slips round the
##        enemy (bout_slip_angles), so the four punches come from four sides and the last from behind. The enemy is
##        locked for the bout (stun for the pose, the "held_by" mark for the lock) and turned to face each punch.
## Without a 3D body the basic falls back to the sprite kit's lunge and the abilities do nothing.

const KANGAROO_FRAMES := preload("res://art/machines/kangaroo/kangaroo_frames.tres")
const CANVAS := 160
const FEET_EDGE_ROW := 141
const REACH_SLACK := 0.3 ## a target may drift this far past the reach between the check and the hit
const CHAIN := ["Jab_Left", "Jab_Right_Quick", "Hook_Right"]
const CHAIN_STRENGTH := [0.55, 0.45, 0.9] ## KitFeel.basic_hit strength per beat
const CHAIN_HITSTOP := [0.03, 0.02, 0.05]
const CHAIN_CUE := ["jab_hit", "jab_hit", "hook_hit"]
const BOUT_CLIPS := ["Jab_Left", "Jab_Right_Quick", "Jab_Left", "Hook_Right"]
const HIT_AT := {"Jab_Left": 0.20, "Jab_Right_Quick": 0.11, "Hook_Right": 0.24} ## each clip's hit event, seconds
const KICK_HIT_AT := 0.5

signal impact(strength: float)
signal used(slot: String)
signal cue(name: String) ## sound: basic_jab, basic_whiff, rhythm_full, rhythm_kick (kept from the sprite kit), jab_hit,
## hook_hit, hop, hop_land, hopjab_hit, tail_brace, tail_hit, tail_land, guard_block, counter_hit, glove_tap, ring_cast,
## and from 2026-11-11: tail_slam (a launched enemy hit a wall or a machine), leap_cover (landed by an ally),
## bout_start (ring up: ring_centre, ring_radius, ring_target are set), bout_beat (a punch landed: bout_beat is its
## number from 1, last_crit says if it was on the beat), bout_launch (the kick landed), bout_end (ring down),
## bout_no_target (slot 4 pressed with no enemy under the aim: nothing is spent), bout_slip (a slip round the enemy
## starts: slip_from, slip_to, slip_time and slip_side are set; target_locked is true from the landing to bout_end)

@export var basic_range := 1.4 ## metres edge to edge (MatchTeams.edge_distance)
@export var basic_cooldown := 0.5 ## set to each beat's own length as it fires; the director reads it after the swing starts
@export var jab_damage := 45.0
@export var kick_damage := 90.0 ## the rhythm kick
@export var kick_knockback := 2.5 ## metres
@export var kick_reach_bonus := 0.3 ## the feet reach a little further than the fists
@export var rhythm_max := 4 ## landed hits that fill the passive
@export var rhythm_fade := 4.0 ## seconds without a landed hit before the stacks drop
@export var chain_reset := 1.5 ## seconds after a basic ends before the chain starts over (the rhino's number)
@export var half_angle := 50.0 ## degrees either side of the aim a swing can reach
@export var free_after_hit := 0.05 ## seconds after a jab lands before the player can walk again
@export_group("1 hop and jab (proposals)")
@export var hop_distance := 3.0 ## with no machine picked: metres covered between the clip's hop and land events
@export var hop_stop_short := 0.9 ## the hop stops when an enemy is this close ahead, edge to edge
@export var hopjab_damage := 25.0 ## each of the four punches
@export var leap_range := 10.0 ## a machine this close (edge to edge) can be leapt to: an enemy or an ally
@export var leap_cone := 25.0 ## degrees either side of the aim that pick the machine; the smallest angle wins
@export var leap_speed := 22.0 ## metres a second in the air
@export var leap_air_max := 0.5 ## seconds; the air time never drops under the clip's own 0.28
@export var leap_ally_gap := 1.0 ## it lands with its middle this far from an ally's edge
@export var leap_cover_share := 0.2 ## landing by an ally: both take this much less damage (needs the rule in hit())
@export var leap_cover_time := 2.5 ## seconds
@export_group("2 tail kick (proposals)")
@export var tailkick_damage := 110.0
@export var tailkick_knockback := 6.0 ## metres the nearest enemy is launched (4.0 before the slam rule, 2026-11-11)
@export var tailkick_flight := 0.35 ## seconds the launch takes
@export var tailkick_cone := 55.0
## Preston, 2026-11-11: "the tail kick should stun enemies when they hit god or wall like gilgamesh". Structure after
## SMITE's Gilgamesh Drop Kick (wiki: the launched enemy takes burst damage and is stunned 1.2 s on a god or a wall,
## and a god it hits takes the burst and the stun too). Numbers are proposals.
@export var slam_stun := 1.2 ## seconds, for the launched enemy and a machine it lands on
@export var slam_damage := 40.0 ## the extra burst on a wall or a machine
@export_group("3 guard (proposals)")
@export var guard_time := 2.0 ## seconds the gloves stay up; every hit in that time is blocked and counted
@export var guard_recast_after := 0.5 ## pressing 3 again after this long throws the counter early
@export var counter_damage := 60.0 ## to every enemy within counter_reach, before the bonus
@export var counter_reach := 3.0 ## metres edge to edge, all around (2.2 and one target before 2026-11-11)
@export var counter_bonus := 0.2 ## share of the damage added per blocked hit
@export var counter_bonus_cap := 1.0 ## the most the bonus can add (five blocked hits)
@export var counter_stun := 0.6 ## seconds, only when at least one hit was blocked
@export_group("4 title bout (proposals)")
@export var bout_range := 8.0 ## an enemy machine this close (edge) and within leap_cone of the aim can be called out
@export var ring_radius := 3.0 ## the ropes around the pair
@export var bout_beats := 4 ## punches before the kick
@export var bout_first_beat := 0.35 ## seconds from the ring going up to the first punch landing
@export var bout_beat_time := 0.65 ## seconds between punches landing
@export var bout_punch_damage := 35.0
@export var bout_crit := 1.5 ## a punch pressed on the beat does this many times the damage
@export var bout_window := 0.25 ## press attack this long or less before a punch lands; earlier spoils that beat
@export var bout_grace := 0.15 ## a press this soon after a punch landed is ignored (a late press, not an early one)
@export var bout_kick_damage := 110.0
@export var bout_slip_angles: Array[float] = [60.0, 60.0, 60.0] ## degrees round the enemy after punches 1, 2 and 3; they add up to behind it
@export var bout_slip_delay := 0.10 ## seconds a punch is left to land before the slip starts
@export var bout_slip_time := 0.25 ## the Slip clips' length
@export_group("")
@export var fx_script_path := "res://scripts/moba3d/kangaroo_fx.gd"
@export var ring_fx_script_path := "res://scripts/moba3d/kangaroo_ring_fx.gd" ## the effects lane's title bout ring; "" to leave it off

var player: Node3D
var fx: Node3D
var current := "" ## the action that owns the machine, or ""
var rhythm := 0
var guarding := false
var blocked := 0 ## hits blocked by the guard that is up now (or the last one)
var last_leap := "" ## what slot 1 last did: "enemy", "ally", or "" for the plain hop (the checks read it)
var leap_target: Node3D
var ring_on := false ## the bout's ring is up (bout_start to bout_end)
var ring_target: Node3D
var ring_centre := Vector3.ZERO
var bout_beat := 0 ## the number of the punch that last landed in this bout, from 1
var last_crit := false ## whether that punch was pressed on the beat
var bout_crits := 0 ## crits in this bout (or the last one)
var bout_next_beat := -1.0 ## seconds until the next punch of the bout lands; -1 when none is coming
var slip_from := Vector3.ZERO ## the slip that last started: where from, where to, how long, and which way
var slip_to := Vector3.ZERO
var slip_time := 0.0
var slip_side := 0 ## 1: to the kangaroo's own left; -1: to its right
var slips := 0 ## slips in this bout (or the last one)
var target_locked := false ## the bout's enemy cannot move, attack or cast (from the landing to bout_end)
var _bout_dir := -1 ## which way round this bout goes; it flips every bout
var _bout_holds := false ## this kit put the held_by mark on the enemy, so this kit takes it off
var swinging := false ## kept for the sprite fallback and older checks
var slams := 0 ## launches that ended on a wall or a machine since the kit started (the checks read it)
var last_slam := "" ## "wall" or "machine": what the last launched enemy hit
var _chain := 0
var _chain_end := -1000.0
var _last_hit := -1000.0
var _guard_left := 0.0
var _guard_age := 0.0
var _last_attacker: Node3D
var _cover_until := -1000.0
var _cover_ally: Node3D
var _bout_land := -1000.0 ## _clock time the next punch lands
var _bout_last := -1000.0 ## _clock time the last punch landed
var _press_good := false
var _press_spoiled := false
var _clock := 0.0 ## game time this kit has run: the fade, the reset, the guard and the ring all use it
var _got := {} ## "clip/event" -> how many times the body has fired it since that clip last started
var _ev_body: MechModel3D = null
var _fx_body: Node3D = null
var _clip_now := "" ## the last clip the kit started on the body
var _ring_fx_on := false


static func install(p: Node3D) -> Node:
	var spr: Node3D = p.get_node("Sprite")
	spr.stop_action()
	spr.sprite_frames = KANGAROO_FRAMES
	spr.canvas_height = CANVAS
	spr.feet_edge_row = FEET_EDGE_ROW
	spr.size_class = "M"
	spr.play(StringName("idle_" + spr.view))
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var kit := new()
	kit.name = "Kit"
	kit.player = p
	p.add_child(kit)
	return kit


func _ready() -> void:
	if player == null:
		player = get_parent()
	impact.connect(_shake)


func _shake(strength: float) -> void:
	if not player.get("bot"):
		KitFeel.shake(self, strength)


## A fresh attack press (left mouse or space) during the bout is a try at the beat. The match's own attack path does
## not reach the kit while the machine is busy, so the kit listens for it here.
func _unhandled_input(event: InputEvent) -> void:
	if current != "Bout" or not is_instance_valid(player) or player.get("bot"):
		return
	var mb := event as InputEventMouseButton
	var key := event as InputEventKey
	if (mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT) \
			or (key != null and key.pressed and not key.echo and key.physical_keycode == KEY_SPACE):
		bout_press()


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if k.physical_keycode < KEY_1 or k.physical_keycode > KEY_4:
		return
	if k.physical_keycode == KEY_3 and guarding and not player.get("bot"):
		guard()  # the second press throws the counter; the slot is already on cooldown, so this comes first
		return
	if player.get("bot") or (player.has_method("slot_ready") and not player.slot_ready(str(k.physical_keycode - KEY_0))):
		return  # a bot's kit ignores the keyboard; in a match a slot waits out its cooldown (MatchRules)
	match k.physical_keycode:
		KEY_1:
			hop_and_jab()
		KEY_2:
			tail_kick()
		KEY_3:
			guard()
		KEY_4:
			boxing_ring()


# ---- small helpers --------------------------------------------------------------------------------------------

static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


func feet() -> Vector3:
	return player.global_position


func ahead() -> Vector3:
	var f: Vector3 = player.facing
	return Vector3(f.x, 0.0, f.z).normalized()


func _aim() -> Vector3:
	var d := Vector3.ZERO
	if player.has_method("aim_dir"):
		d = flat(player.aim_dir())
	return d.normalized() if d.length() > 0.01 else ahead()


func _reach_of(t: Node3D) -> float:
	return MatchTeams.edge_distance(player, t)


## Every enemy the kit can hit: machines, and in a match the towers, cores, minions and camp monsters too.
func _pool() -> Array:
	if MatchTeams.team_of(player) != "":
		return get_tree().get_nodes_in_group("match_unit").filter(func(u: Node) -> bool:
			return u != player and MatchTeams.is_enemy(u, player) and MatchTeams.hittable(u))
	return MatchTeams.enemies_of(player).filter(func(u: Variant) -> bool: return u is Node3D and MatchTeams.hittable(u))


## Enemies within reach (edge to edge) and within cone degrees of dir, nearest first.
func _in_cone(dir: Vector3, reach: float, cone: float) -> Array:
	var found: Array = []
	for t: Node3D in _pool():
		var to := flat(t.global_position - feet())
		if _reach_of(t) <= reach and (cone >= 180.0 or to.length() < 0.3 or rad_to_deg(dir.angle_to(to.normalized())) <= cone):
			found.append(t)
	found.sort_custom(func(a: Node3D, b: Node3D) -> bool: return _reach_of(a) < _reach_of(b))
	return found


func _deal(t: Node3D, damage: float) -> void:
	if t.has_method("hit"):
		t.hit(player, damage / MatchRules.kit_hit_damage)  # machines: plating, guards and shields apply
	elif t.has_method("take_damage"):
		t.take_damage(damage, player)  # towers and cores


## The feel of a landed hit: the camera kick and the victim's shove, and both bodies hold for the hitstop.
func _feel(b: MechModel3D, t: Node3D, push: Vector3, strength: float, stop: float) -> void:
	KitFeel.basic_hit(player, t, push, strength)
	if b != null and is_instance_valid(b):
		b.freeze(stop)
	var tb: Variant = t.get("body")
	if tb is MechModel3D:
		tb.freeze(stop)


func _add_rhythm() -> void:
	_last_hit = _clock
	rhythm = mini(rhythm + 1, rhythm_max)
	if rhythm == rhythm_max:
		cue.emit("rhythm_full")
	_show_rhythm()


func _show_rhythm() -> void:
	if is_instance_valid(fx):
		fx.set_rhythm(mini(rhythm, 3))


func _begin(action: String) -> bool:
	if current != "" or not is_instance_valid(player) or not player.alive or player.stunned > 0.0 or player.has_meta("held_by"):
		return false
	current = action
	player.busy = true
	return true


func _end() -> void:
	current = ""
	swinging = false
	if is_instance_valid(player):
		player.busy = false


## The rigged body once the match has attached it (use_model runs after install), or null. Hangs the effects on it.
func _body() -> MechModel3D:
	var b: Variant = player.get("body") if is_instance_valid(player) else null
	if not (b is MechModel3D) or not is_instance_valid(b) or not b.has_clip("Jab_Left"):
		return null
	if _ev_body != b:
		_ev_body = b
		b.event.connect(_on_body_event.bind(b))
	if _fx_body != b:
		_fx_body = b
		if is_instance_valid(fx):
			fx.queue_free()
		fx = null
		if fx_script_path != "" and (ResourceLoader.exists(fx_script_path) or FileAccess.file_exists(fx_script_path)):
			fx = load(fx_script_path).new()
			player.add_child(fx)
			fx.setup(b, player)
			_show_rhythm()
			if not _ring_fx_on and ring_fx_script_path != "" and ResourceLoader.exists(ring_fx_script_path):
				var ring_fx: Variant = load(ring_fx_script_path)  # the effects lane's observer: it draws the bout's ring from the cues
				if ring_fx != null and ring_fx.has_method("attach"):
					ring_fx.attach(self)
					_ring_fx_on = true
	return b


func _on_body_event(clip: String, n: String, _damage: bool, b: MechModel3D) -> void:
	if b == _ev_body:
		_got[clip + "/" + n] = int(_got.get(clip + "/" + n, 0)) + 1


## Plays clip on the body with its events counted afresh.
func _play(b: MechModel3D, clip: String, speed := 1.0) -> void:
	for k in _got.keys():
		if String(k).begins_with(clip + "/"):
			_got.erase(k)
	_clip_now = clip
	b.play_action(clip, speed)


## Waits until the body's clip has fired event n `count` times. False when the clip ended or was replaced first,
## or the kangaroo died or was stunned.
func _event(b: MechModel3D, clip: String, n: String, count := 1) -> bool:
	while is_instance_valid(b) and player.alive and int(_got.get(clip + "/" + n, 0)) < count:
		if b.action != clip:
			return false
		await get_tree().process_frame
	return is_instance_valid(b) and player.alive and int(_got.get(clip + "/" + n, 0)) >= count


func _clip_end(b: MechModel3D, clip: String) -> void:
	while is_instance_valid(b) and b.action == clip and player.alive:
		await get_tree().process_frame


func _process(delta: float) -> void:
	_clock += delta
	if not is_instance_valid(player):
		return
	var b := _body()
	if rhythm > 0 and _clock - _last_hit > rhythm_fade:
		rhythm = 0
		_show_rhythm()
	if current != "" and (not player.alive or player.stunned > 0.0 or player.has_meta("held_by")):
		_abort(b)
	if guarding:
		_guard_left -= delta
		_guard_age += delta
		if _guard_left <= 0.0:
			_counter()
	if _cover_until > -999.0 and _clock >= _cover_until:
		_cover_until = -1000.0
		for m: Variant in [player, _cover_ally]:
			if is_instance_valid(m) and m.has_meta("kangaroo_cover"):
				m.remove_meta("kangaroo_cover")
		_cover_ally = null
	bout_next_beat = maxf(_bout_land - _clock, 0.0) if current == "Bout" and _bout_land > -999.0 else -1.0
	if ring_on:
		_tick_ring()
	# walking off cancels the rest of a jab's recovery, so the hop starts at once
	if b != null and current != "" and CHAIN.has(current) and not player.busy and b.action == current \
			and player.move_dir().length() > 0.05:
		b.stop_action()


## Death, a stun or a grab ends whatever the kit was doing.
func _abort(b: MechModel3D) -> void:
	guarding = false
	if current == "Bout":
		if b != null and b.action != "":
			b.stop_action()
		_bout_over()
		return
	if b != null and b.action != "" and (b.action == current or b.action == _clip_now):
		b.stop_action()
	_end()


# ---- basic attack and the rhythm kick -----------------------------------------------------------------------------

## The director calls it (target null for the player, aimed with the mouse; a bot passes its target). True if it fired.
func basic_attack(target: Node3D) -> bool:
	if current != "" or swinging or not is_instance_valid(player):
		return false
	if target != null and _reach_of(target) > basic_range + REACH_SLACK:
		return false
	var d := flat(target.global_position - feet()) if target != null else Vector3.ZERO
	if d.length() < 0.01 and target == null:
		d = _aim()
	if d.length() < 0.01:
		d = ahead()
	d = d.normalized()
	if _clock - _last_hit > rhythm_fade:
		rhythm = 0
	var b := _body()
	if b == null:
		_swing_sprite(target, d, rhythm >= rhythm_max)
		return true
	if rhythm >= rhythm_max:
		basic_cooldown = b.clip_length("TailKick")
		player.facing = d
		_kick(b, d, kick_damage, kick_knockback, "rhythm_kick", half_angle)
		return true
	if _clock - _chain_end > chain_reset:
		_chain = 0
	var i := _chain
	_chain = (_chain + 1) % CHAIN.size()
	basic_cooldown = b.clip_length(CHAIN[i])
	player.facing = d
	_beat(b, i, target, d, 1.0)
	return true


func _beat(b: MechModel3D, i: int, target: Node3D, dir: Vector3, speed: float) -> void:
	var clip: String = CHAIN[i]
	if not _begin(clip):
		return
	_play(b, clip, speed)
	cue.emit("basic_jab")
	if await _event(b, clip, "hit"):
		var t: Node3D = target
		if t == null or not is_instance_valid(t) or not MatchTeams.hittable(t) or _reach_of(t) > basic_range + REACH_SLACK:
			var near := _in_cone(dir, basic_range, half_angle)  # the player aims with the mouse: whoever is in front now
			t = near[0] if not near.is_empty() else null
		if t != null:
			_deal(t, jab_damage)
			var f := ahead()
			var push: Vector3 = [f, f, Vector3.UP.cross(f).normalized() * -1.0 + f * 0.4][i]  # the hook shoves across
			_feel(b, t, push.normalized(), CHAIN_STRENGTH[i], CHAIN_HITSTOP[i])
			cue.emit(CHAIN_CUE[i])
			impact.emit(0.2 if i == 2 else 0.12)
			_add_rhythm()
		else:
			cue.emit("basic_whiff")
		# the jab has landed: the player may walk, and walking cancels the rest of the clip (_process)
		await get_tree().create_timer(free_after_hit).timeout
		if current == clip and is_instance_valid(player):
			player.busy = false
		# the next basic may start at the clip's "recover" event if it has one; otherwise when the clip ends
		if await _event(b, clip, "recover"):
			_chain_end = _clock
			if current == clip:
				_end()
			return
	await _clip_end(b, clip)
	_chain_end = _clock
	if current == clip:
		_end()


## The double kick off the tail: the rhythm finisher and slot 2 run through here (the bout has its own).
func _kick(b: MechModel3D, dir: Vector3, damage: float, knockback: float, hit_cue: String, cone: float, only: Node3D = null) -> void:
	if not _begin("TailKick"):
		return
	_play(b, "TailKick")
	var hit_any := false
	if await _event(b, "TailKick", "brace"):
		cue.emit("tail_brace")
	if await _event(b, "TailKick", "hit"):
		var victims: Array = _in_cone(dir, basic_range + kick_reach_bonus + REACH_SLACK, cone)
		if only != null:
			victims = victims.filter(func(t: Node3D) -> bool: return t == only)
		elif hit_cue == "rhythm_kick" and victims.size() > 1:
			victims = [victims[0]]  # the basic's kick is single target, like the jabs
		var launch := hit_cue == "tail_hit" and only == null  # slot 2: the nearest enemy is launched, the rest only take the hit
		for i in victims.size():
			var t: Node3D = victims[i]
			_deal(t, damage)
			_feel(b, t, dir, 1.3, 0.08)
			hit_any = true
			if launch:
				if i == 0:
					_launch(t, dir)
			elif t.has_method("knock_aside"):
				t.knock_aside(dir * knockback, 0.3, false)  # the push only: knock_aside's own hit would add 60 on top
		if hit_any:
			cue.emit(hit_cue)
			if hit_cue != "tail_hit":
				cue.emit("tail_hit")
			impact.emit(0.45)
			if hit_cue == "rhythm_kick":
				rhythm = 0
				_last_hit = _clock
				_show_rhythm()
		else:
			cue.emit("basic_whiff")
	if await _event(b, "TailKick", "land"):
		cue.emit("tail_land")
	await _clip_end(b, "TailKick")
	_chain_end = _clock
	if current == "TailKick":
		_end()


## Slot 2's launch. The enemy flies tailkick_knockback along dir. If a wall stops it short, or it lands on another
## enemy machine on the way, it stops there, takes slam_damage and is stunned; a machine it hit takes both too.
## Where a wall would stop it is worked out before it flies (ArenaMotion.slide, the same sweep the shove uses).
func _launch(victim: Node3D, dir: Vector3) -> void:
	if not victim.has_method("knock_aside"):
		return
	var from := flat(victim.global_position)
	var radius: float = victim.body_radius() if victim.has_method("body_radius") else 0.6
	var end := ArenaMotion.slide(victim, victim.global_position, dir * tailkick_knockback, radius)
	var free := flat(end - victim.global_position).dot(dir)   # metres it can travel along the kick before a wall
	var wall := free < tailkick_knockback - 0.4
	victim.knock_aside(dir * tailkick_knockback, tailkick_flight, false)
	var t := 0.0
	var struck: Node3D = null
	while t < tailkick_flight and is_instance_valid(victim) and victim.get("alive") == true:
		await get_tree().process_frame
		t += get_process_delta_time()
		for o in MatchTeams.enemies_of(player):
			if o is Node3D and o != victim and MatchTeams.hittable(o) and o.has_method("stun") \
					and MatchTeams.edge_distance(victim, o) <= 0.1:
				struck = o
				break
		if struck != null or (wall and (flat(victim.global_position) - from).dot(dir) >= free - 0.15):
			break
	if not is_instance_valid(victim) or victim.get("alive") != true:
		return
	if struck == null and not wall:
		return
	if victim.has_method("halt"):
		victim.halt()  # it stops where it hit
	for s: Node3D in ([victim, struck] if struck != null else [victim]):
		_deal(s, slam_damage)
		if s.has_method("stun"):
			s.stun(slam_stun)
	slams += 1
	last_slam = "machine" if struck != null else "wall"
	cue.emit("tail_slam")
	impact.emit(0.5)
	if is_instance_valid(fx):
		fx.flash(victim.global_position + Vector3.UP * 0.9, 2.2, Color.WHITE, 0.25)


## No 3D body: the sprite kit's lunge on the still (2026-11-05), kept so a sprite kangaroo can still fight.
func _swing_sprite(victim: Node3D, dir: Vector3, kick: bool) -> void:
	swinging = true
	player.busy = true
	player.facing = dir
	basic_cooldown = 0.8
	var spr: Node3D = player.get_node("Sprite")
	var tw := create_tween()
	tw.tween_property(spr, "position", spr.position + dir * 0.25, 0.08)
	await get_tree().create_timer(0.08).timeout
	if not is_instance_valid(player):
		return
	if victim == null:
		var near := _in_cone(dir, basic_range, half_angle)
		victim = near[0] if not near.is_empty() else null
	if victim != null and is_instance_valid(victim) and MatchTeams.hittable(victim) and _reach_of(victim) <= basic_range + REACH_SLACK:
		if kick and victim.has_method("knock_aside"):
			victim.knock_aside(dir * kick_knockback, 0.25, false)
		_deal(victim, kick_damage if kick else jab_damage)
		if kick:
			rhythm = 0
			_last_hit = _clock
			cue.emit("rhythm_kick")
		else:
			cue.emit("basic_jab")
			_add_rhythm()
		impact.emit(0.25 if kick else 0.15)
		await get_tree().create_timer(0.05).timeout
	else:
		cue.emit("basic_whiff")
	if is_instance_valid(spr):
		create_tween().tween_property(spr, "position", spr.position - dir * 0.25, 0.1)
	swinging = false
	if is_instance_valid(player):
		player.busy = false


# ---- 1, hop and jab ------------------------------------------------------------------------------------------------

const CLIP_AIR := 0.28 ## the HopJab clip's hop to land
const LEAP_CLIP_AIR := 0.40 ## the Leap clip's hop to land


## The clip a leap to a machine plays: the long Leap when the body has it (round 10 clips), else HopJab's short hop.
func _leap_clip(b: MechModel3D) -> String:
	return "Leap" if b.has_clip("Leap") else "HopJab"

## The machine slot 1 would leap to: an enemy or an ally within leap_range and leap_cone of the aim. Null: plain hop.
func leap_pick(dir: Vector3, reach := -1.0, allies := true) -> Node3D:
	if reach < 0.0:
		reach = leap_range
	var best: Node3D = null
	var best_angle := leap_cone
	for t: Variant in MatchTeams.enemies_of(player) + (MatchTeams.allies_of(player) if allies else []):
		if not (t is Node3D) or t == player or not MatchTeams.hittable(t):
			continue
		if MatchTeams.team_of(player) != "" and t.get("kind") != "machine":
			continue
		var to := flat(t.global_position - feet())
		if to.length() < 0.3 or _reach_of(t) > reach:
			continue
		var angle := rad_to_deg(dir.angle_to(to.normalized()))
		if angle <= best_angle:
			best_angle = angle
			best = t
	return best


## Where a leap at `target` lands: `gap` from its edge on the kangaroo's side, pushed out of anything solid, so the
## leap clears walls on the way in and never ends inside one.
func _landing(target: Node3D, gap: float) -> Vector3:
	var to := flat(target.global_position - feet())
	var tr: float = target.radius() if target.has_method("radius") else 0.6
	if to.length() <= tr + gap:
		return feet()
	return ArenaMotion.slide(player, target.global_position - to.normalized() * (tr + gap), Vector3.ZERO, player.body_radius())


## Carries the kangaroo to land_at during the leap clip's hop (call it on the clip's "hop" event).
func _fly(b: MechModel3D, land_at: Vector3, clip := "HopJab") -> void:
	var from := feet()
	var clip_air := LEAP_CLIP_AIR if clip == "Leap" else CLIP_AIR
	var air := clampf(flat(land_at - from).length() / leap_speed, clip_air, maxf(leap_air_max, clip_air))
	var hung := air <= clip_air + 0.01
	var t := 0.0
	while t < air and is_instance_valid(b) and b.action == clip and player.alive:
		await get_tree().process_frame
		t += get_process_delta_time()
		if not hung and t >= clip_air * 0.5:
			b.freeze(air - clip_air)  # the body holds the top of the leap for the extra air time
			hung = true
		var at := from.lerp(land_at, minf(t / air, 1.0))
		player.global_position = Vector3(at.x, from.y, at.z)


func hop_and_jab() -> void:
	var b := _body()
	if b == null or not _begin("HopJab"):
		return
	used.emit("1")
	var dir := _aim()
	var target := leap_pick(dir)
	var ally := target != null and MatchTeams.team_of(player) != "" and not MatchTeams.is_enemy(target, player)
	leap_target = target
	last_leap = "" if target == null else ("ally" if ally else "enemy")
	var land_at := feet()
	if target != null:
		dir = flat(target.global_position - feet()).normalized()
		land_at = _landing(target, leap_ally_gap if ally else hop_stop_short)  # reaches run from the middle to the edge
		if is_instance_valid(fx):
			fx.flash(target.global_position + Vector3.UP * 0.2, 2.4, Color(0.55, 1.0, 0.8) if ally else Color.WHITE, 0.35)
	player.facing = dir
	var clip := _leap_clip(b) if target != null else "HopJab"  # the plain hop keeps its own clip
	var punches := "Flurry" if clip == "Leap" and b.has_clip("Flurry") else clip
	_play(b, clip)
	if await _event(b, clip, "hop"):
		cue.emit("hop")
		var t := 0.0
		if target != null:
			await _fly(b, land_at, clip)
		else:
			while t < CLIP_AIR and is_instance_valid(b) and b.action == "HopJab" and player.alive:
				var dt := get_process_delta_time()
				t += dt
				if _in_cone(dir, hop_stop_short, 60.0).is_empty():  # it lands in front of an enemy, not through it
					player.global_position = ArenaMotion.slide(player, player.global_position, dir * hop_distance * dt / CLIP_AIR, player.body_radius())
				await get_tree().process_frame
	if await _event(b, clip, "land"):
		cue.emit("hop_land")
		impact.emit(0.15)
		if ally and is_instance_valid(target):
			# Landing by an ally: no punches. The cover is written on both machines for the match's hit rule to read.
			for m: Node3D in [player, target]:
				m.set_meta("kangaroo_cover", {"share": leap_cover_share, "seconds": leap_cover_time})
			_cover_until = _clock + leap_cover_time
			_cover_ally = target
			cue.emit("leap_cover")
			if is_instance_valid(fx):
				fx.flash(feet() + Vector3.UP * 0.2, 3.0, Color(0.55, 1.0, 0.8), 0.4)
			b.stop_action()
			_end()
			return
	if punches != clip and b.action == clip and current == "HopJab":
		_play(b, punches)  # the Leap ends on its landing; the four punches are their own clip
	for n in 4:
		if not await _event(b, punches, "hit", n + 1):
			break
		var near := _in_cone(dir, basic_range + REACH_SLACK, half_angle)
		if near.is_empty():
			cue.emit("basic_whiff")
			continue
		_deal(near[0], hopjab_damage)
		_feel(b, near[0], dir, 0.4, 0.02)
		cue.emit("hopjab_hit")
		impact.emit(0.1)
		_add_rhythm()
	await _clip_end(b, punches)
	if current == "HopJab":
		_end()


# ---- 2, tail kick --------------------------------------------------------------------------------------------------

func tail_kick() -> void:
	var b := _body()
	if b == null or current != "" or not player.alive or player.stunned > 0.0 or player.has_meta("held_by"):
		return
	var dir := _aim()
	player.facing = dir
	used.emit("2")
	_kick(b, dir, tailkick_damage, tailkick_knockback, "tail_hit", tailkick_cone)


# ---- 3, guard and counter ------------------------------------------------------------------------------------------

## Gloves up. Every hit in the next guard_time seconds is blocked and counted. Pressing 3 again (after
## guard_recast_after) or the time running out throws the counter at everything close by.
func guard() -> void:
	var b := _body()
	if guarding:
		if b != null and _guard_age >= guard_recast_after:
			_counter()
		return
	if b == null or not _begin("Guard"):
		return
	used.emit("3")
	guarding = true
	blocked = 0
	_last_attacker = null
	_guard_left = guard_time
	_guard_age = 0.0
	b.play_hold("Guard")


## The match calls this when anything hits the kangaroo. True while the gloves are up: the hit is blocked (it still
## does MatchRules.blocked_share) and it makes the counter hit harder.
func take_hit(_from: Vector3, by: Node3D = null) -> bool:
	if not guarding:
		return false
	blocked += 1
	if by != null and is_instance_valid(by):
		_last_attacker = by
	cue.emit("guard_block")
	impact.emit(0.15)
	if is_instance_valid(fx):
		fx.flash(feet() + ahead() * 0.5 + Vector3.UP * 1.1, 1.2, Color(0.55, 1.0, 0.8), 0.15)
	return true


## What the counter deals to each enemy it reaches, given the hits blocked so far.
func counter_hit_damage() -> float:
	return counter_damage * (1.0 + minf(blocked * counter_bonus, counter_bonus_cap))


func _counter() -> void:
	var b := _body()
	guarding = false
	if b == null:
		_end()
		return
	var clip := "Guard_Sweep" if b.has_clip("Guard_Sweep") else "Guard_Counter"  # the all-round sweep (round 10 clips)
	current = clip
	player.busy = true
	var face: Node3D = _last_attacker if is_instance_valid(_last_attacker) and MatchTeams.hittable(_last_attacker) else null
	if face == null:
		var close := _in_cone(ahead(), counter_reach, 180.0)
		if not close.is_empty():
			face = close[0]
	if face != null:
		var to := flat(face.global_position - feet())
		if to.length() > 0.01:
			player.facing = to.normalized()
	_play(b, clip)
	if await _event(b, clip, "hit"):
		var victims := _in_cone(ahead(), counter_reach, 180.0)  # all around
		var damage := counter_hit_damage()
		for t: Node3D in victims:
			var away := flat(t.global_position - feet())
			_deal(t, damage)
			_feel(b, t, away.normalized() if away.length() > 0.01 else ahead(), 0.9, 0.05)
			if blocked > 0 and t.has_method("stun") and MatchTeams.hittable(t):
				t.stun(counter_stun)
		if victims.is_empty():
			cue.emit("basic_whiff")
		else:
			cue.emit("counter_hit")
			impact.emit(minf(0.25 + 0.05 * victims.size(), 0.5))
			_add_rhythm()
			if is_instance_valid(fx):
				fx.flash(feet() + Vector3.UP * 0.9, counter_reach * 1.6, Color.WHITE, 0.2)
	await _clip_end(b, clip)
	if current == clip:
		_end()


# ---- 4, title bout ---------------------------------------------------------------------------------------------------

## The enemy machine slot 4 would call out: within bout_range and leap_cone of the aim. Null: nothing happens.
func bout_pick(dir: Vector3) -> Node3D:
	return leap_pick(dir, bout_range, false)


## The key keeps its old name for the match's bot plan. Leap to one enemy, touch gloves, ring up, bout_beats punches
## on the beat, then the tail kick sends it out through the ropes.
func boxing_ring() -> void:
	var b := _body()
	if b == null or current != "" or not is_instance_valid(player) or not player.alive or player.stunned > 0.0 \
			or player.has_meta("held_by"):
		return
	var target := bout_pick(_aim())
	if target == null:
		cue.emit("bout_no_target")  # nobody under the aim: the slot is not spent
		return
	if not _begin("Bout"):
		return
	used.emit("4")
	cue.emit("ring_cast")
	ring_target = target
	bout_beat = 0
	bout_crits = 0
	last_crit = false
	_bout_land = -1000.0
	_bout_last = -1000.0
	var dir := flat(target.global_position - feet()).normalized()
	player.facing = dir
	var land_at := _landing(target, hop_stop_short)
	if is_instance_valid(fx):
		fx.flash(target.global_position + Vector3.UP * 0.2, 2.4, Color.WHITE, 0.35)

	# the leap in
	var leap := _leap_clip(b)
	_play(b, leap)
	if not await _event(b, leap, "hop"):
		_bout_cut(b)
		return
	cue.emit("hop")
	await _fly(b, land_at, leap)
	if not await _event(b, leap, "land") or not _bout_target_ok():
		_bout_cut(b)
		return
	cue.emit("hop_land")
	impact.emit(0.15)
	if target.has_method("stun"):
		target.stun(_bout_length() + 0.45)  # held from the landing until the kick lands
	if not target.has_meta("held_by"):
		target.set_meta("held_by", player)  # the match's own lock: no moving, attacking or casting, and a brace cannot shrug it off
		_bout_holds = true
	target_locked = true
	slips = 0
	_bout_dir = -_bout_dir

	# touch gloves, and the ring goes up
	_face(target)
	_play(b, "Ring_Cast")
	if await _event(b, "Ring_Cast", "glove_tap"):
		cue.emit("glove_tap")
	if not await _event(b, "Ring_Cast", "ring") or not _bout_target_ok():
		_bout_cut(b)
		return
	ring_centre = feet().lerp(target.global_position, 0.5)
	ring_centre.y = feet().y
	ring_on = true
	for m: Node3D in [player, target]:
		m.set_meta("untouchable", player)  # the kangaroo node: the match lets the mark lapse if the kangaroo is gone
	if is_instance_valid(fx):
		fx.ring(ring_centre, ring_radius, _bout_length() + 0.45)
	cue.emit("bout_start")
	impact.emit(0.3)

	# the punches, each landing on its beat
	var start := _clock
	for i in bout_beats:
		var clip: String = BOUT_CLIPS[i % BOUT_CLIPS.size()]
		_bout_land = start + bout_first_beat + i * bout_beat_time
		if i == 0:
			_press_good = false
			_press_spoiled = false
		while _clock < _bout_land - float(HIT_AT[clip]):
			if current != "Bout" or not _bout_target_ok():
				_bout_cut(b)
				return
			await get_tree().process_frame
		_face(target)
		_turn_to_me(target)
		_play(b, clip)
		if not await _event(b, clip, "hit") or current != "Bout" or not _bout_target_ok():
			_bout_cut(b)
			return
		bout_beat = i + 1
		last_crit = _press_good and not _press_spoiled
		_bout_last = _clock
		if last_crit:
			bout_crits += 1
		if _reach_of(target) <= basic_range + kick_reach_bonus + REACH_SLACK:
			_deal(target, bout_punch_damage * (bout_crit if last_crit else 1.0))
			_feel(b, target, ahead(), 0.9 if last_crit else 0.5, 0.05 if last_crit else 0.03)
			impact.emit(0.22 if last_crit else 0.12)
			var tb: Variant = target.get("body")
			if tb is MechModel3D and tb.has_clip("Reel"):
				tb.play_action("Reel")  # it starts and ends on Stun's first frame, so the hold takes over again after it
		cue.emit("bout_beat")
		if i < bout_beats - 1:  # the next punch is on the clock from now, so the countdown and the presses carry through the slip
			_bout_land = start + bout_first_beat + (i + 1) * bout_beat_time
			_press_good = false
			_press_spoiled = false
		if i < bout_beats - 1 and i < bout_slip_angles.size():
			await _bout_slip(b, target, bout_slip_angles[i] * _bout_dir)
			if current != "Bout" or not _bout_target_ok():
				_bout_cut(b)
				return
	_bout_land = _clock + maxf(b.clip_length(BOUT_CLIPS[(bout_beats - 1) % BOUT_CLIPS.size()]) - float(HIT_AT[BOUT_CLIPS[(bout_beats - 1) % BOUT_CLIPS.size()]]), 0.0) + KICK_HIT_AT
	_press_spoiled = true  # the kick has no crit
	await _clip_end(b, BOUT_CLIPS[(bout_beats - 1) % BOUT_CLIPS.size()])
	if current != "Bout" or not _bout_target_ok():
		_bout_cut(b)
		return

	# the kick out through the ropes
	_face(target)
	_turn_to_me(target)
	dir = ahead()
	_play(b, "TailKick")
	if await _event(b, "TailKick", "brace"):
		cue.emit("tail_brace")
	if not await _event(b, "TailKick", "hit") or current != "Bout":
		_bout_cut(b)
		return
	_bout_land = -1000.0
	if _bout_target_ok():
		target.remove_meta("untouchable")  # it leaves the ring: anyone can hit it again
		_bout_release(target)
		if "stunned" in target:
			target.stunned = minf(target.stunned, 0.02)  # the hold ends with the kick; a slam stuns it again
		if _reach_of(target) <= basic_range + kick_reach_bonus + REACH_SLACK:
			_deal(target, bout_kick_damage)
			_feel(b, target, dir, 1.3, 0.08)
			_launch(target, dir)
			cue.emit("tail_hit")
			cue.emit("bout_launch")
			impact.emit(0.45)
		else:
			cue.emit("basic_whiff")
	_bout_release(target)
	ring_target = null
	if await _event(b, "TailKick", "land"):
		cue.emit("tail_land")
	await _clip_end(b, "TailKick")
	_chain_end = _clock
	if current == "Bout":
		_bout_over()


## Seconds from the ring going up to the kick landing.
func _bout_length() -> float:
	var last: String = BOUT_CLIPS[(bout_beats - 1) % BOUT_CLIPS.size()]
	var tail := 0.4
	var b := _body()
	if b != null:
		tail = maxf(b.clip_length(last) - float(HIT_AT[last]), 0.0)
	return bout_first_beat + (bout_beats - 1) * bout_beat_time + tail + KICK_HIT_AT


## Turns the bout's enemy to face the kangaroo, so each punch lands on its front and its reaction reads.
func _turn_to_me(t: Node3D) -> void:
	var to := flat(feet() - t.global_position)
	if to.length() > 0.01 and "facing" in t:
		t.facing = to.normalized()


## Takes the bout's lock off the enemy, if this kit put it on.
func _bout_release(t: Variant) -> void:
	if _bout_holds and is_instance_valid(t) and t.has_meta("held_by") and t.get_meta("held_by") == player:
		t.remove_meta("held_by")
	_bout_holds = false


## One slip: after bout_slip_delay the kangaroo goes `degrees` round the enemy at the distance it already stands
## (positive: to its own left), ducking with the Slip clip when the body has one. Walls stop it short.
func _bout_slip(b: MechModel3D, target: Node3D, degrees: float) -> void:
	var t0 := _clock
	while _clock - t0 < bout_slip_delay:
		if current != "Bout" or not _bout_target_ok():
			return
		await get_tree().process_frame
	var centre := flat(target.global_position)
	var arm := flat(feet()) - centre
	if arm.length() < 0.05 or absf(degrees) < 0.5:
		return
	var theta := -deg_to_rad(degrees)  # facing the enemy, the kangaroo's left is clockwise seen from above
	var end := centre + arm.rotated(Vector3.UP, theta)
	slip_from = feet()
	slip_to = Vector3(end.x, feet().y, end.z)
	slip_time = bout_slip_time
	slip_side = 1 if degrees > 0.0 else -1
	slips += 1
	cue.emit("bout_slip")
	var clip := "Slip_Left" if slip_side > 0 else "Slip_Right"
	if b.has_clip(clip):
		_play(b, clip)
	var t := 0.0
	while t < bout_slip_time:
		await get_tree().process_frame
		t += get_process_delta_time()
		if current != "Bout" or not _bout_target_ok():
			return
		var k := clampf((t - 0.04) / 0.17, 0.0, 1.0)  # the Slip clips' feet are off the ground from "push" to "land"
		k = k * k * (3.0 - 2.0 * k)
		var want := centre + arm.rotated(Vector3.UP, theta * k)
		var here: Vector3 = player.global_position
		player.global_position = ArenaMotion.slide(player, here, Vector3(want.x - here.x, 0.0, want.z - here.z), player.body_radius())
		_face(target)


func _bout_target_ok() -> bool:
	return is_instance_valid(ring_target) and ring_target.get("alive") == true


func _face(t: Node3D) -> void:
	var to := flat(t.global_position - feet())
	if to.length() > 0.01:
		player.facing = to.normalized()


## A fresh attack press during the bout. In the window before a punch lands it makes that punch a crit; earlier than
## the window it spoils the beat; just after a punch landed it is ignored.
func bout_press() -> void:
	if current != "Bout" or not ring_on or _bout_land < -999.0 or _press_spoiled:
		return
	if _clock - _bout_last <= bout_grace:
		return
	var early := _bout_land - _clock
	if early <= bout_window:
		_press_good = true
	else:
		_press_spoiled = true


## The bout stopped before its end (the enemy died, or the kangaroo was killed, stunned or grabbed).
func _bout_cut(b: MechModel3D) -> void:
	if current != "Bout":
		return  # _abort already ended it
	if is_instance_valid(b) and b.action != "":
		b.stop_action()
	_bout_over()


func _bout_over() -> void:
	var was_up := ring_on
	ring_on = false
	_bout_land = -1000.0
	bout_next_beat = -1.0
	for m: Variant in [player, ring_target]:
		if is_instance_valid(m) and m.has_meta("untouchable"):
			m.remove_meta("untouchable")
	_bout_release(ring_target)
	target_locked = false
	if is_instance_valid(ring_target) and "stunned" in ring_target:  # a cut bout lets go of the enemy it was holding
		ring_target.stunned = minf(ring_target.stunned, 0.02)
	ring_target = null
	if is_instance_valid(fx) and "_live" in fx:
		for item: Dictionary in fx._live:
			if item.get("kind") == "ring":
				item["life"] = minf(float(item["life"]), float(item["t"]) + 0.25)  # the ropes drop with the bout
	if was_up:
		cue.emit("bout_end")
	_end()


## While the ring is up: the called-out enemy stays inside it and everyone else is kept out.
func _tick_ring() -> void:
	if _bout_target_ok():
		var out := flat(ring_target.global_position - ring_centre)
		var limit := ring_radius - 0.5
		if out.length() > limit:
			var p := ring_centre + out.normalized() * limit
			ring_target.global_position = Vector3(p.x, ring_target.global_position.y, p.z)
	if MatchTeams.team_of(player) == "":
		return
	for u: Node in get_tree().get_nodes_in_group("match_unit"):
		if u == player or u == ring_target or not (u is Node3D) or u.get("alive") != true:
			continue
		if u.get("kind") == "tower" or u.get("kind") == "core":
			continue
		var away := flat(u.global_position - ring_centre)
		var r: float = u.radius() if u.has_method("radius") else 0.5
		if away.length() < ring_radius + r:
			var at: Vector3 = ring_centre + (away.normalized() if away.length() > 0.01 else ahead()) * (ring_radius + r)
			u.global_position = Vector3(at.x, u.global_position.y, at.z)
