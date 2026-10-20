extends RefCounted
## Battle effects (Claude, 2026-10-15; Preston: "start adding VFX's and effects to weapons/animations etc. everything
## that needs it"). Every effect is drawn here in code, in art pixels on the battle field, so it scales with the field
## and stays as crisp as the machines: muzzle flashes, projectiles, beams, ground shockwaves, sparks, explosions,
## smoke and dust, plus the screen-level beats (shake, white flash, hit freeze) and the struck machine's reaction.
##
## Structure from shipped games, our own code (docs/reference/battle-vfx-2026-10-15.md): Zoids Legacy builds each
## weapon's animation from a shared library of about a hundred effect pieces (beams, smoke-trail projectiles, missile
## volleys, explosion columns, white flashes, background shake); the Pokemon GBA games script each move as timed calls
## into a shared library too. So effects here are small reusable pieces, and scripts/battle/vfx_recipes.gd says which
## pieces each weapon uses and when, by clip frame. scripts/scenes/battle.gd calls play_attack() and the step effects.
##
## Effects animate on 30 fps steps (two GBA frames a step), colours step down short ramps instead of fading smoothly,
## and positions round to whole art pixels, the way sprite-sheet effects look.

const Anim := preload("res://scripts/ui/machine_anim.gd")
const FLASH_SHADER := preload("res://shaders/hit_flash.gdshader")
const STEP := 1.0 / 30.0

## Colour ramps, brightest first. Cyan is the machines' shared "light" colour (5fe1d0).
const RAMPS := {
	"fire": [Color("fffbe6"), Color("ffe680"), Color("ffb03b"), Color("e8642a"), Color("a8321e"), Color("4a2a26")],
	"spark": [Color("ffffff"), Color("fff3a0"), Color("ffc94a"), Color("d9822b")],
	"cyan": [Color("ffffff"), Color("c8fff6"), Color("5fe1d0"), Color("2a9d9a"), Color("16545e")],
	"water": [Color("ffffff"), Color("d6f2ff"), Color("8fd0f0"), Color("4a90c8"), Color("2a5a8a")],
	"red": [Color("fff0e8"), Color("ff7a5a"), Color("e02a2a"), Color("9a1420"), Color("4a0a10")],
	"dust": [Color("fffaf0"), Color("f2e8d2"), Color("dccdac"), Color("b8a684"), Color("8c7c62")],   # lighter than the dirt it rises from
	"smoke": [Color("cfc8bc"), Color("9a9288"), Color("6c655e"), Color("48433f")],
	"steel": [Color("f2f6f8"), Color("b4c0c8"), Color("76828a"), Color("444c54")],
	"ochre": [Color("ffe4a0"), Color("f6c35a"), Color("da8600"), Color("a05a00"), Color("5c3400")],
	"brass": [Color("fff0b0"), Color("e6c050"), Color("a8802a")],
	"heal": [Color("ffffff"), Color("c8ffd8"), Color("7cff9a"), Color("2ea85a")],
}

var field: Node2D            # the zoomed-out battle field (field units = art pixels)
var stage: Node2D            # background + field: the screen shake moves it
var back: Node2D             # effects behind the machines (ground cracks, after-images)
var front: Node2D            # effects in front of them (battle.gd adds it after the machines)
var flash_rect: ColorRect    # the whole-stage flash
var background: CanvasItem   # dimmed while a beam fires
var rng := RandomNumberGenerator.new()
var clock := 0.0
var pending: Array = []      # [{"t", "fn"}], sorted: what after() scheduled
var shake_amp := 0.0
var shake_left := 0.0
var shake_life := 0.0
var _shake_step := -1
var last := {}               # the last attack's worked-out points (its contact), for the checks
var _rects := {}             # texture -> its opaque rect, and its Image for point lookups
var _images := {}


## One effect: draws itself in field units from its age, quantized to STEP, and frees itself when its life is over.
class Fx extends Node2D:
	var t := 0.0
	var life := 0.5
	var shown := -1
	var paint: Callable      # paint(fx: Fx, age: float): draw calls in field units

	func _process(delta: float) -> void:
		t += delta
		if t >= life:
			queue_free()
			return
		var k := int(t / STEP)
		if k != shown:
			shown = k
			queue_redraw()

	func _draw() -> void:
		paint.call(self, maxf(0, shown) * STEP)


## Drives after() and the shake from the scene tree, so nothing fires once the battle scene is gone.
class Ticker extends Node:
	var vfx: RefCounted

	func _process(delta: float) -> void:
		vfx._tick(delta)


func setup(field_node: Node2D, stage_node: Node2D, bg: CanvasItem, seed_value := 7) -> void:
	field = field_node
	stage = stage_node
	background = bg
	rng.seed = seed_value
	back = Node2D.new()
	back.name = "fx_back"
	field.add_child(back)
	var ticker := Ticker.new()
	ticker.name = "fx_ticker"
	ticker.vfx = self
	field.add_child(ticker)
	flash_rect = ColorRect.new()
	flash_rect.name = "fx_flash"
	flash_rect.position = Vector2(-16, -16)
	flash_rect.size = Vector2(352, 212)
	flash_rect.color = Color(1, 1, 1, 0)
	flash_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stage.add_child(flash_rect)


## Gives a machine node the hit-flash material; everything under it draws through it (the older drawn machines nest
## their parts two levels down).
static func prepare_flash(node: Node2D) -> void:
	var m := ShaderMaterial.new()
	m.shader = FLASH_SHADER
	node.material = m
	for c in node.find_children("*", "CanvasItem", true, false):
		c.use_parent_material = true


# --- timing ---------------------------------------------------------------------------------------------------------

## Calls `fn` `delay` seconds from now (on the battle's clock; nothing fires after the scene closes).
func after(delay: float, fn: Callable) -> void:
	var e := {"t": clock + maxf(0.0, delay), "fn": fn}
	var i := pending.bsearch_custom(e, func(a, b): return a.t < b.t, false)
	pending.insert(i, e)


func _tick(delta: float) -> void:
	clock += delta
	while not pending.is_empty() and pending[0].t <= clock:
		pending.pop_front().fn.call()
	if shake_left > 0.0:
		shake_left -= delta
		var k := int(clock / STEP)
		if k != _shake_step:   # a new offset every step, swinging side to side, shrinking to nothing
			_shake_step = k
			var amp := shake_amp * maxf(0.0, shake_left / shake_life)
			var side := 1.0 if k % 2 == 0 else -1.0
			stage.position = Vector2(roundf(side * amp), roundf(rng.randf_range(-0.5, 0.5) * amp))
		if shake_left <= 0.0:
			stage.position = Vector2.ZERO


# --- pixel drawing ---------------------------------------------------------------------------------------------------

static func ramp_at(ramp: Array, u: float) -> Color:
	return ramp[clampi(int(u * ramp.size()), 0, ramp.size() - 1)]


static func dot(ci: CanvasItem, p: Vector2, col: Color, size := 1) -> void:
	ci.draw_rect(Rect2(p.round() - Vector2(size / 2, size / 2), Vector2(size, size)), col)


## A filled circle of whole pixels.
static func disc(ci: CanvasItem, c: Vector2, r: float, col: Color, squash := 1.0) -> void:
	if r < 0.75:
		dot(ci, c, col)
		return
	var cx := roundi(c.x)
	var cy := roundi(c.y)
	var ry := maxi(0, roundi(r * squash))
	for dy in range(-ry, ry + 1):
		var v := float(dy) / maxf(0.5, r * squash)
		var hw := floori(r * sqrt(maxf(0.0, 1.0 - v * v)) + 0.5)
		ci.draw_rect(Rect2(cx - hw, cy + dy, hw * 2 + 1, 1), col)


