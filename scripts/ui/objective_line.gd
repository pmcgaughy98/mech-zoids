extends CanvasLayer
## The objective line across the top of the screen. Updates itself whenever a story flag changes.

const Slot := preload("res://scripts/ui/slot.gd")
const Objective := preload("res://scripts/ui/objective.gd")

var label: Label


func _ready() -> void:
	layer = 5
	var strip := ColorRect.new()
	strip.size = Vector2(320, 11)
	strip.color = Color(0, 0, 0, 0.6)
	add_child(strip)
	label = Slot.text("", Vector2(3, 0), Color("ffd400"))
	add_child(label)
	Run.flags_changed.connect(refresh)
	refresh()


func refresh() -> void:
	label.text = Objective.current(Run.flags).short
