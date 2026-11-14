class_name FalconKit
extends Node
## The falcon's kit in the 3D field slice (falcon mech session, 2026-11-05). The design is Preston's: ranged carry,
## docs/plan/moba-kits.md. Asked for by the game feel lane ("we need basic attacks", Preston, 2026-11-05).
## This slice builds the basic attack and the passive that rides on it:
##   Basic, feather dart: a dart fired from a wing (left and right in turn). The player's shot flies along the mouse
##     aim (facing when the aim is on the machine) and hits the first enemy on the line within basic_range; a wall
##     stops it. A bot's shot goes to the target it picked.
##   Passive, keen eye: the farther the target, the harder the dart hits, up to keen_eye_max more at full range.
##     A full-range hit (keen_eye_full of the range or more) gives a small shake; nearer hits do not, so a steady
##     stream of shots never shakes the screen.
## Not built yet: 1 piercing dart, 2 take off, 3 stoop, 4 sky barrage (its effect art is in
## docs/art/moba/falcon_m/vfx/sky_barrage/, a proposal waiting on Preston).
## Body: until its 35-degree stills exist, install() shows the approved low-angle stills (take-b/views). They are not
## drawn from the game camera, so they do not tilt. No attack frames exist yet, so there is no wing-fire pose and no
## hitstop on a contact frame; the dart leaves at once.
## Every number is a placeholder, not balance. On the match's numbers (MatchRules.kit_hit_damage 60) the dart does 26
## point blank and 39 at full range; the stand-in shot it replaces did 30 at 6 m every 0.9 s.
## class_name FalconKit (2026-11-06, for the sound lane: KitAudio finds a kit's cue row by its global name). Preloading
## the file still works. After a change to the name, run --headless --import once so the class cache knows it.

signal impact(strength: float) ## for KitFeel.shake: only on a full-range keen eye hit
signal used(slot: String)
signal cue(name: String) ## for the sound lane: dart_fire, dart_hit, dart_keen (a full-range hit), dart_miss
signal darted(target: Node3D, damage: float) ## the dart arrived: target null when it hit nothing (or a wall)

const SELF_PATH := "res://scripts/moba3d/falcon_kit.gd"
const VIEWS_DIR := "res://docs/art/moba/falcon_m/take-b/views" ## the approved stills (Preston, 2026-11-03)
const CANVAS := 160
const FEET_EDGE := 141 ## one below the foot row: 160 canvas, feet on row 140
const WING_ROW := 100 ## about the middle of the folded wings in the front still, where darts leave
const WING_SPAN := 0.3 ## metres either side of the middle, left and right wing in turn
const CRIMSON := Color(0.878, 0.118, 0.235) ## e01e3c, the wing crimson
const IVORY := Color(0.925, 0.902, 0.839) ## ece6d6, the body ivory

@export_group("Placeholder numbers, not balance")
@export var basic_range := 7.0 ## metres edge to edge (MatchTeams.edge_distance); the stand-in is 6, melee 1.5 to 2.5
@export var basic_cooldown := 0.9 ## seconds, the stand-in's
@export var basic_damage := 26.0 ## point blank, before keen eye
@export var keen_eye_max := 0.5 ## extra share of basic_damage at full range
@export var keen_eye_full := 0.9 ## share of the range from which a hit counts as full range (the shake and the cue)
@export var dart_speed := 24.0 ## metres a second, as the sky barrage's darts
@export var dart_width := 0.35 ## metres either side of the line, past a unit's own radius, that still counts as hit
@export var range_slack := 0.5 ## a bot's target may have stepped this far past range since it was picked

var current := "" ## no slot ability is built yet, so the falcon is never busy; the basic never sets it
var _wing := 1.0 ## which wing fires next: 1 right, -1 left

@onready var player = get_parent() ## machine_test_player.gd
@onready var sprite: DirectionalSprite3D = get_parent().get_node("Sprite")


## Turns a field Player into the falcon: frames from the approved stills, this kit in place of any other.
static func install(p: Node3D) -> Node:
	var spr: DirectionalSprite3D = p.get_node("Sprite")
	spr.stop_action()
	spr.sprite_frames = frames()
	spr.canvas_height = CANVAS
	spr.feet_edge_row = FEET_EDGE
	spr.size_class = "M"
	spr.play(StringName("idle_" + spr.view))
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var kit: Node = load(SELF_PATH).new()
	kit.name = "Kit"
	p.add_child(kit)
	return kit


## idle_<view> and walk_<view> for the five drawn views, each the approved still. No tilt_anims meta: these were drawn
## at the old low angle. The walk is the still until the walk lane draws one.
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
	return sf


static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


func world() -> Node:
	return player.get_parent()


func feet() -> Vector3:
	return player.global_position


func targets() -> Array:
	return MatchTeams.enemies_of(player)


# ---- basic, feather dart -----------------------------------------------------------------------------------------

