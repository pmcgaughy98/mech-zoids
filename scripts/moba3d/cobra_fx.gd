extends Node3D
## Cobra ability effects, smooth (cobra effects lane, 2026-11-13). Visual only, an observer like bison_fx.gd: it edits
## no kit and no body, and deals nothing. Hood Gaze (slot 2) and Breach (slot 4) so far.
##
## BREACH CONTRACT (proposed): clip "Breach" (1.5 s, in place; the game moves the cobra at 8 m/s from go to stop):
##   wind 0.30, go 0.36, contact 0.42 (snout meets the near face), burst 0.55 (snout out of the far face: damage and
##   knock-back), clear 1.02, stop 1.05. Kit fields read at "wind", all optional:
##     breach_face: Vector3     the section's near face, centre, at floor level
##     breach_normal: Vector3   out of the near face, toward the cobra
##     breach_size: Vector3     width, height, thickness in metres
##     breach_gap_time: float   seconds after burst that allies can walk through
##   Without them the clip's own wall numbers are used: near face 2.163 m ahead, 2.6 m tall, 1.6 m thick.
##   kit cue "breach_hit" after it resolves burst; field breach_hits: Array (the enemies damaged and knocked back).
##
## CONTRACT (proposed to the game feel lane; the cobra has no kit code yet, so a launcher stub drives it):
##   body (MechModel3D) signal event(clip, name, damage), clip "Hood_Gaze" (r2 export, 0.95 s): gather 0.12, gaze 0.30,
##     release 0.62. The events carry all the timing; nothing else is needed for the cone.
##   kit signal cue(name): "gaze_hit" right after the kit resolves the cone at "gaze". Fields read then:
##     gaze_stunned: Array   enemies in the cone that were facing the cobra (they are held out of phase)
##     gaze_slowed: Array    the rest in the cone (the ground goes soft round their feet)
##   kit fields, read if present: gaze_range (m from the cobra's origin), gaze_angle (degrees, full width),
##     gaze_stun_time, gaze_slow_time (s). Defaults below are placeholders, the kit has no numbers yet.
##
## HOOD GAZE. Structure from Medusa's Petrify (SMITE 2, measured at 15 fps on three casts) and Bacchus's Belch cone
## (measured by the hippo lane), see docs/reference/cobra-fx-synthesis-2026-11-13.md. Nothing copied, structure only:
##   gather:  the two hood projector strips (cyan panels on the inner hood plates) and the neck core light up and
##            build to the shot; short primer needles flick out from the strips (Petrify: the caster lights up for the
##            whole charge, then thin needles start out from it)
##   gaze:    one short glint at the hood (Petrify's head burst, kept small: 0.14 s); the strips flare; the cone is
##            on the floor at once and its front, a curved sheet with height, sweeps out to the range in 0.1 s;
##            projector beams run from the strips to the front; enemies in it are marked the same frame (Petrify hit
##            at range in the same cell as the burst; no projectile)
##   hold:    grain runs out along the beams; the soft ground keeps rippling; the front shimmers
##   release: everything goes in 0.08 s (Belch: gone within a cell); the strips cool over 0.3 s; marks stay for the
##            stun and slow times
## PHASE PASS (2026-11-14). The kit's power is "pass-through, making solid matter go soft", and it left Medusa's
## statues out, so nothing turns to stone (a petrify pass on 2026-11-13 was dropped; Preston: "i didnt realize its
## powers were phase, so i guess may not need petrify"). What the gaze does to matter:
##   floor:   the ground it crosses goes soft: waves roll out across it from the hood and the floor behind them wavers
##            (screen-space warp), gold on the crests
##   front:   a soft membrane with height; the world seen through it wavers, with gold interference bands beating
##   stunned: held out of phase: its surface wobbles like it has gone soft, a gold rim and sliding bands run over it,
##            and a faint double of it drifts beside it; when the stun ends it snaps back solid with one short flash
##   slowed:  its feet sink into soft ground: ripples spread round them and the phase shimmer covers it to the ankles
## Colour: "gold" (Preston's pick, 2026-11-14: sulfur gold, yellower than the rhino's amber). "teal", the first pass,
## stays for comparison (P in the launcher). Never red (red marks enemies).
const GLOW := preload("res://shaders/cobra_glow.gdshader")
const FLOOR := preload("res://shaders/cobra_gaze_floor.gdshader")
const WALL := preload("res://shaders/cobra_gaze_wall.gdshader")
const RAY := preload("res://shaders/cobra_gaze_ray.gdshader")
const MARK := preload("res://shaders/cobra_gaze_mark.gdshader")
const SKIN := preload("res://shaders/cobra_phase_skin.gdshader")
const BFACE := preload("res://shaders/cobra_breach_face.gdshader")
const BWAVE := preload("res://shaders/cobra_breach_wave.gdshader")
## BREACH. The kit: "Softens a section of wall and drives through it." The section goes soft rather than breaking (the
## power is soft matter): its near, far and top faces waver like liquid, rings spread from where the snout goes in
## and comes out, a gold frame marks it while allies can pass, then it hardens with one short flash. A single wave
## runs out over the floor on the far side at burst (the knock-back), and each enemy hit gets the small burst.
const BREACH_WALL := Vector3(2.2, 2.6, 1.6) ## width (placeholder), height, thickness: the 5v5 wall from the clip export
const BREACH_AHEAD := 2.163 ## metres from the cobra to the near face at the start, from the clip export
const BREACH_GAP := 4.0 ## seconds after burst allies can pass: placeholder ("a few seconds")
const SNOUT_CONTACT := Vector3(0.079, 1.499, 1.740) ## model space at contact, from the r2 check log
const SNOUT_BURST := Vector3(0.079, 1.083, 2.099) ## model space at burst
const WAVE_R := 3.0 ## metres the far-side wave runs out
const WAVE_T := 0.3 ## seconds it takes
const SLOW_SKIN_H := 0.42 ## metres of shimmer on a slowed enemy (its feet in the soft ground)
const SNAP_BACK := 0.18 ## seconds: the stunned enemy snapping back solid at the end
const GAZE_RANGE := 6.0 ## metres, placeholder
const GAZE_ANGLE := 70.0 ## degrees across, placeholder
const STUN_TIME := 1.2 ## seconds, placeholder
const SLOW_TIME := 2.0 ## seconds, placeholder
const R_IN := 0.9 ## metres: the wedge starts under the hood (the hood is about 1 m ahead of the origin)
const SWEEP := 0.1 ## seconds for the front to reach the range
const WALL_H := 1.7 ## metres, the cobra's own height
const CHARGE := 0.18 ## gather to gaze in the clip
const OUT := 0.08 ## seconds to clear after release
const BEAMS := 3
const BEAM_H := [0.55, 1.1, 0.55] ## where each gaze line meets the front, metres up
const SIDES := 6
## socket -> [bone, rest position in model space (Godot xyz, head toward +Z)]. The strips are the cyan panels on the
## inner hood plates (found from the base texture: Bone_016 left, Bone_018 right, 1.0 to 1.4 m up); the core is the
## cyan strip on the neck front (Bone_004).
const SOCKETS := {
	"proj_l": ["Bone_016", Vector3(0.33, 1.20, 1.05)],
	"proj_r": ["Bone_018", Vector3(-0.245, 1.19, 1.055)],
	"hood": ["Bone_002", Vector3(0.045, 1.24, 1.12)],
	"core": ["Bone_004", Vector3(0.057, 0.95, 1.235)],
}
const PALETTES := {
	"gold": {"hot": Color(1.0, 0.98, 0.80), "warm": Color(0.92, 0.84, 0.18)},
	"teal": {"hot": Color(0.86, 1.0, 0.97), "warm": Color(0.10, 0.82, 0.74)},
}

