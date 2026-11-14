class_name MechModel3D
extends Node3D
## A machine's rigged 3D body (game feel lane, 2026-11-09; Preston: "Yes, start stage 1"). Plan:
## D:/dev/_scratch/game_feel/match_3d_models_plan_2026-11-09.md.
## It loads its kind's GLB, turns to the machine's facing, picks idle / walk / run by ground speed, and plays one-shot
## actions that pause the locomotion until they end. It emits each clip event at its time (event), and carries the
## hit feel: feel_offset for the shove (nudge), a short flash, and hitstop (freeze). One row per kind in ROWS; a kind
## with no row stays a sprite (MachineTestPlayer.use_model). The sprite keeps running hidden under a body, so a kit
## that still times itself on sprite frames works on until its lane moves it to the body.
## Clip names are matched without the kind prefix and the _vNN suffix ("Gorilla_Slam_v25" and "Gorilla_Slam" are both
## "Slam"), so new GLB rounds don't touch the kits. Event times come from <glb>.events.json beside the GLB (the format
## is in the plan); a row's "events" is the stand-in until that file exists.

signal event(clip: String, name: String, damage: bool) ## an action clip reached one of its events
signal step(clip: String, name: String) ## a locomotion loop passed one of its footfalls (row key "steps"); for sound and dust, separate from `event`
signal action_finished(clip: String) ## an action clip ended (or was replaced by stop_action / another action)

const ROWS := {
	"gorilla": {
		"glb": "res://art/arena_models/gorilla.glb",
		"clips": {"Idle":"Gorilla_Idle_v25","Walk":"Gorilla_Walk_v25","Swat_Left":"Gorilla_Swat_Left_v25","Swat_Right":"Gorilla_Swat_Right_v25","Slam":"Gorilla_Slam_v25","Shield_Ally":"Gorilla_Shield_Ally_CodexTrial","Shield_Self":"Gorilla_Shield_Self_CodexTrial","Ult":"Gorilla_ChestBeat_Ult_Codex_ExitTrial","GrabSlam":"Gorilla_GrabSlam_CodexTrial","Fling_Whiff":"Gorilla_Fling_Whiff_v25","DriveBrace":"Gorilla_ShieldDrive_Brace_Trial","Drive":"Gorilla_ShieldDrive_Drive_Trial","DriveHit":"Gorilla_ShieldDrive_Hit_Trial","DriveBrake":"Gorilla_ShieldDrive_Brake_Trial"},
		"scale": 1.0,
		"turn_rate": 16.0,
		"idle": "Idle",
		"walk": "Walk",
		"walk_speed": 3.5, ## m/s the walk was authored at (gorilla lane, 2026-11-09)
		"rest_height": 1.7, ## top of the mesh at rest, m (measured on v26 by the gorilla lane)
		"aliases": {"Ult": "ChestBeat_Ult"}, ## v27's unversioned ult name, v26's name
		## Stand-in until gorilla_kit_v27.events.json lands: the gorilla lane's times, in seconds (2026-11-09).
		## [name, time, damage]; drum strikes are sound only and stay with the kit's audio.
		"events": {
			"Swat_Left": [["hit", 0.30, true]],
			"Swat_Right": [["hit", 0.30, true]],
			"Slam": [["hit", 0.417, true]],
			"Fling": [["grab", 0.18, false], ["release", 0.38, false]],
			"Fling_Whiff": [["clap", 0.18, false]],
			"ChestBeat_Ult": [["beat", 0.42, true], ["beat", 0.75, true], ["beat", 1.27, true]],
			"Hit_Heavy": [["replant", 0.20, false]],
			"Shield_Ally": [["release",.25,false]],
			"Shield_Self": [["release",.25,false]],
			"Ult": [["drum",50.0/120.0,false],["beat",.42,false],["drum",64.0/120.0,false],["drum",77.0/120.0,false],["drum",.75,false],["beat",.75,false],["beat",1.27,false]],
		},
		"peaks": {"Slam": 2.51, "Fling": 2.94, "ChestBeat_Ult": 3.06}, ## top of the mesh during the clip, m
	},
	"rhino": {"glb":"res://art/arena_models/rhino.glb","scale":1.0,"turn_rate":12.0,"idle":"idle","walk":"walk","walk_speed":.48,"run":"charge","run_speed":1.47,"run_above":7.0,"rest_height":1.7},
}

