shader_type spatial;
// Hood Gaze, the cone on the floor (cobra effects lane, 2026-11-14, phase pass). The kit power is making solid matter
// go soft, so the ground the gaze crosses goes soft: waves roll out across it from the hood, the floor behind them
// wavers (the scene is sampled shifted along the waves), and their crests catch the gold. A bright line marks the
// front. Plane-local metres (varying lp), +Z is the cobra facing. blend_mix: the warped floor replaces the floor.
render_mode unshaded, blend_mix, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;
#include "res://shaders/cobra_noise.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform float range_m = 6.0;
uniform float half_angle = 0.61;
uniform float r_in = 0.9;
uniform float front = 0.0;
uniform float amount = 0.0;
uniform float arrive = 0.0;
uniform float age = 0.0;
uniform float seed = 0.0;
uniform vec3 hot_col : source_color = vec3(1.0, 0.98, 0.80);
uniform vec3 warm_col : source_color = vec3(0.92, 0.84, 0.18);

varying vec3 lp;

void vertex() {
	lp = VERTEX;
}

void fragment() {
	vec2 p = lp.xz;
	float r = length(p);
	float a = atan(p.x, p.y);
	float side = half_angle - abs(a);
	float wedge = smoothstep(0.0, 0.05, side) * smoothstep(r_in, r_in + 0.4, r);
	float swept = 1.0 - smoothstep(front - 0.15, front + 0.02, r);
	float soft = wedge * swept;
	// waves bent a little by noise so they read as a soft surface, not rings drawn on the floor
	float bend = (c_vnoise(p * 0.9 + seed) - 0.5) * 1.6;
	float ph = r * 6.5 - age * 11.0 + bend;
	float w = sin(ph);
	float crest = smoothstep(0.55, 1.0, w);
	float trough = smoothstep(0.2, 1.0, -w);
	vec2 off = vec2(cos(ph), sin(ph * 0.7 + a * 3.0)) * 0.006 * soft;
	vec3 bg = texture(screen_tex, SCREEN_UV + off).rgb;
	float fresh = exp(-max(front - r, 0.0) * 0.5);
	vec3 gold = warm_col * (1.1 + 0.5 * arrive) + hot_col * 0.3 * arrive;
	float tint = soft * (0.2 + 0.65 * crest * (0.5 + 0.5 * fresh));
	vec3 col = mix(bg * (1.0 - 0.25 * trough * soft), gold, tint);
	float rim = (1.0 - smoothstep(0.0, 0.06, side)) * smoothstep(-0.03, 0.0, side) * smoothstep(r_in, r_in + 0.3, r) * swept;
	float line = exp(-pow((r - front) / 0.14, 2.0)) * smoothstep(-0.02, 0.05, side) * step(r_in, r);
	col = mix(col, gold, clamp(rim * 0.5, 0.0, 1.0));
	col = mix(col, mix(warm_col, hot_col, 0.5) * (1.2 + 0.4 * arrive), clamp(line * 0.85, 0.0, 1.0));
	float al = max(soft, max(rim * 0.5, line * 0.85));
	ALBEDO = col;
	ALPHA = clamp(al * amount, 0.0, 1.0);
}
