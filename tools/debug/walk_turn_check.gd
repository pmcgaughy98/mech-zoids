extends SceneTree
## Walk turn check (game feel lane, 2026-11-05). Turns a walking machine a full circle a degree at a time, one walk
## frame every 6 steps, then snaps it from e straight to w. At each mirror flip (into or out of sw, w, nw) it logs the
## frame shown and the physical step: the frame, or the frame plus half a loop when mirrored, since a mirrored view
## shows the far legs as the near ones. A jump of more than one step at a flip is the up foot swapping sides.
## Saves each flip's frame before and after (as shown, mirror applied) as flip<k>_a.png and flip<k>_b.png.
## Run: godot --path . -s res://tools/debug/walk_turn_check.gd -- --who=ape --out=<dir>   (needs a renderer, not --headless)
const DS := preload("res://scripts/moba3d/directional_sprite_3d.gd")


func _initialize() -> void:
	var who := "ape"
	var out := "user://walk_turn_check"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--who="):
			who = a.trim_prefix("--who=")
		elif a.begins_with("--out="):
			out = a.trim_prefix("--out=")
	DirAccess.make_dir_recursive_absolute(out)
	var holder := Node3D.new()
	root.add_child(holder)
	var d = DS.new()
	d.sprite_frames = load("res://art/machines/%s/%s_frames.tres" % [who, who])
	holder.add_child(d)
	var steps: Array[Vector3] = []
	for i in 361:
		steps.append(Vector3(sin(deg_to_rad(i)), 0.0, cos(deg_to_rad(i))))
	steps.append(Vector3(1, 0, 0))  # then a snap straight across, e to w
	steps.append(Vector3(-1, 0, 0))
	var lines := PackedStringArray()
	var flips := 0
	var swaps := 0
	var last_phase := -1
	for i in steps.size():
		if i > 0 and i % 6 == 0 and i < 361:
			d.frame = (d.frame + 1) % d.sprite_frames.get_frame_count(d.animation)
		var was_m: bool = d.mirrored
		var before: Image = _shown(d) if i > 0 else null
		d.show_facing(steps[i], Basis.IDENTITY, true)
		var c: int = d.sprite_frames.get_frame_count(d.animation)
		var phase: int = (d.frame + ((c >> 1) if d.mirrored else 0)) % c
		if last_phase >= 0 and d.mirrored != was_m:
			flips += 1
			var step := (phase - last_phase + c) % c
			if step > 1:
				swaps += 1
			lines.append("flip %d at step %d: to %s%s frame %d, physical step %d -> %d%s" % [flips, i, d.view, " mirrored" if d.mirrored else "", d.frame, last_phase, phase, "  FOOT SWAP" if step > 1 else ""])
			before.save_png(out.path_join("flip%d_a.png" % flips))
			_shown(d).save_png(out.path_join("flip%d_b.png" % flips))
		last_phase = phase
	lines.append("%s: %d mirror flips while walking, %d foot swaps" % [who, flips, swaps])
	var fa := FileAccess.open(out.path_join("log.txt"), FileAccess.WRITE)
	fa.store_string("\n".join(lines) + "\n")
	fa.close()
	print("\n".join(lines))
	quit()


func _shown(d) -> Image:
	var img: Image = d.sprite_frames.get_frame_texture(d.animation, d.frame).get_image().duplicate()
	if img.is_compressed():
		img.decompress()
	if d.flip_h:
		img.flip_x()
	return img
