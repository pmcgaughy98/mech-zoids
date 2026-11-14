extends Node
## Attaches the rhino's effects to every rhino kit in the scene (rhino 3D lane, 2026-11-11, after Preston:
## "add rhino ffects work its good"). Meant to be a child node of scenes/moba3d/arena_play.tscn, like
## GorillaFxInstaller. It adds the same two observers the art arena (rhino_art_installer.gd) adds, under the same node
## names, and does not change the starting machine or any kit logic. Remove the node to turn the effects off.
const PAINTED := "res://scripts/moba3d/rhino_painted_fx.gd"
const SMOOTH := "res://scripts/moba3d/rhino_release_fx.gd" ## brace release and hold, tremor, charge pulses, finale, paw scrapes


func _ready() -> void:
	get_tree().node_added.connect(_on_added)
	_install(get_parent())


func _on_added(node: Node) -> void:
	if node is RhinoKit:
		_attach.call_deferred(node)


func _attach(node) -> void:  # untyped: a kit freed before this deferred call (a machine swap) arrives as a freed Object
	if not is_instance_valid(node) or not node.is_inside_tree() or not (node is RhinoKit):
		return
	if not (node.get_parent() is Node3D):
		return
	if node.get_node_or_null("RhinoPaintedFX") == null:
		var fx: Node = load(PAINTED).new()
		fx.name = "RhinoPaintedFX"
		node.add_child(fx)
		fx.setup(node, node.get_parent())
	if node.get_node_or_null("RhinoPixelFX") == null:
		var px: Node = load(SMOOTH).new()
		px.name = "RhinoPixelFX"
		node.add_child(px)
		px.setup(node, node.get_parent())


func _install(node: Node) -> void:
	_attach(node)
	for child in node.get_children():
		if not child.name in ["RhinoPaintedFX", "RhinoPixelFX"]:
			_install(child)
