// The wall fade cut, shared by everything that stands up: walls, rocks, cliffs, towers (wall_fade.gdshader) and
// bushes and banners (sprite_fade.gdshader). Map design lane, 2026-11-04.
// It dithers away pixels inside a cone from the chase camera to the player's machine, so nothing standing between
// them hides the machine. Use it in fragment(), outside the sun's shadow pass, so shadows stay whole:
//   if (PROJECTION_MATRIX[3][3] < 0.5 && fade_cut(world_pos, INV_VIEW_MATRIX[3].xyz, FRAGCOORD.xy)) { discard; }

// The player's feet, published each frame by scripts/moba3d/machine_test_player.gd (game feel lane) and declared in
// project.godot [shader_globals]. Its default, (0, -1000, 0), fades nothing.
global uniform vec3 machine_pos;
// 1 while a ray from the camera to the machine's body hits a wall, 0 in plain view, eased over 0.15 s. Published
// by machine_test_player.gd (game feel lane) and declared in project.godot with default 1.0, so a scene with no
// player keeps the plain cut. It closes the cut while the machine is in view, so a wall curving past the camera
// beside the machine never thins out for nothing.
global uniform float machine_hidden;

uniform float body_height = 1.0; // the fade aims at the machine's body, this far above its feet
uniform float fade_radius = 1.6; // metres round the body; the cut narrows toward the camera, so on screen it
                                 // is the same size wherever the wall stands
uniform float fade_floor = 0.25; // share of wall pixels kept in the middle of the cut
uniform float body_depth = 0.6; // metres in front of the body point (along the view) where the cut stops, so a wall
                                // pressed against the far side of the machine never thins out
uniform float body_ramp = 0.4; // the cut eases in over this many metres in front of that

float bayer4(vec2 p) {
	int x = int(mod(p.x, 4.0));
	int y = int(mod(p.y, 4.0));
	float m[16] = float[16](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0, 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);
	return (m[y * 4 + x] + 0.5) / 16.0;
}

bool fade_cut(vec3 world_pos, vec3 cam, vec2 frag) {
	vec3 seg = machine_pos + vec3(0.0, body_height, 0.0) - cam;
	float len = length(seg);
	float t = dot(world_pos - cam, seg) / max(len * len, 0.0001);
	if (t <= 0.0 || t >= 1.0) { // only between the camera and the machine; walls beyond it stay solid
		return false;
	}
	float d = length(world_pos - (cam + seg * t));
	float r = fade_radius * t;
	float keep = mix(fade_floor, 1.0, smoothstep(r * 0.75, r, d));
	// Ease out by distance, not by share of the way: a share eased up to the body itself, so the top of a wall just
	// past the machine (it projects a little short of the body) dithered.
	float front = len - body_depth;
	keep = max(keep, smoothstep(front - body_ramp, front, t * len));
	keep = mix(1.0, keep, clamp(machine_hidden, 0.0, 1.0)); // in plain view the cut closes
	return keep < bayer4(frag);
}
