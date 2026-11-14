shader_type spatial;
// Gorilla Fault Line, the crack that runs along the floor (gorilla effects lane, 2026-11-12). Smooth, not pixel.
// One flat strip from the fists to the end point. UV.y runs along the line (0 at the fists), UV.x across it.
// The kit's wave head reveals it: everything behind `head` is cracked, hot lime right behind the head and cooling
// to dark fissures with a pale dust lip the further back it is. A jagged main fissure with short side branches.
// Structure from the ult's ground (Cabrakan's cracks: hot, cooled, gone); the timing is the kit's own wave speed.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;
uniform float length_m = 5.0;
uniform float width_m = 2.4;
uniform float head = 0.0; // metres from the strip's start to the wave head
uniform float speed = 9.0; // the wave's metres per second, so "how long ago did the head pass here" is known
uniform float done_age = -1.0; // seconds since the wave stopped; below 0 while it is still running
uniform float seed = 0.0;
uniform vec3 lime = vec3(0.62, 1.0, 0.16);

vec2 hash2(vec2 p) {
	p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
	return fract(sin(p + seed) * 43758.5453);
}

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

// where the main fissure sits across the strip at y metres along it
// (triangle waves, not sines: a crack has kinks; a smooth wave reads as a beam of light)
float tri(float t) { return abs(fract(t) - 0.5) * 4.0 - 1.0; }
float centre(float y) {
	return 0.22 * tri(y * 0.55 + seed) + 0.11 * tri(y * 1.7 + seed * 2.0) + 0.04 * tri(y * 4.3 + seed * 0.7);
}

void fragment() {
	float x = (UV.x - 0.5) * width_m;
	float y = UV.y * length_m;
	float behind = head - y; // metres the head is past this point
	float reveal = smoothstep(-0.05, 0.12, behind) * smoothstep(0.0, 0.25, y) * (1.0 - smoothstep(length_m - 0.1, length_m, y));
	float since = max(behind, 0.0) / speed + max(done_age, 0.0); // seconds since the head passed here
	float dm = abs(x - centre(y)); // metres from the main fissure
	vec3 col = vec3(0.0);
	float alpha = 0.0;

	// main fissure: about 0.17 m at the fists, thinning toward the end (a first take at 0.1 m read as a laser line)
	float w = mix(0.17, 0.08, clamp(y / length_m, 0.0, 1.0));
	float main_line = 1.0 - smoothstep(w * 0.45, w, dm);
	float seam = 1.0 - smoothstep(0.0, w * 0.3, dm);
	// side cracks: Voronoi borders out to about 0.9 m either side, with gaps, so the floor reads as a broken strip
	float edge_d = voronoi_edge(vec2(x * 1.5, y * 1.1) + seed);
	float near = 1.0 - smoothstep(0.25, 0.95, dm);
	float patchy = smoothstep(-0.45, 0.1, sin(y * 1.7 + seed * 1.3) * sin(y * 0.6 + x * 2.1 + seed));
	float branch = (1.0 - smoothstep(0.045, 0.09, edge_d)) * near * patchy;
	float crack = max(main_line, branch * 0.9) * reveal;

	float heat = 1.0 - smoothstep(0.05, 0.75, since);
	float gone = 1.0 - smoothstep(1.4, 2.1, since);
	vec3 hot = mix(lime * 1.7, vec3(2.2), seam);
	vec3 crack_col = mix(vec3(0.05, 0.05, 0.055), hot, heat * (0.35 + 0.65 * max(seam, main_line * 0.6)));
	float lip = (1.0 - smoothstep(w, w * 2.6, dm)) * (1.0 - main_line) * reveal * gone * 0.34;
	col = mix(col, vec3(0.62, 0.58, 0.48), lip);
	alpha = max(alpha, lip);
	float ca = crack * gone * mix(0.55, 0.95, heat);
	col = mix(col, crack_col, ca);
	alpha = max(alpha, ca);

	// a faint lime wash right behind the head, and the head itself: a small hot point while the wave runs
	float wash = exp(-dm * dm / 0.12) * heat * reveal * 0.12;
	col += lime * wash;
	alpha = max(alpha, wash * 0.6);
	float running = step(done_age, -0.5);
	float hx = x - centre(head);
	float hy = y - head;
	float head_glow = exp(-(hx * hx + hy * hy) / 0.035) * running * smoothstep(0.0, 0.25, head);
	col += (lime * 1.1 + vec3(0.4)) * head_glow;
	alpha = max(alpha, head_glow);

	ALBEDO = col / max(alpha, 0.001);
	ALPHA = clamp(alpha, 0.0, 1.0);
}
