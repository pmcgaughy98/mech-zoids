// Rings painted on the ground: a tower's range, camp spots, side pits, spawn pads. Map design lane, 2026-11-04.
// Lay it on a PlaneMesh centred on the thing, a little bigger than the ring, a hair above the floor. Edges step on
// the shared 50 texels per metre grid, so the ring is pixel art like the rest of the ground.
// A tower ring (show_near > 0) reads game feel's machine_pos: it fades in as the player comes within
// radius + show_near metres, and fills faintly once the player is inside the range. "alert" (0 to 1, set per tower
// with arena_blockout.gd's set_tower_alert) turns it to alert_color while that tower aims at the player.
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;

global uniform vec3 machine_pos;

uniform vec4 color : source_color = vec4(1.0, 1.0, 1.0, 0.85);
uniform vec4 alert_color : source_color = vec4(1.0, 0.18, 0.12, 0.95);
uniform float alert = 0.0;
uniform float radius = 3.0;
uniform float width = 0.16; // eight texels
uniform float dashes = 0.0; // dashes round the ring; 0 for a solid line
uniform float fill = 0.0; // alpha inside the ring
uniform float show_near = 0.0; // metres outside the ring where it starts to show; 0 shows it always
uniform float texels_per_metre = 50.0;

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 c = NODE_POSITION_WORLD.xz;
	vec2 q = (floor(world_pos.xz * texels_per_metre) + 0.5) / texels_per_metre - c;
	float d = length(q);
	float a = 0.0;
	if (abs(d - radius) < width * 0.5) {
		a = 1.0;
		if (dashes > 0.0 && fract(atan(q.y, q.x) / TAU * dashes) > 0.6) {
			a = 0.0;
		}
	} else if (d < radius) {
		a = fill;
	}
	float vis = 1.0;
	if (show_near > 0.0) {
		float md = distance(machine_pos.xz, c);
		vis = 1.0 - smoothstep(radius + show_near * 0.5, radius + show_near, md);
		if (md < radius && d < radius - width * 0.5) {
			a = max(a, fill * 2.0); // the player is inside the range
		}
	}
	vec4 col = mix(color, alert_color, clamp(alert, 0.0, 1.0));
	ALPHA = a * col.a * vis;
	if (ALPHA < 0.01) {
		discard;
	}
	ALBEDO = col.rgb;
}
