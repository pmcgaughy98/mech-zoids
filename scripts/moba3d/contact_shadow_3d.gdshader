// The contact shadow under a machine (Claude, 2026-11-04, camera and perspective lane; Preston: "shadow fixes").
// An ellipse on the floor in three flat bands, darkest under the feet, snapped to the floor's own texel grid (50 a
// metre) so its edge steps like the floor art instead of blurring. ContactShadow3D turns it to the machine's drawn
// facing: local +X runs along the body, local +Z across it. It writes no depth, so the sprite standing on it hides the
// part under its body and only the rim round the feet shows.
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix;

uniform vec2 radii = vec2(0.72, 0.70); // metres: along the body, across it
uniform float texel = 0.02; // the floor's texel in metres (50 a metre)
uniform vec4 tint : source_color = vec4(0.06, 0.04, 0.14, 1.0);
uniform vec3 band_alpha = vec3(0.50, 0.32, 0.16); // core, middle, rim
uniform vec2 band_edges = vec2(0.70, 0.88); // where the core and the middle band end, as a share of the radius

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 centre = MODEL_MATRIX[3].xyz;
	vec3 along = normalize(MODEL_MATRIX[0].xyz);
	vec3 across = normalize(MODEL_MATRIX[2].xyz);
	vec3 p = (floor(world_pos / texel) + 0.5) * texel - centre;
	float r = length(vec2(dot(p, along) / radii.x, dot(p, across) / radii.y));
	if (r > 1.0) {
		discard;
	}
	ALBEDO = tint.rgb;
	ALPHA = r < band_edges.x ? band_alpha.x : (r < band_edges.y ? band_alpha.y : band_alpha.z);
}
