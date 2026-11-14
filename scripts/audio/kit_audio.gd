extends Node
## KitAudio (autoload): plays each machine's ability sounds and its AI voice lines.
##
## It never edits the kit scripts (those belong to the game feel lane). It watches for kit nodes
## entering the tree and listens to the two signals every kit already emits:
##   used(slot)        an ability starts: play its cast sound and, if the machine has been quiet
##                     for VOICE_GAP seconds, its voice line
##   impact(strength)  something landed hard: if an ability with a landing sound is in flight,
##                     play that landing sound now, so it hits on the slam frame
##   cue(name)         optional: a named moment the kit marks itself (the rhino's dash, catch, toss landing and
##                     each tremor stomp, 2026-11-05). Plays that kit's "cues" file, so nothing keys on impact
##                     strength (0.35 and 0.4 are too close, and being-hit sparks emit impact too)
## Files: res://audio/sfx/<machine>/<name>.wav and res://audio/voice/<machine>/<name>.ogg.
## A missing file is skipped quietly, so lines can be added one at a time.
## Buses come from res://default_bus_layout.tres: SFX, Voice, and Music (Music ducks under Voice).

const VOICE_GAP := 4.0   ## seconds a machine stays quiet after a callout, so mashing a key doesn't spam it
const LANDING_MIN := 0.7 ## impact strength that counts as the slam (ground pound sends 0.7, stampede finale 1.0)
const CUE_NUDGE := 0.03 ## +-3% pitch on cue sounds (the four tremor stomps in a row)
const HIT_WINDOW := 2.5 ## seconds after used(slot) that a "hits" slot sounds on every impact (each chest beat)

## Keyed by the kit script's class_name. "cast" plays on used(slot). "land" plays on the next impact after
## used(slot) at least "land_min" strong (default LANDING_MIN): the throw, landing or blast frame. "hits" plays
## on every impact for HIT_WINDOW seconds after used(slot). "voice" is the line for that slot. "cues" maps a
## cue(name) to a file; each plays with a small random pitch nudge (CUE_NUDGE) so repeats don't sound looped.
## Gorilla and fennec sounds: tools/audio/synth_kits.py (stand-ins).
const KITS := {
	"LobsterKit": {  # claw snap basic attack cues (Lobster session, 2026-11-06); tools/audio/lobster_claw_recorded.py
		"dir": "lobster",
		"cues": {"basic_snap": "basic_snap", "basic_whiff": "basic_whiff"},
	},
	"FalconKit": {  # dart basic attack cues from falcon_kit.gd (Falcon session, 2026-11-06); tools/audio/falcon_dart_recorded.py
		"dir": "falcon",
		"cues": {"dart_fire": "dart_fire", "dart_hit": "dart_hit", "dart_keen": "dart_keen", "dart_miss": "dart_miss"},
	},
	"HummingbirdKit": {  # needle, link and beak shot cues from hummingbird_kit.gd (Hummingbird session, 2026-11-06); tools/audio/hummingbird_recorded.py
		"dir": "hummingbird",
		"cues": {"needle_cast": "needle_cast", "needle_heal": "needle_heal", "needle_hit": "needle_hit", "needle_miss": "needle_miss",
			"link_on": "link_on", "link_break": "link_break", "beak_shot": "beak_shot", "beak_hit": "beak_hit", "beak_miss": "beak_miss"},
		"loops": {"link_hum": ["link_on", "link_break"]},  # the hum holds while the ruby link is up
	},
	"HippoKit": {  # bite basic attack cues from hippo_kit.gd (Hippo session, 2026-11-05); tools/audio/hippo_bite_recorded.py
		"dir": "hippo",
		"cues": {"bite": "bite", "bite_whiff": "bite_whiff"},
	},
	"WolfKit": {  # key 1 lunge cues from wolf_kit.gd (Wolf session, 2026-11-05); tools/audio/wolf_lunge_recorded.py
		"dir": "wolf",
		"cues": {"lunge_cast": "lunge_cast", "lunge_bite": "lunge_bite", "lunge_miss": "lunge_miss",
				"basic_bite": "basic_bite", "basic_whiff": "basic_whiff"},  # + basic attack (Wolf session, 2026-11-05)
	},
	"RhinoKit": {
		"dir": "rhino",
		"cast": {"2": "pound_rear"},
		"land": {"2": "pound_slam", "4": "pound_slam"},
		# cue(name) from rhino_kit.gd (game feel lane, 2026-11-05); files from tools/audio/rhino_tremor_recorded.py
		"cues": {"dash_cast": "dash_cast", "horn_catch": "horn_catch", "toss_land": "toss_land", "gore_land": "gore_land",  # the 3D horn chain's gore, front feet crash (2026-11-10)
				"tremor_stomp": "tremor_stomp",
				"jab_swing": "jab_swing", "jab_hit": "jab_hit"},  # basic attack (Rhino session, 2026-11-05)
		"voice": {"2": "ability_2"},  # "Ground's coming up!" (Preston's pick: v3 take 1, light)
	},
	"ApeKit": {  # the gorilla
		"dir": "ape",
		"cues": {"strike_swing": "strike_swing", "strike_hit": "strike_hit"},  # basic attack (Gorilla session, 2026-11-05)
		"cast": {"1": "shield_wind", "3": "bound_leap"},
		"land": {"1": "shield_up", "3": "bound_land", "4": "dome_slam"},
		"land_min": {"1": 0.2, "3": 0.7, "4": 0.8},  # shield throw 0.2, bound landing 0.7, the ult's dome beat 0.8
		# Key 4 is the chest beat ult since 2026-11-09 (Gorilla 3D lane): used("4"), beats at 0.3 and 0.15, then 0.8 as the
		# dome rises. Each beat plays chest_hit, and the 0.8 also plays dome_slam, which ends the beats. dome_rise is unused
		# now. "2" stays only while match_bot.gd still calls the old chest_beat() on 2 for bots.
		"hits": {"2": "chest_hit", "4": "chest_hit"},
		# "I've got you." / "Come and get it!" / "Coming in!" / "Nobody leaves."
		"voice": {"1": "ability_1", "2": "ability_2", "3": "ability_3", "4": "ability_4"},
	},
	"FennecKit": {
		"dir": "fennec",
		"cues": {"basic_cast": "basic_cast", "basic_hit": "basic_hit"},  # basic attack (Fennec session, 2026-11-05)
		"cast": {"1": "kick_wind", "2": "burst_charge", "3": "dig_in", "4": "boom_charge"},
		"land": {"1": "kick_sand", "2": "burst_blast", "3": "pop_out", "4": "boom_blast"},
		"land_min": {"1": 0.15, "2": 0.3, "3": 0.35, "4": 0.7},  # kick 0.2, burst 0.35, pop-out 0.4, blast 0.8
		# "Eat dust!" / "Hear that?" / "Follow me down!" / "Here comes the big one!" (Preston's picks, take A)
		"voice": {"1": "ability_1", "2": "ability_2", "3": "ability_3", "4": "ability_4"},
	},
}

