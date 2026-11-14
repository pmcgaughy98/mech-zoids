extends Node3D
## Gorilla ult (Silverback Cage), smooth ground effects (gorilla effects lane, 2026-11-11). Visual only: listens to the
## kit's "used" signal and the 3D body's clip events ("drum" on each chest hit, "beat" on the kit's three beats).
## No kit code, signals or numbers are changed. Structure measured on SMITE 2's Geb and Cabrakan
## (docs/reference/gorilla-fx-synthesis-2026-11-11.md):
##   each chest hit (0.42, 0.53, 0.64, 0.75 s): a small lime ripple at the feet, a little wider and stronger each time
##   beats 1 and 2 (the taunts, 0.42 and 0.75 s): a double ripple that races to the taunt reach and fades in 0.5 s
##   the slam (1.27 s): two fist dents and a crack web that starts hot and cools to dark fissures; a wall of dust and
##                      a lime edge race out to where the cage rises; rock chunks land and lie there, then sink
## Hidden while the ult plays: the kit's pixel pulse ring and pixel impact puff. Codex's atlas ring decal on each beat
## is muted by default (hide_codex_ring) so the two rings do not stack; set it false to keep both.
const RING := preload("res://shaders/gorilla_beat_ring.gdshader")
const GROUND := preload("res://shaders/gorilla_slam_ground.gdshader")
const DUST := preload("res://shaders/gorilla_dust.gdshader")
const LIFT := 0.04
const GRAVITY := 16.0
const CRACK_REACH := 3.2 ## metres the crack web runs out from the fists
const GROUND_EXTENT := 1.2
const GROUND_LIFE := 3.0
const FIST_BONES := ["lefthand", "righthand"] ## lower-case bone names of the two fists; empty or missing uses feet + ahead
var kit: Node
var actor: Node3D
var crack_color := Color(0.62, 1.0, 0.16) ## the hot colour of the weight family (cracks, chunks, the fist light). Lime as built; amber (1.0, 0.62, 0.22) is the alternative shown to Preston 2026-11-12
var hide_stand_ins := true ## the kit's pixel silverback_ring pulses and impact_puff sprite
var hide_codex_ring := true ## Codex's atlas ring decal on each beat (cell 3 of reactor-atlas-v1)
var drums := 0
var beats := 0
var elapsed := 0.0
var hidden_count := 0
var codex_muted := 0
var log_rows: Array = [] ## {name, time, radius} for the checks
var _ult_until := -1.0
var _body: Object = null
var _rings: Array = []
var _dust: Array = []
var _slams: Array = []
var _rock_mesh: Mesh
var _rock_mat: StandardMaterial3D


func setup(k: Node, p: Node3D) -> void:
	kit = k
	actor = p
	kit.used.connect(_on_used)
	kit.contact.connect(_on_contact)
	var rock := SphereMesh.new()  # few segments: a faceted chunk
	rock.radius = 0.5
	rock.height = 0.8
	rock.radial_segments = 5
	rock.rings = 2
	_rock_mesh = rock
	_rock_mat = StandardMaterial3D.new()
	_rock_mat.albedo_color = Color(0.24, 0.24, 0.27)
	_rock_mat.roughness = 0.95
	_rock_mat.emission_enabled = true
	_rock_mat.emission = Color(0.62, 1.0, 0.16)
	_rock_mat.emission_energy_multiplier = 0.0


func _on_used(slot: String) -> void:
	if slot == "4":
		drums = 0
		beats = 0
		_ult_until = elapsed + 2.2  # the clip's slam lands at 1.27 s; stand-ins spawn until then
		_ult_cast = elapsed


func _watch_body() -> void:
	var b: Variant = kit.get("visual_body")
	if b == null or not is_instance_valid(b):
		b = actor.get("body")
	if b == null or b == _body or not is_instance_valid(b) or not b.has_signal("event"):
		return
	_body = b
	b.event.connect(_on_body_event)
	if b.has_signal("step"):
		b.step.connect(_on_step)


func _on_body_event(clip: String, n: String, _damage: bool) -> void:
	if clip == "FaultLine":
		_on_fault_clip(n)
		return
	if clip != "Ult" or elapsed > _ult_until or not is_instance_valid(actor):
		return
	if n == "drum":
		drums += 1
		_drum(drums)
	elif n == "beat":
		beats += 1
		if beats <= 2:
			_beat(beats)
		elif beats == 3:
			_slam()


## One chest hit: a small ripple at the feet. Each is a little wider and stronger, so the four build.
func _drum(i: int) -> void:
	_charge_step(i)
	var r := 1.6 + 0.35 * i
	_ring(kit.feet(), r, 0.26 + 0.07 * i, 0.3, 0.10)
	log_rows.append({"name": "drum_%d" % i, "time": elapsed, "radius": r})


## Beats 1 and 2 are the taunts: the ripple runs to the taunt reach. The second is the quieter one, as in the kit.
func _beat(i: int) -> void:
	var r: float = kit.ult_radius
	_ring(kit.feet(), r, 0.8 if i == 1 else 0.62, 0.5, 0.14)
	_mute_codex_ring()
	log_rows.append({"name": "beat_%d" % i, "time": elapsed, "radius": r})


## Beat 3: both fists down. Cracks at the fists, dust and a lime edge out to the cage wall.
func _slam() -> void:
	var feet: Vector3 = kit.feet()
	var fwd: Vector3 = kit.ahead()
	var right := fwd.cross(Vector3.UP).normalized()
	var fists := _fists(feet, fwd, right)
	var mid: Vector3 = (fists[0] + fists[1]) * 0.5
	mid.y = feet.y
	var gap: float = clampf(Vector3(fists[0].x - fists[1].x, 0.0, fists[0].z - fists[1].z).length() * 0.5, 0.3, 0.9)
	var across := Vector3(fists[1].x - fists[0].x, 0.0, fists[1].z - fists[0].z)
	if across.length() > 0.2:
		right = across.normalized()  # the quad's +X runs fist to fist
	var dome_r: float = kit.ult_dome_radius
	# ground: fist dents and the crack web; a short light at the fists, small, so it never washes the gorilla out
	_ground_burst(mid, right, CRACK_REACH, {"fist_gap": gap}, 10, 1.0, GROUND_LIFE)
	# the reach: a lime edge and a wall of dust from the cage's centre out to its wall
	_ring(feet, dome_r, 0.85, 0.55, 0.14)
	var count := 16
	for i in count:
		var ang := TAU * (float(i) + randf() * 0.5) / float(count)
		var out := Vector3(cos(ang), 0.0, sin(ang))
		var travel := dome_r - 1.6 + randf_range(-0.3, 0.2)
		_dust_at(feet + out * 1.2, randf_range(1.5, 2.0), 0.62, 0.55, out * travel * 6.0, 6.0)
	for f in fists:
		_dust_at(Vector3(f.x, feet.y, f.z) + fwd * 0.15, 1.5, 0.75, 0.75, fwd * 1.0 + Vector3.UP * 0.5, 3.0)
	_mute_codex_ring()
	log_rows.append({"name": "slam", "time": elapsed, "radius": dome_r, "fists": [fists[0] - feet, fists[1] - feet], "gap": gap})