## A circle or ellipse outline of whole pixels; `a0`..`a1` (radians) draws an arc of it.
static func ring(ci: CanvasItem, c: Vector2, r: float, col: Color, squash := 1.0, thick := 1, a0 := 0.0, a1 := TAU) -> void:
	var n := maxi(12, int(absf(a1 - a0) * r * 1.2))
	var last := Vector2(INF, INF)
	for i in n + 1:
		var a := a0 + (a1 - a0) * i / n
		var p := Vector2(c.x + cos(a) * r, c.y + sin(a) * r * squash).round()
		if p != last:
			ci.draw_rect(Rect2(p, Vector2(thick, thick)), col)
			last = p


## A line of whole pixels, `w` wide.
static func line(ci: CanvasItem, a: Vector2, b: Vector2, col: Color, w := 1) -> void:
	var d := b - a
	var n := maxi(1, int(maxf(absf(d.x), absf(d.y))))
	var o := Vector2(w / 2, w / 2)
	for i in n + 1:
		ci.draw_rect(Rect2((a + d * (float(i) / n)).round() - o, Vector2(w, w)), col)


## `glow`: drawn additively, the way Zoids Legacy blends its beam, spark and charge sprites over the background.
func spawn(layer: Node2D, life: float, paint: Callable, glow := false) -> Fx:
	var f := Fx.new()
	f.life = life
	f.paint = paint
	if glow:
		var m := CanvasItemMaterial.new()
		m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		f.material = m
	layer.add_child(f)
	return f


# --- where things are ------------------------------------------------------------------------------------------------

## A frame's opaque rect (art pixels, inside its canvas).
func art_rect(tex: Texture2D) -> Rect2i:
	if tex == null:
		return Rect2i(0, 0, 1, 1)
	if not _rects.has(tex):
		var img := tex.get_image()
		if img.is_compressed():
			img.decompress()
		_images[tex] = img
		_rects[tex] = img.get_used_rect()
	return _rects[tex]


## The texture a machine shows for `clip` frame `k` (k < 0: its first idle frame; no animation: its view).
func frame_tex(node: Node2D, clip: String, k: int) -> Texture2D:
	var a := node.get_node_or_null("anim") as AnimatedSprite2D
	if a != null:
		if k >= 0 and a.sprite_frames.has_animation(clip):
			return a.sprite_frames.get_frame_texture(clip, mini(k, a.sprite_frames.get_frame_count(clip) - 1))
		var hold := "idle" if a.sprite_frames.has_animation("idle") else a.sprite_frames.get_animation_names()[0]
		return a.sprite_frames.get_frame_texture(hold, 0)
	for c in node.find_children("*", "Sprite2D", true, false):
		return c.texture
	return null


## The opaque rect of `tex`, or the machine's whole canvas when it has no image (the older drawn machines).
func rect_of(node: Node2D, tex: Texture2D) -> Rect2i:
	if tex == null:
		return Rect2i(0, 0, int(node.get_meta("width", 64)), int(node.get_meta("height", 48)))
	return art_rect(tex)


## A point on a machine in field units. `pt`: "front" (the edge facing the foe), "back", "center", "top" or "feet";
## `y` is a fraction of the art's height (0 its top, 1 its feet) for front, back and center.
func point(node: Node2D, pt: String, y: float, clip := "", k := -1) -> Vector2:
	var tex := frame_tex(node, clip, k)
	var r := rect_of(node, tex)
	var local := Vector2(r.position.x + r.size.x / 2.0, r.position.y + r.size.y * y)
	match pt:
		"front", "back":
			local.x = _edge(tex, r, roundi(local.y), pt == "front")
		"top":   # the topmost opaque pixels (a raised hand, a crest), not the box's middle
			local = _top_point(tex, r)
		"feet":
			local.y = float(node.get_meta("feet_y", r.end.y))
	return node.position + Vector2(local.x * node.scale.x, local.y)


func _top_point(tex: Texture2D, r: Rect2i) -> Vector2:
	var img: Image = _images.get(tex)
	if img == null:
		return Vector2(r.position.x + r.size.x / 2.0, r.position.y)
	for y in range(r.position.y, r.end.y):
		var xs := []
		for x in range(r.position.x, r.end.x):
			if img.get_pixel(x, y).a > 0.5:
				xs.append(x)
		if xs.size() >= 2:
			return Vector2((xs[0] + xs[-1]) / 2.0, y + 1)
	return Vector2(r.position.x + r.size.x / 2.0, r.position.y)


# the furthest opaque column toward (front) or away from the foe, in a 5-row band around `row`
func _edge(tex: Texture2D, r: Rect2i, row: int, front_side: bool) -> float:
	var img: Image = _images.get(tex)
	if img == null:
		return float(r.end.x if front_side else r.position.x)
	var best := -1
	for y in range(maxi(r.position.y, row - 2), mini(r.end.y, row + 3)):
		for i in r.size.x:
			var x: int = r.end.x - 1 - i if front_side else r.position.x + i
			if img.get_pixel(x, y).a > 0.5:
				if best < 0 or (front_side and x > best) or (not front_side and x < best):
					best = x
				break
	if best < 0:
		return float(r.end.x if front_side else r.position.x)
	return best + 1.0 if front_side else float(best)


## The frame's frontmost opaque point (local, art pixels) between heights `band` (fractions of the art's height, 0 its
## top): what leads a blow, a fist, a bill, two feet. The band keeps a kangaroo's long feet from counting as its jab.
func frontmost(tex: Texture2D, band := [0.0, 0.8]) -> Vector2:
	var r := art_rect(tex)
	var img: Image = _images.get(tex)
	if img == null:
		return Vector2(r.end.x, r.position.y + r.size.y * 0.4)
	var y0 := r.position.y + int(r.size.y * float(band[0]))
	var y1 := r.position.y + int(ceilf(r.size.y * float(band[1])))
	for i in r.size.x:
		var x := r.end.x - 1 - i
		var ys := []
		for y in range(y0, y1):
			if img.get_pixel(x, y).a > 0.5:
				ys.append(y)
		if ys.size() >= 2:   # a single stray pixel is not a fist
			return Vector2(x + 1, (ys[0] + ys[-1]) / 2.0)
	return Vector2(r.end.x, r.position.y + r.size.y * 0.4)


## Where a recipe's anchor is. A spec is {"of": "actor"|"target", "pt", "y", "frame", "dx", "dy"} or a shortcut name;
## "contact" is where a melee blow lands (play_attack works it out), or the target's front when there is none.
func anchor(spec, actor: Node2D, target: Node2D, clip: String, ctx := {}) -> Vector2:
	if spec is String and spec == "contact":
		return ctx.get("contact", anchor("target_front", actor, target, clip))
	var s: Dictionary = SHORTCUTS.get(spec, {}) if spec is String else spec
	var of_actor: bool = s.get("of", "target") == "actor"
	var node := actor if of_actor else target
	var dir := signf(node.scale.x)   # +1: facing right
	var p := point(node, s.get("pt", "center"), s.get("y", 0.45), clip if of_actor else "", s.get("frame", -1) if of_actor else -1)
	return p + Vector2(float(s.get("dx", 0)) * dir, float(s.get("dy", 0)))


const SHORTCUTS := {
	"target": {"of": "target", "pt": "center", "y": 0.45},
	"target_front": {"of": "target", "pt": "front", "y": 0.4},
	"target_low": {"of": "target", "pt": "front", "y": 0.75},
	"target_feet": {"of": "target", "pt": "feet"},
	"target_top": {"of": "target", "pt": "top"},
	"actor_feet": {"of": "actor", "pt": "feet"},
	"actor_center": {"of": "actor", "pt": "center", "y": 0.5},
}


# --- the effects -------------------------------------------------------------------------------------------------------
# Each takes a start point, an end point (for things that travel), the direction it faces (+1 right, -1 left) and its
# parameters. Field units, seconds.

