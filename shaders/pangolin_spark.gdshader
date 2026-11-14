shader_type spatial;
// Pangolin amber spark (pangolin effects lane, 2026-11-12): a camera-facing burst for a hit glancing off the plates.
// A white-amber core for 2 frames and short amber rays thrown out, gone by 0.16 s. No lingering motes.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;

uniform float age = 0.0;
uniform float seed = 0.0;
uniform vec3 amber = vec3(1.0, 0.68, 0.28);
float sq(float x) { return x * x; } // pow(x, 2.0) is undefined for x < 0 in GLSL

float hash(float n) { return fract(sin(n * 91.17 + seed) * 43758.5453); }

void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0.0, 0.0, 0.0),
		vec4(0.0, length(MODEL_MATRIX[1].xyz), 0.0, 0.0), vec4(0.0, 0.0, length(MODEL_MATRIX[2].xyz), 0.0),
		vec4(0.0, 0.0, 0.0, 1.0));
}

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float r = length(p);
	float ang = atan(p.y, p.x);
	float t = clamp(age / 0.16, 0.0, 1.0);
	float core = exp(-sq(r / 0.18)) * (1.0 - smoothstep(0.0, 0.035, age));
	float rays = 0.0;
	for (int i = 0; i < 6; i++) {
		float fi = float(i);
		float a0 = (fi + hash(fi) * 0.6) * 6.2832 / 6.0;
		float head = mix(0.3, 0.95, 1.0 - sq(1.0 - t)) * mix(0.7, 1.0, hash(fi + 4.0));
		float da = abs(mod(ang - a0 + 3.1416, 6.2832) - 3.1416) * r;
		float seg = smoothstep(head - 0.45, head - 0.1, r) * (1.0 - smoothstep(head - 0.05, head, r));
		rays += exp(-sq(da / 0.035)) * seg;
	}
	rays *= 1.0 - smoothstep(0.5, 1.0, t);
	vec3 col = vec3(1.0, 0.9, 0.72) * core * 2.0 + amber * rays * 1.4;
	ALBEDO = col;
	ALPHA = clamp(max(max(col.r, col.g), col.b), 0.0, 1.0);
}