@export var palette := "gold"
var kit: Node
var machine: Node3D
var body: Node3D
var log_rows: Array = []
var marks: Array = []
var needles: Array = [] ## primer needles and lock lines: transient tubes
var _sk: Skeleton3D
var _sockets := {}
var _clock := 0.0
var _mats: Array = []
var _strip := {} ## socket -> [MeshInstance3D, ShaderMaterial]
var _strip_amt := 0.0
var _strip_from := 0.0
var _strip_to := 0.0
var _strip_t := 0.0
var _strip_dur := 0.0
var _flash: MeshInstance3D
var _flash_mat: ShaderMaterial
var _flash_age := 9.0
var _root: Node3D
var _floor: MeshInstance3D
var _floor_mat: ShaderMaterial
var _wall: MeshInstance3D
var _wall_mat: ShaderMaterial
var _wall_ha := -1.0
var _rays: MeshInstance3D
var _ray_mat: ShaderMaterial
var _im: ImmediateMesh
var _gaze := {} ## the live cone: age, out (seconds since release, -1 while held), range, half angle
var _flash_pos: Variant = null ## where the glint sits when it is not at the hood (Breach: the snout on a face)
var _bp := {} ## Breach panels: "near", "far", "top" -> [MeshInstance3D, ShaderMaterial]
var _bwave: MeshInstance3D
var _bwave_mat: ShaderMaterial
var _breach := {} ## the live soft section
var _flash_scale := 1.0
var _halo_k := 1.0 ## the hood halo is the gaze's display; Breach keeps it lower


func setup(k: Node, m: Node3D) -> void:
	kit = k
	machine = m
	body = m.get("body")
	top_level = true
	global_transform = Transform3D.IDENTITY
	for s in ["proj_l", "proj_r", "core", "halo"]:
		var sizes := {"proj_l": Vector2(0.16, 0.5), "proj_r": Vector2(0.16, 0.5), "core": Vector2(0.14, 0.34),
			"halo": Vector2(2.1, 1.75)}
		var q := _quad(sizes[s])
		var mat := _mat(GLOW)
		## the halo: a soft ring just behind the hood with no core, sized to sit round the hood's outline. The strips
		## face forward, so from the chase camera behind the cobra the ring spilling round the hood's edge is what
		## shows the charge (Petrify: the caster's whole outline lights up while it charges).
		mat.set_shader_parameter("billboard_mode", 1 if s == "halo" else 2)
		mat.set_shader_parameter("core_size", 0.02 if s == "halo" else 0.5)
		if s == "halo":
			mat.set_shader_parameter("ring_r", 0.68)
		q.material_override = mat
		q.visible = false
		add_child(q)
		_strip[s] = [q, mat]
	_flash = _quad(Vector2(0.8, 0.42))
	_flash_mat = _mat(GLOW)
	_flash_mat.set_shader_parameter("billboard_mode", 1)
	_flash_mat.set_shader_parameter("core_size", 0.3)
	_flash_mat.set_shader_parameter("streak", 1.0)
	_flash.material_override = _flash_mat
	_flash.visible = false
	add_child(_flash)
	_root = Node3D.new()
	_root.name = "GazeCone"
	_root.visible = false
	add_child(_root)
	_floor = MeshInstance3D.new()
	_floor.mesh = PlaneMesh.new()
	_floor.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_floor_mat = _mat(FLOOR)
	_floor_mat.render_priority = 3
	_floor.material_override = _floor_mat
	_floor.position.y = 0.03
	_root.add_child(_floor)
	_wall = MeshInstance3D.new()
	_wall.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_wall_mat = _mat(WALL)
	_wall.material_override = _wall_mat
	_root.add_child(_wall)
	_im = ImmediateMesh.new()
	_rays = MeshInstance3D.new()
	_rays.mesh = _im
	_rays.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_rays)
	_ray_mat = _mat(RAY)
	for s in ["near", "far", "top"]:
		var bq := _quad(Vector2.ONE)
		var bm := _mat(BFACE)
		bq.material_override = bm
		bq.visible = false
		add_child(bq)
		_bp[s] = [bq, bm]
	_bwave = MeshInstance3D.new()
	var wplane := PlaneMesh.new()
	wplane.size = Vector2.ONE * (WAVE_R * 2.0 + 1.0)
	_bwave.mesh = wplane
	_bwave.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_bwave_mat = _mat(BWAVE)
	_bwave_mat.render_priority = 3
	_bwave.material_override = _bwave_mat
	_bwave.visible = false
	add_child(_bwave)
	set_palette(palette)
	if kit != null and kit.has_signal("cue"):
		kit.connect("cue", _on_cue)
	if body != null and body.has_signal("event"):
		body.connect("event", _on_event)
		if body.has_signal("action_finished"):
			body.connect("action_finished", _on_action_finished)
		_bind_sockets()
	else:
		push_warning("CobraFX: no 3D body with clip events on %s" % m.name)