## The effect names play() knows, and the cue-only ones _cue() handles (tools/debug/vfx_check.gd checks recipes use
## nothing else).
const EFFECTS := ["sparks", "star", "burst", "explosion", "smoke", "dust", "debris", "spray", "rings", "slash", "streak",
	"flame", "charge_in", "sparkle", "speed_lines", "projectile", "beam", "wave", "sound"]
const CUE_ONLY := ["afterimage", "shake", "flash_stage"]


## Plays one recipe cue by name.
func play(fx_name: String, pos: Vector2, to: Vector2, dir: float, p: Dictionary) -> void:
	match fx_name:
		"sparks": sparks(pos, dir, p)
		"star": star(pos, p)
		"burst": burst(pos, p)
		"explosion": explosion(pos, p)
		"smoke": smoke(pos, p)
		"dust": dust(pos, dir, p)
		"debris": debris(pos, dir, p)
		"spray": spray(pos, dir, p)
		"rings": rings(pos, dir, p)
		"slash": slash(pos, dir, p)
		"streak": streak(pos, dir, p)
		"flame": flame(pos, dir, p)
		"charge_in": charge_in(pos, p)
		"sparkle": sparkle(pos, p)
		"speed_lines": speed_lines(pos, dir, p)
		"projectile": projectile(pos, to, p)
		"beam": beam(pos, to, p)
		"wave": wave(pos, to, p)
		"sound": sound_waves(pos, to, dir, p)
		_:
			push_warning("vfx: no effect named %s" % fx_name)


## Hot sparks flung out of an impact, mostly onward (the way the blow travels), falling a little.
func sparks(pos: Vector2, dir: float, p: Dictionary) -> void:
	var life: float = p.get("life", 0.3)
	var ramp: Array = RAMPS[p.get("ramp", "spark")]
	var spread := deg_to_rad(p.get("spread", 70.0))
	var base := deg_to_rad(p.get("angle", 0.0 if dir > 0 else 180.0))
	var g: float = p.get("gravity", 180.0)
	var parts := []
	for i in int(p.get("count", 8)):
		var a := base + rng.randf_range(-spread, spread)
		parts.append({"v": Vector2(cos(a), sin(a)) * float(p.get("speed", 150.0)) * rng.randf_range(0.5, 1.0),
			"l": life * rng.randf_range(0.6, 1.0)})
	spawn(front, life, func(ci: Fx, t: float) -> void:
		for q in parts:
			if t >= q.l:
				continue
			var head: Vector2 = pos + q.v * t + Vector2(0, 0.5 * g * t * t)
			var tail: Vector2 = pos + q.v * maxf(0.0, t - 0.035) + Vector2(0, 0.5 * g * maxf(0.0, t - 0.035) ** 2)
			line(ci, tail, head, ramp_at(ramp, t / q.l)), p.get("glow", true))


## A four-point star flash: a muzzle flash or the instant of contact.
func star(pos: Vector2, p: Dictionary) -> void:
	var r: float = p.get("r", 6.0)
	var life: float = p.get("life", 0.13)
	var ramp: Array = RAMPS[p.get("ramp", "spark")]
	spawn(front, life, func(ci: Fx, t: float) -> void:
		var u := t / life
		var arm := r * (1.0 - u * 0.7)
		var col := ramp_at(ramp, u)
		line(ci, pos - Vector2(arm, 0), pos + Vector2(arm, 0), col)
		line(ci, pos - Vector2(0, arm * 0.7), pos + Vector2(0, arm * 0.7), col)
		disc(ci, pos, maxf(0.0, r * 0.35 * (1.0 - u)), ramp[0]))


## A disc that bursts open and leaves a thinning ring: the core of most impacts.
func burst(pos: Vector2, p: Dictionary) -> void:
	var r: float = p.get("r", 8.0)
	var life: float = p.get("life", 0.2)
	var ramp: Array = RAMPS[p.get("ramp", "spark")]
	var squash: float = p.get("squash", 1.0)
	spawn(front, life, func(ci: Fx, t: float) -> void:
		var u := t / life
		if u < 0.34:
			disc(ci, pos, r * (0.45 + u * 1.6), ramp_at(ramp, u), squash)
			disc(ci, pos, r * 0.3, ramp[0], squash)
		else:
			ring(ci, pos, r * (0.9 + u * 0.4), ramp_at(ramp, u), squash))


## A fireball of a few overlapping puffs that burn white to orange to red, then go to dark smoke and rise.
func explosion(pos: Vector2, p: Dictionary) -> void:
	var r: float = p.get("r", 10.0)
	var life: float = p.get("life", 0.6)
	var fire: Array = RAMPS[p.get("ramp", "fire")]
	var puffs := []
	for i in int(p.get("puffs", 3 + int(r / 4.0))):
		var a := rng.randf() * TAU
		var d := rng.randf() * r * 0.55
		puffs.append({"o": Vector2(cos(a), sin(a) * 0.8) * d, "d": rng.randf() * life * 0.3,
			"r": r * rng.randf_range(0.45, 0.8), "l": life * rng.randf_range(0.55, 0.75)})
	spawn(front, life, func(ci: Fx, t: float) -> void:
		if t < STEP * 2:
			disc(ci, pos, r * 0.7, fire[0])
		for q in puffs:
			var a: float = (t - q.d) / q.l
			if a < 0.0 or a >= 1.0:
				continue
			var rr: float = q.r * (a / 0.3 if a < 0.3 else 1.0 - (a - 0.3) * 0.5)
			var c: Vector2 = pos + q.o + Vector2(0, -a * r * 0.5)
			disc(ci, c, rr, ramp_at(fire, a))
			if a < 0.5:
				disc(ci, c + Vector2(-rr * 0.25, -rr * 0.25), rr * 0.45, ramp_at(fire, a * 0.5)))
	if p.get("smoke", true):
		after(life * 0.45, func() -> void: smoke(pos + Vector2(0, -r * 0.3), {"count": 3, "r": r * 0.35, "life": 0.7, "rise": r * 1.4}))


## Puffs of smoke that swell, rise and thin out.
func smoke(pos: Vector2, p: Dictionary) -> void:
	var life: float = p.get("life", 0.8)
	var ramp: Array = RAMPS[p.get("ramp", "smoke")]
	var r: float = p.get("r", 4.0)
	var rise: float = p.get("rise", 16.0)
	var puffs := []
	for i in int(p.get("count", 4)):
		puffs.append({"x": rng.randf_range(-r, r), "d": rng.randf() * life * 0.3, "l": life * rng.randf_range(0.6, 0.9),
			"drift": rng.randf_range(-4.0, 4.0)})
	spawn(front if p.get("in_front", true) else back, life, func(ci: Fx, t: float) -> void:
		for q in puffs:
			var a: float = (t - q.d) / q.l
			if a < 0.0 or a >= 1.0:
				continue
			var col := ramp_at(ramp, a)
			col.a = 1.0 if a < 0.6 else 0.6
			disc(ci, pos + Vector2(q.x + q.drift * a, -rise * a), r * (0.6 + a * 0.8), col))