var kind := ""
var feel_offset := Vector3.ZERO ## world-space nudge on the whole body (the shove); eased back by nudge()
var lift := 0.0 ## extra height on the whole body, set by kits (the scrap comet lifts the pangolin so its bigger shell sits on the floor)
var action := "" ## the one-shot clip playing (short name), or "" while the body walks or idles
var anim: AnimationPlayer
var skeleton: Skeleton3D
var _row: Dictionary = {}
var _model: Node3D
var _clips := {} ## short name -> the GLB's own clip name
var _events := {} ## short name -> [[name, time, damage], ...], sorted by time
var _peaks := {}
var _rest := 1.7
var _walk_speed := 3.5
var _bridge := "" ## the walk-start or walk-stop clip playing between idle and walk (short name), or ""
var _step_clip := "" ## the loop whose footfalls are being counted, and where it was last frame
var _step_pos := 0.0
var _side := "" ## the directional band playing: "", "strafe" or "back" (kept for the 10 degree hysteresis)
var _run_speed := 0.0
var _hold := false ## the action is a held loop (play_hold): it repeats until stopped or replaced
var external_clock := false
var _action_full := ""
var _fired := 0
var _rate := 1.0
var _freeze := 0.0
const MECH_LOOK := preload("res://scripts/moba3d/mech_look.gd") ## the look lane's set_flash (no class_name)
var _flash_amount := 0.0
var _flash_tw: Tween
var _nudge_tw: Tween


static var _templates := {} ## GLB path -> the generated scene, built once and copied for every body of that kind
static func clear_templates() -> void:
	for template in _templates.values():
		if is_instance_valid(template):template.free()
	_templates.clear()


static func has_row(k: String) -> bool:
	return ROWS.has(k)


## The GLB's scene, generated once per path. An imported GLB loads as a PackedScene; one in a .gdignore'd folder
## (the model_catalog workspaces, where the art lanes export) is read at runtime with GLTFDocument, as their test
## drivers do.
static func _template(path: String) -> Node3D:
	if _templates.has(path) and is_instance_valid(_templates[path]):
		return _templates[path]
	var root: Node3D = null
	if ResourceLoader.exists(path):
		var ps := load(path) as PackedScene
		if ps != null:
			root = ps.instantiate() as Node3D
	elif FileAccess.file_exists(path):
		var doc := GLTFDocument.new()
		var state := GLTFState.new()
		if doc.append_from_file(path, state) == OK:
			root = doc.generate_scene(state, 120.0) as Node3D
	if root != null:
		_templates[path] = root
	return root


## Puts kind k's body on machine (named "Body"), replacing any body it had. Returns null, with no body left on the
## machine, when k has no row or its GLB won't load.
static func attach(machine: Node3D, k: String) -> MechModel3D:
	var old := machine.get_node_or_null("Body")
	if old != null:
		machine.remove_child(old)
		old.queue_free()
	if not ROWS.has(k):
		var profile: Dictionary=load("res://scripts/moba3d/arena_roster.gd").profile(k)
		if not profile.is_empty() and not profile.has("body"):
			var base: MechModel3D=load("res://scripts/moba3d/arena_base_body.gd").new()
			base.name="Body";machine.add_child(base)
			if base.configure(k):return base
			machine.remove_child(base);base.queue_free()
			return null
		if profile.is_empty():return null
	# The rhino's kit drives its own clips once the registered GLB has the horn chain (rhino_kit.gd's body path, game
	# feel lane 2026-11-10). Codex's arena_rhino_body.gd sprite-clock bridge stays for an older rhino GLB without it.
	var rhino_clips: Dictionary = load("res://scripts/moba3d/arena_roster.gd").profile(k).get("body", {}).get("clips", {}) if k == "rhino" else {}
	var b: MechModel3D = load("res://scripts/moba3d/arena_rhino_body.gd").new() if k == "rhino" and not rhino_clips.has("horn_hook") else MechModel3D.new()
	b.name = "Body"
	machine.add_child(b)
	if not b._setup(k):
		machine.remove_child(b)
		b.queue_free()
		return null
	return b


