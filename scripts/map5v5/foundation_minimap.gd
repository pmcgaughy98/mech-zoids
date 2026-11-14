extends Control
var arena: Node3D
var map_size:=Vector2.ZERO
var px_per_metre:=1.0
var outer:=Rect2()
func _ready() -> void:
	mouse_filter=Control.MOUSE_FILTER_IGNORE
	px_per_metre=76.0/maxf(arena.HALF_X*2,arena.HALF_Z*2)
	map_size=Vector2(arena.HALF_X*2,arena.HALF_Z*2)*px_per_metre
	size=map_size+Vector2(4,4)
func _process(_delta: float) -> void:
	position=(get_viewport_rect().size-size-Vector2(3,3)).floor()
	queue_redraw()
func point(p: Vector3) -> Vector2:
	return Vector2(2,2)+(Vector2(p.x,p.z)+Vector2(arena.HALF_X,arena.HALF_Z))*px_per_metre
func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO,size),Color(.035,.05,.065))
	draw_rect(Rect2(Vector2(2,2),map_size),Color(.19,.21,.22))
	for link in arena.connectors:
		var pts:=PackedVector2Array()
		for p in link.points:pts.append(point(Vector3(p.x,0,p.y)))
		draw_polyline(pts,Color(.36,.4,.41),link.width*px_per_metre)
	for route in [arena.LANE,arena.LEFT,arena.RIGHT]:
		var points:=PackedVector2Array()
		for p in route:points.append(point(Vector3(p.x,0,p.y)))
		draw_polyline(points,Color(.55,.57,.56),14*px_per_metre)
		draw_polyline(points,Color(.2,.23,.24),1.6)
	for b in arena.blockers:
		var at: Vector3=b.at;var sz: Vector3=b.size
		var corners:=PackedVector2Array()
		for v in [Vector2(-1,-1),Vector2(1,-1),Vector2(1,1),Vector2(-1,1)]:
			var local: Vector2=v*Vector2(sz.x,sz.z)*.5
			local=local.rotated(-b.get("yaw",0.0))
			corners.append(point(at+Vector3(local.x,0,local.y)))
		draw_colored_polygon(corners,Color(.055,.075,.09))
	for title in arena.sites:
		var site: Dictionary=arena.sites[title];var p: Vector2=site.p
		var boss: bool="GOLD" in title or "WYVERN" in title
		draw_circle(point(Vector3(p.x,0,p.y)),3 if boss else 1.6,Color(1,.65,.2) if "GOLD" in title else (Color(.68,.5,1) if "WYVERN" in title else Color(.65,.75,.78)))
	for u in get_tree().get_nodes_in_group("map_units"):
		if not u is Node3D: continue
		var p:=point(u.global_position)
		if u.get_meta("is_player",false): draw_circle(p,2.2,Color.WHITE)
		else:draw_circle(p,1.2,Color(.2,.65,1) if u.get_meta("team","")=="blue" else Color(1,.3,.2))
