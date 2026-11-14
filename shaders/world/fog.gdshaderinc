// Fog of war for the world shaders (ground, walls, props). Map design lane, 2026-11-04.
// Fed by scenes/moba3d/arena_vision.gd: one texel per 1 m cell of the map, white where the viewing team sees. The
// last two grids ease into each other (fog_mix, 0 to 1 over one update), so the edge glides instead of jumping. The
// grid is read at texel centres of the shared 50 per metre pixel grid, so the edge steps in whole pixels, and in three
// levels, like the wall shading. Off (fog_on false) the world draws as before.
uniform bool fog_on = false;
uniform sampler2D fog_prev : filter_linear, repeat_disable, hint_default_white;
uniform sampler2D fog_next : filter_linear, repeat_disable, hint_default_white;
uniform float fog_mix = 1.0;
uniform vec4 fog_rect = vec4(-42.0, -78.0, 84.0, 156.0); // the grid's corner (world x, z) and its size in metres
uniform float fog_dim = 0.42; // how bright the unseen world stays

// 1 where the viewing team sees, 0.5 at the edge, 0 where it doesn't.
float fog_seen(vec3 world) {
	if (!fog_on) {
		return 1.0;
	}
	vec2 q = (floor(world.xz * 50.0) + 0.5) / 50.0;
	vec2 uv = (q - fog_rect.xy) / fog_rect.zw;
	float s = mix(texture(fog_prev, uv).r, texture(fog_next, uv).r, fog_mix);
	return floor(smoothstep(0.2, 0.8, s) * 2.0 + 0.5) * 0.5;
}

// Unseen colour: darker and cooler, about half its colour gone, so the seen world reads as the lit part.
vec3 fog_tint(vec3 c, float seen) {
	float grey = dot(c, vec3(0.3, 0.59, 0.11));
	vec3 unseen = mix(vec3(grey) * vec3(0.78, 0.85, 1.0), c, 0.45) * fog_dim;
	return mix(unseen, c, seen);
}
