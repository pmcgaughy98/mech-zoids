extends SceneTree
## The match check (Claude, 2026-11-04, game feel lane). Headless:
##   "<godot>" --headless --fixed-fps 60 --path . --script res://tools/debug/match_check.gd
## First it lets arena_play's 3 v 3 play itself for 130 s (waves, bots, towers) and checks what happened. Then it sets up
## one small scene per rule: tower targeting and switching, the warning, kit and attack damage and cooldowns, camps
## (aggro, leash, respawn), death and respawn, base healing, recall, and the win. The timers it shortens are MatchRules
## placeholders. It also listens for the sound lane's signal names.

const SOUND := ["tower_shot", "tower_shot_hit", "tower_destroyed", "core_destroyed", "wave_spawned", "minion_hit",
	"camp_aggro", "respawned", "recall_started", "recall_finished"]

var passed := 0
var failed := 0
var play: Node
var d: MatchDirector
var player: Node3D
var heard := {}
var won_heard: Variant = null


func ok(cond: bool, what: String) -> void:
	if cond:
		passed += 1
		print("PASS ", what)
	else:
		failed += 1
		print("FAIL ", what)


func frames(n: int) -> void:
	for i in n:
		await physics_frame


func secs(t: float) -> void:
	await frames(int(t * 60.0))


func _initialize() -> void:
	for s in SOUND:
		heard[s] = 0
	node_added.connect(_listen)
	_run.call_deferred()


func _listen(n: Node) -> void:
	for s in SOUND:
		if n.has_signal(s):
			n.connect(s, func() -> void: heard[s] += 1)
	if n.has_signal("match_ended"):
		n.connect("match_ended", func(won: bool) -> void: won_heard = won)


func _run() -> void:
	play = load("res://scenes/moba3d/arena_play.tscn").instantiate()
	root.add_child(play)
	await frames(2)
	d = play.director
	player = play.player
	var waited := 0
	while not d.ready_to_play and waited < 300:
		await physics_frame
		waited += 1
	ok(d.ready_to_play, "lanes ready on the nav mesh after %d frames" % waited)
	await _setup_checks()
	await _natural()
	await _quiet()
	await _towers()
	await _kit_and_attack()
	await _bodies()
	await _fog()
	await _camps()
	await _death_heal_recall()
	await _win()
	print("match_check: %d pass, %d fail" % [passed, failed])
	quit(1 if failed > 0 else 0)


func _length(p: PackedVector3Array) -> float:
	var l := 0.0
	for i in p.size() - 1:
		l += p[i].distance_to(p[i + 1])
	return l


func _setup_checks() -> void:
	for team in ["blue", "red"]:
		var l := _length(d.lanes[team])
		ok(l > 95.0 and l < 140.0, "%s lane on the nav mesh is %.1f m, gate to enemy core" % [team, l])
	ok(d.structures.size() == 4 and d.structures.values().all(func(s: MatchStructure) -> bool: return s.hp > 0.0),
		"two towers and two cores with health")
	ok(is_equal_approx(d.structures["BlueTower"].reach, 12.0), "tower range 12 m (placeholder)")
	var blue := d.machines.filter(func(m: Node3D) -> bool: return m.team == "blue")
	var bots := d.machines.filter(func(m: Node3D) -> bool: return m.bot)
	ok(d.machines.size() == 8 and blue.size() == 4 and bots.size() == 7, "4 v 4: eight machines, seven of them bots (red's cobra 2026-11-13, blue's bison 2026-11-16)")
	var kinds := d.machines.filter(func(m: Node3D) -> bool: return m.team == "red").map(func(m: Node3D) -> String: return MatchTeams.machine_kind(m))
	kinds.sort()
	ok(kinds == ["cobra", "gorilla", "kangaroo", "rhino"], "red fields the rhino, gorilla, kangaroo and cobra bots: %s" % [kinds])
	var blue_bots := blue.filter(func(m: Node3D) -> bool: return m.bot).map(func(m: Node3D) -> String: return MatchTeams.machine_kind(m))
	blue_bots.sort()
	ok(blue_bots == ["bison", "fennec", "gorilla"], "blue fields the gorilla, fennec and bison bots: %s" % [blue_bots])
	ok(player.team == "blue" and player.hp == MatchRules.machine_hp and not player.bot, "the player is blue, full health, not a bot")
	ok(d.camps.size() == 4 and d.camps.all(func(c: Dictionary) -> bool: return c["monster"] != null and c["monster"].alive),
		"four camps, each with a monster")
	ok(get_nodes_in_group("arena_pits").size() == 2, "both side pits are capture points (ArenaPit)")
	var units := get_nodes_in_group("map_units")
	ok(units.all(func(u: Node) -> bool: return u.has_meta("team") and u.has_meta("unit_kind")),
		"every map_units node has the map lane's team and unit_kind meta (%d nodes)" % units.size())
	ok(units.filter(func(u: Node) -> bool: return u.get_meta("is_player", false)).size() == 1, "exactly one is_player")


