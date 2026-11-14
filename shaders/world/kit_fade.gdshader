// The Meshy-made foundry kit (walls, rocks, towers, cores, the refinery backdrop). Map design lane, 2026-11-14.
// The model's own PBR textures (glTF base colour, metallic-roughness, normal), with the same dither fade
// (fade_cut.gdshaderinc) and fog of war (fog.gdshaderinc) as wall_fade.gdshader, so a kit wall between the chase
// camera and the player's machine still never hides the machine.
// The kit's amber light strips are found in the base colour (warm, saturated, bright) and lit; team_mix paints them
// in team_color, so one tower model reads blue on one side and red on the other.
shader_type spatial;

#include "res://shaders/world/fade_cut.gdshaderinc"
#include "res://shaders/world/fog.gdshaderinc"

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap_anisotropic, hint_default_white;
uniform vec4 albedo : source_color = vec4(1.0);
uniform sampler2D orm_texture : filter_linear_mipmap, hint_default_white; // glTF: roughness in g, metallic in b
uniform bool use_orm = false;
uniform float roughness = 0.8;
uniform float metallic = 0.0;
uniform sampler2D normal_texture : hint_normal, filter_linear_mipmap;
uniform bool use_normal = false;
uniform sampler2D emission_texture : source_color, filter_linear_mipmap, hint_default_black;
uniform bool use_emission = false;

uniform vec4 team_color : source_color = vec4(1.0, 0.62, 0.22, 1.0);
uniform float team_mix = 0.0; // 0 keeps the strips' own amber, 1 paints them team_color
uniform float strip_glow = 1.2; // how much the strips light up
uniform float hue_lo = 0.03; // the strips' hue band (0..1 round the wheel): amber to yellow
uniform float hue_hi = 0.15;
uniform float sat_min = 0.5;
uniform float val_min = 0.55;
uniform float warm_calm = 0.0; // rocks: warm, saturated pixels go grey and darker, so slag reads cold (game feel's second look)

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

vec3 rgb2hsv(vec3 c) {
	vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
	vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
	float d = q.x - min(q.w, q.y);
	return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + 1e-10)), d / (q.x + 1e-10), q.x);
}

void fragment() {
	if (PROJECTION_MATRIX[3][3] < 0.5 && fade_cut(world_pos, INV_VIEW_MATRIX[3].xyz, FRAGCOORD.xy)) {
		discard;
	}
	vec3 col = texture(albedo_texture, UV).rgb * albedo.rgb;
	vec3 hsv = rgb2hsv(col);
	float strip = smoothstep(hue_lo - 0.02, hue_lo + 0.01, hsv.x) * (1.0 - smoothstep(hue_hi - 0.01, hue_hi + 0.02, hsv.x))
		* smoothstep(sat_min - 0.1, sat_min + 0.1, hsv.y) * smoothstep(val_min - 0.1, val_min + 0.1, hsv.z);
	vec3 paint = team_color.rgb * (0.55 + 0.6 * hsv.z);
	col = mix(col, paint, strip * team_mix);
	if (warm_calm > 0.0) {
		float sat = smoothstep(0.2, 0.45, hsv.y);
		float warm = max(1.0 - smoothstep(0.14, 0.2, hsv.x), smoothstep(0.93, 0.97, hsv.x)) * sat; // red to yellow
		float lum = dot(col, vec3(0.3, 0.59, 0.11));
		col = mix(col, vec3(lum) * vec3(0.36, 0.38, 0.44), warm * warm_calm); // grey and dark: bright orange went pale grey at 0.72
	}
	vec3 lit = col * strip * strip_glow;
	if (use_emission) {
		lit += texture(emission_texture, UV).rgb;
	}
	float fog_s = fog_seen(world_pos);
	ALBEDO = fog_tint(col, fog_s);
	EMISSION = lit * mix(fog_dim, 1.0, fog_s);
	if (use_orm) {
		vec4 orm = texture(orm_texture, UV);
		ROUGHNESS = orm.g;
		METALLIC = orm.b;
	} else {
		ROUGHNESS = roughness;
		METALLIC = metallic;
	}
	if (use_normal) {
		NORMAL_MAP = texture(normal_texture, UV).rgb;
	}
}