func _setup(k: String) -> bool:
	kind = k
	var registered: Dictionary=load("res://scripts/moba3d/arena_roster.gd").profile(k).get("body",{})
	_row = registered if not registered.is_empty() else ROWS.get(k,{})
	var tpl := _template(_row["glb"])
	if tpl == null:
		push_warning("MechModel3D: no GLB at %s" % _row["glb"])
		return false
	_model = tpl.duplicate() as Node3D
	_model.name = "Model"
	_model.scale = Vector3.ONE * float(_row.get("scale", 1.0))
	add_child(_model)
	var players := _model.find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		push_warning("MechModel3D: %s has no AnimationPlayer" % _row["glb"])
		return false
	anim = players[0]
	anim.process_priority=-10 # sample the advanced pose before this body's event polling
	var sk := _model.find_children("*", "Skeleton3D", true, false)
	skeleton = sk[0] if not sk.is_empty() else null
	for full in anim.get_animation_list():
		_clips[_short(full)] = full
	for short_name in _row.get("clips",{}):
		var full: String=_row["clips"][short_name]
		if anim.has_animation(full):_clips[short_name]=full
	var al: Dictionary = _row.get("aliases", {})
	for a in al:  # both ways: the kit may use either name, whichever round the GLB is
		if _clips.has(a) and not _clips.has(al[a]):
			_clips[al[a]] = _clips[a]
		elif _clips.has(al[a]) and not _clips.has(a):
			_clips[a] = _clips[al[a]]
	_rest = float(_row.get("rest_height", 1.7))
	_walk_speed = float(_row.get("walk_speed", 3.5))
	_run_speed = float(_row.get("run_speed", 0.0))
	_events = (_row.get("events", {}) as Dictionary).duplicate(true)
	_peaks = (_row.get("peaks", {}) as Dictionary).duplicate()
	_load_events_file()
	for loop in [_row.get("idle", ""), _row.get("walk", ""), _row.get("run", ""), _row.get("strafe_left", ""), _row.get("strafe_right", ""), _row.get("back", "")]:  # walk_start and walk_stop are one-shots: left alone
		if _clips.has(loop):
			anim.get_animation(_clips[loop]).loop_mode = Animation.LOOP_LINEAR
	_add_springs()
	locomote(0.0)
	return true


## Parts that move on their own (gorilla lane, 2026-11-11): a jaw, shoulder plates, forearm shields. The optional row
## key "springs" lists [root bone, end bone or "", stiffness, drag, end length m]; "" as the end bone means the root
## bone alone, extended along its own length by the last number. A row with the key gets one SpringBoneSimulator3D
## named "Springs" under its skeleton. Its centre is the model node, so turning, nudging or sliding the machine does
## not drive the springs (with the world as centre the drag acts like wind and a steady walk trails every part far
## behind); only the motion inside the clips does. Gravity is off: the parts sit exactly on their clip pose at rest.
## It keeps settling through a hitstop. A row without the key gets no node at all.
func _add_springs() -> void:
	var rows: Array = _row.get("springs", [])
	if rows.is_empty() or skeleton == null:
		return
	var good: Array = []
	for r in rows:
		if r is Array and r.size() >= 5 and skeleton.find_bone(String(r[0])) >= 0 and (String(r[1]) == "" or skeleton.find_bone(String(r[1])) >= 0):
			good.append(r)
		else:  # a wrong bone name or a short entry: skipped once here, so the simulator never errors every frame
			push_warning("MechModel3D: %s springs entry %s skipped (needs 5 values and bones this skeleton has)" % [kind, r])
	if good.is_empty():
		return
	var s := SpringBoneSimulator3D.new()
	s.name = "Springs"
	skeleton.add_child(s)  # the skeleton's last child, so it runs after any other modifier the model carries
	var up := ""  # the path from the simulator up to the model node
	var n: Node = s
	while n != null and n != _model:
		up += "../"
		n = n.get_parent()
	s.set_setting_count(good.size())
	for i in good.size():
		var r: Array = good[i]
		var root_bone := String(r[0])
		var end_bone := String(r[1])
		s.set_root_bone_name(i, root_bone)
		s.set_end_bone_name(i, end_bone if end_bone != "" else root_bone)
		if end_bone == "":
			s.set_extend_end_bone(i, true)
			s.set_end_bone_direction(i, SkeletonModifier3D.BONE_DIRECTION_PLUS_Y)
			s.set_end_bone_length(i, float(r[4]))
		s.set_stiffness(i, float(r[2]))
		s.set_drag(i, float(r[3]))
		s.set_gravity(i, 0.0)
		if n == _model:
			s.set_center_from(i, SpringBoneSimulator3D.CENTER_FROM_NODE)
			s.set_center_node(i, NodePath(up.trim_suffix("/")))


