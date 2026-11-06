class_name ArenaPit
extends Node3D
## A side pit you take and hold (map design lane, 2026-11-05). Preston picked it from
## docs/plan/moba-map-skillup-2026-11-05.md, and the numbers start from Twisted Treeline's altars.
## arena_blockout.gd puts one in each pit at runtime: Built/BluePitCapture and Built/RedPitCapture.
##
## Taking a pit:
## - The alive machines inside count: group "map_units" with meta unit_kind "machine" and meta team. The director
##   drops dead machines from that group.
## - One team inside: the fill grows, 9 s alone, 6 s for two, 4.5 s for three. The other team's fill drains first.
## - Both teams inside: the fill pauses, it does not reset (game feel's ask, 2026-11-05).
## - Nobody inside: after 3 s the fill fades at 10% a second.
## - Full: the team owns the pit. It locks for 90 s and shows the pit's surroundings to the owners (it joins
##   "vision_sources" for that time). After the lock it stays theirs until the other team takes it.
##
## For the other lanes:
## - signal pit_taken(team) fires once per take, here at the pit (MapAudio can hear it by that name).
## - ArenaPit.held(get_tree(), team) is how many pits a team holds now. Game feel reads it for the wave reward.
## The ring is shaders/world/capture_ring.gdshader. The HUD's top stack and the minimap show each pit's state.

signal pit_taken(team: String)

const CAPTURE_TIME := 9.0 ## seconds for one machine
const EXTRA_MACHINE := 0.5 ## each machine past the first adds half the speed again
const LOCK_TIME := 90.0
const DECAY_DELAY := 3.0
const DECAY_RATE := 0.1 ## share of the fill lost per second once nobody is inside
const SIGHT := 10.0 ## metres the pit shows its owners while locked
const RING_INSET := 0.6 ## the ring's outer edge sits this far inside `radius` (4.9 m in a pit, inside the rim's dashes at 5.3)
const RING_WIDTH := 0.7
const FLASH_TIME := 0.6
const SHAKE := 0.35 ## KitFeel's stomp
const SHAKE_NEAR := 22.0 ## the camera feels a take within this many metres

var group := "arena_pits" ## ArenaBeacon sets its own, so held() and the pit markers never count it
var home_team := "" ## whose half the pit sits in
var radius := 5.5 ## machines count inside this
var owner_team := "" ## "" until someone takes it
var progress := 0.0 ## 0 to 1, toward `capturing`
var capturing := ""
var locked_left := 0.0
var contested := false
var colours := {"blue": Color(0.4, 0.6, 1.0), "red": Color(1.0, 0.4, 0.32), "": Color(1.0, 0.6, 0.22)}
var glow: OmniLight3D ## the pit's grate light, recoloured by the owner; may be null
var texels_per_metre := 50.0

var _glow_colour := Color.WHITE
var _glow_energy := 1.6
var _idle := 0.0
var _flash := 0.0
var _t := 0.0
var _mat: ShaderMaterial


## How many pits `team` holds right now.
static func held(tree: SceneTree, team: String) -> int:
	var n := 0
	for p in tree.get_nodes_in_group("arena_pits"):
		if p is ArenaPit and p.owner_team == team:
			n += 1
	return n


func setup(home: String, inside: float, team_colours: Dictionary, light: OmniLight3D, texels: float) -> void:
	home_team = home
	radius = inside
	colours = team_colours
	glow = light
	texels_per_metre = texels


func _ready() -> void:
	add_to_group(group)
	if glow:
		_glow_colour = glow.light_color
		_glow_energy = glow.light_energy
	_mat = ShaderMaterial.new()
	_mat.shader = preload("res://shaders/world/capture_ring.gdshader")
	_mat.set_shader_parameter("radius", radius - RING_INSET)
	_mat.set_shader_parameter("width", RING_WIDTH)
	_mat.set_shader_parameter("texels_per_metre", texels_per_metre)
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * ((radius - RING_INSET) * 2.0 + 0.2)
	plane.material = _mat
	var mi := MeshInstance3D.new()
	mi.name = "Ring"
	mi.mesh = plane
	mi.position.y = 0.035 # just over the painted rings at 0.02
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)
	_show()


func _physics_process(delta: float) -> void:
	_t += delta
	var n := count_inside()
	contested = n.blue > 0 and n.red > 0
	if locked_left > 0.0:
		locked_left = maxf(locked_left - delta, 0.0)
		if locked_left == 0.0:
			remove_from_group("vision_sources")
	else:
		_step(n, delta)
	_flash = maxf(_flash - delta / FLASH_TIME, 0.0)
	_show()


## {"blue": machines inside, "red": machines inside}
func count_inside() -> Dictionary:
	var n := {"blue": 0, "red": 0}
	if not is_inside_tree():
		return n
	for u in get_tree().get_nodes_in_group("map_units"):
		if not (u is Node3D) or String(u.get_meta("unit_kind", "")) != "machine":
			continue
		if "alive" in u and not u.alive:
			continue
		var team := String(u.get_meta("team", ""))
		if not n.has(team):
			continue
		var p: Vector3 = u.global_position
		if Vector2(p.x - global_position.x, p.z - global_position.z).length() <= radius:
			n[team] += 1
	return n


func _step(n: Dictionary, delta: float) -> void:
	if contested:
		_idle = 0.0
		return
	var team := "blue" if n.blue > 0 else ("red" if n.red > 0 else "")
	if team == "":
		_idle += delta
		if _idle > DECAY_DELAY:
			_drain(DECAY_RATE * delta)
		return
	_idle = 0.0
	var rate: float = (1.0 + EXTRA_MACHINE * (n[team] - 1)) / CAPTURE_TIME
	if team == owner_team or (capturing != "" and capturing != team):
		_drain(rate * delta) # owners push an enemy fill back; a new team drains the old fill first
		return
	capturing = team
	progress += rate * delta
	if progress >= 1.0:
		_take(team)


func _drain(amount: float) -> void:
	progress = maxf(progress - amount, 0.0)
	if progress == 0.0:
		capturing = ""


func _take(team: String) -> void:
	owner_team = team
	progress = 0.0
	capturing = ""
	locked_left = LOCK_TIME
	_flash = 1.0
	set_meta("team", team)
	set_meta("vision_radius", SIGHT)
	add_to_group("vision_sources")
	var cam := get_viewport().get_camera_3d()
	if cam and cam.global_position.distance_to(global_position) < SHAKE_NEAR:
		KitFeel.shake(self, SHAKE)
	pit_taken.emit(team)


func _show() -> void:
	if _mat == null:
		return
	var own: Color = colours.get(owner_team, colours[""])
	var base := Color(own.darkened(0.35), 0.5)
	var lit := Color(colours.get(capturing, own), 0.95)
	var fill := progress
	if locked_left > 0.0: # the lit blocks count the lock down
		base = Color(own.darkened(0.55), 0.55)
		lit = Color(own, 0.95)
		fill = locked_left / LOCK_TIME
	_mat.set_shader_parameter("base_color", base)
	_mat.set_shader_parameter("fill_color", lit)
	_mat.set_shader_parameter("fill", fill)
	_mat.set_shader_parameter("pulse", 1.0 if contested and fmod(_t, 0.4) < 0.2 else 0.0)
	_mat.set_shader_parameter("flash", _flash)
	if glow:
		glow.light_color = _glow_colour if owner_team == "" else _glow_colour.lerp(own, 0.75)
		glow.light_energy = _glow_energy * (1.0 + 3.0 * _flash)