func set_palette(p: String) -> void:
	if not PALETTES.has(p):
		return
	palette = p
	for mat in _mats:
		_tint(mat)
	for e in marks:
		if e.has("mat"):
			_tint(e["mat"])
		for pt in e.get("parts", []):
			_tint(pt[1])


func _tint(mat: ShaderMaterial) -> void:
	var c: Dictionary = PALETTES[palette]
	mat.set_shader_parameter("hot_col", c["hot"])
	mat.set_shader_parameter("warm_col", c["warm"])


func _mat(sh: Shader) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = sh
	_tint_new(m)
	_mats.append(m)
	return m


func _tint_new(m: ShaderMaterial) -> void:
	if PALETTES.has(palette):
		_tint(m)


func _bind_sockets() -> void:
	_sk = body.get("skeleton")
	if _sk == null:
		return
	var model: Node3D = body.call("model_root")
	var rel: Transform3D = model.global_transform.affine_inverse() * _sk.global_transform
	for n in SOCKETS:
		var i := _sk.find_bone(String(SOCKETS[n][0]))
		if i < 0:
			push_warning("CobraFX: no bone %s for %s" % [SOCKETS[n][0], n])
			continue
		var rest: Transform3D = rel * _sk.get_bone_global_rest(i)
		_sockets[n] = [i, rest.affine_inverse() * (SOCKETS[n][1] as Vector3)]


## World position of a socket on the moving body (the strips ride the hood plate bones as the hood flares).
func _socket(n: String) -> Vector3:
	if _sk == null or not _sockets.has(n):
		return machine.global_position + _forward() * 1.0 + Vector3.UP * 1.25
	var s: Array = _sockets[n]
	return _sk.global_transform * (_sk.get_bone_global_pose(int(s[0])) * (s[1] as Vector3))


func _forward() -> Vector3:
	var f := Vector3.FORWARD
	if body != null:
		var model: Node3D = body.call("model_root")
		f = model.global_transform.basis.z
	f.y = 0.0
	return f.normalized() if f.length() > 0.001 else Vector3.FORWARD


func _kit_num(field: String, fallback: float) -> float:
	var v: Variant = kit.get(field) if kit != null else null
	return float(v) if v != null else fallback


func _quad(size: Vector2) -> MeshInstance3D:
	var q := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = size
	q.mesh = quad
	q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return q


# --- events ---

func _on_event(clip: String, n: String, _damage: bool) -> void:
	if clip == "Breach":
		_breach_event(n)
		return
	if clip != "Hood_Gaze":
		return
	_halo_k = 1.0
	log_rows.append("event %s at %.3f" % [n, _clock])
	match n:
		"gather":
			_strips_to(0.9, CHARGE, 0.0)
			_primers()
		"gaze":
			_fire()
		"release":
			_release()


func _on_action_finished(clip: String) -> void:
	if clip == "Hood_Gaze" and not _gaze.is_empty() and float(_gaze["out"]) < 0.0:
		log_rows.append("cut short at %.3f" % _clock)
		_release()
	if clip == "Breach" and not _breach.is_empty() and float(_breach.get("clear_at", -1.0)) < 0.0:
		log_rows.append("breach cut short at %.3f" % _clock)
		_breach_clear()


func _on_cue(n: String) -> void:
	log_rows.append("cue %s at %.3f" % [n, _clock])
	if n == "breach_hit":
		var hits: Variant = kit.get("breach_hits") if kit != null else null
		var nh := 0
		if hits is Array:
			for t in hits:
				if t is Node3D and is_instance_valid(t):
					_burst_on(t)
					nh += 1
		log_rows.append("breach hit %d" % nh)
		return
	if n != "gaze_hit":
		return
	var stunned: Variant = kit.get("gaze_stunned") if kit != null else null
	var slowed: Variant = kit.get("gaze_slowed") if kit != null else null
	var ns := 0
	var nl := 0
	if stunned is Array:
		for t in stunned:
			if t is Node3D and is_instance_valid(t):
				_mark_stun(t)
				ns += 1
	if slowed is Array:
		for t in slowed:
			if t is Node3D and is_instance_valid(t):
				_mark_slow(t)
				nl += 1
	log_rows.append("marked stunned %d slowed %d" % [ns, nl])


