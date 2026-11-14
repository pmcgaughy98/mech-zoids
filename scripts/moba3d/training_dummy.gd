class_name TrainingDummy
extends Node3D
## A training dummy for trying kits on (Claude, 2026-11-04). The art is ours (tools/art/pack_rhino_3d.py). It only
## reacts: a flash and a shake when hit, a violet tint while slowed, the stun stars while stunned, and the arcs and
## shoves the rhino's kit gives it. No health yet; the slice has no numbers.
## Walls: every move slides along the arena's walls (ArenaMotion). An enemy dummy cannot cross a gorilla hex dome's
## wall either way, and fire_at() shoots a TestShot for the attacks it does not have yet (Preston, 2026-11-04).

const TEX := preload("res://art/fx/moba3d/training_dummy.png")
const SHADOW := preload("res://art/field/moba3d/shadow.png")
const PX := 0.02
const MARK := preload("res://art/fx/moba3d/taunt_mark.png") ## over a taunted dummy's head
const BODY_R := 0.35 ## how far inside a dome's wall a trapped dummy's middle stops

var stunned := 0.0
var slowed := 0.0
var last_hit_scale := 1.0 ## the damage scale the last kit hit carried (checks read it)
var air := 0.0 ## height above the ground while thrown
var taunted := 0.0 ## seconds left being forced to attack taunted_by (gorilla chest beat)
var taunted_by: Node3D = null
var tint := Color.WHITE ## team tint: an ally dummy in the test fields is set blue
var cage: HexShield = null ## the hex dome trapping this enemy until it ends (gorilla ultimate)
var _bumped := false ## the wall has already sparked for this move
var _mark: Sprite3D
var _flash := 0.0
var push := Vector3.ZERO ## the shove's offset, local; eased back to zero
var _push_tw: Tween = null
var _sprite: Sprite3D
var _stars: AnimatedSprite3D
var _from := Vector3.ZERO
var _to := Vector3.ZERO
var _height := 0.0
var _base_y := 0.0
var _move_tw: Tween ## the move under way (toss, shove or walk)


func _ready() -> void:
	add_to_group("kit_target")
	_sprite = Sprite3D.new()
	_sprite.texture = TEX
	_sprite.pixel_size = PX
	_sprite.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	_sprite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	_sprite.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	_sprite.shaded = false
	_base_y = (TEX.get_height() / 2.0 - 2.0) * PX  # the base plank's outline is the third row from the bottom
	_sprite.position.y = _base_y
	add_child(_sprite)
	var m := StandardMaterial3D.new()
	m.albedo_texture = SHADOW
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	var pm := PlaneMesh.new()
	pm.size = Vector2(1.1, 0.55)
	pm.material = m
	var sh := MeshInstance3D.new()
	sh.mesh = pm
	sh.position.y = 0.015
	add_child(sh)


func _process(delta: float) -> void:
	if has_meta("held_by"):return
	_flash = maxf(_flash - delta, 0.0)
	slowed = maxf(slowed - delta, 0.0)
	if stunned > 0.0:
		stunned -= delta
		if stunned <= 0.0 and _stars != null:
			_stars.queue_free()
			_stars = null
	if taunted > 0.0:
		taunted -= delta
		if _mark != null:
			_mark.visible = fmod(taunted, 0.3) > 0.08  # a quick blink so the mark reads as live
		if taunted <= 0.0:
			taunted_by = null
			if _mark != null:
				_mark.queue_free()
				_mark = null
	var c := tint
	if slowed > 0.0:
		c = Color(0.72, 0.6, 1.0)
	if _flash > 0.0:
		c = Color(2.2, 2.2, 2.2)
	_sprite.modulate = c
	var shake := sin(_flash * 120.0) * 0.05 if _flash > 0.0 else 0.0
	_sprite.position = Vector3(shake, _base_y + air, 0.0) + push


## KitFeel.basic_hit's shove: the sprite (and a minion's drone) offset by world_offset at once, eased back over back.
func shove(world_offset: Vector3, back := 0.18) -> void:
	push = global_basis.inverse() * world_offset
	push.y = 0.0
	if _push_tw != null and _push_tw.is_valid():
		_push_tw.kill()
	_push_tw = create_tween()
	_push_tw.tween_property(self, "push", Vector3.ZERO, back).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)


func hit(_by: Node3D = null, scale := 1.0) -> void: ## a kit passes its machine and a damage scale; the match minions use them
	_flash = 0.16
	last_hit_scale = scale


func stun(t: float) -> void:
	stunned = maxf(stunned, t)
	if _stars == null:
		_stars = Fx3D.spawn(self, "stun_loop", global_position + Vector3.UP * (TEX.get_height() * PX + 0.1), 0.0, true)


func slow(t: float) -> void:
	slowed = maxf(slowed, t)


