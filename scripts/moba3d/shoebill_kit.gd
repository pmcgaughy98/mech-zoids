class_name ShoebillKit
extends Node
## The shoebill's kit in the 3D slice (Claude, 2026-11-05, Shoebill session). Preston picked the moon kit ("Version B,
## moon") and said "Yes, build it" for this slice. Design: docs/plan/moba-kits.md (Shoebill, ode to Thoth); numbers
## from docs/plan/shoebill-kit-2026-11-05.md. Every number here is a proposal: Preston sets them.
##   Passive, moon phases (patience): after standing still for start_delay, a charge every charge_every, up to
##     max_charges. Each charge adds damage_per_charge to the damage and range_per_charge metres to the reach of the
##     next slot 1 or 2. Walking keeps them for keep_walking seconds of walking, then they are gone. A cast spends all.
##   1 moonbeam: a warning line on the ground for warn_time, then a beam of light from the eye lens hits every enemy
##     in the line (it passes through). An arena wall cuts it short.
##   Basic attack, lens flick: a short flick of light that hits the first enemy in its line. The director keeps its
##     cooldown and gates (the game feel lane's basic_attack hook, 2026-11-05).
##   2 moon pool, 3 wane, 4 moonlance: not built yet.
## Body: a stand-in. The shoebill has no 35-degree frames yet, so install() keeps the machine's frames.
## Effects: placeholders drawn in code (a moon disc over the body, a line on the ground, a beam) until the VFX pass.
## Other scripts reach this file by preload, not by class_name, until the editor refreshes the class cache.

signal impact(strength: float) ## something landed hard; cameras can shake on it
signal used(slot: String)
signal cue(name: String) ## named moments for the sound lane: moon_phase, moonbeam_warn, moonbeam_fire, lens_flick

# passive, moon phases
@export var start_delay := 1.0 ## seconds standing still before charging starts
@export var charge_every := 1.0
@export var max_charges := 3
@export var damage_per_charge := 0.15 ## +15% damage a charge
@export var range_per_charge := 1.0 ## metres a charge
@export var keep_walking := 3.0 ## seconds of walking the charges survive
@export var still_speed := 0.05 ## metres a second: slower than this is standing still
@export var disc_up := 2.1 ## metres above the feet the moon disc floats

# 1, moonbeam
@export var beam_range := 10.0 ## metres, middle to the target's edge
@export var beam_damage := 60.0
@export var beam_width := 1.0
@export var warn_time := 0.3
@export var beam_show := 0.25 ## seconds the beam stays on screen
@export var lens_up := 0.9 ## metres off the floor the beam leaves at

# basic attack, lens flick (the director reads basic_cooldown and basic_range)
var basic_cooldown := 1.0
var basic_range := 7.0 ## metres, middle to the target's edge
@export var basic_damage := 28.0
@export var flick_width := 0.5

const MOON := Color("e6eef8")
const MOON_DARK := Color(0.16, 0.18, 0.25, 0.8)
const MOON_RIM := Color("82a6d7")

var charges := 0
var current := "" ## the ability under way, "" when free
var last := {} ## what the last cast did, for the checks
var _still := 0.0
var _clock := 0.0
var _walked := 0.0
var _disc: Sprite3D
static var _phase_tex := {}

@onready var player = get_parent() ## machine_test_player.gd


const SELF_PATH := "res://scripts/moba3d/shoebill_kit.gd"


## Puts this kit on a field Player in place of whatever kit it had. The frames stay (a stand-in body). Made from its
## path, not its class_name, because a new class_name is unknown until the editor refreshes the class cache.
static func install(p: Node3D) -> Node:
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var kit: Node = load(SELF_PATH).new()
	kit.name = "Kit"
	p.add_child(kit)
	return kit


func _ready() -> void:
	if not (player is Node3D):
		return
	_disc = Sprite3D.new()
	_disc.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_disc.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	_disc.pixel_size = 0.02
	_disc.shaded = false
	_disc.no_depth_test = true
	_disc.position = Vector3(0.0, disc_up, 0.0)
	_disc.visible = false
	player.add_child.call_deferred(_disc)


