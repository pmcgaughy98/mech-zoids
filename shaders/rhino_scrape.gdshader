shader_type spatial;
// Rhino paw scrape gouges (rhino effects lane, 2026-11-11). Three claw furrows dragged backward across the floor in
// about 0.12 s: dark cut lines with a pale dust lip, holding a moment, then fading. Local +V (UV.y) points backward.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;

uniform float age = 0.0;
uniform float life = 1.6;
uniform float seed = 0.0;

float hash(float n) { return fract(sin(n * 45.164 + seed) * 43758.5453); }

void fragment() {
	vec2 p = vec2(UV.x * 2.0 - 1.0, UV.y); // x across the paw, y from the paw (0) backward (1)
	float drawn = 1.0 - pow(1.0 - clamp(age / 0.12, 0.0, 1.0), 2.0);
	float fade = 1.0 - smoothstep(life * 0.55, life, age);
	float cut = 0.0;
	float lip = 0.0;
	for (int i = 0; i < 3; i++) {
		float fi = float(i);
		float x0 = (fi - 1.0) * 0.42 + (hash(fi) - 0.5) * 0.12 + p.y * (hash(fi + 3.0) - 0.5) * 0.25;
		float len = drawn * mix(0.75, 1.0, hash(fi + 7.0));
		float along = smoothstep(0.0, 0.08, p.y) * (1.0 - smoothstep(len - 0.25, len, p.y));
		float w = mix(0.17, 0.06, p.y / max(len, 0.01)); // wide where the claw bit in, thin where it lifted
		float dx = abs(p.x - x0);
		cut = max(cut, (1.0 - smoothstep(w * 0.45, w, dx)) * along);
		lip = max(lip, (1.0 - smoothstep(w, w * 2.4, dx)) * along);
	}
	// a heaped lip of dirt at the far end of each furrow
	float heap = exp(-pow((p.y - drawn * 0.92) / 0.08, 2.0)) * (1.0 - smoothstep(0.0, 0.9, abs(p.x))) * 0.5;
	float a_lip = max(lip * (1.0 - cut), heap) * 0.5 * fade;
	float a_cut = cut * 0.7 * fade;
	vec3 col = mix(vec3(0.62, 0.56, 0.46), vec3(0.13, 0.11, 0.09), a_cut / max(a_cut + a_lip, 0.001));
	ALBEDO = col;
	ALPHA = clamp(max(a_cut, a_lip), 0.0, 1.0);
}
