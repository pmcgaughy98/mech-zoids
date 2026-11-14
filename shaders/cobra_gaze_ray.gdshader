shader_type spatial;
// Hood Gaze, thin lines (cobra effects lane, 2026-11-13, petrify pass): the primer needles that flick out from the
// eyes during the gather, the three gaze lines from the eyes to the front while it holds, and the lock line to a
// stunned enemy. ImmediateMesh tubes: UV.x runs along the tube, COLOR.r is a phase, COLOR.a the strength. Grain runs
// out along them like stone dust in the light; no tech dashes. Additive.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;
#include "res://shaders/cobra_noise.gdshaderinc"

uniform float age = 0.0;
uniform vec3 hot_col : source_color = vec3(1.0, 0.98, 0.80);
uniform vec3 warm_col : source_color = vec3(0.92, 0.84, 0.18);

void fragment() {
	float s = UV.x;
	float ph = COLOR.r;
	float strength = COLOR.a;
	float fres = 1.0 - abs(dot(normalize(NORMAL), normalize(VIEW)));
	float core = 1.0 - fres;
	float grain = c_vnoise(vec2(s * 26.0 - age * 15.0 + ph * 13.0, ph * 7.0));
	grain = 0.35 + 0.65 * smoothstep(0.2, 0.8, grain);
	float ends = smoothstep(0.0, 0.1, s) * (1.0 - smoothstep(0.72, 1.0, s));
	vec3 col = mix(warm_col, hot_col, core * core * 0.5) * (0.18 + 0.35 * grain) * (0.8 + 0.4 * strength);
	ALBEDO = col * ends * strength;
	ALPHA = clamp(ends * strength * (0.35 + 0.65 * core), 0.0, 1.0);
}