## Strip glow eases from where it is to `to` over dur seconds.
func _strips_to(to: float, dur: float, _delay: float) -> void:
	_strip_from = _strip_amt
	_strip_to = to
	_strip_t = 0.0
	_strip_dur = maxf(dur, 0.001)


func _primers() -> void:
	var f := _forward()
	var ha := deg_to_rad(_kit_num("gaze_angle", GAZE_ANGLE)) * 0.5
	for i in 8:
		var side := "proj_l" if i % 2 == 0 else "proj_r"
		var sgn := 1.0 if side == "proj_l" else -1.0
		var a := sgn * randf_range(0.1, ha * 0.9)
		var d := f.rotated(Vector3.UP, a)
		d = (d + Vector3.UP * randf_range(-0.25, 0.3)).normalized()
		needles.append({"src": side, "dir": d, "len": randf_range(0.7, 1.4), "age": -0.012 * i, "life": 0.2,
			"r": 0.016, "phase": randf()})


func _fire() -> void:
	var rng := _kit_num("gaze_range", GAZE_RANGE)
	var ha := deg_to_rad(_kit_num("gaze_angle", GAZE_ANGLE)) * 0.5
	_gaze = {"age": 0.0, "out": -1.0, "range": rng, "ha": ha, "seed": randf() * 30.0}
	_strip_amt = 1.45
	_strips_to(0.75, 0.25, 0.0)
	_flash_age = 0.0
	_flash_pos = null
	_flash_scale = 1.0
	(_floor.mesh as PlaneMesh).size = Vector2.ONE * (rng * 2.0 + 0.6)
	_floor_mat.set_shader_parameter("range_m", rng)
	_floor_mat.set_shader_parameter("half_angle", ha)
	_floor_mat.set_shader_parameter("r_in", R_IN)
	_floor_mat.set_shader_parameter("seed", _gaze["seed"])
	_wall_mat.set_shader_parameter("seed", _gaze["seed"])
	if absf(ha - _wall_ha) > 0.001:
		_wall.mesh = _arc_mesh(ha)
		_wall_ha = ha
	_root.visible = true
	_place_root()
	log_rows.append("gaze range %.2f angle %.1f from %s facing %s" % [rng, rad_to_deg(ha * 2.0),
		machine.global_position.snapped(Vector3.ONE * 0.01), _forward().snapped(Vector3.ONE * 0.01)])


func _release() -> void:
	if not _gaze.is_empty() and float(_gaze["out"]) < 0.0:
		_gaze["out"] = 0.0
	_strips_to(0.0, 0.3, 0.0)


func _mark_stun(t: Node3D) -> void:
	_phase(t, -1.0, _kit_num("gaze_stun_time", STUN_TIME))
	# a small, short burst on it, and a lock line from the hood to it
	_burst_on(t)
	needles.append({"src": "hood", "target": t, "age": 0.0, "life": 0.3, "r": 0.03, "phase": randf()})


## A small, short burst on an enemy that was hit (0.55 m, 0.12 s).
func _burst_on(t: Node3D) -> void:
	var b := _quad(Vector2.ONE * 0.55)
	var bm := ShaderMaterial.new()
	bm.shader = GLOW
	bm.set_shader_parameter("billboard_mode", 1)
	bm.set_shader_parameter("core_size", 0.35)
	_tint(bm)
	b.material_override = bm
	add_child(b)
	b.global_position = t.global_position + Vector3.UP * 0.95
	marks.append({"kind": "burst", "node": b, "mat": bm, "target": t, "age": 0.0, "life": 0.12})


func _mark_slow(t: Node3D) -> void:
	var life := _kit_num("gaze_slow_time", SLOW_TIME)
	_phase(t, SLOW_SKIN_H, life)
	var mi := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * 2.0
	mi.mesh = plane
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var m := ShaderMaterial.new()
	m.shader = MARK
	m.render_priority = 3
	m.set_shader_parameter("seed", randf() * 30.0)
	_tint(m)
	mi.material_override = m
	add_child(mi)
	marks.append({"kind": "disc", "node": mi, "mat": m, "target": t, "age": 0.0, "life": life, "r": 0.9})


