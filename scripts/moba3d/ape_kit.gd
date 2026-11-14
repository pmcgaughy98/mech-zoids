class_name ApeKit
extends Node
## Arena Play installs arena_gorilla_kit.gd, the subclass with selected grab-slam/Drive and guarded ult.
## Legacy reveal helpers below remain available; this header's original four slots describe that earlier slice.
## The gorilla's kit in the 3D slice (Claude, 2026-11-04, game feel lane). What each ability does is Preston's
## design in docs/plan/moba-kits.md (Gorilla), under its working labels. Keys 1-4 in the field; a reveal can call the
## same functions. Every length below is a presentation placeholder so the abilities can be seen, not a balance
## number: there are no cooldowns, damage or reduction numbers yet.
##   Passive, silverback: allies (group "kit_ally") inside the green ring around the gorilla are covered (covers()).
##   1 hex shield: throws a green hex shield onto the nearest ally in range, or itself; it clears one slow.
##   2 chest beat: enemies (group "kit_target") close around it are taunted for a moment.
##   3 bound: leaps to the nearest ally in range, or a spot ahead; landing knocks enemies back.
##   4 hex dome: raises a dome of green hex panels; hits from outside stop at its wall (take_hit, dome_at()).
##     Enemies inside when it rises are trapped and enemies outside cannot walk in; allies cross both ways. Enemy
##     shots stop at the wall from either side and wear down its health; at zero it breaks early. Ally shots stop at
##     it too but leave its health alone (Preston, 2026-11-04; the health part is Mech-Zoids' default).
## Every slot plays its own frames (Codex sets A and B, packed by the animation lane). If a sheet lacks an ability's
## frames, it runs on the placeholder timings below with the idle pose instead.
## On a rigged 3D body (player.body, a MechModel3D; stage 1 of the match's move to models, gorilla lane 2026-11-09)
## a slot plays the body's clip and acts on the clip's events instead: the basic chain is Swat_Right, Swat_Left,
## Slam with damage on the event flagged damage; Fling acts on "grab"; the ult on its three "beat" events; the hex
## shield on "release" once the model has the shield clips. A slot whose clip the body lacks keeps the sprite path.

signal impact(strength: float) ## something landed hard; cameras can shake on it
signal used(slot: String)
signal cue(name: String) ## a sound moment for KitAudio's cue rows: strike_swing, strike_hit
signal contact(target: Node3D, slam: bool) ## confirmed basic contact, for model effects
signal shield_applied(target: Node3D) ## actual release, separate from targeting/confirmation
signal _body_tick ## a body clip fired an event, ended, or its body left the tree: wakes the kit's waiters in that same frame

const APE_FRAMES := preload("res://art/machines/ape/ape_frames.tres")
const SHIELD_RELEASE_FRAME := 3 ## hex_shield f3: the widest side silhouette, throwing arm furthest forward (x 141 vs 135)
const BEAT_FRAMES: Array[int] = [2, 3, 4] ## chest_beat f2-f4: the three quick beats (0.1 s each)
const BOUND_PUSH_FRAME := 2 ## bound f2: the push-off (Codex set B brief)
const BOUND_LAND_FRAME := 6 ## bound f6: the fist-slam landing
const DOME_SLAM_FRAME := 5 ## hex_dome f5: both fists hit the ground
const STRIKE_ANIM := "strike" ## the basic attack's own frames: none yet (asked of the attack lane, 2026-11-05)
const STRIKE_HIT_FRAME := 2 ## a guess until the strike frames exist; set it to their contact frame
const STAND_IN_ANIM := "hex_shield" ## until then the swing borrows the shield throw
const STAND_IN_HIT_FRAME := SHIELD_RELEASE_FRAME ## f3: the arm thrown furthest forward
const STRIKE_B_ANIM := "strike_b" ## the other fist; swings alternate (Preston, 2026-11-06: "bunch with both hands one at
## a time"). A view with no drawing of its own gets strike's frames under this name when packed.

@export_group("Placeholder lengths, not balance")
@export var aura_radius := 2.5 ## matches silverback_ring_f0.png (tools/art/draw_ape_kit_fx.py)
@export var shield_range := 6.0
@export var shield_time := 3.0
@export var taunt_radius := 3.0
@export var taunt_time := 1.5
@export var bound_range := 7.0
@export var bound_distance := 5.0 ## straight ahead when no ally is in range
@export var bound_stop_short := 1.2 ## lands this far short of the ally
@export var bound_radius := 2.4
@export var knockback := 2.2
@export var bound_air_time := 0.5 ## only until the bound frames exist; then the frames set the time
@export var bound_height := 1.0 ## only until the bound frames exist; the frames carry their own lift
@export var ult_radius := 5.5 ## chest beat ult (Preston, 2026-11-09): taunt and ally shields reach this far; the old chest beat was 3.0
@export var ult_taunt_time := 1.5
@export var ult_dome_radius := 5.5 ## the taunt reach (Preston, 2026-11-09: "Yes, all three", game feel's cage changes); was 7.0
@export var ult_panels := 10 ## the ult dome wall is this many panels, each broken on its own (about 3.5 m of wall each at 5.5 m)
@export var ult_panel_health := 60.0 ## placeholder: what one panel takes before it breaks and opens a gap
@export var dome_ward_heal := 0.06 ## proposal (Preston, 2026-11-09): share of max hp healed each second inside the ult dome (the 1 hp floor was dropped, 2026-11-09)
@export var beat_times: Array[float] = [] ## seconds after the cast for each beat, from a 3D model's clip (v22 slowed 2026-11-09: 0.42, 0.75, 1.27); empty uses the sprite frames
@export var beat_gap := 0.15 ## seconds between beats when the chest beat has no frames of its own
@export var dome_radius := 3.2
@export var dome_time := 4.0
@export var dome_cast_time := 0.4 ## only until the hex dome frames exist
@export var dome_health := 100.0 ## placeholder: the dome wall's health; each enemy shot wears it down
@export var hit_damage := 10.0 ## placeholder: what a hit on the dome wall takes off it, until hits carry their own

