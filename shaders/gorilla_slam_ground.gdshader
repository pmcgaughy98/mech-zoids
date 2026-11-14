shader_type spatial;
// Gorilla ult slam, the ground layer (gorilla effects lane, 2026-11-11). Smooth, not pixel. Both fists land, so the
// floor gets two fist dents with a crack web breaking outward from the line between them. Structure from the rhino
// lane's release ground (measured on SMITE 2's Cabrakan): a short hot core on the impact frame, cracks that start
// white-hot and lime, cool to dark fissures with a pale dust lip, and fade. One flat quad, driven by age (seconds).
// d = 1 at the crack reach. The quad's +X is the gorilla's right, so the fists sit at x = -gap and x = +gap.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;
uniform float age = 0.0;
uniform float radius_m = 3.2;
uniform float extent = 1.2; // quad half-size in units of the radius
uniform float fist_gap = 0.5; // metres from the centre to each fist
uniform float fist_r = 0.32; // metres, one fist dent
uniform float seed = 0.0;
uniform float flash_mul = 1.0;
uniform float hold = 0.0; // extra seconds before the cooled cracks fade
uniform float dent_mul = 1.0; // 0 = no dents (a hit on a standing target), 1 = the ult's fist prints
uniform float rim_m = 0.0; // metres; above 0 draws a quiet lime rim at that radius (Fault Line's slow area)
uniform float rim_life = 1.4; // seconds the rim stays
uniform vec3 lime = vec3(0.62, 1.0, 0.16);

vec2 hash2(vec2 p) {
	p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
	return fract(sin(p + seed) * 43758.5453);
}

// distance to the nearest Voronoi cell border (the crack lines)
float voronoi_edge(vec2 x) {
	vec2 n = floor(x), f = fract(x), mg = vec2(0.0), mr = vec2(0.0);
	float md = 8.0;
	for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
		vec2 g = vec2(float(i), float(j));
		vec2 r = g + hash2(n + g) - f;
		float dd = dot(r, r);
		if (dd < md) { md = dd; mr = r; mg = g; }
	}
	md = 8.0;
	for (int j = -2; j <= 2; j++) for (int i = -2; i <= 2; i++) {
		vec2 g = mg + vec2(float(i), float(j));
		vec2 r = g + hash2(n + g) - f;
		if (dot(mr - r, mr - r) > 0.00001) md = min(md, dot(0.5 * (mr + r), normalize(r - mr)));
	}
	return md;
}

