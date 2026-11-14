extends SceneTree
## How long a match runs with all six machines on bots (map design lane, 2026-11-06). Answers "our own match length"
## in docs/plan/moba-map-skillup-2026-11-05.md, which open choice 2 (one tower or two) and the plaza beacon (up at
## 4:00) both wait on. Headless, and needs no other Godot running:
## Godot --headless --fixed-fps 60 --path . -s res://tools/map/match_length_sim.gd -- [cap minutes] [runs]
## The player's machine plays itself through a MatchBot, as arena_play's push demo does. Each run gets its own seed.
## It logs when towers and cores fall, beacon and pit takes, and deaths, then a one-line summary per run. Edits
## nothing. Bots walk the lane through the plaza, so a beacon take here means a bot walked over it, not that it
## went for it (whether bots contest objectives is still Preston's call).

var _ev: Array = []
var _d = null


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var cap: float = float(args[0]) * 60.0 if args.size() > 0 else 900.0
	var runs: int = int(args[1]) if args.size() > 1 else 1
	for r in runs:
		await _one(r, cap)
	quit(0)


func _clock() -> String:
	var s := int(_d.elapsed) if _d else 0
	return "%d:%02d" % [s / 60, s % 60]


func _log(what: String) -> void:
	var line := "%s %s" % [_clock(), what]
	_ev.append(line)
	print("    ", line)


func _one(r: int, cap: float) -> void:
	seed(7001 + r * 101)
	_ev.clear()
	var wall := Time.get_ticks_msec()
	var play: Node = load("res://scenes/moba3d/arena_play.tscn").instantiate()
	root.add_child(play)
	for i in 2:
		await process_frame
	_d = play.director
	for i in 600:
		if _d.ready_to_play:
			break
		await physics_frame
	var p = play.player
	p.bot = true
	var b := MatchBot.new()
	b.name = "Bot"
	b.director = _d
	p.add_child(b)
	print("run %d (seed %d), player %s on %s" % [r, 7001 + r * 101, p.name, p.team])

	var deaths := {"blue": 0, "red": 0}
	for m in _d.machines:
		var team: String = m.team
		m.died.connect(func(_by) -> void: deaths[team] += 1)
	var takes: Array = []
	for bn in get_nodes_in_group("arena_beacons"):
		bn.beacon_up.connect(func() -> void: _log("beacon up"))
		bn.beacon_taken.connect(func(t: String) -> void:
			takes.append(t)
			_log("beacon taken by " + t))
	var st := {"pits": 0, "winner": ""} # lambdas capture ints and strings by value, so these live in a dict
	for pn in get_nodes_in_group("arena_pits"):
		var pname: String = pn.name
		pn.pit_taken.connect(func(t: String) -> void:
			st.pits += 1
			_log("%s taken by %s" % [pname, t]))
	var ptm: String = p.team
	_d.match_ended.connect(func(won: bool) -> void:
		st.winner = ptm if won else ("red" if ptm == "blue" else "blue"))

	var low := {"blue": 1.0, "red": 1.0} # each tower's lowest health share, to tell a stalled lane from a tower nothing hurts
	var towers := {"blue": _d.towers_standing("blue"), "red": _d.towers_standing("red")}
	var first_tower := ""
	var minute := 0
	while not _d.over and _d.elapsed < cap:
		await physics_frame
		for team in ["blue", "red"]:
			var n: int = _d.towers_standing(team)
			if n < towers[team]:
				towers[team] = n
				_log("%s tower down" % team)
				if first_tower == "":
					first_tower = "%s at %s" % [team, _clock()]
			var tw = _d.structures.get(team.capitalize() + "Tower")
			if tw != null and is_instance_valid(tw) and float(tw.max_hp) > 0.0:
				low[team] = minf(low[team], maxf(float(tw.hp), 0.0) / float(tw.max_hp))
		if int(_d.elapsed / 60.0) > minute:
			minute = int(_d.elapsed / 60.0)
			print("    %s  deaths blue %d red %d  tower low blue %d%% red %d%%" % [_clock(), deaths.blue, deaths.red,
				roundi(low.blue * 100), roundi(low.red * 100)])
	if _d.over:
		_log("match over, %s wins" % (st.winner if st.winner != "" else "?"))
	var secs := (Time.get_ticks_msec() - wall) / 1000.0
	print("run %d: %s | first tower: %s | towers' lowest blue %d%% red %d%% | beacon takes %s | pit takes %d | deaths blue %d red %d | %.0f s wall" % [
		r, ("ended %s, %s won" % [_clock(), st.winner]) if _d.over else ("no winner by %s" % _clock()),
		first_tower if first_tower != "" else "none", roundi(low.blue * 100), roundi(low.red * 100), str(takes), st.pits,
		deaths.blue, deaths.red, secs])
	play.queue_free()
	_d = null
	for i in 3:
		await process_frame
