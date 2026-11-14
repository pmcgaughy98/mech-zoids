shader_type spatial;
// Gorilla, the ult cage's floor line (gorilla effects lane, 2026-11-14). Smooth, not pixel. At the slam a wide band
// lights the cage's edge and narrows into a thin line in about 0.2 s (Odin's Ring of Spears: one short burst, then a
// thin line joining the wall pieces). The line stays while the cage stands; a broken panel's stretch goes dark, so the
// gap reads on the floor too. Measured in world space round the node, so it matches HexShield.panel_at exactly.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;
uniform float radius_m = 5.5;
uniform float age = 0.0;
uniform float fade = 1.0;
uniform float panel_n = 10.0;
uniform float panel_hp[16];
uniform vec3 edge = vec3(0.62, 1.0, 0.16);
varying vec2 rel;

void vertex() {
	rel = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz - MODEL_MATRIX[3].xz;
}

void fragment() {
	float d = length(rel);
	float a = atan(rel.y, rel.x);
	int i = clamp(int(floor((a + PI) / TAU * panel_n)), 0, 15);
	float hp = panel_hp[i];
	float open = step(0.001, hp);
	float flash = 1.0 - smoothstep(0.0, 0.25, age);
	float w = mix(0.9, 0.08, smoothstep(0.0, 0.22, age)); // the band narrows into the line
	float off = abs(d - radius_m);
	float band = 1.0 - smoothstep(w * 0.5, w * 0.5 + 0.05, off);
	float q = off / 0.4;
	float halo = exp(-q * q) * 0.16;
	float body = (band * (0.55 + 0.45 * flash) + halo) * mix(0.6, 1.0, hp) * open * fade;
	ALBEDO = mix(edge, vec3(1.0), band * flash * 0.3);
	ALPHA = clamp(body, 0.0, 0.9);
}
