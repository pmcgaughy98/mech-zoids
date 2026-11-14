shader_type spatial;
// Pangolin salvage: a stolen armour plate (pangolin effects lane, 2026-11-12). A solid, lit copper plate, so it reads
// as metal and not as a glowing mote. heat lights its edges amber: 1 while it is pulled in and on the snap, then it
// settles to a low glow while it sits on the shell (the stolen armour you can see), fade drops it out at the end.
render_mode cull_back, shadows_disabled;

uniform float heat = 1.0;
uniform float fade = 1.0;
uniform vec3 copper = vec3(0.62, 0.32, 0.17);
uniform vec3 amber = vec3(1.0, 0.68, 0.28);
float sq(float x) { return x * x; } // pow(x, 2.0) is undefined for x < 0 in GLSL

void fragment() {
	float fres = sq(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0));
	ALBEDO = copper * fade;
	METALLIC = 0.75;
	ROUGHNESS = 0.38;
	EMISSION = (copper * 0.12 + amber * (0.12 + 0.75 * fres) * heat) * fade; // first take read as yellow cards, not copper metal
}