## The match plays itself for 130 s: nobody touches it.
func _natural() -> void:
	var far := {}
	var died := [0]
	d.unit_died.connect(func(_u: Node3D, _b: Node3D) -> void: died[0] += 1)
	while d.elapsed < 130.0:
		await frames(30)
		for m: Node3D in d.machines:
			if m.bot:
				far[m] = maxf(far.get(m, 0.0), MatchTeams.flat(m.global_position - d.spawns[m.team]).length())
	ok(d.waves_sent["blue"] == 5 and d.waves_sent["red"] == 5, "a wave every 30 s from each base: 5 each by 130 s")
	ok(heard["wave_spawned"] == 10, "wave_spawned heard once per wave per team (%d)" % heard["wave_spawned"])
	var c: Dictionary = d.first_clash
	var plaza := MatchTeams.flat((play.arena.get_node("Markers/Plaza") as Node3D).global_position)
	ok(not c.is_empty(), "the waves met")
	if not c.is_empty():
		var off := MatchTeams.flat(c["p"] - plaza).length()
		ok(off < 16.0, "the first wave fight is at the plaza: %.1f m from its middle" % off)
		var after: float = c["t"] - MatchRules.first_wave_at
		ok(after > 12.0 and after < 30.0, "it starts %.1f s after the first wave leaves" % after)
	ok(heard["minion_hit"] > 10, "minions trade shots (minion_hit %d)" % heard["minion_hit"])
	ok(died[0] > 6, "units died in the natural match (%d)" % died[0])
	var walked := far.values().filter(func(v: float) -> bool: return v > 20.0).size()
	var bot_n := d.machines.filter(func(m: Node3D) -> bool: return m.bot).size()  # 6 with red's cobra (2026-11-13)
	ok(walked == bot_n, "all %d bots walked out with their waves (%d went past 20 m)" % [bot_n, walked])
	var users := d.kit_uses.keys().filter(func(m: Node3D) -> bool: return m.bot).size()
	ok(users >= 3, "bots used their kits: %d bots, %d uses" % [users, d.kit_uses.values().reduce(func(a, b): return a + b, 0)])
	print("  natural: towers blue %.0f red %.0f, tower shots %s, feed %s" % [d.structures["BlueTower"].hp,
		d.structures["RedTower"].hp, d.tower_shots.slice(0, 8), play.hud.feed_lines()])


## Clears the lane for the set-up scenes: no minions, no more waves, every bot parked at its spawn, full health.
func _quiet() -> void:
	d.next_wave = INF
	d._releases.clear()
	for u in get_nodes_in_group("match_unit"):
		if u is MatchMinion and not (u is MatchMonster):
			u.queue_free()
	for m: Node3D in d.machines:
		if not m.alive:
			d._respawn(m)
		if m.bot:
			m.get_node("Bot").hold = true
		m.halt()
		m.global_position = d._spawn_slot(m)
		m.hp = m.max_hp
		m.cooldowns.clear()
	for s: MatchStructure in d.structures.values():
		s.hp = s.max_hp
	await frames(10)


func _red(kind: String) -> Node3D:
	for m: Node3D in d.machines:
		if m.team == "red" and MatchTeams.machine_kind(m) == kind:
			return m
	return null


