extends Node2D
## One scene for the menu modes (Claude, 2026-10-13): item shop, parts shop, lab, team setup, database, arena, and the
## placeholders for modes not built yet (scripts/game/modes.gd). Run.mode picks the content; every row is a label
## and an action. Text and layout are plain on purpose: the systems underneath (scripts/game/*) are the foundation,
## the look comes in the refinement pass. A mode can open with a story event (Run.mode_args.event, or the lab's first
## welcome), played through scripts/events/event_runner.gd with this screen's text line and rows.
##
## Keys: up / down move, Z (ui_accept) picks, X (ui_cancel) goes back to the field.

const Slot := preload("res://scripts/ui/slot.gd")
const Modes := preload("res://scripts/game/modes.gd")
const Machines := preload("res://scripts/data/machines.gd")
const Items := preload("res://scripts/data/items.gd")
const Pilots := preload("res://scripts/data/pilots.gd")
const Rules := preload("res://scripts/data/battle_rules.gd")
const Roster := preload("res://scripts/game/roster.gd")
const Economy := preload("res://scripts/game/economy.gd")
const Events := preload("res://scripts/data/events.gd")
const EventRunner := preload("res://scripts/events/event_runner.gd")

const ROWS := 11

var rows: Array = []          # [{label, action}]
var cursor := 0
var top := 0
var title: Label
var row_labels: Array = []
var info: Label
var footer: Label
var focus_uid := -1           # the lab's selected machine
var runner = null             # an event playing, or null
var waiting_text := false


func _ready() -> void:
	add_child(Slot.make("res://art/ui/menu_mode.png", Vector2i(320, 180), Color("10141c"), ""))   # art slot: menu background 320x180
	title = Slot.text("", Vector2(10, 6), Color("ffd400"))
	add_child(title)
	for i in ROWS:
		var l := Slot.text("", Vector2(14, 20 + i * 11))
		row_labels.append(l)
		add_child(l)
	info = Slot.text("", Vector2(10, 145))
	info.size = Vector2(300, 22)
	info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(info)
	footer = Slot.text("", Vector2(10, 168), Color(1, 1, 1, 0.6))
	add_child(footer)
	if Run.team_slots.is_empty():   # opened on its own in the editor
		Run.new_game()
	var event: String = Run.mode_args.get("event", "")
	if event == "" and Run.mode == "lab" and not Run.has_flag("lab_welcomed"):
		event = "town_lab_welcome"
	_build()
	if event != "" and Events.EVENTS.has(event):
		_play_event(event)


func _play_event(id: String) -> void:
	runner = EventRunner.new(Run, Run.autopilot)
	runner.say.connect(func(speaker: String, line: String) -> void:
		info.text = "%s: %s" % [speaker, line]
		waiting_text = true
		rows = []
		_draw())
	runner.ask.connect(func(options: Array) -> void:
		rows = []
		for i in options.size():
			rows.append({"label": options[i], "action": _choose.bind(i)})
		cursor = 0
		_draw())
	runner.finished.connect(func(_r: String) -> void:
		runner = null
		waiting_text = false
		_build())
	runner.run_script(Events.EVENTS[id])


func _choose(i: int) -> void:
	runner.choose(i)


# --- Building each mode's rows --------------------------------------------------------------------

func _build() -> void:
	rows = []
	var m: Dictionary = Modes.MODES.get(Run.mode, {})
	info.text = ""
	match Run.mode:
		"item_shop": _shop("items", Items.SHOP_ITEMS, Items.RECOVERY, "ITEM SHOP")
		"parts_shop": _shop("parts", Items.SHOP_PARTS, Items.PARTS, "PARTS SHOP")
		"lab": _lab()
		"team_setup": _team()
		"database": _database()
		"arena": _arena()
		_:
			title.text = Run.mode.to_upper().replace("_", " ")
			info.text = "Wired, not built yet: %s." % m.get("zl", Run.mode)
	rows.append({"label": "Back", "action": _leave})
	cursor = clampi(cursor, 0, rows.size() - 1)
	_draw()


func _shop(kind: String, stock: Array, table: Dictionary, name: String) -> void:
	title.text = name
	for id in stock:
		rows.append({"label": "Buy  %-16s %5d" % [table[id].name, table[id].price], "action": _buy.bind(kind, id)})
	var bag: Dictionary = Run.items if kind == "items" else Run.parts
	for id in bag:
		if int(bag[id]) > 0:
			rows.append({"label": "Sell %-16s x%d  %d" % [table[id].name, bag[id], table[id].price / 2], "action": _sell.bind(kind, id)})


func _lab() -> void:
	if focus_uid >= 0:
		var r := Roster.record_by_uid(Run, focus_uid)
		title.text = "LAB  %s  load %d / %d" % [Machines.MACHINES[r.id].name, Roster.load_used(r), Roster.load_capacity(r.id)]
		for slot in Items.SLOTS:
			var part: String = r.parts[slot]
			rows.append({"label": "%-8s %s" % [slot.capitalize(), Items.PARTS[part].name if part != "" else "(empty)"],
				"action": _cycle_part.bind(focus_uid, slot)})
		rows.append({"label": "Done with this machine", "action": _unfocus})
		return
	title.text = "LAB"
	for r in Run.roster:
		rows.append({"label": "Fit parts: %s" % Machines.MACHINES[r.id].name, "action": _focus.bind(r.uid)})
	for id in Run.unlocked_data:
		if Items.CORES.has(id):
			rows.append({"label": "Build %s  (cores %d, %d cr)" % [Machines.MACHINES[id].name, int(Run.cores.get(id, 0)),
				Items.CORES[id].build_cost], "action": _build_machine.bind(id)})


