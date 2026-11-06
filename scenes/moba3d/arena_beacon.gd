class_name ArenaBeacon
extends ArenaPit
## The plaza beacon (map design lane, 2026-11-05): Joust's Demon King, as a point you take instead of a boss
## (docs/plan/moba-map-skillup-2026-11-05.md, choice 5). arena_blockout.gd puts one at the plaza centre at
## runtime: Built/PlazaBeacon.
## - It comes up at 4:00 of match time, and again 5:00 after each take. While it is down nothing of it shows.
## - Taking it works like a pit (ArenaPit): 9 s alone, 6 s for two, 4.5 s for three. It pauses while both teams
##   are inside, holds 3 s when empty, then fades. Nobody keeps it: a take sends it down again.
## - The match clock is the director's elapsed (group "match_director"). Without a director it keeps its own.
## For the other lanes:
## - signal beacon_up() when it comes up, beacon_taken(team) on a take, both here at the plaza.
## - Game feel switches the other team's tower off on beacon_taken (MatchStructure.off_left).
##   arena_blockout.set_structure_off() gives the tower its switched-off look, and the HUD shows the countdown.

signal beacon_up
signal beacon_taken(team: String)

const FIRST_UP := 240.0 ## 4:00, Joust's Demon King
const BACK_AFTER := 300.0 ## 5:00 after a take, Joust's respawn
const BEAM_HEIGHT := 3.8 ## under the chase camera's 4.45 m frame top
const BEAM_R := 0.25

var active := false
var up_at := FIRST_UP
var last_taker := ""
var _own_clock := 0.0
var _beam: MeshInstance3D
var _beam_mat: StandardMaterial3D
var _light: OmniLight3D


func _init() -> void:
	group = "arena_beacons"


func _ready() -> void:
	super._ready()
	var cyl := CylinderMesh.new()
	cyl.top_radius = BEAM_R * 0.6
	cyl.bottom_radius = BEAM_R
	cyl.height = BEAM_HEIGHT
	cyl.radial_segments = 8
	cyl.rings = 1
	cyl.cap_top = false
	cyl.cap_bottom = false
	_beam_mat = StandardMaterial3D.new()
	_beam_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_beam_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_beam_mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	_beam_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	cyl.material = _beam_mat
	_beam = MeshInstance3D.new()
	_beam.name = "Beam"
	_beam.mesh = cyl
	_beam.position.y = BEAM_HEIGHT * 0.5
	_beam.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_beam)
	_light = OmniLight3D.new()
	_light.name = "Light"
	_light.omni_range = 7.0
	_light.position.y = 1.5
	add_child(_light)
	_show()


## Match seconds: the director's once there is one, else this beacon's own.
func now() -> float:
	var d = _director()
	return float(d.elapsed) if d else _own_clock


## Seconds until it comes up; 0 while it is up.
func up_in() -> float:
	return 0.0 if active else maxf(up_at - now(), 0.0)


func _director(): # untyped: the director's fields are read by name
	return get_tree().get_first_node_in_group("match_director") if is_inside_tree() else null


func _physics_process(delta: float) -> void:
	var d = _director()
	if d == null:
		_own_clock += delta
	elif not d.ready_to_play:
		return
	if active:
		super._physics_process(delta)
		return
	_t += delta
	_flash = maxf(_flash - delta / FLASH_TIME, 0.0)
	if now() >= up_at:
		active = true
		progress = 0.0
		capturing = ""
		_idle = 0.0
		_flash = 1.0
		beacon_up.emit()
	_show()


func _take(team: String) -> void:
	active = false
	last_taker = team
	progress = 0.0
	capturing = ""
	contested = false
	up_at = now() + BACK_AFTER
	_flash = 1.0
	var cam := get_viewport().get_camera_3d()
	if cam and cam.global_position.distance_to(global_position) < SHAKE_NEAR:
		KitFeel.shake(self, SHAKE)
	beacon_taken.emit(team)


func _show() -> void:
	var ring := get_node_or_null("Ring") as Node3D
	if ring:
		ring.visible = active
	if active:
		super._show()
	if _beam == null:
		return
	var lit := active or _flash > 0.0 # after a take the beam bursts in the taker's colour and goes out
	_beam.visible = lit
	_light.visible = lit
	if not lit:
		return
	var col: Color = colours[""]
	if not active:
		col = colours.get(last_taker, col)
	elif capturing != "" and progress > 0.0:
		col = col.lerp(colours.get(capturing, col), 0.6)
	var pulse := 0.5 + 0.5 * sin(_t * 3.0)
	_beam_mat.albedo_color = Color(col.lerp(Color.WHITE, _flash * 0.6), 0.35 + 0.15 * pulse + 0.5 * _flash)
	_light.light_color = col
	_light.light_energy = 1.5 + 0.5 * pulse + 4.0 * _flash
