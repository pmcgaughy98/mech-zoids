shader_type spatial;
// The hippo's poisoned read (hippo effects lane, 2026-11-12). An open cylinder around an enemy standing in a toxic
// puddle or the Toxic Flood lake: violet fumes streaming up off the body, thickest low and at the silhouette, gone by
// the top. `pulse` lifts it for a moment on each damage tick. Toxic purple, never red (red marks enemies). Every
// colour stays under 1.0 so nothing blooms: it reads as gas, not light.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;

uniform float strength = 1.0; // fade in and out
uniform float pulse = 0.0; // 1 on a tick, decays
uniform float seed = 0.0;
uniform vec3 deep : source_color = vec3(0.24, 0.07, 0.34);
uniform vec3 liquid : source_color = vec3(0.56, 0.24, 0.72);
uniform vec3 shine : source_color = vec3(0.80, 0.56, 0.95);

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7)) + seed) * 43758.5453); }
float noise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

void fragment() {
	float h = 1.0 - UV.y; // 0 at the feet, 1 at the top
	float ang = UV.x;
	float t = TIME + seed;
	// wrap-safe streams: two noise layers, both rising
	float n1 = noise(vec2(ang * 9.0, h * 2.6 - t * 1.6));
	float n2 = noise(vec2(ang * 19.0 + 7.0, h * 5.0 - t * 2.4));
	float streak = smoothstep(0.42, 0.82, n1 * 0.65 + n2 * 0.35);
	float fall = smoothstep(0.0, 0.1, h) * (1.0 - smoothstep(0.3, 1.0, h));
	float facing = abs(dot(NORMAL, VIEW));
	float rim = 1.0 - facing;
	float a = fall * (0.18 + 0.82 * streak) * (0.3 + 0.7 * rim);
	a *= 0.75 + 0.45 * pulse;
	vec3 col = mix(deep, liquid, streak) + shine * pulse * streak * 0.35;
	ALBEDO = min(col, vec3(0.98));
	ALPHA = clamp(a * strength, 0.0, 0.8);
}