void fragment() {
	vec2 wm = (UV - 0.5) * 2.0 * extent * radius_m; // metres from the centre
	// distance to the segment between the fists: the cracks break out from that line, not from one point
	float seg = length(vec2(max(abs(wm.x) - fist_gap, 0.0), wm.y));
	float d = seg / radius_m;
	float a = atan(wm.y, wm.x);
	float fl = length(wm - vec2(-fist_gap, 0.0));
	float fr = length(wm - vec2(fist_gap, 0.0));
	float fd = min(fl, fr); // metres to the nearer fist
	vec3 col = vec3(0.0);
	float alpha = 0.0;

	// impact frame: a small white-hot core under each fist and a short lime bloom. Kept small on purpose.
	float f1 = 1.0 - smoothstep(0.0, 0.09, age);
	float f2 = 1.0 - smoothstep(0.02, 0.30, age);
	float core = exp(-fd * fd / 0.05) * f1 * flash_mul;
	float bloom = exp(-seg * seg / 0.9) * f2 * flash_mul * 0.55;
	col += vec3(1.0) * core * 1.8 + lime * bloom * 0.9;
	alpha = max(alpha, max(core, bloom * 0.6));

	// crack web: Voronoi borders in stretched polar space, so the cells run long along the radius
	float front = 1.0 - pow(1.0 - clamp(age / 0.12, 0.0, 1.0), 3.0);
	float wobble = 0.14 * sin(a * 4.0 + seed) + 0.08 * sin(a * 9.0 + seed * 2.0);
	float reach = front;
	float mask = 1.0 - smoothstep(reach - 0.3 + wobble, reach + wobble, d);
	float ra = abs(mod(a + seed * 0.37 + 3.14159, 6.28318) - 3.14159);
	vec2 q = vec2(seg * 1.15, ra * 2.6);
	float edge_d = voronoi_edge(q + seed);
	// smooth patches where the cracks drop out, so the web has gaps instead of being a full star
	float patchy = sin(wm.x * 1.9 + wm.y * 1.6 + seed) * sin(wm.y * 2.3 - wm.x * 1.3 + seed * 1.7);
	float runs = smoothstep(-0.25, 0.2, patchy);
	float near = 1.0 - smoothstep(0.0, 0.45, d);
	mask *= max(runs, near);
	// thin lines: about 0.1 m at the fists down to hairlines at the edge. Thick lines read as a black scribble.
	float w = mix(0.11, 0.035, clamp(d, 0.0, 1.0));
	float crack = (1.0 - smoothstep(w * 0.45, w, edge_d)) * mask;
	float seam = (1.0 - smoothstep(0.0, w * 0.4, edge_d)) * mask;
	float heat = 1.0 - smoothstep(0.12, 1.0, age);
	float gone = 1.0 - smoothstep(1.5 + hold, 2.4 + hold, age);
	vec3 hot = mix(lime * 1.7, vec3(2.2), seam * (1.0 - smoothstep(0.0, 0.45, d)));
	vec3 crack_col = mix(vec3(0.05, 0.05, 0.055), hot, heat * (0.3 + 0.7 * seam));
	float lip = (1.0 - smoothstep(w, w * 2.4, edge_d)) * (1.0 - crack) * mask * gone * 0.38;
	col = mix(col, vec3(0.62, 0.58, 0.48), lip * (1.0 - core));
	alpha = max(alpha, lip);
	float ca = crack * gone * mix(0.55, 0.95, heat); // cooled cracks are half see-through, never solid black
	col = mix(col, crack_col, ca * (1.0 - core));
	alpha = max(alpha, ca);

	// the two fist dents: a soft darker press in the floor, a thin rim that is lime while hot and dust after
	float dent = 1.0 - smoothstep(fist_r * 0.5, fist_r, fd);
	float dent_rim = exp(-pow((fd - fist_r) / 0.035, 2.0));
	float born = smoothstep(0.0, 0.04, age) * dent_mul;
	col = mix(col, vec3(0.045, 0.045, 0.05), dent * gone * born * 0.6 * (1.0 - core));
	alpha = max(alpha, dent * gone * born * 0.5);
	vec3 rim_col = mix(vec3(0.55, 0.52, 0.45), lime * 1.5, heat);
	float rim_a = mix(0.3, 0.8, heat);
	col = mix(col, rim_col, dent_rim * gone * born * rim_a * (1.0 - core));
	alpha = max(alpha, dent_rim * gone * born * rim_a);

	// the slow area's rim (Fault Line): a thin quiet lime line at rim_m and a barely-there fill inside, for rim_life
	if (rim_m > 0.0) {
		float dc = length(wm);
		float show = smoothstep(0.0, 0.15, age) * (1.0 - smoothstep(rim_life - 0.3, rim_life, age));
		float rim_line = exp(-pow((dc - rim_m) / 0.045, 2.0)) * 0.55 * show;
		float rim_fill = (1.0 - smoothstep(rim_m - 0.1, rim_m, dc)) * 0.05 * show;
		col = mix(col, lime * 0.95, clamp(rim_line + rim_fill, 0.0, 1.0) * (1.0 - alpha * 0.6));
		alpha = max(alpha, rim_line + rim_fill);
	}

	// a faint lime wash on the floor that cools with the cracks
	float wash = exp(-d * d / 0.25) * heat * 0.10;
	col += lime * wash;
	alpha = max(alpha, wash * 0.6);

	ALBEDO = col / max(alpha, 0.001);
	ALPHA = clamp(alpha, 0.0, 1.0);
}
