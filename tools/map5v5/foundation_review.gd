extends SceneTree
var game: Node3D
var p: Node3D
var checks: Array=[]
var fails:=0
var output:="res://docs/plan/foundry-5v5-2026-11-11-open-bosses/"
var render:=false
var metrics: Dictionary={}
func _initialize() -> void:
	render="--render" in OS.get_cmdline_user_args()
	run.call_deferred()
func check(value: bool, label: String) -> void:
	checks.append({"pass":value,"label":label})
	if not value:fails+=1;push_error(label)
func wait(seconds: float) -> void:await create_timer(seconds).timeout
func shot(title: String) -> void:
	if not render:return
	await process_frame;await process_frame;await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(output+title+".png")
func route(a: Vector3,b: Vector3,label: String) -> void:
	var path:=NavigationServer3D.map_get_path(game.arena.get_world_3d().navigation_map,a,b,true)
	var length:=0.0
	for i in path.size()-1:length+=path[i].distance_to(path[i+1])
	check(path.size()>1 and path[0].distance_to(a)<1.5 and path[-1].distance_to(b)<1.5,label)
	metrics[label]={"meters":snappedf(length,.1),"seconds_at_3_5":snappedf(length/3.5,.1)}
	# Sample the baked route against the actual physics, so a nav-only pass cannot hide a wall mismatch.
	var blocked:=0
	var blocked_points: Array=[]
	for i in path.size()-1:
		var n:=maxi(1,ceili(path[i].distance_to(path[i+1])))
		for j in n:
			var sample:=path[i].lerp(path[i+1],float(j)/n)*Vector3(1,0,1)
			if ArenaMotion.blocked(p,sample,p.body_radius()):
				blocked+=1;blocked_points.append([sample.x,sample.z])
	if blocked>0:print("BLOCKED_PATH ",label," ",JSON.stringify(blocked_points))
	check(blocked==0,label+" physics clearance")
