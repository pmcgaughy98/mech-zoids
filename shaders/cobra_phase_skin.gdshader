shader_type spatial;
// Hood Gaze, an enemy held out of phase (cobra effects lane, 2026-11-14, phase pass). The kit's power is making solid
// matter go soft, so a stunned enemy does not turn to stone: it goes soft and drained of its colour into the gaze's
// gold, its surface wobbles, the picture of it wavers (the scene under the copy is sampled shifted), a gold rim and
// bands sliding up run over it, and a faint double of it (echo 1, offset by echo_off in world metres) drifts beside
// it, see-through. A slowed enemy wears it to the ankles only (fill_y), where its feet are in the soft ground.
// Worn by copies of the enemy's meshes, pushed out a centimetre; the enemy's own materials and material_overlay are
// never touched. blend_mix; above HDR 1.05 only on the snap as it lands and as it snaps back solid.
render_mode unshaded, blend_mix, cull_back, depth_draw_never, shadows_disabled, fog_disabled;

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform float push = 0.01;
uniform float inv_scale = 1.0; // world metres to the mesh's own units
uniform float fill_y = 100.0;
uniform float amount = 0.0;
uniform float snap = 0.0;
uniform float age = 0.0;
uniform float wobble = 0.0; // metres
uniform float echo = 0.0;
uniform vec3 echo_off = vec3(0.0);
uniform float seed = 0.0;
uniform vec3 hot_col : source_color = vec3(1.0, 0.98, 0.80);
uniform vec3 warm_col : source_color = vec3(0.92, 0.84, 0.18);

varying vec3 wp;

void vertex() {
	vec3 w0 = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float wv = sin(w0.y * 11.0 - age * 15.0 + w0.x * 4.0 + seed) * 0.6 + sin(w0.z * 9.0 + age * 11.0) * 0.4;
	VERTEX += NORMAL * (push + wobble * wv * inv_scale);
	if (echo > 0.5) {
		VERTEX += (inverse(MODEL_MATRIX) * vec4(echo_off, 0.0)).xyz;
	}
	wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float under = fill_y - wp.y;
	if (under < 0.0) {
		discard;
	}
	float fres = 1.0 - abs(dot(normalize(NORMAL), normalize(VIEW)));
	fres = fres * fres;
	float band = fract(wp.y * 5.0 - age * 2.2 + seed);
	float bars = smoothstep(0.0, 0.08, band) * (1.0 - smoothstep(0.12, 0.3, band));
	float line = 1.0 - smoothstep(0.0, 0.05, under);
	vec2 off = vec2(sin(wp.y * 18.0 - age * 14.0), cos(wp.x * 15.0 + age * 11.0)) * 0.006 * (0.5 + wobble * 20.0);
	vec3 bg = texture(screen_tex, SCREEN_UV + off).rgb;
	vec3 g = mix(warm_col, hot_col, clamp(fres * 0.5 + snap * 0.5, 0.0, 1.0));
	float lum = dot(bg, vec3(0.3, 0.59, 0.11));
	vec3 drained = mix(bg, g * (0.3 + lum * 1.1), 0.6);
	vec3 col = drained + g * (fres * 0.9 + bars * 0.45 + line * 0.6) * (1.0 + snap * 1.6);
	ALBEDO = col;
	ALPHA = clamp(amount * (echo > 0.5 ? 0.55 : 0.88), 0.0, 1.0);
}
