class_name WolfKit
extends Node
## The wolf's kit in the 3D slice (Claude, wolf mech session, 2026-11-05). What each ability does is Preston's design
## in docs/plan/moba-kits.md (Wolf, ode to Thanatos). First slice (Preston: "Lunge in the match"): slot 1 only.
##   1 lunge: leaps at the enemy nearest the aim (within lunge_range and aim_cone) and bites. If the target is wounded
##     (at or under half health in a match), part of the cooldown comes back. With no enemy there it leaps straight
##     along the aim and bites the first enemy it meets on the way, or the air.
##   Basic, bite (Preston: "Yes, melee bite", 2026-11-05): Space or left click bites the nearest enemy within reach in
##     front of the aim; a bot passes its target. Follows the hippo's bite (hippo_kit.gd): it always fires for the
##     player, hit or whiff, and fires for a bot only when its target is in reach.
##   Passive scent, 2 hamstring, 3 howl and 4 run down are not built yet.
## The aim: on keys 1-5 machine_test_player turns player.facing to the mouse point before this kit reads it (game feel
## lane, 2026-11-05). Feel: impacts shake the camera through KitFeel for the player's own machine, and the bite holds
## a short hitstop before the target reacts, as the rhino's horn toss does. Sound: cue(name) for the sound lane.
## The wolf has no installed frames yet (its pack is on hold), so install() builds idle and walk from the accepted
## 35-degree stills (wolf_m/take-b/views_cam35_touchup), one still per view, the way CamAngleTest.frames_of does. There are no
## lunge frames: the leap is a hop of the idle pose (as the gorilla's bound ran before its frames existed). Every length
## below is a presentation placeholder so the lunge can be seen, not a balance number.

signal impact(strength: float) ## something landed hard; cameras can shake on it
signal used(slot: String)
signal cue(name: String) ## named moments for the sound lane: lunge_cast, lunge_bite, lunge_miss, basic_bite,
## basic_whiff
signal bit(target: Node3D, wounded: bool) ## the bite landed on target (null when it bit the air)

const VIEWS_DIR := "res://docs/art/moba/wolf_m/take-b/views_cam35_touchup" ## the kept 35-degree stills (Preston,
## "Keep it", 2026-11-05): views_cam35 recoloured, same alpha; 192 canvas, feet row 160. idle35 is built from these.

@export_group("Placeholder lengths, not balance")
@export var lunge_range := 6.0 ## metres to the farthest enemy it will leap at
@export var aim_cone := 40.0 ## degrees either side of the aim an enemy may stand and still be the target
@export var lunge_distance := 3.5 ## along the aim when no enemy is there
@export var stop_short := 0.9 ## lands this far from the target's centre, so the bite reaches without overlapping
@export var crouch_time := 0.12 ## the wind-up: it sinks and draws back before the leap
@export var crouch_back := 0.15 ## metres it draws back during the wind-up
@export var air_time := 0.28
@export var hop_height := 0.45
@export var hitstop := 0.07 ## the bite holds this long before the target reacts (game feel lane: 0.06 to 0.08)
@export var recover_time := 0.22 ## after the bite, before it can walk again
@export var wounded_share := 0.5 ## a match target at or under this share of its health counts as wounded
@export var refund_share := 0.5 ## the share of the lunge cooldown that comes back on a wounded target
@export_group("Basic bite, placeholders")
@export var basic_range := 1.8 ## metres edge to edge (MatchTeams.edge_distance); the director reads it
@export var basic_cooldown := 0.8 ## seconds; the director reads it and keeps the cooldown
@export var bite_damage := 40.0 ## the stand-in shot did 30 at 6 m every 0.9 s; a bite has to get close
@export var bite_half_angle := 50.0 ## degrees either side of the aim a bite can reach
@export var bite_windup := 0.08 ## the snap before the jaws close
@export var bite_hitstop := 0.05 ## the contact holds this long (game feel lane: about 0.05)
@export var bite_shake := 0.2 ## a small impact for KitFeel (0.15 to 0.25)

var current := "" ## the ability in progress, or ""
var biting := false ## a basic bite is under way

const REACH_SLACK := 0.3 ## a bot's target may drift this far past basic_range between its check and the bite

@onready var player = get_parent() ## machine_test_player.gd
@onready var sprite: DirectionalSprite3D = get_parent().get_node("Sprite")


## Turns a field Player into the wolf: frames built from the 35-degree stills, and this kit in place of any other.
static func install(p: Node3D) -> WolfKit:
	var spr: DirectionalSprite3D = p.get_node("Sprite")
	spr.stop_action()
	spr.sprite_frames = frames()
	spr.canvas_height = 192
	spr.feet_edge_row = 161
	spr.size_class = "M"  # sets the texel size and re-raises the sprite for the canvas above
	spr.play(StringName("idle_" + spr.view))
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var kit := WolfKit.new()
	kit.name = "Kit"
	p.add_child(kit)
	return kit


