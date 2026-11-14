class_name SquirrelKit
extends Node
## The squirrel's kit in the 3D slice (Claude, squirrel mech session, 2026-11-05). The design is Preston's, taken on
## 2026-11-05: the squirrel section of docs/plan/moba-kits.md (ode to Ratatoskr, signal relay theme); the starting
## numbers and the reasons for them are in docs/plan/squirrel-ratatoskr-kit-2026-11-05.md.
## First slice (Preston: "Build it"): the basic attack and the passive.
##   Basic, signal dart: a fast amber dart from the tail, along the mouse aim, or at a bot's target. The match director
##     calls basic_attack(target) on Space or left click and keeps the gates and the cooldown (basic_cooldown); the
##     bots walk into basic_range before they fire.
##   Passive, Hearsay: every 4th dart carries on. When it strikes, it jumps to a second enemy within hearsay_reach of
##     the first (to that enemy's edge), machines before minions, nearest first. Three lights over the head count darts
##     1 to 3; the 4th lights all three and they go dark again.
##   Branch Skip, Crosstalk, Tail Ping and Broadcast are not built yet.
## Damage: hit(player, scale) deals MatchRules.kit_hit_damage (60) x scale, so dart 0.5 is 30 and Hearsay 0.3 is 18;
## plating and shields still apply. Sound: cue(name) for the sound lane (dart_fire, dart_hit, hearsay_jump).
## The squirrel has no 35-degree stills yet (it is last in the fleet redraw queue), so install() uses the approved
## low-angle stills (take-b/fixed), one per view, not tilted. The dart, the jump and the lights are placeholder looks.
## Every length is a starting number, not balance.

signal impact(strength: float) ## something landed hard; cameras can shake on it (no dart shakes)
signal used(slot: String)
signal cue(name: String) ## named moments for the sound lane: dart_fire, dart_hit, hearsay_jump
signal dart_hit(target: Node3D, number: int, jumped: bool) ## dart number `number` struck target; jumped: the Hearsay jump
signal hearsay(from: Node3D, to: Node3D, number: int) ## dart number `number` jumped from one enemy to the next

const SCRIPT := "res://scripts/moba3d/squirrel_kit.gd"
const DART := preload("res://scripts/moba3d/squirrel_dart.gd")
const VIEWS_DIR := "res://docs/art/moba/squirrel_s/take-b/fixed" ## approved stills (Preston, 2026-11-03), 160 canvas,
## feet row 140; the front view's tail is cut to one side by hand, and ne carries the capped ink (2026-11-04).
const LIGHTS := 3

@export_group("Starting numbers, not balance")
@export var basic_range := 6.5 ## edge to edge (MatchTeams.edge_distance); the director, bots and HUD read it
@export var basic_cooldown := 0.91 ## 1.1 darts a second
@export var dart_speed := 24.0
@export var dart_scale := 0.5 ## of a kit hit: 30
@export var hearsay_every := 4
@export var hearsay_reach := 4.0 ## metres from the first enemy's middle to the second's edge
@export var hearsay_scale := 0.3 ## of a kit hit: 18
@export var tail_height := 0.55 ## metres above the feet the dart leaves at (placeholder for the tail tip)

var current := "" ## the ability in progress, or "" when free (arena_play's Tab swap and MatchBot._use_kit read it).
## The basic attack never sets it: darts don't hold the machine. The slots will once they are built.
var darts := 0 ## darts fired since install
var count := 0 ## darts toward the next Hearsay, 0 to hearsay_every - 1
var lights: Array[MeshInstance3D] = []

static var _lit: StandardMaterial3D
static var _dim: StandardMaterial3D

@onready var player = get_parent() ## machine_test_player.gd
@onready var sprite: DirectionalSprite3D = get_parent().get_node("Sprite")


## Turns a field Player into the squirrel: frames from the approved stills, and this kit in place of any other.
static func install(p: Node3D) -> Node:
	var spr: DirectionalSprite3D = p.get_node("Sprite")
	spr.stop_action()
	spr.sprite_frames = frames()
	spr.canvas_height = 160
	spr.feet_edge_row = 141
	spr.size_class = "S"  # sets the texel size and re-raises the sprite for the canvas above
	if p.has_method("apply_size_class"):
		p.apply_size_class()
	spr.play(StringName("idle_" + spr.view))
	var old := p.get_node_or_null("Kit")
	if old != null:
		p.remove_child(old)
		old.queue_free()
	var kit: Node = load(SCRIPT).new()
	kit.name = "Kit"
	p.add_child(kit)
	return kit


## idle_<view> and walk_<view> for the five drawn views, each the approved still. They are drawn at the old low angle,
## so nothing is marked to tilt (no tilt_anims). The 35-degree stills and a real walk replace them later.
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
	impact.connect(_shake)
	_make_lights()


func _exit_tree() -> void:
	var holder: Node = player.get_node_or_null("HearsayLights") if is_instance_valid(player) else null
	if holder != null:
		holder.queue_free()


