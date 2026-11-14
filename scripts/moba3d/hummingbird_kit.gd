class_name HummingbirdKit
extends Node
## The hummingbird's kit in the 3D field slice (hummingbird mech session, 2026-11-05; Preston: "Do the link slice").
## The design is his: bonds and hover, docs/plan/moba-kits.md. This slice builds the passive and slot 1 only:
##   Passive, kindred link: the last ally it healed stays linked by a ruby beam from its throat plate and heals a
##     share of its full health each second. The link breaks past link_range or when a wall cuts the line; healing
##     another ally moves it.
##   1 link needle: a needle from the beak along its facing (the player turns to the mouse aim first). The first ally
##     or enemy on the line within needle_range takes it, and a wall stops it. Ally: healed by needle_heal_share of
##     its full health, and linked. Enemy: one kit hit times needle_damage_scale.
##   Basic attack, beak shot (Preston, 2026-11-05: "Yes, ranged beak shot"): a short steel dart from the beak at the
##     nearest enemy within basic_range of the mouse aim (or a bot's target), enemies only, never allies. No target
##     in reach means no shot and no cooldown, like the director's stand-in. No camera shake and no held contact
##     frame: it is a light ranged shot, and the target's hit flash is the feedback.
## Not built yet: 2 surge line, 3 flutter, 4 kindred ring.
## Body: Preston took hover. Until its 35-degree hover stills exist, install() shows the approved low-angle standing
## stills (take-a/views), lifted HOVER_ROWS texels off the ground. They are not drawn from the game camera, so they
## do not tilt. Every number is a placeholder share, not balance: on the match's 600-health machines the needle heals
## 60, the link heals 6 a second and the needle hits for 36 (MatchRules.kit_hit_damage 60 x 0.6).
## class_name HummingbirdKit since 2026-11-06: the sound lane's kit_audio.gd finds a kit's cues by
## script.get_global_name(). The match and the checks still load this file by path, which keeps working either way.

signal impact(strength: float) ## kept for the director's camera shake hookup; the needle is light and never shakes
signal used(slot: String)
signal cue(name: String) ## named moments for the sound lane: needle_cast, needle_heal, needle_hit, needle_miss, link_on, link_break, beak_shot, beak_hit, beak_miss
signal needled(target: Node3D, ally: bool) ## the needle arrived: target is null when it hit nothing (or a wall)
signal beak_landed(target: Node3D) ## a beak shot arrived on target (null when its target was gone by then)
signal linked(ally: Node3D) ## the link moved to this ally
signal unlinked(ally: Node3D, why: String) ## "range", "wall", "gone" or "replaced"

const SELF_PATH := "res://scripts/moba3d/hummingbird_kit.gd"
const VIEWS_DIR := "res://docs/art/moba/hummingbird_s/take-a/views" ## the approved stills (Preston, 2026-11-03)
const CANVAS := 160
const FEET_EDGE := 141 ## one below the foot row: 160 canvas, feet on row 140 (directional_sprite_3d.gd)
const HOVER_ROWS := 12 ## texels of air under the stand-in still's feet (the drone hovers 9)
const THROAT_ROW := 92 ## the ruby throat plate's row in the front still, where the link beam starts
const ALLY_CHEST := 0.8 ## metres up an ally where the beam ends
const RUBY := Color(1.0, 0.25, 0.42) ## the throat plate's ruby, for the link
const GLINT := Color(0.85, 1.0, 1.0) ## the lens glint, for the needle

@export_group("Placeholder numbers, not balance")
@export var needle_range := 10.0
@export var needle_speed := 20.0 ## metres per second
@export var needle_width := 0.5 ## metres either side of the line, past a unit's own radius, that still counts as hit
@export var needle_heal_share := 0.10 ## of the ally's full health
@export var needle_damage_scale := 0.6 ## of MatchRules.kit_hit_damage
@export var link_range := 9.0
@export var link_heal_share := 0.01 ## of the linked ally's full health, each second
@export var basic_range := 6.0 ## metres edge to edge (MatchTeams.edge_distance); the director and bots read it
@export var basic_cooldown := 0.9 ## seconds; the director sets it after each shot
@export var basic_damage := 30.0 ## the stand-in's damage
@export var basic_aim_cone := 30.0 ## degrees either side of the aim an enemy may stand and still be the target
@export var basic_speed := 24.0 ## metres per second

var current := "" ## "needle" while a needle is in the air
var link_target: Node3D = null
var _beam: MeshInstance3D

