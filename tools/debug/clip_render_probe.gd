extends SceneTree
## Debug: render the lab at rest and mid-punch and report how many pixels differ, plus mesh/skeleton wiring.
func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	var lab: Node = load("res://scenes/model_lab_3d.tscn").instantiate()
	root.add_child(lab)
	await process_frame
	var mi: MeshInstance3D = lab.model.find_children("*", "MeshInstance3D", true, false)[0]
	print("PROBE mesh skeleton path '%s' skin %s" % [mi.skeleton, mi.skin])
	var player: AnimationPlayer = lab.model.find_children("*", "AnimationPlayer", true, false)[0]
	player.play("idle")
	player.seek(0.0, true)
	for k in 10: await process_frame
	var a := root.get_texture().get_image()
	player.play("punch")
	player.seek(0.55, true)
	player.pause()
	for k in 10: await process_frame
	var b := root.get_texture().get_image()
	var diff := 0
	for y in range(0, a.get_height(), 4):
		for x in range(0, a.get_width(), 4):
			if a.get_pixel(x, y).is_equal_approx(b.get_pixel(x, y)) == false and absf(a.get_pixel(x, y).v - b.get_pixel(x, y).v) > 0.08:
				diff += 1
	print("PROBE pixels changed between rest and mid-punch: %d of %d sampled" % [diff, (a.get_height() / 4) * (a.get_width() / 4)])
	a.save_png("res://docs/art/3d/probe_rest.png")
	b.save_png("res://docs/art/3d/probe_punch.png")
	quit()