## idle_<view> and walk_<view> for the five drawn views, each the accepted still. Both are drawn from the camera's
## angle, so both tilt. A real walk replaces walk_ when the walk lane packs one.
static func frames() -> SpriteFrames:
	var sf := SpriteFrames.new()
	if sf.has_animation(&"default"):
		sf.remove_animation(&"default")
	for v in DirectionalSprite3D.VIEWS:
		var img := Image.load_from_file(ProjectSettings.globalize_path(VIEWS_DIR.path_join(v + ".png")))
		var tex := ImageTexture.create_from_image(img)
		for kind in ["idle_", "walk_"]:
			var a := StringName(kind + v)
			sf.add_animation(a)
			sf.set_animation_loop(a, true)
			sf.add_frame(a, tex)
	sf.set_meta("tilt_anims", ["idle", "walk"])
	return sf


static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


func _ready() -> void:
	impact.connect(_shake)


## The wolf is never left busy by a lunge or bite cut short (a Tab to another machine).
func _exit_tree() -> void:
	if is_instance_valid(player) and (biting or current != ""):
		player.busy = false
	biting = false
	current = ""


func _shake(strength: float) -> void:
	if not player.get("bot"):
		KitFeel.shake(self, strength)


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if player.get("bot") or (player.has_method("slot_ready") and not player.slot_ready(str(k.physical_keycode - KEY_0))):
		return  # a bot's kit ignores the keyboard; in a match a slot waits out its cooldown (MatchRules)
	if k.physical_keycode == KEY_1:
		lunge()


func world() -> Node:
	return player.get_parent()


func targets() -> Array:
	return MatchTeams.enemies_of(player)


func feet() -> Vector3:
	return player.global_position


func ahead() -> Vector3:
	var f: Vector3 = player.facing
	return Vector3(f.x, 0.0, f.z).normalized()


## A match target at or under wounded_share of its health. Training dummies have no health, so they never count.
func is_wounded(t: Node) -> bool:
	if t == null or not ("hp" in t) or not ("max_hp" in t) or float(t.max_hp) <= 0.0:
		return false
	return float(t.hp) / float(t.max_hp) <= wounded_share


func lunge() -> void:
	if current != "":
		return
	current = "lunge"
	player.busy = true
	used.emit("1")  # in a match the director starts the cooldown on this
	cue.emit("lunge_cast")
	var start: Vector3 = feet()
	var dir := ahead()
	var target := _aimed_target(dir)
	var land: Vector3 = start + dir * lunge_distance
	if target != null:
		var d := flat(target.global_position - start)
		if d.length() > 0.05:
			dir = d.normalized()
			player.facing = dir
		land = start + dir * maxf(d.length() - stop_short, 0.0)
	var base_y := sprite.position.y
	# Wind-up: sink and draw back a little.
	var t := 0.0
	while t < crouch_time:
		await get_tree().process_frame
		t += get_process_delta_time()
		var k := minf(t / crouch_time, 1.0)
		sprite.position.y = base_y - 0.08 * k
		var back: Vector3 = start - dir * crouch_back * k
		player.global_position = ArenaMotion.slide(player, player.global_position, back - player.global_position,
			player.body_radius())
	var from: Vector3 = player.global_position
	Fx3D.spawn(world(), "impact_puff", from, 0.6)
	# The leap: an arc from the drawn-back spot to the landing. With no aimed target, the first enemy that comes
	# within reach on the way is bitten and the leap stops there.
	t = 0.0
	while t < air_time:
		await get_tree().process_frame
		t += get_process_delta_time()
		var k := minf(t / air_time, 1.0)
		var to: Vector3 = from.lerp(land, k)
		player.global_position = ArenaMotion.slide(player, player.global_position, to - player.global_position,
			player.body_radius())
		sprite.position.y = base_y + hop_height * 4.0 * k * (1.0 - k)
		if target == null:
			target = _met(dir)
			if target != null:
				break
	sprite.position.y = base_y
	await _bite(target, dir)
	var r := 0.0
	while r < recover_time:
		await get_tree().process_frame
		r += get_process_delta_time()
	current = ""
	player.busy = false


