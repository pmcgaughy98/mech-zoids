extends Node
## MapAudio (autoload): the map's ambience and its match event sounds.
##
## Ambience: a looping 3D bed is attached at runtime to each map Marker3D whose name holds a zone word
## (BEDS), or to any Node3D in a group "ambient_<zone>", so the sound shifts as the camera crosses the
## map. Events: any node that emits a signal named in EVENTS is heard; a Node3D emitter is heard where
## it stands. The game feel lane owns the emitters and the map scenes; this script only listens.
## Files: res://audio/ambience/<zone>.ogg and res://audio/sfx/map/<file>.wav. A missing file is skipped.

const BEDS := {  # zone -> words in a marker's name
	"base": ["Core"],
	"lane": ["Tower"],
	"jungle": ["Camp"],
	"plaza": ["Plaza"],
	"stream": ["Stream", "River"],
}
const EVENTS := {  # signal -> [file, heard at the emitter's position]
	"tower_shot": ["tower_shot", true],
	"tower_shot_hit": ["tower_hit", true],
	"tower_destroyed": ["tower_down", true],
	"core_destroyed": ["core_down", false],
	"wave_spawned": ["wave_spawn", false],
	"minion_hit": ["minion_hit", true],
	"camp_aggro": ["camp_aggro", true],
	"respawned": ["respawn", true],  # at base, so only a camera there hears it
	"recall_started": ["recall_start", true],
	"recall_finished": ["recall_arrive", true],
	"pit_taken": ["pit_taken", true],  # map lane: ArenaPit.pit_taken(team), heard at the pit
}
## match_ended(won: bool) plays win.wav or lose.wav on the Music bus.
## Match music: the node that has match_ended (the MatchDirector, made when a match starts) also starts one looping
## track on the Music bus; it fades out when that match ends, before the stinger, or when the node leaves the tree.

## Hums: the map lane's turning heads (arena_blockout.gd names them <structure>Gem: BlueTowerGem, RedCoreGem...)
## each get a looping hum, silent while the head is hidden (set_structure_down hides it when the structure falls).
const HUMS := {"TowerGem": "turret_hum", "CoreGem": "core_hum"}  ## name ending -> res://audio/ambience/<file>.ogg
const HUM_UNIT := 7.0
const HUM_MAX := 26.0
const HUM_PITCH := 1.0186  ## the loops' 8 s scan and 0.5 Hz post passes, sped up to the heads' 0.8 rad/s turn

const BED_UNIT := 14.0   ## metres within which a bed plays at full level
const BED_MAX := 45.0    ## past this a bed is silent, so neighbouring zones hand over to each other
const EVENT_UNIT := 12.0
const EVENT_MAX := 70.0
## Voices, after SMITE 2 and Doom (docs/reference/moba-audio-synthesis-2026-11-04.md): SMITE 1 capped sounds
## at 32 and a lane fight still cut gameplay sounds, so every one-shot here has a rank. When all voices are
## busy, the oldest of the lowest-ranked sounds is cut, never one that outranks the newcomer.
const MAX_VOICES := 32
const PRIORITY := {
	"core_destroyed": 100, "tower_destroyed": 90, "pit_taken": 80, "wave_spawned": 70, "tower_shot": 60, "tower_shot_hit": 60,
	"camp_aggro": 50, "respawned": 50, "recall_started": 40, "recall_finished": 40, "minion_hit": 10,
}
const MATCH_END_RANK := 100
const MATCH_MUSIC := "res://audio/music/match_theme.ogg"  ## "Epic boss battle", Juhani Junkala, CC0 (audio/CREDITS.md); Preston's pick 2026-11-16
const MATCH_MUSIC_DB := -14.0  ## the file is -6.9 LUFS and dense; with the Music bus's -8 dB it sits near -29, under the kit sounds
const MUSIC_FADE := 0.6
const SINGLE := ["minion_hit"]  ## one at a time per emitter: a minion's new hit replaces its last one
const PITCH_NUDGE := {"minion_hit": 0.12, "tower_shot": 0.03, "tower_shot_hit": 0.04}  ## repeats never sound identical

