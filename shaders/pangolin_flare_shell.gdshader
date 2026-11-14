shader_type spatial;
// Pangolin scale flare: the plates glow (pangolin effects lane, 2026-11-12). Laid on the body as material_overlay
// only while the flare is up. Structure from Kuzenbo's Shell Spikes (SMITE, measured): the shell itself lights up,
// steady, and goes out in one cell; no bubble around it. Copper rim light with amber glints running across the plates.
// Additive; the glints' cores pass 1.05 only on the flare frame and on a blocked hit (pulse).
render_mode unshaded, blend_add, depth_draw_never, cull_back, shadows_disabled, fog_disabled;

uniform float strength = 0.0; // 0 off, 1 full (two blocks left), about 0.55 with one left
uniform float pulse = 0.0; // 1 on the flare frame or a blocked hit, decays fast
uniform float time_s = 0.0;
uniform vec3 copper = vec3(0.95, 0.48, 0.24);
uniform vec3 amber = vec3(1.0, 0.68, 0.28);
varying vec3 wpos;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float fres = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 2.2);
	// glints: thin bands sliding up the body, broken up so they read as light catching plate edges
	float band = sin(wpos.y * 9.0 + wpos.x * 3.0 - time_s * 4.0) * 0.5 + 0.5;
	float glint = pow(band, 8.0) * (0.6 + 0.4 * sin(wpos.x * 17.0 + wpos.z * 13.0));
	vec3 col = copper * (0.28 + 1.0 * fres) + amber * glint * 1.1; // stronger after the first take: copper on a copper body barely showed
	col += vec3(1.0, 0.86, 0.6) * pulse * (0.35 + 0.9 * fres);
	col *= strength;
	ALBEDO = col;
	ALPHA = clamp(max(max(col.r, col.g), col.b), 0.0, 1.0);
}