## Puts the enemy out of phase: copies of each of its model meshes (same mesh, skin and skeleton, added beside the
## original so they follow every pose) wearing cobra_phase_skin. `to_h` metres of it (a slowed enemy's feet), or the
## whole body when -1 (stunned: it also gets a faint double drifting beside it). The enemy's own materials and its
## material_overlay are left alone; the copies are freed when the mark ends.
func _phase(t: Node3D, to_h: float, life: float) -> void:
	var parts: Array = []
	var lo := INF
	var hi := -INF
	var whole := to_h < 0.0
	var seed := randf() * 30.0
	for node in t.find_children("*", "MeshInstance3D", true, false):
		var src := node as MeshInstance3D
		if src.mesh == null or src.mesh is PrimitiveMesh or not src.is_visible_in_tree() or src.has_meta("cobra_phase"):
			continue
		var box: AABB = src.global_transform * src.get_aabb()
		lo = minf(lo, box.position.y)
		hi = maxf(hi, box.end.y)
		var sc := maxf(src.global_transform.basis.get_scale().x, 0.001)
		for echo in ([0, 1] if whole else [0]):
			var c := MeshInstance3D.new()
			c.set_meta("cobra_phase", true)
			c.mesh = src.mesh
			c.skin = src.skin
			c.layers = src.layers
			c.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			var sm := ShaderMaterial.new()
			sm.shader = SKIN
			_tint(sm)
			sm.set_shader_parameter("seed", seed)
			sm.set_shader_parameter("push", 0.012 / sc)
			sm.set_shader_parameter("inv_scale", 1.0 / sc)
			sm.set_shader_parameter("echo", float(echo))
			c.material_override = sm
			src.add_sibling(c)
			c.transform = src.transform
			c.skeleton = src.skeleton
			parts.append([c, sm, src, echo])
	if parts.is_empty():
		return
	var side := _forward().cross(Vector3.UP).normalized()
	var base_off := lo - t.global_position.y
	var h := (hi - lo) + 0.05 if whole else to_h
	marks.append({"kind": "phase", "parts": parts, "target": t, "age": 0.0, "life": life, "base": base_off, "h": h,
		"whole": whole, "side": side})
	log_rows.append("phase on %s: %d copies, %.2f m" % [t.name, parts.size(), h])


# --- Breach ---

func _breach_event(n: String) -> void:
	log_rows.append("breach %s at %.3f" % [n, _clock])
	match n:
		"wind":
			_halo_k = 0.5
			_breach_begin()
			_strips_to(0.9, CHARGE, 0.0)
		"go":
			_strips_to(1.15, 0.06, 0.0)
		"contact":
			_breach_ring("near", SNOUT_CONTACT)
		"burst":
			_breach_ring("far", SNOUT_BURST)
			_strip_amt = 1.45
			_strips_to(0.6, 0.3, 0.0)
			if not _breach.is_empty():
				var b: Dictionary = _breach
				b["harden_at"] = float(b["age"]) + float(b["gap"])
				b["wave_at"] = b["age"]
				var nv: Vector3 = b["n"]
				_bwave.global_transform = Transform3D(Basis.looking_at(nv, Vector3.UP),
					(b["face"] as Vector3) - nv * (b["size"] as Vector3).z + Vector3.UP * 0.03)
		"clear":
			_breach_clear()


## At wind: where the section is (the kit's numbers, or the clip's), the three soft faces placed on it.
func _breach_begin() -> void:
	var f := _forward()
	var kf: Variant = kit.get("breach_face") if kit != null else null
	var kn: Variant = kit.get("breach_normal") if kit != null else null
	var ks: Variant = kit.get("breach_size") if kit != null else null
	var face: Vector3 = kf if kf is Vector3 else machine.global_position + f * BREACH_AHEAD
	var nv: Vector3 = kn if kn is Vector3 else -f
	nv.y = 0.0
	nv = nv.normalized() if nv.length() > 0.01 else -f
	var size: Vector3 = ks if ks is Vector3 else BREACH_WALL
	var w := size.x
	var h := size.y
	var t := size.z
	_breach = {"age": 0.0, "face": face, "n": nv, "size": size, "gap": _kit_num("breach_gap_time", BREACH_GAP),
		"near_at": -1.0, "far_at": -1.0, "clear_at": -1.0, "harden_at": -1.0, "wave_at": -1.0}
	var seed := randf() * 30.0
	var near: MeshInstance3D = _bp["near"][0]
	var far: MeshInstance3D = _bp["far"][0]
	var top: MeshInstance3D = _bp["top"][0]
	(near.mesh as QuadMesh).size = Vector2(w, h)
	(far.mesh as QuadMesh).size = Vector2(w, h)
	(top.mesh as QuadMesh).size = Vector2(w, t)
	near.global_transform = Transform3D(Basis.looking_at(-nv, Vector3.UP), face + Vector3.UP * h * 0.5 + nv * 0.02)
	far.global_transform = Transform3D(Basis.looking_at(nv, Vector3.UP),
		face - nv * t + Vector3.UP * h * 0.5 - nv * 0.02)
	top.global_transform = Transform3D(Basis.looking_at(Vector3.DOWN, nv), face - nv * t * 0.5 + Vector3.UP * (h + 0.02))
	for s in _bp:
		var m: ShaderMaterial = _bp[s][1]
		m.set_shader_parameter("size", Vector2(w, t) if s == "top" else Vector2(w, h))
		m.set_shader_parameter("hole", Vector2(0.5, 0.5) if s == "top" else Vector2(0.5, 0.42))
		m.set_shader_parameter("seed", seed + (7.0 if s == "far" else 0.0))
		m.set_shader_parameter("amount", 0.0)
		m.set_shader_parameter("frame_amt", 0.0)
		m.set_shader_parameter("churn", 0.0)
		m.set_shader_parameter("ring_age", 9.0)
		(_bp[s][0] as MeshInstance3D).visible = true
	log_rows.append("breach section at %s normal %s size %s gap %.1f" % [face.snapped(Vector3.ONE * 0.01),
		nv.snapped(Vector3.ONE * 0.01), size, float(_breach["gap"])])


