extends Control
var targeting: Node3D
func _draw() -> void:
	if is_instance_valid(targeting):targeting.draw_overlay(self)