## "Gorilla_Slam_v25", "lib/Gorilla_Slam" and "Slam_v25" are all "Slam".
func _short(full: String) -> String:
	var s := full.substr(full.rfind("/") + 1)
	var pre := kind.capitalize().replace(" ", "") + "_"
	if s.to_lower().begins_with(pre.to_lower()):
		s = s.substr(pre.length())
	var re := RegEx.create_from_string("_v\\d+$")
	return re.sub(s, "")


func _load_events_file() -> void:
	var path := String(_row["glb"]).get_basename() + ".events.json"
	if not FileAccess.file_exists(path):
		return
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not (data is Dictionary):
		push_warning("MechModel3D: %s is not a JSON object" % path)
		return
	_rest = float(data.get("rest_height", _rest))
	var clips: Dictionary = data.get("clips", {})
	for full in clips:
		var c: Dictionary = clips[full]
		var key := _short(full)
		var evs := []
		for e in c.get("events", []):
			evs.append([String(e.get("name", "")), float(e.get("time", 0.0)), bool(e.get("damage", false))])
		evs.sort_custom(func(x: Array, y: Array) -> bool: return x[1] < y[1])
		_events[key] = evs
		if c.has("peak_height"):
			_peaks[key] = float(c["peak_height"])
		if c.has("speed"):
			if key == _row.get("walk", ""):
				_walk_speed = float(c["speed"])
			elif key == _row.get("run", ""):
				_run_speed = float(c["speed"])


func _resolve(clip: String) -> String:
	return _clips.get(clip, "")


func _lookup(d: Dictionary, clip: String) -> Variant:
	if d.has(clip):
		return d[clip]
	var al: Dictionary = _row.get("aliases", {})
	for a in al:
		if a == clip and d.has(al[a]):
			return d[al[a]]
		if al[a] == clip and d.has(a):
			return d[a]
	return null


func model_root() -> Node3D:
	return _model


func has_clip(clip: String) -> bool:
	return _clips.has(clip)


func clips() -> Array:
	return _clips.keys()


## The clip's length in seconds at speed 1, or 0.0.
func clip_length(clip: String) -> float:
	var full := _resolve(clip)
	return anim.get_animation(full).length if full != "" else 0.0


## The clip's events as [[name, time, damage], ...] (a copy).
func events_of(clip: String) -> Array:
	var e: Variant = _lookup(_events, clip)
	return (e as Array).duplicate(true) if e is Array else []


## Top of the mesh in metres: at rest, or the clip's peak when it has one (for effects and markers above the body).
func top_height(clip := "") -> float:
	var p: Variant = _lookup(_peaks, clip) if clip != "" else null
	return (float(p) if p != null else _rest) * float(_row.get("scale", 1.0))


## Turns at once (spawns, respawns).
func snap_facing(dir: Vector3) -> void:
	if _model != null and Vector3(dir.x, 0.0, dir.z).length_squared() > 1e-6:
		_model.rotation.y = atan2(dir.x, dir.z)


## Weight in the turn (camera lane, 2026-11-14; Preston picked "Weight in the turn" from the combat camera synthesis).
## The body can turn at most TURN_CAP degrees a second by size class, so a big machine swings round instead of snapping;
## the aim and the machine's facing stay instant (gameplay reads facing, never this heading), the way MechWarrior's legs
## turn by tonnage while the torso aims fast. Placeholders for Preston. 0 = no cap.
const TURN_CAP := {"S": 600.0, "M": 400.0, "L": 260.0}
const TURN_ROSTER := preload("res://scripts/moba3d/arena_roster.gd")
var _turn_cap := -1.0


