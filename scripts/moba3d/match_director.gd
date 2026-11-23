class_name MatchDirector
extends Node3D
## The match in arena_play (Claude, 2026-11-04, game feel lane; Mech-Zoids' brief for Preston's "sel-out moba map. Hook it
## up so it feels legit"). Owns the waves, towers and cores, jungle camps, death and respawn, base healing, recall, the
## bots and the win. Ported from the 2D skeleton (scripts/moba/moba_match.gd and lane_spawner.gd). Layout from the map
## lane's 3 v 3 one-lane proposal; their markers and LANE line, never their Built nodes. Every number: MatchRules.
##
## Signals for the sound lane (their names; MapAudio finds the emitters by name, also at runtime):
##   towers: tower_shot, tower_destroyed; tower_shot_hit from a short-lived node at the impact
##   cores: core_destroyed     wave gates: wave_spawned     minions: minion_hit     camp monsters: camp_aggro
##   machines: respawned, recall_started, recall_finished     this node: match_ended(won)
## For the HUD and the map lane: unit_died(unit, by), feed(text, colour), match_over(winner).

static var over := false ## true once a core has fallen: everything stops

signal match_ended(won: bool) ## the sound lane's name: true when the player's team won
signal match_over(winner: String)
signal unit_died(unit: Node3D, by: Node3D)
signal feed(text: String, colour: Color)

class Gate extends Node3D:
	signal wave_spawned ## the sound lane's name: once per wave per team, where the minions leave the base

## Who plays besides the player: the three machines that exist. A pick until Preston sets the teams.
const BOT_ROSTER := {"blue": ["gorilla", "fennec", "bison"], "red": ["rhino", "gorilla", "kangaroo", "cobra"]} ## blue: the bison added (Preston, 2026-11-16: "Yes, bison bots"; blue so the match is 4 v 4). red: the kangaroo in place of the fennec (Preston, 2026-11-11: "Red, replace fennec"); the cobra added (Preston, 2026-11-13: "The cobra isn't on BOT_ROSTER yet, so add it"; red was the cobra 3D lane's pick). No cobra kit in code yet: it plays as a plain machine in the cobra's body.
const SLOTS := [Vector3(0, 0, 0), Vector3(-2.6, 0, 0), Vector3(2.6, 0, 0), Vector3(-5.2, 0, 0)] ## where a team's machines stand at spawn (the 4th for red's cobra, 2026-11-13)

var arena: Node3D
var player: Node3D
var machines: Array = []
var structures := {} ## "BlueTower" -> MatchStructure
var lanes := {} ## team -> PackedVector3Array, its gate to the enemy core, on the nav mesh
var gates := {} ## team -> Gate
var spawns := {} ## team -> Vector3
var camps: Array = [] ## {marker, home, monster, back_at}
var elapsed := 0.0 ## match seconds, counted from the moment the lanes are ready
var next_wave := 0.0
var waves_sent := {"blue": 0, "red": 0}
var winner := ""
var ready_to_play := false
var respawn_at := {} ## machine -> the match second it comes back
var recalls := {} ## machine -> seconds channelled so far
var first_clash := {} ## {"t", "p"}: when and where two waves first traded shots (the checks read it)
var kit_uses := {} ## machine -> kit uses (the checks read it)
var tower_shots: Array = [] ## the kind of each thing a tower shot at, in order (the checks read it)
var _kits := {} ## machine -> the kit its used(slot) is connected through
var _releases: Array = [] ## minions waiting to leave a gate: {t, team, first}
var _fog_t := 0.0
var _nav_tries := 0


