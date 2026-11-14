extends Node3D
## Pangolin ability effects, smooth (pangolin effects lane, 2026-11-12). Visual only, an observer like
## rhino_release_fx.gd. Iron ball (ult) and scale flare (3) so far.
##
## IRON BALL. The pangolin has no kit code yet, so this listens to whatever kit node it is given for:
##   signal cue(name)   "ball_start" (the tuck begins), "ball_hit" (first enemy struck), "ball_end" (roll over, no hit)
##   rolling: bool, roll_speed: float (m/s), roll_dir: Vector3, hit_speed: float, hit_at: Vector3
## and to the body's clip events: Curl_In "closed" (0.36 s) and Curl_Out "land" (0.30 s).
## Structure from Geb's Roll Out (SMITE 2, measured) and Rammus's Powerball (League, general knowledge), see
## docs/reference/pangolin-fx-synthesis-2026-11-12.md:
##   tuck:   a dust ring at the feet and a dust ring as the plates close; nothing bright
##   roll:   a furrow pressed into the floor behind (pale, with a hot grind line at speed), dust kicked back, and two
##           amber flank streaks that stretch as it builds to full speed
##   crash:  a small 2-frame core, an amber shock edge thrown forward, forward streaks, rocks and dust; bigger the faster
##   unroll: a landing puff
## SCALE FLARE. Kit fields read if present: flare_blocks: int (blocks left, 2 at the start), block_at: Vector3; cues
## "flare_block" (a hit glanced off) and "flare_end". Without them the flare runs off the clip: Scale_Flare "flare"
## (0.20 s) starts it and it lasts FLARE_LIFE. Structure from Kuzenbo's Shell Spikes (SMITE, measured): one cell of
## burst, then the shell itself glows steadily and goes out at once. Ours: the burst is a floor ring for the damage area
## with amber rays all round and plate flakes thrown up; the glow is copper on the plates (material_overlay, only while
## up); each blocked hit throws an amber spark and steps the glow down.
## MAGNETISED MARK (approved kit redo, Preston 2026-11-12): salvage, scale flare and rail dive magnetise enemies; the
## iron ball curves toward them. The kit sets mag_target and mag_time, then emits cue "magnetise" (settled with game
## feel, 2026-11-12: cue only, no direct calls into this node). magnetise() stays public for test scripts only.
## A copper ring with four amber arcs circling under the enemy; one arc goes out per quarter of the time.
## SALVAGE (approved kit redo): cue "salvage" at the start of the cast, with kit field salvage_targets: Array (the
## enemies the cone hit) and optional salvage_time (seconds the stolen armour lasts). Timed to the pangolin 3D lane's
## Pangolin_Salvage clip (r7 events): the field comes on at 0.15 s, three plates snap on at 0.36, 0.42, 0.48 (front,
## middle, rear). The field is a short copper cone with amber bands running inward; at 0.15 a plate rips off a hit
## enemy (amber spark there) and is pulled in on an arc, faster as it comes, and snaps onto the shell (spark, pop).
## The plates stay on the shell with a low amber edge for the stolen-armour time, then drop off. The kit's magnetise
## cue marks each hit enemy as usual.
## Colours: copper with amber sparks, the pangolin's effect theme (Preston, 2026-11-12: any colour added later sits on
## top of it). Never red.
const TRACK := preload("res://shaders/pangolin_track.gdshader")
const WAKE := preload("res://shaders/pangolin_wake.gdshader")
const CRASH := preload("res://shaders/pangolin_crash.gdshader")
const SHELL := preload("res://shaders/pangolin_flare_shell.gdshader")
const SPARK := preload("res://shaders/pangolin_spark.gdshader")
const MAG := preload("res://shaders/pangolin_mag_mark.gdshader")
const MAG_TIME := 4.0 ## seconds, the kit draft's magnetise length
const FLARE_R := 2.5 ## metres: the flare's damage ring (a draft; the kit has no number yet)
const FLARE_LIFE := 3.0 ## seconds the block lasts when the kit gives no count (Kuzenbo's shell held about 2.8 s)
const FIELD := preload("res://shaders/pangolin_salvage_field.gdshader")
const PLATE := preload("res://shaders/pangolin_plate.gdshader")
const SALV_RANGE := 4.0 ## metres: the cone's reach (a draft; the kit has no number yet)
const SALV_HALF := 0.6 ## radians either side of the facing (about 70 degrees across)
const SALV_HOLD := 4.0 ## seconds the stolen plates stay on (draft, "a few seconds")
const SALV_FIELD := 0.15 ## Pangolin_Salvage "field"
const SALV_SNAPS := [0.36, 0.42, 0.48] ## Pangolin_Salvage "plate_snap" x3: front, middle, rear
const RAIL := preload("res://shaders/pangolin_rail.gdshader")
const FIELD_SHELL := preload("res://shaders/pangolin_field_shell.gdshader")
const COMET_LINES := 8 ## magnet field lines from the curled pangolin out to the scrap shell
const RAIL_RELEASE := 0.12 ## Pangolin_Rail_Launch "release" (r7 draft): the streak starts here
const RAIL_TRAIL := 2.6 ## metres of spark streak behind the spine at most
const DUST := preload("res://shaders/rhino_dust.gdshader") ## the rhino lane's smooth dust puff, used as is
const DUST_COL := Color(0.60, 0.53, 0.46) ## warm grey, a touch of the pangolin's copper
const WALK_SPEED := 3.5
const FULL_SPEED := 7.67 ## Ball_Roll's roll_speed in pangolin.events.json
const BALL_MID := 0.42 ## metres: the curled ball's middle above the floor
const LIFT := 0.03
const COMET_PLATES := 12 ## scrap plates stuck on the comet
const COMET_IN := 0.35 ## seconds for the scrap to fly onto the shell
const COMET_R := 3.5 ## metres: the burst ring when the kit gives no comet_radius (a draft)
const GRAVITY := 16.0
const CHARGE_BAND := preload("res://shaders/pangolin_charge_band.gdshader")
const BAND_R := 0.47 ## metres: the charge hoops sit just outside the curled ball (BALL_MID up from the floor)
const BAND_OFF := [0.0, 0.09, 0.18] ## metres added to BAND_R for charges 1, 2 and 3: level hoops round the ball's middle,
## one inside the next, so the count reads from the top-down match camera and from behind (a hoop around the roll axis
## was edge-on to both and read as a line, 2026-11-14 recording)
var _bands: Array = [] ## bank-shot charge hoops: {node, mat, pulse}
var _band_fade := 0.0
var _band_spin := 0.0
var kit: Node
var actor: Node3D
var body: Node
var live: Array = [] ## timed pieces: {node, age, life, kind, ...}
var rocks: Array = []
var log_rows: Array = []
var elapsed := 0.0
var _wake: MeshInstance3D
var _wake_fade := 0.0
var _last_drop := Vector3.INF
var _dust_clock := 0.0
var _rock_mesh: Mesh
var _rock_mat: StandardMaterial3D
var _shell_mat: ShaderMaterial
var _flare_t := -1.0 ## seconds since the flare went up, -1 when down
var _flare_glow := 0.0
var _flare_pulse := 0.0
var _flare_blocks := 0
var _overlaid: Array = []
var marks := {} ## target -> {node, left, total, snap}
var _salv: Array = [] ## casts in progress: {t, targets, field}
var plates: Array = [] ## {node, mat, from, slot, t, arrive, state, hold}
var _plate_mesh: BoxMesh
var _comet := {} ## scrap comet in progress: {phase "in"/"roll"/"burst", t, spin, plates: [{node, mat, from, off, t}]}
var _pull := {} ## the magnet pull line while kit.mag_pull bends the roll: {node, age, fade, target}
var _dive := {} ## the dive in progress: {t, target, lock, streak, start, arrived, after, spark_clock}


