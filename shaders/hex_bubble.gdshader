shader_type spatial;
// The hex shield as a cartoon ship shield (Claude, 2026-11-09, Preston: "like a layer around the model like how ship
// shields are in cartoons, with the hex pattern on it"). A smooth bubble that follows the body's shape at a distance:
// one rounded capsule per bone, melted together (smooth union) and pushed out by `offset`. It is drawn by marching a
// ray against that shape inside a box that covers the machine, so it bends with every pose. Clear in the middle,
// glowing at the edge, hex cells laid over it; locks on from the feet up, flashes on hits, fades at the end.
render_mode unshaded, cull_front, depth_draw_never, shadows_disabled, blend_mix;

const int MAX_SEG = 40;
uniform vec4 seg_a[40]; // xyz: bone start (world), w: radius
uniform vec4 seg_b[40]; // xyz: bone end (world)
uniform int seg_n = 0;
uniform float offset = 0.16;   // the gap between the body and the shield, metres
uniform float melt = 0.22;     // how much the capsules blend into one smooth shape
uniform vec3 origin = vec3(0.0); // the machine's position, so the cells ride with it
uniform float cell = 0.20;
uniform float fade : hint_range(0.0, 1.0) = 1.0;
uniform float flash : hint_range(0.0, 1.0) = 0.0;
uniform float rise : hint_range(0.0, 1.0) = 1.0;
uniform float pulse : hint_range(0.0, 1.0) = 0.0;
uniform float calm : hint_range(0.0, 1.0) = 0.0; // game feel limits (2026-11-09): 0 = full cells (lock-on), 1 = cells at the rim only
uniform vec3 hit_pos = vec3(0.0);   // where the last absorbed hit landed
uniform float hit_k : hint_range(0.0, 1.0) = 0.0; // its local ripple, 0.12 s
uniform float y_min = 0.0;
uniform float y_max = 2.0;
uniform vec3 plate : source_color = vec3(0.07, 0.24, 0.12);
uniform vec3 core : source_color = vec3(0.50, 1.0, 0.30);
uniform vec3 trim : source_color = vec3(0.95, 0.52, 0.14);
uniform float steps = 10.0;

varying vec3 wpos;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

float capsule(vec3 p, vec3 a, vec3 b, float r) {
	vec3 pa = p - a, ba = b - a;
	float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-6), 0.0, 1.0);
	return length(pa - ba * h) - r;
}

float smin(float a, float b, float k) {
	float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
	return mix(b, a, h) - k * h * (1.0 - h);
}

float shape(vec3 p) {
	float d = 1e5;
	for (int i = 0; i < MAX_SEG; i++) {
		if (i >= seg_n) break;
		d = smin(d, capsule(p, seg_a[i].xyz, seg_b[i].xyz, seg_a[i].w), melt);
	}
	return d - offset;
}

vec3 shape_normal(vec3 p) {
	vec2 e = vec2(0.01, 0.0);
	return normalize(vec3(shape(p + e.xyy) - shape(p - e.xyy), shape(p + e.yxy) - shape(p - e.yxy), shape(p + e.yyx) - shape(p - e.yyx)));
}

float hexdist(vec2 p) {
	p = abs(p);
	return max(dot(p, vec2(0.5, 0.8660254)), p.x);
}

vec3 hexcell(vec2 p) {
	p = floor(p * steps) / steps;
	vec2 r = vec2(1.0, 1.7320508);
	vec2 a = mod(p, r) - r * 0.5;
	vec2 b = mod(p - r * 0.5, r) - r * 0.5;
	vec2 g = dot(a, a) < dot(b, b) ? a : b;
	vec2 id = floor((p - g) * 2.0 + 0.5);
	return vec3(hexdist(g) * 2.0, id);
}

void fragment() {
	vec3 ro = CAMERA_POSITION_WORLD;
	vec3 rd = normalize(wpos - ro);
	float t = 0.0;
	bool hit = false;
	// start near the box: march from the camera with sphere tracing
	for (int i = 0; i < 72; i++) {
		float d = shape(ro + rd * t);
		if (d < 0.004) { hit = true; break; }
		t += max(d, 0.01);
		if (t > 200.0) break;
	}
	if (!hit) discard;
	vec3 p = ro + rd * t;
	// hidden behind walls and other machines: the hit point's own depth goes through the normal depth test
	vec4 clip = PROJECTION_MATRIX * (VIEW_MATRIX * vec4(p, 1.0));
#if CURRENT_RENDERER == RENDERER_COMPATIBILITY
	DEPTH = clip.z / clip.w * 0.5 + 0.5;
#else
	DEPTH = clip.z / clip.w;
#endif
	vec3 n = shape_normal(p);
	vec3 q = p - origin;
	vec3 an = abs(n);
	vec2 uv = an.x > an.y && an.x > an.z ? q.zy : (an.y > an.z ? q.xz : q.xy);
	vec3 hc = hexcell(uv / cell);
	float d = hc.x;
	float edge = step(0.86, d);
	float ring = step(0.62, d) * step(d, 0.72);
	float rn = fract(sin(dot(hc.yz + floor(an.xy * 3.0), vec2(12.9898, 78.233))) * 43758.5453);
	float lit = step(0.88, fract(rn + floor(TIME * 2.0) * 0.137));
	float h = clamp((p.y - y_min) / max(y_max - y_min, 0.001), 0.0, 1.0);
	float shown = step(h, rise);
	float band = step(abs(h - rise), 0.05) * step(rise, 0.999);
	float wave = step(abs(h - pulse), 0.06) * step(0.001, pulse) * step(pulse, 0.999);
	float rim = 1.0 - abs(dot(n, -rd));
	// Game feel limits: over the body the cells nearly vanish (lines ~7%, fill 2%) so the pose and wind-ups read;
	// where the surface turns away from the camera they show at 45-60%. The glow line at the very edge stays thin.
	float rimmask = smoothstep(0.55, 0.75, rim);
	float local = hit_k * (1.0 - smoothstep(0.15, 0.7, distance(p, hit_pos)));
	float cells = clamp(mix(1.0, mix(0.15, 1.0, rimmask), calm) + local, 0.0, 1.0);
	float line = step(0.93, rim);
	vec3 col = core;
	float al = 0.02;
	col = mix(col, core, ring);
	al = max(al, ring * 0.30 * cells);
	col = mix(col, core * 1.25, lit * (1.0 - edge));
	al = max(al, lit * (1.0 - edge) * 0.30 * cells);
	col = mix(col, trim, edge * (1.0 - rimmask));
	al = max(al, edge * 0.50 * cells);
	col = mix(col, vec3(0.80, 1.0, 0.70), line);
	al = max(al, line * 0.75);
	col = mix(col, vec3(0.90, 1.0, 0.85), local);
	float glow = max(band, wave);
	col = mix(col, vec3(0.88, 1.0, 0.80), glow);
	al = max(al, glow * 0.85);
	col = mix(col, vec3(0.86, 1.0, 0.92), flash);
	ALBEDO = col;
	ALPHA = clamp(al + flash * 0.45, 0.0, 1.0) * fade * shown;
}
