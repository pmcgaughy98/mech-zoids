extends "res://tools/debug/gorilla_turn_contacts.gd"
func _process_modification_with_delta(delta: float) -> void:
	if not driver or driver.combat_weight>.001 or animation_player.current_animation!="Gorilla_Walk_v17":
		anchors.clear()
		previous_phase.clear()
		return
	super._process_modification_with_delta(delta)
