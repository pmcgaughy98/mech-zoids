extends Node3D
## Revision 4: inner-jungle boss bowls open toward mid and jungle approaches.
## Layout, sizes and travel targets remain proposals. Collision/navigation are authored locally.
const HALF_X := 110.0
const HALF_Z := 120.0
const LANE := [Vector2(0,96),Vector2(-4,64),Vector2(3,30),Vector2(0,0),Vector2(-3,-30),Vector2(4,-64),Vector2(0,-96)]
const LEFT := [Vector2(0,96),Vector2(-44,78),Vector2(-60,54),Vector2(-62,0),Vector2(-60,-54),Vector2(-44,-78),Vector2(0,-96)]
const RIGHT := [Vector2(0,96),Vector2(44,78),Vector2(60,54),Vector2(62,0),Vector2(60,-54),Vector2(44,-78),Vector2(0,-96)]
const GOLD_SITE := Vector2(-34,0)
const WYVERN_SITE := Vector2(34,0)
const PIT_RADIUS := 11.5
const CAMP_POINTS := [Vector2(-34,36),Vector2(34,36),Vector2(34,-36),Vector2(-34,-36)]
const BLUE := Color(0.2,0.6,1)
const RED := Color(1,0.28,0.19)
const GOLD := Color(1,0.62,0.12)
const ASSET_DIR := "res://art/environment/foundry_5v5/runtime/"
var vision = null # Explicit full visibility in the training foundation, no fake fog integration.
var features: Array = []
var blockers: Array = []
var sites: Dictionary = {}
var built: Node3D
var markers: Node3D
var nav: NavigationRegion3D
var nav_bake_ms := 0.0
var dressing_count := 0
var theme := "foundry"
var mats := {}
var module_cache := {}
var objective_models: Dictionary = {}
var connectors: Array = []
var objective_ports: Dictionary = {}

