shader_type spatial;
// Pangolin scrap comet (pangolin effects lane, 2026-11-13): the magnet field that holds the scrap shell in its shape.
// A sphere the size of the scrap ball. Only its rim glows (fresnel), with copper field bands sliding toward the poles
// along the roll axis and a faint amber flicker, so the curled pangolin inside stays visible through the plate gaps.
// Additive, below HDR 1.05; never fills the middle of the ball.
render_mode unshaded, cull_back, depth_draw_never, shadows_disabled, blend_add, fog_disabled;

uniform float fade = 1.0;
uniform float time_s = 0.0;
uniform float pulse = 0.0; // a hit or the slam: the field flares for a moment
uniform vec3 copper = vec3(0.95, 0.48, 0.24);
uniform vec3 amber = vec3(1.0, 0.68, 0.28);
varying vec3 local_n;

float sq(float x) { return x * x; }

void vertex() {
	local_n = normalize(VERTEX);
}

void fragment() {
	float facing = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	float rim = sq(1.0 - facing); // 0 in the middle, 1 at the silhouette
	// field bands: lines of latitude around the local x axis (the roll axis), drifting so the field reads as alive
	float lat = asin(clamp(local_n.x, -1.0, 1.0));
	float band = 0.5 + 0.5 * sin(lat * 14.0 - time_s * 5.0);
	band = smoothstep(0.82, 1.0, band);
	float flick = 0.85 + 0.15 * sin(time_s * 23.0 + local_n.y * 7.0);
	vec3 col = copper * (0.3 * rim + 0.6 * band * rim) * flick + amber * pulse * 0.4 * rim;
	col *= fade;
	ALBEDO = col;
	ALPHA = clamp(max(max(col.r, col.g), col.b), 0.0, 1.0);
}