func _towers() -> void:
	var tower: MatchStructure = d.structures["BlueTower"]
	var t := tower.global_position
	var rhino := _red("rhino")
	var m := d.spawn_minion("red", t + Vector3(0.5, 0, -6.0))
	m.path = PackedVector3Array()
	rhino.global_position = t + Vector3(-2.0, 0, -5.0)
	await secs(0.6)
	ok(tower.target == m, "the blue tower shoots the red minion first, with a red machine as close")
	player.global_position = t + Vector3(2.5, 0, -4.0)
	player.take_damage(10.0, rhino)
	await frames(3)
	ok(tower.target == rhino, "it switches to the red machine that hit the player under it")
	var hp: float = rhino.hp
	await secs(2.0)
	ok(rhino.hp < hp, "its bolts land on the machine (%.0f to %.0f)" % [hp, rhino.hp])
	ok(heard["tower_shot"] > 0 and heard["tower_shot_hit"] > 0, "tower_shot and tower_shot_hit heard")
	m.queue_free()
	rhino.global_position = d._spawn_slot(rhino)
	rhino.hp = rhino.max_hp
	# the warning: alone under the red tower
	var red_tower: MatchStructure = d.structures["RedTower"]
	player.hp = player.max_hp
	player.global_position = red_tower.global_position + Vector3(0, 0, 6.0)
	await secs(0.8)
	ok(red_tower.target == player and d.player_targeted_by() == red_tower and play.hud.warning,
		"the red tower aims at the player and the HUD warning is on")
	ok(red_tower._beam.visible, "the red beam from the tower shows")
	ok(player.hp < player.max_hp, "the player takes its bolts")
	player.global_position = d._spawn_slot(player)
	await secs(0.5)
	ok(not play.hud.warning, "the warning goes when the player leaves its range")
	player.hp = player.max_hp


func _kit_and_attack() -> void:
	var at := Vector3(-3.0, 0, 2.0)  # in the plaza, far from both towers
	player.global_position = at
	player.facing = Vector3(0, 0, -1)
	var m := d.spawn_minion("red", at + Vector3(0, 0, -1.4))
	m.path = PackedVector3Array()
	await frames(3)
	var kit: Node = player.get_node("Kit")
	kit.ground_pound()
	await secs(1.6)
	ok(m.hp <= MatchRules.minion_hp - MatchRules.kit_hit_damage + 0.1, "the rhino's ground pound takes kit damage off a red minion (%.0f)" % m.hp)
	ok(not player.slot_ready("2") and player.cooldowns["2"] > 0.0, "ground pound is on cooldown (%.1f s left, tier short)" % player.cooldowns["2"])
	var waited := 0.0
	while kit.current != "" and waited < 4.0:  # the tremor keeps stomping about 2.5 s (game feel lane, 2026-11-05)
		await secs(0.1)
		waited += 0.1
	var ev := InputEventKey.new()
	ev.physical_keycode = KEY_2
	ev.pressed = true
	Input.parse_input_event(ev)
	await frames(2)
	ok(kit.current == "", "key 2 does nothing while it cools down")
	var before := m.hp
	# The basic comes from the kit when it has one (the rhino's melee horn jab, 2 m, Rhino Session 2026-11-05): stand the
	# minion inside the machine's own reach and aim at it, as the mouse would.
	var reach: float = d.basic_range_of(player)
	var m_r: float = m.radius() if m.has_method("radius") else 0.5
	m.global_position = player.global_position + Vector3(0, 0, -(player.radius() + m_r + clampf(reach - 0.6, 0.3, 4.0)))
	m.global_position.z += MatchTeams.edge_distance(player, m) - clampf(reach - 0.6, 0.3, 4.0)  # by the measured edge distance, as the kit reads it
	await frames(2)
	player.aim_screen_override = player.get_viewport().get_camera_3d().unproject_position(m.global_position)
	player.attack_cd = 0.0
	var pre := "busy %s stunned %.2f cd %.2f current '%s' aim %s to %s edge %.2f hittable %s" % [player.busy, player.stunned, player.attack_cd, kit.current, player.aim_dir(), MatchTeams.flat(m.global_position - player.global_position).normalized(), MatchTeams.edge_distance(player, m), MatchTeams.hittable(m)]
	play.player_attack()
	var post := "cd after %.2f current '%s' action '%s'" % [player.attack_cd, kit.current, player.sprite.action]
	await secs(0.8)
	player.aim_screen_override = null
	print("space basic: ", pre, " | ", post)
	var kit_basic: bool = kit.has_method("basic_attack")
	ok(m.hp < before - 0.1 and (kit_basic or m.hp <= before - MatchRules.basic_damage + 0.1),
		"the basic attack (Space, %s, reach %.1f m) hits it for %.0f" % ["the kit's own" if kit_basic else "the stand-in", reach, before - m.hp])
	m.queue_free()
	player.cooldowns.clear()


