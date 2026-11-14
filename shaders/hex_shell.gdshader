shader_type spatial;
// The gorilla's hex shell (Claude, 2026-11-04; look pass 2026-11-09): the hex shield and the hex dome.
// Look pass: the shell reads as the gorilla's forearm plates, not a plain bubble. Cells are drawn here: dark green
// plate fill, an orange trim line round each cell, a lime ring inside it, and a few lit cells that glow and twinkle
// like the chest core. It builds up from the ground (rise); a warding dome breathes and sends a heal pulse up the
// shell (pulse). Unshaded, both faces, pixel-stepped to keep the game's pixel feel.
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled;

uniform sampler2D hex_tex : source_color, filter_nearest, repeat_enable; // the old tile, no longer sampled
uniform vec2 tiles = vec2(14.0, 12.0); // set from the radius, about one cell per half metre
uniform float fade : hint_range(0.0, 1.0) = 1.0;
uniform float flash : hint_range(0.0, 1.0) = 0.0;
uniform float drift = 0.0;
uniform float rise : hint_range(0.0, 1.0) = 1.0;
uniform float pulse : hint_range(0.0, 1.0) = 0.0;
uniform float ward : hint_range(0.0, 1.0) = 0.0;
uniform float calm : hint_range(0.0, 1.0) = 0.0; // game feel limits (2026-11-09), as the bubble: 0 full cells, 1 cells at the rim only
uniform vec3 hit_pos = vec3(0.0); // world point of the last absorbed hit
uniform float hit_k : hint_range(0.0, 1.0) = 0.0;
uniform float panel_n = 0.0; // the ult wall's panels round the dome (0: one whole wall)
uniform float panel_hp[16];  // each panel's health 0..1; a broken one (0) is a gap
uniform float y_min = -1.0;
uniform float y_max = 1.0;
uniform vec3 plate : source_color = vec3(0.07, 0.24, 0.12);
uniform vec3 core : source_color = vec3(0.50, 1.0, 0.30);
uniform vec3 trim : source_color = vec3(0.95, 0.52, 0.14);
uniform float steps = 24.0; // pixel steps per cell
uniform float density = 1.0; // a big dome is drawn lighter so a team fight stays readable through it

varying float ly;
varying vec3 wp;
varying vec3 centre;
varying float ny;

void vertex() {
	ly = VERTEX.y;
	wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	centre = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	ny = NORMAL.y;
}

float hexdist(vec2 p) {
	p = abs(p);
	return max(dot(p, vec2(0.5, 0.8660254)), p.x);
}

void fragment() {
	vec2 p = (UV * tiles + vec2(drift, 0.0)) * vec2(1.0, 0.8660254);
	p = floor(p * steps) / steps;
	vec2 r = vec2(1.0, 1.7320508);
	vec2 a = mod(p, r) - r * 0.5;
	vec2 b = mod(p - r * 0.5, r) - r * 0.5;
	vec2 g = dot(a, a) < dot(b, b) ? a : b;
	vec2 id = floor((p - g) * 2.0 + 0.5);
	float d = hexdist(g) * 2.0; // 0 at the cell centre, about 1 at its edge
	float edge = step(0.88, d);
	float ring = step(0.64, d) * step(d, 0.75);
	float n = fract(sin(dot(id, vec2(12.9898, 78.233))) * 43758.5453);
	float lit = step(0.86, fract(n + floor(TIME * 2.0) * 0.137));
	float h = clamp((ly - y_min) / max(y_max - y_min, 0.001), 0.0, 1.0);
	float shown = step(h, rise);
	float hw = 0.10 / max(y_max - y_min, 0.001); // the bright lines are 10 cm wide whatever the size
	float band = step(abs(h - rise), hw) * step(rise, 0.999);
	float wave = step(abs(h - pulse), hw) * step(0.001, pulse) * step(pulse, 0.999);
	float ground = step(h, hw * 0.8) * step(abs(y_min), 0.001); // the dome's foot only
	float rim = 1.0 - abs(dot(NORMAL, VIEW));
	rim = floor(rim * 4.0) / 4.0;
	float breathe = ward * (0.5 + 0.5 * sin(TIME * 4.0));
	// rim-only after the lock-on, like the bubble: clear where you look through it, cells where it turns away
	float rimmask = step(0.5, rim);
	float local = hit_k * (1.0 - smoothstep(0.3, 1.6, distance(wp, hit_pos)));
	float cells = clamp(mix(1.0, mix(0.15, 1.0, rimmask), calm) + local, 0.0, 1.0);
	vec3 col = plate;
	float al = mix(0.16 + 0.3 * rim, 0.02 + 0.5 * step(0.75, rim), calm);
	col = mix(col, core, ring * 0.9);
	al = max(al, ring * 0.55 * cells);
	col = mix(col, core * 1.2, lit * (1.0 - edge));
	al = max(al, lit * (1.0 - edge) * (0.45 + 0.25 * breathe) * cells);
	col = mix(col, trim, edge);
	al = max(al, edge * (0.7 + 0.25 * rim) * cells);
	col = mix(col, vec3(0.90, 1.0, 0.85), local);
	if (panel_n > 0.5) {  // panels: a seam between them, a worn one goes orange, a broken one is a gap
		float pa = (atan(wp.z - centre.z, wp.x - centre.x) + PI) / TAU * panel_n;
		int pidx = clamp(int(floor(pa)), 0, int(panel_n) - 1);
		float php = panel_hp[pidx];
		if (php <= 0.0) discard;
		float seam = step(0.485, abs(fract(pa) - 0.5));  // about 3% of a panel, ~10 cm at 5.5 m
		col = mix(col, trim, max(seam, (1.0 - php) * 0.6));
		al = max(al, seam * 0.55 + (1.0 - php) * 0.25);
	}
	float glow = max(band, max(wave, ground));
	col = mix(col, vec3(0.85, 1.0, 0.75), glow);
	al = max(al, glow * 0.9);
	al += breathe * 0.04 * (1.0 - edge) * cells;
	al *= mix(density, 1.0, max(glow, edge * 0.5));
	col = mix(col, vec3(0.84, 1.0, 0.9), flash);
	ALBEDO = col;
	float cap = step(ny, -0.95) * step(abs(y_min), 0.001); // the hemisphere's floor disc: not drawn
	float near = mix(0.12, 1.0, smoothstep(1.5, 6.0, length(VERTEX))); // wall near the camera fades (inside a big dome)
	ALPHA = clamp(al + flash * 0.4, 0.0, 1.0) * fade * shown * (1.0 - cap) * near;
}
