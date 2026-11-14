extends SceneTree
## Sound lane check: the buses exist, Music ducks under Voice, the rhino, gorilla and fennec files load, a rhino
## ground pound (the kit's own signals) starts the rear sound, the voice line and the slam, and each gorilla and
## fennec ability starts its callout and its cast sound, and its landing or hit sound on its own impact.
## Run: godot --headless --path . --script res://tools/debug/check_kit_audio.gd
## The kits print errors here ("Node not found: Sprite", "Invalid access ... on Window") because they run
## without their bodies. Expected; only the ok / FAIL lines count.

const FILES := [
	"res://audio/sfx/rhino/pound_rear.wav",
	"res://audio/sfx/rhino/pound_slam.wav",
	"res://audio/voice/rhino/ability_2.ogg",
	"res://audio/voice/rhino/intro.ogg",
	"res://audio/voice/ape/ability_1.ogg",
	"res://audio/voice/ape/ability_2.ogg",
	"res://audio/voice/ape/ability_3.ogg",
	"res://audio/voice/ape/ability_4.ogg",
	"res://audio/voice/ape/intro.ogg",
	"res://audio/voice/fennec/ability_1.ogg",
	"res://audio/voice/fennec/ability_2.ogg",
	"res://audio/voice/fennec/ability_3.ogg",
	"res://audio/voice/fennec/ability_4.ogg",
	"res://audio/voice/fennec/intro.ogg",
]

var _fails := 0
var _done := false


func _initialize() -> void:
	for b in ["Music", "SFX", "Voice"]:
		if AudioServer.get_bus_index(b) < 0:
			_fail("bus missing: " + b)
	var music := AudioServer.get_bus_index("Music")
	if music >= 0:
		var c := AudioServer.get_bus_effect(music, 0) as AudioEffectCompressor
		if c == null or c.sidechain != &"Voice":
			_fail("the Music bus has no compressor keyed to Voice")
		else:
			print("ok   Music ducks under Voice (threshold %.0f dB, ratio %.0f:1)" % [c.threshold, c.ratio])
	for path in FILES:
		var s := load(path) as AudioStream
		if s == null:
			_fail("cannot load " + path)
		else:
			print("ok   %s  %.2f s" % [path, s.get_length()])


