shader_type spatial;
// Molten rock surface for the bison's bombs, thrown chunks and slag lumps (bison effects lane, 2026-11-13).
// A dark cooling crust broken by glowing seams (cellular noise in object space, so the plates ride the rock as it
// spins). heat 1 = fresh out of the stack, 0 = cold basalt. Seam cores go above HDR 1.05 while hot, the seam edges and
// the crust stay under, and the crust is lit, so it reads as rock with light inside, never as a ball of light.
// Structure from Vulcan's Magma Bomb and Earthshaker shell (SMITE 2, measured): a dark body with hot seams.
// Meshes are made at radius 1 and scaled by the node; the vertex jitter makes them lumpy.
render_mode cull_back, diffuse_burley, specular_schlick_ggx;

uniform vec3 hot_col : source_color = vec3(1.0, 0.97, 0.92);
uniform vec3 warm_col : source_color = vec3(0.95, 0.88, 0.74);
uniform vec3 crust_col : source_color = vec3(0.075, 0.068, 0.062);
uniform float seam_scale = 2.6;
instance uniform float heat = 1.0;
instance uniform float seed = 0.0;
varying vec3 opos;

vec3 hash3(vec3 p) {
	p = vec3(dot(p, vec3(127.1, 311.7, 74.7)), dot(p, vec3(269.5, 183.3, 246.1)), dot(p, vec3(113.5, 271.9, 124.6)));
	return fract(sin(p) * 43758.5453);
}

// Distance to the nearest cell wall (F2 - F1): 0 on a seam, larger inside a plate.
float cell_edge(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	float d1 = 8.0;
	float d2 = 8.0;
	for (int x = -1; x <= 1; x++) {
		for (int y = -1; y <= 1; y++) {
			for (int z = -1; z <= 1; z++) {
				vec3 g = vec3(float(x), float(y), float(z));
				vec3 r = g + hash3(i + g) - f;
				float d = dot(r, r);
				if (d < d1) {
					d2 = d1;
					d1 = d;
				} else if (d < d2) {
					d2 = d;
				}
			}
		}
	}
	return sqrt(d2) - sqrt(d1);
}

void vertex() {
	opos = VERTEX;
	VERTEX *= 1.0 + (hash3(floor(VERTEX * 23.0 + 0.5)).x - 0.5) * 0.18;
}

void fragment() {
	vec3 p = opos * seam_scale + vec3(seed);
	float e = cell_edge(p);
	float e2 = cell_edge(p * 2.3 + 7.0);
	float h = clamp(heat, 0.0, 1.0);
	float w = mix(0.012, 0.075, h);
	float seam = 1.0 - smoothstep(0.0, w, e);
	float fine = (1.0 - smoothstep(0.0, w * 0.4, e2)) * 0.3 * h;
	float core = 1.0 - smoothstep(0.0, w * 0.4, e);
	ALBEDO = crust_col * (0.75 + 0.5 * smoothstep(0.0, 0.4, e2));
	ROUGHNESS = 0.9;
	METALLIC = 0.0;
	vec3 edge_glow = warm_col * 0.8 * clamp(seam + fine, 0.0, 1.0) * h;
	vec3 core_glow = hot_col * 1.6 * core * h * h;
	EMISSION = edge_glow + core_glow + warm_col * 0.04 * h;
}
