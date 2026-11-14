shader_type spatial;
// Breach, the soft wall section (cobra effects lane, 2026-11-14, take 2). The kit's power is making solid matter go
// soft, so the section does not break: its faces (near, far, and the top) go soft. The scene under each panel is
// sampled shifted, so the wall's own surface wavers like liquid; it is drained a little toward gold (the same read as
// an enemy held out of phase); only the crests of the slow sag waves catch a pale highlight. Rings spread from the
// hole where the snout goes in (contact) and comes out (burst): one fast thin ring as it does, and a churn of rings
// while the body passes. The section has no outline: its edge is feathered and irregular, and only its two sides,
// where it meets wall that is still hard, carry a thin wavering seam while allies can pass (frame_amt).
// Take 1 read as a flat yellow glass pane in a hard rectangle; this replaces it. Quad sized `size` metres; UV (0,0)
// is the top left; `hole` is in UV. blend_mix; nothing above HDR 1.05 but the seams and the burst ring.
render_mode unshaded, blend_mix, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

#include "res://shaders/cobra_noise.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform vec2 size = vec2(2.2, 2.6);
uniform vec2 hole = vec2(0.5, 0.42);
uniform float amount = 0.0;
uniform float frame_amt = 0.0;
uniform float churn = 0.0;
uniform float ring_age = 9.0;
uniform float age = 0.0;
uniform float seed = 0.0;
uniform vec3 hot_col : source_color = vec3(1.0, 0.98, 0.80);
uniform vec3 warm_col : source_color = vec3(0.92, 0.84, 0.18);

void fragment() {
	vec2 pm = UV * size; // metres from the top left
	vec2 m = (UV - hole) * size;
	float r = length(m);
	vec2 dir = m / max(r, 0.001);
	// distance to the sides (where the section meets hard wall) and to the top and bottom, in metres
	float ex = min(pm.x, size.x - pm.x);
	float ey = min(pm.y, size.y - pm.y);
	// an irregular, slowly moving edge: the soft part does not stop on a straight line
	float n1 = c_vnoise(vec2(pm.y * 1.7 + seed, age * 0.6 + pm.x * 0.3));
	float n2 = c_vnoise(vec2(pm.x * 1.9 - seed, age * 0.5 + 11.0));
	float inner = smoothstep(0.02, 0.38, ex - 0.14 * n1) * smoothstep(0.0, 0.22, ey - 0.08 * n2);
	// the seams: the two sides only, thin, wavering sideways
	float wx = sin(pm.y * 5.0 - age * 4.0 + seed) * 0.025 + (n1 - 0.5) * 0.04;
	float seam = exp(-pow((ex - 0.05 - wx) / 0.028, 2.0)) * smoothstep(0.0, 0.25, ey);
	// slow sag waves running down the face, bent sideways
	float sag = sin(pm.y * 4.0 - age * 3.0 + sin(pm.x * 2.5 + age * 1.7 + seed) * 1.2);
	float crest = smoothstep(0.6, 1.0, sag);
	// rings: a churn round the hole while the body passes, and one fast thin ring as the snout meets the face
	float rings = churn * smoothstep(0.75, 1.0, sin(r * 10.0 - age * 15.0)) * exp(-r * 0.9);
	float burst = exp(-pow((r - ring_age * 6.0) / 0.07, 2.0)) * (1.0 - smoothstep(0.0, 0.35, ring_age));
	float k = inner * amount;
	vec2 off = (vec2(sag, cos(pm.x * 3.0 + age * 2.3)) * 0.008 + dir * (rings * 0.9 + burst) * 0.016) * k;
	vec3 bg = texture(screen_tex, SCREEN_UV + off).rgb;
	vec3 g = mix(warm_col, hot_col, 0.55);
	float lum = dot(bg, vec3(0.3, 0.59, 0.11));
	vec3 col = mix(bg, warm_col * (0.25 + lum * 1.1), 0.22 * k);
	col += g * k * (0.10 * crest + 0.30 * rings + 0.55 * burst);
	col = mix(col, mix(warm_col, hot_col, 0.5) * 1.3, clamp(seam * frame_amt, 0.0, 1.0));
	ALBEDO = col;
	ALPHA = clamp(max(k, seam * frame_amt), 0.0, 1.0);
}
