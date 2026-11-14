class_name LobsterKit
extends Node
## Lobster kit (Claude, lobster session, 2026-11-06). Its frames are the 35-degree stills Preston accepted
## ("Accept them", 2026-11-06), packed by tools/art/pack_lobster_3d.py. No abilities yet (the design is the Lobster
## section of docs/plan/moba-kits.md). It glides when it moves: its walk is the still until one is drawn
## (docs/art/moba/lobster_l/MECH_STATUS.md).
## Basic attack (Preston, "Melee claw snap", 2026-11-06, on the proposed numbers): a short snap of the big claw, 2 m
## edge to edge, 40 damage, every 1.1 s. No passive rides on it (the molt passive is health-triggered). It lunges on the
## still until the attack lane draws a 35-degree snap. Patterns: KangarooKit's jab and RhinoKit's reach assist.
## No `current`: MatchBot skips a kit without one.
## Loaded by path, not by class_name, inside this file and its checks: a new class_name is unknown until the editor or
## an import refreshes the class cache (the hippo kit's note).

const LOBSTER_FRAMES := preload("res://art/machines/lobster/lobster_frames.tres")
const CANVAS := 192
const FEET_EDGE_ROW := 161 ## the feet stand on row 160
const SIZE_CLASS := "L" ## the HUD's tilted bar for L stands at 2.3 m, which the lobster needs (game feel turn test)
const REACH_SLACK := 0.3 ## a bot's target may drift this far past basic_range between its check and the hit

signal impact(strength: float)
signal cue(name: String) ## for the sound lane: basic_snap, basic_whiff

@export var basic_range := 2.0 ## metres edge to edge (MatchTeams.edge_distance); proposal, Preston's to change
@export var basic_cooldown := 1.1 ## seconds; proposal
@export var snap_damage := 40.0 ## proposal (the stand-in shot does 30 every 0.9 s at 6 m)
@export var half_angle := 60.0 ## degrees either side of the aim the snap prefers; anything else in reach is the assist
@export var windup := 0.1 ## the claw draws back (a heavy claw, a little slower than the kangaroo's 0.08 jab)
@export var hold := 0.05 ## the contact holds (game feel lane: about 0.05)
@export var lunge := 0.25 ## metres the still moves toward the target

var player: Node3D
var swinging := false


## Turns a field Player into the lobster: the lobster frames at size L, and this kit in place of whatever kit it had.
static func install(p: Node3D) -> Node:
	var spr: DirectionalSprite3D = p.get_node("Sprite")
	spr.stop_action()
	spr.sprite_frames = LOBSTER_FRAMES
	spr.canvas_height = CANVAS
	spr.feet_edge_row = FEET_EDGE_ROW
	spr.size_class = SIZE_CLASS
	spr.play(StringName("idle_" + spr.view))
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var kit: Node = load("res://scripts/moba3d/lobster_kit.gd").new()
	kit.name = "Kit"
	kit.set("player", p)
	p.add_child(kit)
	if p.has_method("apply_size_class"):
		p.apply_size_class()
	return kit


static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


## The director calls it (target null for the player, aimed with the mouse; a bot passes its target). True if it fired.
func basic_attack(target: Node3D) -> bool:
	if swinging or not is_instance_valid(player):
		return false
	if target != null and MatchTeams.edge_distance(player, target) > basic_range + REACH_SLACK:
		return false
	var d := flat(target.global_position - player.global_position) if target != null else Vector3.ZERO
	if d.length() < 0.01 and target == null and player.has_method("aim_dir"):
		d = player.aim_dir()
	if d.length() < 0.01:
		d = flat(player.facing)
	d = d.normalized()
	var victim := target if target != null else _pick(d)
	if victim != null:
		var to := flat(victim.global_position - player.global_position)
		if to.length() > 0.01:
			d = to.normalized()
	_snap(victim, d)
	return true


## The enemy in reach nearest the aim's cone; with none in the cone, the nearest in reach (the rhino's assist), so the
## key lands when the mouse points a little off.
func _pick(dir: Vector3) -> Node3D:
	var best: Node3D = null
	var best_d := INF
	var any: Node3D = null
	var any_d := INF
	for e in MatchTeams.enemies_of(player):
		if not (e is Node3D) or not MatchTeams.hittable(e):
			continue
		var reach := MatchTeams.edge_distance(player, e)
		if reach > basic_range:
			continue
		if reach < any_d:
			any_d = reach
			any = e
		var to := flat(e.global_position - player.global_position)
		if (to.length() <= 0.3 or to.normalized().dot(dir) >= cos(deg_to_rad(half_angle))) and reach < best_d:
			best_d = reach
			best = e
	return best if best != null else any


func _snap(victim: Node3D, dir: Vector3) -> void:
	swinging = true
	player.busy = true
	player.facing = dir
	var spr: Node3D = player.get_node("Sprite")
	var home := spr.position
	create_tween().tween_property(spr, "position", home + dir * lunge, windup)  # a lunge on the still (no snap frames yet)
	await get_tree().create_timer(windup).timeout
	if not is_instance_valid(player):
		return
	if victim != null and is_instance_valid(victim) and MatchTeams.hittable(victim) \
			and MatchTeams.edge_distance(player, victim) <= basic_range + REACH_SLACK:
		victim.hit(player, snap_damage / MatchRules.kit_hit_damage)
		cue.emit("basic_snap")
		impact.emit(0.2)
		await get_tree().create_timer(hold).timeout
	else:
		cue.emit("basic_whiff")
	if is_instance_valid(spr):
		create_tween().tween_property(spr, "position", home, 0.1)
	swinging = false
	if is_instance_valid(player):
		player.busy = false
