class_name ContactShadow3D
extends MeshInstance3D
## The contact shadow under a machine (Claude, 2026-11-04, camera and perspective lane; Preston: "shadow fixes").
## The old one was a fixed 2.8 x 1.4 m oval that never turned and sat centred on the spot the near foot of a 35-degree
## drawing was pinned to, so most of it showed in front of the feet and the machine read as floating. This one is
## sized from the machine's feet (DirectionalSprite3D.feet_model(), the "feet" meta on its frames), centred under them,
## and turned to the facing the frame on screen is drawn at (its 45-degree view, not the exact facing, so it always
## matches the picture). Without the meta it is a plain oval sized from the canvas.
## attach() adds one to a machine as its "Shadow" (so code that hides or scales a machine's "Shadow", such as the
## fennec's dig, reaches it) and renames the old fixed one "OldShadow" and hides it.

const SHADER := preload("res://scripts/moba3d/contact_shadow_3d.gdshader")
const PAD_ALONG := 0.32 ## metres past the outer feet along the body, for an L machine; smaller classes scale down
const PAD_ACROSS := 0.28 ## the same across the body
const DEFAULT_FEET := {"front": 0.4, "rear": -0.4, "half_width": 0.4} ## metres, for an L machine with no meta
const LIFT := 0.02 ## above the floor; the team ring sits at 0.035, over it

var sprite: DirectionalSprite3D
var feet_texels := {} ## used when the sprite's frames carry no "feet" meta: the same keys, in texels
var _mat: ShaderMaterial


## Adds a contact shadow under machine for its sprite, named "Shadow"; the old fixed one becomes "OldShadow", hidden.
static func attach(machine: Node3D, s: DirectionalSprite3D, feet := {}) -> ContactShadow3D:
	var old := machine.get_node_or_null("Shadow") as Node3D
	if old is ContactShadow3D:
		return old
	if old != null:
		old.name = "OldShadow"
		old.visible = false
	var c := ContactShadow3D.new()
	c.name = "Shadow"
	c.sprite = s
	c.feet_texels = feet
	machine.add_child(c)
	return c


func _ready() -> void:
	var m := PlaneMesh.new()
	m.size = Vector2(2.0, 2.0)  # radius 1 each way; the transform stretches it to the radii
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	m.material = _mat
	mesh = m
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	top_level = true  # placed in world space each frame
	process_priority = 10  # after the machine has picked its frame
	refresh()


func _process(_delta: float) -> void:
	refresh()


## Puts the oval under the feet of the frame on screen. Checks can pass the camera they render with.
func refresh(camera: Camera3D = null) -> void:
	if sprite == null or _mat == null or not is_inside_tree():
		return
	var cam := camera if camera != null else get_viewport().get_camera_3d()
	if cam == null:
		return
	var k := sprite.size_scale()
	var feet := sprite.feet_model()
	if feet.is_empty() and not feet_texels.is_empty():
		var px := sprite.pixel_size
		feet = {"front": float(feet_texels["front"]) * px, "rear": float(feet_texels["rear"]) * px,
				"half_width": float(feet_texels["half_width"]) * px}
	if feet.is_empty():
		feet = {"front": DEFAULT_FEET["front"] * k, "rear": DEFAULT_FEET["rear"] * k, "half_width": DEFAULT_FEET["half_width"] * k}
	var f := sprite.drawn_facing(cam.global_basis)
	var ra: float = (feet["front"] - feet["rear"]) / 2.0 + PAD_ALONG * k
	var rc: float = float(feet.get("shadow_half_width", feet["half_width"])) + PAD_ACROSS * k
	var at: Vector3 = (get_parent() as Node3D).global_position + f * ((feet["front"] + feet["rear"]) / 2.0) + Vector3.UP * LIFT
	global_transform = Transform3D(Basis(f * ra, Vector3.UP, f.cross(Vector3.UP) * rc), at)
	_mat.set_shader_parameter("radii", Vector2(ra, rc))
