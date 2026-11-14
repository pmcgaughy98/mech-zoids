shader_type spatial;
// Pangolin rail dive (pangolin effects lane, 2026-11-12). One camera-facing ribbon between two world points a and b,
// built in the vertex shader so it always faces the camera around its own length. Two looks, by mode:
//   0, lock line: the field line from the spine to a magnetised enemy, on for a blink before the launch. Thin copper
//      with amber pulses running toward the enemy (b). Mid-air at spine height, never on the floor (no ground track).
//   1, streak: the spark streak off the spine while it rides. A hot white-amber head at the pangolin (b), broken amber
//      dashes trailing back to a (the sparks thrown off), thinning and dimming toward the tail.
// Additive; only the streak head and the lock line's first frames pass 1.05.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled, world_vertex_coords;

uniform int mode = 1;
uniform vec3 a = vec3(0.0); // tail (streak) or the pangolin's spine (lock line), world space
uniform vec3 b = vec3(0.0, 0.0, 1.0); // head (streak) or the enemy (lock line), world space
uniform float width = 0.3; // metres, full width at the head
uniform float arc = 0.0; // metres the middle of the ribbon bows upward (the pull line)
uniform float age = 0.0;
uniform float fade = 1.0;
uniform float seed = 0.0;
uniform vec3 copper = vec3(0.95, 0.48, 0.24);
uniform vec3 amber = vec3(1.0, 0.68, 0.28);
varying vec2 uv2;
varying float len_m;
float sq(float x) { return x * x; } // pow(x, 2.0) is undefined for x < 0 in GLSL
float hash(float n) { return fract(sin(n * 91.17 + seed) * 43758.5453); }

void vertex() {
	float u = VERTEX.x + 0.5; // QuadMesh size 1: x and y run -0.5 to 0.5
	vec3 p = mix(a, b, u);
	p.y += sin(u * 3.14159) * arc; // mode 2 bows up into a field arc so it reads from the camera behind the ball
	vec3 axis = b - a;
	axis.y += cos(u * 3.14159) * 3.14159 * arc; // the arc's tangent, so the ribbon keeps facing the camera along the curve
	len_m = max(length(b - a), 0.001);
	vec3 cam = INV_VIEW_MATRIX[3].xyz;
	vec3 side = cross(normalize(axis), cam - p);
	side = length(side) > 0.0001 ? normalize(side) : vec3(1.0, 0.0, 0.0);
	float w = mode == 1 ? width * mix(0.35, 1.0, u) : width;
	VERTEX = p + side * VERTEX.y * w;
	NORMAL = normalize(cam - p);
	uv2 = vec2(u, UV.y * 2.0 - 1.0);
}

void fragment() {
	float u = uv2.x;
	float v = uv2.y;
	vec3 col;
	if (mode == 2) {
		// pull line: held as long as a magnetised enemy bends the roll. Fainter than the lock line, the pulses run
		// from the enemy (a) to the ball (b), and it stays below 1.05 so it never competes with the hits.
		// brightened 2026-11-13 (Preston: "Yes, brighten it"): wider soft core, base about 0.5, pulses to about 1.0
		float core = exp(-sq(v / 0.45));
		float ph = fract(u * len_m / 0.9 - age * 6.0);
		float pulse = smoothstep(0.0, 0.1, ph) * (1.0 - smoothstep(0.18, 0.4, ph));
		float ends = smoothstep(0.0, 0.06, u) * smoothstep(0.0, 0.04, 1.0 - u);
		float shimmer = 0.85 + 0.15 * sin(age * 31.0 + u * 9.0);
		col = (copper * 0.5 * shimmer + amber * pulse * 0.5) * core * ends;
	} else if (mode == 0) {
		float env = smoothstep(0.0, 0.03, age) * (1.0 - smoothstep(0.16, 0.26, age));
		float core = exp(-sq(v / 0.35));
		float ph = fract(u * len_m / 1.1 - age * 7.0); // pulses run toward b
		float pulse = smoothstep(0.0, 0.12, ph) * (1.0 - smoothstep(0.2, 0.45, ph));
		float ends = smoothstep(0.0, 0.06, u) * smoothstep(0.0, 0.03, 1.0 - u);
		float flash = 1.0 - smoothstep(0.0, 0.06, age);
		col = (copper * 0.55 + amber * pulse * 0.9 + vec3(1.0, 0.9, 0.72) * flash * 0.8) * core * ends * env;
	} else {
		float d = (1.0 - u) * len_m; // metres behind the head
		float core = exp(-sq(v / 0.3));
		float cell = floor(d / 0.32 + age * 9.0);
		float ph = fract(d / 0.32 + age * 9.0);
		float dash = step(0.35, hash(cell)) * smoothstep(0.0, 0.15, ph) * (1.0 - smoothstep(0.45, 0.8, ph));
		float tail = exp(-d / 1.4) * smoothstep(0.0, 0.08, u);
		float head = exp(-sq(d / 0.28));
		col = amber * core * (0.25 * tail + dash * tail * 0.85) + vec3(1.0, 0.9, 0.72) * head * exp(-sq(v / 0.5)) * 1.5;
	}
	col *= fade;
	ALBEDO = col;
	ALPHA = clamp(max(max(col.r, col.g), col.b), 0.0, 1.0);
}