## The snout meets a face: the ring starts there, the churn round it, and a small glint on the face.
func _breach_ring(side: String, snout: Vector3) -> void:
	if _breach.is_empty():
		_breach_begin()
	var model: Node3D = body.call("model_root") if body != null else null
	var wp: Vector3 = model.global_transform * snout if model != null else _socket("hood") + _forward() * 0.6
	var panel: MeshInstance3D = _bp[side][0]
	var sz: Vector2 = (panel.mesh as QuadMesh).size
	var l: Vector3 = panel.global_transform.affine_inverse() * wp
	var uv := Vector2(clampf(l.x / sz.x + 0.5, 0.05, 0.95), clampf(0.5 - l.y / sz.y, 0.05, 0.95))
	(_bp[side][1] as ShaderMaterial).set_shader_parameter("hole", uv)
	_breach[side + "_at"] = _breach["age"]
	var pn := panel.global_transform.basis.z.normalized()
	_flash_pos = wp - pn * (wp - panel.global_position).dot(pn) + pn * 0.12
	_flash_age = 0.0
	_flash_scale = 0.65 if side == "near" else 0.8
	log_rows.append("breach %s ring at uv %s, snout %s" % [side, uv.snapped(Vector2.ONE * 0.01),
		wp.snapped(Vector3.ONE * 0.01)])


func _breach_clear() -> void:
	_strips_to(0.0, 0.3, 0.0)
	if _breach.is_empty():
		return
	_breach["clear_at"] = _breach["age"]
	if float(_breach["harden_at"]) < 0.0:
		_breach["harden_at"] = _breach["age"]


func _tick_breach(delta: float) -> void:
	if _breach.is_empty():
		return
	var b: Dictionary = _breach
	b["age"] = float(b["age"]) + delta
	var age: float = b["age"]
	## the faces soften over wind to contact, then settle to a lower softness for the gap, then harden with one
	## short pass of the frame
	var amt := smoothstep(0.0, 0.12, age)
	var frame := 0.7 * amt
	var far_at: float = b["far_at"]
	if far_at >= 0.0:
		var s := smoothstep(0.3, 0.8, age - far_at)
		amt = lerpf(1.0, 0.6, s)
		frame = lerpf(0.7, 0.45, s)
	var done := false
	var ha: float = b["harden_at"]
	if ha >= 0.0 and age >= ha:
		var k := clampf((age - ha) / 0.2, 0.0, 1.0)
		amt *= (1.0 - k) * (1.0 - k)
		frame = frame * (1.0 - k) + 0.8 * sin(k * PI) * (1.0 - 0.5 * k)
		done = k >= 1.0
	var ca: float = b["clear_at"]
	var fade := 1.0 - smoothstep(0.0, 0.3, age - ca) if ca >= 0.0 else 1.0
	var churn := {}
	for s in ["near", "far"]:
		var at: float = b[s + "_at"]
		churn[s] = smoothstep(0.0, 0.05, age - at) * fade if at >= 0.0 else 0.0
	churn["top"] = 0.3 * maxf(churn["near"], churn["far"])
	for s in _bp:
		var m: ShaderMaterial = _bp[s][1]
		var at: float = b.get(s + "_at", -1.0)
		m.set_shader_parameter("amount", amt * (0.75 if s == "top" else 1.0))
		m.set_shader_parameter("frame_amt", frame)
		m.set_shader_parameter("churn", churn[s])
		m.set_shader_parameter("ring_age", age - at if at >= 0.0 else 9.0)
		m.set_shader_parameter("age", age)
	var wa: float = b["wave_at"]
	if wa >= 0.0:
		var tw := age - wa
		var k := clampf(tw / WAVE_T, 0.0, 1.0)
		_bwave.visible = k < 1.0
		_bwave_mat.set_shader_parameter("radius", WAVE_R * (1.0 - (1.0 - k) * (1.0 - k)))
		_bwave_mat.set_shader_parameter("amount", smoothstep(0.0, 0.03, tw) * (1.0 - k * k))
	if done:
		for s in _bp:
			(_bp[s][0] as MeshInstance3D).visible = false
		_bwave.visible = false
		log_rows.append("breach section hard again at %.3f" % _clock)
		_breach = {}


# --- per frame ---

func _process(delta: float) -> void:
	_clock += delta
	if machine == null or not is_instance_valid(machine):
		return
	_tick_strips(delta)
	_tick_flash(delta)
	_tick_gaze(delta)
	_tick_breach(delta)
	_tick_marks(delta)
	_build_tubes(delta)


func _tick_strips(delta: float) -> void:
	if _strip_dur > 0.0:
		_strip_t += delta
		var k := clampf(_strip_t / _strip_dur, 0.0, 1.0)
		## rising: ease out, so the 0.18 s charge shows early; falling: smooth
		var e := 1.0 - (1.0 - k) * (1.0 - k) if _strip_to > _strip_from else k * k * (3.0 - 2.0 * k)
		_strip_amt = lerpf(_strip_from, _strip_to, e)
		if k >= 1.0:
			_strip_dur = 0.0
	for s in _strip:
		var q: MeshInstance3D = _strip[s][0]
		var m: ShaderMaterial = _strip[s][1]
		var a := _strip_amt * (0.75 * _halo_k if s == "halo" else 1.0)
		q.visible = a > 0.01
		if q.visible:
			q.global_position = _socket("hood") - _forward() * 0.12 if s == "halo" else _socket(s)
			m.set_shader_parameter("amount", a)


func _tick_flash(delta: float) -> void:
	if _flash_age > 0.5:
		_flash.visible = false
		return
	_flash_age += delta
	var t := clampf(_flash_age / 0.14, 0.0, 1.0)
	_flash.visible = t < 1.0
	_flash.global_position = _flash_pos if _flash_pos != null else _socket("hood") + _forward() * 0.12
	_flash.scale = Vector3.ONE * lerpf(0.75, 1.15, t) * _flash_scale
	_flash_mat.set_shader_parameter("amount", 1.0 * (1.0 - t) * (1.0 - t))


