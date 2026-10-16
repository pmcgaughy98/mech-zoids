extends CanvasLayer
## The pause menu, opened with X / Esc outside battle: Deck (equip commands), Team (your machines), Save.
## The deck rule from Zoids Legacy: equip up to Commands.DECK_LIMIT; each works once per battle.

const Slot := preload("res://scripts/ui/slot.gd")
const Commands := preload("res://scripts/data/commands.gd")
const Machines := preload("res://scripts/data/machines.gd")

const ROWS := 9

var page := "main"            # main, deck, team
var cursor := 0
var items: Array = []
var title: Label
var rows: Array = []
var info: Label


func _ready() -> void:
	layer = 20
	var panel := Slot.make("res://art/ui/pause_menu.png", Vector2i(200, 150), Color(0.05, 0.07, 0.12, 0.95))
	panel.position = Vector2(60, 16)
	add_child(panel)
	title = Slot.text("", Vector2(68, 18), Color("ffd400"))
	add_child(title)
	for i in ROWS:
		var l := Slot.text("", Vector2(70, 30 + i * 10))
		rows.append(l)
		add_child(l)
	info = Slot.text("", Vector2(68, 126))
	info.size = Vector2(186, 38)
	info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(info)
	visible = false


func is_open() -> bool:
	return visible


func open() -> void:
	visible = true
	_show("main")


func close() -> void:
	visible = false


func _show(p: String) -> void:
	page = p
	cursor = 0
	_refresh()


func _refresh() -> void:
	info.text = ""
	match page:
		"main":
			title.text = "MENU"
			items = ["Deck", "Team", "Facilities", "Save", "Close"]
		"deck":
			title.text = "DECK  %d / %d equipped" % [Run.deck.size(), Commands.DECK_LIMIT]
			items = []
			for id in Run.owned:
				items.append(("[x] " if Run.deck.has(id) else "[ ] ") + Commands.COMMANDS[id].name)
			if Run.owned.size() > 0:
				info.text = Commands.COMMANDS[Run.owned[cursor]].text
		"facilities":   # every menu mode (scripts/game/modes.gd); towns will open these through events later
			title.text = "FACILITIES"
			items = ["Team setup", "Lab", "Item shop", "Parts shop", "Arena", "Database", "Town map"]
		"team":
			title.text = "TEAM"
			items = []
			for id in Run.team:
				var m := Machines.make(id, "player")
				items.append("%s  %s %s %s" % [m.name, m.size, m.body, m.animal])
				items.append("  HP %d  EP %d  SPD %d  DEF %d" % [m.max_hp, m.max_ep, m.speed, m.defense])
				for w in m.weapons:
					items.append("  %s  %s %d  EP %d" % [w.name, w.type, w.power, w.ep])
	for i in ROWS:
		rows[i].text = (("> " if i == cursor and page != "team" else "  ") + items[i]) if i < items.size() else ""


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	get_viewport().set_input_as_handled()
	if event.is_action_pressed("ui_cancel"):
		if page == "main":
			close()
		else:
			_show("main")
	elif event.is_action_pressed("ui_down") and items.size() > 0:
		cursor = (cursor + 1) % min(items.size(), ROWS)
		_refresh()
	elif event.is_action_pressed("ui_up") and items.size() > 0:
		cursor = (cursor - 1 + min(items.size(), ROWS)) % min(items.size(), ROWS)
		_refresh()
	elif event.is_action_pressed("ui_accept"):
		match page:
			"main":
				match items[cursor]:
					"Facilities": _show("facilities")
					"Deck": _show("deck")
					"Team": _show("team")
					"Save":
						info.text = "Saved." if Run.save_game() else "Could not save."
					"Close": close()
			"facilities":
				close()
				Run.go_mode({"Team setup": "team_setup", "Lab": "lab", "Item shop": "item_shop", "Parts shop": "parts_shop",
					"Arena": "arena", "Database": "database", "Town map": "town_map"}[items[cursor]])
			"deck":
				var full := not Run.toggle_deck(Run.owned[cursor])
				_refresh()
				if full:
					info.text = "The deck is full (%d). Take one out first." % Commands.DECK_LIMIT
