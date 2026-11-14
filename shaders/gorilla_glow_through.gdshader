shader_type spatial;
// Gorilla, the chest charge during the ult's wind-up (gorilla effects lane, 2026-11-14). Smooth, not pixel. A soft lime
// glow that faces the camera and is drawn over the body, so the chest itself seems to light up from inside. The
// script sets strength and spread every frame: it steps up with each chest hit. Kept soft so the gorilla is never
// washed out: the middle never goes fully opaque and only a little of it turns toward white.
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled, shadows_disabled, blend_add, fog_disabled;
uniform float strength = 0.0;
uniform float spread = 1.0; // 0.5 a small glow, 1.0 the full quad
uniform vec3 lime = vec3(0.62, 1.0, 0.16);

void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	MODELVIEW_NORMAL_MATRIX = mat3(MODELVIEW_MATRIX);
}

void fragment() {
	vec2 p = (UV - 0.5) * 2.0;
	float edge = length(p);
	float d = edge / max(spread, 0.05);
	float core = exp(-(d * d) / 0.05);
	float halo = exp(-(d * d) / 0.3) * 0.45;
	float body = (core * 0.6 + halo) * strength * (1.0 - smoothstep(0.85, 1.0, edge));
	ALBEDO = mix(lime, vec3(1.0), core * 0.3);
	ALPHA = clamp(body, 0.0, 0.8);
}