@onready var player = get_parent() ## machine_test_player.gd
@onready var sprite: DirectionalSprite3D = get_parent().get_node("Sprite")


## Turns a field Player into the hummingbird: frames from the approved stills, this kit in place of any other.
static func install(p: Node3D) -> Node:
	var spr: DirectionalSprite3D = p.get_node("Sprite")
	spr.stop_action()
	spr.sprite_frames = frames()
	spr.canvas_height = CANVAS
	spr.feet_edge_row = FEET_EDGE + HOVER_ROWS
	spr.size_class = "S"  # sets the texel size and raises the sprite by feet_edge_row
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
## at the old low angle. The hummingbird never walks, so walk_ stays the still for good.
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


func _ready() -> void:
	_beam = MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(0.05, 0.05, 1.0)
	_beam.mesh = box
	_beam.material_override = _glow(RUBY)
	_beam.visible = false
	add_child(_beam)
	_beam.top_level = true  # placed in world space each frame


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if player.get("bot") or (player.has_method("slot_ready") and not player.slot_ready(str(k.physical_keycode - KEY_0))):
		return  # a bot's kit ignores the keyboard; in a match a slot waits out its cooldown (MatchRules)
	if k.physical_keycode == KEY_1:
		needle()


func world() -> Node:
	return player.get_parent()


func targets() -> Array:
	return MatchTeams.enemies_of(player)


func allies() -> Array:
	return MatchTeams.allies_of(player).filter(func(a: Node) -> bool: return a != player)


func feet() -> Vector3:
	return player.global_position


func ahead() -> Vector3:
	var f: Vector3 = player.facing
	return Vector3(f.x, 0.0, f.z).normalized()


func throat() -> Vector3:
	return feet() + Vector3.UP * ((sprite.feet_edge_row - THROAT_ROW) * sprite.pixel_size)


# ---- 1, link needle ----------------------------------------------------------------------------------------------

func needle() -> void:
	if current != "":
		return
	current = "needle"
	used.emit("1")  # in a match the director starts the cooldown on this
	cue.emit("needle_cast")
	var start := feet()
	var dir := ahead()
	var reach := needle_range
	var wall := ArenaMotion.ray(player, Vector3(start.x, 1.0, start.z), Vector3(start.x, 1.0, start.z) + dir * needle_range)
	if not wall.is_empty():
		reach = flat((wall["position"] as Vector3) - start).length()
	var pick := _first_on_line(start, dir, reach)
	var target: Node3D = pick[0]
	var dist: float = pick[1] if target != null else reach
	await _fly(throat(), throat() + dir * dist)
	current = ""
	if target == null or not is_instance_valid(target) or target.get("alive") == false:
		cue.emit("needle_miss")
		needled.emit(null, false)
	elif pick[2]:
		heal(target, float(target.get("max_hp")) * needle_heal_share)
		cue.emit("needle_heal")
		_link(target)
		needled.emit(target, true)
	else:
		target.hit(player, needle_damage_scale)
		cue.emit("needle_hit")
		needled.emit(target, false)


## [unit, distance along the line, is_ally] for the nearest ally or enemy whose middle is within needle_width (plus
## its radius) of the line and no farther along it than reach; [null, 0, false] when there is none.
func _first_on_line(start: Vector3, dir: Vector3, reach: float) -> Array:
	var best: Array = [null, INF, false]
	var units := []
	for a in allies():
		units.append([a, true])
	for e in targets():
		if MatchTeams.hittable(e) or MatchTeams.team_of(player) == "":
			units.append([e, false])
	for pair in units:
		var u: Node3D = pair[0]
		if not is_instance_valid(u):
			continue
		var rel := flat(u.global_position - start)
		var along := rel.dot(dir)
		var r: float = u.radius() if u.has_method("radius") else TrainingDummy.BODY_R
		if along < 0.0 or along > reach + r:
			continue
		if (rel - dir * along).length() > needle_width + r:
			continue
		if along < best[1]:
			best = [u, along, pair[1]]
	if best[0] == null:
		return [null, 0.0, false]
	return best


func _fly(from: Vector3, to: Vector3, speed := needle_speed, length := 0.45) -> void:
	var n := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(0.04, 0.04, length)
	n.mesh = box
	n.material_override = _glow(GLINT)
	world().add_child(n)
	n.global_position = from
	if from.distance_to(to) > 0.01:
		n.look_at(to, Vector3.UP)
	var t := maxf(from.distance_to(to) / speed, 0.03)
	var tw := n.create_tween()
	tw.tween_property(n, "global_position", to, t)
	await tw.finished
	n.queue_free()