## One cracked-floor burst: the ground quad (dents and crack web), rock chunks, and a short light when peak > 0.
## The quad's +X runs along `right`. params go straight to the ground shader (fist_gap, fist_r, dent_mul, flash_mul, hold).
func _ground_burst(mid: Vector3, right: Vector3, reach: float, params: Dictionary, rocks: int, peak: float, life: float, rock_scale := 1.0) -> Dictionary:
	var row := {"age": 0.0, "rocks": [], "at": mid, "life": life, "peak": peak, "light": null}
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * reach * GROUND_EXTENT * 2.0
	g.mesh = plane
	var mat := ShaderMaterial.new()
	mat.shader = GROUND
	mat.set_shader_parameter("radius_m", reach)
	mat.set_shader_parameter("extent", GROUND_EXTENT)
	mat.set_shader_parameter("seed", randf() * 100.0)
	mat.set_shader_parameter("lime", Vector3(crack_color.r, crack_color.g, crack_color.b))
	for k in params:
		mat.set_shader_parameter(k, params[k])
	g.material_override = mat
	_place(g, mid + Vector3.UP * LIFT)
	g.global_basis = Basis(right, Vector3.UP, right.cross(Vector3.UP))
	row.ground = g
	if peak > 0.0:
		var l := OmniLight3D.new()
		l.light_color = crack_color.lerp(Color.WHITE, 0.45)
		l.omni_range = maxf(reach * 1.1, 2.0)
		l.shadow_enabled = false
		l.light_energy = 0.0
		add_child(l)
		l.top_level = true
		l.global_position = mid + Vector3.UP * 0.5
		row.light = l
	for i in rocks:
		var rk := _rock(mid, i, rocks)
		rk.node.scale *= rock_scale
		row.rocks.append(rk)
	_slams.append(row)
	return row


# --- Slam hits (slice 2, 2026-11-12): the basic chain's third hit and the grab slam. The same cracked floor as the
# ult's slam, smaller, under the target. Weight family: cracks, dust and rock, no ripple. Off by default (slam_hits)
# because it stands in for Codex's atlas crater decal on those two hits: shown old against new first.
var slam_hits := false
var hide_codex_crater := true ## with slam_hits on, mute Codex's atlas crater (cell 1) under those two hits
var crater_muted := 0
var _grab: Object = null


func _floor_under(t: Node3D) -> Vector3:
	return Vector3(t.global_position.x, actor.global_position.y, t.global_position.z)


func _away_from_actor(at: Vector3) -> Vector3:
	var dir := Vector3(at.x - actor.global_position.x, 0.0, at.z - actor.global_position.z)
	return dir.normalized() if dir.length() > 0.05 else kit.ahead()


## The basic chain's third hit (the Slam clip, contact at 0.417 s): cracks break out under the target, dust is thrown
## away from the gorilla, a few small chunks jump. No dent (the target is standing there) and no light.
func _on_contact(target: Node3D, slam: bool) -> void:
	if not slam_hits or not slam or not is_instance_valid(target) or not is_instance_valid(actor):
		return
	var at := _floor_under(target)
	var dir := _away_from_actor(at)
	var side := dir.cross(Vector3.UP).normalized()
	_ground_burst(at, side, 1.7, {"fist_gap": 0.05, "dent_mul": 0.0, "flash_mul": 0.55, "hold": -0.6}, 4, 0.0, 2.2, 0.7)
	for s in [-1.0, 1.0]:
		_dust_at(at + side * 0.45 * s + dir * 0.2, 1.1, 0.55, 0.6, dir * 1.6 + side * 0.9 * s + Vector3.UP * 0.4, 3.5)
	_mute_codex(Vector2(1, 0), hide_codex_crater)
	log_rows.append({"name": "basic_slam", "time": elapsed, "radius": 1.7, "at": at})


## The grab slam: the victim is driven into the floor. One body-sized dent, a wider crack web, dust thrown all round.
func _on_grab_slam(target: Node3D) -> void:
	if not slam_hits or not is_instance_valid(target) or not is_instance_valid(actor):
		return
	var at := _floor_under(target)
	var dir := _away_from_actor(at)
	var side := dir.cross(Vector3.UP).normalized()
	_ground_burst(at, side, 2.4, {"fist_gap": 0.0, "fist_r": 0.55, "dent_mul": 0.8, "flash_mul": 0.35, "hold": -0.2}, 7, 0.6, 2.8)
	for i in 6:
		var ang := TAU * (float(i) + randf() * 0.5) / 6.0
		var out := Vector3(cos(ang), 0.0, sin(ang))
		_dust_at(at + out * 0.5, randf_range(1.2, 1.6), 0.6, 0.6, out * 4.5 + Vector3.UP * 0.3, 5.0)
	_mute_codex(Vector2(1, 0), hide_codex_crater)
	log_rows.append({"name": "grab_slam", "time": elapsed, "radius": 2.4, "at": at})


func _watch_grab() -> void:
	var g: Variant = kit.get("grab")
	if g == null or g == _grab or not is_instance_valid(g) or not g.has_signal("slammed"):
		return
	_grab = g
	g.slammed.connect(_on_grab_slam)


# --- Reactor Fault Line (slice 7, 2026-11-13), key 2. Preston: "No sheets unless enhanced to look like our other
# effects which look not flat". The first try (slice 3) was a flat crack strip sliding along the line and was rejected.
# This one has no travelling flat layer at all. SMITE 2's Cabrakan, Tectonic Shift, reads in its own tooltip as "a
# fissure ... from the fissure, five pieces of earth erupt", and in match footage the pieces are jagged and as tall as
# the body. So: the back reactor glows on the clip's "charge", throws a short lime arc up and over on "fire", and
# where the kit's wave head passes, rock shards erupt out of the floor one after another, left and right, hot lime
# at first and cooling to dark rock, each with a small crack burst that stays where it is and a puff of dust. At the
# end point a crown of shards stands for as long as the slow lasts, then everything sinks back.
# Read only: kit.fault.waves and kit.fault.fields (positions) and the body's "FaultLine" clip events. No kit edits.
# Off by default (fault_line): it hides Codex's sliding atlas crater and its flat area decal, so it is shown old
# against new first.
const GLOW := preload("res://shaders/gorilla_glow.gdshader")
const FAULT_START := 1.0 ## metres ahead of the gorilla where the line begins (where the arc lands)
const SHARD_GAP := 0.55 ## metres of line between eruptions
var fault_line := false
var hide_codex_fault := true ## with fault_line on, hide Codex's sliding crater and its slow-area decal
var fault_muted := 0
var shards_made := 0
var arcs := 0
var _runs: Dictionary = {} ## the wave decal's instance id -> the run drawn for it
var _fault_seen: Dictionary = {}
var _shards: Array = []
var _glows: Array = []
var _shard_meshes: Array = []