## Turns toward dir; faster while an action plays, so a strike lands where it's aimed. The ease is capped at the
## size class's TURN_CAP (also 1.75x while an action plays).
func face(dir: Vector3, delta: float) -> void:
	var flat := Vector3(dir.x, 0.0, dir.z)
	if _model == null or flat.length_squared() < 1e-6:
		return
	var boost := 1.75 if action != "" else 1.0
	var rate := float(_row.get("turn_rate", 16.0)) * boost
	var left := wrapf(atan2(flat.x, flat.z) - _model.rotation.y, -PI, PI)
	var step := left * (1.0 - exp(-rate * delta))
	if _turn_cap < 0.0:
		_turn_cap = float(TURN_CAP.get(str(TURN_ROSTER.profile(kind).get("size_class", "")), 0.0))
	if _turn_cap > 0.0:
		var most := deg_to_rad(_turn_cap) * boost * delta
		step = clampf(step, -most, most)
	_model.rotation.y = wrapf(_model.rotation.y + step, -PI, PI)


## Idle, walk or run by ground speed (m/s), with the walk's playback matched to the speed. Does nothing while an
## action plays: hit clips and strikes own the body until they end.
## move_dir (gorilla lane, 2026-11-10; game feel's conditions): the direction of travel. Measured from the body's own
## heading: more than 50 degrees off plays the strafe on that side, more than 130 the backpedal, each at ground_speed
## over its own authored speed, and each kept until the angle passes its edge by 10 degrees. Picked before the run
## check, so the run only plays travelling forward. Rows without those clips, and callers that pass no direction,
## get exactly the old path.
func locomote(ground_speed: float, move_dir := Vector3.ZERO) -> void:
	if anim == null or action != "":
		return
	var clip: String = _row.get("idle", "")
	var rate := 1.0
	var side := _side_clip(ground_speed, move_dir)
	if side != "":
		clip = side
		var authored := float(_row.get("back_speed", 2.1)) if side == _row.get("back", "") else float(_row.get("strafe_speed", 2.8))
		rate = maxf(0.15, ground_speed / maxf(authored, 0.01))
	elif ground_speed > 0.05:
		var run: String = _row.get("run", "")
		if run != "" and _clips.has(run) and _run_speed > 0.0 and ground_speed >= float(_row.get("run_above", 1.8)):
			clip = run
			rate = ground_speed / _run_speed
		elif _clips.has(_row.get("walk", "")):
			clip = _row["walk"]
			rate = maxf(0.15, ground_speed / maxf(_walk_speed, 0.01))
	if not _clips.has(clip):
		return
	if _bridged(clip, rate):
		return
	if anim.current_animation != _clips[clip]:
		anim.play(_clips[clip], 0.12)
	_rate = rate
	_apply_rate()
	_steps(clip)


## Walk start and stop (gorilla lane, 2026-11-11). With the row keys walk_start, walk_stop and walk_start_exit_s:
## idle to the forward walk plays the start clip, then cuts to the walk at the time the start clip ends on; the
## forward walk to idle plays the stop clip, then the idle from its first frame, the pose the stop ends on. Anything
## else (a change of mind, a strafe, a run, an action in between) is left to the ordinary crossfade. Returns true
## while a bridge owns the body this frame. A row without the keys never bridges.
func _bridged(clip: String, rate: float) -> bool:
	var idle: String = _row.get("idle", "")
	var walk: String = _row.get("walk", "")
	var start: String = _row.get("walk_start", "")
	var stop: String = _row.get("walk_stop", "")
	if _bridge != "":
		var full: String = _clips.get(_bridge, "")
		var target := walk if _bridge == start else idle
		if full == "" or anim.current_animation != full or clip != target:
			_bridge = ""  # cut off, or the machine changed its mind: the crossfade below takes over
		elif anim.is_playing() and anim.current_animation_position < anim.get_animation(full).length - 0.001:
			_rate = rate if _bridge == start else 1.0
			_apply_rate()
			return true
		else:
			var was_start := _bridge == start
			_bridge = ""
			anim.play(_clips[target], 0.0)
			if was_start:
				anim.seek(float(_row.get("walk_start_exit_s", 0.0)), true)
			_rate = rate
			_apply_rate()
			_step_clip = ""
			return true
	if clip == walk and start != "" and _clips.has(start) and _clips.has(idle) and anim.current_animation == _clips[idle]:
		_bridge = start
		anim.play(_clips[start], 0.05)
		_rate = rate
		_apply_rate()
		return true
	if clip == idle and stop != "" and _clips.has(stop) and _clips.has(walk) and anim.current_animation == _clips[walk]:
		_bridge = stop
		anim.play(_clips[stop], 0.10)
		_rate = 1.0
		_apply_rate()
		return true
	return false


