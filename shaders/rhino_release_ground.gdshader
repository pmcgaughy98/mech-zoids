shader_type spatial;
// Rhino brace release, ground layer (rhino effects lane, 2026-11-11). Smooth, not pixel: the structure measured on
// SMITE 2's Cabrakan Tremors. One flat quad holds four parts, all driven by age (seconds):
//   flash  - a white-hot core and amber bloom on the impact frame
//   streaks - thin rays racing out over the first 0.2 s
//   edge   - a mint rim that reaches full radius in 0.1 s with a soft gradient inward, gone by 0.55 s
//   cracks - a crack web in the floor: white and amber while hot, cooling to dark fissures, gone by about 2 s
// d = 1 at the release radius. Values above 1.05 bloom under the arena grade; the rest stays under it.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;
uniform float age = 0.0;
uniform float radius_m = 3.0;
uniform float extent = 1.25; // quad half-size in units of the radius
uniform float power = 0.0; // 0 at no charge, 1 at full
uniform float seed = 0.0;
uniform vec3 mint = vec3(0.32, 1.0, 0.78);
uniform vec3 amber = vec3(1.0, 0.62, 0.22);
// tremor reuse (2026-11-11): defaults keep the brace release as it was
uniform float flash_mul = 1.0;
uniform float streak_mul = 1.0;
uniform float crack_mul = 1.0;
uniform float hold = 0.0; // seconds the crack web stays before it fades (the tremor's slow lasts 2.4 s)
uniform float reheat = 0.0; // 0..1, a stomp re-lights the same cracks
uniform float zone_life = 0.0; // > 0: a thin mint rim holds at the radius this long (the tremor's slow area)

vec2 hash2(vec2 p) {
	p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
	return fract(sin(p + seed) * 43758.5453);
}
float hash1(float x) { return fract(sin(x * 91.3458 + seed) * 47453.5453); }