func setup(a: Node3D, human: Node3D) -> void:
	over = false
	arena = a
	player = human
	add_to_group("match_director") ## the map lane's plaza beacon reads elapsed and ready_to_play from here
	_connect_beacons()
	_connect_beacons.call_deferred()  # again once the whole arena is in the tree
	for team in ["blue", "red"]:
		spawns[team] = _marker_pos(team.capitalize() + "Spawn")
		for kind in ["tower", "core"]:
			var s := MatchStructure.new()
			s.team = team
			s.kind = kind
			s.marker = team.capitalize() + kind.capitalize()
			s.name = s.marker
			s.director = self
			s.arena = arena
			var mk := _marker(s.marker)
			s.body_r = float(mk.get_meta("radius", 1.4 if kind == "tower" else 2.5)) if mk != null else 1.4
			s.reach = float(mk.get_meta("range", MatchRules.tower_range)) if mk != null else MatchRules.tower_range
			s.position = _marker_pos(s.marker)
			add_child(s)
			s.fell.connect(_on_structure_fell)
			s.tower_shot.connect(func() -> void: tower_shots.append(str(s.target.get("kind")) if s.target != null else ""))
			structures[s.marker] = s
		var g := Gate.new()
		g.name = team.capitalize() + "Gate"
		add_child(g)
		gates[team] = g
		var pts := _lane_points(team)
		g.position = pts[0]
	for t in ["Blue", "Red"]:
		for i in [1, 2]:
			var n := "%sCamp%d" % [t, i]
			if _marker(n) != null:
				var c := {"marker": n, "home": _marker_pos(n), "monster": null, "back_at": -1.0}
				camps.append(c)
				_spawn_monster(c)
	player.global_position = spawns["blue"]
	for team in ["blue", "red"]:  # bots first: each is a copy of the player's machine before the match touches it
		var i := 1 if team == "blue" else 0
		for kind in BOT_ROSTER[team]:
			_make_bot(team, kind, i)
			i += 1
	player.set_meta("slot", 0)
	_enlist(player, "blue", false)


func _marker(n: String) -> Node3D:
	return arena.get_node_or_null("Markers/" + n) as Node3D


func _marker_pos(n: String) -> Vector3:
	var m := _marker(n)
	if m != null:
		return MatchTeams.flat(m.global_position)
	for f in arena.get("features"):  # the map lane's features list, if a marker is missing
		if str(f.get("name")).replace(" ", "").to_lower() == n.to_lower():
			return Vector3(f["p"].x, 0.0, f["p"].y)
	return Vector3.ZERO


## The lane's centre line (the map lane's LANE, blue core to red core) for a team: its gate first, the enemy core last.
func _lane_points(team: String) -> Array:
	var k: Dictionary = arena.get_script().get_script_constant_map()
	var line: Array = k.get("LANE", [Vector2(0, 56), Vector2(0, -56)])
	var pts: Array = []
	for p: Vector2 in line:
		pts.append(Vector3(p.x, 0.0, p.y))
	if team == "red":
		pts.reverse()
	var core := _marker_pos(team.capitalize() + "Core")
	var out: Vector3 = (pts[1] - pts[0]).normalized()
	var core_r: float = structures[team.capitalize() + "Core"].body_r if structures.has(team.capitalize() + "Core") else 2.5
	pts[0] = core + out * (core_r + 2.0)  # the gate: just in front of the core, toward the lane
	return pts


## The same line walked on the nav mesh, leg by leg, so minions follow the lane and not a jungle shortcut.
func _lane(team: String) -> PackedVector3Array:
	var out := PackedVector3Array()
	var map := get_world_3d().navigation_map
	if NavigationServer3D.map_get_iteration_id(map) == 0:
		return out
	var pts := _lane_points(team)
	for i in pts.size() - 1:
		var seg := NavigationServer3D.map_get_path(map, pts[i], pts[i + 1], true)
		if seg.size() < 2:
			return PackedVector3Array()
		if out.size() > 0:
			seg = seg.slice(1)
		out.append_array(seg)
	return out


func _physics_process(delta: float) -> void:
	if not ready_to_play:
		_try_lanes()
		return
	if over:
		return
	elapsed += delta
	if elapsed >= next_wave:
		next_wave += MatchRules.wave_interval
		for team in ["blue", "red"]:
			for i in MatchRules.wave_size:
				_releases.append({"t": elapsed + i * MatchRules.wave_stagger, "team": team, "first": i == 0, "power": 1.0 + MatchRules.pit_wave_bonus * ArenaPit.held(get_tree(), team)})
			waves_sent[team] += 1
	for r in _releases.duplicate():
		if elapsed >= r["t"]:
			_releases.erase(r)
			spawn_minion(r["team"], gates[r["team"]].global_position, r.get("power", 1.0))
			if r["first"]:
				gates[r["team"]].wave_spawned.emit()
	_machines_tick(delta)
	MatchBodies.separate(get_tree(), delta)
	for c in camps:
		if c["back_at"] >= 0.0 and elapsed >= c["back_at"]:
			_spawn_monster(c)
	_fog_tick(delta)


