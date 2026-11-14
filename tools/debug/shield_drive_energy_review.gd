extends SceneTree
var game: Node3D
var out:="D:/dev/_scratch/shield-drive-energy-2026-11-10/"
func _initialize() -> void:run.call_deferred()
func wait(t: float) -> void:await create_timer(t).timeout
func run() -> void:
	DirAccess.make_dir_recursive_absolute(out);root.size=Vector2i(1280,720)
	MatchRules.first_wave_at=9999.0 # isolate the visual review from wave combat while recording
	game=load("res://scenes/moba3d/arena_play.tscn").instantiate();root.add_child(game);await process_frame
	game.set_machine("gorilla");await process_frame;await process_frame
	var p: Node3D=game.player
	var kit: ApeKit=p.get_node("Kit")
	var enemy: Node3D=game.director.machines.filter(func(m):return m.team=="red")[0]
	for m in game.director.machines:
		if m.get_node_or_null("Bot")!=null:m.get_node("Bot").hold=true
		m.move_override=Vector3.ZERO;m.global_position=Vector3(18,0,18)
	p.bot=true
	var cam: Camera3D=game.arena.get_node("Camera")
	var cases: Array=[[150,6.8,16,1.2,3.0],[0,12.0,13,3.2,8.0],[90,7.0,16,1.2,3.0]]
	var rows: Array=[]
	for i in cases.size():
		var c: Array=cases[i]
		kit.abort_arena();p.halt();p.alive=true;p.hp=p.max_hp;p.stunned=0;p.cooldowns.clear()
		p.global_position=Vector3(0,0,12);p.facing=Vector3.FORWARD;p.body.snap_facing(p.facing)
		enemy.halt();enemy.global_position=p.global_position+Vector3.FORWARD*float(c[4]);enemy.hp=enemy.max_hp;enemy.alive=true;enemy.stunned=0
		cam.yaw_degrees=c[0];cam.distance=c[1];cam.pitch_degrees=c[2];cam.look_height=c[3];cam.snap()
		await wait(.45)
		kit.bound();await wait(.29)
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(out+"drive-%d.png"%i)
		rows.append({"view":i,"visible_during_drive":kit.drive_energy.visible,"faces":kit.drive_energy.panels.size()})
		await wait(1.25)
		rows[-1]["hidden_after"]=not kit.drive_energy.visible
		kit.abort_arena();await wait(.40)
	kit.bound();await wait(.08);kit.abort_arena()
	rows.append({"interrupted_hidden":not kit.drive_energy.visible})
	var file:=FileAccess.open(out+"results.json",FileAccess.WRITE);file.store_string(JSON.stringify(rows,"\t"));file.close()
	print("SHIELD_DRIVE_ENERGY_REVIEW ",JSON.stringify(rows))
	game.queue_free();await process_frame;quit()
