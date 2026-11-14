extends RefCounted
## Shared local manufacture contract; regenerate with tools/art/build_arena_roster.py.
static var _rows: Dictionary={}
static func rows() -> Dictionary:
	if _rows.is_empty():
		var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://art/arena_models/roster.json"))
		for row in data.entries:_rows[row.id]=row
	return _rows
static func profile(kind: String) -> Dictionary:return rows().get(kind,{})
static func kinds() -> Array:return rows().keys()
static func bounds(model: Node3D) -> AABB:
	var result:=AABB()
	var first:=true
	for m in model.find_children("*","MeshInstance3D",true,false):
		if m.mesh==null:continue
		var b: AABB=(model.global_transform.affine_inverse()*m.global_transform)*m.get_aabb()
		result=b if first else result.merge(b)
		first=false
	return result
