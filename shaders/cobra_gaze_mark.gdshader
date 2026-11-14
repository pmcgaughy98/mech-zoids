shader_type spatial;
// Hood Gaze, the ground under a slowed enemy (cobra effects lane, 2026-11-14, phase pass): the floor round its feet
// goes soft. Rings run out from it and the floor inside wavers (screen-space warp), so it reads as standing in ground
// that has turned liquid; cobra_phase_skin covers it to the ankles. Mesh: a PlaneMesh 2 m across, scaled by the
// script, so r runs 0..1. blend_mix: the warped floor replaces the floor under it.
render_mode unshaded, blend_mix, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform float amount = 0.0;
uniform float age = 0.0;
uniform float seed = 0.0;
uniform vec3 hot_col : source_color = vec3(1.0, 0.98, 0.80);
uniform vec3 warm_col : source_color = vec3(0.92, 0.84, 0.18);

varying vec3 lp;

void vertex() {
	lp = VERTEX;
}

void fragment() {
	float r = length(lp.xz);
	if (r > 1.0) {
		discard;
	}
	float disc = 1.0 - smoothstep(0.55, 1.0, r);
	float rings = 0.0;
	for (int i = 0; i < 3; i++) {
		float ph = fract(age * 1.3 + float(i) / 3.0 + seed);
		float rr = mix(0.15, 0.95, ph);
		rings += exp(-pow((r - rr) / 0.05, 2.0)) * (1.0 - ph) * smoothstep(0.0, 0.15, ph);
	}
	float wave = sin(r * 22.0 - age * 9.0);
	vec2 off = vec2(wave, wave * 0.6) * 0.005 * disc;
	vec3 bg = texture(screen_tex, SCREEN_UV + off).rgb;
	vec3 col = mix(bg * (1.0 - 0.15 * disc), warm_col * 1.15 + hot_col * 0.2, clamp(rings * 0.8, 0.0, 1.0));
	ALBEDO = col;
	ALPHA = clamp((disc * 0.9 + rings * 0.6) * amount, 0.0, 1.0);
}