func _watch_fault(_delta: float) -> void:
	var f: Variant = kit.get("fault")
	if not fault_line or f == null or not is_instance_valid(f):
		return
	var live_ids: Dictionary = {}
	for wave in f.waves:
		if not is_instance_valid(wave.node):
			continue
		var id: int = wave.node.get_instance_id()
		live_ids[id] = true
		if not _runs.has(id):
			_runs[id] = _fault_begin(wave)
		var run: Dictionary = _runs[id]
		run.head = maxf(Vector3(wave.at.x - run.from.x, 0.0, wave.at.z - run.from.z).length() - FAULT_START, 0.0)
		_fault_trail(run)
		_fault_hide(wave.node)
	for field in f.fields:
		if not is_instance_valid(field.node):
			continue
		var id: int = field.node.get_instance_id()
		live_ids[id] = true
		_fault_hide(field.node)
		if _runs.has(id) and not _runs[id].arrived:
			_runs[id].arrived = true
			_runs[id].head = _runs[id].length
			_fault_trail(_runs[id])
			_fault_arrive(_runs[id], field.at, float(f.RADIUS), float(f.LIFE))
	for id in _runs.keys():
		if not live_ids.has(id):
			_runs.erase(id)  # the wave and its area are gone; the shards live out their own time


func _fault_begin(wave: Dictionary) -> Dictionary:
	var dir: Vector3 = wave.direction
	var from := Vector3(actor.global_position.x, actor.global_position.y, actor.global_position.z)
	var total := Vector3(wave.end.x - from.x, 0.0, wave.end.z - from.z).length()
	var length := maxf(total - FAULT_START, 0.3)
	log_rows.append({"name": "fault_run", "time": elapsed, "radius": length})
	return {"from": from, "dir": dir, "length": length, "head": 0.0, "arrived": false, "next": 0.15, "side": 1.0}


## As the wave head passes: a tall shard one side, a short one the other, a small crack burst under them that stays
## put, and dust. Left and right swap each step, so the line is ragged, not a fence.
func _fault_trail(run: Dictionary) -> void:
	while run.head >= run.next and run.next < run.length - 0.5:
		var side: Vector3 = Vector3.UP.cross(run.dir) * run.side
		var at: Vector3 = run.from + run.dir * (FAULT_START + run.next)
		_shard(at + side * 0.22, (side * 0.8 + run.dir * 0.5).normalized(), randf_range(0.85, 1.25), 1.25)
		_shard(at - side * 0.3 + run.dir * 0.2, (-side * 0.9 + run.dir * 0.4).normalized(), randf_range(0.4, 0.6), 1.15)
		_ground_burst(at, side, 0.75, {"fist_gap": 0.0, "dent_mul": 0.0, "flash_mul": 0.4, "hold": -0.7}, 1, 0.0, 1.7, 0.6)
		_dust_at(at + side * 0.35, randf_range(1.0, 1.3), 0.5, 0.6, side * 0.9 + Vector3.UP * 0.7, 4.0)
		run.side = -run.side
		run.next += SHARD_GAP


## The end point: a crown of shards that stands for as long as the slow lasts, a crack burst the size of the area
## with its quiet rim, and dust thrown outward.
func _fault_arrive(run: Dictionary, at: Vector3, radius: float, life: float) -> void:
	var side: Vector3 = Vector3.UP.cross(run.dir)
	var floor_at := Vector3(at.x, actor.global_position.y, at.z)
	_ground_burst(floor_at, side, radius * 1.15, {"fist_gap": 0.0, "dent_mul": 0.0, "flash_mul": 0.5, "hold": -0.3, "rim_m": radius, "rim_life": life}, 4, 0.0, life + 1.4, 0.8)
	_shard(floor_at, (run.dir * 0.4).normalized(), 1.5, life + 0.25)
	for i in 7:
		var ang := TAU * (float(i) + randf() * 0.4) / 7.0
		var out := Vector3(cos(ang), 0.0, sin(ang))
		_shard(floor_at + out * randf_range(0.6, 1.0), out, randf_range(0.55, 0.95), life + 0.2, 0.02 * i)
	for i in 6:
		var ang2 := TAU * (float(i) + randf() * 0.5) / 6.0
		var out2 := Vector3(cos(ang2), 0.0, sin(ang2))
		_dust_at(floor_at + out2 * 0.4, randf_range(1.1, 1.5), 0.55, 0.6, out2 * (radius - 0.4) * 5.0 + Vector3.UP * 0.4, 5.0)
	log_rows.append({"name": "fault_end", "time": elapsed, "radius": radius, "at": floor_at})


func _fault_hide(node: Node3D) -> void:
	if not hide_codex_fault:
		return
	node.visible = false
	if not _fault_seen.has(node.get_instance_id()):
		_fault_seen[node.get_instance_id()] = true
		fault_muted += 1


## One jagged rock shard. It shoots up out of the floor in a tenth of a second, glows the hot colour and cools, stands,
## and sinks back at the end of its life. `lean` tips it away from the line; delay holds it back (the crown's stagger).
func _shard(at: Vector3, lean: Vector3, height: float, life: float, delay := 0.0) -> void:
	if _shard_meshes.is_empty():
		for lean_top in [0.28, 0.5, 0.74]:  # flat-faced wedges with the ridge off centre: broken slabs, not cones
			var wedge := PrismMesh.new()
			wedge.size = Vector3(0.5, 1.0, 0.3)
			wedge.left_to_right = lean_top
			_shard_meshes.append(wedge)
	var node := MeshInstance3D.new()
	node.mesh = _shard_meshes[randi() % _shard_meshes.size()]
	var mat := _rock_mat.duplicate() as StandardMaterial3D
	mat.albedo_color = Color(0.2, 0.21, 0.25)
	mat.emission = crack_color
	node.material_override = mat
	var up := (Vector3.UP + lean * randf_range(0.22, 0.4)).normalized()
	var basis := Basis(Quaternion(Vector3.UP, up)) * Basis(Vector3.UP, randf() * TAU)
	_place(node, at)
	node.visible = false
	_shards.append({"node": node, "mat": mat, "age": -delay, "life": life, "h": height, "basis": basis, "base": Vector3(at.x, actor.global_position.y, at.z)})
	shards_made += 1


