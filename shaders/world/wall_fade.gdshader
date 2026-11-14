// World walls, rocks, cliffs and towers. Map design lane, 2026-11-04.
// Pixel tiles projected from the world (triplanar) at the shared 50 texels per metre, plus the dither fade
// (fade_cut.gdshaderinc) so a wall between the chase camera and the player's machine never hides the machine.
// Art pass, 2026-11-04: an optional grass top with a ragged lip over the edge, darker stone near the ground, and
// an optional painted stripe (the team colour on base walls, towers and cores).
// Use this on things that stand up. Floors use ground.gdshader: under the machine they would dither too.
shader_type spatial;

#include "res://shaders/world/fade_cut.gdshaderinc"
#include "res://shaders/world/fog.gdshaderinc"

uniform sampler2D albedo_texture : source_color, filter_nearest_mipmap, repeat_enable, hint_default_white;
uniform vec4 albedo : source_color = vec4(1.0);
uniform float texels_per_metre = 50.0;
uniform float tile_px = 32.0;
uniform float blend_sharpness = 8.0; // high, so a face takes one projection and the pixels stay crisp

uniform sampler2D top_texture : source_color, filter_nearest_mipmap, repeat_enable, hint_default_white;
uniform bool use_top = false; // grass on the up faces, hanging a few pixels over the edge
uniform vec4 top_tint : source_color = vec4(1.0);
uniform float lip_texels = 4.0; // how far the grass hangs down the side, give or take two pixels

uniform float ao_height = 0.6; // the bottom of a face darkens in three steps over this many metres
uniform float ao_strength = 0.3;

uniform float glow_energy = 0.0; // themes: tile pixels glow by 1 - alpha
uniform vec4 lip_color : source_color = vec4(0.0); // themes: a lit line along the top edge instead of the grass lip
uniform bool lip_hazard = false; // themes: the lip in yellow and black stripes

uniform vec4 band_color : source_color = vec4(0.0); // a painted stripe; alpha 0 for none
uniform float band_lo = 0.0; // metres above the ground
uniform float band_hi = 0.0;
uniform float band_glow = 0.0; // the stripe gives off light: the foundry towers' and cores' team rings
uniform bool use_local = false; // tiles follow the mesh, not the world, so a turning head keeps its pixels

varying vec3 world_pos;
varying vec3 world_normal;
varying float top_y;
varying vec3 local_pos;
varying vec3 local_normal;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = (MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz;
	local_pos = VERTEX;
	local_normal = NORMAL;
	top_y = MODEL_MATRIX[3].y * 2.0; // every wall, rim, rock, pillar and post has its origin halfway up (MultiMesh posts too)
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	// The sun's shadow pass is orthographic: skip the fade there, so walls keep whole shadows.
	if (PROJECTION_MATRIX[3][3] < 0.5 && fade_cut(world_pos, INV_VIEW_MATRIX[3].xyz, FRAGCOORD.xy)) {
		discard;
	}
	vec3 n = normalize(world_normal);
	vec3 tn = use_local ? normalize(local_normal) : n;
	vec3 w = pow(abs(tn), vec3(blend_sharpness));
	w /= dot(w, vec3(1.0));
	vec3 p = (use_local ? local_pos : world_pos) * (texels_per_metre / float(textureSize(albedo_texture, 0).x)) * vec3(1.0, -1.0, 1.0); // any square tile size
	vec4 tex = texture(albedo_texture, p.xy) * w.z
		+ texture(albedo_texture, p.xz) * w.y
		+ texture(albedo_texture, p.zy * vec2(-1.0, 1.0)) * w.x;
	vec3 col = albedo.rgb * tex.rgb;
	vec3 lit = col * (1.0 - tex.a);
	float ty = floor(world_pos.y * texels_per_metre) / texels_per_metre; // height snapped to the pixel grid
	if (band_color.a > 0.0 && n.y < 0.5 && ty >= band_lo && ty < band_hi) {
		float lum = dot(tex.rgb, vec3(0.3, 0.59, 0.11));
		col = band_color.rgb * (0.7 + 0.6 * lum); // keeps the stone's grain under the paint
		if (band_glow > 0.0) {
			lit = band_color.rgb * band_glow;
		}
	}
	float k = floor(clamp(ty / ao_height, 0.0, 1.0) * 3.0) / 3.0;
	col *= mix(1.0 - ao_strength, 1.0, k);
	if (use_top) {
		vec4 top = texture(top_texture, world_pos.xz * texels_per_metre / vec2(textureSize(top_texture, 0))) * top_tint;
		// one column of pixels along the face: the lip ends at a different depth in each
		float column = floor((world_pos.x + world_pos.z) * texels_per_metre);
		float lip = (lip_texels + floor(hash(vec2(column, top_y)) * 3.0) - 1.0) / texels_per_metre;
		if (n.y > 0.5) {
			col = top.rgb;
			lit = top.rgb * (1.0 - top.a);
		} else if (world_pos.y > top_y - lip) {
			col = top.rgb * 0.78; // the lip is in the shade of the top
			if (lip_hazard) {
				col = mod(column + floor(world_pos.y * texels_per_metre), 8.0) < 4.0 ? vec3(0.94, 0.75, 0.13) : vec3(0.13, 0.12, 0.15);
				lit = vec3(0.0);
			} else if (lip_color.a > 0.0) {
				col = lip_color.rgb;
				lit = lip_color.rgb * lip_color.a;
			}
		}
	}
	float fog_s = fog_seen(world_pos);
	ALBEDO = fog_tint(col, fog_s);
	EMISSION = lit * glow_energy * mix(fog_dim, 1.0, fog_s);
	ROUGHNESS = 1.0;
	SPECULAR = 0.0;
}
