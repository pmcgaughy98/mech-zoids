shader_type spatial;
// Mech look v2 (2026-11-09, look lane): inverted-hull outline, constant width on screen.
// Used for the team read (enemy red), not on every mech: SMITE and Paragon draw no ink lines on characters.
// v2: pushes along a smoothed normal (CUSTOM0, baked by mech_look.gd in the vertex's own normal/tangent frame, so it
// follows skinning). Plain NORMAL split at hard plate edges and left gaps in v1.
render_mode unshaded, cull_front, shadows_disabled;
uniform vec4 outline_color : source_color = vec4(0.95, 0.12, 0.10, 1.0);
uniform float width : hint_range(0.0, 0.01) = 0.0034;  // fraction of view distance; 0.0022 was about 1 px at 1280x720 and broke into dots
void vertex() {
	vec3 n = normalize(NORMAL);
	if (dot(CUSTOM0.xyz, CUSTOM0.xyz) > 0.25) {
		n = normalize(CUSTOM0.x * TANGENT + CUSTOM0.y * BINORMAL + CUSTOM0.z * NORMAL);
	}
	float d = max(0.5, -(MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).z);
	VERTEX += n * width * d;
}
void fragment() {
	ALBEDO = outline_color.rgb;
}
