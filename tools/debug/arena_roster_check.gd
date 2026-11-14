extends SceneTree
const ROSTER=preload("res://scripts/moba3d/arena_roster.gd")
var fails:=0
var rows: Array=[]
var game: Node3D
var p: Node3D
func _initialize() -> void:_run.call_deferred()
func check(ok: bool,what: String) -> void:
	rows.append({"check":what,"pass":ok});print(("PASS " if ok else "FAIL ")+what)
	if not ok:fails+=1
func wait(seconds: float) -> void:await create_timer(seconds).timeout
func park() -> void:
	for m in game.director.machines:
		if m.get_node_or_null("Bot")!=null:m.get_node("Bot").hold=true
		m.move_override=Vector3.ZERO
func _run() -> void:
	game=load("res://scenes/moba3d/arena_play.tscn").instantiate();root.add_child(game)
	await process_frame;park();p=game.player
	check(ROSTER.kinds().size()==25,"25 model profiles, reference-only/duplicate excluded")
	for k in ROSTER.kinds():
		game.set_machine(k);await process_frame;await process_frame
		check(game.machine==k and p.body!=null and not p.sprite.visible,k+" selectable 3D body")
		if p.body!=null:
			var bounds: AABB=ROSTER.bounds(p.body.model_root())
			check(bounds.size.length()>.05 and bounds.size.length()<12,k+" finite arena scale")
		check(MatchTeams.machine_kind(p)==k,k+" correct match identity")
	game.set_machine("gorilla");await process_frame;await process_frame
	var kit: ApeKit=p.get_node("Kit")
	check(kit.has_method("abort_arena"),"latest gorilla kit installed")
	check(root.get_node("KitAudio")._wired.has(kit.get_instance_id()),"inherited arena kit wired to audio")
	for clip in ["Shield_Ally","Shield_Self","Ult","GrabSlam","DriveBrace","Drive","DriveHit","DriveBrake"]:check(p.body.has_clip(clip),"current clip "+clip)
	p.global_position=Vector3(0,0,0);p.facing=Vector3.FORWARD;p.body.snap_facing(p.facing)
	kit.hex_shield();await wait(.1);kit.abort_arena();await wait(.25)
	check(ApeKit.shield_on(p)==null,"shield interrupted before .25 release gives no shield")
	var release_frames: Array=[]
	var start_frame:=Engine.get_process_frames()
	var frame_seconds: float=p.get_process_delta_time()
	var release_callback:=func(clip,ev,_damage):
		if clip.begins_with("Shield") and ev=="release":release_frames.append(Engine.get_process_frames())
	p.body.event.connect(release_callback)
	kit.hex_shield();await wait(.40)
	check(ApeKit.shield_on(p)!=null,"shield applies after authored release")
	check(release_frames.size()==1 and float(release_frames[0]-start_frame)*frame_seconds>=.25-frame_seconds-.0001 and float(release_frames[0]-start_frame)*frame_seconds<=.25+frame_seconds+.0001,"shield release emitted once within one rendered frame of .25s")
	p.body.event.disconnect(release_callback)
	print("SHIELD_RELEASE_FRAME_AUDIT ",JSON.stringify({"start":start_frame,"released":release_frames,"frame_seconds":frame_seconds}))
	kit.abort_arena();await wait(.05)
	kit.chest_beat_ult();await wait(.2);kit.abort_arena();await wait(1.5)
	check(HexShield.live_domes().is_empty(),"interrupted ult cannot raise delayed cage")
	var enemy: Node3D=game.director.machines.filter(func(m):return m.team=="red")[0]
	enemy.global_position=Vector3(0,0,-1.8);enemy.hp=enemy.max_hp;enemy.stunned=0;enemy.halt()
	for m in game.director.machines:
		if m!=p and m!=enemy:m.global_position=Vector3(16,0,16)
	var hp: float=enemy.hp
	kit.fling(enemy);await wait(.22)
	check(enemy.has_meta("held_by"),"real match machine captured at .18")
	check(not enemy.slot_ready("1"),"held machine cannot cast")
	await wait(.45)
	check(not enemy.has_meta("held_by") and absf(enemy.global_position.y)<.001,"slam drops victim onto ground")
	check(is_equal_approx(hp-enemy.hp,kit.grab_damage),"ground slam damages exactly once")
	await wait(.5)
	enemy.stunned=0;enemy.global_position=Vector3(0,0,-1.8);enemy.hp=enemy.max_hp
	kit.fling(enemy);await wait(.22);kit.abort_arena();hp=enemy.hp;await wait(.6)
	check(not enemy.has_meta("held_by") and enemy.global_position.y==0,"interrupted grab releases real victim")
	check(enemy.hp==hp,"interrupted grab cannot deal delayed slam damage")
	p.global_position=Vector3(0,0,0);p.facing=Vector3.FORWARD;enemy.global_position=Vector3(0,0,-3);enemy.stunned=0;enemy.hp=enemy.max_hp
	kit.bound();await wait(1.1)
	check(kit.drive.hit_count==1,"drive hits one real target")
	check(is_equal_approx(enemy.max_hp-enemy.hp,kit.drive_damage),"drive no duplicated shove damage")
	check(not p.busy and not p.body.external_clock,"drive returns control and animation clock")
	check(game.hud.SLOT_NAMES.gorilla[1]=="grab slam" and game.hud.SLOT_NAMES.gorilla[2]=="shield drive","HUD names match current moves")
	kit.hex_shield();await wait(.10);p.stun(.5);await wait(.25)
	check(ApeKit.shield_on(p)==null,"real stun interrupts shield before release")
	await wait(.4)
	kit.abort_arena();p.global_position=Vector3.ZERO;p.facing=Vector3.FORWARD
	enemy.global_position=Vector3(10,0,10)
	var minion: Node3D=game.director.spawn_minion("red",Vector3(0,0,-1.8))
	minion.global_position=Vector3(0,0,-1.8) # spawn_minion intentionally scatters normal waves randomly
	minion.stunned=2.0
	kit.fling(minion);await wait(.22)
	check(minion.has_meta("held_by"),"real minion can be held")
	print("MINION_GRAB_AUDIT ",JSON.stringify(kit.grab.capture_audit))
	kit.abort_arena();await process_frame
	check(not minion.has_meta("held_by") and minion.global_position.y==0,"minion released on interruption")
	var other: Node3D=game.director.machines.filter(func(m):return m!=p and m.get("body")!=null and m.body.kind=="gorilla")[0]
	var look=load("res://scripts/moba3d/mech_look.gd")
	look.set_flash(p.body.model_root(),.8);look.set_flash(other.body.model_root(),0.0)
	var ours: Array=p.body.model_root().get_meta("look_flash_materials")
	var theirs: Array=other.body.model_root().get_meta("look_flash_materials")
	check(not ours.is_empty() and ours[0]!=theirs[0] and is_equal_approx(float(ours[0].get_shader_parameter("hit_flash")),.8) and float(theirs[0].get_shader_parameter("hit_flash"))==0,"shared source meshes flash independently")
	look.set_flash(p.body.model_root(),0.0)
	var out:=FileAccess.open("D:/dev/_scratch/arena-roster-check-2026-11-10.json",FileAccess.WRITE);out.store_string(JSON.stringify({"fails":fails,"checks":rows},"\t"));out.close()
	print("ARENA_ROSTER_RESULT ",rows.size()," checks, ",fails," failures")
	game.queue_free();await process_frame;quit(1 if fails else 0)