func _place_root() -> void:
	var f := _forward()
	_root.global_transform = Transform3D(Basis.looking_at(-f, Vector3.UP), Vector3(machine.global_position.x,
		machine.global_position.y, machine.global_position.z))


func _tick_gaze(delta: float) -> void:
	if _gaze.is_empty():
		return
	_gaze["age"] = float(_gaze["age"]) + delta
	var age: float = _gaze["age"]
	var out: float = _gaze["out"]
	if out < 0.0 and age > 0.62:
		out = 0.0 ## the clip never sent release: end it
	if out >= 0.0:
		out += delta
		_gaze["out"] = out
	_place_root()
	var rng: float = _gaze["range"]
	var k := clampf(age / SWEEP, 0.0, 1.0)
	var front := lerpf(R_IN + 0.2, rng, 1.0 - (1.0 - k) * (1.0 - k))
	var arrive := 1.0 - smoothstep(SWEEP, SWEEP + 0.22, age) if k >= 1.0 else 0.0
	var fade := 1.0 if out < 0.0 else 1.0 - clampf(out / OUT, 0.0, 1.0)
	var hold := lerpf(1.0, 0.7, smoothstep(SWEEP, SWEEP + 0.25, age))
	_gaze["front"] = front
	_gaze["fade"] = fade
	_floor_mat.set_shader_parameter("front", front)
	_floor_mat.set_shader_parameter("age", age)
	_floor_mat.set_shader_parameter("arrive", arrive)
	_floor_mat.set_shader_parameter("amount", fade * hold)
	_wall.scale = Vector3(front, WALL_H * lerpf(0.55, 1.0, k), front)
	_wall_mat.set_shader_parameter("amount", fade * lerpf(1.0, 0.8, smoothstep(SWEEP, SWEEP + 0.25, age)))
	_wall_mat.set_shader_parameter("flash", arrive)
	_wall_mat.set_shader_parameter("age", age)
	_ray_mat.set_shader_parameter("age", age)
	if fade <= 0.0:
		_root.visible = false
		_gaze = {}
		log_rows.append("cone cleared at %.3f" % _clock)


func _tick_marks(delta: float) -> void:
	var keep: Array = []
	for e in marks:
		e["age"] = float(e["age"]) + delta
		var age: float = e["age"]
		var life: float = e["life"]
		var t: Node3D = e["target"] if is_instance_valid(e["target"]) else null
		if e["kind"] == "phase":
			if t == null or age >= life:
				for pt in e["parts"]:
					if is_instance_valid(pt[0]):
						(pt[0] as Node).queue_free()
				continue
			keep.append(e)
			var whole: bool = e["whole"]
			var fill: float = t.global_position.y + float(e["base"]) + float(e["h"])
			var land := 1.0 - clampf(age / 0.12, 0.0, 1.0) ## bright and loose as it lands
			## stunned: the last SNAP_BACK seconds it snaps back solid, one short flash; slowed: it just fades
			var out_k := clampf((age - (life - SNAP_BACK)) / SNAP_BACK, 0.0, 1.0) if whole \
				else smoothstep(life - 0.3, life, age)
			var snap := land * land + (sin(out_k * PI) * 1.4 if whole else 0.0)
			var wob := (0.028 if whole else 0.018) * (1.0 - out_k) + 0.05 * land
			var amt := (1.0 - out_k * out_k) * smoothstep(0.0, 0.04, age)
			var side: Vector3 = e["side"]
			var drift := side * (0.13 + 0.05 * sin(age * 6.0))
			for pt in e["parts"]:
				var c: MeshInstance3D = pt[0]
				var sm: ShaderMaterial = pt[1]
				var src: MeshInstance3D = pt[2]
				if not is_instance_valid(c) or not is_instance_valid(src):
					continue
				c.visible = src.is_visible_in_tree()
				var is_echo := int(pt[3]) == 1
				sm.set_shader_parameter("fill_y", fill)
				sm.set_shader_parameter("age", age)
				sm.set_shader_parameter("wobble", wob)
				sm.set_shader_parameter("snap", 0.0 if is_echo else snap)
				sm.set_shader_parameter("echo_off", drift if is_echo else Vector3.ZERO)
				## the double flickers and is gone before the snap back
				var flick := 0.75 + 0.25 * sin(age * 23.0)
				sm.set_shader_parameter("amount", amt * 0.45 * flick * (1.0 - out_k) if is_echo else amt)
			continue
		var node: MeshInstance3D = e["node"]
		var m: ShaderMaterial = e["mat"]
		if t == null and age < life - 0.15:
			e["life"] = age + 0.15 ## its target is gone: fade now
			life = e["life"]
		if age >= life:
			node.queue_free()
			continue
		keep.append(e)
		var at: Vector3 = t.global_position if t != null else node.global_position
		match e["kind"]:
			"disc":
				node.global_position = Vector3(at.x, at.y + 0.035, at.z)
				node.scale = Vector3.ONE * float(e["r"])
				m.set_shader_parameter("age", age)
				m.set_shader_parameter("amount", smoothstep(0.0, 0.05, age) * (1.0 - smoothstep(life - 0.3, life, age)))
			"burst":
				var bt := age / life
				node.global_position = at + Vector3.UP * 0.95
				node.scale = Vector3.ONE * lerpf(0.8, 1.2, bt)
				m.set_shader_parameter("amount", 1.2 * (1.0 - bt) * (1.0 - bt))
	marks = keep