func _try_lanes() -> void:
	_nav_tries += 1
	var blue := _lane("blue")
	var red := _lane("red")
	if blue.size() >= 2 and red.size() >= 2:
		lanes = {"blue": blue, "red": red}
	elif _nav_tries > 240:  # no nav mesh after 4 s: the centre line itself
		push_warning("match: no nav path for the lanes, minions walk the LANE centre line")
		lanes = {"blue": PackedVector3Array(_lane_points("blue")), "red": PackedVector3Array(_lane_points("red"))}
	else:
		return
	ready_to_play = true
	next_wave = MatchRules.first_wave_at


# ---- units ----------------------------------------------------------------------------------------------------------------

func spawn_minion(team: String, at: Vector3, power := 1.0) -> MatchMinion:
	var m := MatchMinion.new()
	m.team = team
	m.power = power  # 1 + pit_wave_bonus per side pit the team held when the wave formed
	m.path = lanes.get(team, PackedVector3Array())
	m.director = self
	m.position = at + Vector3(randf_range(-0.6, 0.6), 0, randf_range(-0.6, 0.6))
	add_child(m)
	m.unit_died.connect(_on_unit_died)
	return m


func _spawn_monster(c: Dictionary) -> void:
	var m := MatchMonster.new()
	m.home = c["home"]
	m.position = c["home"]
	m.camp = c["marker"]
	m.director = self
	add_child(m)
	m.unit_died.connect(_on_unit_died)
	c["monster"] = m
	c["back_at"] = -1.0


func _enlist(m: Node3D, team: String, is_bot: bool) -> void:
	m.team = team
	m.bot = is_bot
	m.max_hp = MatchRules.machine_hp
	m.hp = m.max_hp
	m.alive = true
	for g in ["match_unit", "map_units", "vision_sources"]:
		m.add_to_group(g)
	m.set_meta("team", team)
	m.set_meta("unit_kind", "machine")
	m.set_meta("vision_radius", MatchRules.vision_machine)
	if m == player:
		m.set_meta("is_player", true)
	m.died.connect(_on_machine_died.bind(m))
	m.damaged.connect(_on_machine_damaged.bind(m))
	machines.append(m)
	if m != player:
		var ring := m.get_node_or_null("Ring") as MeshInstance3D
		var pm: PrimitiveMesh = (ring.mesh as PrimitiveMesh) if ring != null else null
		if pm != null and pm.material is StandardMaterial3D:
			var mat := (pm.material as StandardMaterial3D).duplicate() as StandardMaterial3D
			mat.albedo_color = MatchTeams.COLOURS[team] * 1.3
			ring.material_override = mat


func _make_bot(team: String, kind: String, i: int) -> void:
	var m: Node3D = player.duplicate()
	m.name = team.capitalize() + kind.capitalize()
	m.publish_machine_pos = false
	m.set_meta("is_player", false)
	m.set_meta("slot", i)
	for c in m.get_children():  # a copy made mid-match must not carry the player's live effects (a raised hex shield, the
		if c is HexShield or c is Fx3D.FlatFx:  # silverback ring): copies come up empty. Game feel lane, 2026-11-09.
			m.remove_child(c)
			c.free()
	arena.add_child(m)
	match kind:
		"gorilla":
			load("res://scripts/moba3d/arena_gorilla_kit.gd").install_arena(m)
		"fennec":
			FennecKit.install(m)
		"kangaroo":
			KangarooKit.install(m)
		"hummingbird":
			load("res://scripts/moba3d/hummingbird_kit.gd").install(m)  # no class_name on that kit (2026-11-06)
		"lobster":
			load("res://scripts/moba3d/lobster_kit.gd").install(m)  # by path, as in arena_play (2026-11-06)
		"bison":
			load("res://scripts/moba3d/bison_kit.gd").install(m)  # the Whistle Stop kit, by path as in arena_play
			m.sprite.size_class = "L"
	m.apply_size_class()
	var mine := MatchTeams.team_of(player)  # the player is enlisted after the bots, so "" means blue
	m.use_model(kind, team != (mine if mine != "" else "blue"))  # the kind's rigged 3D body, else its sprite (game feel lane, 2026-11-09)
	m.global_position = spawns[team] + SLOTS[i]
	m.facing = Vector3(0, 0, -1) if team == "blue" else Vector3(0, 0, 1)
	_enlist(m, team, true)
	var b := MatchBot.new()
	b.name = "Bot"
	b.director = self
	b.side = SLOTS[i].x * 0.6
	m.add_child(b)


