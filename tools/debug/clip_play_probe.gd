extends SceneTree
## Debug: does play() advance the clips frame by frame in the lab (no seeking)?
func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	var lab: Node = load("res://scenes/model_lab_3d.tscn").instantiate()
	root.add_child(lab)
	current_scene = lab
	await process_frame
	var player: AnimationPlayer = lab.model.find_children("*", "AnimationPlayer", true, false)[0]
	var skel: Skeleton3D = lab.model.find_children("*", "Skeleton3D", true, false)[0]
	var b := skel.find_bone("upper_arm.R")
	print("PROBE callback mode %d, active %s, speed %.2f, playing %s %s" % [player.callback_mode_process, player.active, player.speed_scale, player.is_playing(), player.current_animation])
	lab.play_clip("punch")
	for k in 60:
		await process_frame
		if k % 10 == 0:
			print("PROBE frame %d anim %s pos %.3f arm %s" % [k, player.current_animation, player.current_animation_position, skel.get_bone_pose_rotation(b).get_euler()])
	quit()
