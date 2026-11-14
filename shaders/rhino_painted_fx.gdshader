shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never,shadows_disabled;
uniform sampler2D atlas : source_color,filter_linear_mipmap,repeat_disable;
uniform vec2 cell=vec2(0.0);
uniform float opacity : hint_range(0.0,1.0)=0.5;
uniform vec4 tint : source_color=vec4(1.0);
void fragment(){
 vec4 paint=texture(atlas,(UV+cell)/vec2(4.0,2.0));
 float gutter=smoothstep(0.0,0.085,min(min(UV.x,1.0-UV.x),min(UV.y,1.0-UV.y)));
 ALBEDO=paint.rgb*tint.rgb;
 ALPHA=pow(paint.a,1.85)*gutter*opacity*tint.a;
}