## The director's hook. target null: the player's shot, along the mouse aim. Otherwise a bot's pick. True if it fired.
func basic_attack(target: Node3D) -> bool:
	if target == null:
		var d: Vector3 = player.aim_dir() if player.has_method("aim_dir") else Vector3.ZERO
		if d == Vector3.ZERO:
			d = flat(player.facing)
		return fire_dir(d)
	if not is_instance_valid(target) or target.get("alive") == false:
		return false
	var dist := MatchTeams.edge_distance(player, target)
	if dist > basic_range + range_slack:
		return false
	var dir := flat(target.global_position - feet()).normalized()
	_face(dir)
	_release(target, maxf(dist, 0.0), dir)
	return true


## The player's shot along a flat direction: the first enemy on the line within basic_range, or a miss to full range
## (or to a wall). Always fires when the direction is usable.
func fire_dir(dir: Vector3) -> bool:
	dir = flat(dir).normalized()
	if dir == Vector3.ZERO:
		return false
	_face(dir)
	var start := feet()
	var reach := basic_range
	var wall := ArenaMotion.ray(player, Vector3(start.x, 1.0, start.z), Vector3(start.x, 1.0, start.z) + dir * basic_range)
	if not wall.is_empty():
		reach = flat((wall["position"] as Vector3) - start).length()
	var pick := _first_on_line(start, dir, reach)
	if pick[0] == null:
		_release(null, reach, dir)
	else:
		_release(pick[0], pick[1], dir)
	return true


## Keen eye: damage for a hit at this edge distance.
func dart_damage(edge_dist: float) -> float:
	return basic_damage * (1.0 + keen_eye_max * clampf(edge_dist / basic_range, 0.0, 1.0))


func _face(dir: Vector3) -> void:
	if "facing" in player and dir != Vector3.ZERO:
		player.facing = dir


## [unit, edge distance along the line] for the nearest hittable enemy whose middle is within dart_width (plus its
## radius) of the line and no farther along it than reach; [null, 0] when there is none.
func _first_on_line(start: Vector3, dir: Vector3, reach: float) -> Array:
	var best: Array = [null, INF]
	for e in targets():
		if not is_instance_valid(e):
			continue
		if MatchTeams.team_of(player) != "" and not MatchTeams.hittable(e):
			continue
		var rel := flat((e as Node3D).global_position - start)
		var along := rel.dot(dir)
		var r: float = e.radius() if e.has_method("radius") else TrainingDummy.BODY_R
		if along < 0.0 or along - r > reach:
			continue
		if (rel - dir * along).length() > dart_width + r:
			continue
		var edge := maxf(along - r, 0.0)
		if edge < best[1]:
			best = [e, edge]
	if best[0] == null:
		return [null, 0.0]
	return best


## Fires the dart: it flies from a wing to the target's chest (or to the end of the line on a miss), then lands.
func _release(target: Node3D, edge_dist: float, dir: Vector3) -> void:
	used.emit("basic")
	cue.emit("dart_fire")
	var side := Vector3(-dir.z, 0.0, dir.x) * (WING_SPAN * _wing)
	_wing = -_wing
	var lift := (sprite.feet_edge_row - WING_ROW) * sprite.pixel_size
	var from := feet() + side + Vector3.UP * lift
	var to: Vector3
	if target != null:
		to = target.global_position + Vector3.UP * lift
	else:
		to = feet() + dir * edge_dist + Vector3.UP * lift
	var damage := dart_damage(edge_dist)
	_land(target, damage, edge_dist, from, to)


func _land(target: Node3D, damage: float, edge_dist: float, from: Vector3, to: Vector3) -> void:
	await _fly(from, to)
	if target == null or not is_instance_valid(target) or target.get("alive") == false:
		cue.emit("dart_miss")
		darted.emit(null, 0.0)
		return
	target.hit(player, damage / MatchRules.kit_hit_damage)
	if edge_dist >= basic_range * keen_eye_full:
		cue.emit("dart_keen")
		impact.emit(0.15)
	else:
		cue.emit("dart_hit")
	darted.emit(target, damage)


## A placeholder dart: a thin crimson box with an ivory tip, flying straight. The drawn dart (the sky barrage's
## feather dart) can replace it once Preston has looked at that art.
func _fly(from: Vector3, to: Vector3) -> void:
	var n := Node3D.new()
	world().add_child(n)
	n.global_position = from
	var body := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(0.05, 0.05, 0.5)
	body.mesh = box
	body.material_override = _glow(CRIMSON)
	n.add_child(body)
	var tip := MeshInstance3D.new()
	var tb := BoxMesh.new()
	tb.size = Vector3(0.06, 0.06, 0.12)
	tip.mesh = tb
	tip.material_override = _glow(IVORY)
	tip.position = Vector3(0.0, 0.0, -0.3)  # look_at points -z at the target
	n.add_child(tip)
	if from.distance_to(to) > 0.01:
		n.look_at(to, Vector3.UP)
	var t := maxf(from.distance_to(to) / dart_speed, 0.03)
	var tw := n.create_tween()
	tw.tween_property(n, "global_position", to, t)
	await tw.finished
	n.queue_free()


static func _glow(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = c
	return m
