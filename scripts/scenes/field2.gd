extends Node2D
## The second field area: a canyon. A flying rival circles over it; walking under it starts the battle.
## West edge goes back to the first field. After the win, the talk plays here and the east road says
## the next town is not built yet.

const Slot := preload("res://scripts/ui/slot.gd")
const Walk := preload("res://scripts/ui/walk.gd")
const DialogueBox := preload("res://scripts/ui/dialogue_box.gd")
const ObjectiveLine := preload("res://scripts/ui/objective_line.gd")
const PauseMenu := preload("res://scripts/ui/pause_menu.gd")
const Commands := preload("res://scripts/data/commands.gd")

const BOUNDS := Rect2(0, 40, 308, 100)
const RIVAL := Rect2(180, 46, 64, 48)
const EDGE := 2.0

var pilot: Node2D
var box: DialogueBox
var menu: PauseMenu
var note: Label
var won := false


func _ready() -> void:
	won = Run.has_flag("canyon_battle_won")
	add_child(Slot.make("res://art/field/canyon.png", Vector2i(320, 180), Color("8a5a3c"), ""))
	if not ResourceLoader.exists("res://art/field/canyon.png"):   # placeholder floor until the art is in (2026-10-20: it is)
		var floor_band := ColorRect.new()  # the canyon floor you can walk on
		floor_band.position = Vector2(0, 40)
		floor_band.size = Vector2(320, 116)
		floor_band.color = Color("b07a4f")
		add_child(floor_band)
		add_child(Slot.text("CANYON (placeholder)", Vector2(8, 166), Color(1, 1, 1, 0.4)))
	add_child(Slot.text("< grassland", Vector2(2, 92), Color(1, 1, 1, 0.7)))
	if not won:
		var rival := Slot.machine("hawk_s", true)
		rival.position = RIVAL.position - Vector2(0, 16)  # it flies
		add_child(rival)
	note = Slot.text("", Vector2(170, 140), Color(1, 1, 1, 0.9))
	add_child(note)
	pilot = Slot.make("res://art/people/pilot.png", Vector2i(12, 16), Color("1e90ff"), "")
	pilot.position = Vector2(200, 100) if Run.came_from == "battle" else Vector2(14, 96)
	add_child(pilot)
	add_child(ObjectiveLine.new())
	menu = PauseMenu.new()
	add_child(menu)
	box = DialogueBox.new()
	add_child(box)
	box.finished.connect(func(): Run.debrief_done())
	if not Run.last_battle.is_empty():
		box.start(Run.last_battle.dialogue)


func _process(delta: float) -> void:
	if box.is_open() or menu.is_open():
		return
	var goal = null if won else RIVAL.get_center() - Vector2(6, 8)
	pilot.position = Walk.step(pilot.position, delta, goal, BOUNDS)
	note.text = "Road east: next town not built yet" if won and pilot.position.x > 270 else ""
	if not won and RIVAL.grow(-8).has_point(pilot.position + Vector2(6, 8)):
		set_process(false)
		Run.start_battle(["hawk_s"], ["shield_wall", "power_surge"], "canyon_battle_won", "", "field2")
	elif pilot.position.x <= EDGE:
		set_process(false)
		Run.goto("field")


func _unhandled_input(event: InputEvent) -> void:
	if not box.is_open() and not menu.is_open() and event.is_action_pressed("ui_cancel"):
		menu.open()
