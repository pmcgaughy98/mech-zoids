extends "res://scripts/moba3d/ape_kit.gd"
## Match integration of Preston's selected local trials. Shared parent retains basic/shield rules.
var fx: Node3D
var drive: Node
var grab: Node
var visual_body: MechModel3D
var drive_energy: Node3D
var _custom:=false
var targeting: Node3D
var painted_fx: Node3D
var fault: Node3D
var fault_aim:=Vector3.ZERO
@export var drive_damage:=24.0
@export var grab_damage:=28.0
static func install_arena(p: Node3D) -> ApeKit:
	p.sprite.stop_action();p.sprite.sprite_frames=APE_FRAMES;p.sprite.size_class="L"
	p.sprite.play(StringName("idle_"+p.sprite.view))
	var old:=p.get_node_or_null("Kit")
	if old!=null:p.remove_child(old);old.queue_free()
	var kit: ApeKit=load("res://scripts/moba3d/arena_gorilla_kit.gd").new()
	kit.name="Kit";p.add_child(kit);return kit
func _ready() -> void:
	super._ready()
	if not player.bot:
		targeting=load("res://scripts/moba3d/gorilla_targeting.gd").new()
		add_child(targeting);targeting.setup(self,player)
	painted_fx=load("res://scripts/moba3d/gorilla_painted_fx.gd").new()
	add_child(painted_fx);painted_fx.setup(self,player)
	fault=load("res://scripts/moba3d/gorilla_fault_line.gd").new();add_child(fault);fault.setup(player,painted_fx)
	_configure.call_deferred()
func _unhandled_key_input(event: InputEvent) -> void:
	if player.bot:return
	var key:=event as InputEventKey
	if key==null or not key.pressed or key.echo:return
	if key.physical_keycode>=KEY_1 and key.physical_keycode<=KEY_4:
		if targeting!=null:targeting.arm(str(key.physical_keycode-KEY_0))
		get_viewport().set_input_as_handled()
func blocks_basic_input() -> bool:
	return targeting!=null and targeting.blocks_basic()
func basic_attack(target: Node3D) -> bool:
	if blocks_basic_input():return false
	return super.basic_attack(target)
func _shield_target_valid(target: Node3D) -> bool:
	return is_instance_valid(target) and target.get("alive")!=false and (target==player or allies().has(target)) and flat(target.global_position-feet()).length()<=shield_range and MatchTeams.clear_line(player,feet(),target.global_position)
func _configure() -> void:
	if player.bot and is_instance_valid(targeting):targeting.queue_free();targeting=null
	visual_body=_body()
	if visual_body==null or not visual_body.has_clip("GrabSlam"):return
	fx=load("res://scripts/moba3d/arena_contact_fx.gd").new();add_child(fx);fx.setup(visual_body.model_root())
	drive_energy=load("res://scripts/moba3d/shield_drive_energy.gd").new();add_child(drive_energy);drive_energy.setup(player,visual_body)
	drive=load("res://scripts/moba3d/arena_drive.gd").new();add_child(drive);drive.setup(player);drive.damage=drive_damage
	drive.phase_changed.connect(_drive_phase)
	drive.chain_slam=true
	drive.finished.connect(_drive_finished)
	drive.collision.connect(func(t,_amount):fx.contact(t.global_position+Vector3.UP*.7,player.facing,true);cue.emit("drive_hit"))
	grab=load("res://scripts/moba3d/arena_grab.gd").new();add_child(grab);grab.setup(player,visual_body);grab.damage=grab_damage
	grab.caught.connect(func(_t):fx.cells(.2);cue.emit("fling_grab"))
	grab.slammed.connect(func(t):fx.ground(t.global_position,.7);impact.emit(.65);cue.emit("grab_ground"))
	grab.finished.connect(_custom_finished)
	painted_fx.bind_actions()
	visual_body.event.connect(_visual_event)
	contact.connect(func(t,slam):
		if is_instance_valid(t):fx.contact(t.global_position+Vector3.UP*.7,player.facing,slam)
	)
func _process(delta: float) -> void:
	if current!="" and (not player.alive or player.stunned>0 or player.has_meta("held_by")):
		abort_arena();return
	if not _custom:return
	if not is_instance_valid(visual_body):abort_arena();return
	if not player.alive or player.stunned>0 or player.has_meta("held_by"):abort_arena();return
	if drive.phase!="idle":
		if player.move_dir().length()>.05:drive.request_movement()
		if drive.phase!="idle":
			drive.valid_targets=targets();drive.tick(delta)
			if drive.phase!="idle":visual_body.sample_external(_drive_clip(drive.phase),drive.phase_time)
	if grab.active:grab.tick(delta)
func _begin(anim: String) -> bool:
	if not player.alive or player.stunned>0 or player.has_meta("held_by"):return false
	return super._begin(anim)
