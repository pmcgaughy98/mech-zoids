@tool
extends Node3D
## First arena. Map design lane, 2026-11-04. A proposal for Preston, not canon.
## One lane sized for 3 v 3, a jungle on each side, and a paved plaza at the middle where the waves meet.
## Everything except the Player, Camera, Markers, WorldEnvironment and Sun is built from the numbers in this file
## each time the scene opens or runs, so the top-down sketch that tools/map/arena_check.gd writes always matches.
## For the machine scripts (game feel lane), 2026-11-04:
## - Markers/BlueSpawn, RedSpawn, BlueCore, RedCore, BlueTower, RedTower, BluePit, RedPit, BlueCamp1, BlueCamp2,
##   RedCamp1, RedCamp2, Plaza and Stream1 to Stream4 are Marker3D nodes saved in the scene, so they are in place
##   before _ready. build() moves them onto the numbers below. Each faces up its team's lane (-basis.z): blue toward
##   -z, red +z. Tower and core markers carry meta "team", "radius" and (towers) "range".
## - Solids (walls, rims, cliffs, rocks, towers, cores) are on WORLD_LAYER. The ground is one flat body on
##   GROUND_LAYER with its top at y = 0, there for the nav bake. Nothing is a ramp or a step.
## - Built/Nav is the NavigationRegion3D, baked on load from the bodies for a NAV_AGENT_RADIUS machine.
## - Built/Dressing holds what has no body: crystals, banners, rings on the ground, trees, bushes, tufts, lights.
##   Nothing in it taller than 0.5 m stands where a machine can walk (arena_check holds that).
## - set_structure_down(name, down) and set_tower_alert(name, amount) take the marker names (BlueTower, RedCore...).
## Built is freed and rebuilt by build(), so cache nothing under it before this node's _ready.
##
## Units are metres on the ground: x runs across the map, z along it. Blue's base is at +z and red's at -z, so
## blue's chase camera at yaw 0 looks up the lane toward red. Red's half is blue's half turned 180 degrees about
## the centre, so each team sees the same map from its own base.
## Art pass (2026-11-04): the ground is painted by shaders/world/ground.gdshader from these numbers; walls and rocks
## take the cliff tile with grass tops; tiles come from tools/map/make_arena_tiles.py at 50 texels per metre.
## The chase camera's frame has a level top edge at 4.45 m, so nothing above that ever shows: towers, cores and
## everything standing in the map top out under it, and trees stand past the cliffs, where the camera never goes.

const HALF_X := 42.0
const HALF_Z := 78.0
const TEXELS_PER_M := 50.0 ## the shared pixel grid
const TILE_PX := 32.0 ## the world tiles are 32 px, so one tile is 0.64 m

const LANE := [Vector2(0, 56), Vector2(0, 40), Vector2(-7, 20), Vector2(0, 0),
	Vector2(7, -20), Vector2(0, -40), Vector2(0, -56)] ## lane centre line, blue core to red core
const LANE_WIDTH := 14.0 ## wall face to wall face
const PATH_WIDTH := 4.4 ## the dirt path down the middle, as in field_test
const WALL_THICK := 1.2
const WALL_HEIGHT := 3.0 ## over a large machine (about 2 m), under the chase camera (4.45 m)
const RIM_HEIGHT := 1.5 ## the pit rim, low enough to see into
const EDGE_HEIGHT := 3.5 ## the cliffs round the map; low enough that the forest past them shows (was 6 in the greybox)
const PIECE := 2.0 ## walls are laid in pieces about this long, so an opening can cut any wall

const PLAZA_R := 13.0
const BASE_CENTRE := Vector2(0, 62)
const BASE_R := 15.0
const SPAWN := Vector2(0, 70)
const SPAWN_R := 6.0
const CORE := Vector2(0, 56)
const CORE_R := 2.5
const CORE_HEIGHT := 2.65 ## the stone; its crystal tops out at 4.35 m, under the camera's 4.45 m frame top
const TOWER := Vector2(0, 40)
const TOWER_R := 1.4
const TOWER_HEIGHT := 2.95 ## the stone; its crystal tops out at 4.3 m
const TOWER_RANGE := 12.0 ## placeholder until Preston sets numbers
const PIT := Vector2(25, 12) ## blue's side pit; what sits in it is open
const PIT_R := 6.0
const CAMPS := [Vector2(-27, 34), Vector2(27, 36)]
const CAMP_R := 3.0
const ROCKS := [Vector3(-20, 18, 3.5), Vector3(-32, 50, 4.0), Vector3(16, 42, 3.0),
	Vector3(35, 24, 2.5), Vector3(-17, 47, 2.5)] ## x, z, radius
const STREAM_HALF := 1.6 ## a shallow stream across both jungles at z = 0, looks only
const STREAMS := [Vector2(-35, 0), Vector2(-21, 0), Vector2(21, 0), Vector2(35, 0)] ## markers along it, for sound
const OPENINGS := [ ## gaps cut in any wall: x, z, radius. Blue's half; red's are these turned 180 degrees
	Vector3(0, 47, 7.5), # base gate onto the lane
	Vector3(-13, 54, 3.5), Vector3(13, 54, 3.5), # base side doors into each jungle
	Vector3(-10.7, 32.5, 3.5), # lane to the west jungle, under the tower
	Vector3(2.6, 24.5, 3.5), # lane to the east jungle
	Vector3(-13.6, 0, 4.0), # plaza door to the west jungle (turned, it is the east door)
	Vector3(25, 18.6, 3.0), Vector3(25, 5.4, 3.0), # pit doors, home side and stream side
]

const BLUE := Color(0.25, 0.45, 0.95)
const RED := Color(0.92, 0.3, 0.25)
const PAVING := Color(1.0, 0.94, 0.82) ## warm tint on the plaza, so it reads apart from the grey stone walls
const BLUE_PAVING := Color(0.84, 0.91, 1.0) ## each base's paving leans to its team colour
const RED_PAVING := Color(1.0, 0.86, 0.81)
const CAMP_COLOR := Color(1.0, 0.86, 0.35) ## camp rings
const PIT_COLOR := Color(1.0, 0.6, 0.22) ## side pit rings and the stripe on the rim
const BEACON_R := 4.5 ## the plaza beacon counts machines inside this (arena_beacon.gd)
const BEACON_COLOR := Color(1.0, 0.86, 0.45)
const BEACON_SCRIPT := preload("res://scenes/moba3d/arena_beacon.gd")
const STONE := Color(1.0, 0.96, 0.9) ## a warm lean on the grey cliff tile for walls and rims

## Light and mood. Applied to the scene's Sun and WorldEnvironment by build().
const SUN_COLOR := Color(1.0, 0.93, 0.8) ## warm sun
const SUN_ENERGY := 1.15
const AMBIENT := Color(0.66, 0.72, 0.84) ## cool fill, so the shadows go blue
const AMBIENT_ENERGY := 0.85
const SKY_TOP := Color(0.26, 0.48, 0.85)
const SKY_HORIZON := Color(0.78, 0.86, 0.93)
const FOG := Color(0.72, 0.8, 0.88)
const FOG_DENSITY := 0.004
const BASE_LIGHT := 2.0 ## energy of the team-coloured light over each core
const TOWER_LIGHT := 1.2

## Looks, picked with the "theme" export. "nature" is the stage 1 look. The others are three takes on Preston's ask for
## a "cyber futuristic technology" map (2026-11-04), for him to choose from; their tiles and props come from
## tools/map/make_theme_tiles.py into art/field/moba3d/arena/<theme>/. Layout, checks and camera rules are the same
## in every theme; only surfaces, props, light and colour change.
const THEMES := {
	"nature": {"dir": "", "sun": SUN_COLOR, "sun_energy": SUN_ENERGY, "ambient": AMBIENT, "ambient_energy": AMBIENT_ENERGY,
		"sky_top": SKY_TOP, "sky_horizon": SKY_HORIZON, "sky_ground": Color(0.2, 0.32, 0.18), "fog": FOG,
		"fog_density": FOG_DENSITY, "glow": 0.0, "ragged": 1.0, "line": Color(0, 0, 0, 0), "team_lines": false,
		"water": [Color(0.16, 0.42, 0.66), Color(0.23, 0.53, 0.78), Color(0.49, 0.78, 0.95), Color(0.84, 0.94, 1.0)],
		"water_glow": 0.0, "paving": PAVING, "blue_paving": BLUE_PAVING, "red_paving": RED_PAVING, "stone": STONE,
		"edge": Color(0.8, 0.82, 0.9), "rock": Color(0.95, 0.97, 1.05), "lip": Color(0, 0, 0, 0), "hazard": false,
		"gem_glow": 0.7, "light_scale": 1.0, "flowers": true},
	"circuit": {"dir": "circuit/", "sun": Color(1.0, 0.98, 0.95), "sun_energy": 1.0, "ambient": Color(0.7, 0.76, 0.86),
		"ambient_energy": 0.85, "sky_top": Color(0.35, 0.6, 0.92), "sky_horizon": Color(0.85, 0.92, 0.97),
		"sky_ground": Color(0.6, 0.65, 0.72), "fog": Color(0.82, 0.88, 0.94), "fog_density": 0.004, "glow": 1.6,
		"ragged": 0.0, "line": Color(0.37, 0.85, 1.0, 0.2), "team_lines": true,
		"water": [Color(0.1, 0.45, 0.6), Color(0.2, 0.7, 0.85), Color(0.6, 0.95, 1.0), Color(0.9, 1.0, 1.0)],
		"water_glow": 0.6, "paving": Color(1, 1, 1), "blue_paving": Color(0.86, 0.92, 1.0),
		"red_paving": Color(1.0, 0.88, 0.86), "stone": Color(1, 1, 1), "edge": Color(0.85, 0.88, 0.95),
		"rock": Color(0.95, 0.97, 1.0), "lip": Color(0.37, 0.85, 1.0, 0.25), "hazard": false, "gem_glow": 1.0,
		"light_scale": 1.0, "flowers": false},
	"neon": {"dir": "neon/", "sun": Color(0.55, 0.6, 1.0), "sun_energy": 0.35, "ambient": Color(0.32, 0.3, 0.5),
		"ambient_energy": 0.7, "sky_top": Color(0.03, 0.03, 0.1), "sky_horizon": Color(0.16, 0.1, 0.3),
		"sky_ground": Color(0.05, 0.04, 0.1), "fog": Color(0.18, 0.12, 0.32), "fog_density": 0.007, "glow": 2.5,
		"ragged": 0.0, "line": Color(0.6, 0.42, 1.0, 0.3), "team_lines": true,
		"water": [Color(0.25, 0.1, 0.5), Color(0.45, 0.25, 0.85), Color(0.7, 0.55, 1.0), Color(0.9, 0.85, 1.0)],
		"water_glow": 1.0, "paving": Color(1, 1, 1), "blue_paving": Color(0.8, 0.88, 1.0),
		"red_paving": Color(1.0, 0.82, 0.8), "stone": Color(1, 1, 1), "edge": Color(0.85, 0.85, 0.95),
		"rock": Color(1, 1, 1), "lip": Color(0.37, 0.85, 1.0, 0.3), "hazard": false, "gem_glow": 1.6,
		"light_scale": 1.6, "flowers": false},
	"foundry": {"dir": "foundry/", "sun": Color(1.0, 0.82, 0.62), "sun_energy": 1.3, "ambient": Color(0.5, 0.55, 0.7),
		"ambient_energy": 0.62, "sky_top": Color(0.22, 0.21, 0.34), "sky_horizon": Color(0.8, 0.46, 0.38),
		"sky_ground": Color(0.2, 0.15, 0.12), "fog": Color(0.46, 0.42, 0.48), "fog_density": 0.005, "glow": 1.8,
		"ragged": 0.3, "line": Color(1.0, 0.69, 0.19, 0.3), "team_lines": true,
		"water": [Color(0.12, 0.26, 0.28), Color(0.2, 0.36, 0.37), Color(0.42, 0.56, 0.55), Color(0.74, 0.8, 0.78)],
		"water_glow": 0.15, "paving": Color(1.0, 0.97, 0.92), "blue_paving": Color(0.84, 0.9, 1.0),
		"red_paving": Color(1.0, 0.85, 0.8), "stone": Color(0.9, 0.93, 1.0), "edge": Color(0.8, 0.84, 0.92),
		"rock": Color(0.88, 0.92, 1.0), "lip": Color(0, 0, 0, 0), "hazard": true, "gem_glow": 1.4,
		"light_scale": 1.2, "flowers": false, "structure": "machine", "camp": Color(0.95, 0.76, 0.15),
		"pit_light": Color(1.0, 0.55, 0.18),
		"detail": {"post": Color(0.62, 0.64, 0.72), "ao": 0.5, "grime": Color(0.78, 0.6, 0.48, 0.5),
			"pool": Color(1.0, 0.66, 0.3), "pool_energy": 0.8, "macro": 0.06, "bloom": 0.5, "contrast": 1.08,
			"saturation": 1.1}},
}

