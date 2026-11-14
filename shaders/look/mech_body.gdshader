shader_type spatial;
// Mech look v3 (2026-11-09, look lane): the mech body material with the fresnel rim built in, so the rim costs no
// extra draw. Covers exactly what the gorilla and rhino GLB materials use (measured): albedo texture and colour,
// metallic/roughness as scalar times a texture channel (glTF: roughness G, metallic B), emission colour with an
// optional texture, double-sided. mech_look.gd copies those values over from each StandardMaterial3D.
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;
uniform vec4 albedo : source_color = vec4(1.0);
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap, repeat_enable, hint_default_white;
uniform float metallic = 0.0;
uniform float roughness = 1.0;
uniform sampler2D orm_tex : hint_default_white, filter_linear_mipmap, repeat_enable;
uniform float use_orm = 0.0;
uniform vec4 emission : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float emission_energy = 1.0;
uniform sampler2D emission_tex : source_color, hint_default_white, filter_linear_mipmap, repeat_enable;
uniform vec4 rim_color : source_color = vec4(0.92, 0.94, 1.0, 1.0);
uniform float rim_power : hint_range(0.5, 8.0) = 4.0;
uniform float rim_strength : hint_range(0.0, 4.0) = 0.5;
uniform float top_bias : hint_range(0.0, 1.0) = 0.6;
// Per-mech flash materials are copied lazily by mech_look.set_flash(). Avoid exhausting the
// Compatibility renderer's instance-uniform buffer when several articulated mechs are present.
uniform float hit_flash : hint_range(0.0, 1.0) = 0.0;
uniform vec4 flash_color : source_color = vec4(1.0);
// Finish (2026-11-10, folded in from the Codex art-direction gorilla pass "refined D", which Preston picked): masks
// read from the albedo colour, no authored ID map. Painted armour stays matte, light neutral hardware turns to polished
// metal, dark neutral mechanisms go darker and rough, lime power panels are toned down. finish = 0 is the plain v3 look.
// steel_min: only neutral texels brighter than this count as hardware, so grey-armoured mechs don't turn to chrome.
uniform float finish : hint_range(0.0, 1.0) = 1.0;
uniform float steel_min : hint_range(0.0, 1.0) = 0.05;
void fragment() {
	vec4 a = albedo * texture(albedo_tex, UV);
	ALBEDO = a.rgb;
	vec4 orm = texture(orm_tex, UV);
	METALLIC = metallic * mix(1.0, orm.b, use_orm);
	ROUGHNESS = roughness * mix(1.0, orm.g, use_orm);
	SPECULAR = 0.5;
	vec3 e = emission.rgb * emission_energy * texture(emission_tex, UV).rgb;
	if (finish > 0.0) {
		vec3 c = a.rgb;
		float mx = max(c.r, max(c.g, c.b));
		float mn = min(c.r, min(c.g, c.b));
		float neutral = 1.0 - smoothstep(0.12, 0.32, (mx - mn) / max(mx, 0.004));
		float steel = neutral * smoothstep(steel_min, steel_min + 0.15, mx);
		float mech = neutral * (1.0 - smoothstep(0.06, 0.18, mx));
		float power = smoothstep(1.1, 1.5, c.g / max(c.r, 0.004)) * smoothstep(2.0, 3.5, c.r / max(c.b, 0.004)) * smoothstep(0.15, 0.4, c.g);
		vec3 fa = c * mix(1.0, 0.72, power) * mix(1.0, 0.87, mech);
		float fm = mix(mix(0.12, 0.78, steel), 0.42, mech);
		float fr = mix(mix(0.64, 0.36, steel), 0.7, mech);
		ALBEDO = mix(ALBEDO, fa, finish);
		METALLIC = mix(METALLIC, fm, finish);
		ROUGHNESS = mix(ROUGHNESS, fr, finish);
		e += c * power * 0.12 * finish;
	}
	// Rim: same fresnel as the v1/v2 next_pass, now added to emission. Back faces (cull_disabled) get no rim.
	vec3 n = FRONT_FACING ? NORMAL : -NORMAL;
	float f = pow(1.0 - clamp(dot(n, VIEW), 0.0, 1.0), rim_power);
	vec3 wn = normalize((INV_VIEW_MATRIX * vec4(n, 0.0)).xyz);
	float up = mix(1.0, smoothstep(-0.3, 0.8, wn.y) * 1.4, top_bias);
	ALBEDO = mix(ALBEDO, flash_color.rgb, hit_flash);
	EMISSION = mix(e + rim_color.rgb * f * rim_strength * up, flash_color.rgb * 0.8, hit_flash);
}
