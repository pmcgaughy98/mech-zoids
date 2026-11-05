// A side pit's capture ring (map design lane, 2026-11-05; Preston picked pit capture). A flat quad over the pit
// floor, centred on the pit, drawn by scenes/moba3d/arena_pit.gd. It shows `segments` blocks of a ring between
// `radius - width` and `radius`, read at texel centres of the shared 50-per-metre grid so it draws in whole floor
// pixels. The first `fill` share of the blocks, clockwise from the far side as the camera sees it, shows
// `fill_color`; the rest show `base_color`. `pulse` whitens the lit blocks (a contested pit blinks), `flash` whitens
// everything (the moment a team takes it). Dims under the fog of war like the floor.
shader_type spatial;
render_mode unshaded, cull_back, depth_draw_never, shadows_disabled;

#include "res://shaders/world/fog.gdshaderinc"

uniform float radius = 4.9;
uniform float width = 0.7;
uniform float segments = 24.0;
uniform float gap = 0.2; ///< share of each block left empty
uniform float fill = 0.0;
uniform vec4 fill_color : source_color = vec4(1.0);
uniform vec4 base_color : source_color = vec4(1.0, 0.6, 0.22, 0.5);
uniform float pulse = 0.0;
uniform float flash = 0.0;
uniform float texels_per_metre = 50.0;

varying vec3 world_pos;
varying flat vec2 centre;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	centre = MODEL_MATRIX[3].xz;
}

void fragment() {
	vec2 q = (floor(world_pos.xz * texels_per_metre) + 0.5) / texels_per_metre;
	vec2 d = q - centre;
	float r = length(d);
	if (r > radius || r < radius - width) {
		discard;
	}
	// 0 at -z (up the screen for blue's camera), growing clockwise seen from above
	float a = fract(atan(d.x, -d.y) / TAU);
	float block = floor(a * segments);
	if (fract(a * segments) < gap) {
		discard;
	}
	bool lit = block < floor(fill * segments + 0.001);
	vec4 c = lit ? fill_color : base_color;
	if (lit) {
		c.rgb = mix(c.rgb, vec3(1.0), pulse * 0.65);
	}
	c.rgb = mix(c.rgb, vec3(1.0), flash);
	c.a = mix(c.a, 1.0, flash);
	float s = fog_seen(world_pos);
	ALBEDO = fog_tint(c.rgb, s);
	ALPHA = c.a;
}