@export_group("Fling, slot 2 (Preston's pick, 2026-11-09; game feel's starting numbers)")
@export var fling_reach := 1.6 ## metres edge to edge: the nearest enemy in front this close is grabbed
@export var fling_cone := 70.0 ## degrees either side of the aim
@export var fling_windup := 0.18 ## the grab: the victim can read it
@export var fling_distance := 4.0 ## thrown this far behind the gorilla
@export var fling_height := 1.5 ## the arc over the gorilla's head
@export var fling_air_time := 0.45
@export var fling_wall_stun := 0.5 ## only when it lands short: the dome wall, a hex wall or terrain stopped it
@export var fling_wall_hitstop := 0.06
@export var fling_recover := 0.3 ## after the release, before the gorilla moves again

@export_group("Basic attack, fist strike (working label; picks for Preston to tune)")
@export var basic_range := 2.2 ## metres edge to edge (MatchTeams.edge_distance); the rhino's horn jab is 2.0
@export var basic_cooldown := 1.0 ## seconds between strikes; the director keeps it
@export var basic_damage := 28.0 ## 28 a second at 1.0 s, a little under the rhino's 33: the gorilla guards
@export var basic_cone_degrees := 60.0 ## with no target, the strike takes the nearest enemy this close to the aim
@export var strike_assist := true ## Space with nothing where it aims: the strike turns to the nearest enemy in reach (Preston, 2026-11-05)
@export var basic_hitstop := 0.06 ## seconds the hit frame holds
@export var basic_shake := 0.0 ## random shake on a hit: off, the kick along the punch replaces it (Preston, 2026-11-06)
@export var strike_anim_speed := 1.1 ## the drawn strike: a 100 ms tick a frame, so contact (F2) at 0.18 s and the end at 0.45 s
@export var basic_chain := true ## held hits go swat, swat, slam (Preston, 2026-11-09: "Yes, add the slam", "More damage")
@export var slam_every := 3 ## the slam is this hit of the chain
@export var slam_damage := 42.0 ## 1.5x a swat: 28 + 28 + 42 = 98 every 3 s, 32.7 a second, level with the rhino's 33
@export var slam_hitstop := 0.09 ## game feel's starting number (swats hold 0.06)
@export var slam_strength := 1.5 ## KitFeel.basic_hit strength: a bigger lunge and shove than a swat
@export var slam_shake := 0.3 ## the slam alone shakes the camera; swats stay at basic_shake 0 (Preston, 2026-11-06)
@export var chain_reset := 1.5 ## seconds without a hit before the chain goes back to hit 1
@export var stand_in_anim_speed := 3.0 ## the borrowed shield throw: 12.7 ticks at 10 fps, 0.42 s at 3x, the hit at 0.22 s
@export var walking_swats := true ## moving, a swat plays the clip built on that gait (walk, strafe left or right, backpedal) and the machine keeps moving (Preston, 2026-11-11 and 2026-11-13)
@export var strike_clip_speed := 1.0 ## the 3D body's swats and slam: contact at 0.30 s and 0.417 s at speed 1 (gorilla lane's clips)

var current := "" ## the ability in progress, or ""
var last_hand := "" ## the fist the last strike threw: right (strike) or left (strike_b)
var _left_next := false
var chain_hit := 0 ## where the last swing sat in the chain: 1, 2, or slam_every for the slam
var last_was_slam := false
var _chain_timer: SceneTreeTimer ## game time since the last hit that landed; the chain resets when it runs out
var _recovering := false ## the strike's backswing: moving or an ability cancels it
var shake_camera := true ## impact shakes the match camera; ape_reveal turns it off, as it shakes its own camera
var _aura: Node3D
var _domes := []
const DAMAGE := "*damage" ## key in _ev_seen: how many events flagged damage the body clip has fired
var _ev_clip := "" ## the body clip this kit last started
var _ev_seen := {} ## event name -> how many times it has fired in that clip
var _ev_id := 0 ## goes up with every body clip the kit starts; a waiter from an older clip stops on it
var _ult_body: MechModel3D ## the body playing the ult's clip, while it does