## Footfalls (gorilla lane, 2026-11-11): fires `step` for each [name, seconds] under the row key "steps" as the
## loop playing passes it, the wrap at the loop's end included. Nothing fires on the frame a loop starts.
func _steps(clip: String) -> void:
	var all: Dictionary = _row.get("steps", {})
	if not all.has(clip) or anim.current_animation != _clips[clip]:
		_step_clip = ""
		return
	var now := anim.current_animation_position
	if _step_clip != clip:
		_step_clip = clip
		_step_pos = now
		return
	var prev := _step_pos
	_step_pos = now
	if is_equal_approx(prev, now):
		return
	for e in all[clip]:
		var t := float(e[1])
		if (prev < t and t <= now) if now > prev else (t > prev or t <= now):
			step.emit(clip, String(e[0]))


## The strafe or backpedal clip for travelling along move at the body's current heading, or "" for the ordinary walk.
func _side_clip(ground_speed: float, move: Vector3) -> String:
	var m := Vector3(move.x, 0.0, move.z)
	if ground_speed <= 0.05 or m.length_squared() < 1e-6 or _model == null:
		_side = ""
		return ""
	var f := Vector3(sin(_model.rotation.y), 0.0, cos(_model.rotation.y))  # the body's own heading, which face() eases toward its target
	m = m.normalized()
	var off := rad_to_deg(acos(clampf(f.dot(m), -1.0, 1.0)))
	# each band is kept until the angle passes its edge by 10 degrees, so aim wobble near 50 or 130 cannot flicker
	var band := _side
	if band == "":
		band = "back" if off > 140.0 else ("strafe" if off > 60.0 else "")
	elif band == "strafe":
		band = "back" if off > 140.0 else ("" if off < 40.0 else "strafe")
	else:
		band = "back" if off > 120.0 else ("strafe" if off > 40.0 else "")
	var pick := ""
	if band == "back":
		pick = _row.get("back", "")
	elif band == "strafe":
		pick = _row.get("strafe_left", "") if f.z * m.x - f.x * m.z > 0.0 else _row.get("strafe_right", "")  # the model faces +Z, so its left is +X
	if pick == "" or not _clips.has(pick):
		_side = ""
		return ""
	_side = band
	return pick


## Plays a one-shot clip from its start (a repeat restarts it). Returns its length in seconds at this speed, or 0.0
## when the clip is missing. The clip's events fire through `event` as it passes them, then `action_finished`.
func play_action(clip: String, speed := 1.0, blend := 0.06) -> float:
	var full := _resolve(clip)
	if full == "":
		push_warning("MechModel3D: %s has no clip %s (has %s)" % [kind, clip, _clips.keys()])
		return 0.0
	if action != "":
		_end_action()
	_bridge = ""  # an action ends a walk start or stop at once; locomote() never returns to it
	_step_clip = ""  # and the loop that resumes afterwards counts its footfalls from where it restarts
	action = clip
	_action_full = full
	_fired = 0
	_rate = speed
	if anim.current_animation == full:
		anim.seek(0.0, true)
	else:
		anim.play(full, blend)
	_apply_rate()
	anim.advance(0.0) # apply the new action now, rather than spending a frame on queued playback
	return anim.get_animation(full).length / maxf(speed, 0.01)


