shader_type spatial;
// Thin glowing floor ring for the bison (bison effects lane, 2026-11-17): Whistle Stop's ground ripple at the inhale,
// its scald ring and the faint ally-call ring. On a flat PlaneMesh of side 2; the script scales the node to the radius
// and sets `amount` (0..1) and `width` (the band, as a fraction of the radius). Give the material render_priority 3 so
// it draws over the arena's see-through floor zones. Additive, ALPHA written, fog_disabled. The core goes above
// HDR 1.05 only near amount 1. The band is broken up a little around the circle so it reads as heat, not a UI circle.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform float amount = 0.0;
uniform float width = 0.08;
uniform float seed = 0.0;
uniform float wash = 0.12; // a faint fill inside the band
uniform vec3 hot_col : source_color = vec3(1.0, 0.97, 0.92);
uniform vec3 warm_col : source_color = vec3(0.95, 0.88, 0.74);

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float r = length(p);
	if (r > 1.0) {
		discard;
	}
	float w = max(width, 0.005);
	float d = (r - (1.0 - w)) / w;
	float band = exp(-d * d * 3.0);
	float a = atan(p.y, p.x);
	float n = 0.78 + 0.22 * sin(a * 9.0 + seed) * sin(a * 4.0 - seed * 1.7);
	float fill = smoothstep(0.25, 1.0 - w, r) * (1.0 - smoothstep(1.0 - w, 1.0, r)) * wash;
	float m = clamp(amount, 0.0, 1.0);
	ALBEDO = warm_col * 0.9 * (band * n + fill) + hot_col * 1.3 * band * band * m;
	ALPHA = clamp(m * (band * n + fill), 0.0, 1.0);
}
