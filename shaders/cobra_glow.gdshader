shader_type spatial;
// Soft glow for the cobra (cobra effects lane, 2026-11-13): the hood projector strips charging and flaring for Hood
// Gaze (billboard_mode 2, a tall quad that turns round the vertical so the strip stays upright), the neck core, the
// gaze glint at the hood (billboard_mode 1 with `streak`, a thin sideways glint like an eye catching light), and the
// small burst on a stunned enemy. Structure from Medusa's Petrify (SMITE 2, measured at 15 fps): the caster lights up
// for the whole charge, then one short bright cell at the head when it fires. Ours stays small and short.
// `amount` 0..1 from the script (up to 1.6 for the flare). Core above HDR 1.05 only near amount 1. Additive, ALPHA
// written, fog_disabled. No point light anywhere.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform int billboard_mode = 1; // 0 none, 1 faces the camera, 2 upright (turns round Y only)
uniform float amount = 0.0;
uniform float core_size = 0.4;
uniform float streak = 0.0;
uniform float ring_r = 0.0; // above 0: a soft ring at this radius (0..1 of the quad) in place of the filled disc
uniform vec3 hot_col : source_color = vec3(0.86, 1.0, 0.97);
uniform vec3 warm_col : source_color = vec3(0.10, 0.82, 0.74);

void vertex() {
	if (billboard_mode == 1) {
		MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
		MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0.0, 0.0, 0.0),
			vec4(0.0, length(MODEL_MATRIX[1].xyz), 0.0, 0.0), vec4(0.0, 0.0, length(MODEL_MATRIX[2].xyz), 0.0),
			vec4(0.0, 0.0, 0.0, 1.0));
	} else if (billboard_mode == 2) {
		vec3 up = vec3(0.0, 1.0, 0.0);
		vec3 to_cam = INV_VIEW_MATRIX[3].xyz - MODEL_MATRIX[3].xyz;
		to_cam.y = 0.0;
		vec3 fwd = length(to_cam) > 0.0001 ? normalize(to_cam) : vec3(0.0, 0.0, 1.0);
		vec3 side = cross(up, fwd);
		mat4 m = mat4(vec4(side * length(MODEL_MATRIX[0].xyz), 0.0), vec4(up * length(MODEL_MATRIX[1].xyz), 0.0),
			vec4(fwd * length(MODEL_MATRIX[2].xyz), 0.0), MODEL_MATRIX[3]);
		MODELVIEW_MATRIX = VIEW_MATRIX * m;
	}
}

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float r = length(p);
	float disc = 1.0 - smoothstep(0.0, 1.0, r);
	disc = disc * disc;
	if (ring_r > 0.0) {
		float d = (r - ring_r) / 0.28;
		disc = exp(-d * d) * (1.0 - smoothstep(0.85, 1.0, r));
	}
	float core = 1.0 - smoothstep(0.0, core_size, r);
	float m = clamp(amount, 0.0, 1.6);
	float mc = clamp(m, 0.0, 1.0);
	// the glint: a thin sideways line through the core, fading toward the quad's ends
	float line = (1.0 - smoothstep(0.0, 0.07, abs(p.y))) * (1.0 - smoothstep(0.1, 1.0, abs(p.x)));
	float g = line * streak;
	ALBEDO = warm_col * 0.85 * disc * min(m, 1.25) + hot_col * (1.25 * core * core * mc + 1.1 * g);
	ALPHA = clamp(mc * max(disc, max(core * 0.85, g)), 0.0, 1.0);
}
