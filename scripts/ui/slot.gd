extends RefCounted
## Named art slots. If Codex has dropped a picture at `path`, it is shown; otherwise a coloured box with the
## slot's name, at the exact pixel size the art should be. Every slot is listed in docs/team/CODEX_TASKS.md.

const Machines := preload("res://scripts/data/machines.gd")


static func make(path: String, size: Vector2i, color: Color, label := "") -> Node2D:
	var root := Node2D.new()
	if ResourceLoader.exists(path):
		var s := Sprite2D.new()
		s.texture = load(path)
		s.centered = false
		root.add_child(s)
		return root
	var r := ColorRect.new()
	r.size = size
	r.color = color
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(r)
	if label != "":
		root.add_child(text(label, Vector2(2, 1), Color(0, 0, 0, 0.7)))
	return root


## A battle machine: real art if the slot is filled, otherwise a blocky beast in its faction's colours.
static func machine(id: String, faces_left: bool) -> Node2D:
	var d: Dictionary = Machines.MACHINES[id]
	if ResourceLoader.exists(d.slot):
		var sprite_root := Node2D.new()
		var art := make(d.slot, Machines.SLOT_SIZE, Color.WHITE)
		if faces_left:
			art.scale.x = -1
			art.position.x = Machines.SLOT_SIZE.x
		# Keep the mirror offset local when scenes position the machine's slot.
		sprite_root.add_child(art)
		return sprite_root
	var p := Machines.PALETTE
	var own: Dictionary = d.get("colours", {})   # each machine's own scheme (machines.gd), else the faction's
	var main: Color = Color(own.main) if own.has("main") else (p.player_main if d.faction == "player" else p.rival_main)
	var trim: Color = Color(own.trim) if own.has("trim") else (p.player_trim if d.faction == "player" else p.rival_trim)
	var root := Node2D.new()
	var w := Machines.SLOT_SIZE.x
	# body parts as [x, y, w, h, colour], drawn facing right, mirrored for the enemy
	var parts := [
		[10, 30, 8, 16, p.frame_dark], [42, 30, 8, 16, p.frame_dark],   # legs
		[16, 30, 8, 16, p.frame], [46, 30, 8, 16, p.frame],
		[8, 16, 44, 16, main], [8, 26, 44, 4, trim],                     # body and stripe
		[0, 18, 10, 4, p.frame],                                         # tail
		[48, 6, 16, 14, main], [48, 16, 16, 4, p.frame],                 # head and jaw
		[58, 9, 3, 3, p.light],                                          # eye
	]
	for q in parts:
		var r := ColorRect.new()
		r.size = Vector2(q[2], q[3])
		r.position = Vector2(w - q[0] - q[2] if faces_left else q[0], q[1])
		r.color = q[4]
		root.add_child(r)
	root.add_child(text("%s %s" % [d.animal, d.size], Vector2(0, 46), Color(1, 1, 1, 0.6)))
	return root


static func text(s: String, pos: Vector2, color := Color.WHITE, size := 8) -> Label:
	var l := Label.new()
	l.text = s
	l.position = pos
	l.add_theme_color_override("font_color", color)
	l.add_theme_font_size_override("font_size", size)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l
