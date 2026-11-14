shader_type spatial;
// Gorilla chest beat, the pressure ripple on the floor (gorilla effects lane, 2026-11-11). Smooth, not pixel.
// A chest beat is sound, so it reads as a double ripple: a bright leading rim that races out and slows, a fainter
// echo behind it, and a soft fill between that fades first. Timing measured on SMITE 2 (Cabrakan, Geb): the front
// reaches most of its size in the first third of its life, the leading edge is the brightest part and dies last.
// d = 1 at the target radius. Only the rim of a strong beat goes above the bloom threshold (1.05).
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;
uniform float age = 0.0;
uniform float life = 0.5;
uniform float travel = 0.14; // seconds for the front to reach the target radius
uniform float extent = 1.15; // quad half-size in units of the radius
uniform float radius_m = 5.5; // so the rim keeps the same thickness in metres at every size
uniform float strength = 1.0; // 0.3 a soft drum, 1.0 a full beat
uniform float seed = 0.0;
uniform vec3 lime = vec3(0.62, 1.0, 0.16);
uniform vec3 edge = vec3(0.62, 1.0, 0.16); // the leading rim only; an enemy gorilla's takes its team colour

void fragment() {
	vec2 p = (UV - 0.5) * 2.0 * extent;
	float d = length(p);
	float a = atan(p.y, p.x);
	float t = clamp(age / life, 0.0, 1.0);
	float front = 1.0 - pow(1.0 - clamp(age / travel, 0.0, 1.0), 3.0);
	front = mix(front * 0.92, 1.0, smoothstep(travel, life, age)); // creeps the last part while it fades
	// a slow wobble around the circle so it is a wave, not a compass line
	float wob = 0.5 + 0.5 * sin(a * 3.0 + seed) * sin(a * 7.0 - seed * 1.7);
	float width = mix(0.15, 0.07, t) / radius_m;
	float rim = exp(-pow((d - front) / width, 2.0));
	float echo_r = front * 0.80;
	float echo = exp(-pow((d - echo_r) / (width * 1.4), 2.0)) * 0.35;
	float fill = smoothstep(front - 0.42, front, d) * step(d, front) * 0.16 * (1.0 - smoothstep(0.0, 0.5, t));
	float fade = (1.0 - smoothstep(0.35, 1.0, t)) * smoothstep(0.0, 0.02, age);
	float body = (rim * (0.75 + 0.25 * wob) + echo * (1.0 - smoothstep(0.2, 0.7, t)) + fill) * fade * strength;
	vec3 col = mix(lime, edge, clamp(rim, 0.0, 1.0)) * (0.55 + 1.25 * rim * strength) + vec3(1.0) * rim * rim * 0.2 * strength;
	ALBEDO = col * clamp(body, 0.0, 1.0);
	ALPHA = clamp(body, 0.0, 1.0);
}
