extends Node2D
## A field scene's story triggers (Claude, 2026-10-13): reads scripts/data/field_triggers.gd for this scene, shows each
## spot's label and a "Z" prompt in reach, and plays its event through an EventBox. The scene keeps walking and its
## own talk; it pauses while `is_busy()`.
##   var triggers := FieldTriggers.new("base", func() -> Vector2: return pilot.position)
##   add_child(triggers)

const Slot := preload("res://scripts/ui/slot.gd")
const Data := preload("res://scripts/data/field_triggers.gd")
const EventBox := preload("res://scripts/ui/event_box.gd")

const REACH := 10.0

var scene_name := ""
var where: Callable            # returns the pilot's position (its top-left, as the scenes place it)
var box: EventBox
var prompt: Label


func _init(scene: String, position_of: Callable) -> void:
	scene_name = scene
	where = position_of


func _ready() -> void:
	for t in Data.for_scene(scene_name):
		if t.get("label", "") != "":
			add_child(Slot.text(t.label, t.rect.position + Vector2(2, -9), Color("5fe1d0")))
	prompt = Slot.text("", Vector2(8, 156), Color(1, 1, 1, 0.8))
	add_child(prompt)
	box = EventBox.new()
	add_child(box)


func is_busy() -> bool:
	return box.is_open()


func _feet() -> Vector2:
	return where.call() + Vector2(6, 8)


func _near(kind: String) -> Dictionary:
	for t in Data.for_scene(scene_name):
		if t.kind == kind and Data.active(Run, t) and t.rect.grow(REACH if kind == "talk" else 0.0).has_point(_feet()):
			return t
	return {}


func _fire(t: Dictionary) -> void:
	if t.get("once", false):
		Run.set_flag("trig_" + t.id)
	prompt.text = ""
	box.play(t.event)


func _process(_delta: float) -> void:
	if is_busy():
		return
	var talk := _near("talk")
	prompt.text = "Z: %s" % t_label(talk) if not talk.is_empty() else ""
	var touch := _near("touch")
	if not touch.is_empty() and (not Run.autopilot or touch.get("autopilot", false)):
		_fire(touch)


func t_label(t: Dictionary) -> String:
	return t.get("label", "look").to_lower() if t.get("label", "") != "" else "look"


func _unhandled_input(event: InputEvent) -> void:
	if is_busy() or not event.is_action_pressed("ui_accept"):
		return
	var t := _near("talk")
	if not t.is_empty():
		get_viewport().set_input_as_handled()
		_fire(t)
