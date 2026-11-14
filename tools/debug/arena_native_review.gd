extends SceneTree
var game: Node3D
var p: Node3D
var dir:="D:/dev/_scratch/arena-refresh-2026-11-10/"
var metrics: Array=[]
func _initialize() -> void:run.call_deferred()
func shot(name: String) -> void:
	await process_frame;await process_frame;await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(dir+name+".png")
func wait(seconds: float) -> void:await create_timer(seconds).timeout
func run() -> void:
	DirAccess.make_dir_recursive_absolute(dir)
	root.size=Vector2i(1280,720)
	game=load("res://scenes/moba3d/arena_play.tscn").instantiate();root.add_child(game)
	await process_frame
	p=game.player
	for m in game.director.machines:
		if m.get_node_or_null("Bot")!=null:m.get_node("Bot").hold=true
		m.move_override=Vector3.ZERO
	game.set_machine("gorilla");await wait(.2)
	await shot("01-current-match")
	game.roster_menu.visible=true;await shot("00-roster-menu");game.roster_menu.visible=false
	p.global_position=Vector3(0,0,12);p.facing=Vector3(0,0,-1)
	var cam: Camera3D=game.arena.get_node("Camera")
	cam.yaw_degrees=150;cam.snap()
	for kind in load("res://scripts/moba3d/arena_roster.gd").kinds():
		game.set_machine(kind);await wait(.15)
		await shot("model-"+kind)
		metrics.append({"kind":kind,"body":p.body!=null,"height":p.body.top_height() if p.body!=null else 0,"fps":Engine.get_frames_per_second()})
	game.set_machine("gorilla");await wait(.1)
	var kit: ApeKit=p.get_node("Kit")
	var enemy: Node3D=game.director.machines.filter(func(m):return m.team=="red")[0]
	enemy.global_position=p.global_position+Vector3(0,0,-1.8);enemy.stunned=0;enemy.halt()
	p.facing=Vector3.FORWARD;p.body.snap_facing(p.facing)
	kit.fling(enemy);await wait(.4);await shot("02-grab-lift");await wait(.22);await shot("03-ground-slam");await wait(.7)
	kit.chest_beat_ult();await wait(1.45);await shot("04-current-cage");await wait(.8)
	var file:=FileAccess.open(dir+"native.json",FileAccess.WRITE);file.store_string(JSON.stringify(metrics,"\t"));file.close()
	print("ARENA_NATIVE_REVIEW_COMPLETE")
	game.queue_free();await process_frame;quit()
