extends Node2D
## Title screen: Continue (when a save exists) puts you back where you saved; New Game starts the opening.

const Slot := preload("res://scripts/ui/slot.gd")

var choices: Array = []
var cursor := 0
var rows: Array = []
var frames := 0


func _ready() -> void:
	add_child(Slot.make("res://art/title/background.png", Vector2i(320, 180), Color("15181d"), "slot: title background 320x180"))
	var logo := Slot.make("res://art/title/logo.png", Vector2i(200, 40), Color("1e90ff"), "slot: logo 200x40")
	logo.position = Vector2(60, 34)
	add_child(logo)
	add_child(Slot.text("working title", Vector2(128, 76), Color(1, 1, 1, 0.5)))
	choices = (["Continue"] if Run.has_save() else []) + ["New Game", "Quit"]
	for i in choices.size():
		var l := Slot.text("", Vector2(130, 100 + i * 12))
		rows.append(l)
		add_child(l)
	_draw_menu()


func _draw_menu() -> void:
	for i in choices.size():
		rows[i].text = ("> " if i == cursor else "  ") + choices[i]


func _process(_delta: float) -> void:
	frames += 1
	if Run.autopilot and frames == 5:
		_pick(choices.find("New Game"))


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_down"):
		cursor = (cursor + 1) % choices.size()
		_draw_menu()
	elif event.is_action_pressed("ui_up"):
		cursor = (cursor - 1 + choices.size()) % choices.size()
		_draw_menu()
	elif event.is_action_pressed("ui_accept"):
		_pick(cursor)


func _pick(i: int) -> void:
	match choices[i]:
		"Quit":
			get_tree().quit()
		"Continue":
			if Run.load_game():
				Run.goto(Run.location)
		"New Game":
			Run.new_game()
			Run.goto("opening")
