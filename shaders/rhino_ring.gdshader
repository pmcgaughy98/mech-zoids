shader_type spatial;
// Rhino effects lane, Heave tell (2026-11-12): a camera-facing ring that swells out from the horn like a struck
// tuning fork, or (core > 0) the soft glow on the horn itself. Additive, writes ALPHA, fog off.
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled, shadows_disabled, blend_add, fog_disabled;

uniform float age = 0.0;
uniform float life = 0.35;
uniform float size = 1.0;
uniform float strength = 1.0;
uniform float core = 0.0;
uniform vec3 tint = vec3(0.55, 1.0, 0.85);

void vertex() {
	VERTEX *= size;
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
}

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float d = length(p);
	float t = clamp(age / life, 0.0, 1.0);
	float grow = 1.0 - (1.0 - t) * (1.0 - t);
	float r = mix(0.12, 0.95, grow);
	float w = mix(0.11, 0.035, t);
	float k = (d - r) / w;
	float ring = exp(-k * k) * (1.0 - t) * strength;
	float glow = core * exp(-d * d * 7.0);
	float a = clamp(ring + glow, 0.0, 1.0);
	ALBEDO = mix(tint, vec3(1.0), clamp(ring * 0.6 + glow * 0.7, 0.0, 1.0));
	ALPHA = a;
}