## A soft lime glow that faces the camera. delay holds it back; vel drifts it.
func _glow_at(at: Vector3, size: float, life: float, strength: float, grow := false, delay := 0.0) -> void:
	var q := MeshInstance3D.new()
	var mesh := QuadMesh.new()
	mesh.size = Vector2.ONE * size
	q.mesh = mesh
	var mat := ShaderMaterial.new()
	mat.shader = GLOW
	mat.set_shader_parameter("life", life)
	mat.set_shader_parameter("strength", strength)
	mat.set_shader_parameter("grow", 1.0 if grow else 0.0)
	mat.set_shader_parameter("age", -delay)
	q.material_override = mat
	_place(q, at)
	_glows.append({"node": q, "age": -delay, "life": life})


## The body's FaultLine clip: the reactor on the back charges, then throws a short arc up and over to where the line
## begins. The arc is a string of glow beads lit one after another, so it has height and is gone in a blink.
func _on_fault_clip(n: String) -> void:
	if not fault_line or not is_instance_valid(actor):
		return
	var dir: Vector3 = kit.ahead()
	var feet: Vector3 = kit.feet()
	# The reactor rides the Chest bone (kit v40 arches the back: at the fire the bone is 1.40 m up, 0.48 m back); it
	# sits on the back surface, 0.3 m behind the bone. The old fixed point stays as the fallback.
	var chest: Variant = _bone_pos("chest")
	var reactor: Vector3 = (chest - dir * 0.3) if chest != null else feet - dir * 0.45 + Vector3.UP * 1.05
	if n == "charge":
		_glow_at(reactor, 1.0, 0.34, 0.85, true)
	elif n == "fire":
		var land := feet + dir * FAULT_START + Vector3.UP * 0.1
		for i in 8:
			var u := float(i) / 7.0
			var at := reactor.lerp(land, u) + Vector3.UP * 1.25 * sin(u * PI)
			_glow_at(at, lerpf(0.55, 0.85, u), 0.26, lerpf(0.7, 1.0, u), false, 0.014 * i)
		arcs += 1


# --- Ult wind-up, the chest charge (slice 8, 2026-11-14). Measured on SMITE 2's Geb, Cataclysm: the wind-up belongs
# to the body (he glows for about 0.6 s) and the floor stays quiet until the hit. So: a soft lime glow on the chest
# that steps up with each of the four chest hits, a small spark where the fist lands, and in the last tenth of a
# second before the slam the charge runs out along both arms into the fists. If the ult is cut short it just fades.
# Off by default (windup_glow): shown old against new first. Nothing of Codex's or the kit's is hidden.
const GLOW_THROUGH := preload("res://shaders/gorilla_glow_through.gdshader")
const CHARGE_STEPS := [0.4, 0.55, 0.7, 0.9]
var windup_glow := false
var windup_steps := 0 ## chest hits that stepped the glow up, for the checks
var windup_runs := 0 ## times the charge ran down the arms
var _charge: MeshInstance3D
var _charge_state := "" ## "", "build" or "fade"
var _charge_level := 0.0
var _charge_target := 0.0
var _charge_pop := 0.0
var _ult_cast := -10.0
var _slam_at := 1.27


func _bone_pos(bone_name: String) -> Variant:
	var sk: Variant = _body.get("skeleton") if is_instance_valid(_body) else null
	if not (sk is Skeleton3D):
		return null
	for i in sk.get_bone_count():
		if sk.get_bone_name(i).to_lower() == bone_name:
			return sk.global_transform * sk.get_bone_global_pose(i).origin
	return null


func _chest_point() -> Vector3:
	var at: Variant = _bone_pos("chest")
	return at if at != null else actor.global_position + Vector3.UP * 1.1


## When the slam lands, in seconds after the cast: the clip's third "beat". 1.27 if the body does not say.
func _slam_time() -> float:
	var ev: Variant = _body.get("_events") if is_instance_valid(_body) else null
	if ev is Dictionary and ev.has("Ult"):
		var beats_seen := 0
		for e in ev["Ult"]:
			if String(e[0]) == "beat":
				beats_seen += 1
				if beats_seen == 3:
					return float(e[1])
	return 1.27


func _charge_step(i: int) -> void:
	if not windup_glow:
		return
	if not is_instance_valid(_charge):
		_charge = MeshInstance3D.new()
		var mesh := QuadMesh.new()
		mesh.size = Vector2.ONE * 1.7
		_charge.mesh = mesh
		var mat := ShaderMaterial.new()
		mat.shader = GLOW_THROUGH
		mat.render_priority = 4
		_charge.material_override = mat
		_place(_charge, _chest_point())
		_charge_level = 0.0
	_charge_state = "build"
	_charge_target = CHARGE_STEPS[clampi(i - 1, 0, 3)]
	_charge_pop = 1.0
	_slam_at = _slam_time()
	var chest := _chest_point()
	var best: Variant = null
	for hand in ["lefthand", "righthand"]:
		var hp: Variant = _bone_pos(hand)
		if hp != null and (best == null or (hp - chest).length() < (best - chest).length()):
			best = hp
	if best != null:
		_glow_at(best, 0.55, 0.16, 1.0)  # the spark where that fist lands
	windup_steps += 1


## The charge leaves the chest: a string of beads along each arm into the fists, lit one after another.
func _run_down() -> void:
	var chest := _chest_point()
	for hand in ["lefthand", "righthand"]:
		var hp: Variant = _bone_pos(hand)
		if hp == null:
			continue
		for k in 5:
			var u := float(k + 1) / 5.0
			_glow_at(chest.lerp(hp, u), lerpf(0.45, 0.65, u), 0.2, 0.9, false, 0.018 * k)
	windup_runs += 1


func _charge_tick(delta: float) -> void:
	if _charge_state == "":
		return
	if not is_instance_valid(_charge):
		_charge_state = ""
		return
	var since := elapsed - _ult_cast
	_charge_pop = maxf(_charge_pop - delta / 0.12, 0.0)
	if _charge_state == "build":
		_charge_level = move_toward(_charge_level, _charge_target, delta * 4.0)
		if since >= _slam_at - 0.1:
			_run_down()
			_charge_state = "fade"
		elif since > 0.3 and str(kit.get("current")) == "":
			_charge_state = "fade"  # cut short: no run down the arms
	else:
		_charge_level -= delta * 8.0
		if _charge_level <= 0.0:
			_charge.queue_free()
			_charge = null
			_charge_state = ""
			return
	_charge.global_position = _chest_point()
	var m: ShaderMaterial = _charge.material_override
	m.set_shader_parameter("strength", _charge_level + _charge_pop * 0.3)
	m.set_shader_parameter("spread", lerpf(0.5, 1.0, _charge_level))


