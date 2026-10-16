extends SceneTree
## Checks imported machine view art (art/machines/<id>/views/), so eight views stay one consistent machine
## and nothing jumps when the camera turns. Machines with no imported art are skipped.
## Run: Godot --headless --path . --script res://tools/debug/view_art_check.gd

const Views := preload("res://scripts/machines/machine_views.gd")
const Machines := preload("res://scripts/data/machines.gd")
var fails := 0


func _initialize() -> void:
	var checked := 0
	for id in Machines.MACHINES:
		if not FileAccess.file_exists("res://art/machines/%s/views/views.json" % id):
			continue
		checked += 1
		var info := Views.view_info(id)
		print("%s: canvas %s, feet at %s" % [id, info.size, info.anchor])
		_ok("%s: feet point is the exact middle, so mirrored views stand on it too" % id, info.anchor.x * 2 == info.size.x)
		var pal := {}
		for h in info.palette:
			pal[Color(h).to_html(false)] = true
		var heights := []
		for dir in Views.DIRS:
			var pick := Views.resolve(id, dir)
			_ok("%s %s: has art or a mirror (%s)" % [id, dir, "mirror" if pick.flip else ("art" if pick.path != "" else "none")], pick.path != "")
			if pick.path == "" or pick.flip:
				continue
			var img := Image.load_from_file(ProjectSettings.globalize_path(pick.path))
			_ok("%s %s: canvas is %s" % [id, dir, info.size], img.get_size() == info.size)
			var bottom := -1
			var top := img.get_height()
			var off := 0
			var xs := []
			for y in img.get_height():
				for x in img.get_width():
					var c := img.get_pixel(x, y)
					if c.a > 0.5:
						bottom = max(bottom, y)
						top = min(top, y)
						if not pal.has(c.to_html(false)):
							off += 1
			for y in range(bottom - 3, bottom + 1):
				for x in img.get_width():
					if img.get_pixel(x, y).a > 0.5:
						xs.append(x)
			var mid: float = (xs.min() + xs.max()) / 2.0
			_ok("%s %s: stands on the feet line (bottom row %d)" % [id, dir, bottom], bottom == info.anchor.y)
			_ok("%s %s: feet centred on the feet point (%.1f vs %d)" % [id, dir, mid, info.anchor.x], absf(mid - info.anchor.x) <= 1.0)
			_ok("%s %s: only the machine's own colours (%d stray px)" % [id, dir, off], off <= 3)
			heights.append(bottom - top + 1)
		if heights.size() > 1:
			_ok("%s: no view is much taller or shorter than the rest (%s)" % [id, str(heights)], heights.max() <= heights.min() * 1.35)
	print("\nview_art_check: %d machine(s) with art. %s" % [checked, "PASS" if fails == 0 else "FAIL (%d)" % fails])
	quit(1 if fails > 0 else 0)


func _ok(what: String, good: bool) -> void:
	if not good:
		print("  FAIL  " + what)
		fails += 1
