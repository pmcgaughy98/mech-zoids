shader_type spatial;
// Hippo Lockjaw, the hold read on the victim (hippo effects lane, 2026-11-12). On a TorusMesh around the held enemy at
// the jaws. SMITE puts the read of a hold or stun on the victim, not on the caster (rhino and hippo studies). A violet
// pressure band, hot where it faces the camera, pulsing like a hydraulic clamp; snaps shut on capture, bursts on slam.
// Additive, writes ALPHA, fog_disabled (look lane rule). Only the pulse peaks go above HDR 1.05.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;

uniform float age = 0.0;
uniform float fade = 1.0;
uniform float seed = 0.0;
uniform vec3 shine : source_color = vec3(0.78, 0.36, 1.0);
uniform vec3 hot : source_color = vec3(1.0, 0.82, 1.0);

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7)) + seed) * 43758.5453); }
float noise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

void fragment() {
	float facing = abs(dot(normalize(NORMAL), normalize(VIEW)));
	float beat = 0.5 + 0.5 * cos(age * 14.0);
	// pressure ripples running round the band
	float n = noise(vec2(UV.x * 24.0 - age * 6.0, UV.y * 4.0));
	float body = 0.35 + 0.45 * smoothstep(0.35, 0.9, n);
	// first take read near white over the pale minion: less hot term, so it stays violet with pulsing peaks
	vec3 col = shine * (0.65 + 0.45 * body) + hot * pow(facing, 4.0) * (0.12 + 0.3 * beat);
	float a = (body * 0.5 + pow(facing, 2.0) * 0.2) * fade;
	ALBEDO = col;
	ALPHA = clamp(a, 0.0, 1.0);
}
