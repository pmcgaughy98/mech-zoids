shader_type spatial;
// Kangaroo boxing ring, the wall (kangaroo effects lane, 2026-11-11). An open cylinder at the ring's radius.
// Structure from SMITE 2's Ring of Spears (docs/reference/kangaroo-fx-synthesis-2026-11-11.md): segments that come up
// at full radius, a bright base line and a bright top, a soft translucent sheet between. Ours swaps the spears for a
// boxing ring: eight posts and three ropes that sag between them. The ropes light with the rhythm stacks (0 to 3).
// Only the rope and post cores go over HDR 1.05; the sheet stays well under so the mechs inside stay readable.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled, blend_add, fog_disabled;
uniform vec3 mint = vec3(0.32, 1.0, 0.78);
uniform float rise = 1.0;      // 0 to 1: how far the wall has come up
uniform float fade = 1.0;
uniform float posts = 8.0;
uniform float lit = 0.0;       // ropes lit by the rhythm passive
uniform float pulse = 0.0;     // 1 on the cast and on each new stack, decays
uniform float beat = 0.0;      // title bout: rises to 1 as the next beat window opens, so the player can see the beat
uniform float snap = 0.0;      // title bout: 0 to 1 after the launch kick; the ropes flash and break away
uniform vec2 hit_dir = vec2(1.0, 0.0); // flat direction from the centre to where the ringed enemy hit the wall
uniform float hit_k = 0.0;     // 1 on contact, decays
uniform float height_m = 1.1;
uniform float radius_m = 5.0;
varying vec3 lp;

void vertex() {
	lp = VERTEX;
}

float hash(float n) {
	return fract(sin(n * 12.9898) * 43758.5453);
}

void fragment() {
	float y = 1.0 - UV.y; // CylinderMesh UV.y runs top 0 to bottom 1
	float seg = UV.x * posts;
	float f = fract(seg);
	float sag = sin(3.14159265 * f); // 0 at a post, 1 mid-span
	// each span comes up on its own, a little out of step (Odin's segments do the same)
	float r_seg = clamp(rise * 1.5 - hash(floor(seg) + 3.0) * 0.5, 0.0, 1.0);
	r_seg = 1.0 - pow(1.0 - r_seg, 3.0);
	float top = r_seg * (1.0 - 0.10 * sag);
	float under = 1.0 - smoothstep(top - 0.03, top, y);

	// the sheet: brightest at the base, soft upward, slow bands drifting round
	float sheet = 0.06 + 0.30 * pow(1.0 - y, 2.6);
	sheet *= 0.85 + 0.15 * sin(UV.x * 6.2831853 * 24.0 - TIME * 2.0 + y * 6.0);
	float base_m = y * height_m;
	float base_core = exp(-pow(base_m / 0.035, 2.0));
	float base_glow = exp(-base_m / 0.16) * 0.45;

	// three ropes, sagging between posts, riding up with the span
	float rope_core = 0.0;
	float rope_glow = 0.0;
	for (int i = 0; i < 3; i++) {
		float ry = (0.34 + 0.28 * float(i)) * r_seg - 0.07 * sag * r_seg;
		float d = abs(y - ry) * height_m;
		float on = step(float(i) + 0.5, lit);
		float k = (mix(0.45, 1.0, on) + 0.6 * pulse + 0.7 * beat * beat * beat) * (1.0 - snap) + 4.0 * snap * (1.0 - snap);
		float show = step(ry, top + 0.001) * step(0.05, r_seg);
		rope_core += exp(-pow(d / 0.022, 2.0)) * k * show;
		rope_glow += exp(-d / 0.08) * 0.32 * k * show;
	}

	// posts: slim bright uprights with a cap a little above the top rope
	float span_m = 6.2831853 * radius_m / posts;
	float dp = min(f, 1.0 - f) * span_m;
	float post_top = r_seg * 1.04;
	float post_show = 1.0 - smoothstep(post_top - 0.02, post_top, y);
	float post_core = exp(-pow(dp / 0.035, 2.0)) * post_show;
	float post_glow = exp(-dp / 0.14) * 0.35 * post_show;
	float cap = exp(-pow(dp / 0.06, 2.0)) * exp(-pow((y - post_top) * height_m / 0.05, 2.0)) * step(0.05, r_seg);

	// where the ringed enemy hit the wall: a bright patch with ripples running out from it
	vec2 here = normalize(lp.xz + vec2(1e-5));
	float ang = acos(clamp(dot(here, normalize(hit_dir)), -1.0, 1.0));
	float du = ang * radius_m;
	float ripple = hit_k * exp(-du / 0.7) * (0.55 + 0.45 * sin(du * 9.0 - (1.0 - hit_k) * 22.0));

	float soft = (sheet + base_glow + rope_glow + post_glow) * (1.0 + 0.8 * pulse) + ripple * 0.8;
	float hot = rope_core * 1.6 + post_core * 1.3 + cap * 1.8 + base_core * 1.1 + ripple * 0.6;
	vec3 col = mint * soft + mix(mint, vec3(1.0), 0.55) * hot;
	float m = under * fade;
	ALBEDO = col * m;
	ALPHA = clamp(soft + hot, 0.0, 1.0) * m;
}