@onready var player = get_parent() ## machine_test_player.gd
@onready var sprite: DirectionalSprite3D = get_parent().get_node("Sprite")


## Turns a field Player into the gorilla: the ape frames, and this kit in place of whatever kit it had.
static func install(p: Node3D) -> ApeKit:
	var spr: DirectionalSprite3D = p.get_node("Sprite")
	spr.stop_action()
	spr.sprite_frames = APE_FRAMES
	spr.size_class = "L"  # after a smaller machine (Tab in arena_play)
	spr.play(StringName("idle_" + spr.view))
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var kit := ApeKit.new()
	kit.name = "Kit"
	p.add_child(kit)
	return kit


## Test helper: a training dummy becomes an ally (blue, group kit_ally) for the shield and bound to reach.
static func make_ally(d: Node) -> void:
	d.remove_from_group("kit_target")
	d.add_to_group("kit_ally")
	if "tint" in d:
		d.tint = Color(0.6, 0.8, 1.3)


## The hex shield (not a dome) on a machine, or null.
static func shield_on(node: Node) -> HexShield:
	for c in node.get_children():
		var h := c as HexShield
		if h != null and not h.dome and not h.is_queued_for_deletion():
			return h
	return null


static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


func _ready() -> void:
	_make_aura.call_deferred()
	impact.connect(_shake)
	_watch_states.call_deferred()


## Recall and respawn on the 3D body (gorilla lane, 2026-11-13). The match signals both on the machine
## (recall_started, respawned) and the body has had the clips since kit v30. Recall loops for as long as the director's
## recall runs: its RecallRing child on the machine is the only thing that says so, since a cancelled recall emits
## nothing. It never cuts an ability, a hit reaction or a stun, and anything that starts on the body replaces it.
## Respawn plays once from the wreck pose and ends early if the machine walks, so it never slides.
func _watch_states() -> void:
	if not (player is Node3D):
		return
	if player.has_signal("recall_started") and not player.recall_started.is_connected(_on_recall_started):
		player.recall_started.connect(_on_recall_started)
	if player.has_signal("respawned") and not player.respawned.is_connected(_on_respawned):
		player.respawned.connect(_on_respawned)


func _on_recall_started() -> void:
	var b := _body("Recall")
	if b == null or current != "" or b.action != "":
		return
	if not b.play_hold("Recall", 1.0, 0.15):
		return
	await get_tree().process_frame  # the director adds its ring just after the signal
	while is_instance_valid(b) and b.action == "Recall" and is_instance_valid(player) and player.get_node_or_null("RecallRing") != null:
		await get_tree().process_frame
	if is_instance_valid(b) and b.action == "Recall":
		b.stop_action()


func _on_respawned() -> void:
	var b := _body("Respawn")
	if b == null:
		return
	await get_tree().process_frame  # the player clears a Death clip that is still up on this frame
	if not is_instance_valid(b) or not is_instance_valid(player) or current != "" or b.action != "" or player.get("alive") == false:
		return
	b.play_action("Respawn", 1.0, 0.0)
	while is_instance_valid(b) and b.action == "Respawn":
		if player.move_dir().length() > 0.05:
			b.stop_action()
			return
		await get_tree().process_frame


func _shake(strength: float) -> void:
	if shake_camera and not player.get("bot"):
		KitFeel.shake(self, strength)


## The silverback ring is the gorilla's: it goes when the kit does (a swap to another machine).
func _exit_tree() -> void:
	if is_instance_valid(_aura):
		_aura.queue_free()


func _make_aura() -> void:
	if not (player is Node3D):  # a kit on its own (the sound lane's audio check) has no machine to ring
		return
	_aura = Fx3D.spawn_flat(player, "silverback_ring", 1, feet() + Vector3.UP * 0.025, aura_radius * 2.0)


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if player.get("bot") or (player.has_method("slot_ready") and not player.slot_ready(str(k.physical_keycode - KEY_0))):
		return  # a bot's kit ignores the keyboard; in a match a slot waits out its cooldown (MatchRules)
	match k.physical_keycode:
		KEY_1:
			hex_shield()
		KEY_2:
			fling()
		KEY_3:
			bound()
		KEY_4:
			chest_beat_ult()


## The machine's rigged 3D body when it has one (and, with a clip named, only when the body has that clip), else
## null: the slot then runs on the sprite frames as it always has.
func _body(clip := "") -> MechModel3D:
	var b: Variant = player.get("body") if player != null else null
	if b == null or not is_instance_valid(b):
		return null
	var m := b as MechModel3D
	return m if m != null and (clip == "" or m.has_clip(clip)) else null


## Starts a clip on the body and begins counting its events. Returns its length in seconds.
func _play(b: MechModel3D, clip: String, speed := 1.0) -> float:
	if not b.event.is_connected(_on_body_event):
		b.event.connect(_on_body_event)
		b.action_finished.connect(_on_body_done)
		b.tree_exiting.connect(_on_body_done.bind(""))
	_ev_id += 1
	_ev_clip = clip
	_ev_seen = {}
	return b.play_action(clip, speed)