func setup(k: Node, p: Node3D) -> void:
	kit = k
	actor = p
	if kit.has_signal("cue"):
		kit.cue.connect(on_cue)
	body = p.get("body") if "body" in p else p.get_node_or_null("Body")
	if body != null and body.has_signal("event"):
		body.event.connect(_on_event)
	_wake = MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE
	_wake.mesh = plane
	var wm := ShaderMaterial.new()
	wm.shader = WAKE
	_wake.material_override = wm
	_place(_wake, Vector3.ZERO)
	_wake.visible = false
	var rock := SphereMesh.new()  # few segments: a faceted chunk (same recipe as the rhino's rocks)
	rock.radius = 0.5
	rock.height = 0.8
	rock.radial_segments = 5
	rock.rings = 2
	_rock_mesh = rock
	_rock_mat = StandardMaterial3D.new()
	_rock_mat.albedo_color = Color(0.20, 0.17, 0.15)
	_rock_mat.roughness = 0.95


func on_cue(cue_name: String) -> void:
	if not is_instance_valid(actor):
		return
	match cue_name:
		"ball_start":
			_tuck()
		"ball_hit":
			crash(kit.hit_at, kit.roll_dir, float(kit.hit_speed))
			if "charges" in kit and int(kit.charges) > 0:
				charged_crash(kit.hit_at, int(kit.charges))
		"ball_charge":
			charge()
		"ball_pop":
			pop(kit.pop_at if "pop_at" in kit else actor.global_position,
				float(kit.pop_radius) if "pop_radius" in kit else 2.2)
		"ball_end":
			_last_drop = Vector3.INF
		"ball_bounce":
			bounce(kit.bounce_at if "bounce_at" in kit else actor.global_position)
		"comet_start":
			comet_start()
		"comet_hit":
			comet_hit(kit.comet_hit_at if "comet_hit_at" in kit else actor.global_position)
		"comet_burst":
			comet_burst(kit.comet_burst_at if "comet_burst_at" in kit else actor.global_position,
				float(kit.comet_radius) if "comet_radius" in kit else COMET_R)
		"ball_spiked":
			spiked()
		"spike_burst":
			spike_burst(kit.spike_at if "spike_at" in kit else actor.global_position)
		"ball_bowl":
			bowl(kit.bowl_at if "bowl_at" in kit else actor.global_position)
		"flare_block":
			block(kit.block_at if "block_at" in kit else actor.global_position + Vector3.UP * 0.8)
		"flare_end":
			_flare_off()
		"salvage":
			salvage(kit.salvage_targets if "salvage_targets" in kit else [])
		"rail_dive":
			rail_dive(kit.dive_target if "dive_target" in kit else null)
		"rail_arrive":
			rail_arrive(bool(kit.rail_charged) if "rail_charged" in kit else false)
		"magnetise":
			magnetise(kit.mag_target, float(kit.mag_time) if "mag_time" in kit else MAG_TIME)
	log_rows.append({"cue": cue_name, "time": snappedf(elapsed, 0.01)})


func _on_event(clip: String, ev: String, _damage: bool) -> void:
	if clip.ends_with("Curl_In") and ev == "closed":
		_ring_puffs(actor.global_position, 0.8, 5, 0.45, 0.55)
	elif clip.ends_with("Scale_Flare") and ev == "flare":
		flare()
	elif clip.ends_with("Comet_Gather") and ev == "pull":
		_comet_pull()
	elif clip.ends_with("Comet_Gather") and ev == "plates_on":
		_comet_slam()
	elif clip.ends_with("Curl_Out") and ev == "land":
		_ring_puffs(actor.global_position, 0.7, 4, 0.5, 0.5)


func _tuck() -> void:
	var at := actor.global_position
	_ring_puffs(at, 0.5, 4, 0.35, 0.45)
	_last_drop = at


## The crash on the first enemy hit. speed is the roll speed at contact (m/s).
func crash(at: Vector3, dir: Vector3, speed: float) -> void:
	var power := _power(speed)
	var flat :=Vector3(dir.x, 0, dir.z).normalized() if Vector3(dir.x, 0, dir.z).length() > 0.01 else Vector3.FORWARD
	at.y = actor.global_position.y
	var r := 1.6 + 1.4 * power
	var half := r * 1.4
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE
	g.mesh = plane
	var m := ShaderMaterial.new()
	m.shader = CRASH
	m.set_shader_parameter("radius_m", r)
	m.set_shader_parameter("half_m", half)
	m.render_priority = 3  # drawn after the arena's see-through floor zones, which otherwise cover it
	m.set_shader_parameter("power", power)
	m.set_shader_parameter("seed", randf() * 50.0)
	g.material_override = m
	_place(g, at + Vector3.UP * (LIFT + 0.01))
	g.scale = Vector3(half * 2.0, 1.0, half * 2.0)
	g.rotation.y = atan2(flat.x, flat.z)
	live.append({"node": g, "age": 0.0, "life": 0.95, "kind": "crash"})
	var l := OmniLight3D.new()  # small and short: lights the floor and the victim, never washes the mech out
	l.light_color = Color(1.0, 0.72, 0.45)
	l.omni_range = r * 1.2
	l.shadow_enabled = false
	_place(l, at + Vector3.UP * 0.7 + flat * 0.4)
	live.append({"node": l, "age": 0.0, "life": 0.16, "kind": "light", "peak": 1.0 + 0.8 * power})
	var side := flat.cross(Vector3.UP)
	for i in 4 + int(4 * power):
		var out := (flat * randf_range(0.3, 1.0) + side * randf_range(-0.9, 0.9)).normalized()
		_rock(at + out * 0.4, out * randf_range(1.8, 3.4) * (0.7 + 0.5 * power) + Vector3.UP * randf_range(2.5, 4.5))
	for i in 3 + int(3 * power):
		var out2 := (flat * randf_range(-0.2, 1.0) + side * randf_range(-1.0, 1.0)).normalized()
		_dust(at + out2 * randf_range(0.4, 1.2) + Vector3.UP * 0.35, randf_range(0.9, 1.4) * (0.8 + 0.5 * power), 0.7)
	if is_instance_valid(_wake):
		_wake_fade = minf(_wake_fade, 0.6)
	_last_drop = Vector3.INF
	log_rows.append({"crash": true, "speed": snappedf(speed, 0.01), "power": snappedf(power, 0.01), "radius": snappedf(r, 0.01), "time": snappedf(elapsed, 0.01)})


## Scale flare goes up: the burst ring and flakes now, then the plates glow until the blocks are used or time runs out.
func flare() -> void:
	_flare_ring(actor.global_position, _flare_r(), 0.6, 6)
	_flare_blocks = int(kit.flare_blocks) if "flare_blocks" in kit else 2
	_flare_t = 0.0
	_flare_pulse = 1.0
	_overlay(true)
	log_rows.append({"flare": true, "blocks": _flare_blocks, "overlaid": _overlaid.size(), "time": snappedf(elapsed, 0.01)})


func _flare_r() -> float:
	return float(kit.flare_radius) if is_instance_valid(kit) and "flare_radius" in kit else FLARE_R


