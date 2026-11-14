extends MatchHud
## Current player HUD plus four allies/five opponents. No fictitious wave or boss timer.
func _top(vs: Vector2) -> void:
	var cx := floorf(vs.x * 0.5)
	_plate(Rect2(cx - 70, 2, 140, 18), false, false)
	_text(_canvas, Vector2(cx - 65, 4), "5V5 FOUNDATION / TRAINING", GOLD)
	_text(_canvas, Vector2(cx - 65, 12), "3 LANES / DRAFT / NO WAVES", DIM)

func _kda_panel(vs: Vector2) -> void:
	_text(_canvas, Vector2(3, vs.y - 20), "F6 CALL TRAINING BODIES", DIM, 2)
	_text(_canvas, Vector2(3, vs.y - 12), "F8 ROSTER / B RECALL", DIM, 2)

