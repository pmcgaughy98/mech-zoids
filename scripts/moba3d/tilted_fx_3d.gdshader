// The tilted quad for see-through effects (Claude, 2026-11-05, game feel lane, effects spin-off): the fennec's small
// gate (small_gate.gd) and its bolt (fennec_bolt.gd). The vertex is tilted_sprite_3d.gdshader's, unchanged: the quad faces the camera fully, pivots
// on its feet row (lift metres under the node) and keeps the depth an upright sprite would have, so the effect stands
// on the floor beside a tilted machine and sorts with it the same way. The difference is the fragment: alpha is
// blended (the gate's swirl is part see-through), not cut, so it draws after the machines and writes no depth.
shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never;

uniform sampler2D tex : source_color, filter_nearest;
uniform float lift = 0.0; // metres from the feet up to the node's origin
// The blink's ghost (blink_flash.gd): the machine's own frame drawn in light. All four are off by default, so the
// gate and the bolt draw their colours unchanged.
uniform vec4 tint : source_color = vec4(1.0); // the shape's colour
uniform float tint_mix = 0.0; // 0 draws the texture's colours, 1 the shape in tint alone
uniform vec4 rim : source_color = vec4(0.247, 0.910, 0.690, 1.0); // the shape's outside texels (the fennec's mint)
uniform float rim_mix = 0.0;
uniform float fade = 1.0; // multiplies alpha
uniform float scan = 0.0; // drops this share of every 3 texel rows (1/3 or 2/3): a shimmer
// The cell of a sheet this instance shows (x, y, width, height in UV), set per node with
// set_instance_shader_parameter, so many bolts and sparks share one material (fennec_bolt.gd).
instance uniform vec4 uv_rect = vec4(0.0, 0.0, 1.0, 1.0);

void vertex() {
	vec3 s = vec3(length(MODEL_MATRIX[0].xyz), length(MODEL_MATRIX[1].xyz), length(MODEL_MATRIX[2].xyz));
	vec3 from_feet = (VERTEX + vec3(0.0, lift, 0.0)) * s;
	vec3 feet = MODEL_MATRIX[3].xyz - vec3(0.0, lift * s.y, 0.0);
	vec3 world = feet + mat3(INV_VIEW_MATRIX[0].xyz, INV_VIEW_MATRIX[1].xyz, INV_VIEW_MATRIX[2].xyz) * from_feet;
	vec4 v = VIEW_MATRIX * vec4(world, 1.0);
	float t = max(from_feet.y, 0.0);
	float tan_pitch = max(INV_VIEW_MATRIX[2].y, 0.0) / max(INV_VIEW_MATRIX[1].y, 0.05);
	tan_pitch = min(tan_pitch, 1.43);
	float push = min(t * tan_pitch, 0.8 * max(-v.z, 0.0));
	vec4 clip = PROJECTION_MATRIX * v;
	vec4 upright = PROJECTION_MATRIX * vec4(v.xy, v.z + push, 1.0);
	POSITION = vec4(clip.xy, upright.z / upright.w * clip.w, clip.w);
}

void fragment() {
	vec2 uv = uv_rect.xy + UV * uv_rect.zw;
	vec4 c = texture(tex, uv);
	if (c.a < 0.02) {
		discard;
	}
	vec2 texel = 1.0 / vec2(textureSize(tex, 0));
	if (scan > 0.0 && mod(floor(uv.y / texel.y), 3.0) < scan * 3.0 - 0.01) {
		discard;
	}
	vec3 col = mix(c.rgb, tint.rgb, tint_mix);
	if (rim_mix > 0.0) {
		float inside = texture(tex, uv + vec2(texel.x, 0.0)).a * texture(tex, uv - vec2(texel.x, 0.0)).a
			* texture(tex, uv + vec2(0.0, texel.y)).a * texture(tex, uv - vec2(0.0, texel.y)).a;
		col = mix(col, rim.rgb, rim_mix * step(inside, 0.5));
	}
	ALBEDO = col;
	ALPHA = (tint_mix > 0.0 ? 1.0 : c.a) * fade;
}
