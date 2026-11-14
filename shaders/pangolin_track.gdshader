shader_type spatial;
// Pangolin iron ball ground track (pangolin effects lane, 2026-11-12). One short segment of the furrow the rolling
// ball presses into the floor: a soft darker groove with a pale dust lip either side, and at speed a thin hot line
// down the middle where the plates grind. Laid flat, local +Z along the roll. Structure from Geb's Roll Out (SMITE 2):
// a thin pale trail left on the floor behind the ball. Smooth, no pixel steps; only the hot line goes above 1.05.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;

uniform float age = 0.0;
uniform float life = 1.0;
uniform float heat = 0.0; // 0 at walking speed, 1 at full roll speed
uniform float seed = 0.0;
varying vec2 lp;
float sq(float x) { return x * x; } // pow(x, 2.0) is undefined for x < 0 in GLSL

float hash(float n) { return fract(sin(n * 12.9898 + seed) * 43758.5453); }

void vertex() {
	lp = VERTEX.xz; // -0.5 to 0.5 across (x) and along (z)
}

void fragment() {
	float x = abs(lp.x) * 2.0; // 0 centre, 1 edge
	float z = lp.y + 0.5;
	float ends = smoothstep(0.0, 0.25, z) * smoothstep(1.0, 0.75, z); // soft so segments blend into one furrow
	float fade = 1.0 - smoothstep(life * 0.35, life, age);
	float groove = (1.0 - smoothstep(0.25, 0.55, x)) * 0.42;
	float lip = exp(-sq((x - 0.7) / 0.14)) * 0.30 * (0.8 + 0.4 * hash(floor(z * 6.0)));
	float hot_t = 1.0 - smoothstep(0.0, 0.2 * life, age); // about 0.2 s: a short glowing tail, not a line to the horizon
	float line = exp(-sq(x / 0.06)) * heat * heat * hot_t;
	vec3 col = mix(vec3(0.66, 0.60, 0.52), vec3(0.10, 0.09, 0.08), groove / max(groove + lip, 0.001));
	col = mix(col, vec3(1.5, 0.85, 0.38), clamp(line * 1.3, 0.0, 1.0)); // amber grind line, blooms only at its hottest
	float a = max(max(groove, lip), line) * ends * fade;
	ALBEDO = col;
	ALPHA = clamp(a, 0.0, 1.0);
}
