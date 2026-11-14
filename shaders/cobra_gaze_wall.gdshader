shader_type spatial;
// Hood Gaze, the front of the cone (cobra effects lane, 2026-11-14, phase pass): a curved sheet with height (the cobra
// height) that sweeps out to the range. It is a soft membrane: the world seen through it wavers (screen-space warp)
// and two sets of gold bands at near frequencies slide against each other and beat into slow swells, brightest at
// its foot. UV.x across the arc, UV.y up. blend_mix (it shows the warped scene plus its glow); only the foot and the
// arrival flash go above HDR 1.05.
render_mode unshaded, blend_mix, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform float amount = 0.0;
uniform float flash = 0.0;
uniform float age = 0.0;
uniform float seed = 0.0;
uniform vec3 hot_col : source_color = vec3(1.0, 0.98, 0.80);
uniform vec3 warm_col : source_color = vec3(0.92, 0.84, 0.18);

void fragment() {
	float u = UV.x;
	float v = UV.y;
	float ends = smoothstep(0.0, 0.12, u) * (1.0 - smoothstep(0.88, 1.0, u));
	float top = 1.0 - smoothstep(0.35, 1.0, v);
	float foot = 1.0 - smoothstep(0.0, 0.1, v);
	float mask = ends * top * amount;
	float b1 = sin(v * 36.0 - age * 13.0 + sin(u * 8.0 + age * 2.0 + seed) * 1.3);
	float b2 = sin(v * 41.0 + age * 9.0 + u * 3.0);
	float beat = smoothstep(0.35, 1.0, b1 * b2);
	vec2 off = vec2(sin(v * 18.0 - age * 11.0 + u * 7.0), cos(u * 13.0 + age * 8.0 + v * 5.0)) * 0.014 * mask;
	vec3 bg = texture(screen_tex, SCREEN_UV + off).rgb;
	vec3 glow = warm_col * (0.12 + 0.5 * beat) * top + hot_col * (foot * 0.9 + flash * 0.4 * top);
	ALBEDO = bg + glow * ends * amount;
	ALPHA = clamp(max(mask, foot * ends * amount), 0.0, 1.0);
}
