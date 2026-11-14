extends SceneTree
var failures:=0
func _initialize() -> void:run.call_deferred()
func frames(n: int) -> void:
 for i in n:await process_frame
func check(value: bool,name: String) -> void:
 print("PASS " if value else "FAIL ",name)
 if not value:failures+=1
func run() -> void:
 var scene=load("res://scenes/moba3d/rhino_art_arena.tscn")
 if scene==null:quit(1);return
 var play: Node3D=scene.instantiate();root.add_child(play);await frames(20)
 play.set_machine("rhino");await frames(20)
 var actor: Node3D=play.player;actor.input_override=Vector2.ZERO
 for unit in get_nodes_in_group("match_unit"):
  var brain=unit.get_node_or_null("Brain")
  if brain!=null:brain.set_process(false)
  if unit.get("bot")==true:unit.input_override=Vector2.ZERO
 var kit: RhinoKit=actor.get_node("Kit");var fx=kit.get_node_or_null("RhinoPaintedFX")
 check(fx!=null,"real arena variant installs rhino effects")
 check(kit.get_script().resource_path.ends_with("/rhino_kit.gd"),"base kit unchanged")
 check(actor.body.has_clip("ground_pound"),"registered body has pound clip")
 actor.position=Vector3.ZERO;actor.facing=Vector3.FORWARD;actor.body.snap_facing(actor.facing)
 kit.ground_pound();await frames(24)
 check(fx.event_log.filter(func(row):return row.name=="pound_slam").size()==1,"real match slam drives one art event")
 check(float(actor.cooldowns.get("2",0))>0,"real match still owns cooldown")
 await frames(170)
 check(fx.live.is_empty(),"real match effects expire")
 var ref=weakref(fx);play.set_machine("fennec");await frames(20)
 check(ref.get_ref()==null,"machine swap frees old rhino effects")
 check(not play.player.get_node("Kit") is RhinoKit,"other kit remains its own type")
 play.queue_free();await frames(4);MechModel3D.clear_templates()
 print("RHINO_ART_MATCH_COMPLETE failures=",failures);quit(1 if failures else 0)
