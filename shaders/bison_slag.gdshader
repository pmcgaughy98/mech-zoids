shader_type spatial;
// Slag patch where a bison bomb lands (bison effects lane, 2026-11-13). A flat quad on the floor; give the material
// render_priority 3 (over the arena's see-through floor zones). It must read as crusted molten rock, not a liquid
// (the hippo's toxic lake owns the liquid look): matte dark crust plates, glowing seams between them that narrow and
// dim as it cools, a crust rim pushed up at the edge, a dark scorch halo round it, no ripples, no shine, no flow.
// Lumps with height sit on it (bison_bomb.gdshader meshes, placed by the observer).
// Structure from Magma Bomb's landing (SMITE 2, measured): a dark scorch with small hot spots stays after the burst.
// Seam cores above HDR 1.05 while hot, the rest under. Lit, blend_mix, fog_disabled.
render_mode blend_mix, depth_draw_never, cull_disabled, shadows_disabled, fog_disabled, diffuse_burley, specular_disabled;

uniform vec3 hot_col : source_color = vec3(1.0, 0.97, 0.92);
uniform vec3 warm_col : source_color = vec3(0.95, 0.88, 0.74);
uniform vec3 crust_col : source_color = vec3(0.07, 0.064, 0.06);
uniform vec3 scorch_col : source_color = vec3(0.03, 0.028, 0.026);
uniform float life = 4.5;
instance uniform float age = 0.0;
instance uniform float seed = 0.0;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7)) + seed) * 43758.5453); }
float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
vec2 hash2(vec2 p) {
	p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
	return fract(sin(p + vec2(seed)) * 43758.5453);
}
// F2 - F1: 0 on a seam between plates.
float cell_edge(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	float d1 = 8.0;
	float d2 = 8.0;
	for (int x = -1; x <= 1; x++) {
		for (int y = -1; y <= 1; y++) {
			vec2 g = vec2(float(x), float(y));
			vec2 r = g + hash2(i + g) - f;
			float d = dot(r, r);
			if (d < d1) {
				d2 = d1;
				d1 = d;
			} else if (d < d2) {
				d2 = d;
			}
		}
	}
	return sqrt(d2) - sqrt(d1);
}

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float spread = mix(0.45, 1.0, smoothstep(0.0, 0.18, age));
	float wob = (noise(p * 2.2 + seed) - 0.5) * 0.5 + (noise(p * 5.0 - seed) - 0.5) * 0.18;
	float r = length(p) / spread + wob;
	float t = clamp(age / life, 0.0, 1.0);
	float heat = 1.0 - smoothstep(0.0, 1.0, t);
	float slag = 1.0 - smoothstep(0.55, 0.64, r);
	float scorch = 1.0 - smoothstep(0.64, 0.98, r);
	float e = cell_edge(p * 3.4 + vec2(seed * 0.37));
	float e2 = cell_edge(p * 8.0 + vec2(3.1));
	float w = mix(0.025, 0.13, heat) * (1.0 - smoothstep(0.1, 0.6, r) * 0.5);
	float seam = (1.0 - smoothstep(0.0, w, e)) * slag;
	float fine = (1.0 - smoothstep(0.0, w * 0.45, e2)) * slag * heat * 0.5;
	float core = (1.0 - smoothstep(0.0, w * 0.35, e)) * slag;
	float centre = 1.0 - smoothstep(0.0, 0.62, r);
	float plate = smoothstep(0.0, 0.35, e);
	vec3 crust = crust_col * (0.75 + 0.5 * plate + 0.25 * noise(p * 14.0));
	crust += vec3(0.035) * smoothstep(0.4, 0.58, r) * slag;
	ALBEDO = mix(scorch_col, crust, slag);
	ROUGHNESS = 0.95;
	float k = heat * (0.55 + 0.45 * centre);
	EMISSION = (warm_col * 0.8 * max(seam, fine) + hot_col * 1.4 * core * heat) * k;
	float fade = 1.0 - smoothstep(0.8, 1.0, t);
	float grow_in = smoothstep(0.0, 0.04, age);
	ALPHA = clamp(max(slag, scorch * 0.55) * fade * grow_in, 0.0, 1.0);
}
