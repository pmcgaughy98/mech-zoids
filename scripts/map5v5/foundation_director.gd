extends MatchDirector
## Reuses real unit/cooldown/recall/hold contracts. Passive training, no waves or win claim.

func setup(a: Node3D, human: Node3D) -> void:
	super.setup(a, human)
	for team in ["blue", "red"]:
		# Preserve Claude's current red kangaroo choice without duplicating it in the new slots.
		_make_bot(team, "kangaroo" if team=="blue" else "fennec", 0)
		_make_bot(team, "hummingbird", 1)
		var ordered: Array=[player] if team=="blue" else []
		ordered.append_array(machines.filter(func(m):return m.team==team and m!=player))
		var slot := 0
		for m in ordered:
			if m.team != team: continue
			m.set_meta("slot", slot)
			m.global_position = a.spawn_slots(team)[slot]
			if m.has_node("Bot"): m.get_node("Bot").hold = true
			slot += 1
	for s in structures.values():
		s.set_physics_process(false)
		s.set_process(false)
	ready_to_play = true
	next_wave = INF

func _spawn_slot(m: Node3D) -> Vector3:
	return arena.spawn_slots(m.team)[int(m.get_meta("slot", 0)) % 5]

func _physics_process(delta: float) -> void:
	if not ready_to_play: return
	elapsed += delta
	_machines_tick(delta)
	MatchBodies.separate(get_tree(), delta)
	_fog_tick(delta)
