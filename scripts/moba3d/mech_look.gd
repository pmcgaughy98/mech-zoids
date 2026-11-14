extends RefCounted
## Mech look v3 (2026-11-09, look lane; v1 approved by Preston). Proposal, nothing here is canon. See docs/reference/moba-look-study-2026-11-09.md.
## apply_model(): duplicates each surface material (the GLB is untouched) and chains a fresnel rim, plus a team outline
## for enemies, through next_pass. material_overlay is left alone (hex shield, hit flash).
## grade(): returns a copy of an Environment with filmic tonemapping, a bloom that only catches emissives.

const RIM=preload("res://shaders/look/mech_rim.gdshader")
const OUTLINE=preload("res://shaders/look/mech_outline.gdshader")
const BODY=preload("res://shaders/look/mech_body.gdshader")
const ALLY_RIM=Color(0.92,0.94,1.0)  # v2: near-neutral; the v1 cool blue greyed warm albedos (rhino gold)
const ENEMY_RIM=Color(1.0,0.55,0.45)
const ENEMY_LINE=Color(0.95,0.12,0.10)

static var _mesh_cache:={}
static var _body_cache:={}
static var _line_mat:ShaderMaterial

## v3: each StandardMaterial3D becomes one mech_body ShaderMaterial with the rim built in: no extra draw for the rim.
## Materials are shared per (source material, team, albedo_scale), so six gorillas reuse the same 12 materials.
## outline=true also turns the team outline on for this mech (see set_outline: meant for the targeted enemy only).
## albedo_scale trims a too-bright texture toward the measured albedo target (value p50 about 0.34); 1.0 = as is.
static func apply_model(root:Node, enemy:=false, albedo_scale:=1.0, outline:=false) -> int:
	var count=0
	for mi in root.find_children("*","MeshInstance3D",true,false):
		var m:=mi as MeshInstance3D
		if m.mesh==null:continue
		for s in m.mesh.get_surface_count():
			var base:=m.get_active_material(s)
			if base==null:continue
			m.set_surface_override_material(s,_body(base,enemy,albedo_scale))
			count+=1
	if outline:set_outline(root,true)
	return count

static func _body(base:Material, enemy:bool, albedo_scale:float) -> Material:
	var key=[base,enemy,albedo_scale]
	if _body_cache.has(key):return _body_cache[key]
	var out:Material
	var b:=base as StandardMaterial3D
	if b==null:
		out=base.duplicate()  # unknown material: fall back to the v2 rim pass
		var rim:=ShaderMaterial.new()
		rim.shader=RIM
		rim.set_shader_parameter("rim_color",ENEMY_RIM if enemy else ALLY_RIM)
		_chain(out,rim)
	else:
		var sm:=ShaderMaterial.new()
		sm.shader=BODY
		var c:=b.albedo_color
		sm.set_shader_parameter("albedo",Color(c.r*albedo_scale,c.g*albedo_scale,c.b*albedo_scale,c.a))
		if b.albedo_texture:sm.set_shader_parameter("albedo_tex",b.albedo_texture)
		sm.set_shader_parameter("metallic",b.metallic)
		sm.set_shader_parameter("roughness",b.roughness)
		if b.roughness_texture:
			sm.set_shader_parameter("orm_tex",b.roughness_texture)
			sm.set_shader_parameter("use_orm",1.0)
		if b.emission_enabled:
			sm.set_shader_parameter("emission",b.emission)
			sm.set_shader_parameter("emission_energy",b.emission_energy_multiplier)
			if b.emission_texture:sm.set_shader_parameter("emission_tex",b.emission_texture)
		sm.set_shader_parameter("rim_color",ENEMY_RIM if enemy else ALLY_RIM)
		sm.resource_name=b.resource_name  # keeps the GLB surface name, so set_glow can find "Rhino drum ring glow"
		out=sm
	_body_cache[key]=out
	return out

## The team outline as a next_pass, per mech: turn it on for the targeted (or hovered) enemy only, the SMITE way.
## Every outlined mech adds one draw per surface, so outlining all enemies roughly doubled the frame (map lane, 2026-11-09).
static func set_outline(root:Node, on:bool):
	if _line_mat==null:
		_line_mat=ShaderMaterial.new()
		_line_mat.shader=OUTLINE
		_line_mat.set_shader_parameter("outline_color",ENEMY_LINE)
	for mi in root.find_children("*","MeshInstance3D",true,false):
		var m:=mi as MeshInstance3D
		if m.mesh==null:continue
		if on:
			if m.has_meta("look_plain"):continue
			var mats:=[]
			for s in m.mesh.get_surface_count():mats.append(m.get_surface_override_material(s))
			m.set_meta("look_plain",mats)
			m.mesh=smooth_outline_mesh(m.mesh)  # clears the overrides, so they are put back below
			for s in mats.size():
				var src:Material=mats[s]
				if src==null:continue
				var d:=src.duplicate() as Material
				_chain(d,_line_mat)
				m.set_surface_override_material(s,d)
		elif m.has_meta("look_plain"):
			var mats:Array=m.get_meta("look_plain")
			for s in mats.size():m.set_surface_override_material(s,mats[s])
			m.remove_meta("look_plain")
	if root.has_meta("look_flash_materials"):root.remove_meta("look_flash_materials")  # outline swapped the materials: set_flash re-copies from what is on the mech now

## 0 = off, 1 = white. Lazy per-mech copies keep flashes isolated without consuming one instance-uniform
## allocation per armor mesh. Reuses each copied material across that mech's surfaces; shields keep overlay.
static func set_flash(root:Node, amount:float):
	if not is_instance_valid(root):return
	_mech_copies(root)
	for material in root.get_meta("look_flash_materials"):material.set_shader_parameter("hit_flash",amount)