var _players := {}     # file path -> its own player, so overlapping sounds don't cut each other off
var _pending := {}     # kit instance id -> slot waiting for its landing sound
var _quiet_until := {} # kit instance id -> time (s) the next callout is allowed
var _wired := {}       # kit instance ids already connected, so a kit is never connected twice
var _hitting := {}     # kit instance id -> [slot, time (s) its hits stop sounding]
var _loops := {}       # "kit instance id:file path" -> its looping player (cfg "loops": the link hum)


func _ready() -> void:
	get_tree().node_added.connect(_on_node_added)
	# A scene run directly (F6) can enter the tree before this autoload's _ready runs,
	# so also wire any kits that are already there.
	_wire_tree(get_tree().root)


func _wire_tree(node: Node) -> void:
	_on_node_added(node)
	for child in node.get_children():
		_wire_tree(child)


func _on_node_added(node: Node) -> void:
	var script := node.get_script() as Script
	if script == null or _wired.has(node.get_instance_id()):
		return
	var key := String(script.get_global_name())
	while not KITS.has(key) and script.get_base_script()!=null:
		script=script.get_base_script()
		key=String(script.get_global_name())
	if not KITS.has(key) or not (node.has_signal("used") or node.has_signal("cue")):
		return  # a kit needs used(slot) or cue(name); HippoKit (2026-11-05) only has cue
	var cfg: Dictionary=KITS[key]
	if node.get_script().resource_path.ends_with("/arena_gorilla_kit.gd"):
		cfg=cfg.duplicate(true)
		cfg["cast"]={"1":"shield_wind","3":"shield_wind"}
		cfg["land"]={"1":"shield_up","4":"dome_slam"}
		cfg["hits"]={}
		cfg["cues"]={"strike_swing":"strike_swing","strike_hit":"strike_hit","chest_contact":"chest_hit","drive_hit":"bound_land","grab_ground":"dome_slam","fling_grab":"shield_wind"}
	_wired[node.get_instance_id()] = true
	if node.has_signal("used"):
		node.connect("used", _on_used.bind(node, cfg))
	if node.has_signal("impact"):
		node.connect("impact", _on_impact.bind(node, cfg))
	if node.has_signal("cue") and KITS[key].has("cues"):
		node.connect("cue", _on_cue.bind(node, cfg))