# ---- basic attack, beak shot ---------------------------------------------------------------------------------------

## The director's hook: target is null for the player (aim at the mouse) or a bot's pick. True only if it fired.
func basic_attack(target: Node3D) -> bool:
	var t := target
	if t == null:
		var aim: Vector3 = player.aim_dir() if player.has_method("aim_dir") else Vector3.ZERO
		t = _basic_target(aim if aim != Vector3.ZERO else ahead())
	elif not is_instance_valid(t) or _edge(t) > basic_range + 0.3:
		return false
	if t == null:
		return false
	var to := flat(t.global_position - feet())
	if to.length() > 0.01:
		player.facing = to.normalized()
	cue.emit("beak_shot")
	_beak_shot(t)
	return true


## The nearest enemy within basic_range (edge to edge) and basic_aim_cone of aim, weighting the angle the way the
## director's target pick does; null when there is none.
func _basic_target(aim: Vector3) -> Node3D:
	var best: Node3D = null
	var best_score := INF
	for e in targets():
		if not is_instance_valid(e) or not (MatchTeams.hittable(e) or MatchTeams.team_of(player) == ""):
			continue
		var d := _edge(e)
		if d > basic_range:
			continue
		var to := flat(e.global_position - feet())
		var angle := rad_to_deg(aim.angle_to(to.normalized())) if to.length() > 0.01 else 0.0
		if angle > basic_aim_cone:
			continue
		var score := d + angle / 90.0 * 2.0
		if score < best_score:
			best = e
			best_score = score
	return best


## Middle to edge on the ground (MatchTeams.edge_distance); a training dummy, which has no radius(), counts BODY_R.
func _edge(e: Node3D) -> float:
	if e.has_method("radius"):
		return MatchTeams.edge_distance(player, e)
	return flat(e.global_position - feet()).length() - TrainingDummy.BODY_R


func _beak_shot(t: Node3D) -> void:
	await _fly(throat(), t.global_position + Vector3.UP * ALLY_CHEST, basic_speed, 0.25)
	if not is_instance_valid(t) or t.get("alive") == false:
		cue.emit("beak_miss")
		beak_landed.emit(null)
		return
	t.hit(player, basic_damage / MatchRules.kit_hit_damage)
	cue.emit("beak_hit")
	beak_landed.emit(t)


# ---- passive, kindred link ---------------------------------------------------------------------------------------

## Heals u by amount through its own heal(amount, by) (machine_test_player.gd has one since 2026-11-05, game feel
## lane: capped at full health, 0 for a dead or full machine, emits healed). Returns what actually landed; a unit
## without heal() takes nothing.
func heal(u: Node, amount: float) -> float:
	if u == null or not is_instance_valid(u) or not u.has_method("heal"):
		return 0.0
	return float(u.heal(amount, player))


func _link(ally: Node3D) -> void:
	if ally == link_target:
		return
	if link_target != null:
		_unlink("replaced")
	link_target = ally
	cue.emit("link_on")
	linked.emit(ally)


func _unlink(why: String) -> void:
	var was := link_target
	link_target = null
	_beam.visible = false
	cue.emit("link_break")
	unlinked.emit(was, why)


func _physics_process(delta: float) -> void:
	if link_target == null:
		return
	if not is_instance_valid(link_target) or link_target.get("alive") == false:
		_unlink("gone")
		return
	if flat(link_target.global_position - feet()).length() > link_range:
		_unlink("range")
		return
	if not MatchTeams.clear_line(player, feet(), link_target.global_position):
		_unlink("wall")
		return
	if player.get("alive") == false:
		_unlink("gone")
		return
	heal(link_target, float(link_target.get("max_hp")) * link_heal_share * delta)


func _process(_delta: float) -> void:
	if link_target == null or not is_instance_valid(link_target):
		_beam.visible = false
		return
	var a := throat()
	var b := link_target.global_position + Vector3.UP * ALLY_CHEST
	var length := a.distance_to(b)
	_beam.visible = length > 0.05
	if not _beam.visible:
		return
	_beam.global_position = (a + b) * 0.5
	_beam.look_at(b, Vector3.UP if absf((b - a).normalized().y) < 0.99 else Vector3.RIGHT)
	_beam.scale = Vector3(1.0, 1.0, length)


func _glow(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = c
	m.emission_enabled = true
	m.emission = c
	return m