func _on_body_event(clip: String, ev: String, damage: bool) -> void:
	if clip != _ev_clip:
		return
	_ev_seen[ev] = int(_ev_seen.get(ev, 0)) + 1
	if damage:
		_ev_seen[DAMAGE] = int(_ev_seen.get(DAMAGE, 0)) + 1
	_body_tick.emit()


func _on_body_done(_clip: String) -> void:
	_body_tick.emit()


## How many events named ev (or flagged damage, for DAMAGE) the body's clip carries.
func _event_count(b: MechModel3D, clip: String, ev: String) -> int:
	var n := 0
	for e in b.events_of(clip):
		if (ev == DAMAGE and bool(e[2])) or String(e[0]) == ev:
			n += 1
	return n


## Waits until the body's clip has fired ev `count` times. False when the clip ended or was replaced first (a death,
## another action on the body), or when the clip has no such event.
func _wait_event(b: MechModel3D, clip: String, ev: String, count := 1) -> bool:
	var id := _ev_id
	while is_instance_valid(b) and b.is_inside_tree() and _ev_id == id and int(_ev_seen.get(ev, 0)) < count and b.action == clip:
		await _body_tick  # the event itself, not the frame after: the hit and its hitstop land on the contact pose
	return _ev_id == id and int(_ev_seen.get(ev, 0)) >= count and player.get("alive") != false


## The same, for a clip that may not carry the event yet: then it waits `fallback` seconds into the clip instead.
func _wait_event_or(b: MechModel3D, clip: String, ev: String, fallback: float) -> bool:
	if _event_count(b, clip, ev) > 0:
		return await _wait_event(b, clip, ev)
	var id := _ev_id
	await get_tree().create_timer(fallback).timeout
	return is_instance_valid(b) and _ev_id == id and player.get("alive") != false


## Lets the body's clip play out after the kit has let go of the machine. Moving ends it early, so the recovery
## never slides; a newer clip from the kit takes over on its own.
func _recover(b: MechModel3D, clip: String) -> void:
	var id := _ev_id
	while is_instance_valid(b) and _ev_id == id and b.action == clip:
		if player.move_dir().length() > 0.05:
			b.stop_action()
			return
		await get_tree().process_frame


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


## Passive, silverback: true while an ally stands inside the ring (it takes a little less damage; how much is Preston's).
func covers(ally: Node3D) -> bool:
	return flat(ally.global_position - feet()).length() <= aura_radius


## The hex dome standing over pos, or null.
func dome_at(pos: Vector3) -> HexShield:
	_domes = _domes.filter(func(d): return is_instance_valid(d) and d.is_up())
	for d in _domes:
		if flat(pos - d.global_position).length() <= d.radius:
			return d
	return null


## Call when anything hits the gorilla; true when a hex shield or a dome wall takes the hit.
func take_hit(from: Vector3) -> bool:
	var to := flat(from - feet()).normalized()
	var wall := dome_at(feet())
	if wall != null and dome_at(from) == wall:  # a hit from inside the dome reaches the gorilla
		wall = null
	var own := shield_on(player)
	var blocked := wall != null or own != null
	if wall != null:
		wall.damage(hit_damage)  # enemy hits wear the wall down; at zero it breaks early
		var r := sqrt(maxf(wall.radius * wall.radius - 0.81, 0.0))  # the wall's reach at chest height
		Fx3D.spawn(world(), "deflect_spark", wall.global_position + to * r + Vector3.UP * 0.9, 0.3)
	else:
		if own != null:
			own.hit()
		Fx3D.spawn(world(), "deflect_spark" if blocked else "hit_spark", feet() + to * 0.9 + Vector3.UP * 0.9, 0.3)
	if not blocked:
		sprite.modulate = Color(2.0, 2.0, 2.0)
		create_tween().tween_property(sprite, "modulate", Color.WHITE, 0.15)
		var b := _body()
		if b != null:
			b.flash()
	impact.emit(0.1 if blocked else 0.25)
	return blocked


func hex_shield(target: Node3D = null) -> void:
	if not _begin("hex_shield"):
		return
	used.emit("1")
	if target == null:target = _nearest_ally(shield_range)
	if target != null:
		var d := flat(target.global_position - feet())
		if d.length() > 0.05:
			player.facing = d.normalized()  # turns to throw at the ally
	else:
		target = player
	# the 3D body's cast (Preston accepted the trial, 2026-11-09): the shield lands on the clip's release; a cast cut
	# off before it gives no shield; after it the recovery is free and moving ends it
	var clip := "Shield_Self" if target == player else "Shield_Ally"
	var b := _body(clip)
	var released := true
	if b != null:
		_play(b, clip)
		released = await _wait_event_or(b, clip, "release", 0.25)
	elif _framed("hex_shield"):
		await _wait_frame("hex_shield", SHIELD_RELEASE_FRAME)
	if released and _shield_target_valid(target):
		var old := shield_on(target)
		if old != null:
			old.end()
		HexShield.shield(target, shield_time)
		shield_applied.emit(target)
		if "slowed" in target:
			target.slowed = 0.0  # clears one slow; roots are not in the slice yet
		impact.emit(0.2)
	if b != null:
		_end()
		if is_instance_valid(b):
			_recover(b, clip)
		return
	await _wait_end("hex_shield")
	_end()