## Body collision (MatchBodies): walks may not pass through other bodies, overlaps are eased apart, and a machine
## mid-ability holds its ground while the minion gives way.
func _bodies() -> void:
	var at := Vector3(-3.0, 0, 2.0)
	player.halt()
	player.global_position = at
	var m := d.spawn_minion("blue", at + Vector3(0, 0, -2.0))  # an ally: it stands still and does not fight
	m.path = PackedVector3Array()
	await frames(2)
	m.global_position = at + Vector3(0, 0, -2.0)
	var gap: float = player.radius() + m.radius()
	var closest := INF
	for i in 50:  # the machine walks straight at it, 0.1 m a frame (the bots walk this way)
		player._move_to(player.global_position + Vector3(0, 0, -0.1))
		await physics_frame
		closest = minf(closest, MatchTeams.flat(player.global_position - m.global_position).length())
	ok(closest >= gap - 0.03, "a walking machine never enters a minion (closest %.2f m, bodies %.2f m)" % [closest, gap])
	ok(player.global_position.z < m.global_position.z - 0.3, "and it walks round it instead of stopping (z %.2f past %.2f)" % [player.global_position.z, m.global_position.z])
	player.global_position = at
	m.global_position = at + Vector3(0, 0, 3.0)
	m.path = PackedVector3Array([at + Vector3(0, 0, -3.0)])
	m.path_index = 0
	closest = INF
	for i in 150:
		await physics_frame
		closest = minf(closest, MatchTeams.flat(player.global_position - m.global_position).length())
	ok(closest >= gap - 0.03, "a walking minion never enters the machine standing in its lane (closest %.2f m)" % closest)
	ok(m.path_index >= m.path.size(), "and gets past it to the end of its path")
	m.path = PackedVector3Array()
	player.global_position = at
	m.global_position = at + Vector3(0.1, 0, 0)
	await frames(1)
	var p0: Vector3 = player.global_position
	var m0 := m.global_position
	await secs(0.6)
	var apart := MatchTeams.flat(player.global_position - m.global_position).length()
	ok(apart >= gap - 0.03, "a minion dropped onto a machine is eased off it (%.2f m apart)" % apart)
	ok(p0.distance_to(player.global_position) < m0.distance_to(m.global_position), "the minion gives way more than the heavier machine (%.2f vs %.2f m)" % [m0.distance_to(m.global_position), p0.distance_to(player.global_position)])
	player.busy = true
	m.global_position = player.global_position + Vector3(0.1, 0, 0)
	await frames(1)
	p0 = player.global_position
	await secs(0.6)
	ok(p0.distance_to(player.global_position) < 0.001, "a machine mid-ability (busy) is not moved by the push")
	ok(MatchTeams.flat(player.global_position - m.global_position).length() >= gap - 0.03, "the minion moves the whole way instead")
	player.busy = false
	m.queue_free()
	await frames(2)


## Fog of war with the map lane's arena.vision: enemies the player's team cannot see are hidden (and lose their bar),
## buildings always show, and machines only pick targets their team can see.
func _fog() -> void:
	var vision: Variant = d.arena.get("vision")
	ok(vision != null and (vision as Object).has_method("can_see"), "the map lane's vision exists in the match")
	if vision == null:
		return
	ok(vision.get("fog_shown") == true, "the world dims outside blue's vision (fog_shown)")
	var at := Vector3(-3.0, 0, 2.0)
	player.global_position = at
	var rt: MatchStructure = d.structures["RedTower"]
	var rc: MatchStructure = d.structures["RedCore"]
	var deep := rt.global_position + MatchTeams.flat(rc.global_position - rt.global_position).normalized() * 4.0
	var near := d.spawn_minion("red", at + Vector3(2.5, 0, 0))
	var far := d.spawn_minion("red", deep)
	for m: MatchMinion in [near, far]:
		m.path = PackedVector3Array()
	await frames(2)
	near.global_position = at + Vector3(2.5, 0, 0)
	far.global_position = deep
	await secs(0.4)
	ok(near.seen and near.visible, "a red minion 2.5 m from the player is in view")
	ok(not far.seen and not far.visible, "a red minion behind the red tower, far from every blue unit, is hidden (%.0f m off)" % MatchTeams.flat(far.global_position - at).length())
	ok(rt.seen and rc.seen, "the red tower and core stay in view through the fog")
	ok(not d.team_sees("blue", far) and d.team_sees("red", far), "blue cannot target the hidden one; red's own side sees it")
	ok(d.pick_target(player, 500.0) != far, "the player's attack never picks the hidden minion")
	far.global_position = at + Vector3(-2.5, 0, 0)
	await secs(0.4)
	ok(far.seen and far.visible, "brought next to the player, it shows again")
	near.queue_free()
	far.queue_free()
	await frames(2)


