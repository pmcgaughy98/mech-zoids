shader_type spatial;
// Smooth dust puff (rhino effects lane, 2026-11-11). Replaces the kit's pixel impact_puff and dust_trail sprites during
// the tremor. A camera-facing quad: a soft billowing cloud that swells, rises a little and thins out. Warm grey, under
// the bloom threshold, so it reads as earth thrown up and never as light.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;

uniform float age = 0.0;
uniform float life = 0.7;
uniform float seed = 0.0;
uniform vec3 dust : source_color = vec3(0.56, 0.50, 0.43);
uniform float strength = 0.75;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7)) + seed) * 43758.5453); }
float noise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0.0, 0.0, 0.0),
		vec4(0.0, length(MODEL_MATRIX[1].xyz), 0.0, 0.0), vec4(0.0, 0.0, length(MODEL_MATRIX[2].xyz), 0.0),
		vec4(0.0, 0.0, 0.0, 1.0));
}

void fragment() {
	float t = clamp(age / life, 0.0, 1.0);
	vec2 p = UV * 2.0 - 1.0;
	p.y += 0.25 * t; // the cloud drifts up inside its quad
	float grow = mix(0.45, 1.0, 1.0 - pow(1.0 - t, 2.0));
	vec2 q = p / grow;
	float n = noise(q * 3.0 + seed) * 0.6 + noise(q * 6.5 - seed + t) * 0.4;
	float body = 1.0 - smoothstep(0.35, 0.95, length(q) + (n - 0.5) * 0.55);
	float fade = smoothstep(0.0, 0.08, t) * (1.0 - smoothstep(0.35, 1.0, t));
	float a = body * fade * strength;
	ALBEDO = dust * (0.85 + 0.3 * n) * mix(1.15, 0.9, t);
	ALPHA = clamp(a, 0.0, 1.0);
}
