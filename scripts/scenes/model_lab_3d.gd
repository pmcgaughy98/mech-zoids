extends Node3D
## The 3D model lab (Claude, 2026-10-11; Preston pivoted the machines to 3D). Loads a machine's .glb, gives every
## surface a cel-shaded look (toon light bands, a toon highlight and a rim light) and a dark ink outline, and
## puts it on a floor under a turning camera. Q / E turn the camera 45 degrees, O orbits, Esc goes back to the title.
## Light levels (sun 0.2, fill 0.6) are calibrated so the gorilla renders at the greens of Preston's picked sprite (2026-10-11).
## The game draws at 320x180 and scales up by whole numbers, so 3D here comes out chunky, like the 2D art.
## Codex and Claude check new 3D machines here: set MACHINE to the id.

const MACHINE := "ape_l"
const OUTLINE_SHADER := """
shader_type spatial;
render_mode unshaded, cull_front;
uniform vec4 ink : source_color = vec4(0.06, 0.07, 0.08, 1.0);
uniform float width = 0.03;
void vertex() { VERTEX += NORMAL * width; }
void fragment() { ALBEDO = ink.rgb; }
"""

var camera_deg := 0.0
var target_deg := 0.0
var orbit := false
var model: Node3D
var pivot: Node3D
var _hud: Label
var finish := "metal"   # "metal" (Cybertron finish) or "cel"; HT_FINISH overrides
var finish_count := 0


func _ready() -> void:
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color("1d2024")
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color("8c97a8")
	env.environment.ambient_light_energy = 0.6
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, -35, 0)
	sun.light_energy = 0.2
	sun.shadow_enabled = true
	add_child(sun)
	var floor_mesh := MeshInstance3D.new()
	var disc := CylinderMesh.new()
	disc.top_radius = 3.2
	disc.bottom_radius = 3.2
	disc.height = 0.05
	disc.radial_segments = 48
	floor_mesh.mesh = disc
	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_color = Color("2c3036")
	floor_mat.diffuse_mode = BaseMaterial3D.DIFFUSE_TOON
	floor_mesh.material_override = floor_mat
	floor_mesh.position.y = -0.025
	add_child(floor_mesh)
	model = (load("res://art/machines/%s/%s.glb" % [MACHINE, MACHINE]) as PackedScene).instantiate()
	add_child(model)
	if OS.get_environment("HT_FINISH") != "":
		finish = OS.get_environment("HT_FINISH")
	finish_count = cel_shade(model) if finish == "cel" else metal_finish(model, env.environment, sun)
	play_walk()
	pivot = Node3D.new()
	pivot.position = Vector3(0, 1.0, 0)
	add_child(pivot)
	var cam := Camera3D.new()
	cam.fov = 38.0
	cam.position = Vector3(0, 0, 7.2)
	pivot.add_child(cam)
	pivot.rotation_degrees.x = -24.0
	cam.current = true
	var layer := CanvasLayer.new()
	add_child(layer)
	_hud = Label.new()
	_hud.position = Vector2(4, 2)
	_hud.add_theme_font_size_override("font_size", 8)
	_hud.add_theme_color_override("font_color", Color(1, 1, 1, 0.8))
	layer.add_child(_hud)


## Every surface of every mesh under `root` gets toon lighting and an ink outline, keeping its own colour.
static func cel_shade(root: Node) -> int:
	var outline := ShaderMaterial.new()
	outline.shader = Shader.new()
	outline.shader.code = OUTLINE_SHADER
	var count := 0
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		var m: MeshInstance3D = mi
		for i in m.mesh.get_surface_count():
			var src: Material = m.get_active_material(i)
			var mat: StandardMaterial3D = (src.duplicate() as StandardMaterial3D) if src is StandardMaterial3D else StandardMaterial3D.new()
			mat.diffuse_mode = BaseMaterial3D.DIFFUSE_TOON
			mat.specular_mode = BaseMaterial3D.SPECULAR_TOON
			mat.rim_enabled = true
			mat.rim = 0.2
			mat.rim_tint = 0.4
			mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS   # crisp painted pixels, like the 2D art
			mat.next_pass = outline
			m.set_surface_override_material(i, mat)
			count += 1
	return count


