shader_type spatial;
// Pangolin iron ball speed wake (pangolin effects lane, 2026-11-12). A flat quad trailing behind the ball at the
// height of its middle, local +Z forward: two thin streaks off the flanks that stretch with speed, a faint fill between
// them, and a soft copper glow where the ball meets the floor. Only the streak cores near the ball pass 1.05,
// and only at full speed. Additive: writes ALPHA, fog off, so no pale square shows.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;

uniform float speed01 = 0.0; // 0 at the start of the roll, 1 at full speed
uniform float fade = 1.0;
uniform float time_s = 0.0;
uniform float head_frac = 0.12; // where the ball's centre sits along the quad (from the front)
uniform vec3 copper = vec3(0.95, 0.48, 0.24); // Preston 2026-11-12: copper with amber sparks is the pangolin's effect theme
uniform vec3 amber = vec3(1.0, 0.68, 0.28);
varying vec2 lp;
float sq(float x) { return x * x; } // pow(x, 2.0) is undefined for x < 0 in GLSL

void vertex() {
	lp = VERTEX.xz;
}

void fragment() {
	float x = lp.x * 2.0; // -1 to 1 across
	float along = 1.0 - (lp.y + 0.5); // 0 at the front edge, 1 at the tail
	float tail = clamp((along - head_frac) / (1.0 - head_frac), 0.0, 1.0); // 0 at the ball, 1 at the end
	float ahead = 1.0 - smoothstep(0.0, head_frac, along); // in front of the ball's centre
	// two flank streaks, flickering lengthwise so they read as air moving, not a painted band
	float flick = 0.75 + 0.25 * sin(along * 38.0 - time_s * 55.0);
	float sx = abs(abs(x) - 0.62);
	float streak = exp(-sq(sx / (0.05 + 0.05 * tail))) * pow(1.0 - tail, 1.6) * (1.0 - ahead) * flick;
	float core = exp(-sq(sx / 0.02)) * pow(1.0 - tail, 3.0) * (1.0 - ahead);
	float fill = exp(-sq(x / 0.55)) * pow(1.0 - tail, 2.2) * (1.0 - ahead) * 0.10;
	float glow = exp(-sq(length(vec2(x * 0.9, (along - head_frac) * 4.5)) / 0.55)) * 0.18;
	float s = smoothstep(0.0, 1.0, speed01);
	vec3 col = (copper * (fill * 1.4 + glow) + amber * streak * 0.9) * (0.4 + 0.6 * s); // brighter after the first take: faint on the blue floor
	col += vec3(1.0, 0.86, 0.6) * core * 1.4 * s * s; // white-amber thread at full speed only
	col *= fade;
	ALBEDO = col;
	ALPHA = clamp(max(max(col.r, col.g), col.b), 0.0, 1.0);
}
