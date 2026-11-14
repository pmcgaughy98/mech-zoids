shader_type spatial;
// Mech look v1 (2026-11-09, look lane): an additive fresnel rim on the surface material's next_pass.
// Reads the silhouette against the floor at MOBA camera distance. Biased to upward-facing edges, the way a sky
// backlight would land. Not an overlay: material_overlay stays free for the hex shield and hit flash.
render_mode blend_add, depth_draw_never, cull_back, unshaded, shadows_disabled;
uniform vec4 rim_color : source_color = vec4(0.62, 0.80, 1.0, 1.0);
uniform float rim_power : hint_range(0.5, 8.0) = 4.0;
uniform float rim_strength : hint_range(0.0, 4.0) = 0.5;
uniform float top_bias : hint_range(0.0, 1.0) = 0.6;
void fragment() {
	float f = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), rim_power);
	vec3 wn = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	float up = mix(1.0, smoothstep(-0.3, 0.8, wn.y) * 1.4, top_bias);
	ALBEDO = rim_color.rgb * f * rim_strength * up;
}
