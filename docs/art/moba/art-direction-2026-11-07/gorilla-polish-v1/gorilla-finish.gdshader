
shader_type spatial;
render_mode diffuse_toon,specular_schlick_ggx,cull_disabled;
uniform sampler2D base_map: source_color,filter_linear_mipmap_anisotropic;
uniform sampler2D normal_map: hint_normal,filter_linear_mipmap_anisotropic;
uniform sampler2D orm_map: filter_linear_mipmap_anisotropic;
uniform bool graphic = false;
uniform bool refined = true;
void fragment(){
 vec3 c=texture(base_map,UV).rgb;
 vec3 orm=texture(orm_map,UV).rgb;
 // Color masks are provisional. They are not authored material IDs.
 float coat=smoothstep(1.10,1.55,c.g/max(c.r,0.004))*smoothstep(1.15,1.6,c.b/max(c.r,0.004));
 float power=smoothstep(1.1,1.5,c.g/max(c.r,0.004))*smoothstep(2.0,3.5,c.r/max(c.b,0.004))*smoothstep(0.15,0.4,c.g);
 ALBEDO=mix(c*1.06,c*1.16,coat);
 METALLIC=mix(clamp(orm.b,0.55,0.85),0.15,coat);
 ROUGHNESS=mix(clamp(orm.g,0.32,0.62),0.55,coat);
 NORMAL_MAP=texture(normal_map,UV).rgb;
 NORMAL_MAP_DEPTH=0.55;
 EMISSION=c*power*0.22;
 if(graphic){
   ALBEDO=c*1.20;
   METALLIC=0.08;
   ROUGHNESS=0.75;
   NORMAL_MAP_DEPTH=0.22;
   RIM=0.14;
   RIM_TINT=0.6;
 }
 if(refined){
   float mx=max(c.r,max(c.g,c.b));
   float mn=min(c.r,min(c.g,c.b));
   float neutral=1.0-smoothstep(0.12,0.32,(mx-mn)/max(mx,0.004));
   float steel=neutral*smoothstep(0.05,0.2,mx);
   float mechanism=neutral*(1.0-smoothstep(0.06,0.18,mx));
   ALBEDO=c*mix(1.13,0.72,power);
   ALBEDO*=mix(1.0,0.87,mechanism);
   METALLIC=mix(0.12,0.78,steel);
   METALLIC=mix(METALLIC,0.42,mechanism);
   ROUGHNESS=mix(0.64,0.36,steel);
   ROUGHNESS=mix(ROUGHNESS,0.7,mechanism);
   NORMAL_MAP_DEPTH=0.38;
   EMISSION=c*power*0.12;
   RIM=0.075;
   RIM_TINT=0.55;
 }

}
