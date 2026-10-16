extends SceneTree
## Debug: what is inside each animation clip of the gorilla .glb, and does playing it move the bones?
func _initialize() -> void:
	var model: Node = (load("res://art/machines/ape_l/ape_l.glb") as PackedScene).instantiate()
	root.add_child(model)
	var player: AnimationPlayer = model.find_children("*", "AnimationPlayer", true, false)[0]
	var skel: Skeleton3D = model.find_children("*", "Skeleton3D", true, false)[0]
	for n in player.get_animation_list():
		var a := player.get_animation(n)
		var info := []
		for i in min(a.get_track_count(), 4):
			info.append("%s(%d keys)" % [a.track_get_path(i), a.track_get_key_count(i)])
		print("CLIP %s length %.2f tracks %d : %s" % [n, a.length, a.get_track_count(), ", ".join(info)])
	var b := skel.find_bone("upper_arm.R")
	print("rest rot upper_arm.R ", skel.get_bone_pose_rotation(b).get_euler())
	for n in ["punch", "death"]:
		player.play(n)
		player.seek(player.get_animation(n).length * 0.45, true)
		print("%s at 45%%: upper_arm.R %s  body pos %s" % [n, skel.get_bone_pose_rotation(b).get_euler(), skel.get_bone_pose_position(skel.find_bone("body"))])
	quit()