func _shield_target_valid(target: Node3D) -> bool:
	return is_instance_valid(target)


func chest_beat() -> void:
	if not _begin("chest_beat"):
		return
	used.emit("2")
	var first := true
	for f in BEAT_FRAMES:
		if _framed("chest_beat"):
			await _wait_frame("chest_beat", f)
		_pulse(feet(), taunt_radius, 0.3 if first else 0.2)
		impact.emit(0.3 if first else 0.15)
		if first:
			first = false
			for t in targets():
				if flat(t.global_position - feet()).length() <= taunt_radius and t.has_method("taunt"):
					t.taunt(player, taunt_time)
	await _wait_end("chest_beat")
	_end()


func bound() -> void:
	if not _begin("bound"):
		return
	used.emit("3")
	var start := feet()
	var land := start + ahead() * bound_distance
	var ally := _nearest_ally(bound_range)
	if ally != null:
		var d := flat(ally.global_position - start)
		if d.length() > 0.05:
			player.facing = d.normalized()
			land = start + d - d.normalized() * minf(bound_stop_short, d.length())
	var framed := _framed("bound")
	var air := bound_air_time
	if framed:
		await _wait_frame("bound", BOUND_PUSH_FRAME)
		air = _frames_time(BOUND_PUSH_FRAME, BOUND_LAND_FRAME)
	var base_y := sprite.position.y
	var t := 0.0
	while t < air:
		await get_tree().process_frame
		t += get_process_delta_time()
		var k := minf(t / air, 1.0)
		var to := start.lerp(land, k)
		player.global_position = ArenaMotion.slide(player, player.global_position, to - player.global_position, player.body_radius())
		if not framed:
			sprite.position.y = base_y + bound_height * 4.0 * k * (1.0 - k)
	sprite.position.y = base_y
	land = player.global_position  # an arena wall may have cut the leap short
	Fx3D.spawn(world(), "gp_ring", land, 0.6)
	Fx3D.spawn(world(), "impact_puff", land + ahead() * 0.5, 0.8)
	impact.emit(0.7)
	for e in targets():
		var d := flat(e.global_position - land)
		if d.length() <= bound_radius:
			e.knock_aside((d.normalized() if d.length() > 0.05 else ahead()) * knockback, 0.35)
	await _wait_end("bound")
	_end()


func hex_dome() -> void:
	if not _begin("hex_dome"):
		return
	used.emit("4")
	if _framed("hex_dome"):
		await _wait_frame("hex_dome", DOME_SLAM_FRAME)
	else:
		await get_tree().create_timer(dome_cast_time).timeout
	_raise_dome(feet())
	await _wait_end("hex_dome")
	_end()


## The ult (Preston, 2026-11-09): "him beating his chest... a wide taunt but also shield allies too", with the hex dome
## folded in. Three beats, one job each: taunt every enemy in ult_radius, hex shield every ally in ult_radius and the
## gorilla, then both fists down and the dome rises at its feet. chest_beat() and hex_dome() stay for the reveal.
func chest_beat_ult() -> void:
	if not _begin("chest_beat"):
		return
	used.emit("4")
	_ult_body = _body("Ult")
	if _ult_body != null:
		_play(_ult_body, "Ult")
	# beat 1: the wide taunt
	await _beat(0)
	_pulse(feet(), ult_radius, 0.35)
	impact.emit(0.3)
	for t in targets():
		if flat(t.global_position - feet()).length() <= ult_radius and t.has_method("taunt"):
			t.taunt(player, ult_taunt_time)
	# beat 2: re-taunts whoever stepped into reach since (Preston, 2026-11-09: no ally shields on the ult)
	await _beat(1)
	_pulse(feet(), ult_radius, 0.25)
	impact.emit(0.15)
	for t in targets():
		if flat(t.global_position - feet()).length() <= ult_radius and t.has_method("taunt"):
			t.taunt(player, ult_taunt_time)
	# beat 3: both fists down, the dome rises, and it wards the gorilla's side inside it
	await _beat(2)
	var dome := _raise_dome(feet(), ult_dome_radius, true)
	dome.ward = true
	dome.ward_owner = player
	dome.ward_heal_share = dome_ward_heal
	var b := _ult_body
	_ult_body = null
	if is_instance_valid(b) and b.action == "Ult":
		if _event_count(b, "Ult", "recover") > 0:  # the fists are locked on the plant until then
			await _wait_event(b, "Ult", "recover")
			_end()
			if is_instance_valid(b):
				_recover(b, "Ult")
			return
		while is_instance_valid(b) and b.action == "Ult":
			await get_tree().process_frame
		_end()
		return
	await _wait_end("chest_beat")
	_end()