## The all-round copper burst ring on the floor plus plate flakes thrown up and out. Scale flare and the spiked crash share it.
func _flare_ring(at: Vector3, r: float, power: float, flakes: int) -> void:
	at.y = actor.global_position.y
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE
	g.mesh = plane
	var m := ShaderMaterial.new()
	m.shader = CRASH
	m.set_shader_parameter("radius_m", r)
	m.set_shader_parameter("half_m", r * 1.3)
	m.set_shader_parameter("power", power)
	m.set_shader_parameter("omni", 1.0)
	m.set_shader_parameter("seed", randf() * 50.0)
	m.render_priority = 3
	g.material_override = m
	_place(g, at + Vector3.UP * (LIFT + 0.01))
	g.scale = Vector3.ONE * r * 2.6
	live.append({"node": g, "age": 0.0, "life": 0.9, "kind": "crash"})
	for i in flakes:  # plate flakes thrown up and out (Kuzenbo's dark shards on the cast cell)
		var a := TAU * (float(i) + randf() * 0.6) / float(flakes)
		var out := Vector3(cos(a), 0, sin(a))
		_rock(at + out * 0.5 + Vector3.UP * 0.6, out * randf_range(1.5, 2.6) + Vector3.UP * randf_range(2.5, 4.0), 0.5)


## Slot 3 pressed mid-roll: no Scale_Flare clip plays, so the scales go up from here. A short amber crackle on the
## shell, the plate glow on, and the blocks counted like a normal flare. The scales stay up until flare_end.
func spiked() -> void:
	_spark(actor.global_position + Vector3.UP * (_shell_top() * 0.8), 1.2)
	_flare_blocks = int(kit.flare_blocks) if "flare_blocks" in kit else 2
	_flare_t = 0.0
	_flare_pulse = 1.0
	_overlay(true)
	log_rows.append({"spiked": true, "overlaid": _overlaid.size(), "time": snappedf(elapsed, 0.01)})


## The spiked ball's crash: the flare's burst ring around the target, on top of the iron ball's crash, plus more flakes.
func spike_burst(at: Vector3) -> void:
	_flare_ring(at, _flare_r(), 0.85, 8)
	_spark(at + Vector3.UP * 0.7, 1.4)
	_flare_pulse = 1.0
	log_rows.append({"spike_burst": true, "radius": _flare_r(), "time": snappedf(elapsed, 0.01)})


## A hit glanced off the flared plates: an amber spark where it struck, a pulse, one block used.
func block(at: Vector3) -> void:
	_spark(at, 1.1)
	_flare_pulse = 1.0
	_flare_blocks = int(kit.flare_blocks) if "flare_blocks" in kit else maxi(_flare_blocks - 1, 0)
	log_rows.append({"block": true, "left": _flare_blocks, "time": snappedf(elapsed, 0.01)})
	if _flare_blocks <= 0:
		_flare_off()


## 0 at the kit's start speed, 1 at its top speed (game feel's slot-2 ball: 4 to 12 m/s). Older stub kits fall back to the walk-to-clip range.
func _power(speed: float) -> float:
	var lo := float(kit.ball_start_speed) if is_instance_valid(kit) and "ball_start_speed" in kit else WALK_SPEED
	var hi := float(kit.ball_max_speed) if is_instance_valid(kit) and "ball_max_speed" in kit else FULL_SPEED
	return clampf((speed - lo) / maxf(hi - lo, 0.01), 0.0, 1.0)


## Off a wall: a white-amber spark at the contact, a few copper chips thrown back off the wall, a puff at the foot.
## Small and quick so a pinball run of bounces never stacks into a wash.
func bounce(at: Vector3) -> void:
	var p := _power(float(kit.roll_speed) if "roll_speed" in kit else WALK_SPEED)
	var dir: Vector3 = kit.roll_dir if "roll_dir" in kit else Vector3.FORWARD
	var flat := Vector3(dir.x, 0, dir.z).normalized() if Vector3(dir.x, 0, dir.z).length() > 0.01 else Vector3.FORWARD
	var hit := Vector3(at.x, actor.global_position.y, at.z)
	_spark(hit + Vector3.UP * 0.55, 0.9 + 0.6 * p)
	var side := flat.cross(Vector3.UP)
	for i in 3 + int(2 * p):
		var out := (flat * randf_range(0.2, 0.8) + side * randf_range(-1.0, 1.0)).normalized()
		_rock(hit + Vector3.UP * 0.4, out * randf_range(1.5, 2.8) + Vector3.UP * randf_range(1.5, 3.0), 0.45)
	_dust(hit + Vector3.UP * 0.3, 0.7 + 0.3 * p, 0.45)
	log_rows.append({"bounce": true, "power": snappedf(p, 0.01), "time": snappedf(elapsed, 0.01)})


## Bank-shot charge (Preston 2026-11-14: "A, bank-shot charge"). Each wall bounce that adds a charge puts one copper
## hoop on the ball, which flashes amber as it lands. Three hoops is a full charge. The hoops ride the ball until it uncurls.
func charge() -> void:
	var n := int(kit.charges) if "charges" in kit else _bands.size() + 1
	_sync_bands(n)
	if n > 0 and n <= _bands.size():
		_bands[n - 1].pulse = 1.0
	_spark(actor.global_position + Vector3.UP * (BALL_MID + BAND_R * 0.8), 0.9 + 0.25 * n)
	log_rows.append({"charge": n, "bands": _bands.size(), "time": snappedf(elapsed, 0.01)})


func _sync_bands(n: int) -> void:
	n = clampi(n, 0, BAND_OFF.size())
	while _bands.size() < n:
		var i := _bands.size()
		var off: float = BAND_OFF[i]
		var r := BAND_R + off
		var t := TorusMesh.new()
		t.inner_radius = r - 0.022
		t.outer_radius = r + 0.022
		t.rings = 48
		t.ring_segments = 8
		var q := MeshInstance3D.new()
		q.mesh = t
		var m := ShaderMaterial.new()
		m.shader = CHARGE_BAND
		q.material_override = m
		q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_place(q, actor.global_position)
		_bands.append({"node": q, "mat": m, "pulse": 0.0, "off": off})


func _free_bands() -> void:
	for b in _bands:
		if is_instance_valid(b.node):
			b.node.queue_free()
	_bands.clear()
	_band_fade = 0.0


func _update_bands(delta: float) -> void:
	if _bands.is_empty():
		return
	var rolling := bool(kit.get("rolling"))
	_band_fade = move_toward(_band_fade, 1.0 if rolling else 0.0, delta / (0.1 if rolling else 0.18))
	if not rolling and _band_fade <= 0.001:
		_free_bands()
		return
	var dir: Vector3 = kit.roll_dir if "roll_dir" in kit else Vector3.FORWARD
	dir.y = 0.0
	dir = dir.normalized() if dir.length() > 0.01 else Vector3.FORWARD
	var side := dir.cross(Vector3.UP).normalized()
	var speed := float(kit.roll_speed) if rolling else 0.0
	_band_spin += speed * delta / (TAU * BAND_R)
	var basis := Basis(side, Vector3.UP, side.cross(Vector3.UP))  # level hoops (torus axis up), dashes turned with the roll
	var centre := actor.global_position + Vector3.UP * BALL_MID
	var heat := float(_bands.size()) / float(BAND_OFF.size())
	for b in _bands:
		b.pulse = maxf(float(b.pulse) - delta / 0.25, 0.0)
		b.node.global_transform = Transform3D(basis, centre)
		var m: ShaderMaterial = b.mat
		m.set_shader_parameter("fade", _band_fade)
		m.set_shader_parameter("pulse", b.pulse)
		m.set_shader_parameter("heat", heat)
		m.set_shader_parameter("spin", _band_spin)


## The crash with charges on it: the flare's copper ring around the target, bigger per charge, and at three charges a
## white-amber flash, more chips and a short brighter light, so a three-bank hit is the loudest thing the ball does.
func charged_crash(at: Vector3, n: int) -> void:
	var full := n >= BAND_OFF.size()
	_flare_ring(at, 1.6 + 0.5 * n, 0.55 + 0.15 * n, 3 + 2 * n)
	_spark(Vector3(at.x, actor.global_position.y, at.z) + Vector3.UP * 0.7, 1.2 + 0.3 * n)
	for b in _bands:
		b.pulse = 1.0
	if full:
		_spark(Vector3(at.x, actor.global_position.y, at.z) + Vector3.UP * 1.1, 2.0)
		var l := OmniLight3D.new()
		l.light_color = Color(1.0, 0.75, 0.48)
		l.omni_range = 4.0
		l.shadow_enabled = false
		_place(l, Vector3(at.x, actor.global_position.y, at.z) + Vector3.UP * 0.8)
		live.append({"node": l, "age": 0.0, "life": 0.14, "kind": "light", "peak": 2.2})
	log_rows.append({"charged_crash": n, "full": full, "time": snappedf(elapsed, 0.01)})