# --- Cage wall, rock pylons under the dome (slice 9, 2026-11-14). Measured on SMITE 2's Odin, Ring of Spears: the
# wall is separate solid pieces with gaps, standing on a thin floor line, behind one short burst on the cast. So, when
# the ult's cage goes up: a wide band lights its edge and narrows into a thin line, and a rock pylon (a 1.4 m slab and
# two shorter ones) erupts under each wall panel, hot lime cooling to rock with a faint seam glow. A hit on a panel
# flashes its pylon; a broken panel's pylon shatters into chunks and its stretch of line goes dark. When the cage drops
# the pylons sink. The dome itself is left exactly as it is: nothing of the kit's or the cage's is hidden or edited.
# Off by default (cage_wall): shown old against new first.
const CAGE_LINE := preload("res://shaders/gorilla_cage_line.gdshader")
var cage_wall := false
var cage_pylons := 0 ## pylons raised, for the checks
var cage_cracked := 0 ## hits on a standing panel that flashed its pylon
var cage_shattered := 0 ## pylons shattered when their panel broke
var _cage: Dictionary = {}
var _cages_seen := {}


func _watch_cage(delta: float) -> void:
	if not cage_wall:
		return
	if _cage.is_empty():
		if elapsed - _ult_cast > 4.0:
			return
		for d in HexShield.live_domes():
			if not d.cage_all or d.panel_hp.is_empty() or _cages_seen.has(d.get_instance_id()):
				continue
			if Vector2(d.global_position.x - actor.global_position.x, d.global_position.z - actor.global_position.z).length() < 1.5:
				_cages_seen[d.get_instance_id()] = true
				_cage_begin(d)
				break
		return
	_cage.age += delta
	var line: MeshInstance3D = _cage.line
	var m: ShaderMaterial = line.material_override
	m.set_shader_parameter("age", _cage.age)
	var d: Variant = _cage.dome
	if _cage.end_age < 0.0 and not (is_instance_valid(d) and d.is_up()):
		_cage.end_age = 0.0
		for py in _cage.pylons:
			for sh in py.shards:
				sh.life = minf(sh.life, sh.age + 0.35)  # the pylons sink with the dome
	if _cage.end_age >= 0.0:
		_cage.end_age += delta
		m.set_shader_parameter("fade", clampf(1.0 - _cage.end_age / 0.3, 0.0, 1.0))
		if _cage.end_age >= 0.35:
			line.queue_free()
			_cage = {}
		return
	var hp: Array = d.panel_hp
	for i in mini(hp.size(), _cage.pylons.size()):
		var py: Dictionary = _cage.pylons[i]
		var now := float(hp[i])
		if now < py.hp and py.alive:
			if now <= 0.0:
				_pylon_shatter(py)
			else:
				_glow_at(py.at + Vector3.UP * 0.8, 1.0, 0.18, 0.8)
				cage_cracked += 1
		py.hp = now
	m.set_shader_parameter("panel_hp", _padded(hp))


func _padded(hp: Array) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	out.resize(16)
	for i in 16:
		out[i] = float(hp[i]) if i < hp.size() else 1.0
	return out


func _cage_begin(d: Node3D) -> void:
	var c := Vector3(d.global_position.x, actor.global_position.y, d.global_position.z)
	var r: float = d.radius
	var n: int = d.panel_hp.size()
	var line := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * (r * 2.0 + 1.6)
	line.mesh = plane
	var mat := ShaderMaterial.new()
	mat.shader = CAGE_LINE
	mat.render_priority = 3
	mat.set_shader_parameter("radius_m", r)
	mat.set_shader_parameter("panel_n", float(n))
	mat.set_shader_parameter("panel_hp", _padded(d.panel_hp))
	mat.set_shader_parameter("edge", _edge_color())
	line.material_override = mat
	_place(line, c + Vector3.UP * (LIFT + 0.02))
	var pylons := []
	for i in n:
		var a := -PI + (float(i) + 0.5) * TAU / float(n)  # the middle of panel i, as HexShield.panel_at counts them
		var out := Vector3(cos(a), 0.0, sin(a))
		var side := Vector3(-out.z, 0.0, out.x)
		var at := c + out * r
		var delay := 0.1 * float(i) / float(n)
		var shards := []
		for part in [[Vector3.ZERO, 1.4, out * 0.5], [side * 0.38 - out * 0.05, 0.8, (out + side).normalized()], [-side * 0.34 + out * 0.08, 0.55, (out - side).normalized()]]:
			_shard(at + part[0], part[2], float(part[1]) * randf_range(0.92, 1.08), 999.0, delay)
			var sh: Dictionary = _shards[-1]
			sh.keep = 0.14  # a faint seam glow stays while the cage stands
			shards.append(sh)
		_dust_at(at, 1.5, 0.6, 0.7, out * 1.2 + Vector3.UP * 0.3, 3.0)
		pylons.append({"shards": shards, "at": at, "out": out, "side": side, "hp": float(d.panel_hp[i]), "alive": true})
		cage_pylons += 1
	_cage = {"dome": d, "line": line, "pylons": pylons, "age": 0.0, "end_age": -1.0}


func _pylon_shatter(py: Dictionary) -> void:
	py.alive = false
	for sh in py.shards:
		sh.life = minf(sh.life, sh.age + 0.05)
	var at: Vector3 = py.at
	for k in 7:
		_chip(at + py.side * randf_range(-0.4, 0.4), py.out * randf_range(0.8, 2.6) + py.side * randf_range(-1.6, 1.6) + Vector3.UP * randf_range(3.0, 5.0))
	_glow_at(at + Vector3.UP * 0.7, 1.3, 0.22, 1.0)
	_dust_at(at, 1.8, 0.7, 0.8, py.out * 1.5, 3.0)
	cage_shattered += 1


# --- Team tint (slice 6, 2026-11-13). SMITE 2's own patch notes speak of "team coloration" on ability effects and
# tone it down three times (avoid overloading red, soften the indicators, keep the edge of the damage readable). So
# the team colour is an accent on the edges that mark reach, not a recolour: for a gorilla that is an enemy of the
# machine being played, the rim of the ring under it, the leading rim of each ripple and the cage edge take its team
# colour. Its cracks, glow, dust and chunks stay as they are. Your own gorilla and allied ones stay lime.
const LIME := Vector3(0.62, 1.0, 0.16)
var team_tint := false
var tinted := 0 ## ripples drawn with an enemy edge, for the checks