## Fling (Preston's pick, 2026-11-09, game feel's option A): grab the nearest enemy in front and hurl it over the
## gorilla's head, fling_distance behind. If it lands short (the dome wall, a hex wall or terrain stopped it) it is
## stunned, with a hitstop and a spark at the wall. Single target, no leap, no landing ring. Returns whether it cast.
func fling(target: Node3D = null) -> bool:
	if not _begin("fling"):
		return false
	used.emit("2")
	cue.emit("fling_grab")
	var dir: Vector3 = player.aim_dir() if player.has_method("aim_dir") else ahead()
	if dir == Vector3.ZERO:
		dir = ahead()
	if target == null:
		target = _fling_pick(dir)
	if target != null:
		dir = flat(target.global_position - feet()).normalized()
	player.facing = dir
	# the 3D body: the grab is the clip's "grab" event (0.18 s, the same as fling_windup); with nobody to grab it
	# plays the whiff, whose hands clap shut on air at the same moment
	var b := _body("Fling")
	var clip := "Fling"
	if b != null:
		if target == null and b.has_clip("Fling_Whiff"):
			clip = "Fling_Whiff"
		_play(b, clip)
		await _wait_event_or(b, clip, "clap" if clip == "Fling_Whiff" else "grab", fling_windup)
	else:
		await get_tree().create_timer(fling_windup).timeout
	if target == null or not is_instance_valid(target) or _reach_of(target) > fling_reach + 0.3:
		if b != null and is_instance_valid(b) and clip == "Fling" and b.action == clip and b.has_clip("Fling_Whiff"):
			clip = "Fling_Whiff"  # it slipped the grab: carry on as the whiff from the same moment
			_play(b, clip)
			b.anim.seek(fling_windup, true)
		await get_tree().create_timer(fling_recover).timeout  # a whiff: the grab closes on air
		_end()
		if b != null and is_instance_valid(b):
			_recover(b, clip)
		return true
	last_fling = target
	var land := feet() - dir * fling_distance
	land.y = 0.0
	_watch_landing(target, land)
	target.toss_to(land, fling_height, fling_air_time, 0.0)
	await get_tree().create_timer(fling_recover).timeout
	_end()
	if b != null and is_instance_valid(b):
		_recover(b, clip)  # the heave's follow-through and the re-plant; moving ends it
	return true


var last_fling: Node3D = null ## who the last fling threw, for checks and the bot
var last_fling_wall := false ## whether it landed short against a wall


## After the throw's air time: the landing beat, and the wall beat if it came down short of where it was thrown.
func _watch_landing(target: Node3D, land: Vector3) -> void:
	last_fling_wall = false
	await get_tree().create_timer(fling_air_time + 0.02).timeout
	if not is_instance_valid(target):
		return
	cue.emit("fling_land")
	impact.emit(0.4)
	last_fling_wall = flat(target.global_position - land).length() > 0.35
	if last_fling_wall and target.has_method("stun"):
		target.stun(fling_wall_stun)
		var into := flat(land - target.global_position).normalized()
		Fx3D.spawn(world(), "deflect_spark", target.global_position + into * 0.4 + Vector3.UP * 0.9, 0.3)
		cue.emit("fling_wall")
		impact.emit(0.7)
		Engine.time_scale = 0.05  # the wall hit's own beat
		await get_tree().create_timer(fling_wall_hitstop, true, false, true).timeout
		Engine.time_scale = 1.0


func _fling_pick(dir: Vector3) -> Node3D:
	var pool: Array = targets()
	if MatchTeams.team_of(player) != "":
		pool = get_tree().get_nodes_in_group("match_unit").filter(func(u: Node) -> bool:
			return u != player and MatchTeams.is_enemy(u, player) and MatchTeams.hittable(u))
	var best: Node3D = null
	var best_d := fling_reach
	for t: Node3D in pool:
		var d := _reach_of(t)
		var to := flat(t.global_position - feet())
		if d <= best_d and (to.length() < 0.01 or rad_to_deg(dir.angle_to(to.normalized())) <= fling_cone):
			best = t
			best_d = d
	return best


func _beat(i: int) -> void:
	var b := _ult_body
	if is_instance_valid(b) and b.action == "Ult" and _event_count(b, "Ult", "beat") > i:
		await _wait_event(b, "Ult", "beat", i + 1)  # the clip's own beats (0.42, 0.75 and the slam at 1.27 s)
	elif beat_times.size() > i:
		await get_tree().create_timer(beat_times[i] - (beat_times[i - 1] if i > 0 else 0.0)).timeout
	elif _framed("chest_beat"):
		await _wait_frame("chest_beat", BEAT_FRAMES[i])
	else:
		await get_tree().create_timer(beat_gap if i > 0 else 0.1).timeout


func _raise_dome(c: Vector3, r := -1.0, cage_all := false) -> HexShield:
	r = dome_radius if r <= 0.0 else r
	var dome := HexShield.raise_dome(world(), c, r, dome_time)
	dome.set_meta("team", MatchTeams.team_of(player)) # whose dome, for the match
	if cage_all:  # the ult (Preston, 2026-11-09): nobody leaves, allies included; panels break one at a time
		dome.cage_all = true
		dome.make_panels(ult_panels, ult_panel_health)
	else:
		dome.health = dome_health
	_domes.append(dome)
	var held: Array = targets() + ((allies() + [player]) if cage_all else [])
	for e in held:  # enemies inside are trapped; the ult cage holds the gorilla's side too
		if flat(e.global_position - c).length() <= r and e.has_method("trap"):
			e.trap(dome)
	Fx3D.spawn(world(), "impact_puff", c + ahead() * 0.6, 0.8)
	impact.emit(0.8)
	return dome


