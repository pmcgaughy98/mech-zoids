shader_type spatial;
// Hippo Vent, the spray itself (hippo effects lane, 2026-11-11). On an open cone mesh laid along the aim, narrow end
// at the jaws. Preston: "purple liquid ... poisonous or toxic", so a violet liquid stream (blend_mix, so it can be
// dark and wet) breaking into filaments, with a small glowing throat and filament highlights above HDR 1.05 for the
// toxic sheen. Soft at the silhouette; thins toward the far end.
// UV.y on Godot's CylinderMesh runs 0 at the top ring (the jaws) to 1 at the bottom ring (the far end).
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_mix, fog_disabled;

uniform float age = 0.0;
uniform float fade = 1.0;
uniform float pulse = 0.0;
uniform float seed = 0.0;
uniform vec3 liquid : source_color = vec3(0.30, 0.07, 0.46);
uniform vec3 shine : source_color = vec3(0.78, 0.36, 1.0);
uniform vec3 hot : source_color = vec3(1.0, 0.82, 1.0);

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7)) + seed) * 43758.5453); }
float noise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

void fragment() {
	float along = UV.y;
	float facing = abs(dot(normalize(NORMAL), normalize(VIEW)));
	float soft = smoothstep(0.05, 0.7, facing);
	// filaments: stretched along the stream, scrolling outward fast
	float n = noise(vec2(UV.x * 18.0, along * 3.0 - age * 10.0)) * 0.6 + noise(vec2(UV.x * 41.0, along * 7.0 - age * 16.0)) * 0.4;
	float fil = smoothstep(0.42, 0.85, n);
	// the stream is solid near the jaws and breaks up farther out
	float breakup = mix(0.85, 0.15, smoothstep(0.1, 0.9, along));
	float body = max(fil, breakup * 0.8);
	float len_fade = (1.0 - smoothstep(0.55, 1.0, along)) * smoothstep(0.0, 0.05, along);
	float throat = exp(-along / 0.07);
	float band = exp(-pow((along - (1.0 - pulse)) / 0.12, 2.0)) * pulse;
	vec3 col = mix(liquid, shine, 0.55 * fil) + shine * fil * smoothstep(0.75, 1.0, n) * 0.5 + hot * (throat * 0.8 + band * 0.45);
	float a = (0.25 + 0.6 * body + throat * 0.3 + band * 0.3) * soft * len_fade * fade;
	ALBEDO = col;
	ALPHA = clamp(a, 0.0, 0.9);
}
