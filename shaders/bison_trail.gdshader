shader_type spatial;
// The bison's bomb trail (bison effects lane, 2026-11-13). Drawn on a tube the observer rebuilds every frame along the
// bomb's path, so it has real height and width from every camera (never a flat strip). Per vertex: COLOR.r = heat
// (1 at the bomb, falling with age), COLOR.a = opacity. The tube is soft at its silhouette (view facing) with a hot
// core along its middle. Structure from Vulcan's Magma Bomb (SMITE 2, measured at 15 fps): a thick glowing trail on
// the way up that thins and goes in about 4 cells, a thin short one on the way down.
// Core above HDR 1.05, the rest under. Additive, ALPHA written, fog_disabled.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;

uniform vec3 hot_col : source_color = vec3(1.0, 0.97, 0.92);
uniform vec3 warm_col : source_color = vec3(0.95, 0.88, 0.74);
varying float heatv;
varying float av;

void vertex() {
	heatv = COLOR.r;
	av = COLOR.a;
}

void fragment() {
	float facing = abs(dot(normalize(NORMAL), normalize(VIEW)));
	float soft = facing * facing;
	float core = smoothstep(0.8, 1.0, facing) * heatv;
	float flick = 0.85 + 0.15 * sin(UV.x * 31.0 - TIME * 24.0);
	vec3 c = mix(warm_col * 0.85, hot_col * 1.4, core * core);
	ALBEDO = c * flick;
	ALPHA = clamp(soft * av * 0.8, 0.0, 1.0);
}
