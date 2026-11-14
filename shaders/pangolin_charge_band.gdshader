shader_type spatial;
// Pangolin bank-shot charge (pangolin effects lane, 2026-11-14, Preston: "A, bank-shot charge"). One thin copper hoop
// around the rolling ball per charge, set around the roll axis so it reads as a band on the shell. Dashes run around the
// hoop with the roll so it never looks like a still ring. A new charge flashes amber for a moment (pulse); the third
// band burns a little hotter (heat) so a full charge reads at a glance. Additive, fog off, below HDR 1.05 at rest.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;

uniform float fade = 1.0;
uniform float pulse = 0.0; // 1 on the bounce that added this band, falling to 0
uniform float heat = 0.0; // 0 to 1: how full the charge is
uniform float spin = 0.0; // turns of the ball, so the dashes travel with the roll
uniform vec3 copper = vec3(0.95, 0.48, 0.24);
uniform vec3 amber = vec3(1.0, 0.68, 0.28);

float sq(float x) { return x * x; }

void fragment() {
	float ph = fract(UV.x * 7.0 - spin);
	float dash = smoothstep(0.0, 0.12, ph) * (1.0 - smoothstep(0.5, 0.75, ph));
	float facing = abs(dot(NORMAL, VIEW));
	float edge = 0.55 + 0.45 * sq(1.0 - facing);
	vec3 col = copper * (0.35 + 0.45 * dash) * (0.8 + 0.4 * heat) * edge;
	col += amber * pulse * 0.9 + vec3(1.0, 0.9, 0.72) * sq(pulse) * 0.5;
	col *= fade;
	ALBEDO = col;
	ALPHA = clamp(max(max(col.r, col.g), col.b), 0.0, 1.0);
}
