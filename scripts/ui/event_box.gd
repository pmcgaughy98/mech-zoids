extends CanvasLayer
## Plays a story event script on screen (Claude, 2026-10-13): text in a panel, choices as rows, Z to advance or pick.
## The script runs in scripts/events/event_runner.gd; this is only its window. On autopilot the runner answers itself.

signal finished(result: String)

const Slot := preload("res://scripts/ui/slot.gd")
const Events := preload("res://scripts/data/events.gd")
const EventRunner := preload("res://scripts/events/event_runner.gd")

const ROWS := 3   # rows 9 px apart inside the panel (4 at 7 px overlapped)

var runner = null
var panel: Node
var text: Label
var rows: Array = []
var options: Array = []
var cursor := 0
var waiting := false


func _ready() -> void:
	layer = 25
	panel = Slot.make("res://art/ui/dialogue_box.png", Vector2i(304, 56), Color(0.05, 0.07, 0.12, 0.95))
	panel.position = Vector2(8, 118)
	add_child(panel)
	text = Slot.text("", Vector2(14, 121))
	text.size = Vector2(292, 26)
	text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(text)
	for i in ROWS:
		var l := Slot.text("", Vector2(20, 145 + i * 9))
		rows.append(l)
		add_child(l)
	visible = false


func is_open() -> bool:
	return visible


## Starts script `id` from scripts/data/events.gd.
func play(id: String) -> void:
	visible = true
	runner = EventRunner.new(Run, Run.autopilot)
	runner.say.connect(_on_say)
	runner.ask.connect(_on_ask)
	runner.finished.connect(_on_finished)
	runner.run_script(Events.EVENTS[id])


func _on_say(speaker: String, line: String) -> void:
	text.text = "%s: %s" % [speaker, line] if speaker != "" else line
	options = []
	waiting = true
	_draw()


func _on_ask(opts: Array) -> void:
	options = opts
	cursor = 0
	waiting = false
	_draw()


func _on_finished(result: String) -> void:
	visible = false
	runner = null
	finished.emit(result)


func _draw() -> void:
	for i in ROWS:
		rows[i].text = (("> " if i == cursor else "  ") + options[i]) if i < options.size() else ""


func _unhandled_input(event: InputEvent) -> void:
	if not visible or runner == null:
		return
	get_viewport().set_input_as_handled()
	if waiting and event.is_action_pressed("ui_accept"):
		waiting = false
		runner.advance()
	elif not options.is_empty():
		if event.is_action_pressed("ui_down"):
			cursor = (cursor + 1) % options.size()
			_draw()
		elif event.is_action_pressed("ui_up"):
			cursor = (cursor - 1 + options.size()) % options.size()
			_draw()
		elif event.is_action_pressed("ui_accept"):
			var pick := cursor
			options = []
			_draw()
			runner.choose(pick)
