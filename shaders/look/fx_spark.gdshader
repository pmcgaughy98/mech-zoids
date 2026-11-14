shader_type spatial;
// Look lane 2026-11-11: smooth hit / deflect spark (replaces the pixel flipbook; Preston: "we don't want it to look
// like pixel art"). Built like a MOBA impact: an HDR core flash that blooms (above the grade's 1.05 threshold),
// sharp rays that shoot out and thin, and a fast shock ring. age runs 0 to 1 over the effect's life.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;
uniform float age : hint_range(0.0, 1.0) = 0.0;
uniform vec3 core_col : source_color = vec3(1.0, 0.9, 0.6);
uniform vec3 rim_col : source_color = vec3(1.0, 0.6, 0.2);
uniform float seed = 0.0;
uniform float rays = 7.0;
void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0] * length(MODEL_MATRIX[0].xyz),
		INV_VIEW_MATRIX[1] * length(MODEL_MATRIX[1].xyz), INV_VIEW_MATRIX[2] * length(MODEL_MATRIX[2].xyz), MODEL_MATRIX[3]);
}
void fragment() {
	vec2 p = (UV - 0.5) * 2.0;
	float r = length(p);
	float a = atan(p.y, p.x);
	float life = 1.0 - age;
	float reach = 0.25 + 0.75 * sqrt(age);
	float core = life * life * (1.0 - smoothstep(0.0, 0.18 + 0.2 * age, r));
	float ray = pow(0.5 + 0.5 * cos(a * rays + seed * 6.2832), 28.0) * (1.0 - smoothstep(reach - 0.35, reach, r)) * smoothstep(0.05, 0.15, r);
	ray += 0.6 * pow(0.5 + 0.5 * cos(a * rays * 1.7 + seed * 11.0), 40.0) * (1.0 - smoothstep(reach * 0.6 - 0.2, reach * 0.6, r));
	float ring = exp(-pow((r - reach * 0.85) / 0.035, 2.0)) * life * 0.7;
	float fade = 1.0 - smoothstep(0.92, 1.0, r);
	ALBEDO = (core_col * core * 3.2 + rim_col * (ray * life * 1.8 + ring)) * fade;
	ALPHA = 1.0;  // forces the transparent pass, where blend_add applies (without it the quad is drawn opaque)
}