var _streams := {}  # path -> AudioStream, or null when the file isn't there
var _wired := {}    # instance ids already handled
var _active: Array[Node] = []  # one-shots playing now, oldest first
var _singles := {}  # "emitter id:signal" -> its playing one-shot, for SINGLE signals
var _last_global := {}  # signal -> msec it last played, for events heard everywhere
var _music: AudioStreamPlayer = null  # the match loop: outside _active, so it never takes a voice and stop_all() leaves it


func _ready() -> void:
	get_tree().node_added.connect(_on_node_added)
	_scan(get_tree().root)  # a scene run directly (F6) is already in the tree


func _scan(node: Node) -> void:
	_on_node_added(node)
	for child in node.get_children():
		_scan(child)


func _on_node_added(node: Node) -> void:
	var id := node.get_instance_id()
	if _wired.has(id) or node == self:
		return
	if node is Node3D:
		var zone := _zone_of(node as Node3D)
		if zone != "":
			_wired[id] = true
			_add_bed(node as Node3D, zone)
		for ending in HUMS:
			if String(node.name).ends_with(ending):
				_wired[id] = true
				_add_hum(node as Node3D, HUMS[ending])
	for sig_name in EVENTS.keys() + ["match_ended"]:
		if node.has_signal(sig_name):
			_wired[id] = true
			_listen(node, sig_name)


func _zone_of(node: Node3D) -> String:
	for zone in BEDS:
		if node.is_in_group("ambient_" + zone):
			return zone
		if node is Marker3D:
			for word in BEDS[zone]:
				if word in String(node.name):
					return zone
	return ""


func _add_bed(at: Node3D, zone: String) -> void:
	var stream := _stream("res://audio/ambience/%s.ogg" % zone)
	if stream == null:
		return
	if stream is AudioStreamOggVorbis:
		stream.loop = true
	var p := AudioStreamPlayer3D.new()
	p.name = "AmbientBed"
	p.stream = stream
	p.bus = &"Ambience"
	p.unit_size = BED_UNIT
	p.max_distance = BED_MAX
	_place_bed.call_deferred(at, p)  # deferred: the marker may still be entering the tree


func _place_bed(at: Node3D, p: AudioStreamPlayer3D) -> void:
	if not is_instance_valid(at) or not at.is_inside_tree():
		p.free()
		return
	at.add_child(p)
	p.play(randf() * p.stream.get_length())  # random start, so two beds of one zone never play in step


## Hiding a node never silences a sound under it, so the hum follows its head's visibility itself.
func _add_hum(head: Node3D, file: String) -> void:
	var stream := _stream("res://audio/ambience/%s.ogg" % file)
	if stream == null:
		return
	if stream is AudioStreamOggVorbis:
		stream.loop = true
	var p := AudioStreamPlayer3D.new()
	p.name = "Hum"
	p.stream = stream
	p.bus = &"Ambience"
	p.unit_size = HUM_UNIT
	p.max_distance = HUM_MAX
	p.pitch_scale = HUM_PITCH
	head.visibility_changed.connect(_follow_head.bind(head, p))
	_place_hum.call_deferred(head, p)


func _place_hum(head: Node3D, p: AudioStreamPlayer3D) -> void:
	if not is_instance_valid(head) or not head.is_inside_tree():
		p.free()
		return
	head.add_child(p)
	_follow_head(head, p)


func _follow_head(head: Node3D, p: AudioStreamPlayer3D) -> void:
	if not is_instance_valid(p) or not p.is_inside_tree():
		return
	if not head.is_visible_in_tree():
		p.stop()
	elif not p.playing:
		p.play(randf() * p.stream.get_length())  # random start, so no two heads hum in step


## Connects whatever arguments the signal carries; only match_ended's first one (won) is used.
func _listen(node: Node, sig_name: String) -> void:
	var argc := 0
	for s in node.get_signal_list():
		if s.name == sig_name:
			argc = s.args.size()
			break
	if sig_name == "match_ended":
		if argc >= 1:
			var on_end := _on_match_ended
			node.connect(sig_name, on_end.unbind(argc - 1) if argc > 1 else on_end)
			_start_music(node)
		else:
			push_warning("MapAudio: match_ended needs a won argument; skipped on " + str(node.get_path()))
		return
	var on_event := _on_event.bind(node, sig_name)
	node.connect(sig_name, on_event.unbind(argc) if argc > 0 else on_event)  # unbind(0) is an error


