extends RefCounted
## Walking for the pilot in rooms and on the field. Arrow keys move; on autopilot the pilot walks to a goal.

const SPEED := 80.0  # pixels per second


static func step(pos: Vector2, delta: float, goal, bounds: Rect2) -> Vector2:
	var dir: Vector2
	if Run.autopilot:
		if goal == null:
			return pos
		dir = (goal - pos).limit_length(1.0) if pos.distance_to(goal) > 1.0 else Vector2.ZERO
	else:
		dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	var next := pos + dir * SPEED * delta
	return next.clamp(bounds.position, bounds.end)
