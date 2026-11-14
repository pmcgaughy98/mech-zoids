// The tilted machine sprite with the chameleon's camouflage (chameleon lane, Claude, 2026-11-05). Look B, "colour
// match", picked by Preston 2026-11-05. A superset of the game feel lane's tilted_sprite_3d.gdshader (2026-11-04):
// vertex(), `tex`, `lift` and the render mode are theirs, copied verbatim; the camouflage is added in fragment().
// It stays a cutout (discard below alpha 0.5, no blending, no screen reads), so depth and sorting are the tilt
// shader's. The script computes everything; the shader only reads the values below.
//
// How it looks: the plates take on the floor's colours, washing up from the feet behind a one-pixel pale line.
//   Enemy view: the washed rows dissolve in an ordered 4x4 dither and are gone when fully camouflaged. camo_tell
//   (an enemy close by) brings back a sparse scatter of ground-coloured plate pixels.
//   Ally view: a ground-coloured chameleon with a travelling pale rim, the eyes kept.
//   camo_rim_flash lights the rim for the 2-frame break flash.
// Board, scores and reasoning: docs/art/moba/chameleon_m/camo/, docs/reference/camouflage-reads-2026-11-05.md.
shader_type spatial;
render_mode unshaded, cull_disabled;

uniform sampler2D tex : source_color, filter_nearest;
uniform float lift = 0.0; // metres from the feet up to the node's origin (DirectionalSprite3D raises the node by this)

uniform float camo_hide : hint_range(0.0, 1.0) = 0.0;      // the wash: 0 normal, 1 fully camouflaged (tween over ~0.6 s)
uniform bool camo_ally_view = false;                       // the local player is on the chameleon's team
uniform float camo_tell : hint_range(0.0, 1.0) = 0.0;      // enemy view: 0 no one near, 1 an enemy close (Preston's ~4 m)
uniform float camo_shimmer = -1.0;                         // ally rim shimmer phase 0..1; below 0 it runs on TIME
uniform float camo_rim_flash : hint_range(0.0, 1.0) = 0.0; // the break flash: 1 lights the whole rim
uniform vec3 camo_floor_a : source_color = vec3(0.45, 0.62, 0.20); // floor colours under the machine, commonest first,
uniform vec3 camo_floor_b : source_color = vec3(0.36, 0.52, 0.16); // sampled by the script
uniform vec3 camo_floor_c : source_color = vec3(0.55, 0.72, 0.26);
uniform vec3 camo_rim : source_color = vec3(0.6235, 0.9608, 0.9020);   // #9ff5e6, the chameleon's own pale turquoise
uniform vec3 camo_flash : source_color = vec3(1.0, 0.9843, 0.9020);    // #fffbe6, its brightest lens tone
uniform vec3 camo_lens_a : source_color = vec3(1.0, 0.8471, 0.2902);   // #ffd84a: the lens colours, front views only
uniform vec3 camo_lens_b : source_color = vec3(1.0, 0.9451, 0.6275);   // #fff1a0
uniform vec3 camo_lens_c : source_color = vec3(1.0, 0.9843, 0.9020);   // #fffbe6
uniform float camo_texel_m = 0.020;   // metres per texel (the sprite's pixel_size)
uniform float camo_body_height = 1.18; // metres from the feet edge to the top of the body (take-b e view: 59 rows)
uniform float camo_lum_mean = 0.4544;  // the body's mean luminance, measured from the take-b e view

varying float camo_up; // metres up the quad from the feet edge

void vertex() {
	vec3 s = vec3(length(MODEL_MATRIX[0].xyz), length(MODEL_MATRIX[1].xyz), length(MODEL_MATRIX[2].xyz));
	vec3 from_feet = (VERTEX + vec3(0.0, lift, 0.0)) * s; // the quad measured from the feet row, the pivot
	vec3 feet = MODEL_MATRIX[3].xyz - vec3(0.0, lift * s.y, 0.0);
	vec3 world = feet + mat3(INV_VIEW_MATRIX[0].xyz, INV_VIEW_MATRIX[1].xyz, INV_VIEW_MATRIX[2].xyz) * from_feet;
	vec4 v = VIEW_MATRIX * vec4(world, 1.0);
	float t = max(from_feet.y, 0.0); // metres up the quad from the feet
	float tan_pitch = max(INV_VIEW_MATRIX[2].y, 0.0) / max(INV_VIEW_MATRIX[1].y, 0.05);
	// Steep cameras (the ult rise, 70 and 85 degrees; camera lane, 2026-11-04): t * tan(pitch) grows past the camera
	// and the quad was clipped away. The slope stops at 55 degrees' (game camera 30 and the ult's 55 are unchanged),
	// and the push never passes 80% of the way to the camera, so a sprite close to the lens can't cross it either.
	tan_pitch = min(tan_pitch, 1.43);
	float push = min(t * tan_pitch, 0.8 * max(-v.z, 0.0));
	vec4 clip = PROJECTION_MATRIX * v;
	vec4 upright = PROJECTION_MATRIX * vec4(v.xy, v.z + push, 1.0);
	POSITION = vec4(clip.xy, upright.z / upright.w * clip.w, clip.w);
	camo_up = from_feet.y; // camouflage only: kept signed so rows below the feet edge count as below
}