## The recast pop: the ball springs open where it is. A copper ring out to the pop radius, a puff ring, a spark at the
## middle, and the charge hoops flash once and go with the uncurl.
func pop(at: Vector3, r: float) -> void:
	_flare_ring(at, r, 0.6, 6)
	_ring_puffs(at, r * 0.6, 6, 0.5, 0.5)
	_spark(Vector3(at.x, actor.global_position.y, at.z) + Vector3.UP * 0.6, 1.3)
	for b in _bands:
		b.pulse = 1.0
	log_rows.append({"pop": true, "radius": r, "time": snappedf(elapsed, 0.01)})


## A minion bowled aside: a spark on it and a short side puff. The ball keeps rolling, so no ring and no light:
## the crash stays the one big hit of the roll.
func bowl(at: Vector3) -> void:
	_spark(at + Vector3.UP * 0.5, 0.8)
	_dust(Vector3(at.x, actor.global_position.y, at.z) + Vector3.UP * 0.3, 0.6, 0.4)
	_rock(at + Vector3.UP * 0.5, Vector3(randf_range(-1, 1), 0, randf_range(-1, 1)).normalized() * 2.0 + Vector3.UP * 2.5, 0.4)
	log_rows.append({"bowl": true, "time": snappedf(elapsed, 0.01)})


func _spark(at: Vector3, size: float) -> void:
	var q := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE
	q.mesh = quad
	var m := ShaderMaterial.new()
	m.shader = SPARK
	m.set_shader_parameter("seed", randf() * 50.0)
	q.material_override = m
	_place(q, at)
	q.scale = Vector3.ONE * size
	live.append({"node": q, "age": 0.0, "life": 0.18, "kind": "spark"})


## Salvage cast begins (clip time 0). targets: the enemies the cone hit.
func salvage(targets: Array) -> void:
	_salv.append({"t": 0.0, "targets": targets.duplicate(), "field": false})
	log_rows.append({"salvage": targets.size(), "time": snappedf(elapsed, 0.01)})


func _facing() -> Vector3:
	var f: Vector3 = actor.facing if "facing" in actor else Vector3.FORWARD
	f.y = 0.0
	return f.normalized() if f.length() > 0.01 else Vector3.FORWARD


func _field() -> void:
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE
	g.mesh = plane
	var m := ShaderMaterial.new()
	m.shader = FIELD
	var half := SALV_RANGE + 0.2
	m.set_shader_parameter("range_m", SALV_RANGE)
	m.set_shader_parameter("half_ang", SALV_HALF)
	m.set_shader_parameter("half_m", half)
	m.render_priority = 3  # drawn after the arena's see-through floor zones, which otherwise cover it
	g.material_override = m
	_place(g, actor.global_position + Vector3.UP * (LIFT + 0.03))
	g.scale = Vector3(half * 2.0, 1.0, half * 2.0)
	var f := _facing()
	g.rotation.y = atan2(f.x, f.z)
	live.append({"node": g, "age": 0.0, "life": 0.4, "kind": "field"})


## Where plate i (0 front, 1 middle, 2 rear) sits on the shell right now, from the body's own bounds.
func _slot(i: int) -> Transform3D:
	var top := 0.9
	var length := 1.2
	if body != null and body.has_method("model_root") and body.model_root() != null:
		var box := AABB()
		var first := true
		for mi in body.model_root().find_children("*", "MeshInstance3D", true, false):
			var b: AABB = mi.global_transform * mi.get_aabb()
			box = b if first else box.merge(b)
			first = false
		if not first:
			top = box.end.y - actor.global_position.y
			length = maxf(box.size.x, box.size.z)
	var off: float = [0.28, 0.0, -0.3][i]
	var f := _facing()
	var pos := actor.global_position + f * off * length + Vector3.UP * (top - 0.06 - absf(off) * 0.35)
	var bs := Basis.looking_at(f, Vector3.UP).rotated(f.cross(Vector3.UP).normalized(), -off * 1.2)
	return Transform3D(bs, pos)


func _tear(targets: Array) -> void:
	var valid := []
	for t in targets:
		if is_instance_valid(t) and t is Node3D and t.is_inside_tree() and not (("alive" in t) and not t.alive):
			valid.append(t)
	if valid.is_empty():
		return
	if _plate_mesh == null:
		_plate_mesh = BoxMesh.new()
		_plate_mesh.size = Vector3(0.58, 0.08, 0.44)
	var hold := float(kit.salvage_time) if "salvage_time" in kit else SALV_HOLD
	for i in 3:
		var src: Node3D = valid[i % valid.size()]
		var from := src.global_position + Vector3.UP * randf_range(0.6, 0.85) + Vector3(randf_range(-0.2, 0.2), 0, randf_range(-0.2, 0.2))
		if i < valid.size():
			_spark(from, 1.0)
		var n := MeshInstance3D.new()
		n.mesh = _plate_mesh
		var m := ShaderMaterial.new()
		m.shader = PLATE
		n.material_override = m
		_place(n, from)
		n.rotation = Vector3(randf() * TAU, randf() * TAU, randf() * TAU)
		plates.append({"node": n, "mat": m, "from": from, "slot": i, "t": 0.0, "arrive": float(SALV_SNAPS[i]) - SALV_FIELD,
			"state": "fly", "hold": hold, "spin": Vector3(randf_range(-14, 14), randf_range(-14, 14), randf_range(-14, 14))})
	log_rows.append({"tear": valid.size(), "time": snappedf(elapsed, 0.01)})


func _update_salvage(delta: float) -> void:
	for s in _salv.duplicate():
		s.t += delta
		if not s.field and s.t >= SALV_FIELD:
			s.field = true
			_field()
			_tear(s.targets)
		if s.t > 0.6:
			_salv.erase(s)
	for pl in plates.duplicate():
		var n: MeshInstance3D = pl.node
		if not is_instance_valid(n):
			plates.erase(pl)
			continue
		pl.t += delta
		var slot := _slot(pl.slot)
		match pl.state:
			"fly":
				var u := clampf(pl.t / pl.arrive, 0.0, 1.0)
				var e := u * u  # pulled in, faster as it comes
				var ctrl: Vector3 = (pl.from + slot.origin) * 0.5 + Vector3.UP * 1.1
				var a: Vector3 = pl.from.lerp(ctrl, e)
				var b: Vector3 = ctrl.lerp(slot.origin, e)
				n.global_position = a.lerp(b, e)
				n.rotation += pl.spin * delta * (1.0 - e)
				if u >= 1.0:
					pl.state = "held"
					pl.t = 0.0
					_spark(slot.origin + Vector3.UP * 0.05, 0.8)
					log_rows.append({"snap": pl.slot, "time": snappedf(elapsed, 0.01)})
			"held":
				var pop := 1.0 + 0.35 * (1.0 - smoothstep(0.0, 0.12, pl.t))
				n.global_transform = Transform3D(slot.basis.scaled(Vector3.ONE * pop), slot.origin)
				pl.mat.set_shader_parameter("heat", lerpf(0.18, 1.0, 1.0 - smoothstep(0.0, 0.35, pl.t)))
				if pl.t >= pl.hold:
					pl.state = "drop"
					pl.t = 0.0
					rocks.append({"node": n, "vel": _facing() * -1.2 + Vector3(randf_range(-0.8, 0.8), 2.0, randf_range(-0.8, 0.8)),
						"spin": Vector3(randf_range(-6, 6), randf_range(-6, 6), randf_range(-6, 6)),
						"ground": actor.global_position.y + 0.03, "landed": false, "age": 1.0})
			"drop":
				pl.mat.set_shader_parameter("heat", 0.0)
				pl.mat.set_shader_parameter("fade", 1.0 - smoothstep(0.4, 1.2, pl.t))
				if pl.t > 1.2:
					plates.erase(pl)


