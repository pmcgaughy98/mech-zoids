extends Node3D
## Local-only normal cast. Preview and commit share one shield validity rule.
const GREEN=Color(.64,1,.12)
const PALE=Color(.9,1,.73)
const ORANGE=Color(1,.61,.16)
const INVALID=Color(1,.35,.22)
const DARK=Color(.025,.075,.07,.94)
const NAMES={"1":"HEX SHIELD","2":"FAULT LINE","3":"DRIVE / GROUND SLAM","4":"SILVERBACK CAGE"}
var kit: ApeKit
var actor: Node3D
var slot:=""
var hovered: Node3D
var valid:=false
var reason:=""
var consume_click:=false
var point_override: Variant=null
var screen_override: Variant=null
var pulse_target: Node3D
var cast_target: Node3D
var pulse_left:=0.0
var clock:=0.0
var mesh: ImmediateMesh
var surface: MeshInstance3D
var material: StandardMaterial3D
var overlay: Control
var overlay_layer: CanvasLayer
var shield_art: Texture2D
func setup(k: ApeKit,p: Node3D) -> void:
	kit=k;actor=p
	mesh=ImmediateMesh.new();surface=MeshInstance3D.new();surface.mesh=mesh
	surface.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(surface);surface.top_level=true;surface.global_transform=Transform3D.IDENTITY
	material=StandardMaterial3D.new();material.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	material.vertex_color_use_as_albedo=true;material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	material.cull_mode=BaseMaterial3D.CULL_DISABLED
	overlay_layer=CanvasLayer.new();overlay_layer.layer=8;add_child(overlay_layer)
	overlay=load("res://scripts/moba3d/gorilla_targeting_overlay.gd").new();overlay.targeting=self
	overlay.mouse_filter=Control.MOUSE_FILTER_IGNORE;overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay_layer.add_child(overlay)
	kit.shield_applied.connect(func(t):pulse_target=t;pulse_left=.55;cast_target=null)
	var art:=AtlasTexture.new();art.atlas=load("res://art/fx/gorilla/reactor-atlas-v1.png")
	var cell:=Vector2(art.atlas.get_width()/4.0,art.atlas.get_height()/2.0)
	art.region=Rect2(Vector2(0,cell.y),cell);shield_art=art
func available(s: String) -> bool:
	return actor.alive and actor.stunned<=0 and not actor.has_meta("held_by") and (kit.current=="" or kit._recovering) and actor.slot_ready(s)
func arm(s: String) -> bool:
	if not NAMES.has(s) or not available(s):return false
	slot=s;refresh();return true
func cancel() -> void:
	slot="";hovered=null;valid=false
func blocks_basic() -> bool:return slot!="" or consume_click
func _unhandled_input(event: InputEvent) -> void:
	if slot=="":return
	if event is InputEventKey and event.pressed and event.physical_keycode==KEY_ESCAPE:
		cancel();get_viewport().set_input_as_handled()
	if event is InputEventMouseButton and event.pressed:
		if event.button_index==MOUSE_BUTTON_RIGHT:
			cancel();get_viewport().set_input_as_handled()
		elif event.button_index==MOUSE_BUTTON_LEFT:
			consume_click=true;confirm();get_viewport().set_input_as_handled()
func _process(delta: float) -> void:
	if actor==null:return
	clock+=delta;pulse_left=maxf(0,pulse_left-delta)
	if kit.current!="hex_shield":cast_target=null
	if consume_click and not Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):consume_click=false
	if slot!="":
		if not available(slot):cancel()
		else:refresh()
	_rebuild();overlay.queue_redraw()
func aim() -> Vector3:return point_override if point_override is Vector3 else actor.aim_point()
func direction() -> Vector3:
	var d:=MatchTeams.flat(aim()-actor.global_position)
	return d.normalized() if d.length()>.05 else actor.facing
func shield_candidate() -> Node3D:
	var cam:=get_viewport().get_camera_3d()
	var mouse: Vector2=screen_override if screen_override is Vector2 else (actor.aim_screen_override if actor.aim_screen_override is Vector2 else _aim_screen())
	var best: Node3D=null;var score:=1e9
	for n: Node3D in [actor]+kit.allies():
		if not is_instance_valid(n) or n.get("alive")==false:continue
		var dist:=MatchTeams.flat(n.global_position-aim()).length()
		var value:=dist/1.05
		if cam!=null and point_override==null and not cam.is_position_behind(n.global_position):
			var low:=cam.unproject_position(n.global_position+Vector3.UP*.2)
			var high:=cam.unproject_position(n.global_position+Vector3.UP*_height(n))
			var nearest:=Geometry2D.get_closest_point_to_segment(mouse,low,high)
			value=minf(value,mouse.distance_to(nearest)/28.0)
		if value<=1 and value<score:score=value;best=n
	return actor if best==null else best