func _on_event(node: Node, sig_name: String) -> void:
	var e: Array = EVENTS[sig_name]
	if not e[1]:  # heard everywhere: one event from two emitters at once (a wave from each gate) plays once
		var now := Time.get_ticks_msec()
		if now - int(_last_global.get(sig_name, -100000)) < 300:
			return
		_last_global[sig_name] = now
	var stream := _stream("res://audio/sfx/map/%s.wav" % e[0])
	if stream == null:
		return
	var p: Node
	if e[1] and node is Node3D and node.is_inside_tree():
		var p3 := AudioStreamPlayer3D.new()
		p3.unit_size = EVENT_UNIT
		p3.max_distance = EVENT_MAX
		p3.position = (node as Node3D).global_position  # this autoload has no transform, so this is global
		p = p3
	else:
		p = AudioStreamPlayer.new()
	var key := "%d:%s" % [node.get_instance_id(), sig_name]
	if sig_name in SINGLE and is_instance_valid(_singles.get(key)):
		_stop(_singles[key])
	if not _make_room(PRIORITY[sig_name]):
		p.free()
		return
	if sig_name in SINGLE:
		p.set_meta("single", key)
		_singles[key] = p
	var nudge: float = PITCH_NUDGE.get(sig_name, 0.0)
	_play(p, stream, &"SFX", PRIORITY[sig_name], randf_range(1.0 - nudge, 1.0 + nudge))


func _on_match_ended(won: bool) -> void:
	_stop_music(_music)  # first, so the stinger is the last thing added
	var stream := _stream("res://audio/sfx/map/%s.wav" % ("win" if won else "lose"))
	if stream and _make_room(MATCH_END_RANK):
		_play(AudioStreamPlayer.new(), stream, &"Music", MATCH_END_RANK, 1.0)


## One loop at a time, whichever emitter came first; that emitter leaving the tree (back to the menu, a reload) stops it.
func _start_music(emitter: Node) -> void:
	if is_instance_valid(_music):
		return
	var stream := _stream(MATCH_MUSIC)
	if stream == null:
		return
	if "loop" in stream:
		stream.set("loop", true)  # the .import says so too; this keeps it looping if that is ever reset
	_music = AudioStreamPlayer.new()
	_music.stream = stream
	_music.bus = &"Music"
	_music.volume_db = MATCH_MUSIC_DB
	add_child(_music)
	_music.play()
	emitter.tree_exiting.connect(_stop_music.bind(_music), CONNECT_ONE_SHOT)


func _stop_music(p) -> void:  # untyped: the emitter can leave after the fade has already freed its player
	if not is_instance_valid(p):
		return
	if _music == p:
		_music = null
	if p.is_queued_for_deletion():
		return
	if not is_inside_tree():
		p.queue_free()
		return
	var fade := create_tween()
	fade.tween_property(p, "volume_db", -60.0, MUSIC_FADE)
	fade.tween_callback(p.queue_free)


## True when a sound of `rank` may play: a voice is free, or the oldest of the lowest-ranked sounds playing
## ranks no higher than it and is cut to make room.
func _make_room(rank: int) -> bool:
	if _active.size() < MAX_VOICES:
		return true
	var victim: Node = null
	for p in _active:  # oldest first, so the first of the lowest rank is the oldest of that rank
		if victim == null or int(p.get_meta("rank")) < int(victim.get_meta("rank")):
			victim = p
	if int(victim.get_meta("rank")) > rank:
		return false
	_stop(victim)
	return true


## Silences every one-shot (a match reset; also the headless check, where sounds never finish).
func stop_all() -> void:
	for p in _active.duplicate():
		_stop(p)


func _play(p: Node, stream: AudioStream, bus: StringName, rank: int, pitch: float) -> void:
	p.set("stream", stream)
	p.set("bus", bus)
	p.set("pitch_scale", pitch)
	p.set_meta("rank", rank)
	add_child(p)
	p.call("play")
	_active.append(p)
	p.connect("finished", _stop.bind(p))


func _stop(p: Node) -> void:
	_active.erase(p)
	var key: String = p.get_meta("single", "")
	if _singles.get(key) == p:
		_singles.erase(key)
	p.queue_free()


func _stream(path: String) -> AudioStream:
	if not _streams.has(path):
		_streams[path] = load(path) if ResourceLoader.exists(path) else null
	return _streams[path]