## Rebuilds every tube this frame: primer needles, projector beams, lock lines.
func _build_tubes(delta: float) -> void:
	_im.clear_surfaces()
	var tubes: Array = [] ## [from, to, r0, r1, phase, alpha]
	var keep: Array = []
	for n in needles:
		n["age"] = float(n["age"]) + delta
		var age: float = n["age"]
		var life: float = n["life"]
		if age >= life:
			continue
		keep.append(n)
		if age < 0.0:
			continue
		var t := age / life
		var a := _socket(String(n["src"]))
		if n.has("target"):
			var tg: Node3D = n["target"] if is_instance_valid(n["target"]) else null
			if tg == null:
				continue
			var b: Vector3 = tg.global_position + Vector3.UP * 0.95
			tubes.append([a, b, float(n["r"]), float(n["r"]) * 0.6, float(n["phase"]), 1.0 - t * t])
		else:
			var grow := 1.0 - (1.0 - minf(t / 0.55, 1.0)) * (1.0 - minf(t / 0.55, 1.0))
			var b: Vector3 = a + (n["dir"] as Vector3) * float(n["len"]) * grow
			var a2: Vector3 = a + ((n["dir"] as Vector3) * float(n["len"]) * maxf(0.0, (t - 0.5) * 1.6))
			tubes.append([a2, b, float(n["r"]), float(n["r"]) * 0.4, float(n["phase"]), 1.0 - smoothstep(0.5, 1.0, t)])
	needles = keep
	if not _gaze.is_empty():
		var ha: float = _gaze["ha"]
		var front: float = _gaze.get("front", R_IN)
		var fade: float = _gaze.get("fade", 1.0)
		var age: float = _gaze["age"]
		var base := _root.global_transform
		for i in BEAMS:
			var ang := lerpf(-ha * 0.92, ha * 0.92, float(i) / float(BEAMS - 1))
			var src := "proj_l" if ang > 0.05 else ("proj_r" if ang < -0.05 else "hood")
			var local := Vector3(sin(ang) * front, float(BEAM_H[i]) * clampf(front / 2.5, 0.3, 1.0), cos(ang) * front)
			var b: Vector3 = base * local
			var pulse := 0.75 + 0.25 * sin(age * 21.0 + i * 1.7)
			var strength := fade * lerpf(0.9, 0.5, smoothstep(SWEEP, SWEEP + 0.25, age)) * pulse
			tubes.append([_socket(src), b, 0.012, 0.006, float(i) * 0.37, strength * 0.55])
	if tubes.is_empty():
		return
	_im.surface_begin(Mesh.PRIMITIVE_TRIANGLES, _ray_mat)
	for tb in tubes:
		_tube(tb[0], tb[1], tb[2], tb[3], tb[4], tb[5])
	_im.surface_end()


func _tube(a: Vector3, b: Vector3, r0: float, r1: float, phase: float, alpha: float) -> void:
	var d := b - a
	var length := d.length()
	if length < 0.02 or alpha <= 0.0:
		return
	var z := d / length
	var x := z.cross(Vector3.UP)
	if x.length() < 0.01:
		x = z.cross(Vector3.RIGHT)
	x = x.normalized()
	var y := z.cross(x).normalized()
	var c := Color(phase, 0.0, 0.0, clampf(alpha, 0.0, 1.0))
	for k in SIDES:
		var a0 := TAU * float(k) / float(SIDES)
		var a1 := TAU * float(k + 1) / float(SIDES)
		var n0 := x * cos(a0) + y * sin(a0)
		var n1 := x * cos(a1) + y * sin(a1)
		_v(a + n0 * r0, n0, Vector2(0.0, 0.0), c)
		_v(b + n0 * r1, n0, Vector2(1.0, 0.0), c)
		_v(b + n1 * r1, n1, Vector2(1.0, 1.0), c)
		_v(a + n0 * r0, n0, Vector2(0.0, 0.0), c)
		_v(b + n1 * r1, n1, Vector2(1.0, 1.0), c)
		_v(a + n1 * r0, n1, Vector2(0.0, 1.0), c)


func _v(p: Vector3, n: Vector3, uv: Vector2, c: Color) -> void:
	_im.surface_set_normal(n)
	_im.surface_set_uv(uv)
	_im.surface_set_color(c)
	_im.surface_add_vertex(p)


## The gaze front's sheet: a unit-radius arc, 1 m tall, across +-ha round +Z. UV.x across, UV.y up.
func _arc_mesh(ha: float) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var n := 32
	for i in n:
		var u0 := float(i) / float(n)
		var u1 := float(i + 1) / float(n)
		var a0 := lerpf(-ha, ha, u0)
		var a1 := lerpf(-ha, ha, u1)
		var p00 := Vector3(sin(a0), 0.0, cos(a0))
		var p10 := Vector3(sin(a1), 0.0, cos(a1))
		var p01 := p00 + Vector3.UP
		var p11 := p10 + Vector3.UP
		for q in [[p00, Vector2(u0, 0.0)], [p10, Vector2(u1, 0.0)], [p11, Vector2(u1, 1.0)],
				[p00, Vector2(u0, 0.0)], [p11, Vector2(u1, 1.0)], [p01, Vector2(u0, 1.0)]]:
			st.set_normal(-Vector3((q[0] as Vector3).x, 0.0, (q[0] as Vector3).z))
			st.set_uv(q[1])
			st.add_vertex(q[0])
	return st.commit()