func _height(n: Node3D) -> float:
	var b: Variant=n.get("body")
	return b.top_height() if b is MechModel3D else 1.7
func refresh() -> void:
	hovered=null;valid=true;reason=""
	if slot=="1":
		hovered=shield_candidate();valid=kit._shield_target_valid(hovered)
		if not valid:
			reason="OUT OF RANGE" if MatchTeams.flat(hovered.global_position-actor.global_position).length()>kit.shield_range else "LINE BLOCKED"
	elif slot=="2":
		reason="RUPTURE / SLOW FIELD"
func confirm() -> bool:
	if slot=="" or not available(slot):cancel();return false
	refresh()
	if not valid:return false
	var selected:=slot;var recipient:=hovered;var d:=direction()
	cancel();actor.facing=d;actor._aim_hold=actor.aim_face_time
	match selected:
		"1":
			cast_target=recipient
			kit.hex_shield(recipient)
		"2":kit.fault_line(aim())
		"3":kit.bound()
		"4":kit.chest_beat_ult()
	return true
func _ribbon(a: Vector3,b: Vector3,width: float,color: Color) -> void:
	var edge:=Vector3(-(b-a).z,0,(b-a).x).normalized()*width*.5
	for v in [a-edge,a+edge,b+edge,a-edge,b+edge,b-edge]:
		mesh.surface_set_color(color);mesh.surface_add_vertex(v)
func _ring(center: Vector3,radius: float,width: float,color: Color,segments:=96,start:=0.0,span:=TAU,dashed:=false) -> void:
	for i in segments:
		if dashed and i%4==3:continue
		var a:=start+span*i/segments;var b:=start+span*(i+1)/segments
		_ribbon(center+Vector3(sin(a),0,cos(a))*radius,center+Vector3(sin(b),0,cos(b))*radius,width,color)
func _focus(n: Node3D,color: Color,scale_factor:=1.0) -> void:
	var c:=n.global_position+Vector3.UP*.055
	var r: float=maxf(.75,n.radius()+.23)*scale_factor if n.has_method("radius") else .9*scale_factor
	_ring(c,r,.055,color,6)
	_ring(c,r+.12,.022,Color(color,.55),96,0,TAU,true)
	for i in 6:
		var angle:=i*TAU/6;var out:=Vector3(sin(angle),0,cos(angle));var side:=Vector3(out.z,0,-out.x)
		_ribbon(c+out*(r+.34)+side*.09,c+out*(r+.21),.04,color)
		_ribbon(c+out*(r+.34)-side*.09,c+out*(r+.21),.04,color)
func _rebuild() -> void:
	mesh.clear_surfaces()
	if slot=="" and pulse_left<=0 and not is_instance_valid(cast_target):return
	mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLES,material)
	var c:=actor.global_position+Vector3.UP*.045
	if slot=="1":
		_ring(c,kit.shield_range,.028,Color(GREEN,.30),120,0,TAU,true)
		if is_instance_valid(hovered):_focus(hovered,GREEN if valid else INVALID)
	elif slot=="2":
		var end: Vector3=kit.fault.endpoint(aim())+Vector3.UP*.045
		_ring(end,kit.fault.RADIUS,.045,ORANGE)
		_ribbon(c,end,.025,Color(ORANGE,.45))
	elif slot=="3":
		var d:=direction();var right:=Vector3(d.z,0,-d.x);var length:=1.29904+12.0*38.0/120.0
		for side in [-1,1]:_ribbon(c+right*.64*side,c+d*length+right*.64*side,.045,GREEN)
		_ribbon(c+d*length-right*.64,c+d*length+right*.64,.065,PALE)
		for at in [1.4,2.6,3.8]:
			_ribbon(c+d*at-right*.28,c+d*(at+.3),.05,GREEN)
			_ribbon(c+d*at+right*.28,c+d*(at+.3),.05,GREEN)
	elif slot=="4":
		_ring(c,kit.ult_radius,.065,GREEN)
		_ring(c,kit.ult_radius-.15,.018,Color(GREEN,.45),120,0,TAU,true)
		for i in kit.ult_panels:
			var a:=TAU*i/kit.ult_panels;var out:=Vector3(sin(a),0,cos(a))
			_ribbon(c+out*(kit.ult_radius-.27),c+out*(kit.ult_radius+.05),.09,ORANGE)
	if pulse_left>0 and is_instance_valid(pulse_target):_focus(pulse_target,Color(PALE,pulse_left/.55),1+(.55-pulse_left)*.6)
	if is_instance_valid(cast_target):_focus(cast_target,PALE)
	mesh.surface_end()