const ART := "res://art/field/moba3d/arena/"
const FIELD_ART := "res://art/field/moba3d/"
const FADE_SHADER := preload("res://shaders/world/wall_fade.gdshader") ## stand-up things fade where they hide the player
const GROUND_SHADER := preload("res://shaders/world/ground.gdshader")
const RING_SHADER := preload("res://shaders/world/range_ring.gdshader")
const SPRITE_SHADER := preload("res://shaders/world/sprite_fade.gdshader")
const DECAL_SHADER := preload("res://shaders/world/floor_decal.gdshader") ## the detail pass's floor marks
const DECALS := { ## floor marks in the theme's decals.png: atlas rects in pixels, drawn at the shared 50 a metre
	"arrow": Rect2(0, 0, 52, 32), "hazard": Rect2(64, 0, 64, 16), "hazard2": Rect2(64, 16, 64, 16),
	"oil": Rect2(128, 0, 32, 32), "drain": Rect2(160, 0, 32, 32), "patch": Rect2(192, 0, 32, 32),
	"scorch": Rect2(224, 0, 32, 32), "d07": Rect2(0, 32, 32, 16), "d12": Rect2(32, 32, 32, 16),
	"d21": Rect2(0, 48, 32, 16), "d34": Rect2(32, 48, 32, 16), "vent": Rect2(64, 32, 32, 16),
}
const MINIMAP_SCRIPT := preload("res://scenes/moba3d/arena_minimap.gd")
const VISION_SCRIPT := preload("res://scenes/moba3d/arena_vision.gd")
const WORLD_LAYER := 1 ## collision bit for everything solid (physics layer 1)
const GROUND_LAYER := 2 ## collision bit for the walkable ground (physics layer 2), kept off the world layer on purpose
const NAV_AGENT_RADIUS := 1.0 ## a large machine; smaller ones walk the same mesh, a little wide of the walls
const DRESS_SEED := 7
## Radians per second the tower and core heads turn. The sound lane's turret and core hum loops are pitched to it:
## tell them if it changes.
const HEAD_TURN := 0.8

@export_enum("nature", "circuit", "neon", "foundry") var theme := "foundry" ## the look; see THEMES. Preston picked foundry (2026-11-04)
@export var show_labels := false ## the greybox's floating names over each feature
@export var dressing := true ## trees, bushes, tufts, flowers and banners (structures, rings and lights stay)
@export var minimap := true ## the minimap, bottom right, while the game runs (Built/Minimap/Map)
@export var fog_of_war := true ## dim what the player's team can't see; the vision grid (can_see) runs either way

## Filled by build(); the check reads these.
var vision: Node = null ## Built/Vision while the game runs (scenes/moba3d/arena_vision.gd): can_see(team, pos)
var walls: Array = [] ## {c: Vector2, u: Vector2, half_len, half_thick, h}
var rocks: Array = [] ## {c: Vector2, r, h}
var features: Array = [] ## {name, kind, team, p: Vector2, r}
var holes: Array = [] ## every opening, both halves: Vector3(x, z, radius)
var nav_bake_ms := 0.0

var _root: Node3D
var _dress: Node3D
var _mats := {}
var _structures := {} ## marker name -> {base, gem, light, ring, p, down}
var th: Dictionary = {} ## THEMES[theme], set by build()
var _ground_mat: ShaderMaterial
var _pools: Array = [] ## floor points lit by the wall lamps (detail pass)


func _ready() -> void:
	build()


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	for s in _structures.values():
		if is_instance_valid(s.gem) and not s.get("off", false):
			s.gem.rotate_y(delta * HEAD_TURN)


func build() -> void:
	if _root:
		_root.free()
	walls.clear()
	rocks.clear()
	features.clear()
	holes.clear()
	_structures.clear()
	_mats.clear()
	th = THEMES.get(theme, THEMES["nature"])
	_root = Node3D.new()
	_root.name = "Built"
	add_child(_root)
	_dress = Node3D.new()
	_dress.name = "Dressing"
	_root.add_child(_dress)
	for o in OPENINGS:
		holes.append(o)
		holes.append(Vector3(-o.x, -o.y, o.z))
	var entry: Vector2 = (LANE[2] - LANE[3]).normalized() * (PLAZA_R + WALL_THICK * 0.5)
	holes.append(Vector3(entry.x, entry.y, LANE_WIDTH * 0.5 + 0.2)) # where the lane meets the plaza
	holes.append(Vector3(-entry.x, -entry.y, LANE_WIDTH * 0.5 + 0.2))
	_mood()
	_ground()
	_lane_walls()
	_ring(Vector2.ZERO, PLAZA_R + WALL_THICK * 0.5, WALL_HEIGHT, _fade("cliff", th.stone, true))
	for t in [1.0, -1.0]:
		var col := BLUE if t > 0 else RED
		_ring(BASE_CENTRE * t, BASE_R, WALL_HEIGHT, _fade("cliff", th.stone, true, col, 1.9, 2.3))
		_ring(PIT * t, PIT_R + WALL_THICK * 0.5, RIM_HEIGHT, _fade("cliff", th.stone, true, PIT_COLOR, 0.9, 1.1))
	_edges()
	for r in ROCKS:
		_rock(Vector2(r.x, r.y), r.z, WALL_HEIGHT)
		_rock(Vector2(-r.x, -r.y), r.z, WALL_HEIGHT)
	_features()
	if dressing:
		_dress_world()
	if th.has("detail"): # 2026-11-04 quality pass: posts and lamps, floor marks, baked contact shade and lamp light
		_wall_posts()
		_decals()
		_floor_map()
	vision = null
	if not Engine.is_editor_hint():
		vision = VISION_SCRIPT.new()
		vision.name = "Vision"
		vision.arena = self
		_root.add_child(vision)
	if minimap and not Engine.is_editor_hint():
		var layer := CanvasLayer.new()
		layer.name = "Minimap"
		layer.layer = 5
		var map: Control = MINIMAP_SCRIPT.new()
		map.name = "Map"
		map.arena = self
		layer.add_child(map)
		_root.add_child(layer)
	_place_markers()
	_bake_nav()


## The structure names are the marker names: BlueTower, RedTower, BlueCore, RedCore.
## Sound contract: the sound lane's MapAudio hangs a hum under every node named ...TowerGem or ...CoreGem and stops it
## on that node's visibility_changed, so keep those names and keep hiding (or freeing) the head here.
## Down: the crystal, its light and the range ring go; the stump stays, darkened, and keeps its body.
func set_structure_down(structure: String, down: bool) -> void:
	var s: Dictionary = _structures.get(structure, {})
	if s.is_empty():
		return
	s.down = down
	s.gem.visible = not down
	s.light.visible = not down
	if s.get("trim"):
		s.trim.visible = not down
	if s.ring:
		s.ring.visible = not down
	if s.base.has_meta("down"): # foundry: the wrecked body and its own hull
		var pair: Array = s.base.get_meta("down" if down else "up")
		s.base.mesh = pair[0]
		var cs: CollisionShape3D = s.base.find_children("*", "CollisionShape3D", true, false)[0]
		cs.shape = pair[1]
		if vision:
			for i in s.base.mesh.get_surface_count():
				vision.track(s.base.mesh.surface_get_material(i))
		return
	s.base.material_override = _fade("cliff", Color(0.42, 0.4, 0.4)) if down else null
	if vision and s.base.material_override:
		vision.track(s.base.material_override)


