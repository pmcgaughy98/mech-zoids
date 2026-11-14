shader_type spatial;
// Soft heat glow for the bison (bison effects lane, 2026-11-13): the stack mouths heating before Eruption fires
// (billboard on), and the floor heating under a falling bomb and cooling after it lands (billboard off, on a flat
// quad; give the material render_priority 3 so it draws over the arena's see-through floor zones).
// Structure from Earthshaker (SMITE 2, measured): the floor reddens one cell before the shell lands.
// `amount` 0..1 from the script. Core above HDR 1.05 only near amount 1. Additive, ALPHA written, fog_disabled.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform bool billboard = false;
uniform float amount = 0.0;
uniform vec3 hot_col : source_color = vec3(1.0, 0.97, 0.92);
uniform vec3 warm_col : source_color = vec3(0.95, 0.88, 0.74);

void vertex() {
	if (billboard) {
		MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
		MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0.0, 0.0, 0.0),
			vec4(0.0, length(MODEL_MATRIX[1].xyz), 0.0, 0.0), vec4(0.0, 0.0, length(MODEL_MATRIX[2].xyz), 0.0),
			vec4(0.0, 0.0, 0.0, 1.0));
	}
}

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float r = length(p);
	float disc = 1.0 - smoothstep(0.0, 1.0, r);
	disc = disc * disc;
	float core = 1.0 - smoothstep(0.0, 0.4, r);
	float m = clamp(amount, 0.0, 1.0);
	ALBEDO = warm_col * 0.8 * disc + hot_col * 1.35 * core * core * m;
	ALPHA = clamp(m * max(disc, core * 0.8), 0.0, 1.0);
}
