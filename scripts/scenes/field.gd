extends Node2D
## The first field area. A rival machine waits in the grass; walking into it starts the first battle.
## West edge goes home. Once that battle is won the rival is gone and the east edge leads to the canyon.

const Slot := preload("res://scripts/ui/slot.gd")
const Walk := preload("res://scripts/ui/walk.gd")
const ObjectiveLine := preload("res://scripts/ui/objective_line.gd")
const PauseMenu := preload("res://scripts/ui/pause_menu.gd")
const Commands := preload("res://scripts/data/commands.gd")

const BOUNDS := Rect2(0, 20, 320, 148)
const RIVAL := Rect2(200, 70, 64, 48)
const EDGE := 2.0

var pilot: Node2D
var menu: PauseMenu
var won := false


func _ready() -> void:
	won = Run.has_flag("first_battle_won")
	add_child(Slot.make("res://art/field/grassland.png", Vector2i(320, 180), Color("3e8948"), ""))
	add_child(Slot.text("< hangar", Vector2(2, 90), Color(1, 1, 1, 0.6)))
	if won:
		add_child(Slot.text("canyon >", Vector2(282, 90), Color(1, 1, 1, 0.6)))
	else:
		var rival := Slot.machine("raptor_s", true)
		rival.position = RIVAL.position
		add_child(rival)
	pilot = Slot.make("res://art/people/pilot.png", Vector2i(12, 16), Color("1e90ff"), "")
	pilot.position = Vector2(300, 96) if Run.came_from == "field2" else Vector2(14, 96)
	add_child(pilot)
	add_child(ObjectiveLine.new())
	menu = PauseMenu.new()
	add_child(menu)


func _process(delta: float) -> void:
	if menu.is_open():
		return
	var goal = RIVAL.get_center() - Vector2(6, 8) if not won else Vector2(320, 96)
	pilot.position = Walk.step(pilot.position, delta, goal, BOUNDS)
	if not won and RIVAL.grow(-8).has_point(pilot.position + Vector2(6, 8)):
		set_process(false)
		Run.start_battle(["raptor_s"], Commands.STARTER_DECK, "first_battle_won", Commands.REWARD_FIRST_BATTLE, "base")
	elif pilot.position.x <= EDGE:
		set_process(false)
		Run.goto("base")
	elif won and pilot.position.x >= 320 - 12 - EDGE:
		set_process(false)
		Run.goto("field2")


func _unhandled_input(event: InputEvent) -> void:
	if not menu.is_open() and event.is_action_pressed("ui_cancel"):
		menu.open()