// distance to the nearest Voronoi cell border (crack lines)
float voronoi_edge(vec2 x) {
	vec2 n = floor(x), f = fract(x), mg = vec2(0.0), mr = vec2(0.0);
	float md = 8.0;
	for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
		vec2 g = vec2(float(i), float(j));
		vec2 r = g + hash2(n + g) - f;
		float d = dot(r, r);
		if (d < md) { md = d; mr = r; mg = g; }
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
	vec2 p = (UV - 0.5) * 2.0 * extent; // in units of the radius
	float d = length(p);
	float a = atan(p.y, p.x);
	vec2 wm = p * radius_m; // metres
	vec3 col = vec3(0.0);
	float alpha = 0.0;

	// flash
	float f1 = 1.0 - smoothstep(0.0, 0.10, age);
	float f2 = 1.0 - smoothstep(0.03, 0.40, age);
	float core = exp(-d * d / 0.006) * f1 * flash_mul;
	float bloom = exp(-d * d / (0.06 + 0.03 * power)) * f2 * flash_mul;
	col += vec3(1.0) * core * 2.0 + amber * bloom * (0.7 + 0.4 * power);
	alpha = max(alpha, max(core, bloom * 0.6));

	// streaks
	float front = 1.0 - pow(1.0 - clamp(age / 0.10, 0.0, 1.0), 3.0);
	float rays = 28.0;
	float cell = floor((a + 3.14159) / 6.28318 * rays);
	float ca = (cell + 0.5 + (hash1(cell) - 0.5) * 0.6) / rays * 6.28318 - 3.14159;
	float off = abs(sin(a - ca)) * d * radius_m; // metres from the ray's centre line
	float len = mix(0.45, 1.05, hash1(cell + 7.0)) * front;
	float sf = 1.0 - smoothstep(0.08, 0.22, age);
	float streak = (1.0 - smoothstep(0.0, 0.035, off)) * smoothstep(0.08, 0.25, d) * (1.0 - smoothstep(len - 0.25, len, d)) * sf * step(0.35, hash1(cell + 3.0)) * streak_mul;
	col += mix(amber, vec3(1.0), 0.4) * streak * 1.6;
	alpha = max(alpha, streak);

	// edge
	float ef = 1.0 - smoothstep(0.12, 0.55, age);
	float rim = exp(-pow((d - front) / 0.03, 2.0));
	float inner = smoothstep(front - 0.35, front, d) * step(d, front) * 0.22;
	float e = (rim + inner) * ef * step(0.001, age + 0.001);
	col += mint * (rim * (2.2 + power) + inner * 0.6) * ef;
	alpha = max(alpha, clamp(e, 0.0, 1.0));

	// cracks: Voronoi in stretched polar space (radius in metres, angle times a fixed 1.6 m), so cells run long
	// along the radius and the borders read as fissures breaking outward from the impact, not floor tiles.
	// |angle| from a random axis keeps the space seamless. Low-frequency noise breaks the lines into runs.
	float reach = (0.75 + 0.25 * power) * front;
	float wobble = 0.12 * sin(a * 5.0 + seed) + 0.08 * sin(a * 11.0 + seed * 2.0);
	float mask = 1.0 - smoothstep(reach - 0.25 + wobble, reach + wobble, d);
	float ra = abs(mod(a + seed * 0.37 + 3.14159, 6.28318) - 3.14159);
	vec2 q = vec2(d * radius_m * 0.75, ra * 1.6 * (1.1 + 0.3 * power));
	float edge_d = voronoi_edge(q + seed);
	float runs = smoothstep(0.05, 0.35, fract(sin(dot(floor(wm * 1.3), vec2(12.9898, 78.233)) + seed) * 43758.5453) * 0.6 + 0.4 * sin(wm.x * 2.1 + wm.y * 1.7 + seed));
	float near = 1.0 - smoothstep(0.0, 0.35, d);
	mask *= max(runs, near) * crack_mul;
	float w = mix(0.17, 0.045, clamp(d / max(reach, 0.01), 0.0, 1.0));
	float crack = (1.0 - smoothstep(w * 0.5, w, edge_d)) * mask;
	float seam = (1.0 - smoothstep(0.0, w * 0.4, edge_d)) * mask;
	float heat = max(1.0 - smoothstep(0.15, 1.2 + 0.3 * power, age), reheat);
	float gone = 1.0 - smoothstep(1.3 + 0.5 * power + hold, 2.0 + 0.5 * power + hold, age);
	vec3 hot = mix(amber * 1.9, vec3(2.4), seam * (1.0 - smoothstep(0.0, 0.4, d)));
	vec3 crack_col = mix(vec3(0.04, 0.032, 0.028), hot, heat * (0.3 + 0.7 * seam));
	// a pale dust lip along each crack, so cooled fissures still show on the arena's dark floors
	float lip = (1.0 - smoothstep(w, w * 2.2, edge_d)) * (1.0 - crack) * mask * gone * 0.45;
	col = mix(col, vec3(0.62, 0.56, 0.46), lip * (1.0 - clamp(e + core, 0.0, 1.0)));
	alpha = max(alpha, lip);
	float ca2 = crack * gone * 0.92;
	col = mix(col, crack_col, ca2 * (1.0 - clamp(e + core, 0.0, 1.0)));
	alpha = max(alpha, ca2);

	// lit floor under the burst: a faint warm wash that cools with the cracks
	float wash = exp(-d * d / 0.2) * heat * 0.10 * crack_mul;
	col += amber * wash;
	alpha = max(alpha, wash * 0.6);

	// slow zone: a thin held rim at the radius plus a whisper of fill, so the area still reads after the cracks fade
	if (zone_life > 0.0) {
		float zf = smoothstep(0.08, 0.2, age) * (1.0 - smoothstep(zone_life - 0.4, zone_life, age));
		float zr = exp(-pow((d - 1.0) / 0.012, 2.0)) * 0.75 + step(d, 1.0) * smoothstep(0.6, 1.0, d) * 0.06;
		float za = zr * zf;
		float under = za * (1.0 - clamp(alpha, 0.0, 1.0)); // col is premultiplied here: lay the zone under the rest
		col += mint * 0.85 * under;
		alpha += under;
	}

	ALBEDO = col / max(alpha, 0.001);
	ALPHA = clamp(alpha, 0.0, 1.0);
}