## Ground dust kicked out sideways from a foot, a landing or a blow, low and short.
func dust(pos: Vector2, dir: float, p: Dictionary) -> void:
	var life: float = p.get("life", 0.5)
	var ramp: Array = RAMPS[p.get("ramp", "dust")]
	var both: bool = p.get("both", true)
	var puffs := []
	for i in int(p.get("count", 5)):
		var side := (1.0 if i % 2 == 0 else -1.0) if both else dir
		puffs.append({"x": rng.randf_range(-3.0, 3.0), "vx": side * rng.randf_range(12.0, float(p.get("speed", 40.0))),
			"vy": -rng.randf_range(3.0, 12.0), "r": rng.randf_range(1.5, float(p.get("r", 3.5))), "d": rng.randf() * 0.06})
	spawn(front, life, func(ci: Fx, t: float) -> void:
		for q in puffs:
			var tt: float = t - q.d
			if tt < 0.0:
				continue
			var a: float = tt / (life - q.d)
			var slow := tt * (1.0 - a * 0.5)   # drag: they slow as they spread
			var col := ramp_at(ramp, a * 0.9 + 0.1)
			col.a = 1.0 if a < 0.65 else 0.55
			disc(ci, pos + Vector2(q.x + q.vx * slow, q.vy * slow), q.r * (0.7 + a * 0.6), col))


## Chunks of plate and rock thrown up that fall and bounce once on the ground.
func debris(pos: Vector2, dir: float, p: Dictionary) -> void:
	var life: float = p.get("life", 0.7)
	var ramp: Array = RAMPS[p.get("ramp", "steel")]
	var ground: float = p.get("ground", pos.y + 6.0)
	var g := 300.0
	var parts := []
	for i in int(p.get("count", 6)):
		var a := deg_to_rad(-90.0 + rng.randf_range(-60.0, 60.0) + float(p.get("lean", 25.0)) * dir)
		parts.append({"v": Vector2(cos(a), sin(a)) * float(p.get("speed", 90.0)) * rng.randf_range(0.5, 1.0),
			"s": Vector2(rng.randi_range(1, 3), rng.randi_range(1, 2)), "c": rng.randi_range(0, ramp.size() - 2)})
	spawn(front, life, func(ci: Fx, t: float) -> void:
		for q in parts:
			var at: Vector2 = pos + q.v * t + Vector2(0, 0.5 * g * t * t)
			if at.y > ground:   # one bounce, losing most of its speed
				at.y = ground - (at.y - ground) * 0.25
			var s: Vector2 = q.s if int(t / STEP) % 4 < 2 else Vector2(q.s.y, q.s.x)   # tumbling
			ci.draw_rect(Rect2(at.round(), s), ramp[q.c + (1 if t > life * 0.6 else 0)]))


## Water droplets flung out in a fan, falling.
func spray(pos: Vector2, dir: float, p: Dictionary) -> void:
	var life: float = p.get("life", 0.45)
	var ramp: Array = RAMPS[p.get("ramp", "water")]
	var spread := deg_to_rad(p.get("spread", 60.0))
	var base := deg_to_rad(p.get("angle", -30.0 if dir > 0 else -150.0))
	var g: float = p.get("gravity", 260.0)
	var parts := []
	for i in int(p.get("count", 10)):
		var a := base + rng.randf_range(-spread, spread)
		parts.append({"v": Vector2(cos(a), sin(a)) * float(p.get("speed", 90.0)) * rng.randf_range(0.4, 1.0), "s": 1 + int(rng.randf() < 0.3)})
	spawn(front, life, func(ci: Fx, t: float) -> void:
		for q in parts:
			dot(ci, pos + q.v * t + Vector2(0, 0.5 * g * t * t), ramp_at(ramp, t / life), q.s))


## Rings that open out one after another: a kinetic blast, a ground ring, a shock.
func rings(pos: Vector2, dir: float, p: Dictionary) -> void:
	var life: float = p.get("life", 0.4)
	var n := int(p.get("count", 2))
	var gap: float = p.get("gap", 0.07)
	var r0: float = p.get("r0", 3.0)
	var r1: float = p.get("r1", 18.0)
	var squash: float = p.get("squash", 1.0)
	var drift: float = p.get("drift", 0.0)
	var ramp: Array = RAMPS[p.get("ramp", "steel")]
	var each := life - gap * (n - 1)
	spawn(front, life, func(ci: Fx, t: float) -> void:
		for i in n:
			var a := (t - gap * i) / each
			if a < 0.0 or a >= 1.0:
				continue
			ring(ci, pos + Vector2(drift * a * dir, 0), lerpf(r0, r1, a), ramp_at(ramp, a), squash, 2 if a < 0.3 else 1), p.get("glow", false))


## A blade's arc sweeping through, thick at its head and thin at its tail (angles in degrees, 0 = toward the foe).
func slash(pos: Vector2, dir: float, p: Dictionary) -> void:
	var life: float = p.get("life", 0.2)
	var r: float = p.get("r", 14.0)
	var squash: float = p.get("squash", 0.6)
	var w := int(p.get("w", 3))
	var ramp: Array = RAMPS[p.get("ramp", "steel")]
	var a0 := deg_to_rad(p.get("a0", -70.0))
	var a1 := deg_to_rad(p.get("a1", 70.0))
	if dir < 0:   # mirror for a machine facing left
		a0 = PI - a0
		a1 = PI - a1
	spawn(front, life, func(ci: Fx, t: float) -> void:
		var u := t / life
		var head := clampf(u / 0.45, 0.0, 1.0)
		var tail := clampf((u - 0.3) / 0.7, 0.0, 1.0)
		var n := 10
		for i in n + 1:
			var f := lerpf(tail, head, float(i) / n)
			var a := lerpf(a0, a1, f)
			var thick := maxi(1, roundi(w * (float(i) / n)))
			var c: Color = ramp[0] if i == n else ramp_at(ramp, 0.3 + 0.6 * (1.0 - float(i) / n))
			ci.draw_rect(Rect2(Vector2(pos.x + cos(a) * r, pos.y + sin(a) * r * squash).round() - Vector2(thick / 2, thick / 2), Vector2(thick, thick)), c))


## A straight cut across the target, drawn in two steps and then thinning: a pass-through slash.
func streak(pos: Vector2, dir: float, p: Dictionary) -> void:
	var life: float = p.get("life", 0.2)
	var length: float = p.get("length", 36.0)
	var tilt: float = p.get("tilt", -0.25)
	var ramp: Array = RAMPS[p.get("ramp", "steel")]
	var a := pos - Vector2(length / 2 * dir, -tilt * length / 2)
	var b := pos + Vector2(length / 2 * dir, -tilt * length / 2)
	spawn(front, life, func(ci: Fx, t: float) -> void:
		var u := t / life
		var head := a.lerp(b, clampf(u / 0.3, 0.0, 1.0))
		var w := 3 if u < 0.4 else (2 if u < 0.7 else 1)
		line(ci, a.lerp(b, clampf((u - 0.4) / 0.6, 0.0, 1.0)), head, ramp_at(ramp, u * 0.8 + 0.1), w)
		if u < 0.4:
			line(ci, a, head, ramp[0], 1))


## A booster jet: a flickering tongue of fire pointing at `angle` degrees (90 = straight down).
func flame(pos: Vector2, dir: float, p: Dictionary) -> void:
	var life: float = p.get("life", 0.3)
	var length: float = p.get("length", 7.0)
	var ramp: Array = RAMPS[p.get("ramp", "fire")]
	var a := deg_to_rad(p.get("angle", 110.0))
	if dir < 0:
		a = PI - a
	var v := Vector2(cos(a), sin(a))
	var seed_value := rng.randi()
	spawn(front, life, func(ci: Fx, t: float) -> void:
		var flick := RandomNumberGenerator.new()
		flick.seed = seed_value + int(t / STEP)
		var l := length * flick.randf_range(0.6, 1.0) * (1.0 if t < life * 0.7 else 0.6)
		for i in int(l):
			var f := float(i) / l
			var w := maxi(1, roundi(3.0 * (1.0 - f)))
			dot(ci, pos + v * i, ramp_at(ramp, f * 0.9), w))