func _camps() -> void:
	var c: Dictionary = d.camps[0]
	var mon: MatchMonster = c["monster"]
	var home: Vector3 = c["home"]
	var mon_r: float = mon.radius() if mon.has_method("radius") else 0.6
	# inside the machine's own basic reach: the rhino's jab is melee now (2 m edge to edge)
	player.global_position = mon.global_position + Vector3(player.radius() + mon_r + clampf(d.basic_range_of(player) - 0.6, 0.3, 3.0), 0, 0)
	await frames(2)
	player.attack_cd = 0.0
	d.basic_attack(player, mon)
	await secs(0.8)
	ok(mon.aggro == player and heard["camp_aggro"] == 1, "a hit pulls the camp monster onto the player (camp_aggro heard)")
	ok(mon.hp < mon.max_hp, "it took the hit")
	await secs(1.5)
	ok(player.hp < player.max_hp, "it fights back")
	player.global_position = d._spawn_slot(player)
	await secs(8.0)
	ok(not mon.resetting and MatchTeams.flat(mon.global_position - home).length() < 0.6 and mon.hp == mon.max_hp,
		"left past its leash it walks home and heals to full")
	MatchRules.monster_respawn = 2.0
	mon.take_damage(99999.0, player)
	await frames(2)
	ok(c["monster"] == null and play.hud.feed_lines().any(func(s: String) -> bool: return s.contains("cleared a camp")),
		"killed: the feed says the camp was cleared")
	await secs(2.5)
	ok(c["monster"] != null and c["monster"].alive and MatchTeams.flat(c["monster"].global_position - home).length() < 0.5,
		"the camp respawns at home")


func _death_heal_recall() -> void:
	MatchRules.respawn_time = 2.0
	var fennec := _red("kangaroo")  # red's third machine (the kangaroo replaced the fennec, 2026-11-11)
	player.global_position = Vector3(-3, 0, 2)
	player.hp = player.max_hp
	player.take_damage(99999.0, fennec)
	await frames(2)
	ok(not player.alive and not player.visible, "the player is destroyed and hidden")
	ok(play.hud.feed_lines().has("Red kangaroo destroyed Blue rhino"), "the kill feed: %s" % [play.hud.feed_lines()])
	var r0: int = heard["respawned"]
	await secs(2.4)
	ok(player.alive and player.visible and player.hp == player.max_hp, "back after the respawn timer, at full health")
	ok(MatchTeams.flat(player.global_position - d.spawns["blue"]).length() < 3.0 and heard["respawned"] == r0 + 1,
		"at base, and respawned heard")
	player.hp = player.max_hp * 0.5
	await secs(1.0)
	ok(player.hp > player.max_hp * 0.62, "base heals it (%.0f%% after 1 s from 50%%)" % (player.hp / player.max_hp * 100.0))
	MatchRules.recall_time = 1.5
	player.global_position = Vector3(-3, 0, 2)
	var own := {"started": 0, "finished": 0}  # the player's own signals: heard counts every machine, and a bot may recall too
	player.recall_started.connect(func() -> void: own.started += 1)
	player.recall_finished.connect(func() -> void: own.finished += 1)
	d.start_recall(player)
	await secs(1.8)
	ok(MatchTeams.flat(player.global_position - d.spawns["blue"]).length() < 3.0, "recall (B) brings it home")
	ok(own.started == 1 and own.finished == 1, "recall_started and recall_finished heard (player %d/%d, all machines %d/%d)" % [own.started, own.finished, heard["recall_started"], heard["recall_finished"]])
	player.global_position = Vector3(-3, 0, 2)
	d.start_recall(player)
	await secs(0.5)
	player.take_damage(5.0, fennec)
	await secs(1.5)
	ok(not d.recalls.has(player) and MatchTeams.flat(player.global_position - Vector3(-3, 0, 2)).length() < 1.0,
		"a hit cancels the recall")


func _win() -> void:
	var tower: MatchStructure = d.structures["RedTower"]
	var core: MatchStructure = d.structures["RedCore"]
	core.take_damage(500.0, player)
	ok(core.hp == core.max_hp and not core.can_be_hit(), "the red core takes nothing while its tower stands")
	tower.take_damage(99999.0, player)
	await frames(2)
	ok(not tower.alive and heard["tower_destroyed"] == 1 and core.can_be_hit(), "the tower falls and the core opens")
	core.take_damage(99999.0, player)
	await frames(2)
	ok(d.winner == "blue" and MatchDirector.over and won_heard == true and heard["core_destroyed"] == 1,
		"the core falls: blue wins, match_ended(true) and core_destroyed heard")
	var m: Node3D = d.machines.filter(func(x: Node3D) -> bool: return x.team == "red")[0]
	var p: Vector3 = m.global_position
	m.get_node("Bot").hold = false
	await secs(1.0)
	ok(m.global_position.distance_to(p) < 0.01, "everything stops after the win")
