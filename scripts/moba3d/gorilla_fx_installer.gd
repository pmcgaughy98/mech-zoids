extends Node
## Attaches the gorilla's smooth effects (gorilla effects lane, 2026-11-11) to every gorilla kit in the scene.
## A child node of scenes/moba3d/arena_play.tscn since Preston's "Yes, use it" on the ult before/after (2026-11-11).
## It only adds gorilla_ult_fx.gd beside the kit; no kit logic is replaced. Remove the node to turn the effect off.
## scenes/moba3d/gorilla_fx_arena.tscn is the same match with start_on_gorilla on.
const FX := "res://scripts/moba3d/gorilla_ult_fx.gd"
@export var start_on_gorilla := false ## the gorilla launcher sets this; the main match keeps its own starting machine
@export var slam_hits := true ## slice 2 (cracks under the basic slam and the grab slam): on everywhere since Preston's "Yes, turn on" (2026-11-12); false here turns only that part off
@export var fault_line := true ## slice 7: Reactor Fault Line with height (rock slabs, reactor glow and arc) in place of Codex's flat sliding crater on key 2; on everywhere since Preston's "Yes, turn on" (2026-11-13); false brings Codex's look back
@export var aura_disc := true ## slice 4: the smooth ring under the gorilla in place of the kit's pixel ring; on everywhere since Preston's "Yes, turn on" (2026-11-12); false brings the pixel ring back
@export var step_dust := true ## slice 4: a small dust puff where a hand or foot plants while walking; on everywhere since Preston's "Yes, turn on" (2026-11-12)
@export var drive_dust := true ## slice 5: tall dust plumes and chunks along Drive Slam (key 3); on everywhere since Preston's "Yes, turn on" (2026-11-12)
@export var team_tint := true ## slice 6: an enemy gorilla's ring rim, ripple rims and cage edge take its team colour; on everywhere since Preston's "Yes, turn on" (2026-11-13)
@export var windup_glow := true ## slice 8: the chest glows in four steps during the ult's chest hits and runs down the arms into the slam; on in the main match since 2026-11-14 (Preston)
@export var cage_wall := false ## slice 9: rock pylons under the ult cage, one per panel, on a floor line; a broken panel's pylon shatters; on in the launcher only, until Preston picks


func _ready() -> void:
	get_tree().node_added.connect(_on_added)
	_install(get_parent())
	if start_on_gorilla:
		_start_gorilla.call_deferred()


func _start_gorilla() -> void:
	var arena := get_parent()
	if arena.has_method("set_machine"):
		arena.set_machine("gorilla")


func _on_added(node: Node) -> void:
	if node is ApeKit:
		_attach.call_deferred(node)


func _attach(node: Node) -> void:
	if not is_instance_valid(node) or not node.is_inside_tree() or not (node is ApeKit):
		return
	if node.get_node_or_null("GorillaUltFX") != null or not (node.get_parent() is Node3D):
		return
	var fx: Node = load(FX).new()
	fx.name = "GorillaUltFX"
	node.add_child(fx)
	fx.setup(node, node.get_parent())
	fx.slam_hits = slam_hits
	fx.fault_line = fault_line
	fx.aura_disc = aura_disc
	fx.step_dust = step_dust
	fx.drive_dust = drive_dust
	fx.team_tint = team_tint
	fx.windup_glow = windup_glow
	fx.cage_wall = cage_wall


func _install(node: Node) -> void:
	_attach(node)
	for child in node.get_children():
		if child.name != "GorillaUltFX":
			_install(child)
