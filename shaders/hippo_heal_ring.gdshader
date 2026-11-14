shader_type spatial;
// Hippo Toxic Flood, the heal read (hippo effects lane, 2026-11-12). The hippo heals while it stands in its own lake.
// Same grammar as the gorilla shell's heal pulse (a pale green band running up the body), so heals read alike across
// the roster; here the lake's violet is drawn in at the feet first, so the heal visibly comes from the lake.
//   mode 0, on an open CylinderMesh round the body: a mint band rising from the feet (rise 0 to 1), streaked
//   mode 1, on a floor quad: a violet ring drawn in toward the feet (rise 0 to 1)
// Additive, writes ALPHA, fog_disabled (look lane rule). Only the band's centre goes above HDR 1.05.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;

uniform int mode = 0;
uniform float rise = 0.0;
uniform float fade = 1.0;
uniform float seed = 0.0;
uniform vec3 mint : source_color = vec3(0.45, 1.0, 0.55);
uniform vec3 hot : source_color = vec3(0.9, 1.0, 0.9);
uniform vec3 shine : source_color = vec3(0.78, 0.36, 1.0);

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7)) + seed) * 43758.5453); }
float noise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

void fragment() {
	vec3 col;
	float a;
	if (mode == 0) {
		float h = 1.0 - UV.y;  // 0 at the feet, 1 at the top ring
		// first take washed the hippo near-white mid-body (Preston cut "shining light"): thinner, about half as strong,
		// almost no white core, fainter wake
		float band = exp(-pow((h - rise) / 0.06, 2.0));
		float trail = smoothstep(rise, 0.0, h) * step(h, rise) * 0.15;  // faint wake under the band
		float streak = 0.5 + 0.5 * smoothstep(0.4, 0.8, noise(vec2(UV.x * 30.0, h * 3.0 - rise * 4.0)));
		float facing = abs(dot(normalize(NORMAL), normalize(VIEW)));
		float k = (band * streak + trail * streak) * (0.3 + 0.7 * (1.0 - facing));  // brightest at the silhouette
		col = mint * (0.75 + 0.3 * streak) + hot * pow(band, 4.0) * 0.12;
		a = k * fade * 0.55 * (1.0 - smoothstep(0.8, 1.0, rise));
	} else {
		vec2 p = UV * 2.0 - 1.0;
		float d = length(p);
		float r = mix(0.95, 0.3, rise);
		float ring = exp(-pow((d - r) / 0.07, 2.0));
		float ang = atan(p.y, p.x);
		float br = 0.6 + 0.4 * noise(vec2(ang * 5.0, rise * 3.0));
		col = mix(shine, mint, smoothstep(0.3, 0.9, rise)) * 0.9;
		a = ring * br * fade * 0.8 * (1.0 - smoothstep(0.75, 1.0, rise));
	}
	ALBEDO = col;
	ALPHA = clamp(a, 0.0, 1.0);
}
