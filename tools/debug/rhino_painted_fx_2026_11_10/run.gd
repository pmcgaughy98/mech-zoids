extends SceneTree
func _initialize() -> void:
 var script=load("res://tools/debug/rhino_painted_fx_2026_11_10/review.gd")
 if script==null or not script.can_instantiate():quit(1);return
 var scene:=Node3D.new();scene.set_script(script);root.add_child.call_deferred(scene)
