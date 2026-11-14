shader_type spatial;
// Hippo overcharged Vent slow (hippo effects lane, 2026-11-12): thick toxic goo clinging to a slowed enemy's legs.
// It is the opposite of the poison fumes, which rise: this is heavy, wet and sinking. It is drawn on an open cylinder
// round the unit's feet, base at the ground. A band of goo coats the lower legs, strands reach up from it grabbing at
// the body with beads sliding back down them, and a wet sheen runs along the top edge. `disc` mode draws the sticky
// ground patch under the unit instead.
// Colours stay at or below 0.98 (no HDR); only the sheen goes as high as 0.9.
render_mode unshaded, blend_mix, cull_disabled, depth_draw_never, fog_disabled, shadows_disabled;

uniform float strength = 1.0;
uniform float seed = 0.0;
uniform float disc = 0.0; // 1: the ground patch (UV centred), 0: the leg coat
uniform float pull = 0.0; // 0..1, a short tug when the unit moves: the fingers stretch
uniform float height = 0.5; // the sleeve's height in metres: height and angle come from the vertex, not UV
// (CylinderMesh does not run UV.y 0..1 down its side, so a UV-based height drew only stray strand tips, as shards)
uniform vec3 deep : source_color = vec3(0.13, 0.03, 0.20);
uniform vec3 goo : source_color = vec3(0.42, 0.13, 0.58);
uniform vec3 sheen : source_color = vec3(0.86, 0.64, 0.96);

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

varying float vh;
varying float va;

void vertex() {
	vh = clamp(VERTEX.y / max(height, 0.01) + 0.5, 0.0, 1.0);
	va = atan(VERTEX.z, VERTEX.x) / 6.2831853 + 0.5;
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void fragment() {
	float t = TIME * 0.6 + seed;
	vec3 col;
	float a;
	if (disc > 0.5) {
		vec2 c = (UV - 0.5) * 2.0;
		float r = length(c);
		float ang = atan(c.y, c.x);
		float edge = 0.78 + 0.12 * noise(vec2(ang * 3.0 + seed, t * 0.5));
		float body = 1.0 - smoothstep(edge - 0.06, edge, r);
		float lip = smoothstep(edge - 0.16, edge - 0.05, r) * body;
		float blob = noise(c * 4.0 + vec2(seed, t * 0.3));
		col = mix(deep, goo, 0.4 + 0.4 * blob) + sheen * lip * 0.45;
		a = body * (0.7 + 0.2 * blob);
	} else {
		float h = vh;   // 0 at the ground, 1 at the top of the sleeve
		float ang = va;
		float band = 0.42 + 0.08 * noise(vec2(ang * 11.0 + seed, t * 0.4));
		// strands: some columns reach above the band; the coat is solid below it
		float col_n = noise(vec2(ang * 14.0 + seed * 3.0, 0.0));  // fewer, wider strands: thin ones read as shards edge-on
		float strand = smoothstep(0.55, 0.8, col_n);  // soft-edged columns: each strand is thick in the middle and thins out
		float finger = strand * (0.16 + 0.3 * col_n + 0.25 * pull);  // so the tips come out rounded, not cut
		float creep = fract(t * 0.35 + col_n * 4.0);           // a bead sliding down each finger
		float coat = 1.0 - smoothstep(band - 0.05, band + 0.03, h);
		float hang = strand * (1.0 - smoothstep(band + finger - 0.09, band + finger, h)) * smoothstep(band - 0.05, band, h);
		float shape = max(coat, hang);
		float db = (h - mix(band + finger, band, creep)) / 0.035;
		float bead = hang * exp(-db * db);
		float dr = (h - band) / 0.03;
		float rim = exp(-dr * dr) * (1.0 - strand * 0.5);
		float view_rim = 1.0 - abs(dot(NORMAL, VIEW));
		float thick = 1.0 - smoothstep(0.0, band + 0.1, h);  // heaviest at the feet, thinning up the legs
		float n = noise(vec2(ang * 14.0, h * 5.0 - t * 0.2));
		col = mix(deep, goo, 0.2 + 0.45 * n * (0.4 + h));
		// drips: slow drops forming at the top edge, sagging, then running down the coat to the ground, each in its
		// own column on its own clock, a thin trail left above them
		float cells = 9.0;
		float cell = floor(ang * cells);
		float dh = hash(vec2(cell, seed));
		float dphase = fract(t * (0.18 + 0.12 * dh) + dh * 7.0);
		float hang_t = smoothstep(0.0, 0.35, dphase);                  // sags at the lip first,
		float run_t = smoothstep(0.35, 1.0, dphase);                   // then runs down
		float dy_at = band + 0.02 - hang_t * 0.06 - run_t * (band + 0.08);
		float dx = (fract(ang * cells) - 0.5) / (0.16 + 0.05 * dh);
		float dyy = (h - dy_at) / (0.07 + 0.03 * hang_t);
		float drop = exp(-(dx * dx + dyy * dyy)) * step(0.35, dh);    // about two in three columns drip
		float trail = exp(-dx * dx * 6.0) * step(dy_at, h) * (1.0 - smoothstep(band - 0.02, band + 0.02, h)) * run_t * 0.55 * step(0.35, dh);
		float drip = max(drop, trail);
		// the wet shine: a glossy streak down the side facing the camera, broken up so it reads as liquid
		float facing = abs(dot(NORMAL, VIEW));
		float gloss = smoothstep(0.82, 0.97, facing) * (0.55 + 0.45 * noise(vec2(ang * 30.0, h * 3.0 - t * 0.5))) * shape;
		col = mix(col, goo * 1.15, drip * 0.7);
		col += sheen * (rim * 0.5 + bead * 0.5 + gloss * 0.4 + drop * 0.45);
		shape *= 1.0 - view_rim * view_rim * 0.6;  // edge-on the cylinder fades instead of stacking into spikes
		a = max(shape * (0.62 + 0.3 * thick + 0.08 * n), drip * 0.9) + bead * 0.2;
	}
	ALBEDO = min(col, vec3(0.98));
	ALPHA = clamp(a * strength, 0.0, 0.95);
}