func _edge_color() -> Vector3:
	if not team_tint or not is_instance_valid(actor) or not is_inside_tree():
		return LIME
	var scene := get_tree().current_scene
	var viewer: Variant = scene.get("player") if scene != null else null
	if viewer == null or not is_instance_valid(viewer) or viewer == actor:
		return LIME
	var mine := str(viewer.get("team"))
	var theirs := str(actor.get("team"))
	if mine == theirs or not MatchTeams.COLOURS.has(mine) or not MatchTeams.COLOURS.has(theirs) or mine == "" or theirs == "":
		return LIME
	var c: Color = MatchTeams.COLOURS[theirs]
	return Vector3(c.r, c.g, c.b)


# --- Drive Slam dust (slice 5, 2026-11-12), key 3. Measured on SMITE 2's Geb, Roll Out, at 15 frames a second: a
# charge's trail is not on the floor. It is two tall plumes of brown dust flanking the path, about as tall as the body,
# with the middle left clear so the body reads, and rock chunks in the air; each plume hangs about 0.6 s. So here: one
# tall cloud about every 0.55 m of the drive on alternating sides, a small chunk kicked up with each, a low scrape puff
# at the kick-off, a skid puff thrown ahead on a miss, and a fan of dust thrown past the target on a hit (no cracks
# there: the grab slam that follows has them). Nothing is drawn on the floor. Additive: nothing of Codex's is hidden.
const DRIVE_GAP := 0.55 ## metres of drive between plumes
var drive_dust := false
var drive_puffs := 0 ## plumes left along the drives, for the checks
var drive_events: Array = [] ## "kick", "skid", "hit" in the order they fired
var _drive: Object = null
var _drive_on := false
var _drive_last := Vector3.ZERO
var _drive_acc := 0.0
var _drive_side := 1.0
var _chips: Array = []


func _watch_drive() -> void:
	var d: Variant = kit.get("drive")
	if d == null or d == _drive or not is_instance_valid(d) or not d.has_signal("phase_changed"):
		return
	_drive = d
	d.phase_changed.connect(_on_drive_phase)
	d.collision.connect(_on_drive_hit)


func _on_drive_phase(phase: String) -> void:
	_drive_on = false
	if not drive_dust or not is_instance_valid(actor) or not is_instance_valid(_drive):
		return
	var dir: Vector3 = _drive.direction
	var side := dir.cross(Vector3.UP).normalized()
	var feet: Vector3 = kit.feet()
	if phase == "brace":  # the kick-off: a low scrape thrown back
		_drive_cloud(feet - dir * 0.5, 1.2, 0.45, 0.7, -dir * 1.4 + Vector3.UP * 0.3, 4.0)
		drive_events.append("kick")
	elif phase == "drive":
		_drive_on = true
		_drive_last = actor.global_position
		_drive_acc = 0.3
	elif phase == "brake":  # a miss or a wall: the skid throws dust ahead
		for sgn in [-1.0, 1.0]:
			_drive_cloud(feet + dir * 0.9 + side * 0.45 * sgn, 1.6, 0.55, 0.75, dir * 3.2 + side * 0.8 * sgn + Vector3.UP * 0.5, 5.0)
		_chip(feet + dir * 0.8, dir * 2.4 + Vector3.UP * 3.2)
		drive_events.append("skid")


## While the drive runs: a tall cloud each DRIVE_GAP of ground covered, left then right, and a chunk with it.
func _drive_tick() -> void:
	if not _drive_on:
		return
	if not is_instance_valid(_drive) or String(_drive.phase) != "drive":
		_drive_on = false
		return
	var dir: Vector3 = _drive.direction
	_drive_acc += Vector3(actor.global_position.x - _drive_last.x, 0.0, actor.global_position.z - _drive_last.z).length()
	_drive_last = actor.global_position
	while _drive_acc >= DRIVE_GAP:
		_drive_acc -= DRIVE_GAP
		var side := dir.cross(Vector3.UP).normalized() * _drive_side
		var at: Vector3 = kit.feet() - dir * (0.4 + _drive_acc) + side * 0.8
		_drive_cloud(at, randf_range(1.8, 2.2), 0.62, 0.8, side * 1.3 + dir * 1.6 + Vector3.UP * 0.9, 4.0)
		_chip(at, side * randf_range(0.8, 2.0) - dir * randf_range(0.2, 1.0) + Vector3.UP * randf_range(2.6, 4.0))
		_drive_side = -_drive_side
		drive_puffs += 1


## The drive meets a target: dust fans out past it and a few chunks jump. No cracks, no light.
func _on_drive_hit(target: Node3D, _damage: float) -> void:
	_drive_on = false
	if not drive_dust or not is_instance_valid(target) or not is_instance_valid(actor) or not is_instance_valid(_drive):
		return
	var dir: Vector3 = _drive.direction
	var at := _floor_under(target) - dir * 0.5
	for i in 5:
		var out := dir.rotated(Vector3.UP, deg_to_rad(-56.0 + 28.0 * i))
		_drive_cloud(at + out * 0.4, randf_range(1.4, 1.9), 0.6, 0.75, out * randf_range(4.0, 5.5) + Vector3.UP * 0.5, 5.0)
	for i in 4:
		var fly := dir.rotated(Vector3.UP, randf_range(-0.9, 0.9))
		_chip(at, fly * randf_range(1.5, 3.5) + Vector3.UP * randf_range(2.8, 4.5))
	drive_events.append("hit")


## Drive dust is browner and darker than the slam dust, as Geb's trail is against its floor.
func _drive_cloud(at: Vector3, size: float, life: float, strength: float, vel: Vector3, drag: float) -> void:
	_dust_at(at, size, life, strength, vel, drag)
	_dust[-1].node.material_override.set_shader_parameter("dust", Color(0.50, 0.42, 0.31))


## One small rock chunk: it flies, lands, lies a moment and shrinks away.
func _chip(at: Vector3, vel: Vector3) -> void:
	var rk := _rock(Vector3(at.x, actor.global_position.y, at.z), 0, 1)
	rk.node.scale *= 0.6
	rk.vel = vel
	rk.age = 0.0
	rk.life = 1.0
	_chips.append(rk)


