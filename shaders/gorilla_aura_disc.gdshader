shader_type spatial;
// Gorilla, the always-on ring under it (gorilla effects lane, 2026-11-12). Smooth, not pixel. It marks aura_radius,
// the reach of the gorilla's cover for allies. Quiet on purpose: it is on screen all match, so nothing in it comes
// near the bloom threshold (1.05). A thin lime rim in sixteen soft dashes (a range marker, as the pixel ring was),
// a faint glow just inside it, a barely-there fill, one slow breath. The dashes turn very slowly.
// x is metres from the rim (negative inside), so the rim keeps its thickness whatever the radius.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;
uniform float age = 0.0;
uniform float extent = 1.12; // quad half-size in units of the radius
uniform float radius_m = 2.5;
uniform float strength = 1.0;
uniform float seed = 0.0;
uniform vec3 lime = vec3(0.62, 1.0, 0.16);
uniform vec3 edge = vec3(0.62, 1.0, 0.16); // the rim only; an enemy gorilla's takes its team colour

void fragment() {
	vec2 p = (UV - 0.5) * 2.0 * extent;
	float d = length(p);
	float a = atan(p.y, p.x);
	float x = (d - 1.0) * radius_m;
	float inside = step(x, 0.0);
	float rim = exp(-(x * x) / (0.04 * 0.04));
	float halo = exp(-(x * x) / (0.13 * 0.13)) * 0.07;
	float glow = smoothstep(-0.6, 0.0, x) * inside;
	glow = glow * glow * 0.09;
	float fill = inside * 0.018;
	float dash = mix(0.22, 1.0, smoothstep(-0.25, 0.25, sin(a * 16.0 - age * 0.35 + seed)));
	float breath = 0.88 + 0.12 * sin(age * 2.6 + seed);
	float body = (rim * 0.36 * dash + halo + glow + fill) * breath * strength * smoothstep(0.0, 0.4, age);
	ALBEDO = mix(lime, edge, clamp(rim * 1.5, 0.0, 1.0)) * 0.9;
	ALPHA = clamp(body, 0.0, 1.0);
}