func _exit_tree() -> void:
	if is_instance_valid(_disc):
		_disc.queue_free()
	if current != "" and is_instance_valid(player):
		player.busy = false


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo or player.get("bot") == true:
		return
	if player.has_method("slot_ready") and not player.slot_ready(str(k.physical_keycode - KEY_0)):
		return
	match k.physical_keycode:
		KEY_1:
			moonbeam()


func world() -> Node:
	return player.get_parent()


func targets() -> Array:
	return MatchTeams.enemies_of(player)


func feet() -> Vector3:
	return player.global_position


func _process(delta: float) -> void:
	if not (player is Node3D):
		return
	_patience(delta)
	if is_instance_valid(_disc):
		_disc.visible = charges > 0
		if charges > 0:
			_disc.texture = _phase(charges)


# ---- passive, moon phases ------------------------------------------------------------------------------------------

func _patience(delta: float) -> void:
	if player.get("alive") == false:
		charges = 0
		_still = 0.0
		_clock = 0.0
		_walked = 0.0
		return
	var spd: Variant = player.get("speed")
	var moving: bool = (spd is float) and spd > still_speed
	if moving:
		_still = 0.0
		_clock = 0.0
		if charges > 0:
			_walked += delta
			if _walked >= keep_walking:
				charges = 0
				_walked = 0.0
		return
	_still += delta
	if _still < start_delay or charges >= max_charges:
		return
	_clock += delta
	if _clock >= charge_every:
		_clock -= charge_every
		charges += 1
		_walked = 0.0
		cue.emit("moon_phase")


## Spends the charges: hands back how many there were, and charging starts over.
func _spend() -> int:
	var c := charges
	charges = 0
	_still = 0.0
	_clock = 0.0
	_walked = 0.0
	return c


# ---- 1, moonbeam ---------------------------------------------------------------------------------------------------

## at: a direction, a target, or null for the aim. Returns true if it started.
func moonbeam(at: Variant = null) -> bool:
	if current != "" or not (player is Node3D):
		return false
	if player.get("stunned") is float and player.stunned > 0.0:
		return false
	var dir := _aim(at)
	var c := _spend()
	var from := feet()
	var reach := _clip(from, dir, beam_range + range_per_charge * c)
	var scale := beam_damage / MatchRules.kit_hit_damage * (1.0 + damage_per_charge * c)
	var rec := {"charges": c, "reach": reach, "scale": scale, "dir": dir, "struck": [], "fired": false}
	last["moonbeam"] = rec
	current = "moonbeam"
	player.busy = true
	player.facing = dir
	used.emit("1")
	cue.emit("moonbeam_warn")
	_ground_line(from, dir, reach, beam_width, warn_time)
	_fire_beam(from, dir, reach, scale, rec)
	return true


func _fire_beam(from: Vector3, dir: Vector3, reach: float, scale: float, rec: Dictionary) -> void:
	await get_tree().create_timer(warn_time).timeout
	if not is_instance_valid(player):
		return
	var hits := _line_hits(from, dir, reach, beam_width * 0.5)
	for e in hits:
		e.hit(player, scale)
		rec["struck"].append(e)
	rec["fired"] = true
	_beam(from, dir, reach, beam_width * 0.6, beam_show)
	cue.emit("moonbeam_fire")
	if not hits.is_empty():
		impact.emit(0.2)
	current = ""
	player.busy = false


# ---- basic attack, lens flick --------------------------------------------------------------------------------------

## The director's hook: target is null for the player (aim at the mouse), or the bot's target. True if it fired.
func basic_attack(target: Node3D) -> bool:
	if current != "" or not (player is Node3D):
		return false
	var dir := _aim(target)
	player.facing = dir
	var from := feet()
	var reach := _clip(from, dir, basic_range + 0.1)
	var hits := _line_hits(from, dir, reach, flick_width * 0.5)
	var scale := basic_damage / MatchRules.kit_hit_damage
	var end := reach
	var struck: Array = []
	if not hits.is_empty():
		hits[0].hit(player, scale)
		struck.append(hits[0])
		end = maxf(0.3, MatchTeams.flat(hits[0].global_position - from).dot(dir))
	last["basic"] = {"reach": reach, "scale": scale, "struck": struck}
	_beam(from, dir, end, flick_width * 0.5, 0.12)
	cue.emit("lens_flick")
	return true