func _on_used(slot: String, kit: Node, cfg: Dictionary) -> void:
	var id := kit.get_instance_id()
	var cast: Dictionary = cfg.get("cast", {})
	if cast.has(slot):
		play("res://audio/sfx/%s/%s.wav" % [cfg.dir, cast[slot]], &"SFX")
	if cfg.get("land", {}).has(slot):
		_pending[id] = slot
	var now := Time.get_ticks_msec() / 1000.0
	if cfg.get("hits", {}).has(slot):
		_hitting[id] = [slot, now + HIT_WINDOW]
	else:
		_hitting.erase(id)
	var lines: Dictionary = cfg.get("voice", {})
	if lines.has(slot) and now >= float(_quiet_until.get(id, 0.0)):
		if play("res://audio/voice/%s/%s.ogg" % [cfg.dir, lines[slot]], &"Voice"):
			_quiet_until[id] = now + VOICE_GAP


func _on_impact(strength: float, kit: Node, cfg: Dictionary) -> void:
	var id := kit.get_instance_id()
	var hit: Array = _hitting.get(id, [])
	if not hit.is_empty() and Time.get_ticks_msec() / 1000.0 <= float(hit[1]):
		play("res://audio/sfx/%s/%s.wav" % [cfg.dir, cfg.hits[hit[0]]], &"SFX", randf_range(0.94, 1.06))
	if not _pending.has(id):
		return
	var slot: String = _pending[id]
	if strength < float(cfg.get("land_min", {}).get(slot, LANDING_MIN)):
		return
	_pending.erase(id)
	play("res://audio/sfx/%s/%s.wav" % [cfg.dir, cfg.land[slot]], &"SFX")
	if not hit.is_empty() and hit[0] == slot:
		_hitting.erase(id)  # a slot's landing ends its hits: after the ult's dome beat, punches don't play chest_hit


func _on_cue(cue_name: String, kit: Node, cfg: Dictionary) -> void:
	var cues: Dictionary = cfg.cues
	if cues.has(cue_name):
		play("res://audio/sfx/%s/%s.wav" % [cfg.dir, cues[cue_name]], &"SFX", randf_range(1.0 - CUE_NUDGE, 1.0 + CUE_NUDGE))
	var loops: Dictionary = cfg.get("loops", {})
	for loop_name in loops:
		var ends: Array = loops[loop_name]  # [start cue, stop cue]
		if cue_name == ends[0] or cue_name == ends[1]:
			_loop(kit, "res://audio/sfx/%s/%s.wav" % [cfg.dir, loop_name], cue_name == ends[0])


## A held sound between two cues (the hummingbird's link hum, sound lane 2026-11-06): one looping player per kit and
## file, so two hummingbirds each hum their own link. The file loops on its own loop points (a WAV smpl chunk, which
## Godot's importer reads by default). The player is freed when its kit leaves the tree.
func _loop(kit: Node, path: String, on: bool) -> void:
	var key := "%d:%s" % [kit.get_instance_id(), path]
	var p: AudioStreamPlayer = _loops.get(key)
	if p == null and on and ResourceLoader.exists(path):
		p = AudioStreamPlayer.new()
		p.stream = load(path)
		p.bus = &"SFX"
		add_child(p)
		_loops[key] = p
		kit.tree_exiting.connect(_drop_loop.bind(key), CONNECT_ONE_SHOT)
	if p == null:
		return
	if on and not p.playing:
		p.play()
	elif not on:
		p.stop()


func _drop_loop(key: String) -> void:
	if _loops.has(key):
		_loops[key].queue_free()
		_loops.erase(key)


## Plays a file on a bus. Returns the player, or null when the file isn't there yet.
func play(path: String, bus: StringName, pitch: float = 1.0) -> AudioStreamPlayer:
	if not _players.has(path):
		_players[path] = null
		if ResourceLoader.exists(path):
			var p := AudioStreamPlayer.new()
			p.stream = load(path)
			p.bus = bus
			p.max_polyphony = 1 if bus == &"Voice" else 3
			add_child(p)
			_players[path] = p
	var player: AudioStreamPlayer = _players[path]
	if player:
		player.pitch_scale = pitch
		player.play()
	return player
