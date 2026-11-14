// Pixel billboards for world dressing: trees past the cliffs, bushes on rock and cliff tops. Map design lane,
// 2026-11-04. Upright like the machines (turns about y only), unshaded so the pixel art keeps its own light, and cut
// by the same wall fade as the walls (fade_cut.gdshaderinc). Meant for MultiMeshInstance3D with a QuadMesh whose
// size is the texture's pixels times 0.02 m and whose centre_offset lifts its bottom edge to the instance origin.
shader_type spatial;
render_mode unshaded, cull_disabled;

#include "res://shaders/world/fade_cut.gdshaderinc"
#include "res://shaders/world/fog.gdshaderinc"

uniform sampler2D sprite : source_color, filter_nearest, repeat_disable;
uniform vec4 tint : source_color = vec4(1.0);
uniform float alpha_cut = 0.5;
uniform bool billboard = true; // false: a flat sprite that keeps its own facing (banners on walls)

varying vec3 world_pos;

void vertex() {
	if (billboard) {
		// fixed-y billboard, as StandardMaterial3D builds it for BILLBOARD_FIXED_Y
		MODELVIEW_MATRIX = VIEW_MATRIX * mat4(
			vec4(normalize(cross(vec3(0.0, 1.0, 0.0), INV_VIEW_MATRIX[2].xyz)), 0.0),
			vec4(0.0, 1.0, 0.0, 0.0),
			vec4(normalize(cross(INV_VIEW_MATRIX[0].xyz, vec3(0.0, 1.0, 0.0))), 0.0),
			MODEL_MATRIX[3]);
		MODELVIEW_NORMAL_MATRIX = mat3(MODELVIEW_MATRIX);
	}
	world_pos = (INV_VIEW_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	if (PROJECTION_MATRIX[3][3] < 0.5 && fade_cut(world_pos, INV_VIEW_MATRIX[3].xyz, FRAGCOORD.xy)) {
		discard;
	}
	vec4 t = texture(sprite, UV);
	if (t.a < alpha_cut) {
		discard;
	}
	ALBEDO = fog_tint(t.rgb * tint.rgb, fog_seen(world_pos));
}
