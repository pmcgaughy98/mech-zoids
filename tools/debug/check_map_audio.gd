extends SceneTree
## Map sound check: the files load, beds attach to the arena's marker names and loop, the turning heads hum
## only while shown, and each match
## event signal starts its sound. The map has no towers or waves yet, so a stand-in node emits them.
## Run: godot --headless --path . --script res://tools/debug/check_map_audio.gd

const BEDS := ["lane", "jungle", "plaza", "stream", "base", "turret_hum", "core_hum"]
const SFX := ["tower_shot", "tower_hit", "tower_down", "core_down", "wave_spawn", "minion_hit",
	"camp_aggro", "respawn", "recall_start", "recall_arrive", "win", "lose"]
const EVENTS := {  # signal -> file it should play
	"tower_shot": "tower_shot", "tower_shot_hit": "tower_hit", "tower_destroyed": "tower_down",
	"core_destroyed": "core_down", "wave_spawned": "wave_spawn", "minion_hit": "minion_hit",
	"camp_aggro": "camp_aggro", "respawned": "respawn", "recall_started": "recall_start",
	"recall_finished": "recall_arrive",
}

const VOICES := 32  # MapAudio.MAX_VOICES

var _fails := 0
var _frame := 0
var _markers: Node3D
var _heads: Node3D


func _initialize() -> void:
	if AudioServer.get_bus_index("Ambience") < 0:
		_fail("no Ambience bus")
	for b in BEDS:
		var s := load("res://audio/ambience/%s.ogg" % b) as AudioStream
		if s == null:
			_fail("cannot load bed " + b)
		else:
			print("ok   bed %-7s %.1f s" % [b, s.get_length()])
	for name in SFX:
		var s := load("res://audio/sfx/map/%s.wav" % name) as AudioStream
		if s == null:
			_fail("cannot load " + name)
		else:
			print("ok   %-14s %.2f s" % [name, s.get_length()])


