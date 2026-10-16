extends Node2D
## Home base (the hangar). Talk to the mechanic, see your machine, X for the menu, east door to the field.
## After a battle that ends here, the talk for how it went plays once.

const Slot := preload("res://scripts/ui/slot.gd")
const Walk := preload("res://scripts/ui/walk.gd")
const DialogueBox := preload("res://scripts/ui/dialogue_box.gd")
const ObjectiveLine := preload("res://scripts/ui/objective_line.gd")
const PauseMenu := preload("res://scripts/ui/pause_menu.gd")
const FieldTriggers := preload("res://scripts/field/field_triggers.gd")

const BOUNDS := Rect2(8, 20, 312, 148)
const DOOR := Rect2(306, 80, 14, 32)   # walk into it to go to the field
const MECHANIC := Vector2(90, 70)

var pilot: Node2D
var box: DialogueBox
var menu: PauseMenu
var prompt: Label
var triggers: FieldTriggers   # story triggers here (scripts/data/field_triggers.gd): the lab terminal


func _ready() -> void:
	add_child(Slot.make("res://art/rooms/hangar.png", Vector2i(320, 180), Color("2a2f36"), ""))
	var door := Slot.make("res://art/rooms/hangar_door.png", Vector2i(14, 32), Color("ffd400"), "")
	door.position = DOOR.position
	add_child(door)
	var parked := Slot.machine("lion_m", false)
	parked.position = Vector2(170, 40)
	add_child(parked)
	var mechanic := Slot.make("res://art/people/mechanic.png", Vector2i(12, 16), Color("e07a2f"), "")
	mechanic.position = MECHANIC - Vector2(6, 16)
	add_child(mechanic)
	add_child(Slot.text("HANGAR   X: menu", Vector2(8, 166), Color(1, 1, 1, 0.4)))
	pilot = Slot.make("res://art/people/pilot.png", Vector2i(12, 16), Color("1e90ff"), "")
	pilot.position = Vector2(290, 96) if Run.came_from in ["field", "battle"] else Vector2(60, 110)
	add_child(pilot)
	prompt = Slot.text("", Vector2(60, 118), Color(1, 1, 1, 0.8))
	add_child(prompt)
	add_child(ObjectiveLine.new())
	menu = PauseMenu.new()
	add_child(menu)
	box = DialogueBox.new()
	add_child(box)
	box.finished.connect(_dialogue_done)
	triggers = FieldTriggers.new("base", func() -> Vector2: return pilot.position)
	add_child(triggers)
	if not Run.last_battle.is_empty():
		box.start(Run.last_battle.dialogue)


func _dialogue_done() -> void:
	if not Run.last_battle.is_empty():
		Run.debrief_done()


func _process(delta: float) -> void:
	if box.is_open() or menu.is_open() or triggers.is_busy():
		return
	pilot.position = Walk.step(pilot.position, delta, _autopilot_goal(), BOUNDS)
	prompt.text = "Z / Enter: talk" if pilot.position.distance_to(MECHANIC) < 24 else ""
	if DOOR.has_point(pilot.position + Vector2(6, 8)):
		set_process(false)
		Run.goto("field")


func _unhandled_input(event: InputEvent) -> void:
	if box.is_open() or menu.is_open() or triggers.is_busy():
		return
	if event.is_action_pressed("ui_cancel"):
		menu.open()
	elif event.is_action_pressed("ui_accept") and pilot.position.distance_to(MECHANIC) < 24:
		box.start("mechanic")


## On autopilot: head for the door while there is a battle still to win, then stand still.
func _autopilot_goal():
	if Run.has_flag("canyon_battle_won"):
		return null
	return DOOR.get_center() - Vector2(6, 8)