## Energy drawn in to a point: a charge-up (Zoids Legacy charges its big shots with particles drawn inward).
func charge_in(pos: Vector2, p: Dictionary) -> void:
	var life: float = p.get("life", 0.55)
	var r: float = p.get("r", 24.0)
	var ramp: Array = RAMPS[p.get("ramp", "cyan")]
	var parts := []
	for i in int(p.get("count", 12)):
		var a := rng.randf() * TAU
		parts.append({"d": Vector2(cos(a), sin(a) * 0.8) * r * rng.randf_range(0.7, 1.2), "s": rng.randf() * 0.3})
	spawn(front, life, func(ci: Fx, t: float) -> void:
		var u := t / life
		for q in parts:
			var a := clampf((u - q.s) / (1.0 - q.s), 0.0, 1.0)
			if a <= 0.0 or a >= 1.0:
				continue
			var head: Vector2 = pos + q.d * (1.0 - a * a)
			line(ci, head, pos + q.d * (1.0 - minf(1.0, a * a + 0.15)), ramp_at(ramp, 1.0 - a))
			dot(ci, head, ramp[1], 2)
		if u > 0.25:
			ring(ci, pos, r * (1.0 - u) * 0.8, ramp_at(ramp, 1.0 - u), 0.8)
		if u > 0.8:
			disc(ci, pos, 2.0, ramp[0]), true)


## Rising plus-signs: a repair or a restored gauge.
func sparkle(pos: Vector2, p: Dictionary) -> void:
	var life: float = p.get("life", 0.75)
	var ramp: Array = RAMPS[p.get("ramp", "heal")]
	var spread: float = p.get("spread", 16.0)
	var parts := []
	for i in int(p.get("count", 7)):
		parts.append({"o": Vector2(rng.randf_range(-spread, spread), rng.randf_range(-spread * 0.6, spread * 0.4)), "d": rng.randf() * life * 0.4})
	spawn(front, life, func(ci: Fx, t: float) -> void:
		for q in parts:
			var a: float = (t - q.d) / (life - q.d)
			if a < 0.0 or a >= 1.0:
				continue
			var c: Vector2 = pos + q.o + Vector2(0, -18.0 * a)
			var col := ramp_at(ramp, a)
			line(ci, c - Vector2(1, 0), c + Vector2(1, 0), col)
			line(ci, c - Vector2(0, 1), c + Vector2(0, 1), col))


## Horizontal speed streaks passing behind a machine moving at full speed.
func speed_lines(pos: Vector2, dir: float, p: Dictionary) -> void:
	var life: float = p.get("life", 0.3)
	var h: float = p.get("h", 20.0)
	var lines := []
	for i in int(p.get("count", 7)):
		lines.append({"y": rng.randf_range(-h, h), "x": rng.randf_range(-30.0, 10.0), "l": rng.randf_range(10.0, 26.0)})
	spawn(back, life, func(ci: Fx, t: float) -> void:
		var u := t / life
		for q in lines:
			var x0: float = pos.x + (q.x - u * 70.0) * dir
			var col := Color(1, 1, 1, 0.75 if u < 0.6 else 0.4)
			line(ci, Vector2(x0, pos.y + q.y), Vector2(x0 - q.l * dir, pos.y + q.y), col))


## Something thrown or fired from `pos` to `to`: a shell, a scale plate, a ballast block, a missile with its smoke.
## p.time: the flight in seconds; p.arc: how high it lobs.
func projectile(pos: Vector2, to: Vector2, p: Dictionary) -> void:
	var life: float = p.get("time", 0.3)
	var arc: float = p.get("arc", 0.0)
	var style: String = p.get("style", "pellet")
	var ramp: Array = RAMPS[p.get("ramp", "spark")]
	var at := func(u: float) -> Vector2: return pos.lerp(to, u) + Vector2(0, -arc * 4.0 * u * (1.0 - u))
	if style == "ball":   # a cannonball: a few puffs of powder smoke left along its path
		for i in 3:
			var u := (i + 0.5) / 5.0
			after(life * u, func() -> void: smoke(at.call(u), {"count": 1, "r": 2.5, "life": 0.4, "rise": 4.0, "in_front": false}))
	if style == "missile":   # its smoke trail stays behind it
		for i in 6:
			var u := (i + 0.5) / 6.0
			after(life * u, func() -> void: smoke(at.call(u), {"count": 1, "r": 2.0, "life": 0.45, "rise": 5.0, "in_front": false}))
	spawn(front, life, func(ci: Fx, t: float) -> void:
		_draw_projectile(ci, style, ramp, at, t / life, int(t / STEP)))


func _draw_projectile(ci: CanvasItem, style: String, ramp: Array, at: Callable, u: float, k: int) -> void:
	var c: Vector2 = at.call(u)
	if style == "pellet":
		line(ci, at.call(maxf(0.0, u - 0.12)), c, ramp[2])
		dot(ci, c, ramp[0], 2)
	elif style == "orb":
		disc(ci, c, 3.0, ramp[2 + k % 2])
		disc(ci, c, 1.0, ramp[0])
	elif style == "plate":   # tumbling end over end
		var s := Vector2(4, 2) if k % 2 == 0 else Vector2(2, 3)
		ci.draw_rect(Rect2(c.round() - (s / 2).floor(), s), ramp[2])
		dot(ci, c, ramp[0])
	elif style == "block":   # a heavy slab turning over: lit top edge, dark bottom edge
		var s := Vector2(8, 6) if k % 4 < 2 else Vector2(6, 8)
		ci.draw_rect(Rect2(c.round() - s / 2, s), ramp[2])
		ci.draw_rect(Rect2(c.round() - s / 2, Vector2(s.x, 1)), ramp[0])
		ci.draw_rect(Rect2(c.round() - s / 2 + Vector2(0, s.y - 1), Vector2(s.x, 1)), ramp[3])
	elif style == "ball":   # dark iron, lit on its upper left
		disc(ci, c, 3.5, ramp[3])
		dot(ci, c + Vector2(-1, -1), ramp[1], 2)
	elif style == "missile":
		var back_pt: Vector2 = at.call(maxf(0.0, u - 0.06))
		line(ci, back_pt, c, ramp[1], 2)
		dot(ci, back_pt, RAMPS.fire[k % 3], 2)


## A beam that reaches its target in `grow` seconds, holds with its colours cycling, then narrows away.
## p.wave: a sideways ripple (a water jet); p.width: its thickness; p.pair: two beams this far apart (twin jets).
func beam(pos: Vector2, to: Vector2, p: Dictionary) -> void:
	var life: float = p.get("life", 0.4)
	var grow: float = p.get("grow", 0.06)
	var width := int(p.get("width", 3))
	var wave_amp: float = p.get("wave", 0.0)
	var ramp: Array = RAMPS[p.get("ramp", "cyan")]
	var d := to - pos
	var n := d.normalized().orthogonal()
	var pair: float = p.get("pair", 0.0)
	if pair > 0.0:
		var one := p.duplicate()
		one.erase("pair")
		one.dim = false
		beam(pos + n * pair / 2.0, to + n * pair / 2.0, one)
		beam(pos - n * pair / 2.0, to - n * pair / 2.0, one)
		return
	spawn(front, life, func(ci: Fx, t: float) -> void:
		var tip := pos.lerp(to, clampf(t / grow, 0.0, 1.0))
		var fade := clampf((t - life * 0.65) / (life * 0.35), 0.0, 1.0)
		var w := maxi(1, roundi(width * (1.0 - fade)))
		var k := int(t / STEP)
		var outer: Color = ramp[2 + k % 2]   # the rim cycles between two colours, like a palette-cycled GBA beam
		var inner: Color = ramp[k % 2]
		var len_px := maxi(1, int(pos.distance_to(tip)))
		for i in len_px + 1:
			var f := float(i) / len_px
			var c := pos.lerp(tip, f) + n * (sin(f * 18.0 + t * 40.0) * wave_amp)
			ci.draw_rect(Rect2(c.round() - Vector2(w / 2, w / 2), Vector2(w, w)), outer)
		for i in len_px + 1:   # the bright core over the rim
			var f := float(i) / len_px
			var c := pos.lerp(tip, f) + n * (sin(f * 18.0 + t * 40.0) * wave_amp)
			var wi := maxi(1, w / 2)
			ci.draw_rect(Rect2(c.round() - Vector2(wi / 2, wi / 2), Vector2(wi, wi)), inner)
		disc(ci, pos, w * 0.8 + 1.0, ramp[1])
		disc(ci, tip, w * 0.9 + (1.0 if k % 2 == 0 else 0.0), ramp[0]), p.get("glow", true))
	if p.get("dim", true):
		dim(0.45, life)


