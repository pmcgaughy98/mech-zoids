shader_type spatial;
// Rhino brace release, the shell wall (rhino effects lane, 2026-11-11): an open cylinder at the edge's radius, bright
// at the ground and fading upward, so the edge reads as the front of a dome rather than a line on the floor.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;
uniform float fade = 1.0;
uniform vec3 mint = vec3(0.32, 1.0, 0.78);
void fragment() {
	float up = 1.0 - UV.y; // the CylinderMesh's UV.y runs top 0 to bottom 1
	float g = pow(1.0 - up, 2.2);
	ALBEDO = mint * (0.4 + 1.4 * g) * fade;
	ALPHA = g * fade;
}
