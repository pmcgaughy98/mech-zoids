shader_type spatial;
#include "res://shaders/world/fade_cut.gdshaderinc"
uniform sampler2D base_texture : source_color, filter_linear_mipmap;
uniform vec4 base_colour : source_color = vec4(1.0);
uniform sampler2D emission_texture : source_color, filter_linear_mipmap, hint_default_black;
uniform vec4 glow_colour : source_color = vec4(0.0);
uniform float roughness_value = 0.7;
uniform float metallic_value = 0.25;
varying vec3 world_pos;
void vertex() { world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
	if (PROJECTION_MATRIX[3][3] < 0.5 && fade_cut(world_pos, INV_VIEW_MATRIX[3].xyz, FRAGCOORD.xy)) { discard; }
	ALBEDO = texture(base_texture, UV).rgb * base_colour.rgb;
	ROUGHNESS = roughness_value;
	METALLIC = metallic_value;
	EMISSION = texture(emission_texture, UV).rgb * glow_colour.rgb;
}
