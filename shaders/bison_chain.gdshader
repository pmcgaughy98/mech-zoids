shader_type spatial;
// Coupling Chain links (bison effects lane, 2026-11-13). Heavy iron links drawn by a MultiMesh: real 3D links, so the
// chain has height and thickness from every camera, never a flat strip. Per link, INSTANCE_CUSTOM.r = heat 0..1 (a dim
// red-hot glow at rest, the heat pulse running out along it on top). Dark iron, lit and a little metallic; hot links
// glow magma from the rim in. Structure from Ares' Shackles (SMITE 2, measured at 15 fps): a solid dark chain, there
// within one cell, a heat pulse running from the caster to the target on each refire.
// Pulse cores above HDR 1.05; the rest glow stays under.
render_mode cull_back, diffuse_burley, specular_schlick_ggx;

uniform vec3 hot_col : source_color = vec3(1.0, 0.93, 0.70);
uniform vec3 warm_col : source_color = vec3(1.0, 0.36, 0.06);
uniform vec3 iron_col : source_color = vec3(0.10, 0.095, 0.09);
varying float heatv;

void vertex() {
	heatv = INSTANCE_CUSTOM.r;
}

void fragment() {
	float h = clamp(heatv, 0.0, 1.0);
	float rim = 1.0 - abs(dot(normalize(NORMAL), normalize(VIEW)));
	ALBEDO = iron_col;
	METALLIC = 0.55;
	ROUGHNESS = 0.5;
	EMISSION = warm_col * (0.25 + 0.65 * rim) * h + hot_col * 1.5 * h * h * h;
}