## Rail dive cast begins (Rail_Launch time 0). target: the magnetised enemy it locked onto, or null for a short dash.
func rail_dive(target) -> void:
	_rail_free()
	var t: Node3D = target if (target is Node3D and is_instance_valid(target)) else null
	_dive = {"t": 0.0, "target": t, "lock": null, "streak": null, "start": _spine(), "arrived": false, "after": 0.0,
		"spark_clock": 0.0}
	if t != null:
		_dive.lock = _ribbon(0, 0.16)
		_spark(_spine(), 0.6)
	log_rows.append({"rail_dive": t.name if t != null else "spot", "time": snappedf(elapsed, 0.01)})


## Rail dive ends on arrival. charged: it arrived on a magnetised enemy and spent the charge for the extra damage.
func rail_arrive(charged: bool) -> void:
	if _dive.is_empty():
		return
	_dive.arrived = true
	_dive.after = 0.0
	var f := _facing()
	var hit_at := actor.global_position + f * 1.18  # Rail_Arrive: the claws slam 1.18 m ahead of the body centre
	var t = _dive.target
	if charged and t != null and is_instance_valid(t):
		hit_at = t.global_position
		_spark(hit_at + Vector3.UP * 0.75, 1.5)
		crash(hit_at, f, (WALK_SPEED + FULL_SPEED) * 0.5)  # the iron ball's impact at half power: one family of hits
		if marks.has(t):  # the charge is spent: the mark snaps once and goes out
			marks[t].snap = 1.0
			marks[t].left = minf(marks[t].left, 0.2)
	else:
		_ring_puffs(hit_at, 0.6, 4, 0.45, 0.5)
	log_rows.append({"rail_arrive": charged, "time": snappedf(elapsed, 0.01)})


## The top of the shell above the pangolin's centre, from the body's own bounds (also used for the salvage plates).
func _shell_top() -> float:
	var top := 0.9
	if body != null and body.has_method("model_root") and body.model_root() != null:
		var first := true
		var box := AABB()
		for mi in body.model_root().find_children("*", "MeshInstance3D", true, false):
			var bb: AABB = mi.global_transform * mi.get_aabb()
			box = bb if first else box.merge(bb)
			first = false
		if not first:
			top = box.end.y - actor.global_position.y
	return top


func _spine() -> Vector3:
	return actor.global_position + Vector3.UP * (_shell_top() - 0.05)


func _ribbon(mode: int, w: float) -> MeshInstance3D:
	var q := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE
	quad.subdivide_width = 24  # enough points for the pull line's arc to bend smoothly
	q.mesh = quad
	q.custom_aabb = AABB(Vector3(-500, -50, -500), Vector3(1000, 100, 1000))  # built in world space by the shader
	var m := ShaderMaterial.new()
	m.shader = RAIL
	m.set_shader_parameter("mode", mode)
	m.set_shader_parameter("width", w)
	m.set_shader_parameter("seed", randf() * 50.0)
	q.material_override = m
	_place(q, Vector3.ZERO)
	return q


func _rail_free() -> void:
	for k in ["lock", "streak"]:
		if _dive.has(k) and is_instance_valid(_dive[k]):
			_dive[k].queue_free()
	_dive = {}


func _update_dive(delta: float) -> void:
	if _dive.is_empty():
		return
	_dive.t += delta
	var head := _spine()
	var lock = _dive.lock
	if lock != null and is_instance_valid(lock):
		var m: ShaderMaterial = lock.material_override
		m.set_shader_parameter("age", _dive.t)
		m.set_shader_parameter("a", head)
		var t = _dive.target
		if t != null and is_instance_valid(t):
			m.set_shader_parameter("b", t.global_position + Vector3.UP * 0.75)
		if _dive.t > 0.26:
			lock.queue_free()
			_dive.lock = null
	if _dive.streak == null and _dive.t >= RAIL_RELEASE and not _dive.arrived:
		_dive.streak = _ribbon(1, 0.32)
		_dive.start = head
	var s = _dive.streak
	if s != null and is_instance_valid(s):
		var m2: ShaderMaterial = s.material_override
		var back: Vector3 = _dive.start - head
		var tail_len := minf(back.length(), RAIL_TRAIL)
		if _dive.arrived:  # the tail catches up to the head and the streak goes out
			_dive.after += delta
			tail_len *= 1.0 - smoothstep(0.0, 0.14, _dive.after)
			m2.set_shader_parameter("fade", 1.0 - smoothstep(0.04, 0.16, _dive.after))
		else:
			_dive.spark_clock += delta
			if _dive.spark_clock >= 0.07 and back.length() > 0.4:  # sparks thrown off the spine as it rides
				_dive.spark_clock = 0.0
				var side := _facing().cross(Vector3.UP)
				_spark(head + side * randf_range(-0.25, 0.25) - _facing() * 0.2, randf_range(0.3, 0.45))
		var tail := head + (back.normalized() * tail_len if back.length() > 0.001 else Vector3.ZERO)
		m2.set_shader_parameter("a", tail)
		m2.set_shader_parameter("b", head + _facing() * 0.15)
		m2.set_shader_parameter("age", _dive.t)
	if _dive.arrived and _dive.after > 0.2:
		_rail_free()
	elif _dive.t > 3.0:  # no arrival cue came: never leave a streak hanging
		_rail_free()


func _flare_off() -> void:
	_flare_t = -1.0


## The glow rides on the body's meshes as material_overlay, only while the flare is up (the slot the look lane keeps
## free for shield looks). Never replaces an overlay something else put there.
func _overlay(on: bool) -> void:
	if body == null or not body.has_method("model_root") or body.model_root() == null:
		return
	if _shell_mat == null:
		_shell_mat = ShaderMaterial.new()
		_shell_mat.shader = SHELL
	if on:
		for mi in body.model_root().find_children("*", "MeshInstance3D", true, false):
			if mi.material_overlay == null:
				mi.material_overlay = _shell_mat
				_overlaid.append(mi)
	else:
		for mi in _overlaid:
			if is_instance_valid(mi) and mi.material_overlay == _shell_mat:
				mi.material_overlay = null
		_overlaid.clear()


func _update_flare(delta: float) -> void:
	var up := _flare_t >= 0.0
	if up:
		_flare_t += delta
		if not ("flare_blocks" in kit) and _flare_t >= FLARE_LIFE:
			_flare_off()
			up = false
	var target := 0.0
	if up:
		target = 1.0 if _flare_blocks >= 2 else 0.55
	if not _comet.is_empty() and _comet.phase != "burst":
		target = maxf(target, 0.75)  # scrap comet: the shell runs hot under the stuck plates
	# Kuzenbo's glow comes up in a cell and goes out in a cell
	_flare_glow = move_toward(_flare_glow, target, delta / 0.08)
	_flare_pulse = maxf(0.0, _flare_pulse - delta * 5.0)
	if _shell_mat != null:
		_shell_mat.set_shader_parameter("strength", _flare_glow)
		_shell_mat.set_shader_parameter("pulse", _flare_pulse)
		_shell_mat.set_shader_parameter("time_s", elapsed)
	if _flare_glow <= 0.001 and not _overlaid.is_empty():
		_overlay(false)


