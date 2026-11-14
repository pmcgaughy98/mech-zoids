shader_type spatial;
// Kangaroo title bout, the world outside the ropes (kangaroo effects lane, 2026-11-11). A full-screen pass that dims
// and cools everything further than the ring's radius from its centre, so only the pair inside reads at full colour.
// Our version of the private space Ne Zha's ult cuts to (measured: the world bleeds away in about 0.3 s), in dark teal
// rather than his red, because red marks enemies here. A dark teal veil laid over the scene (blend_mul drew black under gl_compatibility); the HUD is on a CanvasLayer, untouched.
render_mode unshaded, blend_mix, depth_draw_never, depth_test_disabled, cull_disabled, shadows_disabled, fog_disabled;
uniform sampler2D depth_tex : hint_depth_texture, filter_nearest;
uniform vec3 centre = vec3(0.0);
uniform float radius_m = 3.0;
uniform float k = 0.0;          // 0 to 1: how far the world has gone
uniform vec3 tint = vec3(0.01, 0.05, 0.06);
uniform float strength = 0.5; // share of the veil outside the ropes: about half the light

void vertex() {
	POSITION = vec4(VERTEX.xy * 2.0, 0.0, 1.0); // a 1 x 1 QuadMesh stretched over the whole screen
}

void fragment() {
	float d = texture(depth_tex, SCREEN_UV).r;
	vec3 ndc = vec3(SCREEN_UV * 2.0 - 1.0, d * 2.0 - 1.0); // the project runs gl_compatibility: OpenGL depth is -1 to 1
	vec4 view = INV_PROJECTION_MATRIX * vec4(ndc, 1.0);
	view.xyz /= view.w;
	vec3 world = (INV_VIEW_MATRIX * vec4(view.xyz, 1.0)).xyz;
	float dist = length(world.xz - centre.xz);
	float out_k = smoothstep(radius_m + 0.15, radius_m + 1.4, dist);
	ALBEDO = tint;
	ALPHA = out_k * k * strength;
}
