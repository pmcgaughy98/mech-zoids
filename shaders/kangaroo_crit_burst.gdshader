shader_type spatial;
// Kangaroo title bout, an on-beat (crit) punch (kangaroo effects lane, 2026-11-11). A small camera-facing burst on the
// target: a white-hot core for the first frames, four short rays and a thin ring opening out. Small and short on
// purpose (Preston cut the big white flash on the rhino). Only the core goes over HDR 1.05.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled, depth_test_disabled;
uniform vec3 mint = vec3(0.32, 1.0, 0.78);
uniform float t = 0.0; // 0 to 1 over the burst's life
uniform float spin = 0.0;

void fragment() {
	vec2 p = (UV - 0.5) * 2.0;
	float r = length(p);
	float a = atan(p.y, p.x) + spin;
	float core = exp(-pow(r / mix(0.22, 0.05, t), 2.0)) * (1.0 - t);
	float rays = pow(abs(cos(a * 2.0)), 40.0) * exp(-r / mix(0.25, 0.7, t)) * (1.0 - t);
	float ring_r = mix(0.2, 0.9, sqrt(t));
	float ring = exp(-pow((r - ring_r) / 0.04, 2.0)) * (1.0 - t);
	vec3 col = mix(mint, vec3(1.0), 0.7) * core * 1.8 + mint * (rays * 0.9 + ring * 0.7);
	ALBEDO = col;
	ALPHA = clamp(core + rays + ring, 0.0, 1.0) * step(r, 1.0);
}
