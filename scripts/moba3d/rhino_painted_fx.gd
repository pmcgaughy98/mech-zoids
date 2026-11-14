extends Node3D
## Visual-only observer: existing body events and kit cues remain authoritative.
const IMAGE="res://art/fx/rhino/seismic-atlas-v1.png"
const SHADER=preload("res://shaders/rhino_painted_fx.gdshader")
var actor: Node3D
var kit: RhinoKit
var body: MechModel3D
var texture: Texture2D
var live: Array=[]
var wake: MeshInstance3D
var brace_mark: MeshInstance3D
var brace_face: MeshInstance3D
var toss_direction:=Vector3.FORWARD
var toss_landing:=Vector3.ZERO
var toss_travel:=false
var was_braced:=false
var event_log: Array=[]
var elapsed:=0.0
func setup(k: RhinoKit,p: Node3D) -> void:
 kit=k;actor=p;texture=load(IMAGE)
 wake=piece(2);brace_mark=piece(5);brace_face=piece(4)
 kit.cue.connect(on_cue)
 kit.used.connect(func(slot):
  if slot=="1":toss_direction=actor.facing;toss_travel=false
 )
 bind_body()
func bind_body() -> void:
 var next: Variant=actor.get("body")
 if next==body:return
 if is_instance_valid(body) and body.event.is_connected(on_body_event):body.event.disconnect(on_body_event)
 body=next if next is MechModel3D else null
 if body!=null:body.event.connect(on_body_event)
func piece(index: int) -> MeshInstance3D:
 var node:=MeshInstance3D.new();var plane:=PlaneMesh.new();plane.size=Vector2.ONE;node.mesh=plane
 var mat:=ShaderMaterial.new();mat.shader=SHADER;mat.set_shader_parameter("atlas",texture);mat.set_shader_parameter("cell",Vector2(index%4,int(index/4)))
 node.material_override=mat;node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 add_child(node);node.top_level=true;node.global_transform=Transform3D.IDENTITY;node.visible=false;return node
func place(node: MeshInstance3D,at: Vector3,size: Vector2,alpha: float,normal:=Vector3.UP,yaw:=0.0) -> void:
 node.visible=alpha>.001;node.global_position=at
 node.global_basis=Basis(Quaternion(Vector3.UP,normal.normalized()))*Basis(Vector3.UP,yaw)
 node.scale=Vector3(size.x,1,size.y);node.material_override.set_shader_parameter("opacity",alpha)
func horn() -> Vector3:
 if is_instance_valid(body) and is_instance_valid(body.skeleton):
  for name in ["Bone_008","Bone008"]:
   var i:=body.skeleton.find_bone(name)
   if i>=0:return body.skeleton.to_global(body.skeleton.get_bone_global_pose(i).origin)
 return actor.global_position+actor.facing*1.25+Vector3.UP
func burst(index: int,at: Vector3,size: Vector2,life: float,alpha: float,normal:=Vector3.UP,yaw:=0.0) -> void:
 var node:=piece(index)
 live.append({"node":node,"at":at,"size":size,"life":life,"age":0.0,"alpha":alpha,"normal":normal,"yaw":yaw})
 place(node,at,size,alpha,normal,yaw)
func mark(name: String) -> void:event_log.append({"name":name,"time":elapsed,"clip":body.action if is_instance_valid(body) else ""})
func on_cue(name: String) -> void:
 if not is_instance_valid(actor) or not actor.alive:return
 match name:
  "dash_cast":toss_travel=true;mark("toss_travel")
  "horn_catch":
   toss_travel=false;burst(6,horn(),Vector2(1.25,1.65),.3,.65,actor.facing);mark("toss_catch")
  "toss_land":
   burst(1,toss_landing+Vector3.UP*.06,Vector2.ONE*2,.55,.5);mark("toss_land")
  "jab_hit":
   burst(6,horn(),Vector2.ONE*.8,.18,.6,actor.facing);mark("confirmed_basic_hit")
  "tremor_stomp":
   burst(5,actor.global_position+Vector3.UP*.075,Vector2.ONE*kit.pound_radius*1.8,.35,.38);mark("tremor_stomp")
func on_body_event(clip: String,event: String,_damage: bool) -> void:
 if not is_instance_valid(actor) or not actor.alive:return
 if clip in ["horn_hook","horn_rip","horn_gore"] and event=="hit" and kit.current==clip:
  var right: Vector3=actor.facing.cross(Vector3.UP).normalized()
  burst(0,horn(),Vector2(1.7,1.0),.22,.62,right if clip=="horn_gore" else actor.facing)
  mark("basic_arc")
 if clip=="horn_toss" and event=="release":
  toss_travel=false;toss_landing=actor.global_position-toss_direction*kit.toss_land_behind
 if clip in ["ground_pound","ground_pound_finale"] and event=="slam" and kit.current=="ground_pound":
  var finale:=clip=="ground_pound_finale"
  var radius:=kit.finale_radius if finale else kit.pound_radius
  var center: Vector3=actor.global_position+(actor.facing*.5 if finale else Vector3.ZERO)+Vector3.UP*.07
  burst(7 if finale else 1,center,Vector2.ONE*radius*1.45,.65,.50)
  burst(3,center,Vector2.ONE*radius*1.8,kit.patch_time if finale else kit.tremor_stomps*kit.tremor_interval+kit.tremor_linger,.24)
  mark("finale_slam" if finale else "pound_slam")
func clear_transients() -> void:
 for row in live:
  if is_instance_valid(row.node):row.node.queue_free()
 live.clear();toss_travel=false
 for node in [wake,brace_mark,brace_face]:
  if is_instance_valid(node):node.visible=false
func _process(delta: float) -> void:
 if not is_instance_valid(actor) or not is_instance_valid(kit):return
 elapsed+=delta;bind_body()
 if not actor.alive:clear_transients();was_braced=false;return
 if kit.current!="horn_toss":toss_travel=false
 var travel: bool=kit.current=="stampede" or toss_travel
 wake.visible=false;brace_mark.visible=false;brace_face.visible=false
 if travel:
  place(wake,actor.global_position-actor.facing*.85+Vector3.UP*.07,Vector2(1.45,3.1),.36,Vector3.UP,atan2(-actor.facing.x,-actor.facing.z))
 if kit.braced:
  place(brace_mark,actor.global_position+Vector3.UP*.065,Vector2.ONE*2.1,.25,Vector3.UP,elapsed*.12)
  place(brace_face,actor.global_position+actor.facing*.65+Vector3.UP*.95,Vector2(1.7,1.25),.28,actor.facing)
 if kit.braced and not was_braced:mark("brace_planted")
 was_braced=kit.braced
 for row in live.duplicate():
  row.age+=delta
  if row.age>=row.life:row.node.queue_free();live.erase(row);continue
  var u: float=row.age/row.life
  place(row.node,row.at,row.size*(.94+.06*u),row.alpha*(1-smoothstep(.15,1,u)),row.normal,row.yaw)
