// The arena's whole ground in one plane. Map design lane, 2026-11-04.
// Paints, from the layout numbers arena_blockout.gd passes in: dark jungle grass everywhere, bright grass inside
// the lane walls, the worn dirt path down the lane, the paved plaza and bases (each base tinted its team's colour),
// spawn pads, camp clearings, the side pit floors and the stream. Every edge steps on the shared 50 texels per metre
// grid and is ragged by a little noise, so nothing reads as a vector shape. Change a number in arena_blockout.gd and
// the ground follows. Lit (takes the sun's shadows); only the water moves, at a few frames a second like pixel art.
shader_type spatial;

uniform sampler2D lane_grass_tex : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D jungle_tex : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D dirt_tex : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D paving_tex : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D pit_tex : source_color, filter_nearest_mipmap, repeat_enable;
uniform float texels_per_metre = 50.0;
uniform float tile_px = 32.0;

uniform vec2 lane_pts[8]; // the lane centre line, core to core
uniform int lane_count = 0;
uniform float path_half = 2.2;
uniform float lane_half = 7.0;
uniform float plaza_r = 13.0;
uniform vec4 plaza_tint : source_color = vec4(1.0, 0.86, 0.66, 1.0);
uniform vec4 bases[2]; // x, z, radius, team (1 blue, -1 red)
uniform vec4 blue_tint : source_color = vec4(0.78, 0.86, 1.0, 1.0);
uniform vec4 red_tint : source_color = vec4(1.0, 0.8, 0.74, 1.0);
uniform vec4 pads[12]; // x, z, radius, kind: 1 camp clearing, 2 pit floor, 3 blue spawn, 4 red spawn
uniform int pad_count = 0;
uniform float stream_half = 1.6;
uniform float stream_gap = 14.2; // no water within this distance of x = 0: the plaza
uniform vec4 water_deep : source_color = vec4(0.16, 0.42, 0.66, 1.0);
uniform vec4 water_mid : source_color = vec4(0.23, 0.53, 0.78, 1.0);
uniform vec4 water_light : source_color = vec4(0.49, 0.78, 0.95, 1.0);
uniform vec4 water_foam : source_color = vec4(0.84, 0.94, 1.0, 1.0);
uniform float water_fps = 6.0;
uniform float water_glow = 0.0; // the tech themes' coolant gives off light
// Themes (2026-11-04): tile pixels glow by 1 - alpha; ragged 0 gives clean machined edges; line_color draws a lit line
// along the path edges and the plaza rim, and blue_line / red_line round each base.
uniform float glow_energy = 0.0;
uniform float ragged = 1.0;
uniform vec4 line_color : source_color = vec4(0.0);
uniform vec4 blue_line : source_color = vec4(0.0);
uniform vec4 red_line : source_color = vec4(0.0);
uniform float line_width = 0.08;
uniform bool stage = false; // foundry (2026-11-06 floor zones): the plaza drawn as a stage, the spawn pads with a team emblem
uniform vec4 stage_dark : source_color = vec4(0.12, 0.11, 0.14, 1.0);
// Detail pass (themes with a "detail" entry, 2026-11-04): a map baked by arena_blockout.gd (_floor_map) with contact
// shade by walls, rocks and structures in r and the wall lamps' light in g, both stepped in thirds with a dithered
// edge, plus a slow three-step brightness drift so a big floor never reads as one repeated tile.
uniform bool use_detail = false;
uniform sampler2D floor_map : filter_linear, repeat_disable, hint_default_black;
uniform vec4 floor_rect = vec4(-44.0, -80.0, 88.0, 160.0); // the map's corner (world x, z) and size in metres
uniform float ao_strength = 0.4;
uniform vec4 grime_color : source_color = vec4(0.78, 0.6, 0.48, 0.5); // the shade leans this way, by alpha
uniform vec4 pool_color : source_color = vec4(1.0, 0.66, 0.3, 1.0);
uniform float pool_energy = 0.45;
uniform float macro = 0.06;

#include "res://shaders/world/fog.gdshaderinc"
varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

// A tile of any size at the shared grid: w is in texels (world metres times texels_per_metre).
vec4 tile(sampler2D t, vec2 w) {
	return texture(t, w / vec2(textureSize(t, 0)));
}

