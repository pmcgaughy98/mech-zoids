extends SceneTree
## Camera kick check (camera lane, 2026-11-06; Preston: "Kick the camera along the punch"). Headless: puts a camera
## at the chase camera's pitch, distance and field of view, kicks it along three ground directions and logs the
## picture's shift in game pixels each frame: it must be 2 px on the first frame, point the way the punch goes on
## screen, and be back at 0 by the end. Then a kick on top of a shake must also settle to 0.
## Run: godot --headless --fixed-fps 60 --path <project> --script <this file>

const PITCH := 30.0
const DIST := 6.5
const FRAMES := 14 ## at 60 fps, a little past the 0.15 s kick

var cam: Camera3D
var fails := 0


func _initialize() -> void:
	cam = Camera3D.new()
	cam.fov = 75.0
	var p := deg_to_rad(PITCH)
	var pos := Vector3(0.0, sin(p) * DIST, cos(p) * DIST)
	cam.transform = Transform3D(Basis.looking_at(-pos), pos)  # look_at errors before the tree is up
	root.add_child(cam)
	cam.current = true
	_run.call_deferred()


func _run() -> void:
	var m := KitFeel.metres_per_px(cam)
	print("kick_check: viewport %s, %.4f m a pixel at %.1f m" % [str(root.get_visible_rect().size), m, DIST])
	# On screen the picture should move: right -> +x, away from the camera -> up (+y here).
	for c in [["right", Vector3.RIGHT, Vector2(1, 0)], ["away", Vector3.FORWARD, Vector2(0, 1)],
			["toward and left", Vector3(-1, 0, 1).normalized(), Vector2(-1, -0.5).normalized()]]:  # toward the camera is squashed by sin 30 on screen
		KitFeel.kick(cam, c[1])
		var first := Vector2.ZERO
		var peak := 0.0
		var log_px: Array = []
		for i in FRAMES:
			await process_frame  # reads the frame before the shaker's own _process, so a kick can show one frame late
			var picture := -Vector2(cam.h_offset, cam.v_offset) / m  # the picture moves against the camera
			if first == Vector2.ZERO and picture.length() > 0.001:
				first = picture
			peak = maxf(peak, picture.length())
			log_px.append(snappedf(picture.length(), 0.01))
		var ok := absf(first.length() - 2.0) < 0.05 and first.normalized().dot(c[2]) > 0.99 \
				and absf(peak - first.length()) < 0.01 and is_zero_approx(cam.h_offset) and is_zero_approx(cam.v_offset)
		fails += 0 if ok else 1
		print("  %s: first frame %.2f px toward (%.2f, %.2f), want 2 px toward (%.2f, %.2f); px by frame %s; end (%.4f, %.4f) %s"
				% [c[0], first.length(), first.normalized().x, first.normalized().y, c[2].x, c[2].y, str(log_px),
				cam.h_offset, cam.v_offset, "OK" if ok else "FAIL"])
	KitFeel.shake(cam, 0.35)
	KitFeel.kick(cam, Vector3.RIGHT)
	for i in 90:
		await process_frame
	var settled := is_zero_approx(cam.h_offset) and is_zero_approx(cam.v_offset)
	fails += 0 if settled else 1
	print("  kick on a shake: after 1.5 s (%.4f, %.4f) %s" % [cam.h_offset, cam.v_offset, "OK" if settled else "FAIL"])
	print("kick_check: %d failures" % fails)
	quit(1 if fails > 0 else 0)
