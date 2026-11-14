extends SceneTree
var failed:=0
func _initialize() -> void:run.call_deferred()
func check(ok: bool,label: String) -> void:
	print("PASS " if ok else "FAIL ",label)
	if not ok:failed+=1
func frames(n: int) -> void:
	for i in n:await process_frame
func run() -> void:
	var play: Node3D=load("res://scenes/moba3d/arena_play.tscn").instantiate();root.add_child(play)
	await frames(4);play.set_machine("gorilla");await frames(5)
	var p: Node3D=play.player;var k: ApeKit=p.get_node("Kit");var t: Node3D=k.targeting
	check(t!=null,"main arena installs local targeting")
	var allies: Array=MatchTeams.allies_of(p).filter(func(n):return n!=p)
	var ally: Node3D=allies[0]
	p.position=Vector3.ZERO;ally.position=Vector3(2,0,-3);p.input_override=Vector2.ZERO
	for unit in get_nodes_in_group("match_unit"):
		var brain: Node=unit.get_node_or_null("Bot")
		if brain!=null:brain.hold=true
		if unit.get("bot")==true:unit.input_override=Vector2.ZERO
	t.point_override=ally.position
	check(t.arm("1") and t.hovered==ally,"main arena hover selects real allied machine")
	check(p.cooldowns.is_empty(),"main director charges nothing for preview")
	var attack_before: float=p.attack_cd;play.player_attack()
	check(p.attack_cd==attack_before and k.current=="","main basic polling is suppressed during targeting")
	t.confirm();await frames(1)
	check(float(p.cooldowns.get("1",0))>0,"main director starts cooldown on confirmed cast")
	await frames(30)
	check(ApeKit.shield_on(ally)!=null,"real ally receives shield in main arena")
	await frames(15);k.abort_arena();p.cooldowns.clear()
	var foes: Array=MatchTeams.enemies_of(p).filter(func(n):return n.get("kind")=="machine")
	var foe: Node3D=foes[0];foe.halt();foe.position=Vector3(0,0,-4);foe.hp=foe.max_hp;foe.stunned=0;foe.facing=Vector3.FORWARD
	p.position=Vector3.ZERO;p.facing=Vector3.FORWARD;t.point_override=foe.position;p.aim_screen_override=p.get_viewport().get_camera_3d().unproject_position(foe.position)
	check(t.arm("3") and t.confirm(),"main arena confirms combined move")
	await frames(120)
	check(is_equal_approx(foe.max_hp-foe.hp,52) and not foe.has_meta("held_by"),"real match drive and slam apply once and release")
	check(float(p.cooldowns.get("3",0))>0 and float(p.cooldowns.get("2",0))<=0,"real director charges single combined cooldown")
	k.abort_arena();p.cooldowns.clear();p.position=Vector3.ZERO;foe.position=Vector3(0,0,-4);foe.hp=foe.max_hp;foe.stunned=0
	t.point_override=foe.position;check(t.arm("2") and t.confirm(),"main arena confirms new fault line")
	await frames(80)
	check(is_equal_approx(foe.max_hp-foe.hp,22) and foe.slowed>0,"real match fault line damages and slows")
	k.abort_arena();p.cooldowns.clear();t.arm("1")
	var weak=weakref(t);play.set_machine("rhino");await frames(4)
	check(weak.get_ref()==null,"swapping machine removes preview and input controller")
	play.queue_free();await frames(4);MechModel3D.clear_templates()
	print("MAIN_TARGETING_CHECK_COMPLETE failures=",failed);quit(1 if failed else 0)