// 4 x 4 ordered dither, 0 to 1, from a texel's whole coordinates.
float bayer2(vec2 a) {
	a = floor(a);
	return fract(dot(a, vec2(0.5, a.y * 0.75)));
}

float bayer4(vec2 a) {
	return bayer2(0.5 * a) * 0.25 + bayer2(a);
}

float lane_dist(vec2 q) {
	float best = 1e6;
	for (int i = 0; i < 7; i++) {
		if (i + 1 >= lane_count) {
			break;
		}
		vec2 a = lane_pts[i];
		vec2 ab = lane_pts[i + 1] - a;
		float t = clamp(dot(q - a, ab) / dot(ab, ab), 0.0, 1.0);
		best = min(best, length(q - (a + ab * t)));
	}
	return best;
}

// true inside an edge at distance e, with a band of scattered pixels just outside it (a worn, ragged border)
bool worn(float d, float e, float band, float grain) {
	return d < e || (d < e + band && grain < 0.5 - 0.5 * (d - e) / band);
}

void fragment() {
	vec2 q = (floor(world_pos.xz * texels_per_metre) + 0.5) / texels_per_metre; // texel centre: edges step on the grid
	vec2 uv = world_pos.xz * texels_per_metre; // in texels; tile() fits each tile's own size (32 px, or 128 in foundry)
	float rag = (vnoise(q * 2.2) - 0.5) * ragged; // edges wander about half a metre
	float grain = hash(floor(q * texels_per_metre)); // one random value per texel
	float band = 0.5 * ragged + 0.001;
	vec4 col = tile(jungle_tex, uv);
	vec3 lit = vec3(0.0); // light given off, on top of the glow in the tiles
	float ld = lane_dist(q);
	if (worn(ld, lane_half + 0.6 + rag, band, grain)) {
		col = tile(lane_grass_tex, uv);
	}
	if (worn(ld, path_half + rag * 0.7, band, grain)) {
		col = tile(dirt_tex, uv);
	}
	if (line_color.a > 0.0 && abs(ld - path_half) < line_width) {
		col = vec4(line_color.rgb, 1.0);
		lit = line_color.rgb * line_color.a;
	}
	if (abs(q.x) > stream_gap) {
		float bank = stream_half + rag * 0.35;
		float sz = abs(q.y);
		if (sz < bank + 0.3) {
			col = vec4(tile(dirt_tex, uv).rgb * 0.6, 1.0); // a muddy bank
		}
		if (sz < bank) {
			float t = floor(TIME * water_fps) / water_fps;
			float w = vnoise(vec2(q.x * 1.6 - t * 1.4, q.y * 4.0)) + 0.3 * sin(q.x * 5.0 - t * 4.0 + q.y * 3.0);
			vec3 wc = water_mid.rgb;
			if (w < 0.32) {
				wc = water_deep.rgb;
			} else if (w > 0.92) {
				wc = water_light.rgb;
			}
			if (sz > bank - 0.1 - 0.08 * grain) {
				wc = water_foam.rgb; // a broken line of foam along each bank
			}
			col = vec4(wc, 1.0);
			lit = wc * water_glow;
		}
	}
	vec4 pave = tile(paving_tex, uv);
	float pr = length(q);
	if (pr < plaza_r + 0.3) {
		col = vec4(pave.rgb * plaza_tint.rgb, pave.a);
		lit = vec3(0.0);
		if (stage) { // the beacon's light dais, a dark ring, twelve sectors split by spokes, then a lit inlay ring
			float turns = atan(q.y, q.x) / 6.2831853 + 0.5;
			float sec = fract(turns * 12.0);
			if (pr < 4.7) {
				col = vec4(tile(lane_grass_tex, uv).rgb * plaza_tint.rgb * 0.9, 1.0);
			} else if (pr < 5.1) {
				col = vec4(stage_dark.rgb, 1.0);
			} else if (pr < 9.0) {
				col.rgb *= mod(floor(turns * 12.0), 2.0) > 0.5 ? 0.8 : 1.0;
				if (min(sec, 1.0 - sec) * 6.2831853 / 12.0 * pr < 0.07) {
					col = vec4(stage_dark.rgb, 1.0);
				}
			} else if (pr < 9.36) {
				col = vec4(line_color.rgb, 1.0);
				lit = line_color.rgb * line_color.a;
			}
		}
	}
	if (line_color.a > 0.0 && abs(pr - plaza_r - 0.3) < line_width) {
		col = vec4(line_color.rgb, 1.0);
		lit = line_color.rgb * line_color.a;
	}
	for (int i = 0; i < 2; i++) {
		vec4 b = bases[i];
		float bd = distance(q, b.xy);
		if (b.z > 0.0 && bd < b.z + 0.2) {
			col = vec4(pave.rgb * (b.w > 0.0 ? blue_tint.rgb : red_tint.rgb), pave.a);
			lit = vec3(0.0);
		}
		vec4 bl = b.w > 0.0 ? blue_line : red_line;
		if (b.z > 0.0 && bl.a > 0.0 && abs(bd - b.z + 1.2) < line_width * 1.5) { // just inside the base wall
			col = vec4(bl.rgb, 1.0);
			lit = bl.rgb * bl.a;
		}
	}
	for (int i = 0; i < 12; i++) {
		if (i >= pad_count) {
			break;
		}
		vec4 p = pads[i];
		float d = distance(q, p.xy);
		if (p.w < 1.5) {
			if (worn(d, p.z + rag * 0.8, band, grain)) {
				vec4 t = tile(dirt_tex, uv);
				col = vec4(t.rgb * 0.9, t.a); // a trampled clearing
			}
		} else if (p.w < 2.5) {
			if (d < p.z) {
				col = tile(pit_tex, uv);
			}
		} else if (d < p.z) {
			vec3 tint = p.w < 3.5 ? blue_tint.rgb : red_tint.rgb;
			col = vec4(pave.rgb * tint * tint, pave.a); // the spawn pad: the base's paving, twice as tinted
			if (stage) { // a lit team ring and three chevrons pointing up the map
				vec4 tl = p.w < 3.5 ? blue_line : red_line;
				vec2 dir = normalize(-p.xy);
				vec2 rel = q - p.xy;
				float across = abs(dot(rel, vec2(-dir.y, dir.x)));
				float v = dot(rel, dir) - across * 0.8;
				bool chev = d < p.z - 1.0 && across < 2.4 && v > -2.2 && v < 2.0 && fract(v / 1.4) < 0.3;
				if (abs(d - (p.z - 0.6)) < 0.12 || chev) {
					col = vec4(tl.rgb, 1.0);
					lit = tl.rgb * tl.a * 1.6;
				}
			}
		}
	}
	vec3 pool_lit = vec3(0.0);
	if (use_detail) {
		float b = bayer4(floor(q * texels_per_metre)) - 0.5;
		float mv = vnoise(q * 0.13) * 0.65 + vnoise(q * 0.41 + 17.0) * 0.35;
		col.rgb *= 1.0 + (clamp(floor(mv * 3.0 + b * 0.35), 0.0, 2.0) - 1.0) * macro;
		vec4 fm = texture(floor_map, (q - floor_rect.xy) / floor_rect.zw);
		float ao = clamp(floor(fm.r * 3.0 + 0.5 + b * 0.6), 0.0, 3.0) / 3.0;
		col.rgb = mix(col.rgb, col.rgb * grime_color.rgb, ao * grime_color.a);
		col.rgb *= 1.0 - ao * ao_strength;
		float pool = clamp(floor(fm.g * 3.0 + 0.5 + b * 0.2), 0.0, 3.0) / 3.0; // a narrow dither: crisp rings at range
		col.rgb = mix(col.rgb, col.rgb * (1.0 + pool_color.rgb * 0.5), pool * 0.6);
		pool_lit = pool_color.rgb * pool;
	}
	float fog_s = fog_seen(world_pos);
	ALBEDO = fog_tint(col.rgb, fog_s);
	EMISSION = (col.rgb * (1.0 - col.a) * glow_energy + lit * glow_energy + pool_lit * pool_energy) * mix(fog_dim, 1.0, fog_s);
	ROUGHNESS = 1.0;
	SPECULAR = 0.0;
}
