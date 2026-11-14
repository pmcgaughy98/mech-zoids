shader_type spatial;
// Smooth dust cloud for the gorilla's slam (gorilla effects lane, 2026-11-11). A camera-facing quad: a soft billowing
// cloud that swells, lifts a little and thins out. Structure from the rhino lane's dust; measured on SMITE 2's Geb,
// whose shock ring is a wall of dust and rock, not light: warm grey, always under the bloom threshold.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;
uniform float age = 0.0;
uniform float life = 0.6;
uniform float seed = 0.0;
uniform vec3 dust : source_color = vec3(0.60, 0.56, 0.47);
uniform float strength = 0.7;

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
	p.y += 0.22 * t;
	float grow = mix(0.5, 1.0, 1.0 - pow(1.0 - t, 2.0));
	vec2 q = p / grow;
	float n = noise(q * 2.6 + seed) * 0.6 + noise(q * 6.0 - seed + t * 1.3) * 0.4;
	float body = 1.0 - smoothstep(0.30, 0.95, length(q) + (n - 0.5) * 0.6);
	float fade = smoothstep(0.0, 0.07, t) * (1.0 - smoothstep(0.3, 1.0, t));
	ALBEDO = dust * (0.82 + 0.32 * n) * mix(1.12, 0.9, t);
	ALPHA = clamp(body * fade * strength, 0.0, 1.0);
}
