shader_type spatial;
// Kangaroo boxing ring, the floor (kangaroo effects lane, 2026-11-11). One flat quad under the ring:
//   cast:  a small soft core at the centre and a wave that races out to the radius in about 0.2 s
//   held:  a soft glow either side of the wall's foot and a faint apron just inside it, so the ring's edge
//          reads on the floor even where the wall is seen edge-on
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;
uniform vec3 mint = vec3(0.32, 1.0, 0.78);
uniform float radius_m = 5.0;
uniform float extent = 6.2;   // half the quad's width, metres
uniform float wave = 0.0;     // 0 to 1: the cast wave's position as a share of the radius
uniform float wave_k = 0.0;   // the wave's strength
uniform float flash = 0.0;    // the centre core on the cast frame
uniform float held = 0.0;     // 0 to 1: the edge glow and apron
uniform float pulse = 0.0;

void fragment() {
	vec2 p = (UV - 0.5) * 2.0 * extent;
	float d = length(p);
	float e = d - radius_m;
	float edge_glow = exp(-abs(e) / 0.22) * 0.38 + exp(-pow(e / 0.05, 2.0)) * 0.5;
	float apron = smoothstep(radius_m - 1.4, radius_m, d) * step(d, radius_m) * 0.10;
	float soft = (edge_glow + apron) * held * (1.0 + 0.7 * pulse);
	float wr = wave * radius_m;
	float front = exp(-pow((d - wr) / 0.10, 2.0));
	float trail = smoothstep(wr - 1.2, wr, d) * step(d, wr) * 0.25;
	soft += (front * 0.6 + trail) * wave_k;
	float hot = front * wave_k * 0.9 + exp(-pow(d / 0.35, 2.0)) * flash * 1.4;
	vec3 col = mint * soft + mix(mint, vec3(1.0), 0.6) * hot;
	ALBEDO = col;
	ALPHA = clamp(soft + hot, 0.0, 1.0) * step(d, extent);
}