## Every material that dims under the fog of war (the shaders that include fog.gdshaderinc), for Built/Vision.
func fog_materials() -> Array:
	var out := []
	var stack: Array = [_root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		stack.append_array(n.get_children())
		var m: Material = null
		if n is MeshInstance3D:
			m = n.material_override if n.material_override else (n.mesh.surface_get_material(0) if n.mesh else null)
		elif n is MultiMeshInstance3D and n.multimesh and n.multimesh.mesh:
			m = n.multimesh.mesh.surface_get_material(0)
		if m is ShaderMaterial and m.shader in [FADE_SHADER, GROUND_SHADER, SPRITE_SHADER, DECAL_SHADER] and not out.has(m):
			out.append(m)
	return out


## Towers and cores for the minimap: {name, team, kind ("tower" or "core"), p: Vector2, down}.
func structure_list() -> Array:
	var out := []
	for k in _structures:
		var s: Dictionary = _structures[k]
		out.append({"name": k, "team": "blue" if k.begins_with("Blue") else "red",
			"kind": "core" if k.ends_with("Core") else "tower", "p": s.p, "down": s.down})
	return out


## 0 to 1: turns that tower's range ring to the alert red while it aims at the player.
## A structure the plaza beacon has switched off (game feel's MatchStructure decides when): its head stops
## turning, its team light drops to 15% and its range ring hides. Looks only. A fallen structure stays fallen.
func set_structure_off(structure: String, off: bool) -> void:
	var s: Dictionary = _structures.get(structure, {})
	if s.is_empty() or s.down:
		return
	s["off"] = off
	if not s.has("light_energy"):
		s["light_energy"] = s.light.light_energy
	s.light.light_energy = s.light_energy * (0.15 if off else 1.0)
	if s.ring:
		s.ring.visible = not off


func set_tower_alert(structure: String, amount: float) -> void:
	var s: Dictionary = _structures.get(structure, {})
	if not s.is_empty() and s.ring:
		s.ring.mesh.material.set_shader_parameter("alert", clampf(amount, 0.0, 1.0))


func _mood() -> void:
	var sun := get_node_or_null("Sun") as DirectionalLight3D
	if sun:
		sun.light_color = th.sun
		sun.light_energy = th.sun_energy
		sun.shadow_enabled = true
		sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL # one map over 48 m: about a texel a pixel
		sun.directional_shadow_max_distance = 48.0
		sun.shadow_bias = 0.04
		sun.shadow_normal_bias = 1.2
		sun.light_angular_distance = 0.0 # hard edges, like the pixel art
	var we := get_node_or_null("WorldEnvironment") as WorldEnvironment
	if we == null or we.environment == null:
		return
	var e := we.environment
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = th.ambient
	e.ambient_light_energy = th.ambient_energy
	e.fog_enabled = true
	e.fog_light_color = th.fog
	e.fog_density = th.fog_density
	e.fog_sky_affect = 0.5
	if e.sky and e.sky.sky_material is ProceduralSkyMaterial:
		var sky: ProceduralSkyMaterial = e.sky.sky_material
		sky.sky_top_color = th.sky_top
		sky.sky_horizon_color = th.sky_horizon
		sky.ground_horizon_color = th.sky_horizon
		sky.ground_bottom_color = th.sky_ground
	var post: Dictionary = th.get("detail", {})
	e.glow_enabled = post.has("bloom")
	if post.has("bloom"): # lamps, vents, the pit grate and team lights bloom a little; the small levels keep it tight
		e.glow_intensity = post.bloom
		e.glow_strength = 1.0
		e.glow_bloom = 0.0
		e.glow_hdr_threshold = 0.9
		e.glow_blend_mode = Environment.GLOW_BLEND_MODE_ADDITIVE
		var levels := [1.0, 0.7, 0.35, 0.0, 0.0, 0.0, 0.0]
		for i in 7:
			e.set_glow_level(i, levels[i])
	e.adjustment_enabled = post.has("contrast")
	if post.has("contrast"):
		e.adjustment_contrast = post.contrast
		e.adjustment_saturation = post.saturation


func _ground() -> void:
	var m := ShaderMaterial.new()
	m.shader = GROUND_SHADER
	_ground_mat = m
	for k in ["lane_grass", "jungle", "dirt", "paving"]:
		m.set_shader_parameter(k + "_tex", load(_art(k)))
	m.set_shader_parameter("pit_tex", load(_art("pit_floor")))
	m.set_shader_parameter("glow_energy", th.glow)
	m.set_shader_parameter("ragged", th.ragged)
	m.set_shader_parameter("line_color", th.line)
	if th.team_lines:
		m.set_shader_parameter("blue_line", Color(BLUE.lerp(Color.WHITE, 0.2), 0.35))
		m.set_shader_parameter("red_line", Color(RED.lerp(Color.WHITE, 0.2), 0.35))
	for i in 4:
		m.set_shader_parameter(["water_deep", "water_mid", "water_light", "water_foam"][i], th.water[i])
	m.set_shader_parameter("water_glow", th.water_glow)
	m.set_shader_parameter("texels_per_metre", TEXELS_PER_M)
	m.set_shader_parameter("tile_px", TILE_PX)
	var pts := PackedVector2Array(LANE)
	while pts.size() < 8:
		pts.append(Vector2.ZERO)
	m.set_shader_parameter("lane_pts", pts)
	m.set_shader_parameter("lane_count", LANE.size())
	m.set_shader_parameter("path_half", PATH_WIDTH * 0.5)
	m.set_shader_parameter("lane_half", LANE_WIDTH * 0.5)
	m.set_shader_parameter("plaza_r", PLAZA_R)
	m.set_shader_parameter("plaza_tint", th.paving)
	m.set_shader_parameter("blue_tint", th.blue_paving)
	m.set_shader_parameter("red_tint", th.red_paving)
	m.set_shader_parameter("bases", PackedVector4Array([Vector4(BASE_CENTRE.x, BASE_CENTRE.y, BASE_R, 1),
		Vector4(-BASE_CENTRE.x, -BASE_CENTRE.y, BASE_R, -1)]))
	var pads := PackedVector4Array()
	for t in [1.0, -1.0]:
		for c in CAMPS:
			pads.append(Vector4(c.x * t, c.y * t, CAMP_R + 0.6, 1))
		pads.append(Vector4(PIT.x * t, PIT.y * t, PIT_R, 2))
		pads.append(Vector4(SPAWN.x * t, SPAWN.y * t, SPAWN_R, 3 if t > 0 else 4))
	while pads.size() < 12:
		pads.append(Vector4.ZERO)
	m.set_shader_parameter("pads", pads)
	m.set_shader_parameter("pad_count", 8)
	m.set_shader_parameter("stream_half", STREAM_HALF)
	m.set_shader_parameter("stream_gap", PLAZA_R + WALL_THICK)
	var plane := PlaneMesh.new()
	plane.size = Vector2(HALF_X * 2 + 40, HALF_Z * 2 + 40) # out under the trees past the cliffs
	plane.material = m
	var mi := MeshInstance3D.new()
	mi.name = "Floor"
	mi.mesh = plane
	_root.add_child(mi)
	var ground := StaticBody3D.new() # one flat body for the nav bake, out to the cliffs' outer faces
	ground.name = "Ground"
	ground.collision_layer = GROUND_LAYER
	ground.collision_mask = 0
	var slab := BoxShape3D.new()
	slab.size = Vector3((HALF_X + WALL_THICK) * 2, 1.0, (HALF_Z + WALL_THICK) * 2)
	var gs := CollisionShape3D.new()
	gs.shape = slab
	gs.position.y = -0.5
	ground.add_child(gs)
	_root.add_child(ground)


func _lane_walls() -> void:
	var mat := _fade("cliff", th.stone, true)
	var off_d := (LANE_WIDTH + WALL_THICK) * 0.5
	for i in LANE.size() - 1:
		var a: Vector2 = LANE[i]
		var b: Vector2 = LANE[i + 1]
		var u := (b - a).normalized()
		var n := Vector2(-u.y, u.x)
		var length := a.distance_to(b)
		var count := int(ceil(length / PIECE))
		var step := length / count
		for side in [-1.0, 1.0]:
			var off: Vector2 = n * side * off_d
			for k in count:
				var c: Vector2 = a + u * step * (k + 0.5) + off
				# on the inside of a bend a piece would poke into the next stretch of lane; the walls still cross
				var inside_bend := _lane_dist(c) < off_d - 0.3
				if not _in_area(c) and not _in_hole(c) and not inside_bend:
					_wall(c, u, step + 0.05, WALL_THICK, WALL_HEIGHT, mat)
	for i in range(1, LANE.size() - 1): # a rock on the outside of each bend closes the corner
		var u1: Vector2 = (LANE[i] - LANE[i - 1]).normalized()
		var u2: Vector2 = (LANE[i + 1] - LANE[i]).normalized()
		for side in [-1.0, 1.0]:
			var n1: Vector2 = Vector2(-u1.y, u1.x) * side
			if n1.dot(u2) > 0.0:
				continue # the inside of the bend: the walls already overlap there
			var p1: Vector2 = LANE[i] + n1 * off_d
			var p2: Vector2 = LANE[i] + Vector2(-u2.y, u2.x) * side * off_d
			var c := (p1 + p2) * 0.5
			if not _in_area(c) and not _in_hole(c):
				_rock(c, 1.6, WALL_HEIGHT)


func _lane_dist(p: Vector2) -> float: # distance from p to the nearest point of the lane centre line
	var best := INF
	for i in LANE.size() - 1:
		best = minf(best, p.distance_to(Geometry2D.get_closest_point_to_segment(p, LANE[i], LANE[i + 1])))
	return best


func _ring(c: Vector2, r: float, h: float, mat: Material) -> void:
	var count := int(ceil(TAU * r / PIECE / 2.0)) * 2 # even, so the ring turns onto itself
	var arc := TAU * r / count
	for k in count:
		var ang := TAU * (k + 0.5) / count
		var p := c + Vector2(cos(ang), sin(ang)) * r
		if not _in_hole(p):
			_wall(p, Vector2(-sin(ang), cos(ang)), arc + 0.1, WALL_THICK, h, mat)


func _edges() -> void:
	var mat := _fade("cliff", th.edge, true)
	var t := WALL_THICK
	_wall(Vector2(0, HALF_Z + t * 0.5), Vector2.RIGHT, HALF_X * 2 + t * 2, t, EDGE_HEIGHT, mat)
	_wall(Vector2(0, -HALF_Z - t * 0.5), Vector2.RIGHT, HALF_X * 2 + t * 2, t, EDGE_HEIGHT, mat)
	_wall(Vector2(HALF_X + t * 0.5, 0), Vector2(0, 1), HALF_Z * 2, t, EDGE_HEIGHT, mat)
	_wall(Vector2(-HALF_X - t * 0.5, 0), Vector2(0, 1), HALF_Z * 2, t, EDGE_HEIGHT, mat)


func _features() -> void:
	for t in [1.0, -1.0]:
		var team := "blue" if t > 0 else "red"
		var tc := "Blue" if t > 0 else "Red"
		var col := BLUE if t > 0 else RED
		_ring_decal(SPAWN * t, SPAWN_R - 0.4, col.lerp(Color.WHITE, 0.3), 0.24, 0.0)
		_feature(team + " spawn", "spawn", team, SPAWN * t, SPAWN_R, col)
		_structure(tc + "Core", CORE * t, CORE_R, CORE_HEIGHT, Vector3(1.2, 0.5, 1.2), col, 0.0)
		_feature(team + " core", "core", team, CORE * t, CORE_R, col)
		_structure(tc + "Tower", TOWER * t, TOWER_R, TOWER_HEIGHT, Vector3(0.6, 0.35, 1.0), col, TOWER_RANGE)
		_feature(team + " tower", "tower", team, TOWER * t, TOWER_R, col)
		_ring_decal(PIT * t, PIT_R - 0.7, PIT_COLOR, 0.2, 24.0, 0.05)
		_ring_decal(PIT * t, 1.6, PIT_COLOR, 0.16, 8.0)
		var pit_glow: OmniLight3D = null
		if th.has("pit_light"): # the grate glows from below; a low light in the pit sells it
			var glow := OmniLight3D.new()
			glow.light_color = th.pit_light
			glow.light_energy = 1.6
			glow.omni_range = PIT_R + 1.5
			glow.position = Vector3(PIT.x * t, 0.6, PIT.y * t)
			_dress.add_child(glow)
			pit_glow = glow
		_feature(team + " side pit", "pit", team, PIT * t, PIT_R, col)
		if not Engine.is_editor_hint(): # the pit you take and hold (Preston's pick, 2026-11-05): arena_pit.gd
			var cap := ArenaPit.new()
			cap.name = tc + "PitCapture"
			cap.position = Vector3(PIT.x * t, 0, PIT.y * t)
			var cols := {"blue": BLUE.lerp(Color.WHITE, 0.25), "red": RED.lerp(Color.WHITE, 0.15), "": PIT_COLOR}
			cap.setup(team, PIT_R - 0.5, cols, pit_glow, TEXELS_PER_M)
			_root.add_child(cap)
		for c in CAMPS:
			_ring_decal(c * t, CAMP_R, th.get("camp", CAMP_COLOR), 0.2, 16.0, 0.05)
			_feature(team + " camp", "camp", team, c * t, CAMP_R, col)
	_feature("plaza", "plaza", "", Vector2.ZERO, PLAZA_R, Color.WHITE)
	if not Engine.is_editor_hint(): # the plaza beacon (map skill-up choice 5, 2026-11-05): arena_beacon.gd
		var beacon = BEACON_SCRIPT.new()
		beacon.name = "PlazaBeacon"
		var bcols := {"blue": BLUE.lerp(Color.WHITE, 0.25), "red": RED.lerp(Color.WHITE, 0.15), "": BEACON_COLOR}
		beacon.setup("", BEACON_R, bcols, null, TEXELS_PER_M)
		_root.add_child(beacon)


## A tower or core: a pillar with a team stripe, a turning head on top, a team light, and for a tower its range
## ring. The head is a crystal (gem: radius, lower half's height, upper half's height), or in foundry a turret on
## a tower and a reactor on a core. Every head tops out under the camera's 4.45 m frame top.
func _structure(structure: String, c: Vector2, r: float, h: float, gem: Vector3, col: Color, reach: float) -> void:
	var band_lo := snappedf(h * 0.6, 0.02)
	var base := _pillar(c, r, h, _fade("cliff", th.rock, false, col, band_lo, band_lo + 0.5))
	var trim: Node3D = null
	if th.get("structure", "crystal") == "machine":
		trim = _machine_body(structure, base, c, r, h, col, reach <= 0.0)
	var holder := Node3D.new()
	holder.name = structure + "Gem"
	if th.get("structure", "crystal") == "machine":
		holder.position = Vector3(c.x, h, c.y)
		if reach > 0.0:
			_turret(holder, r, col)
		else:
			_reactor(holder, r, col)
	else:
		holder.position = Vector3(c.x, h + 0.05 + gem.y, c.y)
		_crystal(holder, gem, col)
	_dress.add_child(holder)
	var light := OmniLight3D.new()
	light.light_color = col.lerp(Color.WHITE, 0.2)
	light.light_energy = (TOWER_LIGHT if reach > 0.0 else BASE_LIGHT) * th.light_scale
	light.omni_range = 8.0 if reach > 0.0 else 18.0
	light.position = Vector3(c.x, h + 1.0, c.y)
	_dress.add_child(light)
	var ring: MeshInstance3D = null
	if reach > 0.0:
		ring = _ring_decal(c, reach, col.lerp(Color.WHITE, 0.25), 0.24, 48.0, 0.08, 5.0)
	_structures[structure] = {"base": base, "gem": holder, "light": light, "ring": ring, "trim": trim, "p": c, "down": false}


## The stage 1 head: two four-sided pyramids, point to point.
func _crystal(holder: Node3D, gem: Vector3, col: Color) -> void:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = col.lerp(Color.WHITE, 0.35)
	mat.emission_enabled = true
	mat.emission = col
	mat.emission_energy_multiplier = th.gem_glow
	mat.roughness = 0.35
	for half in [-1.0, 1.0]: # two four-sided pyramids, point to point: a gem
		var cone := CylinderMesh.new()
		var hh: float = gem.z if half > 0 else gem.y
		cone.top_radius = 0.0 if half > 0 else gem.x
		cone.bottom_radius = gem.x if half > 0 else 0.0
		cone.height = hh
		cone.radial_segments = 4
		cone.rings = 0
		cone.material = mat
		var mi := MeshInstance3D.new()
		mi.mesh = cone
		mi.position.y = hh * 0.5 * half
		holder.add_child(mi)


## Foundry's tower and core bodies (2026-11-04 quality pass; Preston: the towers looked like an old Roblox asset).
## The round stone becomes a stepped plinth, four buttresses on it, and a faceted armoured shaft thin enough under the
## head that the turret reads top-heavy, with a glowing team ring under the collar and four team light strips up the
## faces, so the team reads from any side at eye level. The plinth's corners sit at r, as the round body's did, and the
## body is this mesh's hull, so the footprint and the nav mesh stay as before (8 corners where there were 10). It all
## follows r and h, so the height calls stay one number each. Returns the strips' node, which goes dark with the
## structure.
func _machine_body(structure: String, base: MeshInstance3D, c: Vector2, r: float, h: float, col: Color, wide := false) -> Node3D:
	var sh := _shaft(r, wide)
	var sb := sh.x
	var top := sh.y
	var mesh := _lathe([Vector2(r, 0.0), Vector2(r, 0.16), Vector2(r - 0.1, 0.24), Vector2(r - 0.22, 0.24),
		Vector2(r - 0.22, 0.42), Vector2(r - 0.3, 0.5), Vector2(sb, 0.5), Vector2(top, h - 0.32),
		Vector2(top + 0.1, h - 0.24), Vector2(top + 0.1, h - 0.06), Vector2(top + 0.02, h), Vector2(0.0, h)],
		8, -h * 0.5, _fade("armor", Color(0.9, 0.92, 1.0), false, col, h - 0.74, h - 0.44, 0.9))
	var apo := cos(PI / 8.0) # a flat face sits this far in from the corners
	var out := (r - 0.12) * apo
	var fin := _extrude([Vector2(sb * 0.7, 0.24), Vector2(out, 0.24), Vector2(out, 0.62), Vector2(sb * 0.7, 1.72)],
		0.2 + r * 0.06, null)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for k in 4: # on the diagonals, between the strips
		st.append_from(fin, 0, Transform3D(Basis(Vector3.UP, -(PI * 0.25 + PI * 0.5 * k)), Vector3(0, -h * 0.5, 0)))
	st.commit(mesh)
	mesh.surface_set_material(1, _fade("armor", Color(0.62, 0.64, 0.7)))
	base.mesh = mesh
	var cs: CollisionShape3D = base.find_children("*", "CollisionShape3D", true, false)[0]
	cs.shape = mesh.create_convex_shape()
	var wreck := _wreck(r, h, sb, top, wide)
	base.set_meta("up", [mesh, cs.shape])
	base.set_meta("down", [wreck, wreck.create_convex_shape()])
	var trim := Node3D.new()
	trim.name = structure + "Trim"
	trim.position = Vector3(c.x, 0.0, c.y)
	_dress.add_child(trim)
	var y0 := 0.5
	var y1 := h - 0.32
	var phi := atan((sb - top) * apo / (y1 - y0))
	var ys0 := 0.8
	var ys1 := h - 0.7
	var yc := (ys0 + ys1) * 0.5
	var rc := (sb - (sb - top) * (yc - y0) / (y1 - y0)) * apo + 0.025
	var strip := _box(Vector3(0.16, (ys1 - ys0) / cos(phi), 0.06))
	strip.material = _team_glow(col, true)
	for k in 4:
		var a := TAU * k / 4.0
		var mi := MeshInstance3D.new()
		mi.mesh = strip
		mi.transform = Transform3D(Basis(Vector3(sin(a), 0, -cos(a)), Vector3(-cos(a) * sin(phi), cos(phi), -sin(a) * sin(phi)),
			Vector3(cos(a) * cos(phi), sin(phi), sin(a) * cos(phi))), Vector3(cos(a) * rc, yc, sin(a) * rc))
		trim.add_child(mi)
	return trim


## Foundry's felled tower or core: the plinth stays, the buttresses snap, the shaft breaks off near 40% of its height in
## a jagged sooty rim round a crater that still glows, and armour slabs (and on a tower, a barrel) lie on the plinth.
## It all stays inside the footprint r, so its hull keeps the standing body's footprint.
func _wreck(r: float, h: float, sb: float, top: float, wide: bool) -> ArrayMesh:
	var apo := cos(PI / 8.0)
	var yb := h * 0.4
	var y1 := h - 0.32
	var jag := [0.35, -0.15, 0.25, -0.3, 0.3, -0.05, 0.4, -0.25]
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	st.append_from(_lathe([Vector2(r, 0.0), Vector2(r, 0.16), Vector2(r - 0.1, 0.24), Vector2(r - 0.22, 0.24),
		Vector2(r - 0.22, 0.42), Vector2(r - 0.3, 0.5), Vector2(sb, 0.5)], 8, -h * 0.5, null), 0, Transform3D.IDENTITY)
	var rim: Array = []
	for k in 8:
		var t := TAU * (k - 0.5) / 8.0
		var y: float = yb + jag[k] * (0.6 + r * 0.15)
		var rad := sb - (sb - top) * (y - 0.5) / (y1 - 0.5)
		rim.append(Vector3(cos(t) * rad, y - h * 0.5, sin(t) * rad))
	var pit := Vector3(0, yb - 0.45 - h * 0.5, 0)
	var ember := SurfaceTool.new()
	ember.begin(Mesh.PRIMITIVE_TRIANGLES)
	for k in 8:
		var t0 := TAU * (k - 0.5) / 8.0
		var t1 := TAU * (k + 0.5) / 8.0
		var tm := TAU * k / 8.0
		var b0 := Vector3(cos(t0) * sb, 0.5 - h * 0.5, sin(t0) * sb)
		var b1 := Vector3(cos(t1) * sb, 0.5 - h * 0.5, sin(t1) * sb)
		var n := Vector3(cos(tm), 0.15, sin(tm))
		_tri(st, b0, rim[k], rim[(k + 1) % 8], n)
		_tri(st, b0, rim[(k + 1) % 8], b1, n)
		_tri(ember, pit, rim[k], rim[(k + 1) % 8], Vector3.UP)
	var mesh := st.commit()
	var junk := SurfaceTool.new()
	junk.begin(Mesh.PRIMITIVE_TRIANGLES)
	var out := (r - 0.12) * apo
	var fins := [[Vector2(sb * 0.7, 0.24), Vector2(out, 0.24), Vector2(out, 0.62), Vector2((out + sb * 0.7) * 0.5, 1.05), Vector2(sb * 0.7, 1.15)],
		[Vector2(sb * 0.7, 0.24), Vector2(out, 0.24), Vector2(out, 0.46), Vector2((out + sb * 0.7) * 0.5, 0.78), Vector2(sb * 0.7, 0.9)]]
	for k in 4:
		junk.append_from(_extrude(fins[k % 2], 0.2 + r * 0.06, null), 0,
			Transform3D(Basis(Vector3.UP, -(PI * 0.25 + PI * 0.5 * k)), Vector3(0, -h * 0.5, 0)))
	var long := 0.55 + r * 0.1
	var slab := _box(Vector3(long, 0.07, 0.42))
	var tilt := deg_to_rad(25.0)
	for k in 3: # leaning on the shaft
		var a := PI / 8.0 + TAU * k / 3.0
		var rr := Vector3(cos(a), 0, sin(a))
		var along := rr * sin(tilt) + Vector3.UP * cos(tilt)
		var across := rr * cos(tilt) - Vector3.UP * sin(tilt)
		var at := rr * (sb * apo + 0.06 + long * 0.5 * sin(tilt)) + Vector3.UP * (0.5 + long * 0.5 * cos(tilt) - h * 0.5)
		junk.append_from(slab, 0, Transform3D(Basis(along, across, Vector3.UP.cross(rr)), at))
	if not wide: # a barrel off the head, lying on the plinth
		var a := deg_to_rad(200.0)
		var rr := Vector3(cos(a), 0, sin(a))
		var tg := Vector3(-sin(a), 0, cos(a))
		junk.append_from(_cyl(0.07, 0.07, 1.0, 6), 0, Transform3D(Basis(rr, tg, -Vector3.UP), rr * (sb * apo + 0.2) + Vector3.UP * (0.57 - h * 0.5)))
	junk.commit(mesh)
	ember.commit(mesh)
	mesh.surface_set_material(0, _fade("armor", Color(0.82, 0.8, 0.84), false, Color(0.2, 0.16, 0.15), yb - 0.12, yb + 1.0))
	mesh.surface_set_material(1, _fade("armor", Color(0.66, 0.66, 0.72)))
	mesh.surface_set_material(2, _fade("armor", Color(0.3, 0.26, 0.26), false, Color(1.0, 0.42, 0.16), -10.0, 10.0, 1.1))
	return mesh


## The shaft's radius at its foot and at its top for a structure of footprint radius r: a tower's thin under its
## head, a core's (wide) stocky, so it reads as the heavier building.
func _shaft(r: float, wide := false) -> Vector2:
	return Vector2(r * 0.8, r * 0.66) if wide else Vector2(r * 0.62, r * 0.5)


## Foundry's tower head on the shaft top (top at 3.8 m): a wide faceted housing, longer front to back and wider than
## the shaft, so the top-heavy turret shape reads at the frame's top edge; a glowing team ring round it, a mantlet
## with a team visor, twin barrels, a rear counterweight and a mast with a team beacon. Tiles follow the head
## (use_local), so its pixels turn with it.
func _turret(holder: Node3D, _r: float, col: Color) -> void:
	var h: float = holder.position.y
	var shell := _fade("armor", Color(1.0, 1.0, 1.06), false, col, h + 0.31, h + 0.39, 1.0, true)
	var mid := _fade("armor", Color(0.82, 0.84, 0.9), false, Color(0, 0, 0, 0), 0.0, 0.0, 0.0, true)
	var dark := _fade("armor", Color(0.55, 0.56, 0.62), false, Color(0, 0, 0, 0), 0.0, 0.0, 0.0, true)
	var lit := _team_glow(col)
	_mesh_part(holder, _lathe([Vector2(1.0, 0.0), Vector2(1.0, 0.08), Vector2(0.9, 0.13), Vector2(1.2, 0.26),
		Vector2(1.2, 0.44), Vector2(1.04, 0.5), Vector2(0.68, 0.62), Vector2(0.0, 0.62)], 8, 0.0, shell, 1.22))
	_part(holder, _box(Vector3(0.84, 0.3, 0.34)), mid, Vector3(0, 0.35, -1.36))
	_part(holder, _box(Vector3(0.6, 0.08, 0.04)), lit, Vector3(0, 0.44, -1.545))
	for x in [-0.2, 0.2]:
		var barrel := _part(holder, _cyl(0.07, 0.07, 1.0, 6), dark, Vector3(x, 0.34, -2.0))
		barrel.rotation.x = PI * 0.5
		_part(holder, _box(Vector3(0.17, 0.17, 0.14)), dark, Vector3(x, 0.34, -2.48))
	_part(holder, _box(Vector3(0.9, 0.28, 0.42)), dark, Vector3(0, 0.33, 1.42))
	_part(holder, _box(Vector3(0.07, 0.16, 0.07)), dark, Vector3(0.38, 0.68, 0.36))
	_gem(holder, Vector3(0.38, 0.8, 0.36), 0.1, 0.05, lit)


## Foundry's core head on the body top (top at 4.35 m): a deck, a glowing team reactor drum with two dark bands, four
## armoured clamps that turn round it with the holder, a cap ring and a small beacon.
func _reactor(holder: Node3D, r: float, col: Color) -> void:
	var shell := _fade("armor", Color(1.0, 1.0, 1.06), false, Color(0, 0, 0, 0), 0.0, 0.0, 0.0, true)
	var mid := _fade("armor", Color(0.82, 0.84, 0.9), false, Color(0, 0, 0, 0), 0.0, 0.0, 0.0, true)
	var dark := _fade("armor", Color(0.55, 0.56, 0.62), false, Color(0, 0, 0, 0), 0.0, 0.0, 0.0, true)
	var lit := _team_glow(col)
	var deck := _shaft(r, true).y + 0.1
	var drum := r * 0.44
	_mesh_part(holder, _lathe([Vector2(deck, 0.0), Vector2(deck, 0.08), Vector2(deck - 0.12, 0.16), Vector2(0.0, 0.16)], 8, 0.0, dark))
	_mesh_part(holder, _lathe([Vector2(drum, 0.16), Vector2(drum, 1.3), Vector2(0.0, 1.3)], 8, 0.0, _team_glow(col, true)))
	for y in [0.5, 0.95]:
		_mesh_part(holder, _lathe([Vector2(drum + 0.1, y), Vector2(drum + 0.1, y + 0.1), Vector2(0.0, y + 0.1)], 8, 0.0, dark))
	var clamp := _extrude([Vector2(drum + 0.12, 0.16), Vector2(deck - 0.08, 0.16), Vector2(deck - 0.08, 0.52),
		Vector2(drum + 0.36, 1.32), Vector2(drum + 0.12, 1.46)], 0.36, mid)
	for k in 4:
		var mi := _mesh_part(holder, clamp)
		mi.rotation.y = -(PI * 0.25 + PI * 0.5 * k)
	_mesh_part(holder, _lathe([Vector2(drum + 0.42, 1.44), Vector2(drum + 0.42, 1.54), Vector2(drum + 0.26, 1.62),
		Vector2(drum * 0.5, 1.62), Vector2(0.0, 1.62)], 8, 0.0, shell))
	_gem(holder, Vector3(0, 1.66, 0), 0.1, 0.04, lit)


## A solid turned from a profile of (radius, height) points, bottom up with the outside on the right as it climbs,
## in flat facets with a face centred on each axis (and each diagonal, for 8 sides). End on radius 0 for a cap. z_scale
## stretches it front to back.
func _lathe(profile: Array, sides: int, y_off: float, mat: Material, z_scale := 1.0) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in profile.size() - 1:
		var a: Vector2 = profile[i]
		var b: Vector2 = profile[i + 1]
		var n2 := Vector2(b.y - a.y, -(b.x - a.x))
		for k in sides:
			var t0 := TAU * (k - 0.5) / sides
			var t1 := TAU * (k + 0.5) / sides
			var tm := TAU * k / sides
			var n := Vector3(cos(tm) * n2.x, n2.y, sin(tm) * n2.x * z_scale)
			var p00 := Vector3(cos(t0) * a.x, a.y + y_off, sin(t0) * a.x * z_scale)
			var p01 := Vector3(cos(t1) * a.x, a.y + y_off, sin(t1) * a.x * z_scale)
			var p10 := Vector3(cos(t0) * b.x, b.y + y_off, sin(t0) * b.x * z_scale)
			var p11 := Vector3(cos(t1) * b.x, b.y + y_off, sin(t1) * b.x * z_scale)
			_tri(st, p00, p10, p11, n)
			_tri(st, p00, p11, p01, n)
	var mesh := st.commit()
	mesh.surface_set_material(0, mat)
	return mesh


## A flat convex profile of (out, up) points pushed depth deep, centred: a buttress or a clamp.
func _extrude(poly: Array, depth: float, mat: Material) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var hz := depth * 0.5
	var cen := Vector2.ZERO
	for p: Vector2 in poly:
		cen += p / poly.size()
	for i in poly.size():
		var a: Vector2 = poly[i]
		var b: Vector2 = poly[(i + 1) % poly.size()]
		var n2 := Vector2(b.y - a.y, -(b.x - a.x))
		if n2.dot((a + b) * 0.5 - cen) < 0.0:
			n2 = -n2
		var n := Vector3(n2.x, n2.y, 0.0)
		_tri(st, Vector3(a.x, a.y, -hz), Vector3(b.x, b.y, -hz), Vector3(b.x, b.y, hz), n)
		_tri(st, Vector3(a.x, a.y, -hz), Vector3(b.x, b.y, hz), Vector3(a.x, a.y, hz), n)
		for s in [-1.0, 1.0]:
			_tri(st, Vector3(cen.x, cen.y, s * hz), Vector3(a.x, a.y, s * hz), Vector3(b.x, b.y, s * hz), Vector3(0, 0, s))
	var mesh := st.commit()
	mesh.surface_set_material(0, mat)
	return mesh


## One flat-shaded triangle facing along n (Godot draws clockwise faces as the front).
func _tri(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, n: Vector3) -> void:
	var g := (b - a).cross(c - a)
	if g.length_squared() < 1e-10:
		return
	var nn := g.normalized() if g.dot(n) > 0.0 else -g.normalized()
	if g.dot(n) > 0.0:
		var t := b
		b = c
		c = t
	for v in [a, b, c]:
		st.set_normal(nn)
		st.add_vertex(v)


func _mesh_part(holder: Node3D, mesh: Mesh) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	holder.add_child(mi)
	return mi


## A small four-sided gem, two pyramids point to point, centred on at.
func _gem(holder: Node3D, at: Vector3, radius: float, half: float, mat: Material) -> void:
	for s in [-1.0, 1.0]:
		_part(holder, _cyl(0.0 if s > 0.0 else radius, radius if s > 0.0 else 0.0, half, 4), mat, at + Vector3(0, half * 0.5 * s, 0))


func _part(holder: Node3D, mesh: PrimitiveMesh, mat: Material, at: Vector3) -> MeshInstance3D:
	mesh.material = mat
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.position = at
	holder.add_child(mi)
	return mi


func _cyl(top: float, bottom: float, h: float, sides: int) -> CylinderMesh:
	var m := CylinderMesh.new()
	m.top_radius = top
	m.bottom_radius = bottom
	m.height = h
	m.radial_segments = sides
	m.rings = 0
	return m


func _box(size: Vector3) -> BoxMesh:
	var m := BoxMesh.new()
	m.size = size
	return m


func _steel(c: Color) -> StandardMaterial3D:
	var key := "steel" + c.to_html()
	if not _mats.has(key):
		var m := StandardMaterial3D.new()
		m.albedo_color = c
		m.roughness = 0.7
		_mats[key] = m
	return _mats[key]


## deep: the team colour itself, not washed toward white, at a glow that stays under the bloom's clip, so the hue
## holds at range (the foundry towers' strips and the cores' drums).
func _team_glow(col: Color, deep := false) -> StandardMaterial3D:
	var key := "glow%s%s" % [col.to_html(), deep]
	if not _mats.has(key):
		var m := StandardMaterial3D.new()
		m.albedo_color = col * 0.8 if deep else col.lerp(Color.WHITE, 0.35)
		m.emission_enabled = true
		m.emission = col
		m.emission_energy_multiplier = minf(th.gem_glow, 1.2) if deep else th.gem_glow
		m.roughness = 0.35
		_mats[key] = m
	return _mats[key]

func _feature(label: String, kind: String, team: String, p: Vector2, r: float, col: Color) -> void:
	features.append({"name": label, "kind": kind, "team": team, "p": p, "r": r})
	if not show_labels:
		return
	var l := Label3D.new()
	l.text = label
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.no_depth_test = true
	l.fixed_size = true # about 16 px tall at 720p at any distance, so up close it never covers a machine
	l.pixel_size = 0.0008
	l.font_size = 32
	l.outline_size = 8
	l.modulate = col.lerp(Color.WHITE, 0.5)
	# under the chase camera's eye (4.45 m): the frame's top edge is level, so nothing higher ever shows
	l.position = Vector3(p.x, 3.2, p.y)
	_dress.add_child(l)


## A ring painted on the ground. show_near > 0 makes it a tower ring: it shows only as the player comes near.
func _ring_decal(c: Vector2, r: float, col: Color, width: float, dashes: float, fill := 0.0, show_near := 0.0) -> MeshInstance3D:
	var m := ShaderMaterial.new() # one each, so a tower's alert colours only its own ring
	m.shader = RING_SHADER
	m.set_shader_parameter("color", Color(col, 0.85))
	m.set_shader_parameter("radius", r)
	m.set_shader_parameter("width", width)
	m.set_shader_parameter("dashes", dashes)
	m.set_shader_parameter("fill", fill)
	m.set_shader_parameter("show_near", show_near)
	m.set_shader_parameter("texels_per_metre", TEXELS_PER_M)
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * (r * 2.0 + width + 0.4)
	plane.material = m
	var mi := MeshInstance3D.new()
	mi.mesh = plane
	mi.position = Vector3(c.x, 0.02, c.y)
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_dress.add_child(mi)
	return mi


func _dress_world() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = DRESS_SEED
	# Trees past the cliffs, three rows deep. The camera is held inside the map, so they never stand between it
	# and a machine; over the 3.5 m cliffs their canopies fill the band up to the frame's top edge.
	var round_trees: Array = []
	var pines: Array = []
	var out_x := HALF_X + WALL_THICK
	var out_z := HALF_Z + WALL_THICK
	for row in [1.7, 3.9, 6.3]:
		for side in 4:
			var along_x := side < 2
			var reach: float = (out_x if along_x else out_z) + 7.0
			var s := -reach + rng.randf() * 2.0
			while s < reach:
				var off: float = row + rng.randf_range(-0.5, 0.5)
				var sgn := 1.0 if side % 2 == 0 else -1.0
				var p := Vector3(s, 0, sgn * (out_z + off)) if along_x else Vector3(sgn * (out_x + off), 0, s)
				(round_trees if rng.randf() < 0.6 else pines).append(Transform3D(Basis(), p))
				s += rng.randf_range(1.9, 2.8)
	var tech: bool = th.dir != ""
	_sprites(_art("skyline_b") if tech else FIELD_ART + "tree_round.png", round_trees)
	_sprites(_art("skyline_a") if tech else FIELD_ART + "tree_pine.png", pines)
	# Bushes on solid things only: rock tops and the cliff tops. Nothing taller than a tuft grows where a machine
	# walks, so nothing reads as a stealth bush (camouflage stays the chameleon's).
	var bushes: Array = []
	for r in rocks:
		for k in maxi(1, int(r.r * 0.9)):
			var a := rng.randf() * TAU
			var d: float = rng.randf() * r.r * 0.4
			bushes.append(Transform3D(Basis(), Vector3(r.c.x + cos(a) * d, r.h, r.c.y + sin(a) * d)))
	for side in 4:
		var along_x := side < 2
		var sgn := 1.0 if side % 2 == 0 else -1.0
		var reach := HALF_X if along_x else HALF_Z
		var s := -reach + rng.randf() * 2.0
		while s < reach:
			var mid := sgn * ((HALF_Z if along_x else HALF_X) + WALL_THICK * 0.5)
			bushes.append(Transform3D(Basis(), Vector3(s, EDGE_HEIGHT, mid) if along_x else Vector3(mid, EDGE_HEIGHT, s)))
			s += rng.randf_range(2.2, 3.6)
	_sprites(_art("cap") if tech else FIELD_ART + "bush.png", bushes)
	# Tufts and flowers on the open ground, laid on blue's half and turned onto red's, kept off the path, the paving,
	# the pads, the stream and the solids.
	var tufts: Array = []
	var flowers := [[], [], []]
	var tries := 0
	while tufts.size() < 520 and tries < 20000:
		tries += 1
		var p := Vector2(rng.randf_range(-HALF_X + 0.6, HALF_X - 0.6), rng.randf_range(0.0, HALF_Z - 0.6))
		if not _open_ground(p):
			continue
		var jungle := _lane_dist(p) > LANE_WIDTH * 0.5 + 1.0
		var list: Array = tufts
		if jungle and th.flowers and rng.randf() < 0.3:
			list = flowers[rng.randi() % 3]
		list.append(Transform3D(Basis(), Vector3(p.x, 0, p.y)))
		list.append(Transform3D(Basis(), Vector3(-p.x, 0, -p.y)))
	_sprites(_art("stud") if tech else FIELD_ART + "tuft.png", tufts)
	for i in 3:
		_sprites(FIELD_ART + ["flower_pink.png", "flower_violet.png", "flower_white.png"][i], flowers[i])
	# Team banners on the inside of each base wall.
	var banner_path := _art("banner")
	var banner := load(banner_path if ResourceLoader.exists(banner_path) else ART + "banner.png") as Texture2D
	for t in [1.0, -1.0]:
		var col := (BLUE if t > 0 else RED).lerp(Color.WHITE, 0.15)
		for k in 16:
			var ang := TAU * (k + 0.5) / 16.0
			var dir := Vector2(cos(ang), sin(ang))
			var on_wall: Vector2 = BASE_CENTRE * t + dir * BASE_R
			var side := Vector2(-dir.y, dir.x) * 0.9
			if _in_hole(on_wall) or _in_hole(on_wall + side) or _in_hole(on_wall - side):
				continue
			var p: Vector2 = BASE_CENTRE * t + dir * (BASE_R - WALL_THICK * 0.5 - 0.03)
			_flat_sprite(banner, col, Vector3(p.x, 1.95, p.y), atan2(-dir.x, -dir.y))


## Foundry detail pass (2026-11-04; Preston asked for a higher quality map). Steel posts along the walls with an amber
## lamp on each, painted and worn marks on the floor, and a baked map of contact shade and lamp light for
## the ground shader. None of it has a body or stops sight, so play, the nav mesh and the fog of war are as before.
## Only themes with a "detail" entry get it; its numbers are look placeholders for Preston.
func _wall_posts() -> void:
	var d: Dictionary = th.detail
	var posts: Array = []
	var lamps: Array = []
	_pools.clear()
	var run := 0
	var count := 0
	for w in walls:
		var h: float = w.h
		if h < 2.0:
			continue # the pit rims stay low and bare
		var c: Vector2 = w.c
		var u: Vector2 = w.u
		var half_len: float = w.half_len
		var half_thick: float = w.half_thick
		var spots: Array = []
		if half_len > 3.0: # the long edge walls: a post every 8 m or so
			var n := maxi(1, int(half_len * 2.0 / 8.0))
			for k in n:
				spots.append(c + u * (-half_len + (k + 0.5) * half_len * 2.0 / n))
		else: # walls laid in 2 m pieces: a post at every fourth joint
			run += 1
			if run % 4 == 0:
				spots.append(c + u * half_len)
		var basis := Basis(Vector3.UP, atan2(-u.y, u.x))
		var nrm := Vector2(-u.y, u.x)
		for s: Vector2 in spots:
			posts.append(Transform3D(basis * Basis.from_scale(Vector3(1.0, h + 0.2, 1.0)), Vector3(s.x, (h + 0.2) * 0.5, s.y)))
			count += 1
			for side in [-1.0, 1.0]:
				var face: Vector2 = s + nrm * side * (half_thick + 0.2)
				if absf(face.x) > HALF_X - 0.3 or absf(face.y) > HALF_Z - 0.3 or _in_hole(face):
					continue
				lamps.append(Transform3D(basis, Vector3(face.x, h - 0.6, face.y)))
				_pools.append(s + nrm * side * (half_thick + 1.0))
	var post := BoxMesh.new()
	post.size = Vector3(0.44, 1.0, WALL_THICK + 0.28)
	post.material = _fade("cliff", d.post, true)
	_multi(post, posts, true).name = "WallPosts"
	var lamp := BoxMesh.new()
	lamp.size = Vector3(0.3, 0.16, 0.12)
	lamp.material = _fade("lamp")
	_multi(lamp, lamps, false).name = "WallLamps"


func _multi(mesh: Mesh, xforms: Array, shadow: bool) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mesh
	mm.instance_count = xforms.size()
	for i in xforms.size():
		mm.set_instance_transform(i, xforms[i])
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	if not shadow:
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_dress.add_child(mmi)
	return mmi


## Marks on the floor (shaders/world/floor_decal.gdshader), laid on blue's half and turned onto red's: arrows down the
## path to the plaza, hazard bands where the lane leaves the base and meets the plaza, bay numbers by the camps and
## the spawn, and oil, scorch, patches, drains and vents scattered off the walls, the pits and the stream.
func _decals() -> void:
	var tex := load(_art("decals")) as Texture2D
	if tex == null:
		return
	var atlas := Vector2(tex.get_width(), tex.get_height())
	var rng := RandomNumberGenerator.new()
	rng.seed = DRESS_SEED + 11
	var list: Array = [] # [kind, at, yaw]
	var walked := 0.0
	var next_arrow := 9.0
	for i in 3: # the lane from blue's core to the plaza
		var a: Vector2 = LANE[i]
		var b: Vector2 = LANE[i + 1]
		var u := (b - a).normalized()
		var seg := a.distance_to(b)
		while next_arrow < walked + seg:
			var p := a + u * (next_arrow - walked)
			if p.distance_to(TOWER) > TOWER_R + 2.5 and p.length() > PLAZA_R + 2.0 and p.distance_to(BASE_CENTRE) > BASE_R + 1.0:
				list.append(["arrow", p, atan2(-u.y, u.x)])
			next_arrow += 11.0
		walked += seg
	var gate_u: Vector2 = (LANE[1] - LANE[0]).normalized()
	var mouth_u: Vector2 = (LANE[3] - LANE[2]).normalized()
	for band in [[BASE_CENTRE + gate_u * (BASE_R + 1.2), gate_u], [mouth_u * -(PLAZA_R + 1.8), mouth_u]]:
		var at: Vector2 = band[0]
		var bu: Vector2 = band[1]
		var bn := Vector2(-bu.y, bu.x)
		for k in 4:
			list.append(["hazard" if k % 2 == 0 else "hazard2", at + bn * (k - 1.5) * 1.28, atan2(-bn.y, bn.x)])
	var placed: Array = []
	for item in list:
		placed.append(item[1])
	var tries := 0
	var made := 0
	while made < 36 and tries < 4000:
		tries += 1
		var p := Vector2(rng.randf_range(-HALF_X + 1.5, HALF_X - 1.5), rng.randf_range(1.0, HALF_Z - 1.5))
		if not _decal_ok(p, 0.6):
			continue
		var near := false
		for q: Vector2 in placed:
			if q.distance_to(p) < 3.0:
				near = true
				break
		if near:
			continue
		var on_path := _lane_dist(p) < PATH_WIDTH * 0.5
		var paved := p.length() < PLAZA_R or p.distance_to(BASE_CENTRE) < BASE_R
		var pick: Array = ["oil", "scorch"] if on_path else (["patch", "drain", "patch", "vent"] if paved else ["oil", "patch", "drain", "vent", "scorch", "patch"])
		list.append([pick[rng.randi() % pick.size()], p, rng.randi_range(0, 3) * PI * 0.5])
		placed.append(p)
		made += 1
	for k in CAMPS.size():
		var camp: Vector2 = CAMPS[k]
		list.append([["d07", "d12"][k], camp + Vector2(0, -(CAMP_R + 1.3)), 0.0])
	list.append(["d21", SPAWN + Vector2(-3.2, -(SPAWN_R + 1.0)), 0.0])
	list.append(["d34", SPAWN + Vector2(3.2, -(SPAWN_R + 1.0)), 0.0])
	var mat := ShaderMaterial.new()
	mat.shader = DECAL_SHADER
	mat.set_shader_parameter("atlas", tex)
	mat.set_shader_parameter("texels_per_metre", TEXELS_PER_M)
	mat.set_shader_parameter("glow_energy", th.glow)
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE
	plane.material = mat
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_custom_data = true
	mm.mesh = plane
	mm.instance_count = list.size() * 2
	var i := 0
	for item in list:
		var r: Rect2 = DECALS[item[0]]
		var at: Vector2 = item[1]
		for t in [1.0, -1.0]:
			var basis := Basis(Vector3.UP, float(item[2]) + (0.0 if t > 0.0 else PI)) * Basis.from_scale(Vector3(r.size.x / TEXELS_PER_M, 1.0, r.size.y / TEXELS_PER_M))
			mm.set_instance_transform(i, Transform3D(basis, Vector3(at.x * t, 0.012, at.y * t)))
			mm.set_instance_custom_data(i, Color(r.position.x / atlas.x, r.position.y / atlas.y, r.size.x / atlas.x, r.size.y / atlas.y))
			i += 1
	var mmi := MultiMeshInstance3D.new()
	mmi.name = "FloorMarks"
	mmi.multimesh = mm
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_dress.add_child(mmi)


func _decal_ok(p: Vector2, r: float) -> bool:
	if absf(p.x) > HALF_X - 1.0 or absf(p.y) > HALF_Z - 1.0:
		return false
	if absf(p.x) > PLAZA_R + WALL_THICK and absf(p.y) < STREAM_HALF + 0.8:
		return false
	for w in walls:
		var u: Vector2 = w.u
		var dd: Vector2 = p - w.c
		var along: float = absf(dd.dot(u)) - w.half_len
		var across: float = absf(dd.dot(Vector2(-u.y, u.x))) - w.half_thick
		if Vector2(maxf(along, 0.0), maxf(across, 0.0)).length() < r + 0.3:
			return false
	for k in rocks:
		if p.distance_to(k.c) < k.r + r + 0.3:
			return false
	for s in structure_list():
		if p.distance_to(s.p) < 4.0:
			return false
	for t in [1.0, -1.0]:
		if p.distance_to(PIT * t) < PIT_R + 1.0:
			return false
	return true


## The ground shader's baked map: r, contact shade within 2.2 m of every wall, rock and structure (the pit rims
## lighter); g, the light pool in front of each wall lamp. 4 cells a metre; blue's half is worked out and turned
## onto red's, as the map is the same map turned 180 degrees.
func _floor_map() -> void:
	var d: Dictionary = th.detail
	var px := 4.0
	var w := int((HALF_X + 2.0) * 2.0 * px)
	var h := int((HALF_Z + 2.0) * 2.0 * px)
	var corner := -Vector2(w, h) / px * 0.5
	var shade := PackedFloat32Array()
	shade.resize(w * h)
	var light := PackedFloat32Array()
	light.resize(w * h)
	var reach := 2.2
	var solids: Array = [] # [centre, along, half length, half thickness or radius, strength]; round ones have along zero
	for wl in walls:
		solids.append([wl.c, wl.u, wl.half_len, wl.half_thick, 1.0 if wl.h >= 2.0 else 0.6])
	for rk in rocks:
		solids.append([rk.c, Vector2.ZERO, 0.0, rk.r, 1.0])
	for s in structure_list():
		solids.append([s.p, Vector2.ZERO, 0.0, TOWER_R if s.kind == "tower" else CORE_R, 1.0])
	for sd in solids:
		var c: Vector2 = sd[0]
		var u: Vector2 = sd[1]
		var hl: float = sd[2]
		var ht: float = sd[3]
		var st: float = sd[4]
		var round := u == Vector2.ZERO
		var n := Vector2(-u.y, u.x)
		var ext := Vector2(absf(u.x) * hl + absf(n.x) * ht, absf(u.y) * hl + absf(n.y) * ht) + Vector2.ONE * (reach + (ht if round else 0.0))
		var x0 := maxi(0, int((c.x - ext.x - corner.x) * px))
		var x1 := mini(w - 1, int((c.x + ext.x - corner.x) * px))
		var y0 := maxi(h / 2, int((c.y - ext.y - corner.y) * px))
		var y1 := mini(h - 1, int((c.y + ext.y - corner.y) * px))
		for y in range(y0, y1 + 1):
			var pz := corner.y + (y + 0.5) / px
			for x in range(x0, x1 + 1):
				var dv := Vector2(corner.x + (x + 0.5) / px, pz) - c
				var dist: float
				if round:
					dist = maxf(dv.length() - ht, 0.0)
				else:
					dist = Vector2(maxf(absf(dv.dot(u)) - hl, 0.0), maxf(absf(dv.dot(n)) - ht, 0.0)).length()
				var v := 1.0 - dist / reach
				if v <= 0.0:
					continue
				v = pow(v, 1.5) * st
				var k := y * w + x
				if v > shade[k]:
					shade[k] = v
	var pool_r := 3.5
	for pc: Vector2 in _pools:
		if pc.y < -pool_r:
			continue
		var x0 := maxi(0, int((pc.x - pool_r - corner.x) * px))
		var x1 := mini(w - 1, int((pc.x + pool_r - corner.x) * px))
		var y0 := maxi(h / 2, int((pc.y - pool_r - corner.y) * px))
		var y1 := mini(h - 1, int((pc.y + pool_r - corner.y) * px))
		for y in range(y0, y1 + 1):
			for x in range(x0, x1 + 1):
				var v := 1.0 - (corner + Vector2(x + 0.5, y + 0.5) / px).distance_to(pc) / pool_r
				var k := y * w + x
				if v > light[k]:
					light[k] = v
	var bytes := PackedByteArray()
	bytes.resize(w * h * 2)
	var cells := w * h
	for k in range(cells / 2, cells):
		var a := int(shade[k] * 255.0)
		var g := int(light[k] * 255.0)
		var j := cells - 1 - k
		bytes[k * 2] = a
		bytes[k * 2 + 1] = g
		bytes[j * 2] = a
		bytes[j * 2 + 1] = g
	var img := Image.create_from_data(w, h, false, Image.FORMAT_RG8, bytes)
	var m := _ground_mat
	m.set_shader_parameter("floor_map", ImageTexture.create_from_image(img))
	m.set_shader_parameter("floor_rect", Vector4(corner.x, corner.y, w / px, h / px))
	m.set_shader_parameter("use_detail", true)
	m.set_shader_parameter("ao_strength", d.ao)
	m.set_shader_parameter("grime_color", d.grime)
	m.set_shader_parameter("pool_color", d.pool)
	m.set_shader_parameter("pool_energy", d.pool_energy)
	m.set_shader_parameter("macro", d.macro)


## A tile or prop of the current theme.
func _art(file: String) -> String:
	return ART + th.dir + file + ".png"


func _open_ground(p: Vector2) -> bool:
	if _lane_dist(p) < PATH_WIDTH * 0.5 + 0.8 or p.length() < PLAZA_R + 1.6:
		return false
	if p.distance_to(BASE_CENTRE) < BASE_R + 1.2 or p.distance_to(PIT) < PIT_R + 1.6:
		return false
	if absf(p.y) < STREAM_HALF + 0.8:
		return false
	for c in CAMPS:
		if p.distance_to(c) < CAMP_R + 1.2:
			return false
	for w in walls:
		var d: Vector2 = p - w.c
		var along: float = absf(d.dot(w.u)) - w.half_len
		var across: float = absf(d.dot(Vector2(-w.u.y, w.u.x))) - w.half_thick
		if Vector2(maxf(along, 0.0), maxf(across, 0.0)).length() < 0.6:
			return false
	for r in rocks:
		if p.distance_to(r.c) < r.r + 0.6:
			return false
	return true


## Billboards from one pixel-art texture, standing on each transform's origin, as one MultiMesh.
func _sprites(path: String, spots: Array) -> void:
	if spots.is_empty():
		return
	var tex := load(path) as Texture2D
	var quad := QuadMesh.new()
	quad.size = Vector2(tex.get_width(), tex.get_height()) / TEXELS_PER_M
	quad.center_offset = Vector3(0, quad.size.y * 0.5, 0)
	var m := ShaderMaterial.new()
	m.shader = SPRITE_SHADER
	m.set_shader_parameter("sprite", tex)
	quad.material = m
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = quad
	mm.instance_count = spots.size()
	for i in spots.size():
		mm.set_instance_transform(i, spots[i])
	var mmi := MultiMeshInstance3D.new()
	mmi.name = path.get_file().get_basename().capitalize().replace(" ", "")
	var origins := PackedVector3Array() # kept as meta: the headless renderer keeps no MultiMesh transforms to read back
	for t in spots:
		origins.append(t.origin)
	mmi.set_meta("spots", origins)
	mmi.multimesh = mm
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mmi.custom_aabb = AABB(Vector3(-HALF_X - 20, -1, -HALF_Z - 20), Vector3(HALF_X * 2 + 40, 12, HALF_Z * 2 + 40))
	_dress.add_child(mmi)


## A flat pixel sprite (a banner) that does not turn to the camera; yaw turns its face toward -z of that basis.
func _flat_sprite(tex: Texture2D, tint: Color, at: Vector3, yaw: float) -> void:
	var quad := QuadMesh.new()
	quad.size = Vector2(tex.get_width(), tex.get_height()) / TEXELS_PER_M
	var key := "flat" + str(tex.get_rid()) + tint.to_html()
	if not _mats.has(key):
		var m := ShaderMaterial.new()
		m.shader = SPRITE_SHADER
		m.set_shader_parameter("sprite", tex)
		m.set_shader_parameter("tint", tint)
		m.set_shader_parameter("billboard", false)
		_mats[key] = m
	quad.material = _mats[key]
	var mi := MeshInstance3D.new()
	mi.mesh = quad
	mi.transform = Transform3D(Basis(Vector3.UP, yaw), at)
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_dress.add_child(mi)


func _wall(c: Vector2, u: Vector2, length: float, thick: float, h: float, mat: Material) -> void:
	var box := BoxMesh.new()
	box.size = Vector3(length, h, thick)
	box.material = mat
	var mi := MeshInstance3D.new()
	mi.mesh = box
	mi.transform = Transform3D(Basis(Vector3.UP, atan2(-u.y, u.x)), Vector3(c.x, h * 0.5, c.y))
	_root.add_child(mi)
	var shape := BoxShape3D.new()
	shape.size = box.size
	_collide(mi, shape)
	walls.append({"c": c, "u": u, "half_len": length * 0.5, "half_thick": thick * 0.5, "h": h})


func _rock(c: Vector2, r: float, h: float) -> void:
	_pillar(c, r, h, _fade("cliff", th.rock, true), 0.75)
	rocks.append({"c": c, "r": r, "h": h})


func _pillar(c: Vector2, r: float, h: float, mat: Material, taper := 0.7) -> MeshInstance3D:
	var cyl := CylinderMesh.new()
	cyl.top_radius = r * taper
	cyl.bottom_radius = r
	cyl.height = h
	cyl.radial_segments = 10
	cyl.material = mat
	var mi := MeshInstance3D.new()
	mi.mesh = cyl
	mi.position = Vector3(c.x, h * 0.5, c.y)
	_root.add_child(mi)
	var pts := PackedVector3Array()
	for k in cyl.radial_segments: # the corners CylinderMesh uses, so the body tapers with the mesh
		var a := TAU * k / cyl.radial_segments
		pts.append(Vector3(sin(a) * r, -h * 0.5, cos(a) * r))
		pts.append(Vector3(sin(a) * r * taper, h * 0.5, cos(a) * r * taper))
	var shape := ConvexPolygonShape3D.new()
	shape.points = pts
	_collide(mi, shape)
	return mi


func _collide(mi: MeshInstance3D, shape: Shape3D) -> void:
	var body := StaticBody3D.new()
	body.collision_layer = WORLD_LAYER
	body.collision_mask = 0
	var cs := CollisionShape3D.new()
	cs.shape = shape
	body.add_child(cs)
	mi.add_child(body)


func _place_markers() -> void: # the named points the machine scripts read; saved in the scene, moved here
	var holder: Node3D = get_node_or_null("Markers")
	if holder == null:
		holder = Node3D.new()
		holder.name = "Markers"
		add_child(holder)
	var spots := {"Spawn": SPAWN, "Core": CORE, "Tower": TOWER, "Pit": PIT, "Camp1": CAMPS[0], "Camp2": CAMPS[1]}
	for t in [1.0, -1.0]:
		var team := "Blue" if t > 0 else "Red"
		for key in spots:
			_marker(holder, team + key, spots[key] * t, 0.0 if t > 0 else PI)
		var tower := holder.get_node(team + "Tower")
		tower.set_meta("team", team.to_lower())
		tower.set_meta("radius", TOWER_R)
		tower.set_meta("range", TOWER_RANGE)
		var core := holder.get_node(team + "Core")
		core.set_meta("team", team.to_lower())
		core.set_meta("radius", CORE_R)
	_marker(holder, "Plaza", Vector2.ZERO, 0.0)
	for i in STREAMS.size():
		_marker(holder, "Stream%d" % (i + 1), STREAMS[i], 0.0)


func _marker(holder: Node3D, marker_name: String, p: Vector2, yaw: float) -> void:
	var m: Marker3D = holder.get_node_or_null(marker_name)
	if m == null:
		m = Marker3D.new()
		m.name = marker_name
		holder.add_child(m)
	m.transform = Transform3D(Basis(Vector3.UP, yaw), Vector3(p.x, 0.0, p.y))


func _bake_nav() -> void: # from the bodies, so a new wall or prop with a body joins the nav mesh by itself
	var nm := NavigationMesh.new()
	nm.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	nm.geometry_collision_mask = WORLD_LAYER | GROUND_LAYER
	nm.agent_radius = NAV_AGENT_RADIUS
	nm.agent_height = 2.0
	nm.agent_max_climb = 0.25
	nm.region_min_size = 40.0 # squared into 0.25 m cells: islands under 100 m2 (rock and pillar tops) are dropped
	var t0 := Time.get_ticks_usec()
	var src := NavigationMeshSourceGeometryData3D.new()
	NavigationServer3D.parse_source_geometry_data(nm, src, _root)
	NavigationServer3D.bake_from_source_geometry_data(nm, src)
	nav_bake_ms = (Time.get_ticks_usec() - t0) / 1000.0
	var region := NavigationRegion3D.new()
	region.name = "Nav"
	region.navigation_mesh = nm
	_root.add_child(region)


func _in_area(p: Vector2) -> bool: # inside the plaza or a base, where lane walls stop
	if p.length() < PLAZA_R + 0.2:
		return true
	for t in [1.0, -1.0]:
		if p.distance_to(BASE_CENTRE * t) < BASE_R - 0.4:
			return true
	return false


func _in_hole(p: Vector2) -> bool:
	for h in holes:
		if p.distance_to(Vector2(h.x, h.y)) < h.z:
			return true
	return false


## Walls, rocks, cliffs, towers: anything that stands up. tex is a tile in ART ("" for plain colour); top puts grass
## on the up faces; band paints a stripe band_lo to band_hi metres up (alpha 0 for none).
func _fade(tex: String, tint := Color.WHITE, top := false, band := Color(0, 0, 0, 0), band_lo := 0.0, band_hi := 0.0,
		band_glow := 0.0, local := false) -> ShaderMaterial:
	var key := "fade%s%s%s%s%.2f%.2f%.2f%s" % [tex, tint.to_html(), top, band.to_html(), band_lo, band_hi, band_glow, local]
	if not _mats.has(key):
		var m := ShaderMaterial.new()
		m.shader = FADE_SHADER
		if tex != "":
			m.set_shader_parameter("albedo_texture", load(_art(tex)))
		m.set_shader_parameter("albedo", tint)
		m.set_shader_parameter("texels_per_metre", TEXELS_PER_M)
		m.set_shader_parameter("tile_px", TILE_PX)
		if top:
			m.set_shader_parameter("use_top", true)
			m.set_shader_parameter("top_texture", load(_art("grass_top")))
			m.set_shader_parameter("lip_color", th.lip)
			m.set_shader_parameter("lip_hazard", th.hazard)
		m.set_shader_parameter("glow_energy", th.glow)
		if band.a > 0.0:
			m.set_shader_parameter("band_color", band)
			m.set_shader_parameter("band_lo", band_lo)
			m.set_shader_parameter("band_hi", band_hi)
			m.set_shader_parameter("band_glow", band_glow)
		if local:
			m.set_shader_parameter("use_local", true)
		_mats[key] = m
	return _mats[key]
