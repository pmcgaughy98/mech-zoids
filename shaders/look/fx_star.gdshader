shader_type spatial;
// Look lane 2026-11-11: smooth stun star (replaces the pixel stars). A soft-edged five-point star with a hot centre.
render_mode unshaded, blend_mix, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;
uniform vec3 col : source_color = vec3(1.0, 0.82, 0.25);
uniform float glow = 1.6;
uniform float spin = 0.0;
void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0] * length(MODEL_MATRIX[0].xyz),
		INV_VIEW_MATRIX[1] * length(MODEL_MATRIX[1].xyz), INV_VIEW_MATRIX[2] * length(MODEL_MATRIX[2].xyz), MODEL_MATRIX[3]);
}
// Five-point star signed distance (the standard formula by Inigo Quilez).
float star(vec2 p, float r, float rf) {
	const vec2 k1 = vec2(0.809016994375, -0.587785252292);
	const vec2 k2 = vec2(-0.809016994375, -0.587785252292);
	p.x = abs(p.x);
	p -= 2.0 * max(dot(k1, p), 0.0) * k1;
	p -= 2.0 * max(dot(k2, p), 0.0) * k2;
	p.x = abs(p.x);
	p.y -= r;
	vec2 ba = rf * vec2(-k1.y, k1.x) - vec2(0.0, 1.0);
	float h = clamp(dot(p, ba) / dot(ba, ba), 0.0, r);
	return length(p - ba * h) * sign(p.y * ba.x - p.x * ba.y);
}
void fragment() {
	vec2 p = (UV - 0.5) * 2.0;
	float c = cos(spin);
	float s = sin(spin);
	p = mat2(vec2(c, -s), vec2(s, c)) * p;
	float d = star(p, 0.8, 0.45);
	float w = fwidth(d) * 1.2;
	float body = 1.0 - smoothstep(-w, w, d);
	float halo = (1.0 - smoothstep(0.0, 0.25, d)) * 0.35;
	float hot = 1.0 - smoothstep(0.0, 0.45, length(p));
	ALBEDO = col * mix(1.0, glow, hot) + vec3(0.25) * hot;
	ALPHA = clamp(body + halo * (1.0 - body), 0.0, 1.0);
}