## Per-mech glow: sets emission energy on this mech's copy of the named surface only (default the rhino drum ring),
## so pulsing one rhino doesn't pulse every rhino. Uses the same per-mech copies as set_flash. The energy is kept in
## meta and re-applied if set_outline forces fresh copies. Returns how many surfaces it changed (0 = name not found).
static func set_glow(root:Node, energy:float, surface_name:="Rhino drum ring glow") -> int:
	if not is_instance_valid(root):return 0
	var glow:Dictionary=root.get_meta("look_glow",{})
	glow[surface_name]=energy
	root.set_meta("look_glow",glow)
	_mech_copies(root)
	return _apply_glow(root)

static func _apply_glow(root:Node) -> int:
	var n=0
	var glow:Dictionary=root.get_meta("look_glow",{})
	for material in root.get_meta("look_flash_materials",[]):
		if glow.has(material.resource_name):
			material.set_shader_parameter("emission_energy",glow[material.resource_name])
			n+=1
	return n

static func _mech_copies(root:Node):
	if not root.has_meta("look_flash_materials"):
		var copies: Dictionary={}
		for mi in root.find_children("*","MeshInstance3D",true,false):
			if mi.mesh==null:continue
			for s in mi.mesh.get_surface_count():
				var material: Material=mi.get_active_material(s)
				if not material is ShaderMaterial or material.shader!=BODY:continue
				if not copies.has(material):copies[material]=material.duplicate()
				mi.set_surface_override_material(s,copies[material])
		root.set_meta("look_flash_materials",copies.values())
		_apply_glow(root)

## Outline gap fix: averages the normals of vertices that share a position (hard plate edges are split vertices), and
## stores that averaged direction in CUSTOM0 relative to each vertex's own normal and tangent, so the skinned shader can
## rebuild it after the bones move. Adds a tangent if the GLB has none. Cached per mesh; the GLB file is untouched.
static func smooth_outline_mesh(src:Mesh) -> Mesh:
	if _mesh_cache.has(src):return _mesh_cache[src]
	var out:=ArrayMesh.new()
	for s in src.get_surface_count():
		var arrays:=src.surface_get_arrays(s)
		var verts:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var normals:PackedVector3Array=arrays[Mesh.ARRAY_NORMAL]
		var n:=verts.size()
		var sums:={}
		for i in n:
			var k:=Vector3i((verts[i]*2000.0).round())
			sums[k]=sums.get(k,Vector3.ZERO)+normals[i]
		var tangents=arrays[Mesh.ARRAY_TANGENT]
		if tangents==null or (tangents as PackedFloat32Array).size()!=n*4:
			tangents=PackedFloat32Array()
			tangents.resize(n*4)
			for i in n:
				var nn:=normals[i]
				var t:=(Vector3.UP if absf(nn.y)<0.9 else Vector3.RIGHT).cross(nn).normalized()
				tangents[i*4]=t.x;tangents[i*4+1]=t.y;tangents[i*4+2]=t.z;tangents[i*4+3]=1.0
			arrays[Mesh.ARRAY_TANGENT]=tangents
		var custom:=PackedFloat32Array()
		custom.resize(n*4)
		for i in n:
			var nn:=normals[i].normalized()
			var t:Vector3=Vector3(tangents[i*4],tangents[i*4+1],tangents[i*4+2]).normalized()
			var b:Vector3=nn.cross(t)*float(tangents[i*4+3])
			var sm:Vector3=sums[Vector3i((verts[i]*2000.0).round())]
			sm=sm.normalized() if sm.length()>0.0001 else nn
			custom[i*4]=sm.dot(t);custom[i*4+1]=sm.dot(b);custom[i*4+2]=sm.dot(nn);custom[i*4+3]=1.0
		arrays[Mesh.ARRAY_CUSTOM0]=custom
		var flags:int=src.surface_get_format(s) & (Mesh.ARRAY_FLAG_USE_8_BONE_WEIGHTS|Mesh.ARRAY_FLAG_USE_DYNAMIC_UPDATE)
		flags|=Mesh.ARRAY_CUSTOM_RGBA_FLOAT<<Mesh.ARRAY_FORMAT_CUSTOM0_SHIFT
		out.add_surface_from_arrays(src.surface_get_primitive_type(s),arrays,[],{},flags)
		out.surface_set_material(s,src.surface_get_material(s))
		out.surface_set_name(s,src.surface_get_name(s))
	_mesh_cache[src]=out
	return out

static func _chain(mat:Material, extra:Material):
	var last:=mat
	while last.next_pass!=null:last=last.next_pass
	last.next_pass=extra

static func grade(source:Environment) -> Environment:
	var e:=source.duplicate() as Environment
	e.tonemap_mode=Environment.TONE_MAPPER_FILMIC  # ACES skewed the faction green toward cyan (measured)
	e.tonemap_exposure=1.45  # v3: bodies lost the v2 haze lift (0.29 -> 0.20)
	e.tonemap_white=6.0
	e.ambient_light_energy=0.7  # keep the arena's warm ambient colour: sky ambient turned the green teal
	e.ssao_enabled=false  # v3: the map lane measured 0.69% of pixels changed in gl_compatibility; not worth shipping
	e.glow_enabled=true
	e.glow_intensity=0.55
	e.glow_bloom=0.0
	e.glow_hdr_threshold=1.05
	e.glow_blend_mode=Environment.GLOW_BLEND_MODE_SOFTLIGHT
	e.adjustment_enabled=true
	e.adjustment_saturation=1.1  # v3: 1.3 in v2 was compensating for fog haze the extra rim pass added; gone with the rim in the material
	e.adjustment_contrast=1.06
	return e
