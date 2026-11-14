extends SceneTree
## Times arena_play's push demo headless before recording it (Claude, 2026-11-04, game feel lane):
##   "<godot>" --headless --fixed-fps 60 --path . --script res://tools/debug/push_probe.gd
## Every 2 s: match time, minions per team, the player's spot, both towers' health and aim.

func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var play: Node = load("res://scenes/moba3d/arena_play.tscn").instantiate()
	root.add_child(play)
	await physics_frame
	play._push_demo()
	var d: MatchDirector = play.director
	var last := -1
	while play._t < 74.0:
		await physics_frame
		var s := int(d.elapsed)
		if s % 2 == 0 and s != last:
			last = s
			var mins := {"blue": 0, "red": 0}
			for u in get_nodes_in_group("match_unit"):
				if u.get("kind") == "minion":
					mins[u.team] += 1
			var rt: MatchStructure = d.structures["RedTower"]
			var p: Vector3 = play.player.global_position
			print("t %2d  minions b%d r%d  player (%.0f, %.0f) hp %.0f  red tower %.0f aim %s  clash %s" % [s, mins["blue"],
				mins["red"], p.x, p.z, play.player.hp, rt.hp, rt.target.get("kind") if rt.target else "-",
				"%.1f" % d.first_clash["t"] if not d.first_clash.is_empty() else "-"])
	print("feed: ", play.hud.feed_lines())
	quit()