## Forced to attack `by` for t seconds (gorilla chest beat); the green mark over its head shows it.
func taunt(by: Node3D, t: float) -> void:
	taunted = maxf(taunted, t)
	taunted_by = by
	if _mark == null:
		_mark = Sprite3D.new()
		_mark.texture = MARK
		_mark.pixel_size = PX
		_mark.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
		_mark.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		_mark.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		_mark.shaded = false
		_mark.position.y = TEX.get_height() * PX + 0.4  # above the stun stars
		add_child(_mark)


## Thrown in an arc to land, then a puff and a stun (horn toss).
func toss_to(land: Vector3, height: float, time: float, stun_t: float, deal := true) -> void:  # deal false: the lift only
	if deal:
		hit()
	_from = global_position
	_to = land
	_bumped = false
	_height = height
	var tw := _move_tween()
	tw.tween_method(_arc_step, 0.0, 1.0, time)
	await tw.finished
	air = 0.0
	Fx3D.spawn(get_parent(), "impact_puff", global_position, 0.3)
	hit()
	stun(stun_t)


## Shoved aside with a small hop (stampede).
func knock_aside(offset: Vector3, time: float, deal := true) -> void:  # deal false: the push only (rhino release)
	if deal:
		hit()
	_from = global_position
	_to = global_position + offset
	_bumped = false
	_height = 0.5
	_move_tween().tween_method(_shove_step, 0.0, 1.0, time)


func _arc_step(k: float) -> void:
	_move_to(_from.lerp(_to, k))
	air = _height * 4.0 * k * (1.0 - k)


func _shove_step(k: float) -> void:
	_move_to(_from.lerp(_to, 1.0 - (1.0 - k) * (1.0 - k)))
	air = _height * 4.0 * k * (1.0 - k)


## Every move goes through here: arena walls stop it (it slides along them), then a hex dome's wall if it is an enemy.
func _move_to(p: Vector3) -> void:
	var prev := global_position
	global_position = ArenaMotion.slide(self, prev, p - prev, BODY_R)
	_dome_walls(prev)


## A new move replaces the one under way instead of fighting it for the position.
func _move_tween() -> Tween:
	halt()
	_move_tw = create_tween()
	return _move_tw


## Stops whatever move is under way (the fennec's tunnel takes an ally mid-walk).
func halt() -> void:
	if _move_tw != null and _move_tw.is_valid():
		_move_tw.kill()
	air = 0.0


## Fires a test shot toward p (TestShot): the dummies have no attacks of their own yet.
func fire_at(p: Vector3, hit_node: Node3D = null) -> TestShot:
	return TestShot.fire(get_parent(), global_position, p, is_in_group("kit_target"), hit_node)


## Trapped under a hex dome (ApeKit.hex_dome): it cannot leave until the dome ends.
func trap(dome: HexShield) -> void:
	cage = dome


## Slides to p over time: the reveals' stand-in for walking, since a dummy has no legs. A dome it is trapped in stops it.
func walk_to(p: Vector3, time: float) -> void:
	_from = global_position
	_to = p
	_height = 0.0
	_bumped = false
	_move_tween().tween_method(_shove_step, 0.0, 1.0, time)


## Hex domes (gorilla ultimate; Preston, 2026-11-04): an enemy inside when one rose is trapped until it ends, and an
## enemy outside cannot walk in. Either way it stops at the wall, with a spark and the wall's flash the first time.
## Allies (group kit_ally) cross both ways. Called from each move step, so a tween never carries it through for a frame.
func _dome_walls(prev: Vector3) -> void:
	if cage != null and (not is_instance_valid(cage) or not cage.is_up()):
		cage = null
	for dome: HexShield in HexShield.live_domes():
		if not _blocked_by(dome):
			continue
		var c := dome.global_position
		var was := Vector2(prev.x - c.x, prev.z - c.z).length()
		var d := Vector3(global_position.x - c.x, 0.0, global_position.z - c.z)
		var inside := dome == cage or was <= dome.radius
		var r := dome.radius - BODY_R if inside else dome.radius + BODY_R
		if (inside and d.length() <= r) or (not inside and d.length() >= r):
			continue
		if not dome.blocks_at(global_position):  # through a broken panel's gap
			if cage == dome:
				cage = null
			continue
		var n := d.normalized()
		if d.length() < 0.001:
			n = Vector3(prev.x - c.x, 0.0, prev.z - c.z).normalized() if was > 0.001 else Vector3.RIGHT
		global_position = Vector3(c.x + n.x * r, global_position.y, c.z + n.z * r)
		if not _bumped:
			_bumped = true
			dome.hit()
			var face := n * (BODY_R if inside else -BODY_R)
			Fx3D.spawn(get_parent(), "deflect_spark", global_position + face + Vector3.UP * 0.9, 0.3)


## Whether a dome's wall holds this dummy: enemies of the gorilla only, which in the test fields is group kit_target.
## A match minion (MatchMinion) asks the dome's team instead.
func _blocked_by(dome: HexShield) -> bool:
	return is_in_group("kit_target") or dome.cage_all  # the ult cage holds the gorilla's side too (2026-11-09)
