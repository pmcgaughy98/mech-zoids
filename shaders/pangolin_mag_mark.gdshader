shader_type spatial;
// Pangolin "magnetised" mark (pangolin effects lane, 2026-11-12). A flat quad under a magnetised enemy: a thin copper
// ring with four amber arc segments circling it like a field. The segments go out one by one as the mark runs down,
// so the ring also says how long is left. On apply it snaps in from wider with a short pulse. Copper and amber,
// Preston's pangolin theme; it moves, so it never reads as a team ring (those are still circles).
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;

uniform float radius_m = 1.1;
uniform float half_m = 1.75; // half the quad's size in metres
uniform float remain = 1.0; // 1 just applied, 0 expired
uniform float snap = 0.0; // 1 on apply or refresh, decays
uniform float fade = 1.0;
uniform float time_s = 0.0;
uniform vec3 copper = vec3(0.95, 0.48, 0.24);
uniform vec3 amber = vec3(1.0, 0.68, 0.28);
varying vec2 lp;
float sq(float x) { return x * x; } // pow(x, 2.0) is undefined for x < 0 in GLSL

void vertex() {
	lp = VERTEX.xz;
}

void fragment() {
	vec2 p = lp * 2.0 * half_m;
	float R = radius_m * (1.0 + 0.6 * snap * snap);
	float r = length(p);
	float ang = atan(p.y, p.x) + time_s * 1.3; // the field turns
	float ring = exp(-sq((r - R) / 0.035)) * 0.9 + exp(-sq((r - R) / 0.14)) * 0.3; // first take too faint
	float inner = exp(-sq((r - R * 0.8) / (R * 0.3))) * 0.12;
	// four arcs just outside the ring, one per quarter of the mark's time
	float seg_r = R + 0.16;
	float q = fract(ang / 6.2832 * 4.0); // 0..1 within each quarter
	float idx = floor(mod(ang / 6.2832 * 4.0, 4.0));
	float lit = step(idx / 4.0, remain - 0.001); // a quarter goes out as each quarter of the time passes
	float along = smoothstep(0.08, 0.2, q) * (1.0 - smoothstep(0.62, 0.75, q));
	float head = smoothstep(0.45, 0.72, q) * along; // brighter toward the leading end, like a spark running
	float arc = exp(-sq((r - seg_r) / 0.055)) * along * lit;
	vec3 col = copper * (ring + inner) + amber * arc * (0.85 + 0.45 * head);
	col += vec3(1.0, 0.86, 0.6) * snap * exp(-sq((r - R) / 0.06)) * 1.2; // apply pulse, the only bloom
	col *= fade;
	ALBEDO = col;
	ALPHA = clamp(max(max(col.r, col.g), col.b), 0.0, 1.0);
}
