// Painted and worn marks on the floor: lane arrows, hazard bands, oil, drains, patches, scorch, bay numbers, vents.
// Map design lane, 2026-11-04 (quality pass). One MultiMesh of flat quads built by arena_blockout.gd (_decals); each
// instance's custom data is its rect in the theme's decals.png. The atlas is read at texel centres of the shared 50
// per metre grid, so a mark laid at an angle still draws in whole floor pixels. Alpha under 0.3 is cut; alpha under
// 0.95 glows (the vents). Lit like the floor, and dims under the fog of war like it.
shader_type spatial;
render_mode cull_back;

#include "res://shaders/world/fog.gdshaderinc"

uniform sampler2D atlas : source_color, filter_nearest, repeat_disable;
uniform float texels_per_metre = 50.0;
uniform float glow_energy = 0.0;

varying vec3 world_pos;
varying flat vec4 rect;
varying flat vec4 inv;
varying flat vec2 origin;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	rect = INSTANCE_CUSTOM;
	mat2 im = inverse(mat2(MODEL_MATRIX[0].xz, MODEL_MATRIX[2].xz));
	inv = vec4(im[0], im[1]);
	origin = MODEL_MATRIX[3].xz;
}

void fragment() {
	vec2 q = (floor(world_pos.xz * texels_per_metre) + 0.5) / texels_per_metre;
	vec2 l = mat2(inv.xy, inv.zw) * (q - origin) + 0.5;
	if (l.x < 0.0 || l.y < 0.0 || l.x > 1.0 || l.y > 1.0) {
		discard;
	}
	vec4 t = texture(atlas, rect.xy + l * rect.zw);
	if (t.a < 0.3) {
		discard;
	}
	float s = fog_seen(world_pos);
	ALBEDO = fog_tint(t.rgb, s);
	EMISSION = t.rgb * (t.a < 0.95 ? 1.0 : 0.0) * glow_energy * mix(fog_dim, 1.0, s);
	ROUGHNESS = 1.0;
	SPECULAR = 0.0;
}
