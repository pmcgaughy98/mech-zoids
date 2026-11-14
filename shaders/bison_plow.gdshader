shader_type spatial;
// Plow bow wave (bison effects lane, 2026-11-13). A standing wall of burning earth thrown up along the plow's arc: an
// ImmediateMesh strip rebuilt each frame, one column per sample of the head's sweep, so it has height from every camera
// and is never a flat strip on the floor. Per vertex: COLOR.r = heat (1 where the head just passed, cooling behind it),
// COLOR.a = fade (the script also fades both ends). UV.x = metres along the arc, UV.y = 0 at the floor, 1 at the top.
// Mixed, not added: additive orange over the blue arena floor washed out to peach in the first take. Ragged flame
// tongues scroll up; a hot base (cores above HDR 1.05 there only), a deep magma body, sooty tips; as a column cools it
// darkens toward soot and sinks. Not the rhino's swipe: that is a thin bright crescent in the air; this is a heavy
// wall rising out of the ground.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix;

uniform vec3 hot_col : source_color = vec3(1.0, 0.93, 0.70);
uniform vec3 warm_col : source_color = vec3(1.0, 0.36, 0.06);
uniform vec3 soot_col : source_color = vec3(0.10, 0.07, 0.055);

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void fragment() {
	float h = clamp(COLOR.r, 0.0, 1.0);
	float y = UV.y;
	float n1 = vnoise(vec2(UV.x * 4.0, y * 2.5 - TIME * 4.0));
	float n2 = vnoise(vec2(UV.x * 9.0, y * 5.0 - TIME * 7.0));
	float n = n1 * 0.6 + n2 * 0.4;
	float e = y + (n - 0.5) * 0.9 + 0.3 * (1.0 - h); // tongue height falls as the column cools
	float body = (1.0 - smoothstep(0.45, 0.75, e)) * smoothstep(0.0, 0.06, y);
	float base = (1.0 - smoothstep(0.0, 0.35, y)) * h;
	vec3 fire = mix(warm_col * 0.95, hot_col * 1.5, base * base * smoothstep(0.35, 0.8, n2 + 0.2));
	fire *= 0.4 + 0.6 * h;
	float soot = smoothstep(0.25, 0.65, e) * (1.0 - 0.5 * h);
	ALBEDO = mix(fire, soot_col, soot);
	ALPHA = clamp(body * COLOR.a * mix(0.9, 0.6, soot), 0.0, 1.0);
}
