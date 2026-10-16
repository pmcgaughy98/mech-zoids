extends SceneTree
## Records the view lab with the camera orbiting, for showing (Claude, 2026-10-11).
##   Godot --path . --write-movie view_lab.avi --fixed-fps 30 --script res://tools/debug/view_lab_record.gd
func _initialize() -> void:
	_run.call_deferred()
func _run() -> void:
	var lab: Node = load("res://scenes/view_lab.tscn").instantiate()
	root.add_child(lab)
	current_scene = lab
	for k in 30:
		await process_frame
	for step in 8:   # eight 45-degree turns, a pause on each
		lab.turn(1)
		for k in 30:
			await process_frame
	lab.orbit = true   # then a smooth orbit
	for k in 240:
		await process_frame
	quit()