// The 4x4 ordered dither value of a texel, 0..1 (the same order as the look board).
float camo_bayer(ivec2 p) {
	int a = ((p.x ^ p.y) & 1) << 1 | (p.y & 1);
	int b = (((p.x >> 1) ^ (p.y >> 1)) & 1) << 1 | ((p.y >> 1) & 1);
	return (float(a * 4 + b) + 0.5) / 16.0;
}

bool camo_is_lens(vec3 c) {
	return distance(c, camo_lens_a) < 0.03 || distance(c, camo_lens_b) < 0.03 || distance(c, camo_lens_c) < 0.03;
}

void fragment() {
	vec4 c = texture(tex, UV) * COLOR;
	if (c.a < 0.5) {
		discard;
	}
	vec3 col = c.rgb;
	if (camo_hide > 0.0 || camo_rim_flash > 0.0) {
		ivec2 ts = textureSize(tex, 0);
		ivec2 texel = ivec2(floor(UV * vec2(ts)));
		float b = camo_bayer(texel);
		bool rim = texelFetch(tex, texel + ivec2(-1, 0), 0).a < 0.5 || texelFetch(tex, texel + ivec2(1, 0), 0).a < 0.5
				|| texelFetch(tex, texel + ivec2(0, -1), 0).a < 0.5 || texelFetch(tex, texel + ivec2(0, 1), 0).a < 0.5;
		if (camo_hide > 0.0) {
			// The floor's colours scattered over the body in the dither order, the commonest on half the texels.
			vec3 floor_col = b < 0.5 ? camo_floor_a : (b < 0.8 ? camo_floor_b : camo_floor_c);
			float shade = dot(c.rgb, vec3(0.2126, 0.7152, 0.0722)) - camo_lum_mean;
			// The wash, a row at a time from the feet up, a quarter of the body wide.
			float rows_up = floor(camo_up / camo_texel_m + 0.001);
			float u = clamp(rows_up * camo_texel_m / camo_body_height, 0.0, 1.0);
			float k = clamp((camo_hide * 1.25 - u) / 0.25, 0.0, 1.0);
			bool front = k > 0.0 && k <= camo_texel_m / (0.25 * camo_body_height) + 0.0001;
			if (camo_ally_view) {
				col = mix(c.rgb, clamp(floor_col * (1.0 + 1.3 * shade), 0.0, 1.0), k * 0.7);
				if (front) {
					col = camo_rim;
				}
				if (camo_hide > 0.6) {
					float ph = camo_shimmer < 0.0 ? fract(TIME) : camo_shimmer;
					bool band = mod(float(texel.x + texel.y) + floor(ph * 12.0), 12.0) < 4.0;
					if (rim && band) {
						col = camo_rim;
					}
					if (camo_is_lens(c.rgb)) {
						col = c.rgb;
					}
				}
			} else if (front) {
				col = camo_rim;
			} else if (k >= 1.0) {
				// Fully washed: gone, except the tell's sparse ground-coloured plates (4 texels in 16 at tell 1).
				if (b >= camo_tell * 0.25) {
					discard;
				}
				col = clamp(floor_col * (1.0 + 1.6 * shade), 0.0, 1.0);
			} else if (k > 0.0) {
				// Mid-wash: the plates turn to the floor's colours and dissolve in the dither as k rises.
				if (b < k) {
					discard;
				}
				col = mix(c.rgb, clamp(floor_col * (1.0 + 1.3 * shade), 0.0, 1.0), k);
			}
		}
		if (camo_rim_flash > 0.0 && rim) {
			col = mix(col, camo_flash, camo_rim_flash);
		}
	}
	ALBEDO = col;
}