func _shake(strength: float) -> void:
	if not player.get("bot"):
		KitFeel.shake(self, strength)


func world() -> Node:
	return player.get_parent()


func targets() -> Array:
	return MatchTeams.enemies_of(player)


func feet() -> Vector3:
	return player.global_position


## The basic attack: one signal dart. target is a bot's pick, or null for the player, who aims with the mouse (facing
## when the aim is on the machine itself). Returns false when nothing fired, so the director starts no cooldown.
func basic_attack(target: Node3D) -> bool:
	var dir := Vector3.ZERO
	if target != null and is_instance_valid(target):
		dir = flat(target.global_position - feet())
	elif player.has_method("aim_dir"):
		dir = player.aim_dir()
	if dir.length() < 0.05:
		dir = flat(player.facing)
	if dir.length() < 0.05:
		return false
	dir = dir.normalized()
	player.facing = dir
	darts += 1
	count += 1
	var carries := count >= hearsay_every
	if carries:
		count = 0
	_show_lights(carries)
	var from: Vector3 = feet() + Vector3.UP * tail_height + dir * 0.25
	var d = DART.fire(world(), from, dir, targets(), dart_speed, basic_range + 0.5)
	d.data = {"number": darts, "carries": carries}
	d.struck.connect(_on_dart_struck.bind(d.data))
	cue.emit("dart_fire")
	return true


func _on_dart_struck(target: Node3D, data: Dictionary) -> void:
	if not is_instance_valid(target):
		return
	if target.has_method("hit"):
		target.hit(player, dart_scale)
	cue.emit("dart_hit")
	dart_hit.emit(target, int(data["number"]), false)
	if not data["carries"]:
		return
	var next := jump_target(target)
	if next == null:
		return  # nobody close enough: the word stops here
	hearsay.emit(target, next, int(data["number"]))
	cue.emit("hearsay_jump")
	var jd := {"number": data["number"], "carries": false}
	var to := flat(next.global_position - target.global_position)
	if to.length() < 0.05:
		_on_jump_struck(next, jd)
		return
	var j = DART.fire(world(), target.global_position + Vector3.UP * tail_height, to, [next], dart_speed, to.length() + 1.0)
	j.ignore = [target]
	j.data = jd
	j.struck.connect(_on_jump_struck.bind(jd))


func _on_jump_struck(target: Node3D, data: Dictionary) -> void:
	if not is_instance_valid(target):
		return
	if target.has_method("hit"):
		target.hit(player, hearsay_scale)
	cue.emit("dart_hit")
	dart_hit.emit(target, int(data["number"]), true)


## Where the Hearsay jump goes from `first`: the nearest enemy machine within hearsay_reach, else the nearest other enemy
## within it (minions, monsters), else null.
func jump_target(first: Node3D) -> Node3D:
	var best: Node3D = null
	var best_score := INF
	for e in targets():
		if not is_instance_valid(e) or e == first or not (e is Node3D) or e.get("alive") == false or not e.visible:
			continue
		var d := MatchTeams.edge_distance(first, e)
		if d > hearsay_reach:
			continue
		var score := d + (0.0 if e.get("kind") == "machine" else 1000.0)
		if score < best_score:
			best = e
			best_score = score
	return best


## Three small lights over the head: the Hearsay count. Placeholder until the tail's own segment lights are drawn.
func _make_lights() -> void:
	var old: Node = player.get_node_or_null("HearsayLights")
	if old != null:
		player.remove_child(old)
		old.queue_free()
	if _lit == null:
		_lit = StandardMaterial3D.new()
		_lit.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		_lit.albedo_color = DART.COLOUR
		_dim = StandardMaterial3D.new()
		_dim.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		_dim.albedo_color = Color(0.16, 0.18, 0.24)
	var holder := Node3D.new()
	holder.name = "HearsayLights"
	player.add_child(holder)
	holder.position = Vector3.UP * (2.0 * sprite.size_scale())
	lights.clear()
	for i in LIGHTS:
		var mi := MeshInstance3D.new()
		var s := SphereMesh.new()
		s.radius = 0.045
		s.height = 0.09
		s.radial_segments = 8
		s.rings = 4
		mi.mesh = s
		mi.material_override = _dim
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mi.position = Vector3((i - 1) * 0.13, 0.0, 0.0)
		holder.add_child(mi)
		lights.append(mi)


func lit_count() -> int:
	var n := 0
	for l in lights:
		if is_instance_valid(l) and l.material_override == _lit:
			n += 1
	return n


func _show_lights(carries: bool) -> void:
	for i in lights.size():
		lights[i].material_override = _lit if (carries or i < count) else _dim
	if carries:
		get_tree().create_timer(0.25).timeout.connect(_dim_after_jump)


func _dim_after_jump() -> void:
	if count != 0:
		return  # a dart already fired since: its lights stay
	for l in lights:
		if is_instance_valid(l):
			l.material_override = _dim