func _ready() -> void:
	markers = get_node("Markers")
	for c in markers.get_children(): c.free()
	built = Node3D.new(); built.name = "Built"; add_child(built)
	_mood()
	_box("Ground", Vector3(0,-0.3,0), Vector3(HALF_X*2,.6,HALF_Z*2), _floor_mat("jungle"), true, 2)
	# Boss bowls face the central jungle; backing walls remain on their outer-lane side.
	for side in [-1.0,1.0]:
		for end in [-1.0,1.0]:
			_obstacle(Vector3(32*side,1.95,21*end),Vector3(28,3.9,10))
			_obstacle(Vector3(31*side,1.7,60*end),Vector3(22,3.4,20))
			_obstacle(Vector3(17*side,1.6,91*end),Vector3(3,3.2,12),false)
			# Exterior lane buttresses guide the approach and make a small recess to scout from.
			_obstacle(Vector3(72*side,1.6,42*end),Vector3(8,3.2,12),false)
			var cross: Array=[Vector2(0,30*end),Vector2(12*side,34*end),Vector2(30*side,36*end),Vector2(49*side,34*end),Vector2(62*side,26*end)]
			connectors.append({"name":"Jungle loop","points":cross,"width":9.0})
			var home: Array=[Vector2(0,85*end),Vector2(14*side,83*end),Vector2(30*side,79*end),Vector2(49*side,73*end),Vector2(60*side,60*end)]
			connectors.append({"name":"Home service road","points":home,"width":8.0})
			var approach: Array=[Vector2(0,24*end),Vector2(12*side,24*end),Vector2(16*side,15*end),Vector2(24.8*side,9.2*end),Vector2(30*side,5*end)]
			connectors.append({"name":"Jungle boss approach","points":approach,"width":8.0})
			# A return loop joins the back of a camp to its home road, without a dead end.
			connectors.append({"name":"Camp return","points":[Vector2(10*side,36*end),Vector2(11*side,62*end),Vector2(14*side,80*end)],"width":7.0})
	for side in [-1.0,1.0]:
		connectors.append({"name":"Mid boss opening","points":[Vector2(0,0),Vector2(24*side,0),Vector2(30*side,0)],"width":12.0})
	for route in [LANE, LEFT, RIGHT]:
		_route(route,14.0,_floor_mat("paving"))
		_route(route,5.4,_floor_mat("dirt"),false,.016)
	for link in connectors:_route(link.points,link.width,_floor_mat("lane_grass"))
	# Map boundaries: higher behind players but short enough for the flat camera's horizon.
	for x in [-HALF_X+1,HALF_X-1]: _obstacle(Vector3(x,1.8,0),Vector3(2,3.6,HALF_Z*2),false)
	for z in [-HALF_Z+1,HALF_Z-1]: _obstacle(Vector3(0,1.8,z),Vector3(HALF_X*2,3.6,2),false)
	for t in [1.0,-1.0]:
		var team := "Blue" if t > 0 else "Red"
		var colour := BLUE if t > 0 else RED
		_disk(team+"Base",Vector2(0,102*t),17,colour.darkened(.65),.015)
		_ring(Vector2(0,108*t),9.5,colour)
		_marker(team+"Spawn",Vector2(0,108*t))
		_marker(team+"Core",Vector2(-6*t,96*t),2.5)
		_marker(team+"Tower",Vector2(-9*t,64*t),1.4)
		for lane_x in [-59.0,0.0,59.0]:
			var tower_pos := Vector2(lane_x,64*t)
			if lane_x == 0: tower_pos.x=-9*t
			_structure(team+"TowerDraft",tower_pos,colour)
		_structure(team+"CoreDraft",Vector2(-6*t,96*t),colour,2.1)
		for i in 2:
			var cp := Vector2(-34 if i==0 else 34,36*t)
			_marker(team+"Camp"+str(i+1),cp)
			_site(team+" Camp "+str(i+1),cp,5,colour,"camp")
		for i in 5:
			var p: Vector3=spawn_slots(team.to_lower())[i]
			_marker(team+"Spawn"+str(i+1),Vector2(p.x,p.z))
			_ring(Vector2(p.x,p.z),1.3,colour)
		_label(team.to_upper()+" BASE",Vector3(0,4,90*t),colour)
	_site("GOLD BEETLE / MINT YARD",GOLD_SITE,PIT_RADIUS,GOLD,"landmark")
	_site("WYVERN / REACTOR VAULT",WYVERN_SITE,PIT_RADIUS,Color(.66,.44,1),"landmark")
	_objective_court("gold",GOLD_SITE,GOLD)
	_objective_court("wyvern",WYVERN_SITE,Color(.66,.44,1))
	_boss("gold_beetle",GOLD_SITE,PI*.5)
	_boss("wyvern",WYVERN_SITE,-PI*.5)
	for x in [-62.0,0.0,62.0]:
		_label("WEST ROUTE" if x<0 else ("EAST ROUTE" if x>0 else "MID ROUTE"),Vector3(x,3.4,8),GOLD)
	# Distant industrial skyline, outside collision boundaries and navigation.
	for side in [-1.0,1.0]:
		for i in 12:
			var at := Vector3(side*(HALF_X+24+3*(i%3)),4+(i%4),-113+i*20)
			_box("Skyline",at,Vector3(5,at.y*2,7),_solid_mat(Color(.14,.19,.23)),false)
	_bake_nav()
	var camera := get_node("Camera")
	# The flat-camera arm needs non-walkable clearance beyond low perimeter walls. Do not force a close-up at the edge.
	camera.bounds = Vector2(HALF_X+14,HALF_Z+14)
	var layer := CanvasLayer.new(); layer.layer=5; layer.name="Minimap"; built.add_child(layer)
	var map: Control = load("res://scripts/map5v5/foundation_minimap.gd").new()
	map.arena=self; map.name="Map"; layer.add_child(map)

func spawn_slots(team: String) -> Array[Vector3]:
	var t:=1.0 if team=="blue" else -1.0
	var out: Array[Vector3]=[]
	for x in [0.0,-4.0,4.0,-8.0,8.0]: out.append(Vector3(x,0,108*t))
	return out

