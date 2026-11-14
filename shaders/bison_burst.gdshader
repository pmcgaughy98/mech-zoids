shader_type spatial;
// Small spiky fire burst for the bison: the stack muzzle and the bomb impact (bison effects lane, 2026-11-13).
// A camera-facing quad. Structure from Magma Bomb's impact (SMITE 2, measured at 15 fps): one cell of hot core, one
// cell of a wider spiky star, two cells of glow going out. Small and short: no big white flash.
// Core above HDR 1.05 only in the first half of its life; rays under. Additive, ALPHA written, fog_disabled.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform float age = 0.0;
uniform float life = 0.26;
uniform float seed = 0.0;
uniform float spikes = 9.0;
uniform vec3 hot_col : source_color = vec3(1.0, 0.97, 0.92);
uniform vec3 warm_col : source_color = vec3(0.95, 0.88, 0.74);

float hash1(float n) { return fract(sin(n * 12.9898 + seed) * 43758.5453); }

void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0.0, 0.0, 0.0),
		vec4(0.0, length(MODEL_MATRIX[1].xyz), 0.0, 0.0), vec4(0.0, 0.0, length(MODEL_MATRIX[2].xyz), 0.0),
		vec4(0.0, 0.0, 0.0, 1.0));
}

void fragment() {
	float t = clamp(age / life, 0.0, 1.0);
	vec2 p = UV * 2.0 - 1.0;
	float r = length(p);
	float a = atan(p.y, p.x) / 6.2831853 + 0.5;
	float k = a * spikes;
	float i0 = floor(k);
	float f = fract(k);
	float len = mix(hash1(i0), hash1(mod(i0 + 1.0, spikes)), smoothstep(0.0, 1.0, f));
	float tooth = 1.0 - abs(f - 0.5) * 2.0;
	tooth = tooth * tooth;
	float reach = mix(0.3, 1.0, 1.0 - (1.0 - t) * (1.0 - t));
	float ray_len = reach * (0.45 + 0.55 * len) * mix(0.5, 1.0, tooth);
	float ray = 1.0 - smoothstep(ray_len * 0.5, ray_len, r);
	float core = 1.0 - smoothstep(0.0, mix(0.36, 0.08, t), r);
	float hot = 1.0 - smoothstep(0.0, 0.5, t);
	float fade = 1.0 - smoothstep(0.3, 1.0, t);
	ALBEDO = mix(warm_col * 0.85, hot_col * 1.6, core * hot);
	ALPHA = clamp(max(ray * 0.75, core) * fade, 0.0, 1.0);
}
