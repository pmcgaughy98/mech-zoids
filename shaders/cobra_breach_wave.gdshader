shader_type spatial;
// Breach, the knock-back on the far side (cobra effects lane, 2026-11-14, take 2): at `burst` one wave runs out across
// the floor from the far face, forward half only, out to 3 m in 0.3 s, then gone. The floor wavers under it (the scene
// sampled shifted) and only a thin pale line rides the crest; take 1's crest was a thick flat yellow band.
// Plane-local metres (varying lp), +Z away from the wall. blend_mix.
render_mode unshaded, blend_mix, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform float radius = 0.0;
uniform float amount = 0.0;
uniform vec3 hot_col : source_color = vec3(1.0, 0.98, 0.80);
uniform vec3 warm_col : source_color = vec3(0.92, 0.84, 0.18);

varying vec3 lp;

void vertex() {
	lp = VERTEX;
}

void fragment() {
	vec2 p = lp.xz;
	float r = length(p);
	float fwd = smoothstep(-0.3, 0.5, p.y);
	float swell = exp(-pow((r - radius + 0.08) / 0.3, 2.0)); // the warp, wider and just behind the line
	float line = exp(-pow((r - radius) / 0.06, 2.0));
	float m = fwd * max(swell * 0.9, line) * amount;
	vec2 off = (p / max(r, 0.001)) * swell * 0.014 * fwd * amount;
	vec3 bg = texture(screen_tex, SCREEN_UV + off).rgb;
	vec3 col = mix(bg, mix(warm_col, hot_col, 0.6) * 1.15, clamp(line * fwd * amount * 0.6, 0.0