## The bite at the end of the leap: the target is hit if it is still within reach of the jaws. The contact holds for
## the hitstop before the target reacts.
func _bite(target: Node3D, dir: Vector3) -> void:
	var reached := target != null and is_instance_valid(target) \
		and flat(target.global_position - feet()).length() <= stop_short + 0.6
	if not reached:
		Fx3D.spawn(world(), "dust_trail", feet() + dir * 0.6, 0.5)
		cue.emit("lunge_miss")
		impact.emit(0.1)
		bit.emit(null, false)
		return
	var jaws: Vector3 = feet() + dir * 0.7 + Vector3.UP * 0.6
	var wounded := is_wounded(target)
	cue.emit("lunge_bite")
	Fx3D.spawn(world(), "hit_spark", jaws, 0.3)
	impact.emit(0.6 if wounded else 0.5)
	await get_tree().create_timer(hitstop).timeout
	if not is_instance_valid(target):
		bit.emit(null, false)
		return
	if target.has_method("hit"):
		target.hit(player)
	if wounded:
		Fx3D.spawn(world(), "deflect_spark", jaws + Vector3.UP * 0.15, 0.3)
		if "cooldowns" in player and player.cooldowns.has("1"):
			player.cooldowns["1"] = float(player.cooldowns["1"]) * (1.0 - refund_share)
	bit.emit(target, wounded)


## The enemy nearest the wolf within lunge_range and aim_cone of the aim, or null.
func _aimed_target(aim: Vector3) -> Node3D:
	var best: Node3D = null
	var best_d := lunge_range
	var cos_cone := cos(deg_to_rad(aim_cone))
	for e in targets():
		if not (e is Node3D) or not is_instance_valid(e):
			continue
		var d := flat(e.global_position - feet())
		if d.length() <= best_d and (d.length() < 0.05 or d.normalized().dot(aim) >= cos_cone):
			best = e
			best_d = d.length()
	return best


## An enemy within bite reach ahead of the wolf mid-leap, or null.
func _met(dir: Vector3) -> Node3D:
	for e in targets():
		if not (e is Node3D) or not is_instance_valid(e):
			continue
		var d := flat(e.global_position - feet())
		if d.length() <= stop_short + 0.3 and (d.length() < 0.05 or d.normalized().dot(dir) > 0.5):
			return e
	return null


# ---- basic, bite ---------------------------------------------------------------------------------------------------

## Called by the director (Space or left click with target null, aimed with the mouse; a bot passes its target).
## True when the bite fired, hit or whiff; false when a bot's target is out of reach or the wolf is mid-move.
func basic_attack(target: Node3D) -> bool:
	if biting or current != "" or not is_instance_valid(player):
		return false
	var dir := _bite_aim(target)
	var victim: Node3D = target
	if victim != null:
		if MatchTeams.edge_distance(player, victim) > basic_range + REACH_SLACK:
			return false
	else:
		victim = _bite_pick(dir)
	_basic_bite(victim, dir)
	return true


func _bite_aim(target: Node3D) -> Vector3:
	var d := Vector3.ZERO
	if target != null:
		d = flat(target.global_position - player.global_position)
	elif player.has_method("aim_dir"):
		d = player.aim_dir()
	if d.length() < 0.01:
		d = flat(player.facing)
	return d.normalized()


## The nearest hittable enemy within reach and inside the bite's arc.
func _bite_pick(dir: Vector3) -> Node3D:
	var best: Node3D = null
	var best_d := INF
	var min_dot := cos(deg_to_rad(bite_half_angle))
	for e in targets():
		if not (e is Node3D) or not MatchTeams.hittable(e):
			continue
		var reach := MatchTeams.edge_distance(player, e)
		if reach > basic_range:
			continue
		var to := flat(e.global_position - player.global_position)
		if to.length() > 0.3 and to.normalized().dot(dir) < min_dot:
			continue
		if reach < best_d:
			best_d = reach
			best = e
	return best


func _basic_bite(victim: Node3D, dir: Vector3) -> void:
	biting = true
	player.busy = true
	player.facing = dir
	await get_tree().create_timer(bite_windup).timeout
	if not is_instance_valid(player):
		return
	if victim != null and is_instance_valid(victim) and MatchTeams.hittable(victim) 			and MatchTeams.edge_distance(player, victim) <= basic_range + REACH_SLACK:
		var r: float = victim.radius() if victim.has_method("radius") else 0.0
		var at: Vector3 = victim.global_position - dir * r + Vector3.UP * 0.6
		victim.hit(player, bite_damage / MatchRules.kit_hit_damage)
		Fx3D.spawn(world(), "hit_spark", at, 0.0)
		cue.emit("basic_bite")
		impact.emit(bite_shake)
		await get_tree().create_timer(bite_hitstop).timeout  # the contact holds (the wolf has no bite frames to pause)
	else:
		Fx3D.spawn(world(), "impact_puff", player.global_position + dir * 0.8 + Vector3.UP * 0.4, 0.0)
		cue.emit("basic_whiff")
	biting = false
	if is_instance_valid(player):
		player.busy = false