# --- The always-on ring and footfall dust (slice 4, 2026-11-12). Both stay under the gorilla; nothing travels on
# its own. Off by default: aura_disc stands in for the kit's pixel silverback ring (hidden, never freed), so it is
# shown old against new first. step_dust adds a small low puff where a hand or foot plants (the body's `step` signal).
const AURA := preload("res://shaders/gorilla_aura_disc.gdshader")
const AURA_EXTENT := 1.12
const STEP_BONES := {"hand_l": "lefthand", "hand_r": "righthand", "foot_l": "leftfoot", "foot_r": "rightfoot"}
var aura_disc := false
var step_dust := false
var steps := 0 ## footfall puffs drawn, for the checks
var aura_hidden := false ## the kit's pixel ring is hidden right now
var _disc: MeshInstance3D
var _disc_age := 0.0
var _last_pos := Vector3.ZERO
var _move_dir := Vector3.ZERO


func _watch_aura(delta: float) -> void:
	var old: Variant = kit.get("_aura")
	var has_old: bool = old != null and is_instance_valid(old)
	if not aura_disc:
		if is_instance_valid(_disc):
			_disc.queue_free()
			_disc = null
		if aura_hidden and has_old:
			old.visible = true
		aura_hidden = false
		return
	if has_old and old.visible:
		old.visible = false
		aura_hidden = true
	if not is_instance_valid(_disc):
		_disc = MeshInstance3D.new()
		var r: float = kit.aura_radius
		var plane := PlaneMesh.new()
		plane.size = Vector2.ONE * r * AURA_EXTENT * 2.0
		_disc.mesh = plane
		var mat := ShaderMaterial.new()
		mat.shader = AURA
		mat.render_priority = 3  # over the floor zones
		mat.set_shader_parameter("radius_m", r)
		mat.set_shader_parameter("extent", AURA_EXTENT)
		mat.set_shader_parameter("seed", randf() * 30.0)
		_disc.material_override = mat
		_disc.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		actor.add_child(_disc)  # rides the gorilla, as the pixel ring did, and hides with it
		_disc.global_position = kit.feet() + Vector3.UP * 0.03
		_disc_age = 0.0
	_disc_age += delta
	_disc.material_override.set_shader_parameter("age", _disc_age)
	_disc.material_override.set_shader_parameter("edge", _edge_color())


## One footfall of the walk: a small low puff where that hand or foot is, pushed a little back along the travel.
## The knuckles carry the weight, so a hand's puff is a little bigger than a foot's.
func _on_step(_clip: String, n: String) -> void:
	if not step_dust or not is_instance_valid(actor) or not actor.is_visible_in_tree():
		return
	var at: Variant = _bone_floor(String(STEP_BONES.get(n, "")))
	if at == null:
		return
	var hand := n.begins_with("hand")
	_dust_at(at, 1.2 if hand else 0.95, 0.45, 0.85 if hand else 0.65, -_move_dir * 0.6 + Vector3.UP * 0.3, 4.0)
	steps += 1


func _bone_floor(bone_name: String) -> Variant:
	var sk: Variant = _body.get("skeleton") if is_instance_valid(_body) else null
	if not (sk is Skeleton3D) or bone_name == "":
		return null
	for i in sk.get_bone_count():
		if sk.get_bone_name(i).to_lower() == bone_name:
			var at: Vector3 = sk.global_transform * sk.get_bone_global_pose(i).origin
			return Vector3(at.x, actor.global_position.y, at.z)
	return null


func _exit_tree() -> void:
	if is_instance_valid(_disc):
		_disc.queue_free()
	var old: Variant = kit.get("_aura") if is_instance_valid(kit) else null
	if aura_hidden and old != null and is_instance_valid(old):
		old.visible = true


## Where the two fists are, from the model's bones; without them, a guess in front of the feet.
func _fists(feet: Vector3, fwd: Vector3, right: Vector3) -> Array:
	var out: Array = []
	var sk: Variant = _body.get("skeleton") if is_instance_valid(_body) else null
	if sk is Skeleton3D:
		for bone_name in FIST_BONES:
			for i in sk.get_bone_count():
				if sk.get_bone_name(i).to_lower() == bone_name:
					out.append(sk.global_transform * sk.get_bone_global_pose(i).origin)
					break
	if out.size() == 2 and (out[0] - feet).length() < 3.0 and (out[1] - feet).length() < 3.0:
		return out
	return [feet + fwd * 0.9 - right * 0.5, feet + fwd * 0.9 + right * 0.5]


func _ring(at: Vector3, r: float, strength: float, life: float, travel: float) -> void:
	var node := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * r * 1.15 * 2.0
	node.mesh = plane
	var mat := ShaderMaterial.new()
	mat.shader = RING
	mat.set_shader_parameter("radius_m", r)
	mat.set_shader_parameter("life", life)
	mat.set_shader_parameter("travel", travel)
	var edge := _edge_color()
	mat.set_shader_parameter("edge", edge)
	if not edge.is_equal_approx(LIME):
		tinted += 1
	mat.set_shader_parameter("strength", strength)
	mat.set_shader_parameter("seed", randf() * 30.0)
	node.material_override = mat
	_place(node, Vector3(at.x, actor.global_position.y + LIFT + 0.01, at.z))
	_rings.append({"node": node, "age": 0.0, "life": life})


func _dust_at(at: Vector3, size: float, life: float, strength: float, vel: Vector3, drag: float) -> void:
	var q := MeshInstance3D.new()
	var mesh := QuadMesh.new()
	mesh.size = Vector2.ONE * size
	q.mesh = mesh
	var mat := ShaderMaterial.new()
	mat.shader = DUST
	mat.set_shader_parameter("seed", randf() * 50.0)
	mat.set_shader_parameter("life", life)
	mat.set_shader_parameter("strength", strength)
	q.material_override = mat
	_place(q, Vector3(at.x, at.y + size * 0.32, at.z))
	_dust.append({"node": q, "age": 0.0, "life": life, "vel": vel, "drag": drag})


func _rock(at: Vector3, i: int, count: int) -> Dictionary:
	var node := MeshInstance3D.new()
	node.mesh = _rock_mesh
	var mat := _rock_mat.duplicate() as StandardMaterial3D
	mat.emission = crack_color
	node.material_override = mat
	var s := randf_range(0.16, 0.32)
	node.scale = Vector3(s, s * randf_range(0.6, 1.0), s * randf_range(0.7, 1.2))
	var ang := TAU * (float(i) + randf() * 0.7) / float(count)
	var out := Vector3(cos(ang), 0, sin(ang))
	_place(node, at + out * randf_range(0.3, 0.9) + Vector3.UP * 0.1)
	node.rotation = Vector3(randf() * TAU, randf() * TAU, randf() * TAU)
	return {"node": node, "mat": mat, "vel": out * randf_range(1.6, 3.4) + Vector3.UP * randf_range(3.0, 5.5), "spin": Vector3(randf_range(-9, 9), randf_range(-9, 9), randf_range(-9, 9)), "ground": at.y + s * 0.3, "landed": false}