## Changes the playing action's speed (the rhino's Tremor charge loop follows the run's pace).
func set_action_rate(speed: float) -> void:
	if _bridge != "":
		return  # a walk start or stop keeps its own rate; there is no action to pace
	_rate = speed
	_apply_rate()


## Ends the action now; the next locomote() picks idle or walk again.
func stop_action() -> void:
	if action != "":
		_end_action()


## Plays clip as a held loop (a brace, the stampede's charge): it stays the action, repeating, until stop_action() or
## another action. False when the clip is missing. Its events fire on the first pass only.
func play_hold(clip: String, speed := 1.0, blend := 0.06) -> bool:
	var full := _resolve(clip)
	if full == "":
		return false
	anim.get_animation(full).loop_mode = Animation.LOOP_LINEAR
	play_action(clip, speed, blend)
	_hold = true
	return true


## Hitstop: holds the pose for t seconds (the longer of two overlapping holds wins).
func freeze(t: float) -> void:
	_freeze = maxf(_freeze, t)
	_apply_rate()


## Shoves the body by world (a world-space offset) at once, then eases it back over back seconds.
func nudge(world: Vector3, back: float) -> void:
	var p := get_parent() as Node3D
	feel_offset = p.global_basis.inverse() * world if p != null else world
	if _nudge_tw != null:
		_nudge_tw.kill()
	_nudge_tw = create_tween()
	_nudge_tw.tween_property(self, "feel_offset", Vector3.ZERO, back).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)


## A short white flash on this body only, through the look lane's per-instance hit_flash (0 to 1) in mech_body
## (2026-11-10). material_overlay stays free for the hex shield.
func flash(strength := 0.6, t := 0.15) -> void:
	if _model == null:
		return
	if _flash_tw != null:
		_flash_tw.kill()
	_set_flash(strength)
	_flash_tw = create_tween()
	_flash_tw.tween_method(_set_flash, strength, 0.0, t)


func flashing() -> bool:
	return _flash_amount > 0.001


func _set_flash(x: float) -> void:
	_flash_amount = x
	MECH_LOOK.set_flash(_model, x)


func _meshes() -> Array:
	return _model.find_children("*", "MeshInstance3D", true, false) if _model != null else []


func _apply_rate() -> void:
	if anim != null:
		anim.speed_scale = 0.0 if _freeze > 0.0 else _rate


func _end_action() -> void:
	var c := action
	action = ""
	_action_full = ""
	_hold = false
	action_finished.emit(c)


func _process(delta: float) -> void:
	position = feel_offset + Vector3(0.0, lift, 0.0)
	if external_clock:return
	if _freeze > 0.0:
		_freeze -= delta
		if _freeze <= 0.0:
			_freeze = 0.0
			_apply_rate()
	if action == "" or anim == null:
		return
	var c := action
	var evs: Variant = _lookup(_events, action)
	var list: Array = evs if evs is Array else []
	var done := not anim.is_playing() or anim.current_animation != _action_full
	var t := anim.get_animation(_action_full).length if done else anim.current_animation_position
	while _fired < list.size() and float(list[_fired][1]) <= t + 0.0001:
		event.emit(c, String(list[_fired][0]), bool(list[_fired][2]))
		_fired += 1
		if action != c:  # a handler started another action (a chain); that one runs its own events from 0
			return
	if done or (not _hold and t >= anim.get_animation(_action_full).length - 0.001):
		_end_action()


## Explicit manual clock for movement-owned phases and two-body interactions.
func start_external(clip: String) -> void:
	external_clock=true
	anim.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	play_action(clip,1.0,0.0)
	anim.advance(0.0)
func sample_external(clip: String, time: float) -> void:
	if action!=clip:play_action(clip,1.0,0.0)
	anim.seek(time,true);anim.advance(0.0)
func finish_external() -> void:
	stop_action();external_clock=false
	anim.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_IDLE
	locomote(0.0)
func grip() -> Vector3:
	var a:=skeleton.find_bone("LeftHand");var b:=skeleton.find_bone("RightHand")
	return skeleton.global_transform*((skeleton.get_bone_global_pose(a).origin+skeleton.get_bone_global_pose(b).origin)*.5)
