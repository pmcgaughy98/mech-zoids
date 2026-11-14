shader_type spatial;
// Hippo Vent, the ground layer (hippo effects lane, 2026-11-11). A wedge on the floor, apex at the jaws. Structure
// from SMITE 2's Belch of the Gods (docs/reference/hippo-fx-synthesis-2026-11-11.md): the cone is on the floor at full
// size within a frame or two, a translucent fill with brighter side rims and far arc, and a band sweeping outward on
// each hit. Look (Preston, 2026-11-11): "purple liquid ... poisonous or toxic", so this is a toxic violet liquid, not
// light: blend_mix so it can be dark and wet, with a few glowing highlights above HDR 1.05 for the toxic sheen.
// After cone_end the spray leaves a bubbling puddle (Intoxicate's ragged liquid edge) that shrinks away (residue).
// The quad's +Z (UV.y) points forward from the apex; UV.x runs across.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;

uniform float range_m = 5.5;
uniform float half_angle = 0.52; // radians
uniform float age = 0.0;     // seconds since cone_start
uniform float fade = 1.0;    // the spray layer: 1 while open, falls to 0 after cone_end
uniform float residue = 0.0; // the puddle left behind: rises while open, shrinks away after
uniform float pulse = 0.0;   // 1 on a hit, decays
uniform float seed = 0.0;
uniform float pool_at = 1.65; // metres from the apex to the puddle's centre (kit: 0.6 of the range from the body)
uniform float pool_r = 1.6;   // the kit's puddle_radius
uniform vec3 liquid : source_color = vec3(0.30, 0.07, 0.46);
uniform vec3 shine : source_color = vec3(0.78, 0.36, 1.0);
uniform vec3 hot : source_color = vec3(1.0, 0.82, 1.0);

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7)) + seed) * 43758.5453); }
float noise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}
vec2 hash2(vec2 p) { return vec2(hash(p), hash(p + 17.3)); }

void fragment() {
	float w = 2.0 * range_m * sin(half_angle);
	vec2 p = vec2((UV.x - 0.5) * w, UV.y * range_m); // metres, apex at (0, 0)
	float d = length(p);
	float ang = atan(p.x, max(p.y, 0.0001));
	float edge_dist = (half_angle - abs(ang)) * d; // metres to the side rim, inside > 0
	float inside = smoothstep(-0.05, 0.12, edge_dist) * step(0.0, p.y);
	float reach = range_m * (1.0 - pow(1.0 - clamp(age / 0.08, 0.0, 1.0), 3.0));
	float front = smoothstep(reach + 0.05, reach - 0.25, d);
	float fall = 1.0 - smoothstep(range_m * 0.55, range_m * 1.0, d) * 0.45;
	// liquid streaks running outward along the spray
	float s = noise(vec2(ang * 9.0, d * 1.1 - age * 11.0)) * 0.6 + noise(vec2(ang * 23.0, d * 2.6 - age * 17.0)) * 0.4;
	float streak = smoothstep(0.5, 0.95, s);
	float band_pos = (1.0 - pulse) * range_m * 1.15;
	float band = exp(-pow((d - band_pos) / 0.35, 2.0)) * pulse;
	float rim_side = exp(-pow(max(edge_dist, 0.0) / 0.09, 2.0));
	float rim_far = exp(-pow((reach - d) / 0.12, 2.0));
	float spray_a = (0.30 * fall + 0.35 * streak * fall + rim_side * 0.55 + rim_far * 0.5 + band * 0.5) * inside * front * fade;
	vec3 spray_c = mix(liquid, shine, 0.35 * streak + 0.5 * rim_side + 0.5 * rim_far) + hot * band * 0.55;

	// the puddle: the kit's damage circle (pool_r round pool_at on the cone's axis; Preston 2026-11-12 "match it"), a
	// ragged liquid edge that shrinks toward the centre as residue falls, with bubbles popping
	float blot = noise(p * 0.9 + seed) * 0.55 + noise(p * 2.3 - seed) * 0.3 + noise(p * 6.0) * 0.15;
	float circ = (pool_r - length(p - vec2(0.0, pool_at))) / pool_r;
	float lvl = circ * 2.2 + (blot - 0.5) * 0.35 - (1.0 - residue) * 2.0;
	float wet = smoothstep(0.0, 0.05, lvl) * step(d, reach + 0.1);
	float lip = exp(-pow(lvl / 0.05, 2.0)) * step(d, reach + 0.1); // a glowing edge where the liquid ends
	vec2 cell = floor(p * 2.2);
	vec2 bp = (cell + 0.2 + 0.6 * hash2(cell)) / 2.2;
	float phase = fract(age * 0.9 + hash(cell + 3.1));
	float br = 0.03 + 0.09 * phase;
	float ring = exp(-pow((length(p - bp) - br) / 0.018, 2.0)) * (1.0 - phase) * step(0.55, hash(cell + 7.7));
	// first take: a dark puddle vanished on the dark blue floor, so it glows like a toxic spill with a bright lip
	float pud_a = max(wet * (0.7 + 0.25 * ring), lip * 0.85 * step(0.02, residue));
	vec3 pud_c = mix(liquid * 1.6, shine * 1.1, 0.3 + 0.3 * smoothstep(0.6, 1.0, blot) + ring * 0.7) + shine * lip * 0.6;

	float a = max(spray_a, pud_a);
	vec3 col = spray_a >= pud_a ? spray_c : pud_c;
	ALBEDO = col;
	ALPHA = clamp(a, 0.0, 0.92);
}