## Marks target as magnetised for seconds; a second call refreshes it (the ring snaps again).
func magnetise(target: Node3D, seconds := MAG_TIME) -> void:
	if not is_instance_valid(target):
		return
	var row: Dictionary = marks.get(target, {})
	if row.is_empty():
		var q := MeshInstance3D.new()
		var plane := PlaneMesh.new()
		plane.size = Vector2.ONE
		q.mesh = plane
		var m := ShaderMaterial.new()
		m.shader = MAG
		q.material_override = m
		_place(q, target.global_position + Vector3.UP * (LIFT + 0.015))
		q.scale = Vector3.ONE * 3.5
		row = {"node": q}
		marks[target] = row
	row.left = seconds
	row.total = seconds
	row.snap = 1.0
	log_rows.append({"magnetise": target.name, "seconds": seconds, "time": snappedf(elapsed, 0.01)})


func _update_marks(delta: float) -> void:
	for target in marks.keys():
		var row: Dictionary = marks[target]
		var q: MeshInstance3D = row.node
		var alive: bool = is_instance_valid(target) and target.is_inside_tree() and not (("alive" in target) and not target.alive)
		row.left -= delta
		if not alive or row.left <= 0.0:
			if is_instance_valid(q):
				q.queue_free()
			marks.erase(target)
			continue
		row.snap = maxf(0.0, row.snap - delta * 6.0)
		q.global_position = target.global_position * Vector3(1, 0, 1) + Vector3.UP * (actor.global_position.y + LIFT + 0.015)
		var m: ShaderMaterial = q.material_override
		m.set_shader_parameter("remain", clampf(row.left / row.total, 0.0, 1.0))
		m.set_shader_parameter("snap", row.snap)
		m.set_shader_parameter("fade", smoothstep(0.0, 0.25, row.left))
		m.set_shader_parameter("time_s", elapsed)


func _ring_puffs(at: Vector3, rad: float, n: int, size: float, life: float) -> void:
	for i in n:
		var a := TAU * (float(i) + randf() * 0.5) / float(n)
		_dust(at + Vector3(cos(a), 0, sin(a)) * rad + Vector3.UP * 0.2, size * randf_range(0.8, 1.2), life)


func _dust(at: Vector3, size: float, life: float) -> void:
	var q := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE
	q.mesh = quad
	var m := ShaderMaterial.new()
	m.shader = DUST
	m.set_shader_parameter("life", life)
	m.set_shader_parameter("seed", randf() * 50.0)
	m.set_shader_parameter("dust", Vector3(DUST_COL.r, DUST_COL.g, DUST_COL.b))
	m.set_shader_parameter("strength", 0.6)
	q.material_override = m
	_place(q, at)
	q.scale = Vector3.ONE * size
	live.append({"node": q, "age": 0.0, "life": life, "kind": "dust"})


func _track(at: Vector3, dir: Vector3, heat: float, wide := 1.0) -> void:
	var q := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE
	q.mesh = plane
	var m := ShaderMaterial.new()
	m.shader = TRACK
	m.set_shader_parameter("heat", heat)
	m.set_shader_parameter("seed", randf() * 50.0)
	m.set_shader_parameter("life", 1.1)
	q.material_override = m
	_place(q, at + Vector3.UP * LIFT)
	q.scale = Vector3(0.55 * wide, 1.0, 0.75)
	q.rotation.y = atan2(dir.x, dir.z)
	live.append({"node": q, "age": 0.0, "life": 1.1, "kind": "track"})


func _rock(at: Vector3, vel: Vector3, size := 1.0) -> void:
	var n := MeshInstance3D.new()
	n.mesh = _rock_mesh
	n.material_override = _rock_mat
	var s := randf_range(0.10, 0.2) * size
	n.scale = Vector3(s, s * randf_range(0.6, 1.0), s * randf_range(0.7, 1.2))
	_place(n, at + Vector3.UP * 0.1)
	n.rotation = Vector3(randf() * TAU, randf() * TAU, randf() * TAU)
	rocks.append({"node": n, "vel": vel, "spin": Vector3(randf_range(-9, 9), randf_range(-9, 9), randf_range(-9, 9)), "ground": at.y + s * 0.3, "landed": false, "age": 0.0})


func _place(node: Node3D, at: Vector3) -> Node3D:
	if node is GeometryInstance3D:
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	node.top_level = true
	node.global_position = at
	return node


## While the kit says it is rolling: the furrow, the dust kicked back and the flank streaks follow the ball.
func _update_roll(delta: float) -> void:
	var rolling := (bool(kit.get("rolling")) or bool(kit.get("comet"))) if is_instance_valid(kit) else false
	var wide := _comet_size() * 0.6 if is_instance_valid(kit) and bool(kit.get("comet")) else 1.0  # the comet's furrow is as wide as the big ball
	_wake_fade = move_toward(_wake_fade, 1.0 if rolling else 0.0, delta / (0.2 if rolling else 0.15))
	_wake.visible = _wake_fade > 0.001
	if not rolling and not _wake.visible:
		return
	var dir: Vector3 = kit.roll_dir if rolling else Vector3.FORWARD
	dir.y = 0.0
	if dir.length() < 0.01:
		return
	dir = dir.normalized()
	var speed := float(kit.roll_speed)
	var s := _power(speed)
	var at := actor.global_position
	var length := 1.4 + 2.6 * s
	var head := 0.45  # metres of quad ahead of the ball's centre (the contact glow)
	_wake.scale = Vector3(1.7 * wide, 1.0, length + head)
	_wake.rotation.y = atan2(dir.x, dir.z)
	_wake.global_position = at + Vector3.UP * (LIFT + 0.02) + dir * (head - (length + head) * 0.5)
	var wm: ShaderMaterial = _wake.material_override
	wm.set_shader_parameter("speed01", s)
	wm.set_shader_parameter("fade", _wake_fade)
	wm.set_shader_parameter("time_s", elapsed)
	wm.set_shader_parameter("head_frac", head / (length + head))
	if not rolling:
		return
	if _last_drop == Vector3.INF:
		_last_drop = at
	if at.distance_to(_last_drop) >= 0.35:  # a segment every 0.35 m; they overlap into one furrow
		_track(at - dir * 0.25, dir, s, wide)
		_last_drop = at
	_dust_clock -= delta
	if _dust_clock <= 0.0:
		_dust_clock = lerpf(0.16, 0.07, s)
		var side := dir.cross(Vector3.UP) * randf_range(-0.35, 0.35)
		_dust(at - dir * randf_range(0.5, 0.8) + side + Vector3.UP * 0.25, lerpf(0.45, 0.85, s), lerpf(0.5, 0.65, s))


func _comet_size() -> float:
	return float(kit.comet_size) if is_instance_valid(kit) and "comet_size" in kit else 2.0


