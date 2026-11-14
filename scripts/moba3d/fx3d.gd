class_name Fx3D
extends RefCounted
## Effects for the machines' kits in the 3D slice (Claude, 2026-11-04). The art is Codex's effect set
## (codex-set-b/effects) and the ground pound ring (codex-ground-pound/clean/effect), packed by
## tools/art/pack_rhino_3d.py with each effect's anchor at its canvas centre, on the same 50 texels per metre grid
## as the machines.

const FRAMES := preload("res://art/fx/moba3d/fx_frames.tres")
const DIR := "res://art/fx/moba3d/"
const PX := 0.02
const LOOK_FX := preload("res://scripts/moba3d/look_fx.gd")  # smooth sparks and stars (look lane)


## A billboard effect whose anchor sits at pos. toward_camera pulls it that far toward the camera so it draws over
## the machine it belongs to. Frees itself when done unless loop is true.
static func spawn(parent: Node, anim: String, pos: Vector3, toward_camera := 0.0, loop := false) -> AnimatedSprite3D:
	var s := AnimatedSprite3D.new()
	s.sprite_frames = FRAMES
	s.pixel_size = PX
	s.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	s.shaded = false
	parent.add_child(s)
	var cam := parent.get_viewport().get_camera_3d()
	if cam != null and toward_camera > 0.0:
		var d := cam.global_position - pos
		d.y = 0.0
		if d.length() > 0.01:
			pos += d.normalized() * toward_camera
	s.global_position = pos
	s.play(StringName(anim))
	if anim in LOOK_FX.SMOOTH and not LOOK_FX.off:  # look lane 2026-11-11: smooth shader version; the sprite stays as an invisible carrier
		s.modulate = Color(1, 1, 1, 0)
		s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISABLED  # a discard sprite still writes depth; a fully clear blended one draws nothing
		var n := FRAMES.get_frame_count(StringName(anim))
		var fps := FRAMES.get_animation_speed(StringName(anim))
		s.add_child(LOOK_FX.make(anim, n / maxf(fps, 1.0)))
	if not loop:
		s.animation_finished.connect(s.queue_free)
	return s


## An effect drawn as a ground ellipse (brace ring), laid flat and stretched back to a circle so the gameplay camera
## sees it as drawn. Cycles its frames until freed.
static func spawn_flat(parent: Node, frames_name: String, count: int, pos: Vector3, width_m: float, fps := 10.0) -> Node3D:
	var f := FlatFx.new()
	for i in count:
		f.textures.append(load(DIR + "%s_f%d.png" % [frames_name, i]))
	f.fps = fps
	f.mat = _flat_material(f.textures[0])
	var pm := PlaneMesh.new()
	pm.size = Vector2(width_m, width_m)
	pm.material = f.mat
	f.mesh = pm
	parent.add_child(f)
	f.global_position = pos
	return f


## A still texture lying on the ground (cracks, the slow patch) that fades out over its last 0.6 s.
static func ground_decal(parent: Node, file: String, pos: Vector3, size_m: float, life: float, lift := 0.02) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var m := _flat_material(load(DIR + file))
	var pm := PlaneMesh.new()
	pm.size = Vector2(size_m, size_m)
	pm.material = m
	mi.mesh = pm
	parent.add_child(mi)
	mi.global_position = pos + Vector3.UP * lift
	var tw := mi.create_tween()
	tw.tween_interval(maxf(life - 0.6, 0.0))
	tw.tween_property(m, "albedo_color:a", 0.0, 0.6)
	tw.tween_callback(mi.queue_free)
	return mi


static func _flat_material(tex: Texture2D) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_texture = tex
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	return m


class FlatFx extends MeshInstance3D:
	var textures: Array[Texture2D] = []
	var fps := 10.0
	var mat: StandardMaterial3D
	var t := 0.0

	func _process(delta: float) -> void:
		t += delta
		mat.albedo_texture = textures[int(t * fps) % textures.size()]
