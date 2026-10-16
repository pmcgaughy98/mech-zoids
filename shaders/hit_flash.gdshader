shader_type canvas_item;
// Battle hit flash (Claude, 2026-10-15): blends a machine's pixels toward one colour without touching its alpha, so a
// struck machine blinks white as a solid silhouette (Zoids Legacy and the Pokemon GBA games flash the struck sprite
// to show damage). scripts/battle/vfx.gd sets `flash` in steps; 0 draws the art unchanged.

uniform vec4 flash_color : source_color = vec4(1.0);
uniform float flash : hint_range(0.0, 1.0) = 0.0;

void fragment() {
	COLOR.rgb = mix(COLOR.rgb, flash_color.rgb, flash);
}
