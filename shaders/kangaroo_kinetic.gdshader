shader_type spatial;
// Kangaroo kinetic discharge (kangaroo effects lane, 2026-11-12). Preston sent kit design's kinetic power to effects:
// the punches, hops and kicks fire stored kinetic force through capacitor gauntlets and charged legs.
// One quad, three looks (mode):
//   0 shock: a pressure ring that bursts outward from the point of release, plain in the quad's own plane, with a
//     white-hot centre for the first instant. Faces along the punch, so from the match camera it reads as a ring
//     of force leaving the glove, not a flat sticker.
//   1 charge: a ring that closes in on the glove and loops, faster and brighter as the stacks fill (gathering).
//   2 core: a camera-facing pin of light at the release point, gone in a few frames.
// Only the core passes HDR 1.05; the rings stay under it. blend_add writes ALPHA and skips fog, per the look lane.
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, fog_disabled;
uniform vec3 tint : source_color = vec3(0.45, 1.0, 0.82);
uniform int mode = 0;
uniform float t = 0.0;      // 0..1 over the piece's life (shock, core); seconds for charge
uniform float charge = 0.0; // 0..1, stacks / rhythm_max
uniform bool billboard = false;
uniform float segs = 4.0;   // charge: arcs in the stack meter (kit.rhythm_max)

void vertex() {
	if (billboard) {
		MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
		MODELVIEW_NORMAL_MATRIX = mat3(MODELVIEW_MATRIX);
	}
}

void fragment() {
	vec2 p = (UV - 0.5) * 2.0;
	float r = length(p);
	vec3 col = vec3(0.0);
	float m = 0.0;
	if (mode == 0) {
		float e = 1.0 - (1.0 - t) * (1.0 - t) * (1.0 - t);
		float grow = mix(0.12, 0.95, e);
		float w = mix(0.10, 0.035, t);
		float d = (r - grow) / w;
		float ring = exp(-d * d);
		float inner = smoothstep(grow, grow * 0.55, r) * (1.0 - t) * 0.25;
		float hot = (1.0 - smoothstep(0.0, 0.22, r)) * max(1.0 - t * 4.0, 0.0);
		float fade = 1.0 - t * t;
		m = clamp(ring * 0.95 + inner, 0.0, 1.0) * fade;
		col = tint * m + vec3(1.0) * hot * 1.6;
		m = clamp(m + hot, 0.0, 1.0);
	} else if (mode == 1) {
		// Take 2 (Preston 2026-11-12, "Yes, bigger charge"): a stack meter round the glove, one arc per stack,
		// so the charge reads at the match camera; inside it the ring still closes in, and the glove itself glows.
		float speed = mix(1.6, 4.0, charge);
		float ph = fract(t * speed);
		float rad = mix(0.78, 0.2, ph);
		float d = (r - rad) / 0.06;
		float ring = exp(-d * d) * ph * (1.0 - ph) * 4.0;
		float a = atan(p.y, p.x);
		float seg = 6.2831853 / segs;
		float u = mod(1.5707963 - a, 6.2831853);
		float idx = floor(u / seg);
		float gap = abs(u - (idx + 0.5) * seg) / (seg * 0.5);
		float arc_on = step(idx + 0.5, charge * segs);
		float dm = (r - 0.86) / 0.05;
		float arc = exp(-dm * dm) * (1.0 - smoothstep(0.72, 0.84, gap));
		float meter = arc * mix(0.14, 1.0, arc_on);
		float glow = (1.0 - smoothstep(0.0, 0.42, r)) * (0.3 + 0.7 * charge);
		float full = step(0.999, charge) * (0.75 + 0.25 * sin(t * 18.0));
		m = clamp(ring * mix(0.3, 0.9, charge) + meter + glow * 0.7, 0.0, 1.0) * step(0.001, charge);
		col = tint * m * 0.95 + vec3(1.0) * glow * full * 0.6;
	} else {
		float k = 1.0 - smoothstep(0.0, 1.0, r);
		m = k * k * (1.0 - t);
		col = mix(tint, vec3(1.0), 0.7) * m * 1.8;
	}
	ALBEDO = col;
	ALPHA = clamp(m, 0.0, 1.0);
}