func _process(_delta: float) -> bool:
	_frame += 1
	if _frame == 1:  # the arena's marker names, plus one stream marker by group
		_markers = Node3D.new()
		for n in ["BlueCore", "BlueTower", "BlueCamp1", "RedCamp2", "Plaza", "BluePit"]:
			var m := Marker3D.new()
			m.name = n
			_markers.add_child(m)
		var w := Marker3D.new()
		w.name = "Water"
		w.add_to_group("ambient_stream")
		_markers.add_child(w)
		root.add_child(_markers)
		_heads = Node3D.new()  # the arena's turning heads, as arena_blockout.gd names them
		for n in ["BlueTowerGem", "RedCoreGem"]:
			var h := Node3D.new()
			h.name = n
			_heads.add_child(h)
		root.add_child(_heads)
		return false

	for m in _markers.get_children():  # frame 2: the deferred beds are in
		var bed := m.get_node_or_null("AmbientBed") as AudioStreamPlayer3D
		if m.name == "BluePit":
			if bed:
				_fail("BluePit got a bed; it has no zone yet")
			else:
				print("ok   BluePit has no bed (no zone assigned yet)")
		elif bed == null or not bed.playing:
			_fail("no playing bed on " + m.name)
		else:
			print("ok   %-9s -> %s on %s, loop %s" % [m.name, bed.stream.resource_path.get_file(), bed.bus, bed.stream.loop])

	for h in _heads.get_children():  # a hum under each head, silent while hidden (set_structure_down)
		var want: String = "turret_hum.ogg" if "Tower" in String(h.name) else "core_hum.ogg"
		var hum := h.get_node_or_null("Hum") as AudioStreamPlayer3D
		if hum == null or not hum.playing or hum.stream.resource_path.get_file() != want:
			_fail("no playing %s on %s" % [want, h.name])
			continue
		h.visible = false
		var hushed := not hum.playing
		h.visible = true
		if hushed and hum.playing:
			print("ok   %-12s -> %s on %s, loop %s, silent while hidden, back when shown" % [h.name, want, hum.bus, hum.stream.loop])
		else:
			_fail("%s hum does not follow the head's visibility" % h.name)

	var ma: Node = root.get_node_or_null("MapAudio")
	if ma == null:
		_fail("MapAudio autoload missing")
		return _end()
	var stand_in := Node3D.new()
	stand_in.position = Vector3(5, 0, 3)
	for sig in EVENTS:
		if sig == "tower_shot":  # one signal with an argument, to prove arguments are tolerated
			stand_in.add_user_signal(sig, [{"name": "target", "type": TYPE_OBJECT}])
		else:
			stand_in.add_user_signal(sig)
	stand_in.add_user_signal("match_ended", [{"name": "won", "type": TYPE_BOOL}])
	root.add_child(stand_in)

	for sig in EVENTS:
		ma.stop_all()  # headless audio never finishes a sound, so clear the voices per event
		var before := ma.get_child_count()
		if sig == "tower_shot":
			stand_in.emit_signal(sig, null)
		else:
			stand_in.emit_signal(sig)
		var p: Node = ma.get_child(ma.get_child_count() - 1) if ma.get_child_count() > before else null
		if p == null or not p.get("playing") or p.get("stream").resource_path.get_file() != EVENTS[sig] + ".wav":
			_fail("%s did not start %s.wav" % [sig, EVENTS[sig]])
		else:
			var where: String = "at the emitter" if p is AudioStreamPlayer3D and p.position == stand_in.position else "non-positional"
			print("ok   %-16s -> %s.wav (%s)" % [sig, EVENTS[sig], where])
	ma.stop_all()
	var n := ma.get_child_count()
	stand_in.emit_signal("wave_spawned")  # the other gate, same moment
	if ma.get_child_count() != n:
		_fail("a second wave_spawned in the same moment played again")
	else:
		print("ok   wave_spawned from two gates at once -> played once")
	ma.stop_all()
	stand_in.emit_signal("match_ended", true)
	var last: Node = ma.get_child(ma.get_child_count() - 1)
	if last.get("stream").resource_path.get_file() == "win.wav" and last.get("bus") == &"Music":
		print("ok   match_ended(true) -> win.wav on Music")
	else:
		_fail("match_ended did not play win.wav on Music")

	# Priority (SMITE 2, Doom): a crowd of minion hits never cuts or blocks a tower or core sound.
	ma.stop_all()
	ma._last_global.clear()
	var minions: Array[Node3D] = []
	for i in 40:
		var m := Node3D.new()
		m.add_user_signal("minion_hit")
		root.add_child(m)
		minions.append(m)
		m.emit_signal("minion_hit")
	if ma._active.size() != VOICES:
		_fail("40 minion hits should fill all %d voices, got %d" % [VOICES, ma._active.size()])
	stand_in.emit_signal("tower_destroyed")
	var tower: Node = ma._active.back()
	if tower.get("stream").resource_path.get_file() == "tower_down.wav" and tower.get("playing"):
		print("ok   all %d voices busy with minion hits, and tower_down still gets one" % VOICES)
	else:
		_fail("tower_down did not get a voice over minion hits")
	stand_in.emit_signal("core_destroyed")
	var core: Node = ma._active.back()
	for m in minions:
		m.emit_signal("minion_hit")
	if core.get("stream").resource_path.get_file() == "core_down.wav" and ma._active.has(core) and ma._active.has(tower):
		print("ok   core_down and tower_down survive 40 more minion hits")
	else:
		_fail("minion hits cut a tower or core sound")
	ma.stop_all()
	for i in 5:
		minions[0].emit_signal("minion_hit")
	if ma._active.size() == 1:
		print("ok   one minion's 5 hits take one voice (each replaces the last)")
	else:
		_fail("one minion's 5 hits took %d voices" % ma._active.size())
	return _end()


func _end() -> bool:
	print("RESULT: ", "PASS" if _fails == 0 else "%d FAIL" % _fails)
	quit(_fails)
	return true


func _fail(what: String) -> void:
	print("FAIL ", what)
	_fails += 1