## Scrap comet cast: every stolen plate plus scrap from the floor around it flies onto the shell in an arc (0.35 s),
## the shell runs hot, and the plates stay stuck on, turning with the roll, until the burst.
func comet_start() -> void:
	if not _comet.is_empty():
		_comet_free()
	if _plate_mesh == null:
		_plate_mesh = BoxMesh.new()
		_plate_mesh.size = Vector3(0.58, 0.08, 0.44)
	var at := actor.global_position
	var list := []
	# floor scrap plus two more for each plate still worn from salvage (kit.comet_plates); no wrecks in the arena yet
	var count := mini(COMET_PLATES + 2 * (int(kit.comet_plates) if "comet_plates" in kit else 0), 18)
	# The 3D lane's model (2026-11-13) carries the stuck-on plates as real geometry with Comet_Gather / Comet_Roll /
	# Comet_Burst. Then the effect draws no plates of its own: it adds the pull field (scrap chunks and dust drawn in
	# along the plates' straight paths), the slam flash at the gather's 0.32 s, and debris after the burst.
	var model_plates: bool = body != null and body.has_method("has_clip") and body.has_clip("Comet_Gather")
	if model_plates:
		count = 0  # the pull field and the slam wait for Comet_Gather's "pull" and "plates_on" events (_on_event)
	for i in count:
		var a := TAU * (float(i) + randf() * 0.7) / float(count)
		var from := at + Vector3(cos(a), 0, sin(a)) * randf_range(2.5, 4.5) + Vector3.UP * randf_range(0.1, 0.5)
		var n := MeshInstance3D.new()
		n.mesh = _plate_mesh
		var m := ShaderMaterial.new()
		m.shader = PLATE
		m.set_shader_parameter("heat", 1.0)
		n.material_override = m
		_place(n, from)
		n.rotation = Vector3(randf() * TAU, randf() * TAU, randf() * TAU)
		# where it sits on the ball: a direction on the upper three quarters of a sphere, in the ball's own frame
		var off := Vector3(randf_range(-1, 1), randf_range(-0.3, 1), randf_range(-1, 1)).normalized()
		list.append({"node": n, "mat": m, "from": from, "off": off, "t": -randf() * 0.12})
		_dust(from + Vector3.UP * 0.2, 0.5, 0.4)
	_comet = {"phase": "in", "t": 0.0, "spin": 0.0, "plates": list, "model": model_plates, "slammed": false}
	_overlay(true)
	_flare_pulse = 1.0
	_ring_puffs(at, 1.2, 6, 0.6, 0.55)
	log_rows.append({"comet_start": count, "time": snappedf(elapsed, 0.01)})


## Comet_Gather "pull" (0.04 s): scrap chunks and dust drawn in along the model plates' straight paths, landing on the
## shell as the plates slam on 0.28 s later.
func _comet_pull() -> void:
	var at := actor.global_position
	var reach := 3.25 * _comet_size()
	for i in 10:
		var a2 := TAU * (float(i) + randf() * 0.6) / 10.0
		var from2 := at + Vector3(cos(a2), 0, sin(a2)) * reach * randf_range(0.7, 1.0) + Vector3.UP * randf_range(0.3, 1.0)
		var to := at + Vector3.UP * 0.9 * _comet_size()
		var tt := 0.28
		_rock(from2, (to - from2) / tt + Vector3.UP * 0.5 * GRAVITY * tt, 0.8)
		_dust(Vector3(from2.x, at.y, from2.z) + Vector3.UP * 0.25, 0.55, 0.35)
	log_rows.append({"comet_pull": true, "time": snappedf(elapsed, 0.01)})


## Comet_Gather "plates_on" (0.32 s): the slam flash as the model's plates hit the shell.
func _comet_slam() -> void:
	_spark(actor.global_position + Vector3.UP * 0.6 * _comet_size(), 1.0 * _comet_size())
	_flare_pulse = 1.0
	_ring_puffs(actor.global_position, 0.9 * _comet_size(), 6, 0.55, 0.45)
	log_rows.append({"comet_slam": true, "time": snappedf(elapsed, 0.01)})


## One enemy run over: the iron ball's crash at the comet's speed, a spark, and the ball's plates flash.
func comet_hit(at: Vector3) -> void:
	var dir: Vector3 = kit.roll_dir if "roll_dir" in kit else _facing()
	crash(at, dir, float(kit.roll_speed) if "roll_speed" in kit else FULL_SPEED)
	_spark(at + Vector3.UP * 0.9, 1.3)
	_flare_pulse = 1.0
	log_rows.append({"comet_hit": true, "size": snappedf(_comet_size(), 0.01), "time": snappedf(elapsed, 0.01)})


## The burst: every stuck plate is thrown outward and falls as a chunk, the copper ring goes out to the radius,
## a white-amber core and a short light. The shell cools.
func comet_burst(at: Vector3, r: float) -> void:
	_flare_ring(at, r, 1.0, 10)
	_spark(at + Vector3.UP * 1.0, 2.2)
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.72, 0.45)
	l.omni_range = r
	l.shadow_enabled = false
	_place(l, at + Vector3.UP * 1.0)
	live.append({"node": l, "age": 0.0, "life": 0.18, "kind": "light", "peak": 1.6})
	if not _comet.is_empty():
		for p in _comet.plates:
			var n: MeshInstance3D = p.node
			if not is_instance_valid(n):
				continue
			var out := Vector3(n.global_position.x - at.x, 0, n.global_position.z - at.z)
			out = out.normalized() if out.length() > 0.05 else Vector3(randf_range(-1, 1), 0, randf_range(-1, 1)).normalized()
			rocks.append({"node": n, "vel": out * randf_range(4.0, 7.0) + Vector3.UP * randf_range(3.0, 5.5),
				"spin": Vector3(randf_range(-12, 12), randf_range(-12, 12), randf_range(-12, 12)), "ground": at.y + 0.04,
				"landed": false, "age": 0.0})
		_comet.plates.clear()
		_comet.phase = "burst"
		if _comet.get("model", false):  # the model's plates shrink away; the effect throws the debris
			for i in 12:
				var a := TAU * (float(i) + randf() * 0.6) / 12.0
				var out := Vector3(cos(a), 0, sin(a))
				_rock(at + out * 0.8 + Vector3.UP * 0.8, out * randf_range(4.0, 7.0) + Vector3.UP * randf_range(3.0, 5.5), 1.1)
		_field_free()  # the field cuts out: that is why the plates fly off
	_comet = {}
	log_rows.append({"comet_burst": true, "radius": snappedf(r, 0.01), "time": snappedf(elapsed, 0.01)})


func _comet_free() -> void:
	_field_free()
	for p in _comet.get("plates", []):
		if is_instance_valid(p.node):
			p.node.queue_free()
	_comet = {}


func _update_comet(delta: float) -> void:
	if _comet.is_empty():
		return
	_comet.t += delta
	var size := _comet_size()
	var rad := 0.6 * size  # the plates sit on the big ball's skin (the pangolin ball is about 1.25 m across at 1x)
	var centre := actor.global_position + Vector3.UP * rad * 0.95
	var dir: Vector3 = kit.roll_dir if "roll_dir" in kit else _facing()
	dir.y = 0.0
	dir = dir.normalized() if dir.length() > 0.01 else Vector3.FORWARD
	var axis := dir.cross(Vector3.UP).normalized()
	var spd := float(kit.roll_speed) if "roll_speed" in kit else 0.0
	_comet.spin -= spd / maxf(rad, 0.1) * delta  # turning with the roll, so the plates read as stuck to a rolling ball
	var spin_b := Basis(axis, _comet.spin)
	var yaw := Basis(Vector3.UP, atan2(dir.x, dir.z))
	for p in _comet.plates:
		var n: MeshInstance3D = p.node
		if not is_instance_valid(n):
			continue
		p.t += delta
		var on: Vector3 = centre + spin_b * (yaw * p.off) * rad
		var k := clampf(p.t / COMET_IN, 0.0, 1.0)
		if k < 1.0:
			var e := k * k * (3.0 - 2.0 * k)
			n.global_position = p.from.lerp(on, e) + Vector3.UP * sin(k * PI) * 1.2
			n.rotation += Vector3(9, 7, 11) * delta
			p.mat.set_shader_parameter("heat", 1.0)
		else:
			var normal: Vector3 = (on - centre).normalized()
			n.global_transform = Transform3D(Basis.looking_at(normal.cross(axis).normalized() if absf(normal.dot(axis)) < 0.95 else dir, normal), on)
			p.mat.set_shader_parameter("heat", 0.35 + 0.65 * _flare_pulse)
	_update_field(delta, centre, rad, spin_b * yaw)
	if _comet.phase == "in" and _comet.t >= COMET_IN + 0.12:
		_comet.phase = "roll"


