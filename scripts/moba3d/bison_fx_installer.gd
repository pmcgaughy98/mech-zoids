extends Node
## Attaches the bison's smooth effects (bison effects lane, 2026-11-14) to every bison kit in the scene: bison_fx.gd
## beside each BisonKit, as gorilla_fx_installer.gd does for the gorilla. A child node of scenes/moba3d/arena_play.tscn
## since Preston's "also turn on" (2026-11-14, relayed by the bison 3D lane). It replaces no kit logic and the kit's own
## fx_on stays false. The kit would only hang the effects at its first cast, so the footfall dust and the cooldown stacks
## would wait for one; this attaches them as soon as the body is on. Remove the node to turn the effects off.
## The bison fx launcher (scenes/moba3d/bison_fx_arena.tscn) runs its own stand-in and stub kit, so this stays out there.
const FX := "res://scripts/moba3d/bison_fx.gd"
const KIT := "res://scripts/moba3d/bison_kit.gd"
const FX_NAME := "BisonFx"

var _kit_script: Script


func _ready() -> void:
	if get_parent().get_node_or_null("BisonFxStandIn") != null:
		return  # the launcher has its own stand-in effects
	_kit_script = load(KIT) if ResourceLoader.exists(KIT) else null
	if _kit_script == null:
		return
	get_tree().node_added.connect(_on_added)
	_install(get_parent())


func _is_kit(node: Node) -> bool:
	return node != null and node.get_script() == _kit_script


func _on_added(node: Node) -> void:
	if _is_kit(node):
		_attach.call_deferred(node, 0)


## Deferred: the match calls use_model right after the kit's install, so the body is on by the end of the frame. A body
## that is still missing is waited for, a few frames at most.
func _attach(kit: Node, tries: int) -> void:
	if not is_instance_valid(kit) or not kit.is_inside_tree() or not _is_kit(kit):
		return
	var player := kit.get_parent() as Node3D
	if player == null or kit.get_node_or_null(FX_NAME) != null or player.get_node_or_null(FX_NAME) != null:
		return
	if player.get("body") == null:
		if tries < 30:
			await get_tree().process_frame
			_attach(kit, tries + 1)
		return
	var script: Variant = load(FX)
	if not (script is Script) or not script.can_instantiate():
		push_warning("BisonFxInstaller: %s did not compile; the bison runs without its effects" % FX)
		return
	var fx: Node = script.new()
	fx.name = FX_NAME
	kit.add_child(fx)  # under the kit, so a swap to another machine frees it with the kit
	fx.setup(kit, player)
	if "_fx_hung" in kit:
		kit.set("_fx_hung", true)  # so the kit never hangs a second copy if its fx_on is turned on later


func _install(node: Node) -> void:
	if _is_kit(node):
		_attach(node, 0)
	for child in node.get_children():
		_install(child)