func _place(node: Node3D, at: Vector3) -> Node3D:
	if node is GeometryInstance3D:
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	node.top_level = true
	node.global_position = at
	return node


## Codex's painted fx draws its atlas ring (cell 3) on each beat. Muting sets that burst's opacity to zero; nothing is
## freed and its own timer still cleans it up. The targeting seal and every other decal are left alone.
func _mute_codex_ring() -> void:
	codex_muted += _mute_codex(Vector2(3, 0), hide_codex_ring)


## Mutes the atlas bursts of one cell that Codex's painted fx started this frame. Returns how many.
func _mute_codex(which: Vector2, enabled: bool) -> int:
	if not enabled:
		return 0
	var pf: Variant = kit.get("painted_fx")
	if pf == null or not is_instance_valid(pf):
		return 0
	var count := 0
	for row in pf.live:
		if row.alpha > 0.0 and row.time < 0.05 and not row.has("normal") and is_instance_valid(row.node):
			var cell: Variant = row.node.material_override.get_shader_parameter("cell")
			if cell is Vector2 and cell.is_equal_approx(which):
				row.alpha = 0.0
				row.node.visible = false
				count += 1
	if which.is_equal_approx(Vector2(1, 0)):
		crater_muted += count
	return count


## While the ult plays, the kit's pixel pulse ring (Fx3D "silverback_ring", grown by a tween) and its pixel impact puff
## are hidden the frame they appear. The always-on ring under the gorilla is parented to the player and is left alone.
func _hide_ult_stand_ins() -> void:
	var parent: Node = kit.world() if kit.has_method("world") else null
	if parent == null:
		return
	for i in range(parent.get_child_count() - 1, -1, -1):
		var c := parent.get_child(i)
		if not (c is Node3D) or c.has_meta("gorilla_fx_seen"):
			continue
		c.set_meta("gorilla_fx_seen", true)
		if c.global_position.distance_to(actor.global_position) > 2.5:
			continue
		if c is Fx3D.FlatFx or (c is AnimatedSprite3D and String(c.animation) == "impact_puff"):
			c.visible = false
			hidden_count += 1


func _process(delta: float) -> void:
	elapsed += delta
	if not is_instance_valid(kit) or not is_instance_valid(actor):
		return
	_watch_body()
	_watch_grab()
	_watch_fault(delta)
	_watch_aura(delta)
	_watch_drive()
	_drive_tick()
	_charge_tick(delta)
	_watch_cage(delta)
	var moved := Vector3(actor.global_position.x - _last_pos.x, 0.0, actor.global_position.z - _last_pos.z)
	if moved.length() > 0.001:
		_move_dir = moved.normalized()
	_last_pos = actor.global_position
	if hide_stand_ins and elapsed <= _ult_until:
		_hide_ult_stand_ins()
	for ring in _rings.duplicate():
		ring.age += delta
		if ring.age >= ring.life:
			ring.node.queue_free()
			_rings.erase(ring)
			continue
		ring.node.material_override.set_shader_parameter("age", ring.age)
	for d in _dust.duplicate():
		d.age += delta
		if d.age >= d.life:
			d.node.queue_free()
			_dust.erase(d)
			continue
		d.node.material_override.set_shader_parameter("age", d.age)
		d.node.global_position += d.vel * delta
		d.vel *= maxf(0.0, 1.0 - delta * d.drag)  # thrown dust slows fast
	for c in _chips.duplicate():
		c.age += delta
		var cn: MeshInstance3D = c.node
		if not c.landed:
			c.vel.y -= GRAVITY * delta
			cn.global_position += c.vel * delta
			cn.rotation += c.spin * delta
			if cn.global_position.y <= c.ground and c.vel.y < 0.0:
				cn.global_position.y = c.ground
				c.landed = true
		if c.age > c.life - 0.3:
			cn.scale *= maxf(0.0, 1.0 - delta * 6.0)
		if c.age >= c.life:
			cn.queue_free()
			_chips.erase(c)
	for sh in _shards.duplicate():
		sh.age += delta
		if sh.age < 0.0:
			continue
		var k := 1.0
		if sh.age < 0.1:
			var u: float = sh.age / 0.1
			k = (1.0 - (1.0 - u) * (1.0 - u) * (1.0 - u)) * (1.0 + 0.12 * sin(u * PI))
		elif sh.age > sh.life - 0.35:
			k = clampf((sh.life - sh.age) / 0.35, 0.0, 1.0)
		var sn: MeshInstance3D = sh.node
		var sb: Basis = sh.basis
		sn.visible = true
		sn.global_basis = sb * Basis.from_scale(Vector3(sh.h, sh.h * maxf(k, 0.02), sh.h))
		sn.global_position = sh.base + sb.y * (sh.h * k * 0.5 - 0.04)
		sh.mat.emission_energy_multiplier = maxf(0.85 * (1.0 - smoothstep(0.05, 0.6, sh.age)), float(sh.get("keep", 0.0)))
		if sh.age >= sh.life:
			sn.queue_free()
			_shards.erase(sh)
	for gl in _glows.duplicate():
		gl.age += delta
		gl.node.material_override.set_shader_parameter("age", gl.age)
		if gl.age >= gl.life:
			gl.node.queue_free()
			_glows.erase(gl)
	for row in _slams.duplicate():
		row.age += delta
		var t: float = row.age
		row.ground.material_override.set_shader_parameter("age", t)
		if row.light != null:
			row.light.light_energy = float(row.peak) * (1.0 - smoothstep(0.0, 0.2, t))
		for rock in row.rocks:
			var n: MeshInstance3D = rock.node
			rock.mat.emission_energy_multiplier = 0.9 * (1.0 - smoothstep(0.0, 0.35, t))
			if not rock.landed:
				rock.vel.y -= GRAVITY * delta
				n.global_position += rock.vel * delta
				n.rotation += rock.spin * delta
				if n.global_position.y <= rock.ground and rock.vel.y < 0.0:
					n.global_position.y = rock.ground
					if rock.vel.y < -3.0:
						rock.vel = Vector3(rock.vel.x * 0.35, -rock.vel.y * 0.25, rock.vel.z * 0.35)
						rock.spin *= 0.4
					else:
						rock.landed = true
			if t > row.life - 0.6:
				n.global_position.y -= delta * 0.25  # sink into the floor at the end
		if t >= row.life:
			row.ground.queue_free()
			if row.light != null:
				row.light.queue_free()
			for rock in row.rocks:
				rock.node.queue_free()
			_slams.erase(row)
