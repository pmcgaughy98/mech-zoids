shader_type spatial;
// Pangolin salvage: the magnetic field cone (pangolin effects lane, 2026-11-12). A flat quad centred on the pangolin,
// rotated so local +Z is its facing. Inside a short cone in front: a faint copper fill, thin copper edges, and amber
// field bands that run INWARD toward the pangolin (the pull), brightest at the far rim on the first frames. On for
// about 0.25 s, the field window of the Salvage clip (0.15 to about 0.35 s). Additive; only the first-frame rim and
// the band heads pass 1.05.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;

uniform float age = 0.0; // seconds since the field came on
uniform float range_m = 4.0;
uniform float half_ang = 0.6; // radians either side of the facing
uniform float half_m = 4.2; // half the quad's size in metres
uniform vec3 copper = vec3(0.95, 0.48, 0.24);
uniform vec3 amber = vec3(1.0, 0.68, 0.28);
varying vec2 lp;
float sq(float x) { return x * x; } // pow(x, 2.0) is undefined for x < 0 in GLSL

void vertex() {
	lp = VERTEX.xz;
}

void fragment() {
	vec2 p = lp * 2.0 * half_m; // metres, +y is forward
	float r = length(p);
	float a = abs(atan(p.x, p.y));
	float env = smoothstep(0.0, 0.04, age) * (1.0 - smoothstep(0.26, 0.38, age)); // holds until the last plate lands (0.33 s after the field)
	float inside = (1.0 - smoothstep(half_ang - 0.03, half_ang, a)) * (1.0 - smoothstep(range_m - 0.05, range_m, r))
		* smoothstep(0.25, 0.6, r);
	float edge_a = exp(-sq((a - half_ang) * r / 0.05)) * step(r, range_m) * smoothstep(0.25, 0.6, r);
	float rim = exp(-sq((r - range_m) / 0.06)) * (1.0 - smoothstep(half_ang - 0.02, half_ang + 0.02, a));
	// bands move inward: phase grows with r, time pulls them toward r = 0
	float ph = fract(r / 0.7 + age * 6.0);
	float band = smoothstep(0.0, 0.1, ph) * (1.0 - smoothstep(0.18, 0.42, ph)); // thicker after the first take read as nothing
	float taper = smoothstep(0.0, 0.5, 1.0 - a / half_ang); // bands fade before the cone's edges
	float flash = 1.0 - smoothstep(0.0, 0.08, age); // first frames: the far rim snaps on
	vec3 col = copper * (inside * 0.3 + edge_a * 0.8) + amber * band * inside * taper * 1.1
		+ amber * rim * (0.6 + 0.7 * flash);
	col *= env;
	ALBEDO = col;
	ALPHA = clamp(max(max(col.r, col.g), col.b), 0.0, 1.0);
}
