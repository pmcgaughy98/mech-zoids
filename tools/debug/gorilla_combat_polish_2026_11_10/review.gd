extends Node3D
const P="res://tools/debug/gorilla_combat_polish_2026_11_10/"
const OUT="D:/dev/_scratch/gorilla/combat-polish-2026-11-10/"
const SHOTS=[
 [2.2,"CURRENT / HEAVY BASIC / GAME CAMERA",false,180.0,"single"],
 [2.2,"COMPACT / HEAVY BASIC / GAME CAMERA",true,180.0,"single"],
 [2.2,"CURRENT / FRONT QUARTER",false,45.0,"single"],
 [2.2,"COMPACT / FRONT QUARTER",true,45.0,"single"],
 [2.2,"CURRENT / SIDE / SUPPORT CHECK",false,90.0,"single"],
 [2.2,"COMPACT / SIDE / SUPPORT CHECK",true,90.0,"single"],
 [4.0,"CURRENT / THREE HIT CHAIN",false,180.0,"chain"],
 [4.0,"COMPACT / THREE HIT CHAIN",true,180.0,"chain"],
 [4.0,"CURRENT / STRAFE WHILE ATTACKING",false,180.0,"move"],
 [4.0,"COMPACT / STRAFE WHILE ATTACKING",true,180.0,"move"],
 [4.0,"COMPACT / SHARP STRAFE REVERSAL",true,180.0,"turn"]
]
var actor: Node3D
var body: MechModel3D
var kit: ApeKit
var enemy: Node3D
var camera: Camera3D
var label: Label
var interactive:=false
var shot:=-1
var clock:=0.0
var elapsed:=0.0
var next_attack:=.45
var attacks:=0
var events: Array=[]
var results: Array=[]
var hits:=0
var cd:=0.0
func _ready() -> void:
 process_priority=-20
 interactive="--interactive" in OS.get_cmdline_user_args()
 get_window().title="Gorilla / combat polish A-B"
 get_window().size=Vector2i(1280,720)
 get_window().content_scale_size=Vector2i(1280,720)
 var field: Node3D=load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
 add_child(field)
 actor=field.get_node("Player")
 actor.process_priority=-15
 actor.team="blue"
 actor.set_meta("is_player",false)
 if actor.body!=null:actor.body.visible=false
 for n in ["Sprite","Ring","Shadow"]:actor.get_node(n).visible=false
 body=load(P+"body.gd").new()
 actor.add_child(body)
 assert(body.configure_review())
 actor.body=body
 actor.MECH_LOOK.apply_model(body.model_root(),false)
 kit=load("res://scripts/moba3d/arena_gorilla_kit.gd").install_arena(actor)
 kit.shake_camera=false
 kit.set_process_unhandled_key_input(false)
 enemy=load("res://tools/debug/gorilla_visual_review_2026_11_09/target.gd").new()
 add_child(enemy)
 enemy.visual_fx=false
 enemy.hurt.connect(func(amount,_by):hits+=1;events.append({"time":clock,"amount":amount,"clip":body.action,"clip_time":body.anim.current_animation_position}))
 camera=field.get_node("Camera")
 camera.distance=6.6
 camera.pitch_degrees=12
 camera.look_height=1.3
 camera.set_process_unhandled_input(interactive)
 var layer:=CanvasLayer.new();add_child(layer)
 label=Label.new();label.position=Vector2(20,20);label.add_theme_font_size_override("font_size",23);layer.add_child(label)
 var bus:=AudioServer.get_bus_index("SFX")
 if bus>=0:AudioServer.set_bus_mute(bus,true)
 set_shot(0)
 print("COMBAT_POLISH_READY")
func result() -> Dictionary:return {"shot":shot,"title":SHOTS[shot][1],"compact":SHOTS[shot][2],"attacks":attacks,"hits":hits,"hp":enemy.hp,"events":events.duplicate(true),"position":actor.global_position,"remaining_action":body.action}
func set_shot(index: int) -> void:
 if shot>=0:results.append(result())
 kit.abort_arena();body.stop_action()
 shot=index;clock=0;next_attack=.45;attacks=0;hits=0;events.clear();cd=0
 kit.chain_hit=0;kit._chain_timer=null;kit._left_next=false
 actor.position=Vector3.ZERO;actor.facing=Vector3(0,0,1);actor.busy=false;actor.stunned=0
 actor.move_override=null if interactive else Vector3.ZERO
 actor.input_override=null if interactive else Vector2.ZERO
 body.use_compact(SHOTS[shot][2]);body.snap_facing(actor.facing);body.locomote(0)
 enemy.reset(Vector3(0,0,1.28 if SHOTS[shot][4] in ["single","chain"] else 1.8))
 camera.yaw_degrees=SHOTS[shot][3];camera.snap()
func attack(force_slam: bool) -> void:
 if force_slam:kit.chain_hit=2;kit._chain_timer=get_tree().create_timer(5)
 if kit.basic_attack(enemy):attacks+=1;cd=kit.basic_cooldown
func _process(delta: float) -> void:
 if actor==null:return
 elapsed+=delta;clock+=delta;cd=maxf(0,cd-delta)
 if is_instance_valid(kit._aura):kit._aura.visible=false
 if is_instance_valid(kit.fx):kit.fx.visible=false
 var mode: String=SHOTS[shot][4]
 if not interactive:
  if mode in ["move","turn"]:
   var rel: Vector3=actor.global_position-enemy.global_position;rel.y=0
   var sign: float=-1.0 if mode=="turn" and clock>2.1 else 1.0
   var tangent:=Vector3(-rel.z,0,rel.x).normalized()*sign
   var radial:=rel.normalized()*(1.8-rel.length())*2.5
   actor.move_override=(tangent+radial).limit_length(1)
   actor.facing=-rel.normalized();actor._aim_hold=.2
  if clock>=next_attack and attacks<(1 if mode=="single" else 3):
   attack(mode=="single");next_attack+=1.05
  if clock>=SHOTS[shot][0]:
   if shot+1==SHOTS.size():
    results.append(result())
    var file:=FileAccess.open(OUT+"native-results.json",FileAccess.WRITE);file.store_string(JSON.stringify(results,"  "))
    print("COMBAT_POLISH_COMPLETE");get_tree().quit()
   else:set_shot(shot+1)
 else:
  if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and cd<=0:attack(false)
 label.text="GORILLA / COMBAT POLISH\n"+("WASD / hold LMB / 3 heavy / Tab current vs compact / R reset" if interactive else SHOTS[shot][1])+"\nBODY ONLY / EXISTING KIT TIMING"
func _unhandled_input(event: InputEvent) -> void:
 if not interactive or not event is InputEventKey or not event.pressed or event.echo:return
 if event.keycode==KEY_TAB:set_shot(0 if SHOTS[shot][2] else 1)
 elif event.keycode==KEY_R:set_shot(shot)
 elif event.keycode==KEY_3 and cd<=0:attack(true)
 elif event.keycode==KEY_ESCAPE:get_tree().quit()
func _exit_tree() -> void:
 for template in MechModel3D._templates.values():
  if is_instance_valid(template):template.free()
 MechModel3D._templates.clear()
