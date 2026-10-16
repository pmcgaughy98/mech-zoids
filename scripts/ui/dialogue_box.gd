extends CanvasLayer
## A plain dialogue box. Lines live in dialogue/*.txt as "Speaker|Line" so text can change without code.
## Press accept to move on; on autopilot it moves on by itself. Emits `finished` after the last line.

signal finished

const Slot := preload("res://scripts/ui/slot.gd")

var lines: Array = []
var index := 0
var auto_wait := 0.0
var speaker: Label
var body: Label


func _ready() -> void:
	layer = 10
	var panel := Slot.make("res://art/ui/dialogue_box.png", Vector2i(312, 44), Color(0.05, 0.07, 0.12, 0.92))
	panel.position = Vector2(4, 132)
	add_child(panel)
	speaker = Slot.text("", Vector2(10, 133), Color("ffd400"))
	body = Slot.text("", Vector2(10, 145))
	body.size = Vector2(300, 30)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(speaker)
	add_child(body)
	visible = false


func start(file: String) -> void:
	lines = load_lines(file)
	index = 0
	visible = true
	_show()


static func load_lines(file: String) -> Array:
	var out := []
	var f := FileAccess.open("res://dialogue/%s.txt" % file, FileAccess.READ)
	if f == null:
		return [["", "(missing dialogue file: %s)" % file]]
	for raw in f.get_as_text().split("\n"):
		var line := raw.strip_edges()
		if line == "" or line.begins_with("#"):
			continue
		var cut := line.split("|", true, 1)
		out.append(cut if cut.size() == 2 else ["", line])
	return out


func is_open() -> bool:
	return visible


func _process(delta: float) -> void:
	if visible and Run.autopilot:
		auto_wait += delta
		if auto_wait > 0.05:
			auto_wait = 0.0
			_advance()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_accept"):
		get_viewport().set_input_as_handled()
		_advance()


func _advance() -> void:
	index += 1
	if index >= lines.size():
		visible = false
		finished.emit()
	else:
		_show()


func _show() -> void:
	speaker.text = lines[index][0]
	body.text = lines[index][1]
