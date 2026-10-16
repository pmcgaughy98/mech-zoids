// Banded 2D light for normal-mapped pixel sprites (Claude, 2026-10-14; reports/Lit pixel sprites in Godot.md).
// The normal map comes from Blender's check_normal+y matcap, pixelized with the sprite (tools/art/pixelize_render.py);
// this rounds each light's N.L into a few hard steps so lit pixel art stays pixel art instead of a smooth gradient.
// LIGHT.a is written as 1.0 because the engine also folds a directional light's energy into the blend (read in the
// Forward+ source; checked here by tools/debug/lit_capture.gd's energy test on the Compatibility renderer).
shader_type canvas_item;

uniform float bands : hint_range(1.0, 8.0, 1.0) = 3.0;

void light() {
	float ndl = max(dot(NORMAL, LIGHT_DIRECTION), 0.0);
	float falloff = LIGHT_IS_DIRECTIONAL ? 1.0 : LIGHT_COLOR.a;   // a point light's texture alpha
	float i = ndl * falloff * LIGHT_ENERGY;
	i = floor(i * bands + 0.5) / bands;
	LIGHT = vec4(LIGHT_COLOR.rgb * COLOR.rgb * i, 1.0);
}