## A shockwave running along the ground from `pos` to `to`: the ground heaves up in a moving ridge of thrown earth and
## rock, leaves a dark crack, and throws dust as it goes. p.time: how long it takes to arrive.
func wave(pos: Vector2, to: Vector2, p: Dictionary) -> void:
	var travel: float = p.get("time", 0.35)
	var life := travel + 0.4
	var dust_ramp: Array = RAMPS.dust
	var rock: Array = RAMPS.steel
	var jag := []
	for i in 64:
		jag.append(rng.randi_range(-1, 1))
	var heights := []
	for i in 6:
		heights.append(rng.randi_range(4, 11))
	for i in 7:   # dust thrown up along the way
		var u := (i + 1) / 8.0
		after(travel * u, func() -> void: dust(pos.lerp(to, u), 1.0, {"count": 4, "r": 4.0, "life": 0.45, "speed": 30.0}))
	spawn(front, life, func(ci: Fx, t: float) -> void:
		var u := clampf(t / travel, 0.0, 1.0)
		var front_pt := pos.lerp(to, u)
		var steps := maxi(1, int(pos.distance_to(front_pt) / 3.0))
		var crack: Color = Color("2a2420") if t < travel + 0.2 else Color("4a4036")
		for i in steps:   # the crack behind the ridge
			var a := pos.lerp(front_pt, float(i) / steps) + Vector2(0, jag[i % 64])
			var b := pos.lerp(front_pt, float(i + 1) / steps) + Vector2(0, jag[(i + 1) % 64])
			line(ci, a, b, crack, 2)
		if u < 1.0:   # the ridge: slabs of earth and rock thrown up at the front, flickering as it rolls
			var k := int(t / STEP)
			for j in 6:
				var hgt: int = heights[(j + k) % 6]
				var col: Color = dust_ramp[1 + (j + k) % 3] if j % 2 == 0 else rock[1 + (j + k) % 2]
				ci.draw_rect(Rect2((front_pt + Vector2(j * 3 - 9, -hgt)).round(), Vector2(3, hgt)), col)
				ci.draw_rect(Rect2((front_pt + Vector2(j * 3 - 9, -hgt)).round(), Vector2(3, 1)), dust_ramp[0]))


## Sound waves: arcs that leave the mouth and roll toward the target, opening as they go (a concussive howl).
func sound_waves(pos: Vector2, to: Vector2, dir: float, p: Dictionary) -> void:
	var travel: float = p.get("time", 0.3)
	var n := int(p.get("count", 4))
	var gap: float = p.get("gap", 0.06)
	var ramp: Array = RAMPS[p.get("ramp", "red")]
	var life := travel + gap * (n - 1)
	var facing := 0.0 if dir > 0 else PI
	spawn(front, life, func(ci: Fx, t: float) -> void:
		for i in n:
			var a := (t - gap * i) / travel
			if a < 0.0 or a >= 1.0:
				continue
			var c := pos.lerp(to, a)
			var r := lerpf(float(p.get("r0", 4.0)), float(p.get("r1", 14.0)), a)
			ring(ci, c - Vector2(r * 0.6 * dir, 0), r, ramp_at(ramp, a * 0.7), 1.0, 2 if a < 0.5 else 1, facing - 0.9, facing + 0.9))


# --- screen-level beats and the machines' reactions ------------------------------------------------------------------

## Shakes the stage (screen pixels), side to side, dying away over `life`.
func shake(amp: float, life := 0.25) -> void:
	if amp <= 0.0:
		return
	if shake_left <= 0.0 or amp >= shake_amp * maxf(0.0, shake_left / maxf(shake_life, 0.001)):
		shake_amp = amp
		shake_life = life
		shake_left = life


## Flashes the whole stage a colour, in two steps down.
func flash_stage(col: Color, strength := 0.7) -> void:
	flash_rect.color = Color(col, strength)
	after(STEP * 2, func() -> void: flash_rect.color = Color(col, strength * 0.45))
	after(STEP * 4, func() -> void: flash_rect.color = Color(col, 0.0))


## Blinks a machine toward `col` in steps: `pattern` is the strength per STEP.
func flash(node: Node2D, col: Color, pattern: Array) -> void:
	var m := node.material as ShaderMaterial
	if m == null:
		return
	m.set_shader_parameter("flash_color", col)
	for i in pattern.size():
		var v: float = pattern[i]
		after(STEP * i, func() -> void:
			if is_instance_valid(node):
				m.set_shader_parameter("flash", v))
	after(STEP * pattern.size(), func() -> void:
		if is_instance_valid(node):
			m.set_shader_parameter("flash", 0.0))


## The hit freeze: both machines hold their frame for an instant at the moment of contact.
func hitstop(nodes: Array, life: float) -> void:
	for node: Node2D in nodes:
		var a := node.get_node_or_null("anim") as AnimatedSprite2D
		if a == null:
			continue
		a.speed_scale = 0.0
		after(life, func() -> void:
			if is_instance_valid(a):
				a.speed_scale = 1.0)


## Knocked back `px` away from the blow (dir: the blow's direction), then back to where it stood.
func knock(node: Node2D, dir: float, px: float) -> void:
	var home := node.position.x
	var t := node.create_tween()
	t.tween_property(node, "position:x", home + px * dir, 0.06)
	t.tween_property(node, "position:x", home, 0.22).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


## A dodge: a sway away from the blow and back on a cosine, about 0.6 s (Zoids Legacy's miss sway runs 37 frames).
func dodge(node: Node2D, dir: float) -> void:
	var home := node.position.x
	var t := node.create_tween()
	t.tween_method(func(f: float) -> void:
		if is_instance_valid(node):
			node.position.x = roundf(home + 12.0 * dir * 0.5 * (1.0 - cos(f * TAU))), 0.0, 1.0, 0.6)


## The struck machine's own shake (the screen stays put): its art jitters side to side, each offset held a step,
## shrinking over `life` (Zoids Legacy shakes only the target's layer, 17 frames).
func jolt(node: Node2D, amp: float, life := 0.28) -> void:
	var art: CanvasItem = null
	for c in node.get_children():
		if c is Node2D:
			art = c
			break
	if art == null:
		return
	var n := int(life / STEP)
	for i in n:
		var v := roundf(amp * (1.0 - float(i) / n)) * (1.0 if i % 2 == 0 else -1.0)
		after(STEP * i, func() -> void:
			if is_instance_valid(art):
				art.position.x = v)
	after(STEP * n, func() -> void:
		if is_instance_valid(art):
			art.position.x = 0.0)


## Darkens the background (not the machines) while something bright plays, then lifts it (the Pokemon GBA games darken
## the background before a beam).
func dim(amount: float, life: float) -> void:
	if background == null:
		return
	var steps := 3
	for i in steps:
		var v := 1.0 - amount * float(i + 1) / steps
		after(STEP * i, func() -> void: background.modulate = Color(v, v, v))
	for i in steps:
		var v := 1.0 - amount * (1.0 - float(i + 1) / steps)
		after(life + STEP * i, func() -> void: background.modulate = Color(v, v, v))


