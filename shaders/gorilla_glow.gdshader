shader_type spatial;
// Gorilla, a soft round glow that faces the camera (gorilla effects lane, 2026-11-13). Smooth, not pixel. Used for the
// back reactor charging and for the arc it throws on Reactor Fault Line. grow = 1: swells and holds, then drops at
// the very end (the charge). grow = 0: appears full and fades (one bead of the arc). Small on purpose: no big flash.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;
uniform float age = 0.0;
uniform float life = 0.3;
uniform float strength = 1.0;
uniform float grow = 0.0;
uniform vec3 lime = vec3(0.62, 1.0, 0.16);

void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	MODELVIEW_NORMAL_MATRIX = mat3(MODELVIEW_MATRIX);
}

void fragment() {
	vec2 p = (UV - 0.5) * 2.0;
	float d = length(p);
	float t = clamp(age / life, 0.0, 1.0);
	float core = exp(-(d * d) / 0.03);
	float halo = exp(-(d * d) / 0.22) * 0.5;
	float swell = smoothstep(0.0, 0.6, t) * (1.0 - smoothstep(0.85, 1.0, t));
	float drop = (1.0 - t) * (1.0 - t);
	float fade = mix(drop, swell, step(0.5, grow)) * step(0.0, age);
	float body = (core + halo) * fade * strength * (1.0 - smoothstep(0.8, 1.0, d));
	ALBEDO = mix(lime, vec3(1.0), core * 0.5);
	ALPHA = clamp(body, 0.0, 1.0);
}