func _objective_court(key: String,centre: Vector2,colour: Color) -> void:
	var side:=signf(centre.x)
	objective_ports[key]={}
	# Open inner half-bowl: north/south jungle entries plus a broad central mid approach.
	for end in [-1.0,1.0]:
		var port:=centre+Vector2(-side*9.2,end*9.2)
		objective_ports[key]["north" if end<0 else "south"]=port
		_ring(port,1.3,colour)
		_marker(key.capitalize()+("North" if end<0 else "South"),port)
	objective_ports[key]["mid"]=centre+Vector2(-side*13,0)
	_marker(key.capitalize()+"Mid",objective_ports[key].mid)
	for i in 40:
		var angle:=TAU*(i+.5)/40.0
		var p:=centre+Vector2(cos(angle),sin(angle))*13.0
		if (p.x-centre.x)*side<0:continue # No ring wall across the mid/jungle-facing half.
		var is_door:=false
		for port: Vector2 in objective_ports[key].values():
			if p.distance_to(port)<4.5:is_door=true
		if is_door:continue
		var dimensions:=Vector3(2.25,3.6,1.8)
		var yaw: float=-angle-PI*.5
		blockers.append({"at":Vector3(p.x,1.8,p.y),"size":dimensions,"yaw":yaw})
		var wall:=_box("ObjectiveCourtWall",Vector3(p.x,1.8,p.y),dimensions,_solid_mat(Color(.7,.77,.84)),true)
		wall.rotation.y=yaw
		if i%5==0:
			var pillar:=_module("pillar",Vector3(p.x,0,p.y),Vector3(1.6,3.9,1.6))
			if pillar!=null:pillar.rotation.y=yaw
		var cap:=_box("ObjectiveGuide",Vector3(p.x,3.62,p.y),Vector3(2.2,.08,.12),_glow(colour),false)
		cap.rotation.y=yaw

func _mood() -> void:
	var foundry: Dictionary=load("res://scenes/moba3d/arena_blockout.gd").THEMES.foundry
	var grade: Dictionary=foundry.grade
	var env: Environment=get_node("WorldEnvironment").environment.duplicate()
	get_node("WorldEnvironment").environment=env
	env.ambient_light_color=foundry.ambient; env.ambient_light_energy=grade.ambient_energy
	env.tonemap_mode=Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure=grade.exposure;env.tonemap_white=grade.white
	env.glow_enabled=true;env.glow_intensity=grade.bloom;env.glow_hdr_threshold=grade.threshold
	env.glow_blend_mode=Environment.GLOW_BLEND_MODE_SOFTLIGHT
	env.adjustment_enabled=true;env.adjustment_contrast=grade.contrast;env.adjustment_saturation=grade.saturation
	# Longer map draft: atmospheric fog is lighter than 3v3; this is not gameplay fog of war.
	env.fog_density=.0018; env.fog_light_color=foundry.fog
	var sky: Sky=env.sky.duplicate(); env.sky=sky
	var sm: ProceduralSkyMaterial=sky.sky_material.duplicate(); sky.sky_material=sm
	sm.sky_top_color=foundry.sky_top; sm.sky_horizon_color=foundry.sky_horizon
	sm.ground_horizon_color=sm.sky_horizon_color
	get_node("Sun").light_energy=foundry.sun_energy
	get_node("Sun").light_color=foundry.sun

func _floor_mat(tile: String) -> StandardMaterial3D:
	if mats.has(tile): return mats[tile]
	var m:=StandardMaterial3D.new()
	m.albedo_texture=load("res://art/field/moba3d/arena/foundry/"+tile+".png")
	m.uv1_triplanar=true; m.uv1_world_triplanar=true; m.uv1_scale=Vector3.ONE*.39
	m.roughness=.85; m.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	mats[tile]=m
	return m

func _solid_mat(colour: Color) -> ShaderMaterial:
	var key:=colour.to_html()
	if mats.has(key): return mats[key]
	var m:=ShaderMaterial.new()
	m.shader=load("res://shaders/world/wall_fade.gdshader")
	m.set_shader_parameter("albedo_texture",load("res://art/field/moba3d/arena/foundry/cliff.png"))
	m.set_shader_parameter("albedo",colour)
	m.set_shader_parameter("tile_px",128.0)
	mats[key]=m
	return m

func _box(title: String, at: Vector3, dimensions: Vector3, material: Material, solid: bool, layer:=1) -> Node3D:
	var mesh:=BoxMesh.new(); mesh.size=dimensions; mesh.material=material
	var mi:=MeshInstance3D.new(); mi.name=title; mi.mesh=mesh; mi.position=at; built.add_child(mi)
	if solid:
		var body:=StaticBody3D.new(); body.collision_layer=layer; body.collision_mask=0; mi.add_child(body)
		var shape:=BoxShape3D.new(); shape.size=dimensions
		var cs:=CollisionShape3D.new(); cs.shape=shape; body.add_child(cs)
	return mi