func _polygon(c: Control,points: PackedVector2Array,fill: Color,edge: Color,width:=2.0) -> void:
	c.draw_colored_polygon(points,fill);var closed:=points.duplicate();closed.append(points[0]);c.draw_polyline(closed,edge,width,true)
func draw_overlay(c: Control) -> void:
	if slot=="" and pulse_left<=0 and not is_instance_valid(cast_target):return
	var cam:=get_viewport().get_camera_3d();var font:=ThemeDB.fallback_font
	if slot!="":
		var size:=get_viewport().get_visible_rect().size;var at:=Vector2(size.x*.5-205,size.y*.80)
		c.draw_style_box(_panel(),Rect2(at,Vector2(410,64)))
		var subtitle: String=reason if reason!="" else ("SELF" if hovered==actor else MatchTeams.unit_name(hovered).to_upper()) if is_instance_valid(hovered) else "MAX PATH / STOPS ON IMPACT" if slot=="3" else "CAGE BOUNDARY" if slot=="4" else "AIM"
		c.draw_string(font,at+Vector2(16,23),slot+"  /  "+NAMES[slot],HORIZONTAL_ALIGNMENT_LEFT,-1,18,PALE)
		c.draw_string(font,at+Vector2(16,47),subtitle+"  /  "+("LMB CAST / " if valid else "")+"RMB CANCEL",HORIZONTAL_ALIGNMENT_LEFT,-1,13,GREEN if valid else INVALID)
	var target: Node3D=hovered if slot in ["1","2"] else cast_target if is_instance_valid(cast_target) else pulse_target if pulse_left>0 else null
	if not is_instance_valid(target) or cam==null or cam.is_position_behind(target.global_position):return
	var top:=cam.unproject_position(target.global_position+Vector3.UP*(_height(target)+.48))
	var col:=ORANGE if slot=="2" else GREEN if valid or slot=="" else INVALID
	var shield:=PackedVector2Array([Vector2(-17,-15),Vector2(17,-15),Vector2(17,4),Vector2(0,20),Vector2(-17,4)]) if slot!="2" else PackedVector2Array([Vector2(-17,-12),Vector2(-8,-19),Vector2(8,-19),Vector2(17,-12),Vector2(17,12),Vector2(0,20),Vector2(-17,12)])
	for i in shield.size():shield[i]+=top
	if slot=="2":_polygon(c,shield,DARK,col,2.5)
	else:c.draw_texture_rect(shield_art,Rect2(top-Vector2(36,36),Vector2(72,72)),false,Color.WHITE if valid or slot=="" else INVALID)
	if slot=="2":
		for x in [-7,0,7]:c.draw_line(top+Vector2(x,-9),top+Vector2(x,4),PALE,3,true)
		c.draw_line(top+Vector2(-9,8),top+Vector2(9,8),col,3,true)
	# Four corner brackets frame the recipient, with dark backing for bright floors.
	var feet2:=cam.unproject_position(target.global_position);var h:=maxf(45,feet2.y-top.y-22);var w:=clampf(h*.55,30,80)
	for x in [-1,1]:
		for y in [0,1]:
			var corner:=Vector2(feet2.x+x*w,top.y+28+h*y)
			var points:=PackedVector2Array([corner+Vector2(-x*13,0),corner,corner+Vector2(0,12 if y==0 else -12)])
			c.draw_polyline(points,Color(.01,.025,.02,.85),5,true);c.draw_polyline(points,col,2.5,true)
func _panel() -> StyleBoxFlat:
	var box:=StyleBoxFlat.new();box.bg_color=DARK;box.border_color=Color(GREEN,.65)
	box.set_border_width_all(1);box.border_width_left=3;box.set_corner_radius_all(5);return box


## The reticle under the camera's mouse look, else the cursor (camera lane, 2026-11-13).
func _aim_screen() -> Vector2:
	var cam := get_viewport().get_camera_3d()
	return cam.call("aim_screen") if cam != null and cam.has_method("aim_screen") else get_viewport().get_mouse_position()
