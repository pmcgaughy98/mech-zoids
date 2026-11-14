shader_type spatial;
// Rhino horn swipe (rhino effects lane, 2026-11-12). A crescent slash on a quad laid in the swing's plane: the head
// races from angle a0 to a1 in about 0.07 s, white-hot at the head and mint toward the tail, then the whole arc thins
// and fades by 0.22 s. Structure from MOBA melee basics (a short bright arc on contact, gone before the next swing).
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled, shadows_disabled, blend_add, fog_disabled; // drawn over the body: the play camera sits behind the rhino, so a depth-tested slash hides behind it

uniform float age = 0.0;
uniform float a0 = 0.0; // degrees, where the swing starts (0 = quad +X, 90 = quad +Y)
uniform float a1 = 150.0; // degrees, where it ends; may be less than a0 for a reversed swing
uniform float strength = 1.0;
uniform vec3 mint = vec3(0.32, 1.0, 0.78);

float wrap180(float x) { return mod(x + 180.0, 360.0) - 180.0; }

void fragment() {
	vec2 p = vec2(UV.x * 2.0 - 1.0, 1.0 - UV.y * 2.0);
	float r = length(p);
	float a = degrees(atan(p.y, p.x));
	float span = a1 - a0;
	float s = wrap180(a - a0) / span; // 0 at the start of the swing, 1 at its end
	float head = 1.0 - pow(1.0 - clamp(age / 0.07, 0.0, 1.0), 2.0);
	float fade = 1.0 - smoothstep(0.07, 0.22, age);
	float in_arc = step(0.0, s) * (1.0 - smoothstep(head - 0.02, head, s));
	float tail = clamp(s / max(head, 0.001), 0.0, 1.0); // 0 at the tail, 1 at the head
	float w = mix(0.02, 0.11, tail) * mix(1.0, 0.5, smoothstep(0.07, 0.22, age));
	float band = exp(-pow((r - 0.78) / w, 2.0));
	float glow = exp(-pow((r - 0.74) / (w * 3.0), 2.0)) * 0.35; // a soft inner wash so the slash reads as a sweep
	float v = (band + glow) * in_arc * pow(tail, 1.5) * fade * strength;
	vec3 col = mix(mint, vec3(1.0), smoothstep(0.6, 1.0, tail) * band) * (0.9 + 1.0 * band * tail);
	ALBEDO = col * v;
	ALPHA = clamp(v, 0.0, 1.0);
}