func run() -> void:
	create_timer(90).timeout.connect(func():push_error("foundation review timed out");quit(2))
	DirAccess.make_dir_recursive_absolute(output)
	root.size=Vector2i(1280,720)
	game=load("res://scenes/map5v5/foundation.tscn").instantiate();root.add_child(game)
	await wait(.3);p=game.player
	for i in 60:await physics_frame
	check(game.director.machines.size()==10,"ten real training bodies")
	for team in ["blue","red"]:
		check(game.director.machines.filter(func(m):return m.team==team).size()==5,team+" five bodies")
		for at in game.arena.spawn_slots(team):
			check(not ArenaMotion.blocked(p,at,1),team+" spawn clear "+str(at.x))
	var cam: Camera3D=game.arena.get_node("Camera")
	check(cam.distance==12 and cam.pitch_degrees==13 and cam.look_height==3.2 and cam.fov==60,"approved native camera preserved")
	var saved_position: Vector3=p.global_position
	p.global_position=Vector3(game.arena.HALF_X-4,0,30);cam.yaw_degrees=90;cam.snap()
	check(cam.global_position.distance_to(p.global_position)>12,"camera apron preserves full arm at outer wall")
	var rear_foot:=cam.unproject_position(p.global_position+Vector3(1.5,0,0))
	check(rear_foot.y<root.get_visible_rect().size.y-31,"outer-wall rear-foot clearance above player HUD")
	p.global_position=saved_position;cam.yaw_degrees=0;cam.snap()
	check(game.MACHINES.size()>=25,"current roster available")
	var a: Vector3=game.arena.spawn_slots("blue")[0]
	for x in [-62.0,0.0,62.0]:route(a,Vector3(x,0,0),"spawn to route "+str(x))
	route(a,game.arena.spawn_slots("red")[0],"base to base")
	var gates: Dictionary=game.arena.objective_ports
	for kind in gates:
		for door in gates[kind]:
			var gate: Vector2=gates[kind][door]
			var target:=Vector3(gate.x,0,gate.y)
			for team in ["blue","red"]:route(game.arena.spawn_slots(team)[0],target,team+" to "+kind+" "+door)
			var inside:=Vector3(gate.x+signf(gate.x)*5.2,0,signf(gate.y)*5)
			route(target,inside,kind+" "+door+" enters court")
			check(ArenaMotion.ray(p,target+Vector3.UP*1.2,inside+Vector3.UP*1.2).is_empty(),kind+" "+door+" clear entrance sightline")
		check(gates[kind].north.distance_to(gates[kind].south)>=16,kind+" entrances spatially separate")
	for camp: Vector2 in game.arena.CAMP_POINTS:route(a,Vector3(camp.x,0,camp.y),"camp "+str(camp))
	_rotation_audit(gates)
	var b: Dictionary=game.arena.blockers[0]
	var at: Vector3=b.at;var sz: Vector3=b.size
	var from:=Vector3(-31,0,32)
	var to:=ArenaMotion.slide(p,from,Vector3(0,0,-16),.8)
	check(to.z>=26.75,"swept movement stops at connected jungle wall")
	# Test the current authored gorilla contracts on real foundation units.
	p.global_position=Vector3.ZERO;p.facing=Vector3.FORWARD;p.move_override=Vector3.ZERO
	for m in game.director.machines:
		if m!=p:m.move_override=Vector3.ZERO
	var enemy: Node3D=game.director.machines.filter(func(m):return m.team=="red")[0]
	enemy.global_position=Vector3(0,0,-1.8);enemy.stunned=0;enemy.hp=enemy.max_hp
	var kit=p.get_node("Kit")
	check(kit.grab!=null and kit.drive!=null,"current gorilla grab and Drive installed")
	kit.fling(enemy) # Current kit routes this to Drive Slam, not the November 10 standalone grab.
	for i in 100:
		if enemy.has_meta("held_by"):break
		await wait(.02)
	check(enemy.has_meta("held_by"),"current Drive Slam holds real target in foundation")
	await shot("grab-current-camera")
	kit.abort_arena();await wait(.15)
	check(not enemy.has_meta("held_by") and absf(enemy.position.y)<.01,"interruption releases target")
	p.global_position=Vector3.ZERO;p.facing=Vector3.FORWARD;cam.snap();p.aim_screen_override=cam.unproject_position(Vector3(0,0,-10))
	enemy.global_position=Vector3(0,0,-4);enemy.hp=enemy.max_hp;enemy.stunned=0
	p.cooldowns["3"]=0
	var hits_before: int=kit.drive.hit_count
	kit.bound();await wait(.3);await shot("drive-current-camera");await wait(1.8)
	check(kit.drive.hit_count==hits_before+1,"Drive hits one real foundation target")
	check(is_equal_approx(enemy.max_hp-enemy.hp,kit.drive_damage+kit.grab_damage),"current Drive Slam contact plus slam damage once each")
	check(game.hud.SLOT_NAMES.gorilla[1]=="fault line" and game.hud.SLOT_NAMES.gorilla[2]=="drive slam","current redesigned kit names inherited")
	kit.abort_arena();p.aim_screen_override=null
	kit.chest_beat_ult();await wait(.8)
	var head:=cam.unproject_position(p.global_position+Vector3.UP*3.1)
	var feet:=cam.unproject_position(p.global_position)
	check(head.y>0 and head.y<feet.y and feet.y<root.get_visible_rect().size.y-31,"full 3.1m Ult height fits camera above player HUD")
	await shot("ult-current-camera");await wait(1.3);kit.abort_arena()
	game.set_machine("rhino");await wait(.2)
	check(p.body!=null and p.body.kind=="rhino","current rhino body available")
	await shot("rhino-current-camera")
	game.set_machine("gorilla");await wait(.2)
	if render:
		var gallery: Array=[]
		var i:=0
		for kind in ["wall","pillar","camp","landmark"]:
			var asset: Node3D=game.arena._module(kind,Vector3(-9+i*6,0,8),{"wall":Vector3(6,2.6,1.6),"pillar":Vector3(2.4,4,2.4),"camp":Vector3(3.6,3.2,3.6),"landmark":Vector3(5.2,5,5.2)}[kind])
			if asset!=null:gallery.append(asset)
			i+=1
		p.global_position=Vector3(0,0,26);cam.yaw_degrees=0;cam.snap();game.hud.visible=false
		game.arena.built.get_node("Minimap").visible=false
		await shot("batch-game-camera")
		for asset in gallery:asset.queue_free()
		game.arena.dressing_count-=gallery.size()
		await process_frame;game.hud.visible=true;game.arena.built.get_node("Minimap").visible=true
		for res in [Vector2i(1280,720),Vector2i(1920,1080)]:
			root.size=res
			p.global_position=game.arena.spawn_slots("blue")[0];cam.yaw_degrees=0;cam.snap();await wait(.1)
			await shot("hud-"+str(res.x))
			check(root.get_texture().get_image().get_size()==res,"native capture "+str(res))
		root.size=Vector2i(1280,720)
		for spot in [{"p":Vector3(0,0,45),"yaw":0,"name":"mid-route"},{"p":Vector3(-62,0,32),"yaw":0,"name":"west-route"},{"p":Vector3(-23,0,8),"yaw":105,"name":"gold-approach"},{"p":Vector3(23,0,-8),"yaw":-75,"name":"power-approach"},{"p":Vector3(-50,0,35),"yaw":0,"name":"camp-loop"},{"p":Vector3(0,0,0),"yaw":90,"name":"mid-boss-sightline"},{"p":Vector3(-31,0,30),"yaw":0,"name":"cover-fade"},{"p":Vector3(game.arena.HALF_X-4,0,30),"yaw":90,"name":"edge-clamp"}]:
			p.global_position=spot.p;cam.yaw_degrees=spot.yaw;cam.snap();await wait(.22);await shot(spot.name)
		p.global_position=Vector3(-31,0,30);cam.yaw_degrees=180;cam.snap();await wait(.2)
		p.publish_machine_pos=false
		RenderingServer.global_shader_parameter_set("machine_hidden",0.0)
		await shot("occlusion-no-fade")
		var without:=root.get_texture().get_image()
		RenderingServer.global_shader_parameter_set("machine_hidden",1.0)
		await shot("occlusion-fade")
		var with_fade:=root.get_texture().get_image()
		var changed:=0
		for y in range(350,565):
			for x in range(550,730):
				if without.get_pixel(x,y).is_equal_approx(with_fade.get_pixel(x,y)):continue
				changed+=1
		metrics["fade_changed_pixels_in_body_region"]=changed
		check(changed>250,"native wall/module fade changes occluded body region")
		p.publish_machine_pos=true
		var overhead:=Camera3D.new();overhead.projection=Camera3D.PROJECTION_ORTHOGONAL;overhead.size=235
		game.add_child(overhead);overhead.position=Vector3(0,200,.001);overhead.size=255;overhead.look_at(Vector3.ZERO,Vector3.FORWARD);overhead.current=true
		game.hud.visible=false;game.arena.built.get_node("Minimap").visible=false
		await shot("top-down")
	metrics["nav_bake_ms"]=game.arena.nav_bake_ms
	var roster: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://art/arena_models/roster.json"))
	metrics["current_roster_snapshot"]=[]
	for entry in roster.entries:
		metrics.current_roster_snapshot.append({"id":entry.id,"stage":entry.stage,"source_sha256":entry.source_sha256})
	metrics["dressing_instances"]=game.arena.dressing_count
	var layout: Dictionary={"half_size":[game.arena.HALF_X,game.arena.HALF_Z],"routes":{},"connectors":[],"ports":{},"blockers":[],"sites":{},"spawns":{}}
	for key in ["LANE","LEFT","RIGHT"]:
		layout.routes[key]=[]
		for pt in game.arena.get_script().get_script_constant_map()[key]:layout.routes[key].append([pt.x,pt.y])
	for blocker in game.arena.blockers:layout.blockers.append({"center":[blocker.at.x,blocker.at.z],"size":[blocker.size.x,blocker.size.z],"yaw":blocker.get("yaw",0)})
	for link in game.arena.connectors:
		var pts: Array=[]
		for pt in link.points:pts.append([pt.x,pt.y])
		layout.connectors.append({"name":link.name,"points":pts,"width":link.width})
	for kind in gates:
		layout.ports[kind]={}
		for door in gates[kind]:layout.ports[kind][door]=[gates[kind][door].x,gates[kind][door].y]
	for key in game.arena.sites:
		var site: Dictionary=game.arena.sites[key]
		layout.sites[key]={"center":[site.p.x,site.p.y],"radius":site.radius}
	for team in ["blue","red"]:
		layout.spawns[team]=[]
		for spawn in game.arena.spawn_slots(team):layout.spawns[team].append([spawn.x,spawn.z])
	var layout_file:=FileAccess.open(output+"layout.json",FileAccess.WRITE);layout_file.store_string(JSON.stringify(layout,"\t"));layout_file.close()
	if "--require-batch" in OS.get_cmdline_user_args():
		for kind in ["wall","pillar","camp","landmark"]:
			check(ResourceLoader.exists(game.arena.ASSET_DIR+kind+".glb"),"runtime batch module "+kind)
		for kind in ["gold_beetle","wyvern"]:
			check(game.arena.objective_models.has(kind),"existing objective model placed "+kind)
		check(ArenaMotion.blocked(p,Vector3(game.arena.GOLD_SITE.x,0,game.arena.GOLD_SITE.y),.7) and ArenaMotion.blocked(p,Vector3(game.arena.WYVERN_SITE.x,0,game.arena.WYVERN_SITE.y),.7),"authored boss body footprints block movement")
	var f:=FileAccess.open(output+("native-review.json" if render else "checks.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"checks":checks,"fails":fails,"metrics":metrics},"\t"));f.close()
	print("FOUNDATION_RESULT ",checks.size()," checks / ",fails," failures")
	game.queue_free();await process_frame;await process_frame
	quit(1 if fails else 0)

func _path_length(a: Vector3,b: Vector3) -> float:
	var path:=NavigationServer3D.map_get_path(game.arena.get_world_3d().navigation_map,a,b,true)
	if path.size()<2:return INF
	var distance:=0.0
	for j in path.size()-1:distance+=path[j].distance_to(path[j+1])
	return distance

func _rotation_audit(gates: Dictionary) -> void:
	var mid: Dictionary={};var return_time: Dictionary={}
	var team_return: Dictionary={"blue":{},"red":{}}
	for kind in gates:
		mid[kind]=INF;return_time[kind]=INF
		for team in team_return:team_return[team][kind]=INF
		for door in gates[kind]:
			var gate: Vector2=gates[kind][door]
			var at:=Vector3(gate.x,0,gate.y)
			route(Vector3.ZERO,at,"mid to "+kind+" "+door)
			mid[kind]=minf(mid[kind],_path_length(Vector3.ZERO,at)/3.5)
			for team in ["blue","red"]:
				var seconds:=_path_length(game.arena.spawn_slots(team)[0],at)/3.5
				team_return[team][kind]=minf(team_return[team][kind],seconds)
				return_time[kind]=minf(return_time[kind],seconds)
		var centre:=Vector3(game.arena.GOLD_SITE.x if kind=="gold" else game.arena.WYVERN_SITE.x,1.2,0)
		check(absf(centre.x)+14<55,kind+" entire court inside outer-lane jungle edge")
		var opening:=Vector3(centre.x-signf(centre.x)*5,1.2,0)
		check(ArenaMotion.ray(p,Vector3(0,1.2,0),opening).is_empty(),kind+" open mid-facing sightline")
		route(Vector3.ZERO,opening*Vector3(1,0,1),kind+" direct mid opening")
		for end in [-1.0,1.0]:
			route(Vector3(10*signf(centre.x),0,36*end),Vector3(gates[kind].mid.x,0,0),kind+" jungle approach "+str(end))
	var between:=INF
	for first_door in gates.gold:
		var a: Vector2=gates.gold[first_door]
		for second_door in gates.wyvern:
			var b: Vector2=gates.wyvern[second_door]
			route(Vector3(a.x,0,a.y),Vector3(b.x,0,b.y),"gold "+first_door+" to wyvern "+second_door)
			between=minf(between,_path_length(Vector3(a.x,0,a.y),Vector3(b.x,0,b.y))/3.5)
	# Rotation timing is observational; Preston withdrew the long anti-chain requirement.
	metrics["objective_rotation"]={"mid_seconds":mid,"between_seconds":between,"defender_return_seconds":return_time,"return_seconds_by_team":team_return,"respawn_seconds":MatchRules.respawn_time,"walking_speed":3.5,"clear_time_assumption":0.0}
