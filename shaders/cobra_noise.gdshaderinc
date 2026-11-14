// Shared noise for the cobra petrify effects (cobra effects lane, 2026-11-13): value noise for grain and a Voronoi
// edge distance for cracks. c_crack returns F2 - F1: near 0 on a crack, so 1 - smoothstep(0, w, c_crack(p)) draws
// cracks w wide (in cells). c_cracks warps p first so the lines wander like split stone.
float c_hash2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

vec2 c_hash22(vec2 p) {
	return fract(sin(vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)))) * 43758.5453);
}

float c_vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(c_hash2(i), c_hash2(i + vec2(1.0, 0.0)), u.x),
		mix(c_hash2(i + vec2(0.0, 1.0)), c_hash2(i + vec2(1.0, 1.0)), u.x), u.y);
}

float c_crack(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	float d1 = 8.0;
	float d2 = 8.0;
	for (int y = -1; y <= 1; y++) {
		for (int x = -1; x <= 1; x++) {
			vec2 g = vec2(float(x), float(y));
			float d = length(g + c_hash22(i + g) - f);
			if (d < d1) {
				d2 = d1;
				d1 = d;
			} else if (d < d2) {
				d2 = d;
			}
		}
	}
	return d2 - d1;
}

float c_cracks(vec2 p, float w) {
	vec2 q = p + (vec2(c_vnoise(p * 1.3), c_vnoise(p * 1.3 + 5.2)) - 0.5) * 0.8;
	return 1.0 - smoothstep(0.0, w, c_crack(q));
}
