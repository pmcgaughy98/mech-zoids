shader_type spatial;
// Kangaroo afterimage (kangaroo effects lane, 2026-11-12). Preston: faded copies trailing a fighter's moves, as boxing
// anime and speedsters do. One frozen copy of the pose: a bright rim where the surface turns away, a faint fill
// inside, the whole thing fading. Stays under HDR 1.05 so the copies never bloom over the real machine.
// blend_mix, not add (2026-11-12 take 2): added light only drew thin wisps on the bright floor; a see-through
// filled copy reads as the anime afterimage.
render_mode unshaded, blend_mix, cull_back, depth_draw_never, shadows_disabled, fog_disabled;
uniform vec3 tint : source_color = vec3(0.32, 1.0, 0.78);
uniform float fade = 1.0;

void fragment() {
	float facing = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	float rim = pow(1.0 - facing, 2.2);
	ALBEDO = min(tint * (0.7 + 0.45 * rim), vec3(1.0));
	ALPHA = clamp((0.32 + 0.55 * rim) * fade, 0.0, 1.0);
}