## The magnet field holding the scrap shell (Preston, 2026-11-13: "you can see the magnetism holding the ball in its
## shape while still being able to see pangolin through the gaps"). A rim-only copper field sphere at the shell's size,
## and COMET_LINES field lines from the curled pangolin's core out to points on the shell, pulses running inward
## (the pull). The lines and the sphere turn with the roll. They come on with the gather (0.35 s) and go at the burst.
func _field_make() -> void:
	var s := MeshInstance3D.new()
	var sm := SphereMesh.new()
	sm.radius = 1.0
	sm.height = 2.0
	sm.radial_segments = 32
	sm.rings = 16
	s.mesh = sm
	var m := ShaderMaterial.new()
	m.shader = FIELD_SHELL
	s.material_override = m
	_place(s, actor.global_position)
	var lines := []
	for i in COMET_LINES:
		# spread over the sphere (golden spiral), lower half skipped where the ball meets the floor
		var y := 1.0 - (float(i) + 0.5) / float(COMET_LINES) * 1.6
		var r := sqrt(maxf(1.0 - y * y, 0.0))
		var ang := float(i) * 2.39996
		lines.append({"node": _ribbon(2, 0.26), "off": Vector3(cos(ang) * r, y, sin(ang) * r), "age": randf() * 2.0})
	_comet.shell = s
	_comet.lines = lines
	_comet.field = 0.0


func _update_field(delta: float, centre: Vector3, rad: float, b: Basis) -> void:
	if not _comet.has("shell"):
		_field_make()
	_comet.field = minf(float(_comet.field) + delta / COMET_IN, 1.0)
	var f: float = _comet.field
	# The 3D lane's round-13 model: the plates are one node, scrap_shell, on the ball's centre bone. Its origin is the
	# ball's centre, it turns with the ball, and game feel scales it (2.0 to 2.6) while the pangolin stays normal size
	# in the middle. Plates lie at 0.66-0.68 of its scale; the curled pangolin reaches 0.64 m. Follow it when present.
	var inner := 0.0
	if not _comet.has("shell_node"):
		_comet.shell_node = body.find_child("scrap_shell", true, false) if body != null else null
	var sn = _comet.shell_node
	if sn is Node3D and is_instance_valid(sn):
		var gb: Basis = sn.global_basis
		centre = sn.global_position
		rad = 0.67 * sn.scale.x  # the 3D lane's sizes are against the node's own scale (2.0-2.6), not its world scale
		b = gb.orthonormalized()
		inner = 0.64  # lines stop at the curled pangolin's skin (0.64 m from the centre)
		if not _comet.has("logged"):
			_comet.logged = true
			log_rows.append({"field_on_shell": true, "rad": snappedf(rad, 0.01), "world_scale": snappedf(gb.get_scale().x, 0.01), "time": snappedf(elapsed, 0.01)})
	var s: MeshInstance3D = _comet.shell
	if is_instance_valid(s):
		s.global_transform = Transform3D(b.scaled(Vector3.ONE * rad * 1.04), centre)
		var sm: ShaderMaterial = s.material_override
		sm.set_shader_parameter("fade", f)
		sm.set_shader_parameter("time_s", elapsed)
		sm.set_shader_parameter("pulse", _flare_pulse)
	var core := actor.global_position + Vector3.UP * 0.55  # the curled pangolin at normal size
	for l in _comet.lines:
		if not is_instance_valid(l.node):
			continue
		l.age += delta
		var m: ShaderMaterial = l.node.material_override
		m.set_shader_parameter("a", centre + b * l.off * rad * 0.97)  # pulses run a to b: from the shell in to the core
		m.set_shader_parameter("b", centre + b * l.off * inner if inner > 0.0 else core)
		m.set_shader_parameter("arc", 0.12 * rad)
		m.set_shader_parameter("age", l.age)
		m.set_shader_parameter("fade", f * 1.4)  # louder inner lines (Preston 2026-11-14)


func _field_free() -> void:
	if _comet.has("shell") and is_instance_valid(_comet.shell):
		_comet.shell.queue_free()
	for l in _comet.get("lines", []):
		if is_instance_valid(l.node):
			l.node.queue_free()
	_comet.erase("shell")
	_comet.erase("lines")


## The magnet pull line: while the roll is bent toward a magnetised enemy (kit.mag_pull), a faint copper line runs
## from the enemy's chest to the shell with amber pulses travelling toward the ball. On in 0.08 s, off in 0.15 s, and
## it switches straight to a new enemy if the pull changes. No light, no floor mark: the mark on the enemy is the anchor.
func _update_pull(delta: float) -> void:
	var t = kit.get("mag_pull") if bool(kit.get("rolling")) else null
	if t != null and not is_instance_valid(t):
		t = null
	if t != null:
		if _pull.is_empty() or not is_instance_valid(_pull.node):
			_pull = {"node": _ribbon(2, 0.22), "age": 0.0, "fade": 0.0, "target": t}
			log_rows.append({"pull_on": t.name, "time": snappedf(elapsed, 0.01)})
		_pull.target = t
		_pull.fade = minf(_pull.fade + delta / 0.08, 1.0)
	elif not _pull.is_empty():
		_pull.fade -= delta / 0.15
		if _pull.fade <= 0.0 or not is_instance_valid(_pull.node):
			if is_instance_valid(_pull.node):
				_pull.node.queue_free()
			log_rows.append({"pull_off": true, "time": snappedf(elapsed, 0.01)})
			_pull = {}
			return
	if _pull.is_empty():
		return
	_pull.age += delta
	var tgt = _pull.target
	if tgt == null or not is_instance_valid(tgt):
		_pull.fade = minf(_pull.fade, 0.0)
		return
	var m: ShaderMaterial = _pull.node.material_override
	m.set_shader_parameter("a", tgt.global_position + Vector3.UP * 0.8)
	m.set_shader_parameter("b", _spine())
	var span: float = (tgt.global_position - actor.global_position).length()
	m.set_shader_parameter("arc", clampf(span * 0.3, 0.6, 2.0))  # a field arc over both machines, readable from behind
	m.set_shader_parameter("age", _pull.age)
	m.set_shader_parameter("fade", clampf(_pull.fade, 0.0, 1.0))


func _process(delta: float) -> void:
	elapsed += delta
	if is_instance_valid(actor) and is_instance_valid(kit):
		_update_roll(delta)
		_update_flare(delta)
		_update_marks(delta)
		_update_salvage(delta)
		_update_dive(delta)
		_update_pull(delta)
		_update_comet(delta)
		_update_bands(delta)
	for row in live.duplicate():
		row.age += delta
		var n = row.node
		if not is_instance_valid(n):
			live.erase(row)
			continue
		match row.kind:
			"light":
				n.light_energy = float(row.peak) * (1.0 - smoothstep(0.0, row.life, row.age))
			_:
				n.material_override.set_shader_parameter("age", row.age)
		if row.age >= row.life:
			n.queue_free()
			live.erase(row)
	for rock in rocks.duplicate():
		rock.age += delta
		var rn: MeshInstance3D = rock.node
		if not rock.landed:
			rock.vel.y -= GRAVITY * delta
			rn.global_position += rock.vel * delta
			rn.rotation += rock.spin * delta
			if rn.global_position.y <= rock.ground and rock.vel.y < 0.0:
				rn.global_position.y = rock.ground
				if rock.vel.y < -3.0:
					rock.vel = Vector3(rock.vel.x * 0.35, -rock.vel.y * 0.25, rock.vel.z * 0.35)
					rock.spin *= 0.4
				else:
					rock.landed = true
		if rock.age > 1.6:
			rn.global_position.y -= delta * 0.25
		if rock.age >= 2.2:
			rn.queue_free()
			rocks.erase(rock)
