extends Node
## Optional art-enabled Arena variant. Does not replace kit logic or other mechs.
func _ready() -> void:
 get_tree().node_added.connect(on_added)
 install(get_tree().current_scene if get_tree().current_scene!=null else get_parent())
 start_rhino.call_deferred()
func start_rhino() -> void:
 var arena=get_parent()
 if not arena.has_method("set_machine"):return
 arena.set_machine("rhino")
 # The base arena's --rhino/test startup can still be the legacy sprite.
 # The art variant explicitly chooses the already registered native body.
 if arena.player.body==null:arena.player.use_model("rhino")
func on_added(node: Node) -> void:
 if node is RhinoKit:attach.call_deferred(node)
func attach(node: Node) -> void:
 if not is_instance_valid(node) or not node.is_inside_tree():return
 if node is RhinoKit and node.get_node_or_null("RhinoPaintedFX")==null:
  var fx=load("res://scripts/moba3d/rhino_painted_fx.gd").new()
  fx.name="RhinoPaintedFX";node.add_child(fx);fx.setup(node,node.get_parent())
 if node is RhinoKit and node.get_node_or_null("RhinoPixelFX")==null:
  var px=load("res://scripts/moba3d/rhino_release_fx.gd").new()
  px.name="RhinoPixelFX";node.add_child(px);px.setup(node,node.get_parent())
func install(node: Node) -> void:
 attach(node)
 for child in node.get_children():
  if not child.name in ["RhinoPaintedFX","RhinoPixelFX"]:install(child)
