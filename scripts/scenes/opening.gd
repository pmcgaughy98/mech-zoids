extends Node2D
## The opening scene: placeholder story lines, then the home base. The story itself is Preston's to write.

const Slot := preload("res://scripts/ui/slot.gd")
const DialogueBox := preload("res://scripts/ui/dialogue_box.gd")


func _ready() -> void:
	add_child(Slot.make("res://art/opening/scene.png", Vector2i(320, 180), Color("0d1b2a"), "slot: opening scene 320x180"))
	var box := DialogueBox.new()
	add_child(box)
	box.finished.connect(_done)
	box.start("opening")


func _done() -> void:
	Run.set_flag("opening_seen")
	Run.goto("base")