func _spawn_slot(m: Node3D) -> Vector3:
	return spawns[m.team] + SLOTS[int(m.get_meta("slot", 0)) % SLOTS.size()]


func towers_standing(team: String) -> int:
	var n := 0
	for s: MatchStructure in structures.values():
		if s.team == team and s.kind == "tower" and s.alive:
			n += 1
	return n


## The tower aiming at the player right now, or null (the HUD's warning).
func player_targeted_by() -> MatchStructure:
	for s: MatchStructure in structures.values():
		if s.kind == "tower" and s.alive and s.target == player and player.alive:
			return s
	return null


func note_clash(a: Node3D, t: Node3D) -> void:
	if first_clash.is_empty() and t.get("kind") == "minion":
		first_clash = {"t": elapsed, "p": a.global_position}


## The best thing for a machine to shoot within reach: closest by edge distance, things in front of `facing` first.
## Enemy units, camp monsters and hittable buildings; never through a wall.
func pick_target(m: Node3D, reach: float, facing := Vector3.ZERO) -> Node3D:
	var best: Node3D = null
	var best_score := INF
	for u: Node3D in get_tree().get_nodes_in_group("match_unit"):
		if u == m or not MatchTeams.is_enemy(u, m) or not MatchTeams.hittable(u):
			continue
		var d := MatchTeams.edge_distance(m, u)
		if d > reach or not team_sees(MatchTeams.team_of(m), u):
			continue
		var building: bool = u.get("kind") == "tower" or u.get("kind") == "core"
		if not building and not MatchTeams.clear_line(m, m.global_position, u.global_position, 0.8):
			continue
		var score := d
		if facing != Vector3.ZERO:
			var to := MatchTeams.flat(u.global_position - m.global_position).normalized()
			score += rad_to_deg(facing.angle_to(to)) / 90.0 * 2.0
		if score < best_score:
			best = u
			best_score = score
	return best


## The basic attack. A kit with basic_attack(target) -> bool fires its own (the squirrel's darts and Hearsay count live
## in the kit): target is null for the player, who aims with the mouse, or a bot's pick. The kit may set basic_cooldown,
## else MatchRules.basic_cooldown. The director keeps the gates and the cooldown either way. Without a kit basic, the
## stand-in: a test shot, the same for every machine, until Preston defines real ones.
func basic_attack(m: Node3D, target: Node3D) -> bool:
	if m.has_meta("held_by"):return false
	if over or not m.alive or m.attack_cd > 0.0 or m.busy or m.stunned > 0.0:
		return false
	var kit := m.get_node_or_null("Kit")
	if kit != null and kit.has_method("basic_attack"):
		if target != null and not MatchTeams.hittable(target):
			return false
		if not kit.basic_attack(target):
			return false
		m.attack_cd = basic_cooldown_of(m)
		if recalls.has(m):
			_end_recall(m, false)
		return true
	if not MatchTeams.hittable(target):
		return false
	m.attack_cd = MatchRules.basic_cooldown
	var to := MatchTeams.flat(target.global_position - m.global_position)
	if to.length() > 0.01:
		m.facing = to.normalized()
	var s := TestShot.fire(m.get_parent(), m.global_position, target.global_position, m.team == "red", target)
	s.team = m.team
	s.hp_damage = MatchRules.basic_damage
	s.source = m
	s.reach = MatchRules.basic_range + 3.0
	if recalls.has(m):
		_end_recall(m, false)
	return true


## A machine's basic reach (edge to edge, MatchTeams.edge_distance) and cooldown: its kit's basic_range and
## basic_cooldown when the kit has its own basic_attack, else the stand-in's (MatchRules.basic_range, basic_cooldown).
## The bots walk into this reach before they swing, so a melee kit's bots close in; the HUD's basic sweep can read it.
func basic_range_of(m: Node3D) -> float:
	var kit := m.get_node_or_null("Kit")
	return float(kit.get("basic_range")) if kit != null and kit.has_method("basic_attack") and "basic_range" in kit else MatchRules.basic_range


func basic_cooldown_of(m: Node3D) -> float:
	var kit := m.get_node_or_null("Kit")
	var cd := float(kit.get("basic_cooldown")) if kit != null and kit.has_method("basic_attack") and "basic_cooldown" in kit else MatchRules.basic_cooldown
	if m.has_method("rallied") and m.rallied():
		cd /= maxf(float(m.get("rally_rate")), 0.1)  # the bison's Eruption rally (2026-11-14)
	return cd


