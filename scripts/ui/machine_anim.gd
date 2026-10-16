class_name MachineAnim
extends RefCounted
## Battle sprites with animation (animation pass 3, 2026-10-12). Builds an AnimatedSprite2D from
## res://art/machines/<id>/anim/anim.json (frame picks and per-frame durations from
## reports/Gorilla mech animation foundation.md, packed by tools/art/export_anim.py); without that, the
## machine's side view from its views folder; without that, the drawn placeholder from slot.gd.
## Returns a Node2D carrying meta "width", "height", "feet_y" (the ground row inside the art) and, when
## animated, a child named "anim". A mirrored machine (faces_left) is flipped about the node's origin, so
## callers place it by its right edge.

const Machines := preload("res://scripts/data/machines.gd")
const Slot := preload("res://scripts/ui/slot.gd")


static func machine(id: String, faces_left: bool) -> Node2D:
	var root := Node2D.new()
	var anim_path := "res://art/machines/%s/anim/anim.json" % id
	var view_path := "res://art/machines/%s/views/e.png" % id
	var w: int = Machines.SLOT_SIZE.x
	var h: int = Machines.SLOT_SIZE.y
	var feet: int = Machines.SLOT_SIZE.y
	var top := 0   # the highest opaque row in any frame (2026-10-15, for stage_y)
	var clip_tops := {}   # the same per clip
	if FileAccess.file_exists(anim_path):
		var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(anim_path))
		var frames := SpriteFrames.new()
		frames.remove_animation("default")
		top = int(meta.size[1])
		for clip in meta.clips:
			var c: Dictionary = meta.clips[clip]
			frames.add_animation(clip)
			frames.set_animation_speed(clip, 10.0)   # a frame duration of 1.0 is 100 ms
			frames.set_animation_loop(clip, c.loop != "once")
			var clip_top := int(meta.size[1])
			for k in c.frames.size():
				var tex: Texture2D = load("res://art/machines/%s/anim/%s" % [id, c.frames[k]])
				frames.add_frame(clip, tex, float(c.ms[k]) / 100.0)
				clip_top = mini(clip_top, _top_row(tex))
			clip_tops[clip] = clip_top
			top = mini(top, clip_top)
		var a := AnimatedSprite2D.new()
		a.name = "anim"
		a.sprite_frames = frames
		a.centered = false
		a.set_meta("clips", meta.clips)
		a.play("idle" if frames.has_animation("idle") else frames.get_animation_names()[0])
		a.animation_finished.connect(func() -> void:
			if a.animation != "death" and a.sprite_frames.has_animation("idle"):
				a.play("idle"))
		root.add_child(a)
		w = int(meta.size[0])
		h = int(meta.size[1])
		feet = int(meta.feet_y) + 1
	elif ResourceLoader.exists(view_path):
		var s := Sprite2D.new()
		s.texture = load(view_path)
		s.centered = false
		root.add_child(s)
		w = s.texture.get_width()
		h = s.texture.get_height()
		feet = h
		top = _top_row(s.texture)
		var vmeta_path := "res://art/machines/%s/views/views.json" % id
		if FileAccess.file_exists(vmeta_path):
			var vm: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(vmeta_path))
			feet = int(vm.anchor[1]) + 1
	else:
		root.add_child(Slot.machine(id, false))
	if faces_left:
		root.scale.x = -1
	root.set_meta("width", w)
	root.set_meta("height", h)
	root.set_meta("feet_y", feet)
	root.set_meta("top_y", top)
	root.set_meta("clip_tops", clip_tops)
	return root


## The highest opaque row of a frame (a very large row when the frame is empty or failed to load, so it never
## pulls a machine down).
static func _top_row(tex: Texture2D) -> int:
	if tex == null:
		push_warning("MachineAnim: a battle frame failed to load (not imported yet?); treated as empty")
		return 1 << 20
	var img := tex.get_image()
	if img.is_compressed():
		img.decompress()
	var used := img.get_used_rect()
	return used.position.y if used.size.y > 0 else 1 << 20


## The highest opaque row of `clip`; for a machine without that clip (or without animation), of all its art.
## (scripts/battle/stage.gd uses these to keep machines on screen.)
static func clip_top(node: Node2D, clip: String) -> int:
	var tops: Dictionary = node.get_meta("clip_tops", {})
	return tops[clip] if tops.has(clip) else int(node.get_meta("top_y", 0))


## The highest opaque row over the listed clips the machine has (all its art when it has none of them).
static func clips_top(node: Node2D, clips: Array) -> int:
	var tops: Dictionary = node.get_meta("clip_tops", {})
	var top := 1 << 20
	for c in clips:
		if tops.has(c):
			top = mini(top, tops[c])
	return top if top < 1 << 20 else int(node.get_meta("top_y", 0))


## Seconds from the start of `clip` to its strike frame (the frame already past the target), and its full length.
static func clip_times(node: Node2D, clip: String) -> Array:
	var a := node.get_node_or_null("anim") as AnimatedSprite2D
	if a == null or not a.sprite_frames.has_animation(clip):
		return [0.12, 0.5]
	var c: Dictionary = a.get_meta("clips")[clip]
	var total := 0.0
	var strike := 0.0
	for k in c.ms.size():
		if k == int(c.strike):
			strike = total
		total += float(c.ms[k]) / 1000.0
	if int(c.strike) < 0:
		strike = total * 0.5
	return [strike, total]


## Plays `clip` on an animated machine; returns false when the machine has no such clip.
static func play(node: Node2D, clip: String) -> bool:
	var a := node.get_node_or_null("anim") as AnimatedSprite2D
	if a == null or clip == "" or not a.sprite_frames.has_animation(clip):
		return false
	a.play(clip)
	return true
