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
	// the seams: the