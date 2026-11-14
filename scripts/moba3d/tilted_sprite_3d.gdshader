// The tilted machine sprite (Claude, 2026-11-04, game feel lane), used by DirectionalSprite3D when tilt_to_camera is
// on, a test that is off in the game. The quad faces the camera fully, pivoting on the feet row, lift metres under the node.
// It is drawn where the tilted quad is, but its depth is the depth today's upright sprite would have at that row's
// height. A tilted quad leans back by the camera's pitch, so its top would otherwise sink into a wall or tower standing
// just behind the machine; with upright depth, things behind it stay behind and things in front still hide it.
// A row t metres up the quad shows what stands about t / cos(pitch) metres up an upright one, whose depth is
// t * tan(pitch) nearer the camera than the feet (the orthographic estimate; the chase camera is close to that).
// The quad has only its four corners, so that depth is exact at the top corners only. The bottom corners (the canvas
// edge, below the feet) keep the feet's depth, and rows in between are interpolated. So the feet row itself ends up
// about 0.3 to 0.4 m nearer the camera than the anchor (rhino, 192 canvas, feet edge 161; less on smaller canvases),
// and a few rows below the feet are still nearer than the floor in front of them. Body radii keep other units
// farther off than that.
// SpriteBase3D hands its texture only to its own material, so DirectionalSprite3D sets "tex" on each frame change.
shader_type spatial;
render_mode unshaded, cull_disabled;

uniform sampler2D tex : source_color, filter_nearest;
uniform float lift = 0.0; // metres from the feet up to the node's origin (DirectionalSprite3D raises the node by this)

void vertex() {
	vec3 s = vec3(length(MODEL_MATRIX[0].xyz), length(MODEL_MATRIX[1].xyz), length(MODEL_MATRIX[2].xyz));
	vec3 from_feet = (VERTEX + vec3(0.0, lift, 0.0)) * s; // the quad measured from the feet row, the pivot
	vec3 feet = MODEL_MATRIX[3].xyz - vec3(0.0, lift * s.y, 0.0);
	vec3 world = feet + mat3(INV_VIEW_MATRIX[0].xyz, INV_VIEW_MATRIX[1].xyz, INV_VIEW_MATRIX[2].xyz) * from_feet;
	vec4 v = VIEW_MATRIX * vec4(world, 1.0);
	float t = max(from_feet.y, 0.0); // metres up the quad from the feet
	float tan_pitch = max(INV_VIEW_MATRIX[2].y, 0.0) / max(INV_VIEW_MATRIX[1].y, 0.05);
	// Steep cameras (the ult rise, 70 and 85 degrees; camera lane, 2026-11-04): t * tan(pitch) grows past the camera
	// and the quad was clipped away. The slope stops at 55 degrees' (game camera 30 and the ult's 55 are unchanged),
	// and the push never passes 80% of the way to the camera, so a sprite close to the lens can't cross it either.
	tan_pitch = min(tan_pitch, 1.43);
	float push = min(t * tan_pitch, 0.8 * max(-v.z, 0.0));
	vec4 clip = PROJECTION_MATRIX * v;
	vec4 upright = PROJECTION_MATRIX * vec4(v.xy, v.z + push, 1.0);
	POSITION = vec4(clip.xy, upright.z / upright.w * clip.w, clip.w);
}

void fragment() {
	vec4 c = texture(tex, UV) * COLOR;
	if (c.a < 0.5) {
		discard;
	}
	ALBEDO = c.rgb;
}