## Faded copies of a machine's current frame trailing behind it: speed. They add light to what is behind them, as
## Zoids Legacy's after-images do (copies drawn over at full opacity read as a muddy smear).
func afterimage(node: Node2D, dir: float, p: Dictionary) -> void:
	var a := node.get_node_or_null("anim") as AnimatedSprite2D
	var tex: Texture2D = a.sprite_frames.get_frame_texture(a.animation, a.frame) if a != null else frame_tex(node, "", -1)
	if tex == null:
		return
	var life: float = p.get("life", 0.25)
	var col: Color = Color(p.get("color", "5fe1d0")).lerp(Color.WHITE, 0.3)
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	for i in int(p.get("count", 3)):
		var s := Sprite2D.new()
		s.texture = tex
		s.centered = false
		s.scale = node.scale
		s.material = add
		s.position = (node.position - Vector2(float(p.get("gap", 9.0)) * (i + 1) * dir, 0)).round()
		s.modulate = Color(col, 0.4 - 0.1 * i)
		back.add_child(s)
		var tw := s.create_tween()
		tw.tween_property(s, "modulate:a", 0.0, life).set_delay(STEP * i)
		tw.tween_callback(s.queue_free)


# --- whole sequences ---------------------------------------------------------------------------------------------------

## One attack's effects and movement, from the recipe (scripts/battle/vfx_recipes.gd). `times` is [strike, total]
## from MachineAnim.clip_times; `home` is where the attacker stands between moves and `base_y` the row it plays this
## clip at (lower than home when the clip is too tall for its slot), `max_y` the lowest it may stand (the player's
## row: an enemy never steps over the panel). A melee recipe ("advance") carries the attacker
## across: Zoids Legacy moves the acting unit out before it strikes, and with the zoomed-out field the two machines
## stand too far apart for a blow to land in place. It leaves at frame "go", arrives as the strike frame starts with its
## frontmost point (fist, bill, feet) just inside the target's edge, holds, and goes back from frame "back".
## Returns the seconds from now to the impact, when the battle shows the damage.
func play_attack(actor: Node2D, target: Node2D, clip: String, times: Array, recipe: Dictionary, hit: bool, home: Vector2, base_y: float, max_y: float) -> float:
	var dir := signf(actor.scale.x)
	var starts := _frame_starts(actor, clip)
	var ctx := {}
	var strike_k := _strike_frame(actor, clip)
	var freeze: float = recipe.get("hitstop", 0.06) if hit else 0.0   # the hit freeze holds the clip back too
	var at_time := func(cue: Dictionary) -> float:
		if cue.has("frame") and int(cue.frame) < starts.size():
			var late := freeze if strike_k >= 0 and int(cue.frame) > strike_k else 0.0
			return starts[int(cue.frame)] + float(cue.get("t", 0.0)) + late
		return float(times[0]) + float(cue.get("t", 0.0))
	last = ctx   # for tools/debug/vfx_check.gd
	var tw := actor.create_tween()
	if recipe.get("advance", false) and strike_k >= 0:
		var tip := frontmost(frame_tex(actor, clip, strike_k), recipe.get("lead", [0.0, 0.8])) if frame_tex(actor, clip, strike_k) != null else Vector2(float(actor.get_meta("width", 64)), float(actor.get_meta("height", 48)) * 0.4)
		var dy := (target.position.y + float(target.get_meta("feet_y")) - (base_y + float(actor.get_meta("feet_y")))) * float(recipe.get("depth", 0.6))
		# the blow lands on the body: a fist that would pass over a short target (or under a tall one) comes down (up)
		var body := rect_of(target, frame_tex(target, "", -1))
		var lo := target.position.y + body.position.y + body.size.y * 0.15
		var hi := target.position.y + body.end.y - body.size.y * 0.2
		var tip_y := base_y + tip.y + dy
		dy += maxf(0.0, lo - tip_y) - maxf(0.0, tip_y - hi)
		# stepping down toward the near lane stops at the player's row (`max_y`), above the panel
		dy = minf(base_y + dy, maxf(base_y, max_y)) - base_y
		# stepping up toward the far lane stops where the clip's art would leave the top of the screen
		dy = maxf(base_y + dy, minf(base_y, -float(Anim.clip_top(actor, clip)))) - base_y
		var tip_field := Vector2(home.x + tip.x * dir, base_y + tip.y + dy)
		var edge := _edge_at(target, tip_field.y)
		var dx := edge - tip_field.x + float(recipe.get("overlap", 3.0)) * dir
		if dx * dir < 0.0:
			dx = 0.0
		# where a big machine cannot reach down to a small one without stepping over the panel, the blow lands on
		# its top edge rather than in the air above it
		var y_lo := target.position.y + body.position.y + 2.0
		ctx.contact = Vector2(tip_field.x + dx, clampf(tip_field.y, y_lo, maxf(y_lo, target.position.y + body.end.y - 2.0)))
		var go: float = at_time.call({"frame": recipe.get("go", 2)})
		var arrive: float = starts[mini(strike_k, starts.size() - 1)] - 0.02
		var back: float = at_time.call({"frame": recipe.get("back", 7)})   # includes the freeze
		var dest := Vector2(roundf(home.x + dx), roundf(base_y + dy))
		var order := actor.get_index()
		field.move_child(actor, front.get_index() - 1)   # the one attacking draws in front of the other machine
		if base_y > home.y:   # too tall for its slot: down first, before the wind-up's tall frames
			tw.tween_property(actor, "position:y", base_y, 0.12)
			go = maxf(go, 0.12)
			tw.tween_interval(go - 0.12)
		else:
			tw.tween_interval(go)
		tw.tween_property(actor, "position", dest, maxf(0.05, arrive - go)).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		tw.tween_interval(maxf(0.0, back - arrive))
		# back across at the clip's row; up to the home row only once the clip has ended, as a plain step-down does
		tw.tween_property(actor, "position", Vector2(home.x, base_y), maxf(0.15, float(times[1]) + freeze - back)).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		if base_y > home.y:
			tw.tween_property(actor, "position:y", home.y, 0.2)
		tw.tween_callback(func() -> void: field.move_child(actor, order))
	elif base_y > home.y:   # a clip too tall for the slot plays a little lower, then it steps back up
		tw.tween_property(actor, "position:y", base_y, 0.12)
		tw.tween_interval(maxf(0.0, float(times[1]) + (float(recipe.get("hitstop", 0.06)) if hit else 0.0) - 0.12))
		tw.tween_property(actor, "position:y", home.y, 0.2)
	else:
		tw.kill()
	for cue: Dictionary in recipe.get("cues", []):
		after(at_time.call(cue), func() -> void: _cue(cue, actor, target, clip, dir, ctx))
	var impact: float = times[0]
	var shot: Dictionary = recipe.get("shot", {})
	if not shot.is_empty():
		var fire_t: float = at_time.call(shot)
		impact = fire_t + float(shot.get("time", 0.0)) + float(shot.get("grow", 0.0))
		after(fire_t, func() -> void: _fire(shot, actor, target, clip, dir, hit, ctx))
	after(impact, func() -> void: _impact(recipe, actor, target, clip, dir, hit, ctx))
	ctx.impact = impact
	return impact


func _strike_frame(node: Node2D, clip: String) -> int:
	var a := node.get_node_or_null("anim") as AnimatedSprite2D
	if a == null or not a.sprite_frames.has_animation(clip):
		return -1
	return int(a.get_meta("clips")[clip].get("strike", -1))


# the target's front edge (field x) at field row `y`, held inside its art
func _edge_at(target: Node2D, y: float) -> float:
	var tex := frame_tex(target, "", -1)
	var r := rect_of(target, tex)
	var row := clampi(roundi(y - target.position.y), r.position.y + 2, maxi(r.position.y + 2, r.end.y - 3))
	return target.position.x + _edge(tex, r, row, true) * target.scale.x