## The basic attack (game feel's hook, 2026-11-05). Space and a bot's basic come here through the director, which
## keeps the cooldown (basic_cooldown) and the gates, and reads basic_range. Melee: one enemy in front, within reach.
## Until the attack lane draws strike frames, the swing borrows the hex shield throw, sped up. Refuses mid-ability.
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
	if target == null and strike_assist and _strike_pick(dir) == null:
		var near := _strike_pick(dir, 180.0)  # nothing where it aims: turn to whoever is in reach
		if near != null:
			dir = flat(near.global_position - feet()).normalized()
	player.facing = dir
	_strike(target, dir)
	return true


## One swing: wind-up and contact lock the machine; after the hit the backswing is free, and moving or an ability
## cancels it (MOBA feel, Preston 2026-11-06). Holding Space repeats it every basic_cooldown (arena_play polls the button).
func _strike(target: Node3D, dir: Vector3) -> void:
	if _chain_timer == null or _chain_timer.time_left <= 0.0:
		chain_hit = 0
	chain_hit = chain_hit % slam_every + 1
	var slam := basic_chain and chain_hit == slam_every
	last_was_slam = slam
	if slam:
		last_hand = "both"  # until slam frames exist the sprite plays the right-fist strike
	else:
		last_hand = "left" if _left_next else "right"
		_left_next = not _left_next
	var clip := "Slam" if slam else ("Swat_Left" if last_hand == "left" else "Swat_Right")
	var walking := false
	if walking_swats and not slam and player.has_method("move_dir"):
		var mv := flat(player.move_dir())
		# moving: the swat built on the gait for that direction, so no hand or foot slides. Within 50 degrees of the
		# aim it is the walk's; beyond 130 the backpedal's; in between the strafe's, to whichever side the machine is
		# going (the same left/right test as MechModel3D._side_clip). A body without that clip swats rooted.
		if mv.length() > 0.05:
			var m := mv.normalized()
			var along := m.dot(dir)
			var gait := "_Walk" if along > 0.64 else ("_Back" if along < -0.64 else ("_StrafeL" if dir.z * m.x - dir.x * m.z > 0.0 else "_StrafeR"))
			if _body(clip + gait) != null:
				clip += gait
				walking = true
	var b := _body(clip)
	if b != null:
		await _strike_3d(b, clip, target, dir, slam, walking)
		return
	var anim := ""
	var speed := stand_in_anim_speed
	var hit_frame := STAND_IN_HIT_FRAME
	if _framed(STRIKE_ANIM):
		anim = STRIKE_B_ANIM if last_hand == "left" and _framed(STRIKE_B_ANIM) else STRIKE_ANIM
		speed = strike_anim_speed
		hit_frame = STRIKE_HIT_FRAME
	elif _framed(STAND_IN_ANIM):
		anim = STAND_IN_ANIM
	current = "strike"
	player.busy = true
	cue.emit("strike_swing")
	if anim != "":
		sprite.play_action(anim)
		sprite.speed_scale = speed
		await _wait_frame(anim, hit_frame)
		if sprite.action != anim:  # something else took the sprite (a stun, a death)
			sprite.speed_scale = 1.0
			current = ""
			player.busy = false
			return
	else:
		await get_tree().create_timer(0.22).timeout
	var t: Node3D = target
	if t == null or not MatchTeams.hittable(t) or _reach_of(t) > basic_range + 0.5:
		t = _strike_pick(dir)
	if t != null:
		if anim != "":
			sprite.hold_frame(hit_frame)
		if t.has_method("hit"):
			t.hit(player, (slam_damage if slam else basic_damage) / MatchRules.kit_hit_damage)
		elif t.has_method("take_damage"):
			t.take_damage(slam_damage if slam else basic_damage, player)
		_chain_timer = get_tree().create_timer(chain_reset)
		# the lunge, the shove, the spark and the camera kick along the punch (game feel and camera lanes, 2026-11-06)
		KitFeel.basic_hit(player, t, Vector3.ZERO, slam_strength if slam else 1.0)
		cue.emit("strike_hit")
		if slam and slam_shake > 0.0:
			impact.emit(slam_shake)
		elif not slam and basic_shake > 0.0:
			impact.emit(basic_shake)
		await get_tree().create_timer(slam_hitstop if slam else basic_hitstop).timeout
		if anim != "":
			sprite.release_from(hit_frame, speed)  # the tail keeps the strike's speed
	else:
		KitFeel.nudge(sprite, dir * KitFeel.lunge_m, KitFeel.lunge_back)  # a whiff still carries the weight forward
	if anim != "":
		_recovering = true
		player.busy = false  # the backswing: free to move, and moving ends it
		while _recovering and sprite.action == anim and sprite.is_playing():
			if player.move_dir().length() > 0.05:
				break
			await get_tree().process_frame
		if not _recovering:  # an ability cancelled the backswing and owns the machine now
			return
		_recovering = false
		if sprite.action != anim and sprite.action != "":  # something else took the sprite (a stun, a death)
			current = ""
			return
	_end()


