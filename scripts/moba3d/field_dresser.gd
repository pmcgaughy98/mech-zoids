extends Node3D
## Dresses the 3D test field to the look of the reel Preston sent (Claude, 2026-11-04): an open lime meadow with a
## dirt lane through it, a pond, billboard trees, bushes, rocks, flowers and tufts on the machines' pixel grid, and
## a ring of low-poly hills carrying the tree line, fading into blue-grey haze. All art is ours
## (tools/art/make_moba3d_field.py). Seeded, so the field is the same every run.

const DIR := "res://art/field/moba3d/"

@export var seed := 11
@export var texels_per_metre := 50.0
@export var field_radius := 24.0 ## open play area
@export var hill_inner := 27.0
@export var hill_outer := 70.0
@export var lane_half_width := 2.2
@export var pond_centre := Vector3(11.0, 0.0, -7.0)
@export var pond_radius := 4.5

var rng := RandomNumberGenerator.new()
var noise := FastNoiseLite.new()
var shadow_mesh: PlaneMesh


func _ready() -> void:
	rng.seed = seed
	noise.seed = seed
	noise.frequency = 0.9
	shadow_mesh = PlaneMesh.new()
	shadow_mesh.size = Vector2(1.0, 0.5)
	shadow_mesh.material = _flat_material(load(DIR + "shadow.png"), true)
	_build_hills()
	_scatter()


func _tri_material(tex: Texture2D) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_texture = tex
	m.uv1_triplanar = true
	m.uv1_world_triplanar = true
	m.uv1_scale = Vector3.ONE * (texels_per_metre / tex.get_width())
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	return m


func _flat_material(tex: Texture2D, transparent: bool) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_texture = tex
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	if transparent:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	return m


## Ground height: flat inside the field, rising into rolling hills toward the edge.
func height_at(x: float, z: float) -> float:
	var r := Vector2(x, z).length()
	var a := atan2(z, x)
	var rise := smoothstep(hill_inner, hill_inner + 14.0, r)
	return rise * (3.0 + 5.0 * (noise.get_noise_2d(cos(a) * 3.0, sin(a) * 3.0) + 1.0)) \
		+ smoothstep(hill_inner + 20.0, hill_outer, r) * 6.0


func _build_hills() -> void:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	st.set_smooth_group(-1)  # flat-shaded facets: the low-poly look
	var rings := 9
	var segs := 40
	var pts := []
	for i in rings + 1:
		var r := lerpf(hill_inner - 3.0, hill_outer, float(i) / rings)
		var row := []
		for j in segs:
			var a := TAU * (j + (0.5 if i % 2 else 0.0)) / segs
			var x := cos(a) * r
			var z := sin(a) * r
			row.append(Vector3(x, height_at(x, z), z))
		pts.append(row)
	for i in rings:
		for j in segs:
			var a: Vector3 = pts[i][j]
			var b: Vector3 = pts[i][(j + 1) % segs]
			var c: Vector3 = pts[i + 1][j]
			var d: Vector3 = pts[i + 1][(j + 1) % segs]
			for v in [a, c, b, b, c, d]:
				st.add_vertex(v)
	st.generate_normals()
	var mi := MeshInstance3D.new()
	mi.mesh = st.commit()
	mi.material_override = _tri_material(load(DIR + "grass_tile.png"))
	mi.name = "Hills"
	add_child(mi)


func _prop(file: String, pos: Vector3, with_shadow: float = 0.0) -> void:
	var tex: Texture2D = load(DIR + file)
	var s := Sprite3D.new()
	s.texture = tex
	s.pixel_size = 1.0 / texels_per_metre
	s.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	s.shaded = false
	s.position = pos + Vector3.UP * (tex.get_height() * 0.5 - 2.0) * s.pixel_size
	s.flip_h = rng.randf() < 0.5
	add_child(s)
	if with_shadow > 0.0:
		var sh := MeshInstance3D.new()
		sh.mesh = shadow_mesh
		sh.scale = Vector3(with_shadow, 1.0, with_shadow)
		sh.position = pos + Vector3.UP * 0.015
		add_child(sh)


func _open_spot(min_r: float, max_r: float, keep_clear := true) -> Vector3:
	for _try in 40:
		var a := rng.randf() * TAU
		var r := sqrt(lerpf(min_r * min_r, max_r * max_r, rng.randf()))
		var p := Vector3(cos(a) * r, 0.0, sin(a) * r)
		if keep_clear and (absf(p.x) < lane_half_width + 0.8 or p.length() < 5.0
				or p.distance_to(pond_centre) < pond_radius + 1.2):
			continue
		p.y = height_at(p.x, p.z)
		return p
	return Vector3.INF


func _scatter() -> void:
	var plan := [
		# file, count, min radius, max radius, shadow width (m)
		["tree_round.png", 7, 9.0, field_radius, 3.2], ["tree_pine.png", 4, 12.0, field_radius, 2.4],
		["bush.png", 16, 6.0, field_radius, 1.7], ["rock.png", 9, 6.0, field_radius, 1.2],
		["tuft.png", 140, 2.0, field_radius + 4.0, 0.0],
		["flower_white.png", 40, 3.0, field_radius, 0.0], ["flower_pink.png", 25, 3.0, field_radius, 0.0],
		["flower_violet.png", 25, 3.0, field_radius, 0.0],
		# the tree line on the hills
		["tree_round.png", 70, hill_inner + 1.0, hill_outer - 8.0, 3.2],
		["tree_pine.png", 50, hill_inner + 3.0, hill_outer - 4.0, 2.4],
	]
	for p in plan:
		for i in int(p[1]):
			var spot := _open_spot(p[2], p[3])
			if spot != Vector3.INF:
				_prop(p[0], spot, p[4])
