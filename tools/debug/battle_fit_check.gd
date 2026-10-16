extends SceneTree
## Every battle frame of every machine with art stays on screen in both battle slots (Claude, 2026-10-15).
## Places each machine through scripts/battle/stage.gd, the same functions battle.gd uses: its home row between moves,
## the step down while a taller clip plays (modelled frame by frame, including the Stage.STEP_TIME tween at the start
## of a clip). Measures each frame's highest opaque row on screen. Runs at every field scale a window can produce
## (the zoomed-out field, 2026-10-15: 1.0 at a 320x180 window, 0.5 to 0.8 at the usual sizes).
## FAIL: any frame cut by more rows than ALLOWED names for it. ALLOWED holds poses known to be too tall for the
## screen in either slot (the player slot cannot step down); each is a pose to fix, not a pass.
## Run: Godot --headless --path . --script res://tools/debug/battle_fit_check.gd

const Anim := preload("res://scripts/ui/machine_anim.gd")
const Stage := preload("res://scripts/battle/stage.gd")

# "<machine>/<clip>": rows a frame of it may lose off the top. Measured 2026-10-15 at scale 1 (a 320x180 window; the
# zoomed-out field cuts nothing); fix the pose, then delete the line.
const ALLOWED := {
	"kangaroo_m/kick": 7,   # kick/5 reaches 7 rows above the screen even at the player's row
	"pangolin_m/roll": 5,   # roll/6 likewise, 5 rows
}


func _initialize() -> void:
	var ok := true
	var scales := []
	for k in range(1, 13):   # window scales 1 to 12 (320x180 up to 3840x2160)
		var s := Stage.field_scale(k)
		if not scales.has(s):
			scales.append(s)
	for s in scales:
		var cut_any := false
		for id in DirAccess.get_directories_at("res://art/machines"):
			if not FileAccess.file_exists("res://art/machines/%s/anim/anim.json" % id) and not ResourceLoader.exists("res://art/machines/%s/views/e.png" % id):
				continue
			for is_player in [true, false]:
				var node := Anim.machine(id, not is_player)
				var home := Stage.home_y(node, is_player, s)
				node.position.y = home
				var steps := []
				var cuts := []
				var a := node.get_node_or_null("anim") as AnimatedSprite2D
				if a != null:
					var clips: Dictionary = a.get_meta("clips")
					for clip in a.sprite_frames.get_animation_names():
						var target := Stage.clip_y(node, is_player, clip, s)
						if target > home:
							steps.append("%s +%d" % [clip, target - home])
						var start := 0.0
						var worst := 0
						var worst_k := -1
						for k in a.sprite_frames.get_frame_count(clip):
							# where the node is when frame k first shows: still easing down during the first STEP_TIME
							var y := home + (target - home) * minf(1.0, start / Stage.STEP_TIME)
							var cut := ceili(-(y + Anim._top_row(a.sprite_frames.get_frame_texture(clip, k))) * s)
							if cut > worst:
								worst = cut
								worst_k = k
							start += float(clips[clip].ms[k]) / 1000.0
						var allowed: int = ALLOWED.get("%s/%s" % [id, clip], 0)
						if worst > allowed:
							ok = false
							cuts.append("FAIL %s/%d cut %d rows (allowed %d)" % [clip, worst_k, worst, allowed])
						elif worst > 0:
							cuts.append("known %s/%d cut %d rows (ALLOWED)" % [clip, worst_k, worst])
						cut_any = cut_any or worst > 0
				else:
					var cut := maxi(0, ceili(-(home + int(node.get_meta("top_y", 0))) * s))
					if cut > 0:
						ok = false
						cuts.append("FAIL view cut %d rows" % cut)
				if s >= 1.0 or not cuts.is_empty():
					print("battle_fit_check: scale %.3f %-11s %-6s home feet row %3d | steps down: %s | %s" % [
						s, id, "player" if is_player else "enemy", roundi((home + int(node.get_meta("feet_y"))) * s),
						", ".join(steps) if steps else "none", "; ".join(cuts) if cuts else "nothing cut"])
				node.free()
		print("battle_fit_check: scale %.3f %s" % [s, "cuts within ALLOWED" if cut_any else "nothing cut"])
	print("battle_fit_check: %s" % ("PASS" if ok else "FAIL"))
	quit(0 if ok else 1)
