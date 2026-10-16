extends SceneTree
## Headless check of the Zoids Legacy-shaped foundation (Claude, 2026-10-13): player state, shops, parts and load,
## pilots and pulse through a real battle, the lab building from a core, team slots, battle rules, the event runner,
## save and load, and that every mode has a scene.
##   Godot --headless --path . --script res://tools/debug/foundation_check.gd

const Logic := preload("res://scripts/battle/battle_logic.gd")
const Machines := preload("res://scripts/data/machines.gd")
const Items := preload("res://scripts/data/items.gd")
const Rules := preload("res://scripts/data/battle_rules.gd")
const Modes := preload("res://scripts/game/modes.gd")
const Roster := preload("res://scripts/game/roster.gd")
const Economy := preload("res://scripts/game/economy.gd")
const Events := preload("res://scripts/data/events.gd")
const EventRunner := preload("res://scripts/events/event_runner.gd")

var fails: Array = []


func check(ok: bool, what: String) -> void:
	if not ok:
		fails.append(what)
	print(("  ok   " if ok else "  FAIL ") + what)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var run = root.get_node("Run")
	run.save_path = "user://foundation_check_save.json"
	run.new_game()
	print("== player state")
	check(run.pilots.has("pilot_lead"), "new game has the lead pilot")
	check(run.roster.size() == run.team.size() and run.roster.size() > 0, "a machine record for each team machine")
	check(run.team_slots.size() == Roster.TEAM_SLOTS and run.team_slots[0].pilot == "pilot_lead", "six team slots, lead pilot in slot 1")
	check(run.money == Items.STARTING_MONEY, "starting money")

	print("== shops")
	var m0: int = run.money
	check(Economy.buy(run, "items", "repair_kit") == "" and run.money == m0 - Items.RECOVERY.repair_kit.price, "buy an item")
	check(Economy.buy(run, "parts", "plate_armor_1") == "" and int(run.parts.plate_armor_1) == 1, "buy a part")
	var m1: int = run.money
	check(Economy.sell(run, "items", "repair_kit") == "" and run.money == m1 + Items.RECOVERY.repair_kit.price / 2, "sell for half")
	check(Economy.sell(run, "parts", "thruster_pack") != "", "cannot sell what you do not have")
	run.money = 5
	check(Economy.buy(run, "parts", "impact_rams") == "not enough credits", "cannot buy without credits")
	run.money = 20000

	print("== parts and load")
	var rec: Dictionary = run.roster[0]
	var bare: Dictionary = Roster.make_unit(run, rec, "player")
	check(Roster.equip(run, rec.uid, "plate_armor_1") == "", "fit armour")
	var fitted: Dictionary = Roster.make_unit(run, rec, "player")
	check(fitted.defense == bare.defense + 6, "fitted armour raises defense (%d to %d)" % [bare.defense, fitted.defense])
	for i in 8:
		Economy.buy(run, "parts", "plate_armor_2")
	Economy.buy(run, "parts", "impact_rams")
	Economy.buy(run, "parts", "thruster_pack")
	Economy.buy(run, "parts", "target_sensor")
	Roster.equip(run, rec.uid, "impact_rams")
	Roster.equip(run, rec.uid, "thruster_pack")
	Roster.equip(run, rec.uid, "target_sensor")
	var heavy := Roster.equip(run, rec.uid, "plate_armor_2")
	check(Roster.load_used(rec) <= Roster.load_capacity(rec.id), "load never exceeds capacity (%d / %d; heavy armour: '%s')" % [Roster.load_used(rec), Roster.load_capacity(rec.id), heavy])
	Roster.unequip(run, rec.uid, "weapon")
	check(rec.parts.weapon == "" and int(run.parts.impact_rams) >= 1, "unfit returns the part")

	print("== a battle with the team, and its payout")
	var lead: Dictionary = run.pilots.pilot_lead
	var lvl0: int = lead.level
	var b = Logic.new()
	b.setup(run.battle_team(), ["pangolin_m"], [], [], 7)
	while b.winner == "":
		var u: Dictionary = b.begin_turn()
		if u.is_empty():
			break
		var c: Dictionary = b.choose(u, "smart")
		if c.command != "":
			b.play_command(u, c.command)
		b.do_action(u, c)
	check(b.units[0].has("uid") and b.units[0].pilot == "pilot_lead", "team units carry their record and pilot")
	var money_before: int = run.money
	var lines: Array = run.apply_battle_result(b.units, b.winner, {"purse": 300, "core": "pangolin_m"})
	print("    winner %s, %d rounds: %s" % [b.winner, b.round_no, "; ".join(lines)])
	check(lead.exp > 0, "the pilot gained experience")
	check(rec.pulse > 0, "the pair gained pulse (%d)" % rec.pulse)
	if b.winner == "player":
		check(run.money > money_before and int(run.cores.get("pangolin_m", 0)) == 1, "a win pays credits and the core")
	for i in 30:
		run.apply_battle_result(b.units, "player", {})
	check(lead.level > lvl0, "repeated wins raise the pilot's level (%d to %d)" % [lvl0, lead.level])
	check(rec.pulse_effects.size() > 0, "pulse unlocks effects (%s)" % ", ".join(rec.pulse_effects))
	check(run.catalog.machines.has("pangolin_m"), "the database records the machine fought")

	print("== items in battle")
	var b2 = Logic.new()
	b2.setup(run.battle_team(), ["pangolin_m"], [], [], 3)
	var me: Dictionary = b2.begin_turn()
	while me.side != "player":
		b2.do_action(me, b2.choose(me, "basic"))
		me = b2.begin_turn()
	me.hp = me.max_hp / 4
	run.items["repair_kit"] = 1
	var restored: int = Economy.use_on_unit(run, "repair_kit", me)
	b2.use_item(me, "Repair Kit", restored, "HP")
	check(restored > 0 and int(run.items.repair_kit) == 0, "a repair kit restores health and is spent (+%d)" % restored)
	check(b2.queue[-1].kind == "item" and (b2.order.is_empty() or b2.order[0] != me), "using an item records its step and ends the turn")
	check(Economy.use_on_unit(run, "repair_kit", me) == -1, "no kit left, nothing used")
	print("== formation: front and back rows")
	var team4 := ["wolf_m", "hippo_m", "pangolin_m", "shoebill_m"]
	var foes4 := ["raptor_s", "hawk_s", "hippo_m", "wolf_m"]
	var f = Logic.new()
	f.setup(team4, foes4, [], [], 5)
	var back: Dictionary = f.units[3]
	check(f.units[0].row == "front" and back.row == "back" and f.units[7].row == "back", "the first three stand in front, the fourth behind")
	var melee_i: int = back.weapons.map(func(w): return w.type).find("melee")
	check(melee_i >= 0 and not f.can_use(back, back.weapons[melee_i]) and not f._affordable(back, melee_i), "melee cannot strike out of the back row")
	var lead_u: Dictionary = f.units[0]
	var fm0: int = lead_u.weapons.map(func(w): return w.type).find("melee")
	var fr0: int = lead_u.weapons.map(func(w): return w.type != "melee").find(true)
	check(f.valid_targets(lead_u, lead_u.weapons[fm0]).size() == 3 and not f.valid_targets(lead_u, lead_u.weapons[fm0]).has(f.units[7]), "melee reaches only the enemy's front row")
	check(fr0 < 0 or f.valid_targets(lead_u, lead_u.weapons[fr0]).size() == 4, "guns, beams and missiles reach every row")
	var picked: Dictionary = f.choose(back, "smart")
	check(picked.kind == "charge" or not lead_u.weapons.is_empty() and f.can_use(back, back.weapons[picked.weapon]), "a back-row machine only picks weapons that reach")
	for i in [4, 5, 6]:
		f.units[i].hp = 0
	check(f.front_line("enemy") == [f.units[7]], "an empty front row pulls the back row forward")
	var named: Dictionary = {"kind": "attack", "weapon": fm0, "target": 7}
	check(f._target_for(lead_u, named) == f.units[7], "a named target that is in reach is the one hit")
	var g = Logic.new()
	g.setup(team4, foes4, [], [], 9)
	var turns := 0
	while g.winner == "" and turns < 600:
		var gu: Dictionary = g.begin_turn()
		if gu.is_empty():
			break
		g.do_action(gu, g.choose(gu, "smart"))
		turns += 1
	check(g.winner != "", "a four-a-side battle finishes (%s wins, %d turns, %d rounds)" % [g.winner, turns, g.round_no])

	print("== the lab and team setup")
	run.cores["pangolin_m"] = 1
	if not run.unlocked_data.has("pangolin_m"):
		run.unlocked_data.append("pangolin_m")
	var built: Dictionary = Roster.build_machine(run, "pangolin_m")
	check(not built.is_empty() and run.roster.size() == 2, "build a machine from its data and a core")
	check(Roster.build_machine(run, "pangolin_m").is_empty(), "cannot build without another core")
	Roster.add_pilot(run, "pilot_ace")
	check(Roster.assign(run, 1, "pilot_ace", built.uid) and run.team.size() == 2, "assign a pilot and machine to slot 2")
	check(run.battle_team().size() == 2 and run.battle_team(1).size() == 1, "battle team follows the slots and a rule's cap")

	print("== battle rules")
	check(not Rules.allows("ground_only", Machines.MACHINES.shoebill_m), "ground-only rule keeps flyers out")
	check(not Rules.allows("light_class", Machines.MACHINES.ape_l) and Rules.allows("light_class", Machines.MACHINES.wolf_m), "light class keeps size L out")

	print("== event runner")
	run.flags.erase("lab_welcomed")
	var runner = EventRunner.new(run, true)
	var cores0: int = int(run.cores.get("pangolin_m", 0))
	var res: String = await runner.run_script(Events.EVENTS.town_lab_welcome)
	check(run.has_flag("lab_welcomed") and int(run.cores.get("pangolin_m", 0)) == cores0 + 1, "the welcome script sets its flag and gives the core")
	check(res == "mode", "the script hands over to the lab mode (%s)" % res)
	var runner2 = EventRunner.new(run, true)
	var res2: String = await runner2.run_script(Events.EVENTS.town_lab_welcome)
	check(res2 == "mode" and not runner2.log.has("choice") and runner2.log.has("text"), "a second visit takes the short branch (no choice offered)")
	var runner3 = EventRunner.new(run, true)
	check(await runner3.run_script(Events.EVENTS.arena_first_bout) == "battle", "a script can start a battle")

	print("== field triggers")
	var FT = load("res://scripts/data/field_triggers.gd")
	var term: Dictionary = FT.for_scene("base")[0]
	check(FT.active(run, term) and Events.EVENTS.has(term.event), "the hangar lab terminal is live and its script exists")
	var once := {"id": "test_once", "once": true}
	run.set_flag("trig_test_once")
	check(not FT.active(run, once), "a once-only trigger stays off after firing")
	check(not FT.active(run, {"id": "x", "if_flag": "never_set_flag"}) and FT.active(run, {"id": "y", "if_not_flag": "never_set_flag"}), "flag conditions gate triggers")
	for scene in FT.TRIGGERS:
		for t in FT.TRIGGERS[scene]:
			check(Events.EVENTS.has(t.event), "trigger %s in %s points at a real script" % [t.id, scene])
	print("== save and load")
	check(run.save_game(), "save")
	var pulse_saved: int = rec.pulse
	var level_saved: int = lead.level
	var money_saved: int = run.money
	run.new_game()
	check(run.load_game(), "load")
	check(run.roster.size() == 2 and run.roster[0].pulse == pulse_saved and run.pilots.pilot_lead.level == level_saved and run.money == money_saved,
		"roster, pulse, pilot level and credits survive a save")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(run.save_path))

	print("== every foundation script loads (parse errors show here, not only when a scene opens)")
	for path in ["res://scripts/scenes/menu_mode.gd", "res://scripts/ui/event_box.gd", "res://scripts/field/field_triggers.gd",
		"res://scripts/game/modes.gd", "res://scripts/game/roster.gd", "res://scripts/game/progression.gd", "res://scripts/game/economy.gd",
		"res://scripts/events/event_runner.gd", "res://scripts/scenes/base.gd", "res://scripts/scenes/battle.gd", "res://scripts/ui/pause_menu.gd"]:
		var sc = load(path)
		check(sc != null and sc.can_instantiate(), "loads: %s" % path.get_file())
	print("== modes")
	for m in Modes.MODES:
		var scene: String = Modes.scene_of(m)
		check(scene == "" or ResourceLoader.exists("res://scenes/%s.tscn" % scene), "mode %s has its scene (%s)" % [m, scene])

	print("foundation_check: %s (%d failed)" % ["PASS" if fails.is_empty() else "FAIL", fails.size()])
	quit(0 if fails.is_empty() else 1)
