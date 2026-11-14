extends SceneTree
func _initialize() -> void:run.call_deferred()
func run() -> void:
	# Historical measurement only. Refuse to overwrite v1 evidence against a newer map.
	var script = load("res://scripts/map5v5/foundation_map.gd")
	if script.get_script_constant_map().HALF_X != 80.0:
		push_error("Baseline tool requires the archived v1 layout; existing evidence was preserved.")
		quit(1)
		return
	var game: Node3D=load("res://scenes/map5v5/foundation.tscn").instantiate();root.add_child(game)
	for i in 90:await physics_frame
	var map: RID=game.arena.get_world_3d().navigation_map
	var points: Dictionary={"gold":Vector3(-29,0,9),"wyvern":Vector3(29,0,-9),"mid":Vector3.ZERO}
	var rows: Dictionary={}
	for pair in [["mid","gold"],["mid","wyvern"],["gold","wyvern"]]:
		var path:=NavigationServer3D.map_get_path(map,points[pair[0]],points[pair[1]],true)
		var distance:=0.0
		for j in path.size()-1:distance+=path[j].distance_to(path[j+1])
		rows[pair[0]+"_to_"+pair[1]]={"m":distance,"seconds_at_3_5":distance/3.5}
	var f:=FileAccess.open("res://docs/plan/foundry-5v5-2026-11-11/v1-rotation.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(rows,"\t"));f.close();print("V1_ROTATION ",JSON.stringify(rows))
	game.queue_free();await process_frame;quit()