func _connect_beacons() -> void:
	for b in get_tree().get_nodes_in_group("arena_beacons"):
		if b.has_signal("beacon_taken") and not b.beacon_taken.is_connected(_on_beacon_taken):
			b.beacon_taken.connect(_on_beacon_taken)


## The plaza beacon (map lane, 2026-11-05): the team that takes it switches the other team's tower off for
## MatchRules.beacon_tower_off seconds. A tower already down: nothing, since cores don't shoot.
func _on_beacon_taken(team: String) -> void:
	var other := "red" if team == "blue" else "blue"
	for s: MatchStructure in structures.values():
		if s.team == other and s.kind == "tower" and s.alive:
			s.switch_off(MatchRules.beacon_tower_off)


# ---- machines: cooldowns, death and respawn, base healing, recall ------------------------------------------------------

func _machines_tick(delta: float) -> void:
	for m: Node3D in machines:
		var kit := m.get_node_or_null("Kit")
		if kit != null and _kits.get(m) != kit:
			_kits[m] = kit
			if kit.has_signal("used"):
				kit.used.connect(_on_kit_used.bind(m))
		if not m.alive:
			if elapsed >= float(respawn_at.get(m, INF)):
				_respawn(m)
			continue
		if MatchTeams.flat(m.global_position - spawns[m.team]).length() <= MatchRules.base_heal_radius and m.hp < m.max_hp:
			m.hp = minf(m.max_hp, m.hp + m.max_hp * MatchRules.base_heal_share * delta)
		if recalls.has(m):
			if m.speed > 0.05 or m.busy or m.stunned > 0.0 or m._forced():
				_end_recall(m, false)
			else:
				recalls[m] += delta
				if recalls[m] >= MatchRules.recall_time:
					_end_recall(m, true)


func _on_kit_used(slot: String, m: Node3D) -> void:
	m.cooldowns[slot] = MatchRules.cooldown(MatchTeams.machine_kind(m), slot)
	kit_uses[m] = int(kit_uses.get(m, 0)) + 1
	if recalls.has(m):
		_end_recall(m, false)


func start_recall(m: Node3D) -> void:
	if over or not m.alive or recalls.has(m):
		return
	recalls[m] = 0.0
	m.recall_started.emit()
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = MatchTeams.COLOURS[m.team].lightened(0.3)
	mat.albedo_color.a = 0.7
	var ring := TorusMesh.new()
	ring.inner_radius = 1.0
	ring.outer_radius = 1.15
	ring.rings = 24
	ring.ring_segments = 4
	ring.material = mat
	var mi := MeshInstance3D.new()
	mi.name = "RecallRing"
	mi.mesh = ring
	mi.scale = Vector3(1, 0.05, 1)
	mi.position.y = 0.05
	m.add_child(mi)
	var tw := mi.create_tween().set_loops()
	tw.tween_property(mi, "position:y", 2.2, 0.8)
	tw.tween_property(mi, "position:y", 0.05, 0.0)


func _end_recall(m: Node3D, done: bool) -> void:
	recalls.erase(m)
	var ring := m.get_node_or_null("RecallRing")
	if ring != null:
		ring.queue_free()
	if done:
		m.halt()
		m.global_position = _spawn_slot(m)
		m.recall_finished.emit()
		if m == player:
			_snap_camera()


func _on_machine_damaged(_amount: float, by: Node3D, victim: Node3D) -> void:
	if recalls.has(victim):
		_end_recall(victim, false)
	if by == null or not is_instance_valid(by) or by.get("kind") != "machine" or not MatchTeams.is_enemy(by, victim):
		return
	for s: MatchStructure in structures.values():  # an enemy machine hit an allied machine under our tower
		if s.kind == "tower" and s.alive and s.team == victim.team:
			if MatchTeams.flat(by.global_position - s.global_position).length() <= s.reach \
					and MatchTeams.flat(victim.global_position - s.global_position).length() <= s.reach:
				s.switch_to(by)


