shader_type spatial;
// Hippo Piston Drop, the floor (hippo effects lane, 2026-11-11). One quad per landing, centred on it. Kit plan
// (docs/plan/hippo-kit-pressure-2026-11-11.md): the landing pumps pressure into the floor and the ground erupts and
// stuns about 0.5 s later. Toxic purple to match the Vent (Preston). blend_mix so the liquid can be dark and wet; only
// the eruption core and the vein peaks go above HDR 1.05.
//   age 0 to 0.35:    a thin liquid shock ring rolls out from the belly to the radius
//   age 0 to erupt:   the warning: a filled disc, a rim that pumps faster and faster, veins that brighten
//   age erupt:        a short pale core, then a splashed toxic pool that bubbles and shrinks away
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;

uniform float radius_m = 3.2;
uniform float extent = 1.3;   // the quad spans radius * extent each way
uniform float age = 0.0;
uniform float erupt = 0.5;    // seconds from the landing to the eruption
uniform float pool_life = 1.3;
uniform float flash_mul = 1.0; // 0 for drips and splats that should not flash (Lockjaw trail)
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
	vec2 p = (UV * 2.0 - 1.0) * radius_m * extent; // metres from the landing
	float d = length(p);
	float ang = atan(p.y, p.x);
	float r = radius_m;
	float in_disc = 1.0 - smoothstep(r - 0.05, r + 0.08, d);

	// shock ring from the landing
	float st = clamp(age / 0.35, 0.0, 1.0);
	float ring_r = mix(0.6, r, 1.0 - pow(1.0 - st, 3.0));
	float wob = (noise(vec2(ang * 3.0, 1.0)) - 0.5) * 0.15;
	float shock = exp(-pow((d - ring_r - wob) / 0.12, 2.0)) * (1.0 - st) * step(age, 0.35);

	// the warning: rim pumping faster toward the eruption, veins brightening
	float wt = clamp(age / erupt, 0.0, 1.0);
	float warn_on = step(age, erupt) * smoothstep(0.0, 0.08, age);
	float beat = 0.5 + 0.5 * cos(6.2832 * (age * (3.0 + 9.0 * wt)));
	float rim = exp(-pow((d - r) / 0.09, 2.0)) * (0.45 + 0.55 * beat) * warn_on;
	float vein_n = noise(vec2(ang * 7.0 + seed, d * 1.6)) ;
	float veins = smoothstep(0.08, 0.0, abs(vein_n - 0.5)) * in_disc * warn_on * (0.25 + 0.75 * wt);
	float disc = in_disc * warn_on * (0.18 + 0.2 * wt);

	// eruption: a short pale core (0.07 s) then a splashed pool shrinking away
	float et = age - erupt;
	float flash = (et >= 0.0) ? flash_mul * exp(-et / 0.05) * (1.0 - smoothstep(0.0, r * 0.9, d)) : 0.0;
	float pt = clamp(et / pool_life, 0.0, 1.0);
	float blot = noise(p * 1.1 + seed) * 0.55 + noise(p * 2.7 - seed) * 0.3 + noise(p * 7.0) * 0.15;
	float splash_edge = r * (0.6 + 0.3 * noise(vec2(ang * 5.0, seed))); // ragged edge inside the rim (first take flooded the screen)
	float lvl = blot + 0.1 - pt * 0.9 - smoothstep(splash_edge - 0.4, splash_edge, d);
	float pool_on = step(0.0, et) * step(et, pool_life);
	float wet = smoothstep(0.0, 0.05, lvl) * pool_on;
	float lip = exp(-pow(lvl / 0.035, 2.0)) * pool_on;
	vec2 cell = floor(p * 2.0);
	vec2 bp = (cell + 0.2 + 0.6 * hash2(cell)) / 2.0;
	float ph = fract(et * 1.1 + hash(cell + 3.1));
	float bub = exp(-pow((length(p - bp) - (0.03 + 0.09 * ph)) / 0.018, 2.0)) * (1.0 - ph) * step(0.55, hash(cell + 7.7)) * wet;

	float warn_a = max(disc, max(rim * 0.9, veins * 0.8));
	vec3 warn_c = mix(liquid * 1.5, shine * (1.0 + 0.6 * wt), clamp(rim + veins, 0.0, 1.0)) + hot * veins * wt * 0.4;
	float pool_a = max(wet * (0.55 + 0.25 * bub), lip * 0.8);
	vec3 pool_c = mix(liquid * 1.6, shine * 1.1, 0.3 + 0.3 * smoothstep(0.6, 1.0, blot) + bub * 0.7) + shine * lip * 0.6;

	float a = max(max(warn_a, pool_a), max(shock * 0.85, flash * 0.9));
	vec3 col = pool_c;
	if (warn_a >= pool_a) { col = warn_c; }
	col = mix(col, shine * 1.2, clamp(shock * 1.2, 0.0, 1.0));
	col = mix(col, hot * 1.4, clamp(flash, 0.0, 1.0));
	ALBEDO = col;
	ALPHA = clamp(a, 0.0, 0.92);
}
