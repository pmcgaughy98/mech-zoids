shader_type spatial;
// Hippo Pressure Tanks (hippo effects lane, 2026-11-12): the toxic liquid inside the flank tank windows. Drawn on an
// oval panel fitted into each window, riding the hippo's spine bone. UV x runs along the window, UV y down it. The level is the
// kit's pressure; above it the glass reads dark and empty, at the line a pale meniscus that sloshes, below it the
// liquid with bubbles rising (boiling when overcharged). Only the overcharged meniscus goes above 1.0.
render_mode unshaded, blend_mix, cull_back, depth_draw_never, fog_disabled, shadows_disabled;

uniform float fill : hint_range(0.0, 1.0) = 0.5;
uniform float slosh = 0.0;
uniform float boil = 0.0;
uniform float bright = 1.0;
uniform float seed = 0.0;
uniform vec3 deep : source_color = vec3(0.20, 0.05, 0.30);
uniform vec3 liquid : source_color = vec3(0.58, 0.22, 0.78);
uniform vec3 shine : source_color = vec3(0.86, 0.66, 0.98);
uniform vec3 glass : source_color = vec3(0.07, 0.03, 0.11);

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	float v = 1.0 - UV.y;
	float u = UV.x;
	vec2 e = (UV - 0.5) * 2.0;
	vec2 e2 = e * e;
	float oval = 1.0 - smoothstep(0.82, 1.0, dot(e2, e2));  // a rounded rectangle, like the window
	float t = TIME + seed;
	float wave = sin(u * 8.0 + t * 2.6) * 0.018 + sin(u * 15.0 - t * 3.9) * 0.010;
	wave += sin(u * 5.0 + t * 7.0) * 0.05 * slosh;
	wave += sin(u * 23.0 + t * 11.0) * 0.012 * boil;
	float lvl = mix(-0.03, 1.03, fill) + wave;
	float below = 1.0 - smoothstep(lvl - 0.012, lvl + 0.012, v);
	float d = (v - lvl) / 0.045;
	float line = exp(-d * d) * step(0.01, fill) * step(fill, 0.995);
	// bubbles rising through the liquid
	vec2 g = vec2(u * 7.0, v * 5.0 - t * (0.7 + boil * 2.2));
	vec2 id = floor(g);
	vec2 f = fract(g) - 0.5;
	float h = hash(id + seed);
	vec2 c = vec2(h - 0.5, fract(h * 7.31) - 0.5) * 0.5;
	float bub = smoothstep(0.17, 0.09, length(f - c)) * step(0.62 - boil * 0.4, h) * below;
	float depth = clamp(v / max(lvl, 0.05), 0.0, 1.0);
	vec3 col = mix(deep, liquid, 0.35 + 0.65 * depth) * bright;
	col += shine * bub * 0.35;
	col = min(col, vec3(0.98));
	vec3 rim = shine * (0.9 + 0.35 * boil);  // the meniscus: the one bright core, above 1.0 only when boiling
	vec3 outc = mix(glass, col, below);
	outc = mix(outc, rim, clamp(line, 0.0, 1.0));
	ALBEDO = outc;
	ALPHA = clamp(mix(0.86, 0.95, below) + line * 0.3, 0.0, 0.98) * oval;
}
