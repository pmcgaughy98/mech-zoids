shader_type spatial;
// Rhino Brace, the held state (rhino effects lane, 2026-11-11): replaces the pixel brace_ring. A soft mint disc under
// the planted rhino with a brighter rim, slowly breathing, and five notches on the rim that light one per Seismic
// charge. Smooth, additive, nothing on a pixel grid. Only the lit notches and the rim's crest pass HDR 1.05.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;
uniform float age = 0.0;
uniform float charge = 0.0; // 0 to 5
uniform float flash = 0.0; // 1 on a new charge, decaying
uniform float fade = 1.0;
uniform vec3 mint = vec3(0.32, 1.0, 0.78);
void fragment() {
	vec2 p = (UV - 0.5) * 2.0; // rim at d = 0.85
	float d = length(p);
	float a = atan(p.x, -p.y); // 0 at the top (+Z forward after the plane's mapping), clockwise
	float breathe = 0.85 + 0.15 * sin(age * 3.2);
	float rim = exp(-pow((d - 0.85) / 0.05, 2.0));
	float fill = (1.0 - smoothstep(0.2, 0.85, d)) * 0.10 + smoothstep(0.45, 0.85, d) * step(d, 0.85) * 0.12;
	// five notches spaced round the rim, lit one per charge
	float seg = 6.28318 / 5.0;
	float k = floor(mod(a + seg * 0.5 + 6.28318, 6.28318) / seg);
	float local = mod(a + seg * 0.5 + 6.28318, 6.28318) - (k + 0.5) * seg;
	float notch = (1.0 - smoothstep(0.08, 0.13, abs(local))) * exp(-pow((d - 0.85) / 0.07, 2.0));
	float lit = step(k + 0.5, charge);
	vec3 c = mint * (rim * (0.9 + 0.5 * flash) + fill) * breathe;
	c += mix(mint * 0.35, vec3(1.6, 2.2, 1.9), lit) * notch * (1.0 + flash);
	float alpha = clamp(rim * 0.8 + fill + notch, 0.0, 1.0) * fade;
	ALBEDO = c * fade;
	ALPHA = alpha;
}