## The same swing on the rigged 3D body: the clip's wind-up locks the machine, the hit lands on the clip's damage
## event, hitstop freezes the body, and the backswing is free: moving or an ability ends it. The lunge is in the
## clip, so the attacker gets no extra nudge (game feel, 2026-11-09).
## walking: the clip is a swat built on the walk (Swat_*_Walk). The machine is not rooted, there is no hitstop
## (a frozen pose would slide), and the clip ends early only if the machine stops.
func _strike_3d(b: MechModel3D, clip: String, target: Node3D, dir: Vector3, slam: bool, walking := false) -> void:
	current = "strike"
	player.busy = not walking
	cue.emit("strike_swing")
	_play(b, clip, strike_clip_speed)
	var id := _ev_id
	if not await _wait_event(b, clip, DAMAGE):
		if _ev_id == id:  # cut off before contact (a death, another clip on the body): no hit
			if is_instance_valid(b) and b.action == clip:
				b.stop_action()
			current = ""
			player.busy = false
		return
	var t: Node3D = target
	if t == null or not is_instance_valid(t) or not MatchTeams.hittable(t) or _reach_of(t) > basic_range + 0.5:
		t = _strike_pick(dir)
	if t != null:
		if t.has_method("hit"):
			t.hit(player, (slam_damage if slam else basic_damage) / MatchRules.kit_hit_damage)
		elif t.has_method("take_damage"):
			t.take_damage(slam_damage if slam else basic_damage, player)
		_chain_timer = get_tree().create_timer(chain_reset)
		KitFeel.basic_hit(player, t, Vector3.ZERO, slam_strength if slam else 1.0)
		contact.emit(t,slam)
		cue.emit("strike_hit")
		if slam and slam_shake > 0.0:
			impact.emit(slam_shake)
		elif not slam and basic_shake > 0.0:
			impact.emit(basic_shake)
		if not walking:
			var hold := slam_hitstop if slam else basic_hitstop
			b.freeze(hold)
			await get_tree().create_timer(hold).timeout
	_recovering = true
	player.busy = false  # the backswing: free to move, and moving ends it
	while _recovering and _ev_id == id and is_instance_valid(b) and b.action == clip:
		if (player.move_dir().length() > 0.05) != walking:  # a standing swat ends when the machine walks off; a walking swat when it stops
			b.stop_action()
			break
		await get_tree().process_frame
	if not _recovering:  # an ability cancelled the backswing and owns the machine now
		return
	_recovering = false
	_end()


## The nearest enemy within basic_range and basic_cone_degrees of dir; in a match, any enemy match unit.
func _strike_pick(dir: Vector3, cone := -1.0) -> Node3D:
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
		if d <= best_d and (cone >= 180.0 or to.length() < 0.01 or rad_to_deg(dir.angle_to(to.normalized())) <= cone):
			best = t
			best_d = d
	return best


func _reach_of(t: Node3D) -> float:
	return MatchTeams.edge_distance(player, t)


## A green ring that swells to `radius` and fades: the reach of a beat.
func _pulse(c: Vector3, radius: float, life: float) -> void:
	var f = Fx3D.spawn_flat(world(), "silverback_ring", 1, c + Vector3.UP * 0.03, radius * 2.0)
	f.scale = Vector3.ONE * 0.7
	var tw: Tween = f.create_tween().set_parallel()
	tw.tween_property(f, "scale", Vector3.ONE, life)
	tw.tween_property(f.mat, "albedo_color:a", 0.0, life)
	tw.chain().tween_callback(f.queue_free)


func _nearest_ally(r: float) -> Node3D:
	var best: Node3D = null
	var best_d := r
	for a in allies():
		var d := flat(a.global_position - feet()).length()
		if d <= best_d:
			best = a
			best_d = d
	return best


## Seconds from frame a to frame b of the action playing now.
func _frames_time(a: int, b: int) -> float:
	var anim := sprite.action_anim()
	var sf := sprite.sprite_frames
	var t := 0.0
	for i in range(a, mini(b, sf.get_frame_count(anim))):
		t += sf.get_frame_duration(anim, i)
	return t / maxf(sf.get_animation_speed(anim) * absf(sprite.speed_scale), 0.001)


func _framed(anim: String) -> bool:
	return sprite.sprite_frames.has_animation(anim + "_s")


func _begin(anim: String) -> bool:
	if current == "strike" and _recovering:
		_recovering = false  # an ability cancels the strike's backswing
		var b := _body()
		if b != null and b.action != "":
			b.stop_action()  # the swat gives way on the body too
	elif current != "":
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


func _wait_frame(anim: String, f: int) -> void:
	while sprite.action == anim and sprite.frame < f and sprite.is_playing():
		await get_tree().process_frame


func _wait_end(anim: String) -> void:
	while sprite.action == anim and sprite.is_playing():
		await get_tree().process_frame