## Runs on the first frame, once the tree is live (during _initialize nothing is inside it yet).
func _process(_delta: float) -> bool:
	if _done:
		return true
	_done = true
	var kit: Node = load("res://scripts/moba3d/rhino_kit.gd").new()
	var ka: Node = root.get_node_or_null("KitAudio")
	if ka:
		print("info KitAudio autoload present; the kit spawns after it (node_added path)")
		root.add_child(kit)
	else:
		print("info no autoload in this mode; the kit goes in first, like an F6 scene run (scan path)")
		root.add_child(kit)
		ka = load("res://scripts/audio/kit_audio.gd").new()
		ka.name = "KitAudio"
		root.add_child(ka)

	kit.emit_signal("used", "2")
	_expect(ka, "res://audio/sfx/rhino/pound_rear.wav", "rear plays when ground pound starts")
	_expect(ka, "res://audio/voice/rhino/ability_2.ogg", "\"Ground's coming up!\" plays")
	kit.emit_signal("impact", 0.35)  # a horn toss landing must not trigger the slam
	var slam: AudioStreamPlayer = ka._players.get("res://audio/sfx/rhino/pound_slam.wav")
	if slam and slam.playing:
		_fail("slam fired on a light impact")
	kit.emit_signal("impact", 0.7)
	_expect(ka, "res://audio/sfx/rhino/pound_slam.wav", "slam plays on the slam-frame impact")

	# The gorilla: each ability starts its callout (the 4 s voice gap is reset between casts).
	var ape: Node = load("res://scripts/moba3d/ape_kit.gd").new()
	root.add_child(ape)
	_kit_slots(ka, ape, "ApeKit", "gorilla")
	# The chest beat ult on 4 (2026-11-09): no dome sound on the press, a chest hit on each beat (0.3, 0.15), the 0.8
	# dome beat plays the chest hit and the dome slam, and a punch after it plays no chest hit.
	var chest: AudioStreamPlayer = ka._players["res://audio/sfx/ape/chest_hit.wav"]
	var dome: AudioStreamPlayer = ka._players["res://audio/sfx/ape/dome_slam.wav"]
	chest.stop()
	dome.stop()
	ape.emit_signal("used", "4")
	var rise: AudioStreamPlayer = ka._players.get("res://audio/sfx/ape/dome_rise.wav")
	ape.emit_signal("impact", 0.3)
	var beat_ok: bool = chest.playing and not dome.playing and (rise == null or not rise.playing)
	chest.stop()
	ape.emit_signal("impact", 0.15)
	beat_ok = beat_ok and chest.playing and not dome.playing
	chest.stop()
	ape.emit_signal("impact", 0.8)
	var dome_ok: bool = chest.playing and dome.playing
	chest.stop()
	ape.emit_signal("impact", 0.3)
	if not beat_ok:
		_fail("ult beats play the chest hit, with no dome sound before the dome beat")
	elif not dome_ok:
		_fail("the ult's 0.8 dome beat plays the chest hit and the dome slam")
	elif chest.playing:
		_fail("a punch after the ult's dome beat plays no chest hit")
	else:
		print("ok   gorilla ult: chest hit per beat, dome slam on the 0.8 beat, then the beats stop")

	# The fennec: each ability starts its callout, the same way.
	var fennec: Node = load("res://scripts/moba3d/fennec_kit.gd").new()
	root.add_child(fennec)
	_kit_slots(ka, fennec, "FennecKit", "fennec")

	# Other kits' hard hits (gorilla 0.8, fennec sonic boom 0.8) must not fire the rhino slam.
	slam = ka._players["res://audio/sfx/rhino/pound_slam.wav"]
	slam.stop()
	ape.emit_signal("impact", 0.8)
	fennec.emit_signal("impact", 0.8)
	if slam.playing:
		_fail("another kit's hit fired the rhino slam")
	else:
		print("ok   gorilla and fennec hits do not fire the rhino slam")
	# cue(name): the rhino's named moments (dash, catch, toss landing, tremor stomps), 2026-11-05.
	for cue_name in ["dash_cast", "horn_catch", "toss_land", "tremor_stomp", "jab_swing", "jab_hit", "gore_land"]:
		var path := "res://audio/sfx/rhino/%s.wav" % cue_name
		kit.emit_signal("cue", cue_name)
		if ResourceLoader.exists(path):
			_expect(ka, path, "cue %s plays" % cue_name)
		elif ka._players.has(path):
			print("ok   cue %s is wired (file not installed yet)" % cue_name)
		else:
			_fail("cue %s is not wired" % cue_name)
	# ApeKit basic attack cues (2026-11-05).
	var ape_cues: Node = load("res://scripts/moba3d/ape_kit.gd").new()
	root.add_child(ape_cues)
	ka._on_node_added(ape_cues)  # safe twice (KitAudio skips wired kits)
	for cue_name in ["strike_swing", "strike_hit"]:
		ape_cues.emit_signal("cue", cue_name)
		_expect(ka, "res://audio/sfx/ape/%s.wav" % cue_name, "gorilla cue %s plays" % cue_name)
	# HippoKit bite cues (2026-11-05): a kit with cue(name) but no used(slot).
	var hippo_cues: Node = load("res://scripts/moba3d/hippo_kit.gd").new()
	root.add_child(hippo_cues)
	ka._on_node_added(hippo_cues)  # safe twice (KitAudio skips wired kits)
	for cue_name in ["bite", "bite_whiff"]:
		hippo_cues.emit_signal("cue", cue_name)
		_expect(ka, "res://audio/sfx/hippo/%s.wav" % cue_name, "hippo cue %s plays" % cue_name)
	# FennecKit basic attack cues (2026-11-05).
	var fennec_cues: Node = load("res://scripts/moba3d/fennec_kit.gd").new()
	root.add_child(fennec_cues)
	ka._on_node_added(fennec_cues)  # safe twice (KitAudio skips wired kits)
	for cue_name in ["basic_cast", "basic_hit"]:
		fennec_cues.emit_signal("cue", cue_name)
		_expect(ka, "res://audio/sfx/fennec/%s.wav" % cue_name, "fennec cue %s plays" % cue_name)
	# LobsterKit claw snap cues (2026-11-06).
	var lobster_cues: Node = load("res://scripts/moba3d/lobster_kit.gd").new()
	root.add_child(lobster_cues)
	ka._on_node_added(lobster_cues)  # safe twice (KitAudio skips wired kits)
	for cue_name in ["basic_snap", "basic_whiff"]:
		lobster_cues.emit_signal("cue", cue_name)
		_expect(ka, "res://audio/sfx/lobster/%s.wav" % cue_name, "lobster cue %s plays" % cue_name)
	# WolfKit lunge cues (2026-11-05).
	var wolf: Node = load("res://scripts/moba3d/wolf_kit.gd").new()
	root.add_child(wolf)
	ka._on_node_added(wolf)  # safe twice (KitAudio skips wired kits); a bare kit logs an onready error, harmless here
	for cue_name in ["lunge_cast", "lunge_bite", "lunge_miss", "basic_bite", "basic_whiff"]:
		wolf.emit_signal("cue", cue_name)
		_expect(ka, "res://audio/sfx/wolf/%s.wav" % cue_name, "wolf cue %s plays" % cue_name)
	var hum: Node = load("res://scripts/moba3d/hummingbird_kit.gd").new()
	root.add_child(hum)
	ka._on_node_added(hum)  # safe twice (KitAudio skips wired kits)
	for cue_name in ["needle_cast", "needle_heal", "needle_hit", "needle_miss", "link_on", "link_break", "beak_shot", "beak_hit", "beak_miss"]:
		hum.emit_signal("cue", cue_name)
		_expect(ka, "res://audio/sfx/hummingbird/%s.wav" % cue_name, "hummingbird cue %s plays" % cue_name)
	hum.emit_signal("cue", "link_on")
	var hum_loop: AudioStreamPlayer = ka._loops.get("%d:res://audio/sfx/hummingbird/link_hum.wav" % hum.get_instance_id())
	if hum_loop == null or not hum_loop.playing:
		_fail("link_on starts the link hum")
	elif (hum_loop.stream as AudioStreamWAV).loop_mode != AudioStreamWAV.LOOP_FORWARD:
		_fail("link_hum.wav loops forward (its smpl chunk)")
	else:
		print("ok   link_on starts the link hum, and it loops forward")
	hum.emit_signal("cue", "link_break")
	if hum_loop != null and hum_loop.playing:
		_fail("link_break stops the link hum")
	else:
		print("ok   link_break stops the link hum")
	var falcon: Node = load("res://scripts/moba3d/falcon_kit.gd").new()
	root.add_child(falcon)
	ka._on_node_added(falcon)  # safe twice (KitAudio skips wired kits)
	for cue_name in ["dart_fire", "dart_hit", "dart_keen", "dart_miss"]:
		falcon.emit_signal("cue", cue_name)
		_expect(ka, "res://audio/sfx/falcon/%s.wav" % cue_name, "falcon cue %s plays" % cue_name)
	print("RESULT: ", "PASS" if _fails == 0 else "%d FAIL" % _fails)
	quit(_fails)
	return true