func _route(route: Array, width: float, material: Material,edge_lights:=true,height:=.004) -> void:
	for i in route.size()-1:
		var a: Vector2=route[i]; var b: Vector2=route[i+1]; var mid: Vector2=(a+b)*.5
		var mi:=_box("Route",Vector3(mid.x,height,mid.y),Vector3(width,.018,a.distance_to(b)+.1),material,false)
		mi.rotation.y=-atan2((b-a).y,(b-a).x)+PI*.5
		if not edge_lights:continue
		# Thin luminous route edges in short repeated bars.
		var side: Vector2=Vector2(-(b-a).y,(b-a).x).normalized()
		for j in maxi(1,int(a.distance_to(b)/8)):
			var p: Vector2=a.lerp(b,(j+.5)/maxi(1,int(a.distance_to(b)/8)))
			for s in [-1.0,1.0]:
				var q: Vector2=p+side*s*(width*.5-.35)
				var strip:=_box("RouteLight",Vector3(q.x,.024,q.y),Vector3(.18,.025,2),_glow(GOLD.darkened(.2)),false)
				strip.rotation.y=mi.rotation.y

func _obstacle(at: Vector3, dimensions: Vector3, dress:=true) -> void:
	blockers.append({"at":at,"size":dimensions})
	var mi:=_box("Cover",at,dimensions,_solid_mat(Color(.7,.77,.84)),true)
	if dress:
		# Recess the housing behind module skins; collision retains the conservative outer envelope.
		(mi.mesh as BoxMesh).size=Vector3(dimensions.x-2,dimensions.y,dimensions.z-1.6)
		# Modules dress the authored island's faces without stretching a thin wall into a whole island.
		for side in [-1.0,1.0]:
			var n:=maxi(1,floori(dimensions.x/7))
			for i in n:
				var along: float=(i-(n-1)*.5)*6.8
				_module("wall",at+Vector3(along,-dimensions.y*.5,side*(dimensions.z*.5-.8)),Vector3(minf(dimensions.x,6),2.6,1.6))
		for side in [-1.0,1.0]:
			_module("pillar",at+Vector3(signf(at.x)*(dimensions.x*.5-1),-dimensions.y*.5,side*(dimensions.z*.5-1)),Vector3(2,3.8,2))

func _module(kind: String, at: Vector3, dimensions: Vector3) -> Node3D:
	var file:=ASSET_DIR+kind+".glb"
	if not ResourceLoader.exists(file): return null
	if not module_cache.has(kind): module_cache[kind]=load(file)
	var n: Node3D=module_cache[kind].instantiate(); n.position=at
	# Runtime copies are normalized to the module's documented meter envelope.
	var sizes: Dictionary={"wall":Vector3(6,2.6,1.6),"pillar":Vector3(2.4,4,2.4),"camp":Vector3(3.6,3.2,3.6),"landmark":Vector3(5.2,5,5.2)}
	n.scale=dimensions/sizes[kind]; built.add_child(n); dressing_count+=1
	for mi in n.find_children("*","MeshInstance3D",true,false):mi.visibility_range_end=110.0
	_module_materials(n,kind)
	return n

func _module_materials(node: Node,kind: String) -> void:
	if node is MeshInstance3D:
		for i in node.mesh.get_surface_count():
			var source: Material=node.mesh.surface_get_material(i)
			if not source is StandardMaterial3D:continue
			var key:="module_"+kind+str(source.get_instance_id())
			if not mats.has(key):
				var m:=ShaderMaterial.new();m.shader=load("res://shaders/map5v5/module_fade.gdshader")
				m.set_shader_parameter("base_texture",source.albedo_texture)
				m.set_shader_parameter("base_colour",source.albedo_color)
				m.set_shader_parameter("roughness_value",maxf(source.roughness,.55))
				m.set_shader_parameter("metallic_value",minf(source.metallic,.45))
				if source.emission_texture!=null:m.set_shader_parameter("emission_texture",source.emission_texture)
				m.set_shader_parameter("glow_colour",source.emission)
				mats[key]=m
			node.set_surface_override_material(i,mats[key])
	for child in node.get_children():_module_materials(child,kind)

func _marker(title: String, p: Vector2, radius:=0.0) -> void:
	var marker:=Marker3D.new(); marker.name=title; marker.position=Vector3(p.x,0,p.y)
	marker.set_meta("radius",radius); marker.set_meta("range",12.0); markers.add_child(marker)
	features.append({"name":title,"p":p})

func _structure(title: String,p: Vector2,colour: Color,factor:=1.0) -> void:
	var at:=Vector3(p.x,0,p.y)
	_box(title,at+Vector3.UP*1.4,Vector3(2.2,2.8,2.2)*factor,_solid_mat(colour),true)
	_box("StructureLight",at+Vector3.UP*3*factor,Vector3(1.9,.18,1.9)*factor,_glow(colour),false)