# ---- shared --------------------------------------------------------------------------------------------------------

func _aim(at: Variant) -> Vector3:
	var d := Vector3.ZERO
	if at is Vector3:
		d = at
	elif at is Object and is_instance_valid(at) and at is Node3D:
		d = (at as Node3D).global_position - feet()
	elif player.has_method("aim_dir"):
		d = player.aim_dir()
	d.y = 0.0
	if d.length() < 0.001:
		d = player.facing
		d.y = 0.0
	return d.normalized()


## How far a line from the lens gets before an arena wall.
func _clip(from: Vector3, dir: Vector3, reach: float) -> float:
	var a := from + Vector3.UP * lens_up
	var hit := ArenaMotion.ray(player, a, a + dir * reach)
	if hit.is_empty():
		return reach
	return MatchTeams.flat(hit.position - from).length()


## Every enemy the line touches, nearest first. A target counts when its edge is inside the line.
func _line_hits(from: Vector3, dir: Vector3, reach: float, half_width: float) -> Array:
	var found: Array = []
	for e in targets():
		if not is_instance_valid(e) or e.get("alive") == false:
			continue
		if e.has_method("can_be_hit") and not e.can_be_hit():
			continue
		var r: float = e.radius() if e.has_method("radius") else 0.4
		var rel := MatchTeams.flat(e.global_position - from)
		var along := rel.dot(dir)
		if along < -r or along > reach + r:
			continue
		if (rel - dir * along).length() > half_width + r:
			continue
		found.append([along, e])
	found.sort_custom(func(x, y): return x[0] < y[0])
	return found.map(func(pair): return pair[1])


static func _phase(n: int) -> Texture2D:
	if _phase_tex.has(n):
		return _phase_tex[n]
	var size := 24
	var img := Image.create_empty(size, size, false, Image.FORMAT_RGBA8)
	var c := (size - 1) * 0.5
	var r := size * 0.5 - 1.0
	for y in size:
		for x in size:
			var d := Vector2(x - c, y - c).length()
			if d > r:
				continue
			var lit := true
			if n == 2:
				lit = x >= c
			elif n == 1:
				lit = Vector2(x - (c - r * 0.55), y - c).length() > r
			var col := MOON if lit else MOON_DARK
			if d > r - 1.2:
				col = MOON_RIM
			img.set_pixel(x, y, col)
	var tex := ImageTexture.create_from_image(img)
	_phase_tex[n] = tex
	return tex


func _ground_line(from: Vector3, dir: Vector3, length: float, width: float, life: float) -> void:
	var pm := PlaneMesh.new()
	pm.size = Vector2(width, length)
	var mat := _glow(Color(MOON.r, MOON.g, MOON.b, 0.25))
	var m := _place(pm, mat, from + dir * (length * 0.5) + Vector3.UP * 0.03, dir)
	var tw := m.create_tween()
	tw.tween_property(mat, "albedo_color:a", 0.6, life)
	tw.tween_callback(m.queue_free)


func _beam(from: Vector3, dir: Vector3, length: float, width: float, life: float) -> void:
	var bm := BoxMesh.new()
	bm.size = Vector3(width, width * 0.5, length)
	var mat := _glow(Color(MOON.r, MOON.g, MOON.b, 0.95))
	var m := _place(bm, mat, from + dir * (length * 0.5) + Vector3.UP * lens_up, dir)
	var tw := m.create_tween()
	tw.tween_property(mat, "albedo_color:a", 0.0, life)
	tw.tween_callback(m.queue_free)


func _glow(col: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.albedo_color = col
	return mat


func _place(mesh: Mesh, mat: Material, pos: Vector3, dir: Vector3) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	m.mesh = mesh
	m.material_override = mat
	m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	world().add_child(m)
	m.global_transform = Transform3D(Basis.looking_at(dir, Vector3.UP), pos)
	return m
