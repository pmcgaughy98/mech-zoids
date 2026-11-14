extends SceneTree
## Real movement through the revised jungle; isolated cuts are explicitly captioned.
var game: Node3D
var player: Node3D
var camera: Camera3D
var caption: Label
var checks: Array=[]
var output:="res://docs/plan/foundry-5v5-2026-11-11-open-bosses/"
func _initialize() -> void:run.call_deferred()
func wait(seconds: float) -> void:await create_timer(seconds).timeout
func run() -> void:
	create_timer(100).timeout.connect(func():push_error("walkthrough timed out");quit(2))
	root.size=Vector2i(1280,720)
	game=load("res://scenes/map5v5/foundation.tscn").instantiate();root.add_child(game)
	await wait(1.2)
	player=game.player;camera=game.arena.get_node("Camera")
	var layer:=CanvasLayer.new();layer.layer=40;root.add_child(layer)
	# The project renders UI on a 320x180 base canvas, then scales to the native window.
	caption=Label.new();caption.position=Vector2(49,26);caption.add_theme_font_size_override("font_size",6)
	caption.add_theme_color_override("font_shadow_color",Color.BLACK);caption.add_theme_constant_override("shadow_offset_x",1);caption.add_theme_constant_override("shadow_offset_y",1);layer.add_child(caption)
	player.move_override=Vector3.ZERO;player.global_position=Vector3(0,0,24);camera.yaw_degrees=90;camera.snap()
	caption.text="MID > OPEN JUNGLE APPROACH > MINT YARD  |  actual 3.5 m/s walking"
	await wait(1)
	for point: Vector2 in [Vector2(-12,24),Vector2(-16,15),Vector2(-24.8,9.2),Vector2(-30,5)]:
		await walk_to(Vector3(point.x,0,point.y))
	caption.text="GOLD BEETLE  |  open toward mid and both jungle routes"
	player.move_override=Vector3.ZERO;camera.yaw_degrees=105;camera.snap();await wait(3)
	caption.text="WALKING BACK THROUGH THE BROAD MID OPENING"
	await walk_to(Vector3(-26,0,0));await walk_to(Vector3(0,0,0));await wait(1)
	caption.text="CUT TO OPPOSITE COURT  |  WYVERN / REACTOR VAULT"
	player.global_position=Vector3(23,0,-8);camera.yaw_degrees=-75;camera.snap();await wait(3)
	caption.text="FIXED PLACEMENTS  |  OPEN MID / JUNGLE FACES, OUTER BACKING WALLS"
	var overhead:=Camera3D.new();overhead.projection=Camera3D.PROJECTION_ORTHOGONAL;overhead.size=255
	game.add_child(overhead);overhead.position=Vector3(0,200,.001);overhead.look_at(Vector3.ZERO,Vector3.FORWARD);overhead.current=true
	game.hud.visible=false;game.arena.built.get_node("Minimap").visible=false;await wait(4)
	var f:=FileAccess.open(output+"walkthrough-checks.json",FileAccess.WRITE);f.store_string(JSON.stringify(checks,"\t"));f.close()
	var failures:=checks.filter(func(c):return not c.pass).size()
	print("WALKTHROUGH_RESULT ",checks.size()," waypoints / ",failures," failures")
	game.queue_free();await process_frame;quit(1 if failures else 0)
func walk_to(target: Vector3) -> void:
	var path:=NavigationServer3D.map_get_path(game.arena.get_world_3d().navigation_map,player.global_position,target,true)
	var frames:=0
	for at in path:
		at.y=0
		while player.global_position.distance_to(at)>.3 and frames<650:
			var dir: Vector3=(at-player.global_position).normalized()
			player.move_override=dir
			var desired:=rad_to_deg(atan2(-dir.x,-dir.z))
			camera.yaw_degrees=rad_to_deg(lerp_angle(deg_to_rad(camera.yaw_degrees),deg_to_rad(desired),.08))
			await process_frame;frames+=1
		if frames>=650:break
	player.move_override=Vector3.ZERO
	checks.append({"target":[target.x,target.z],"actual":[player.global_position.x,player.global_position.z],"pass":player.global_position.distance_to(target)<1.0,"frames":frames})
