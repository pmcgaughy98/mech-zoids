shader_type spatial;
// Plow scorch (bison effects lane, 2026-11-13). The band of ground the plow churned: dark char with furrows running
// along the arc and embers in it that cool in about a second, gone by 2.4 s. Short on purpose: slag (the stacks' fire,
// 4.5 s, crusted lumps) stays the only lasting floor mark, and nothing here looks like the hippo's liquid.
// An ImmediateMesh band rebuilt each frame. Per vertex: COLOR.r = ember heat, COLOR.a = fade. UV.x = metres along the
// arc, UV.y = 0 at the inner edge, 1 at the outer. Floor effect: the material sets render_priority 3.
// Structure from Vulcan's Magma Bomb (SMITE 2, measured at 15 fps): a dark scorch with a few small hot spots.
render_mode blend_mix, depth_draw_never, cull_disabled, diffuse_burley, specular_disabled;

uniform vec3 hot_col : source_color = vec3(1.0, 0.93, 0.70);
uniform vec3 warm_col : source_color = vec3(1.0, 0.36, 0.06);
uniform vec3 char_col : source_color = vec3(0.05, 0.045, 0.04);

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void fragment() {
	vec2 p = vec2(UV.x, UV.y * 1.6);
	float n = vnoise(p * 2.2) * 0.6 + vnoise(p * 5.0) * 0.4;
	float across = 1.0 - abs(UV.y * 2.0 - 1.0);
	float mask = smoothstep(0.0, 0.45, across + (n - 0.5) * 0.6);
	float furrow = vnoise(vec2(UV.x * 1.2, UV.y * 9.0)); // lines along the arc, where the plow dragged
	float h = clamp(COLOR.r, 0.0, 1.0);
	ALBEDO = char_col * (0.7 + 0.6 * furrow);
	ROUGHNESS = 0.95;
	float ember = smoothstep(0.6, 0.9, vnoise(p * 4.0 + 7.3) * (0.65 + 0.35 * furrow) + 0.1 * across);
	EMISSION = warm_col * 1.1 * ember * h + hot_col * 1.3 * ember * h * h * h;
	ALPHA = clamp(mask * COLOR.a * 0.88, 0.0, 1.0);
}