## Plays the machine's "walk" loop if its .glb has one (the gorilla's knuckle walk, built in Blender). Returns the player.
func play_walk() -> AnimationPlayer:
	var players := model.find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		return null
	var player: AnimationPlayer = players[0]
	for clip_name in ["walk", "idle"]:   # the loops; punch, hit and death play once
		if player.has_animation(clip_name):
			player.get_animation(clip_name).loop_mode = Animation.LOOP_LINEAR
	if player.has_animation("walk"):
		player.play("walk")
	return player


## Keys 1-5 play walk, idle, punch, hit and death.
func play_clip(clip_name: String) -> void:
	var players := model.find_children("*", "AnimationPlayer", true, false)
	if not players.is_empty() and (players[0] as AnimationPlayer).has_animation(clip_name):
		(players[0] as AnimationPlayer).play(clip_name)


## The Cybertron finish (Preston, 2026-10-11: "look like War for Cybertron and Fall of Cybertron"): the model's own
## colour, surface-detail (normal) and metal/roughness maps lit as worn metal, a sky for reflections, a warm key
## light, ACES tone mapping and glow on the lights. A thin ink line keeps the shape readable at 320x180.
static func metal_finish(root: Node, environment: Environment, sun: DirectionalLight3D) -> int:
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color("2a3340")
	sky_mat.sky_horizon_color = Color("6d6a64")
	sky_mat.ground_horizon_color = Color("4a4038")
	sky_mat.ground_bottom_color = Color("1b1a19")
	var sky := Sky.new()
	sky.sky_material = sky_mat
	environment.sky = sky
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	environment.ambient_light_energy = 1.0
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("1d2024")
	environment.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	environment.tonemap_mode = Environment.TONE_MAPPER_ACES
	environment.glow_enabled = true
	environment.glow_intensity = 0.35
	environment.ssao_enabled = true   # contact shadow where plates overlap, so the layers read as layers
	environment.ssao_radius = 0.6
	environment.ssao_intensity = 2.0
	sun.light_color = Color("ffd8b0")
	sun.light_energy = 1.4
	var rim := DirectionalLight3D.new()   # a cool back light, the strong rim lighting the Cybertron games use
	rim.rotation_degrees = Vector3(-25, 160, 0)
	rim.light_color = Color("9fc4ff")
	rim.light_energy = 0.9
	root.add_child(rim)
	var outline := ShaderMaterial.new()
	outline.shader = Shader.new()
	outline.shader.code = OUTLINE_SHADER
	outline.set_shader_parameter("width", 0.012)
	var count := 0
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		var m: MeshInstance3D = mi
		for i in m.mesh.get_surface_count():
			var src: Material = m.get_active_material(i)
			var mat: StandardMaterial3D = (src.duplicate() as StandardMaterial3D) if src is StandardMaterial3D else StandardMaterial3D.new()
			mat.diffuse_mode = BaseMaterial3D.DIFFUSE_BURLEY
			mat.specular_mode = BaseMaterial3D.SPECULAR_SCHLICK_GGX
			mat.rim_enabled = true
			mat.rim = 0.2
			mat.rim_tint = 0.5
			mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
			mat.next_pass = outline
			m.set_surface_override_material(i, mat)
			count += 1
	return count


## Turn the camera by whole 45-degree steps (eased); the check calls this directly.
func turn(steps: int) -> void:
	target_deg += steps * 45.0


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_Q: turn(-1)
		KEY_E: turn(1)
		KEY_O: orbit = not orbit
		KEY_1: play_clip("walk")
		KEY_2: play_clip("idle")
		KEY_3: play_clip("punch")
		KEY_4: play_clip("hit")
		KEY_5: play_clip("death")
		KEY_ESCAPE: get_tree().change_scene_to_file("res://scenes/title.tscn")


func _process(delta: float) -> void:
	if orbit:
		target_deg += 25.0 * delta
	camera_deg = move_toward(camera_deg, target_deg, maxf(90.0 * delta, absf(target_deg - camera_deg) * 6.0 * delta))
	pivot.rotation_degrees.y = camera_deg
	_hud.text = "3D MODEL LAB  %s   camera %d   Q/E turn   O orbit %s   1-5 walk idle punch hit death   Esc title" % [MACHINE, int(fposmod(round(camera_deg), 360.0)), "on" if orbit else "off"]
