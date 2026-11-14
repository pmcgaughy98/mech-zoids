shader_type spatial;
// Pangolin iron ball crash (pangolin effects lane, 2026-11-12). One ground quad at the point of contact, local +Z the
// way the ball was rolling. Built on the rhino release's measured order (Cabrakan's Tremors), made directional:
//   impact frame: a small white-hot core (2 frames, short on purpose: Preston cut the rhino's big flash)
//   0 to 0.12 s:  an amber shock edge races out, ease-out, wider in front than behind
//   0 to 0.3 s:   speed streaks thrown forward in a cone, the way the ball was going
//   ground:       a pale scuffed burst where the plates struck, gone by about 0.9 s
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;

uniform float age = 0.0;
uniform float radius_m = 2.0; // the shock edge's full radius at the front
uniform float half_m = 2.6; // half the quad's size in metres
uniform float power = 1.0; // 0 slow hit, 1 full-speed hit
uniform float seed = 0.0;
uniform float omni = 0.0; // 1 = a round burst with rays all around (scale flare); 0 = the crash's forward bow
uniform vec3 copper = vec3(0.95, 0.48, 0.24); // Preston 2026-11-12: copper with amber sparks
uniform vec3 amber = vec3(1.0, 0.68, 0.28);
varying vec2 lp;
float sq(float x) { return x * x; } // pow(x, 2.0) is undefined for x < 0 in GLSL

float hash(float n) { return fract(sin(n * 78.233 + seed) * 43758.5453); }

void vertex() {
	lp = VERTEX.xz;
}

void fragment() {
	vec2 p = lp * 2.0 * half_m; // metres, +y forward
	float r = length(p);
	float ang = atan(p.x, p.y); // 0 straight ahead
	float fwd = 0.5 + 0.5 * cos(ang); // 1 ahead, 0 behind
	float reach = radius_m * mix(mix(0.55, 1.0, fwd), 1.0, omni); // the edge is pushed forward like a bow wave
	// core: two frames hot, then gone
	float core_t = 1.0 - smoothstep(0.0, 0.07, age);
	float core = exp(-sq(r / (0.35 + 0.15 * power))) * core_t;
	// shock edge
	float front = 1.0 - pow(1.0 - clamp(age / 0.12, 0.0, 1.0), 3.0);
	float er = reach * front;
	float edge_fade = 1.0 - smoothstep(0.10, 0.42, age);
	float w = 0.08 + 0.14 * front;
	float edge = exp(-sq((r - er) / w)) * edge_fade;
	float inner = (1.0 - smoothstep(0.0, er + 0.001, r)) * smoothstep(0.0, er + 0.001, r) * 1.6 * edge_fade * 0.35;
	// forward streaks: thin rays inside a 70 degree cone ahead
	float rays = 0.0;
	for (int i = 0; i < 12; i++) {
		float fi = float(i);
		float on = mix(step(fi, 6.5), 1.0, omni); // the crash uses 7 rays in its cone, the flare 12 all around
		float a0 = mix((hash(fi) - 0.5) * 1.2, (fi + hash(fi) * 0.5) * 6.2832 / 12.0 - 3.1416, omni);
		float len = radius_m * mix(0.9, 1.5, hash(fi + 9.0)) * front;
		float da = abs(mod(ang - a0 + 3.1416, 6.2832) - 3.1416) * r;
		float along_ray = smoothstep(0.2, 0.6, r) * (1.0 - smoothstep(len * 0.7, len, r));
		rays += exp(-sq(da / 0.05)) * along_ray * on;
	}
	rays *= (1.0 - smoothstep(0.06, 0.3, age)) * mix(0.4, 1.0, power);
	// scuff: a pale dust burst on the floor (stays under 1.0)
	float scuff_t = smoothstep(0.0, 0.05, age) * (1.0 - smoothstep(0.3, 0.9, age));
	float scuff = (1.0 - smoothstep(0.2, 1.1 * radius_m * mix(mix(0.5, 1.0, fwd), 1.0, omni), r)) * scuff_t * 0.16;
	vec3 col = vec3(1.0, 0.92, 0.78) * core * (1.6 + 0.6 * power);
	col += mix(amber, vec3(1.0, 0.9, 0.7), 0.3) * edge * (0.9 + 0.7 * power);
	col += copper * inner;
	col += vec3(1.0, 0.78, 0.42) * rays * 1.3; // amber sparks thrown forward
	col += vec3(0.62, 0.55, 0.47) * scuff;
	ALBEDO = col;
	ALPHA = clamp(max(max(col.r, col.g), col.b), 0.0, 1.0);
}
