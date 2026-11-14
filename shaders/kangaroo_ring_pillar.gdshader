shader_type spatial;
// Kangaroo boxing ring, the cast beam (kangaroo effects lane, 2026-11-11). A short column of light on the kangaroo
// on the cast frame, after the beam Odin raises when he casts Ring of Spears. Kept thin and short (Preston cut the big
// white flash on the rhino): a narrow hot core, a soft mint sheath, fading toward the top. Faces the camera (the
// script turns it about the vertical).
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;
uniform vec3 mint = vec3(0.32, 1.0, 0.78);
uniform float k = 1.0; // 1 at the cast, falls to 0

void fragment() {
	float x = (UV.x - 0.5) * 2.0;
	float up = 1.0 - UV.y;
	float width = mix(0.35, 1.0, k);
	float core = exp(-pow(x / (0.10 * width), 2.0));
	float sheath = exp(-abs(x) / (0.38 * width)) * 0.45;
	float along = (1.0 - smoothstep(0.35, 1.0, up)) * smoothstep(0.0, 0.06, up);
	float m = along * k;
	vec3 col = mint * sheath + mix(mint, vec3(1.0), 0.6) * core * 1.5;
	ALBEDO = col * m;
	ALPHA = clamp(core + sheath, 0.0, 1.0) * m;
}