func _drive_clip(phase: String) -> String:return {"brace":"DriveBrace","drive":"Drive","hit":"DriveHit","brake":"DriveBrake"}.get(phase,"DriveBrake")
func _drive_phase(phase: String) -> void:
	if is_instance_valid(drive_energy):drive_energy.set_phase(phase)
	if phase!="idle":visual_body.start_external(_drive_clip(phase))
	if phase=="brace":fx.cells(.2)
func _custom_finished(_reason: String) -> void:
	_custom=false
	if is_instance_valid(visual_body):visual_body.finish_external()
	_end()
func _drive_finished(reason: String) -> void:
	if reason=="enemy_hit" and is_instance_valid(drive.struck) and grab.eligible(drive.struck) and MatchTeams.edge_distance(player,drive.struck)<=fling_reach+.1 and flat(drive.struck.global_position-feet()).dot(drive.direction)>0 and MatchTeams.clear_line(player,feet(),drive.struck.global_position) and not grab._cage_blocks(feet(),drive.struck.global_position):
		player.busy=true
		player.facing=flat(drive.struck.global_position-feet()).normalized();visual_body.snap_facing(player.facing)
		if grab.begin(drive.struck,true):return
	_custom_finished(reason)
func abort_arena() -> void:
	if is_instance_valid(targeting):targeting.cancel()
	_ev_id+=1;_recovering=false;_ult_body=null
	if is_instance_valid(drive):drive.interrupt("interrupted")
	if is_instance_valid(grab):grab.interrupt("interrupted")
	_custom=false
	if is_instance_valid(visual_body):
		if visual_body.external_clock:visual_body.finish_external()
		else:visual_body.stop_action()
	_end()
func _exit_tree() -> void:
	if is_instance_valid(grab):grab.interrupt("exit")
	super._exit_tree()
func fling(target: Node3D=null) -> bool:
	var dir: Vector3=flat(target.global_position-feet()).normalized() if is_instance_valid(target) else player.aim_dir() if not player.bot else ahead()
	return _start_drive(dir)
func bound() -> void:
	var dir: Vector3=player.aim_dir() if not player.bot else ahead()
	_start_drive(dir)
func _start_drive(dir: Vector3) -> bool:
	if drive==null or not player.slot_ready("3") or not _begin("shield_drive"):return false
	_custom=true;used.emit("3")
	if dir.length_squared()<.01:dir=ahead()
	visual_body.snap_facing(dir)
	if not drive.begin(dir):_custom_finished("refused");return false
	return true
func fault_line(at: Vector3=Vector3.INF) -> void:
	if not player.slot_ready("2") or not _begin("fault_line"):return
	fault_aim=fault.endpoint((player.aim_point() if not player.bot else feet()+ahead()*fault.RANGE) if at==Vector3.INF else at)
	used.emit("2")
	var clip:="FaultLine" if _body("FaultLine")!=null else "Slam" # slot 2's own clip when the body has one (gorilla lane, 2026-11-13); the heavy slam otherwise
	var b:=_body(clip)
	if b==null:_end();return
	_play(b,clip)
	var id:=_ev_id
	if await _wait_event(b,clip,DAMAGE):
		if _ev_id==id and player.alive and player.stunned<=0:fault.launch(fault_aim);cue.emit("grab_ground")
		if clip=="FaultLine" and _ev_id==id:await _wait_event(b,clip,"recover") # rooted until 0.2 s after it fires
	if _ev_id==id:
		_end();_recover(b,clip)
func _visual_event(clip: String, ev: String, _damage: bool) -> void:
	if clip=="Ult" and ev=="drum":fx.cells(.12);cue.emit("chest_contact")
	if ev=="release" and clip.begins_with("Shield"):fx.cells(.2)
func _raise_dome(c: Vector3,r:=-1.0,cage_all:=false) -> HexShield:
	var dome:=super._raise_dome(c,r,cage_all)
	dome._mat.shader=load("res://shaders/arena_cage.gdshader")
	dome._mat.set_shader_parameter("tiles",Vector2(36,21))
	if fx!=null:fx.ground(c,.9)
	return dome
func chest_beat_ult() -> void:
	if not _begin("chest_beat"):return
	used.emit("4")
	var b:=_body("Ult")
	if b==null:_end();return
	_ult_body=b;_play(b,"Ult")
	var id:=_ev_id
	for i in 3:
		if not await _wait_event(b,"Ult","beat",i+1):
			if _ev_id==id:_end()
			_ult_body=null;return
		if _ev_id!=id or not player.alive or player.stunned>0:return
		if i<2:
			_pulse(feet(),ult_radius,.35 if i==0 else .25)
			impact.emit(.3 if i==0 else .15)
			for t in targets():
				if flat(t.global_position-feet()).length()<=ult_radius and t.has_method("taunt"):t.taunt(player,ult_taunt_time)
		else:
			var dome:=_raise_dome(feet(),ult_dome_radius,true)
			dome.ward=true;dome.ward_owner=player;dome.ward_heal_share=dome_ward_heal
	while is_instance_valid(b) and b.action=="Ult" and _ev_id==id:await get_tree().process_frame
	_ult_body=null
	if _ev_id==id:_end()