func _team() -> void:
	title.text = "TEAM SETUP"
	for i in Roster.TEAM_SLOTS:
		var s: Dictionary = Run.team_slots[i]
		var mname: String = Machines.MACHINES[Roster.record_by_uid(Run, s.machine).id].name if s.machine >= 0 else "(empty)"
		var pname: String = Run.pilots[s.pilot].name if s.pilot != "" else "(no pilot)"
		rows.append({"label": "%d  %-20s %s" % [i + 1, mname, pname], "action": _cycle_slot.bind(i)})


func _database() -> void:
	title.text = "DATABASE  machines %d  pilots %d  parts %d" % [Run.catalog.machines.size(), Run.catalog.pilots.size(), Run.catalog.parts.size()]
	for id in Run.catalog.machines:
		var d: Dictionary = Machines.MACHINES[id]
		rows.append({"label": "%-20s %s %s %s" % [d.name, d.size, d.body, d.animal], "action": func() -> void: info.text = d.weapons.map(func(w): return w.name).reduce(func(a, b): return a + ", " + b)})
	for id in Run.catalog.pilots:
		rows.append({"label": "Pilot  %-18s Lv %d" % [Run.pilots[id].name, Run.pilots[id].level], "action": func() -> void: pass})


func _arena() -> void:
	title.text = "ARENA"
	for c in Rules.CHALLENGES:
		var r: Dictionary = Rules.RULES[c.rule]
		var foes: String = ", ".join(c.enemy.map(func(e): return Machines.MACHINES[e].name))
		rows.append({"label": "%-16s vs %s  %d cr" % [r.name, foes, c.purse], "action": _challenge.bind(c)})


# --- Actions --------------------------------------------------------------------------------------

func _buy(kind: String, id: String) -> void:
	var why := Economy.buy(Run, kind, id)
	_build()
	info.text = why if why != "" else "Bought."


func _sell(kind: String, id: String) -> void:
	var why := Economy.sell(Run, kind, id)
	_build()
	info.text = why if why != "" else "Sold."


func _focus(uid: int) -> void:
	focus_uid = uid
	cursor = 0
	_build()


func _unfocus() -> void:
	focus_uid = -1
	cursor = 0
	_build()


## Fits the next owned part for this slot, or empties it after the last one.
func _cycle_part(uid: int, slot: String) -> void:
	var r := Roster.record_by_uid(Run, uid)
	var choices: Array = Items.PARTS.keys().filter(func(p): return Items.PARTS[p].slot == slot and int(Run.parts.get(p, 0)) > 0)
	var why := ""
	if choices.is_empty():
		Roster.unequip(Run, uid, slot)
	else:
		why = Roster.equip(Run, uid, choices[0])
	_build()
	info.text = why if why != "" else "%s: %s" % [slot.capitalize(), Items.PARTS[r.parts[slot]].name if r.parts[slot] != "" else "empty"]


func _build_machine(id: String) -> void:
	var r := Roster.build_machine(Run, id)
	_build()
	info.text = "Built a %s." % Machines.MACHINES[id].name if not r.is_empty() else "Needs its data, a core and the credits."


## Puts the next machine not in the team into this slot, with the next free pilot.
func _cycle_slot(i: int) -> void:
	var used: Array = Run.team_slots.map(func(s): return s.machine)
	var free: Array = Run.roster.filter(func(r): return not used.has(r.uid))
	if free.is_empty():
		info.text = "No other machines. Build one in the lab."
		return
	var pilot: String = Run.team_slots[i].pilot
	if pilot == "":
		var busy: Array = Run.team_slots.map(func(s): return s.pilot)
		var idle: Array = Run.pilots.keys().filter(func(p): return not busy.has(p))
		pilot = idle[0] if not idle.is_empty() else ""
	if pilot == "":
		info.text = "No free pilot for this slot."
		return
	Roster.assign(Run, i, pilot, free[0].uid)
	_build()


func _challenge(c: Dictionary) -> void:
	Run.start_story_battle({"enemy": c.enemy, "rule": c.rule, "purse": c.purse, "core": c.core,
		"flag": c.id, "reward": "", "win_scene": Run.location})


func _leave() -> void:
	Run.goto(Run.location)


# --- Drawing and input ----------------------------------------------------------------------------

func _draw() -> void:
	if cursor < top:
		top = cursor
	elif cursor >= top + ROWS:
		top = cursor - ROWS + 1
	for i in ROWS:
		var k := top + i
		row_labels[i].text = (("> " if k == cursor else "  ") + rows[k].label) if k < rows.size() else ""
	footer.text = "Credits %d" % Run.money + ("   (Z to continue)" if waiting_text else "")


func _unhandled_input(event: InputEvent) -> void:
	if waiting_text:
		if event.is_action_pressed("ui_accept"):
			waiting_text = false
			runner.advance()
		return
	if rows.is_empty():
		return
	if event.is_action_pressed("ui_down"):
		cursor = (cursor + 1) % rows.size()
		_draw()
	elif event.is_action_pressed("ui_up"):
		cursor = (cursor - 1 + rows.size()) % rows.size()
		_draw()
	elif event.is_action_pressed("ui_accept"):
		rows[cursor].action.call()
	elif event.is_action_pressed("ui_cancel") and runner == null:
		_leave()
