shader_type spatial;
// Hippo Toxic Flood, the lake (hippo effects lane, 2026-11-12). One quad centred on the hippo. Structure from SMITE 2's
// Intoxicate, measured (docs/reference/hippo-fx-synthesis-2026-11-11.md): one short bright beat, then a liquid pool with
// a ragged, splashy edge and lighter streaks on its surface, lying for seconds. Toxic purple (Preston). blend_mix so
// it is wet and dark; only ripple crests, bubble rims and the lip glow.
//   age 0 to spread: the edge rolls out behind the wave
//   while it lies:   ripples run outward, streaks drift, bubbles pop, a glowing lip at the edge
//   last 1 s:        it shrinks back from its edges into blotches and is gone
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;

uniform float radius_m = 6.0;
uniform float extent = 1.25;
uniform float age = 0.0;
uniform float spread = 0.45;
uniform float life = 4.0;
uniform float seed = 0.0;
uniform vec3 liquid : source_color = vec3(0.30, 0.07, 0.46);
uniform vec3 shine : source_color = vec3(0.78, 0.36, 1.0);
uniform vec3 hot : source_color = vec3(1.0, 0.82, 1.0);

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7)) + seed) * 43758.5453); }
vec2 hash2(vec2 p) { return vec2(hash(p), hash(p + 17.3)); }
float noise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

void fragment() {
	vec2 p = (UV * 2.0 - 1.0) * radius_m * extent;
	float d = length(p);
	float ang = atan(p.y, p.x);
	float grow = 1.0 - pow(1.0 - clamp(age / spread, 0.0, 1.0), 3.0);
	// ragged, splashy edge: big lobes plus small splash fingers
	float edge = radius_m * grow * (0.82 + 0.16 * noise(vec2(ang * 3.0, seed)) + 0.08 * noise(vec2(ang * 13.0, seed + 4.0)));
	float shrink = smoothstep(life - 1.0, life, age);
	float blot = noise(p * 0.7 + seed) * 0.55 + noise(p * 1.9 - seed) * 0.3 + noise(p * 5.0) * 0.15;
	float lvl = (edge - d) / max(radius_m, 0.01) * 4.0 + (blot - 0.5) * 0.6 - shrink * 1.6;
	float wet = smoothstep(0.0, 0.08, lvl);
	float lip = exp(-pow(lvl / 0.06, 2.0)) * step(0.001, grow) * (1.0 - shrink * 0.5);
	// ripples running outward from the centre
	float rip = 0.5 + 0.5 * sin(d * 3.2 - age * 7.0 + noise(p * 0.8) * 3.0);
	rip = pow(rip, 6.0) * smoothstep(0.0, 1.5, d);
	// streaks drifting on the surface
	float streak = smoothstep(0.62, 0.9, noise(vec2(ang * 6.0, d * 0.9 - age * 0.6)));
	// bubbles
	vec2 cell = floor(p * 1.6);
	vec2 bp = (cell + 0.2 + 0.6 * hash2(cell)) / 1.6;
	float ph = fract(age * 0.8 + hash(cell + 3.1));
	float bub = exp(-pow((length(p - bp) - (0.04 + 0.11 * ph)) / 0.02, 2.0)) * (1.0 - ph) * step(0.6, hash(cell + 7.7));
	// first take read as flat violet paint over the floor: darker, thinner body, so the crests, streaks and lip carry it
	vec3 col = mix(liquid * 0.9, shine * 1.05, 0.08 + 0.3 * streak + 0.7 * rip + 0.8 * bub) + shine * lip * 0.8 + hot * rip * 0.2;
	float a = max(wet * (0.42 + 0.12 * streak + 0.3 * rip + 0.25 * bub), lip * 0.85);
	ALBEDO = col;
	ALPHA = clamp(a, 0.0, 0.9);
}