func _on_machine_died(by: Node3D, m: Node3D) -> void:
	respawn_at[m] = elapsed + MatchRules.respawn_time
	if recalls.has(m):
		_end_recall(m, false)
	var hold := float(m.get("death_hold")) if m.get("death_hold") != null else 0.0
	if hold > 0.0:  # the wreck plays its Death clip first (game feel lane, 2026-11-10)
		get_tree().create_timer(hold).timeout.connect(_hide_wreck.bind(m))
	else:
		m.visible = false
	if m.bot:
		m.move_override = Vector3.ZERO
	for g in ["map_units", "vision_sources"]:
		m.remove_from_group(g)
	Fx3D.spawn(m.get_parent(), "impact_puff", m.global_position, 1.0)
	_say("%s destroyed %s" % [_killer_name(by), MatchTeams.unit_name(m)], by)
	unit_died.emit(m, by)


func _hide_wreck(m: Node3D) -> void:
	if is_instance_valid(m) and not m.alive:
		m.visible = false


func _respawn(m: Node3D) -> void:
	respawn_at.erase(m)
	m.halt()
	m.global_position = _spawn_slot(m)
	m.facing = Vector3(0, 0, -1) if m.team == "blue" else Vector3(0, 0, 1)
	m.hp = m.max_hp
	m.alive = true
	m.stunned = 0.0
	m.slowed = 0.0
	m.slows.clear()
	m.grounded = 0.0
	m.boosts.clear()
	m.taunted = 0.0
	m.visible = m.seen
	for g in ["map_units", "vision_sources"]:
		m.add_to_group(g)
	m.respawned.emit()
	if m == player:
		_snap_camera()


func _snap_camera() -> void:
	var cam := arena.get_node_or_null("Camera")
	if cam != null and cam.has_method("snap"):
		cam.snap()


# ---- deaths, the kill feed and the win -------------------------------------------------------------------------------

func _killer_name(by: Node3D) -> String:
	if by == null or not is_instance_valid(by):
		return "Something"
	if by.get("kind") == "minion":
		return MatchTeams.team_of(by).capitalize() + " minions"
	return MatchTeams.unit_name(by)


func _say(text: String, by: Node3D) -> void:
	feed.emit(text, MatchTeams.COLOURS.get(MatchTeams.team_of(by), Color.WHITE))


func _on_unit_died(u: Node3D, by: Node3D) -> void:
	unit_died.emit(u, by)
	if u is MatchMonster:
		for c in camps:
			if c["monster"] == u:
				c["monster"] = null
				c["back_at"] = elapsed + MatchRules.monster_respawn
		if by != null and is_instance_valid(by) and by.get("kind") == "machine":
			_say("%s cleared a camp" % MatchTeams.unit_name(by), by)


func _on_structure_fell(s: MatchStructure, by: Node3D) -> void:
	_say("%s destroyed %s" % [_killer_name(by), MatchTeams.unit_name(s)], by)
	unit_died.emit(s, by)
	if s.kind != "core" or winner != "":
		return
	winner = "red" if s.team == "blue" else "blue"
	over = true
	for m: Node3D in machines:
		if recalls.has(m):
			_end_recall(m, false)
		m.move_override = Vector3.ZERO
	player.input_override = Vector2.ZERO
	match_over.emit(winner)
	match_ended.emit(winner == player.team)


# ---- fog of war: the map lane's vision, called as agreed (they build it; this hides what it says is unseen) ----------

func _fog_tick(delta: float) -> void:
	_fog_t -= delta
	if _fog_t > 0.0:
		return
	_fog_t = 0.1
	var vision: Variant = arena.get("vision")
	if vision == null or not (vision as Object).has_method("can_see"):
		return
	for u: Node3D in get_tree().get_nodes_in_group("match_unit"):
		if u.get("kind") == "tower" or u.get("kind") == "core":
			continue  # buildings stay in view through the fog, as the genre does
		if MatchTeams.team_of(u) != player.team and u.has_method("set_seen"):
			u.set_seen(vision.can_see(player.team, u.global_position))


## Whether a team's vision (the map lane's arena.vision) covers pos; true when there is no vision. Machines (the
## player's attack and the bots) only pick targets their team can see. Buildings are always seen.
func team_sees(team: String, u: Node3D) -> bool:
	if u.get("kind") == "tower" or u.get("kind") == "core":
		return true
	var vision: Variant = arena.get("vision") if arena != null else null
	if vision == null or not (vision as Object).has_method("can_see"):
		return true
	return vision.can_see(team, u.global_position)