func _frame_starts(node: Node2D, clip: String) -> Array:
	var a := node.get_node_or_null("anim") as AnimatedSprite2D
	var out := []
	if a == null or not a.sprite_frames.has_animation(clip):
		return out
	var t := 0.0
	for ms in a.get_meta("clips")[clip].ms:
		out.append(t)
		t += float(ms) / 1000.0
	return out


func _cue(cue: Dictionary, actor: Node2D, target: Node2D, clip: String, dir: float, ctx := {}) -> void:
	if not is_instance_valid(actor) or not is_instance_valid(target):
		return
	match cue.fx:
		"afterimage":
			afterimage(actor, dir, cue)
		"shake":
			shake(cue.get("amp", 2.0), cue.get("life", 0.2))
		"flash_stage":
			flash_stage(Color(cue.get("color", "ffffff")), cue.get("strength", 0.6))
		_:
			var pos := anchor(cue.get("at", "actor_center"), actor, target, clip, ctx)
			pos += Vector2(float(cue.get("dx", 0)) * dir, float(cue.get("dy", 0)))   # dx: toward the foe
			var to := anchor(cue.get("to", "target"), actor, target, clip, ctx)
			play(cue.fx, pos, to, dir, cue)


## The shot leaves the muzzle: its flash, then the projectile, beam or wave (a miss flies past, behind the target).
func _fire(shot: Dictionary, actor: Node2D, target: Node2D, clip: String, dir: float, hit: bool, ctx := {}) -> void:
	if not is_instance_valid(actor) or not is_instance_valid(target):
		return
	var from := anchor(shot.get("from", "actor_center"), actor, target, clip)
	var to := anchor(shot.get("to", "target"), actor, target, clip)
	if not hit:   # it flies past and spends itself on the ground behind
		to = anchor("target_feet", actor, target, clip) + Vector2(28.0 * dir, -2.0)
	ctx.shot_to = to
	var muzzle: Dictionary = shot.get("muzzle", {})
	for b in int(shot.get("bursts", 1)):
		after(float(shot.get("gap", 0.07)) * b, func() -> void:
			if not muzzle.is_empty():
				play(muzzle.get("fx", "star"), from, to, dir, muzzle)
			var n := int(shot.get("count", 1))
			for i in n:
				var spread: float = shot.get("spread", 0.0)
				var off := Vector2(rng.randf_range(-spread, spread) * 0.5, rng.randf_range(-spread, spread)) if n > 1 else Vector2.ZERO
				var lag := rng.randf_range(0.0, float(shot.get("stagger", 0.0)))
				var land := to + off
				after(lag, func() -> void:
					play(shot.fx, from, land, dir, shot)
					if shot.has("land"):   # each pellet or plate pops where it lands
						after(float(shot.get("time", 0.0)), func() -> void: play(shot.land.get("fx", "star"), land, land, dir, shot.land))))


## The moment of contact: the impact pieces, the white blink, the hit freeze, the shake, the knock back. A miss:
## the target dodges and the shot or blow spends itself on the ground.
func _impact(recipe: Dictionary, actor: Node2D, target: Node2D, clip: String, dir: float, hit: bool, ctx := {}) -> void:
	if not is_instance_valid(actor) or not is_instance_valid(target):
		return
	if not hit:
		dodge(target, dir)
		var landed: Vector2 = ctx.get("shot_to", anchor("target_feet", actor, target, clip) + Vector2(-10.0 * dir, 0.0))
		for cue: Dictionary in recipe.get("miss", [{"fx": "dust", "count": 5}]):
			play(cue.fx, landed, landed, dir, cue)
		return
	for cue: Dictionary in recipe.get("impact", []):
		var go := func() -> void:
			if is_instance_valid(target):
				_cue(cue, actor, target, clip, dir, ctx)
		if cue.has("t"):
			after(float(cue.t), go)
		else:
			go.call()
	var freeze: float = recipe.get("hitstop", 0.06)
	# the burst reads first on the target as it is, then it blinks toward white (a full white silhouette at the
	# moment of contact hid the impact drawn over it)
	after(STEP * 2, func() -> void:
		if is_instance_valid(target):
			flash(target, Color.WHITE, [0.6, 0.0, 0.45, 0.0, 0.25]))
	hitstop([actor, target], freeze)
	jolt(target, recipe.get("jolt", 2.0))
	shake(recipe.get("shake", 0.0), recipe.get("shake_life", 0.3))   # the screen itself only for the heavy blows
	if recipe.has("white"):
		flash_stage(Color.WHITE, recipe.white)
	after(freeze, func() -> void:
		if is_instance_valid(target):
			var a := target.get_node_or_null("anim") as AnimatedSprite2D
			if a != null and a.sprite_frames.has_animation("hit"):
				a.play("hit")
			knock(target, dir, recipe.get("knock", 8.0)))


## A machine going down: blasts break out over its body one after another, then a white flash and a column of
## fireballs climbing in waves (Zoids Legacy's explosion columns climb in waves four frames apart), flying plate, and a
## smoke column that outlasts the step. Returns how long the step should hold.
func destroyed(node: Node2D) -> float:
	var r := rect_of(node, frame_tex(node, "", -1))
	var dir := signf(node.scale.x)
	var at := func(fx: float, fy: float) -> Vector2:
		return node.position + Vector2((r.position.x + r.size.x * fx) * node.scale.x, r.position.y + r.size.y * fy)
	for i in 6:
		var p: Vector2 = at.call(rng.randf_range(0.15, 0.85), rng.randf_range(0.2, 0.75))
		after(0.1 + 0.14 * i, func() -> void:
			explosion(p, {"r": rng.randf_range(10.0, 14.0), "life": 0.45, "smoke": false})
			sparks(p, dir, {"count": 6, "spread": 180.0, "speed": 120.0})
			shake(1.5, 0.12))
	var center: Vector2 = at.call(0.5, 0.55)
	var feet: Vector2 = at.call(0.5, 1.0)
	after(0.95, func() -> void:
		flash_stage(Color.WHITE, 0.6)
		debris(center, dir, {"count": 16, "speed": 150.0, "ground": feet.y, "life": 1.0})
		sparks(center, dir, {"count": 14, "spread": 180.0, "speed": 180.0, "life": 0.45})
		shake(6.0, 0.5))
	for w in 5:   # the column: each wave a little higher and smaller
		var p: Vector2 = center + Vector2(rng.randf_range(-0.15, 0.15) * r.size.x, -w * r.size.y * 0.16)
		after(0.95 + w * 4.0 / 60.0, func() -> void: explosion(p, {"r": 26.0 - w * 3.0, "life": 0.7}))
	after(1.3, func() -> void: smoke(feet + Vector2(0, -8), {"count": 10, "r": 9.0, "life": 1.3, "rise": 54.0}))
	return 2.65   # the smoke is gone before the next machine can be staged here


## Charging energy: light drawn into the machine's core, and a cyan blink.
func charging(node: Node2D) -> void:
	var c := point(node, "center", 0.5)
	charge_in(c, {"r": 46.0, "count": 22, "life": 0.65})   # Zoids Legacy draws its charge from a 48-68 px arc
	after(0.45, func() -> void:
		flash(node, Color("5fe1d0"), [0.6, 0.0, 0.4, 0.0])
		sparkle(c, {"ramp": "cyan", "count": 5, "life": 0.5}))


## A repair or energy item: green plus-signs rising, and a green blink.
func repaired(node: Node2D) -> void:
	sparkle(point(node, "center", 0.5), {"count": 8})
	flash(node, Color("7cff9a"), [0.5, 0.0, 0.35, 0.0])