## Each slot: the callout and cast sound on used(slot); a "hits" sound on an impact; a "land" sound that
## ignores an impact just under its land_min and plays on one at it.
func _kit_slots(ka: Node, kit: Node, key: String, who: String) -> void:
	var cfg: Dictionary = load("res://scripts/audio/kit_audio.gd").KITS[key]
	for slot in ["1", "2", "3", "4"]:
		ka._quiet_until.clear()
		kit.emit_signal("used", slot)
		_expect(ka, "res://audio/voice/%s/ability_%s.ogg" % [cfg.dir, slot], "%s slot %s callout plays" % [who, slot])
		if cfg.get("cast", {}).has(slot):
			_expect(ka, _sfx(cfg, cfg.cast[slot]), "%s slot %s cast sound plays" % [who, slot])
		if cfg.get("hits", {}).has(slot):
			kit.emit_signal("impact", 0.3)
			_expect(ka, _sfx(cfg, cfg.hits[slot]), "%s slot %s sounds on each impact" % [who, slot])
		if cfg.get("land", {}).has(slot):
			var need: float = cfg.get("land_min", {}).get(slot, 0.7)
			var land := _sfx(cfg, cfg.land[slot])
			kit.emit_signal("impact", need - 0.05)
			var early: AudioStreamPlayer = ka._players.get(land)
			if early and early.playing:
				_fail("%s slot %s landing fired on a weaker impact" % [who, slot])
			kit.emit_signal("impact", need)
			_expect(ka, land, "%s slot %s landing sound plays on its impact (%.2f)" % [who, slot, need])


func _sfx(cfg: Dictionary, name: String) -> String:
	return "res://audio/sfx/%s/%s.wav" % [cfg.dir, name]


func _expect(ka: Node, path: String, what: String) -> void:
	var p: AudioStreamPlayer = ka._players.get(path)
	if p and p.playing:
		print("ok   %s (bus %s)" % [what, p.bus])
	else:
		_fail(what)


func _fail(what: String) -> void:
	print("FAIL ", what)
	_fails += 1
