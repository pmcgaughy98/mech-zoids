extends SceneTree
func _initialize() -> void:
	var scene:=Node3D.new()
	scene.set_script(load("res://tools/debug/gorilla_targeting_2026_11_10/art_review.gd"))
	root.add_child.call_deferred(scene)