func _glow(colour: Color) -> StandardMaterial3D:
	var key:="glow"+colour.to_html()
	if mats.has(key):return mats[key]
	var m:=StandardMaterial3D.new(); m.albedo_color=colour; m.emission_enabled=true; m.emission=colour; m.emission_energy_multiplier=.6; mats[key]=m
	return m

func _disk(title: String,p: Vector2,radius: float,colour: Color,y: float) -> void:
	var mesh:=CylinderMesh.new(); mesh.top_radius=radius; mesh.bottom_radius=radius; mesh.height=.025; mesh.radial_segments=48; mesh.material=_glow(colour)
	var mi:=MeshInstance3D.new();mi.name=title;mi.mesh=mesh;mi.position=Vector3(p.x,y,p.y);built.add_child(mi)

func _ring(p: Vector2,radius: float,colour: Color) -> void:
	var mesh:=TorusMesh.new();mesh.inner_radius=radius-.12;mesh.outer_radius=radius+.12;mesh.rings=48;mesh.ring_segments=6;mesh.material=_glow(colour)
	var mi:=MeshInstance3D.new();mi.mesh=mesh;mi.position=Vector3(p.x,.055,p.y);mi.scale.y=.15;built.add_child(mi)

func _site(title: String,p: Vector2,radius: float,colour: Color,module: String) -> void:
	sites[title]={"p":p,"radius":radius}
	_disk(title,p,radius,Color(.17,.21,.24),.025);_ring(p,radius,colour)
	_label(title,Vector3(p.x,4.5,p.y),colour)
	# Landmark sits behind the reserved encounter floor, outside its two open approaches.
	# Keep both north/south contest entrances and their chase-camera arms free of tall dressing.
	var at:=Vector3(p.x+signf(p.x)*(radius+3),0,p.y) if module=="landmark" else Vector3(p.x,0,p.y+signf(p.y)*(radius+3))
	var dims:=Vector3(5.2,5,5.2) if module=="landmark" else Vector3(3.6,3.2,3.6)
	var proxy:=_box("InstallationCollision",at+Vector3.UP*dims.y*.5,dims,_solid_mat(colour),true)
	proxy.visible=_module(module,at,dims)==null

func _label(text: String,at: Vector3,colour: Color) -> void:
	var l:=Label3D.new();l.text=text;l.position=at;l.font_size=32;l.pixel_size=.006;l.modulate=colour;l.billboard=BaseMaterial3D.BILLBOARD_ENABLED;l.no_depth_test=false;built.add_child(l)

func _boss(kind: String,site: Vector2,yaw: float) -> void:
	var path:=ASSET_DIR+kind+".glb"
	if not ResourceLoader.exists(path):return
	var model: Node3D=load(path).instantiate()
	model.name="Objective_"+kind;model.position=Vector3(site.x,0,site.y);model.rotation.y=yaw
	built.add_child(model);objective_models[kind]=model
	load("res://scripts/moba3d/mech_look.gd").apply_model(model,false)
	# Deliberate local body footprint, not collision generated from the creature's wings or legs.
	var footprint:=Vector3(3.2,2.6,3.2) if kind=="gold_beetle" else Vector3(3.5,4.5,3.8)
	var collision:=_box("ObjectiveBody",Vector3(site.x,footprint.y*.5,site.y),footprint,_solid_mat(Color(.1,.1,.1)),true)
	collision.visible=false

func _bake_nav() -> void:
	var nm:=NavigationMesh.new();nm.geometry_parsed_geometry_type=NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	# Extra voxel clearance keeps diagonal nav corners outside the real 0.8m player sphere.
	nm.geometry_collision_mask=3;nm.agent_radius=1.25;nm.agent_height=3.25;nm.agent_max_climb=.25;nm.region_min_size=40
	var start:=Time.get_ticks_usec();var src:=NavigationMeshSourceGeometryData3D.new()
	NavigationServer3D.parse_source_geometry_data(nm,src,built)
	NavigationServer3D.bake_from_source_geometry_data(nm,src)
	nav_bake_ms=(Time.get_ticks_usec()-start)/1000.0
	nav=NavigationRegion3D.new();nav.name="Nav";nav.navigation_mesh=nm;built.add_child(nav)

# The shared training director calls this API; passive visual foundations have no destroyed state.
func set_structure_down(_title: String,_down: bool) -> void: pass
func set_tower_alert(_title: String,_amount: float) -> void: pass
func set_structure_off(_title: String,_off: bool) -> void: pass
