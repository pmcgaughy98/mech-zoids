extends SceneTree
## The gorilla lighting slice (Claude, 2026-10-14; reports/Lit pixel sprites in Godot.md). Builds a battle stage in a
## 320x180 SubViewport so light lands per art pixel: the gorilla's side view as a CanvasTexture (its colour and the
## normal map tools/art/pixelize_render.py writes next to it) with shaders/banded_light.gdshader, a key light from the
## upper left matching the light baked into the sprite, a cool rim light, the visor drawn unshaded with a 1 px additive
## halo and a teal light on the plates around it, and a hit flash. Run windowed:
##   Godot --path . --script res://tools/debug/lit_capture.gd
## Writes docs/art/2d/lit_capture.png (baked only, lit, lit with a hit flash, two key-light angles, the flip test) and
## prints the report's checks: flip (a flipped sprite lit from the left mirrors the plain one lit from the right) and
## energy (doubling the key light's energy doubles the light added, not quadruples it).

const DIR := "res://art/machines/ape_l/lit/"

var vp: SubViewport
var sprite: Sprite2D
var visor: Sprite2D
var halo: Sprite2D
var key: DirectionalLight2D
var rim: PointLight2D
var visor_light: PointLight2D
var flash: PointLight2D
var cmod: CanvasModulate
var lit_mat: ShaderMaterial
var bg_layer: CanvasLayer
var flash_bg: PointLight2D
var col_img: Image


func _initialize() -> void:
	call_deferred("_run")


func _tex(file: String) -> ImageTexture:
	# loaded as plain images: the normal map must stay lossless (no VRAM compression, no mipmaps)
	return ImageTexture.create_from_image(Image.load_from_file(ProjectSettings.globalize_path(DIR + file)))


func _radial() -> GradientTexture2D:
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(1, 1, 1, 0))
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(1.0, 0.5)
	t.width = 64
	t.height = 64
	return t


func _point(c: Color, energy: float, height: float, radius: float, pos: Vector2) -> PointLight2D:
	var l := PointLight2D.new()
	l.texture = _radial()
	l.texture_scale = radius * 2.0 / 64.0
	l.color = c
	l.energy = energy
	l.height = height
	l.position = pos
	l.range_item_cull_mask = 2   # lights only the machine
	vp.add_child(l)
	return l


func _halo(e: Image) -> ImageTexture:
	var w := e.get_width()
	var h := e.get_height()
	var out := Image.create(w, h, false, Image.FORMAT_RGBA8)
	for y in h:
		for x in w:
			if e.get_pixel(x, y).a > 0.5:
				continue
			for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
				var q: Vector2i = Vector2i(x, y) + d
				if q.x >= 0 and q.y >= 0 and q.x < w and q.y < h and e.get_pixelv(q).a > 0.5:
					out.set_pixel(x, y, Color(0.12, 0.55, 0.5, 0.5))
					break
	return ImageTexture.create_from_image(out)


func _centroid(e: Image) -> Vector2:
	var s := Vector2.ZERO
	var n := 0
	for y in e.get_height():
		for x in e.get_width():
			if e.get_pixel(x, y).a > 0.5:
				s += Vector2(x, y)
				n += 1
	return s / max(n, 1)


func _build() -> void:
	root.size = Vector2i(1280, 720)
	root.content_scale_size = Vector2i(320, 180)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	var cont := SubViewportContainer.new()
	cont.stretch = true
	cont.size = Vector2(320, 180)
	cont.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(cont)
	vp = SubViewport.new()
	vp.size = Vector2i(320, 180)
	vp.snap_2d_transforms_to_pixel = true
	vp.snap_2d_vertices_to_pixel = true
	vp.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	cont.add_child(vp)
	var bg := Sprite2D.new()
	bg.centered = false
	bg.texture = load("res://art/battle/background.png")
	# the stage on its own canvas layer: the machine's darker ambient (CanvasModulate) stays off it, and its own copy of
	# the hit flash lights the ground
	bg_layer = CanvasLayer.new()
	bg_layer.layer = -1
	vp.add_child(bg_layer)
	bg_layer.add_child(bg)
	var col := _tex("e.png")
	col_img = col.get_image()
	var ct := CanvasTexture.new()
	ct.diffuse_texture = col
	ct.normal_texture = _tex("e_n.png")
	sprite = Sprite2D.new()
	sprite.texture = ct
	sprite.centered = false
	sprite.position = Vector2(70, 124 - col.get_height())
	lit_mat = ShaderMaterial.new()
	lit_mat.shader = load("res://shaders/banded_light.gdshader")
	sprite.material = lit_mat
	sprite.light_mask = 2   # the machine: key, rim, visor and flash all reach it
	vp.add_child(sprite)
	var e_img := Image.load_from_file(ProjectSettings.globalize_path(DIR + "e_e.png"))
	visor = Sprite2D.new()
	visor.texture = ImageTexture.create_from_image(e_img)
	visor.centered = false
	var unshaded := CanvasItemMaterial.new()
	unshaded.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	visor.material = unshaded
	sprite.add_child(visor)
	halo = Sprite2D.new()
	halo.texture = _halo(e_img)
	halo.centered = false
	var add := CanvasItemMaterial.new()
	add.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	halo.material = add
	sprite.add_child(halo)
	cmod = CanvasModulate.new()
	cmod.color = Color(0.68, 0.7, 0.8)
	vp.add_child(cmod)
	key = DirectionalLight2D.new()
	key.rotation_degrees = -45.0   # travelling down and right: from the upper left, as the bake
	key.height = 0.6
	key.energy = 0.45
	key.color = Color(1.0, 0.95, 0.86)
	vp.add_child(key)
	var w := float(col.get_width())
	var h := float(col.get_height())
	rim = _point(Color(0.55, 0.72, 1.0), 0.5, 4.0, 70.0, sprite.position + Vector2(w + 12, h * 0.25))
	visor_light = _point(Color(0.3, 1.0, 0.9), 0.7, 6.0, 26.0, sprite.position + _centroid(e_img))
	flash = _point(Color(1.0, 0.82, 0.55), 0.0, 24.0, 70.0, sprite.position + Vector2(w + 4, h * 0.7))
	flash_bg = _point(Color(1.0, 0.82, 0.55), 0.0, 24.0, 70.0, flash.position)
	flash_bg.range_item_cull_mask = 1
	flash_bg.reparent(bg_layer)


func _shot() -> Image:
	for i in 4:
		await process_frame
	await RenderingServer.frame_post_draw
	return root.get_texture().get_image()


func _setup(lit: bool, flash_e := 0.0, key_rot := -45.0, extras := true) -> void:
	sprite.material = lit_mat if lit else null
	cmod.visible = lit
	key.enabled = lit
	key.rotation_degrees = key_rot
	rim.enabled = lit and extras
	visor_light.enabled = lit and extras
	visor.visible = lit and extras
	halo.visible = lit and extras
	flash.energy = flash_e
	flash.enabled = lit and flash_e > 0.0
	flash_bg.energy = flash_e * 0.6
	flash_bg.enabled = lit and flash_e > 0.0


## Mean brightness of the sprite's own pixels in a window shot (the viewport is drawn 4x).
func _sprite_mean(img: Image, flipped := false) -> float:
	var s := 0.0
	var n := 0
	for y in col_img.get_height():
		for x in col_img.get_width():
			if col_img.get_pixel(x, y).a < 0.5:
				continue
			var sx := (col_img.get_width() - 1 - x) if flipped else x
			var p := img.get_pixel(int((sprite.position.x + sx) * 4 + 2), int((sprite.position.y + y) * 4 + 2))
			s += p.r + p.g + p.b
			n += 1
	return s / max(n, 1) / 3.0


func _run() -> void:
	_build()
	var shots: Array = []
	_setup(false)
	shots.append(await _shot())                    # 1 baked only: the sprite as installed
	_setup(true)
	shots.append(await _shot())                    # 2 lit: key, rim, visor
	_setup(true, 1.6)
	shots.append(await _shot())                    # 3 lit with a hit flash
	_setup(true, 0.0, 45.0, false)
	shots.append(await _shot())                    # 4 key light from the upper right
	_setup(true, 0.0, 180.0, false)
	shots.append(await _shot())                    # 5 key light from below
	# flip test: flipped and lit from the left should mirror the plain sprite lit from the right
	_setup(true, 0.0, 90.0, false)                 # travelling left: lit from the right
	var plain := await _shot()
	sprite.flip_h = true
	_setup(true, 0.0, -90.0, false)                # travelling right: lit from the left
	var flipped := await _shot()
	shots.append(flipped)                          # 6 flip test
	var a := _sprite_mean(plain)
	var b := _sprite_mean(flipped, true)
	sprite.flip_h = false
	# energy test: only the key light over a black ambient, energy 0.5 then 1.0
	_setup(true, 0.0, -45.0, false)
	cmod.color = Color(0, 0, 0)
	lit_mat.set_shader_parameter("bands", 8.0)
	key.energy = 0.5
	var e1 := _sprite_mean(await _shot())
	key.energy = 1.0
	var e2 := _sprite_mean(await _shot())
	var closeups: Array = []
	var cr := Rect2i(int(sprite.position.x * 4) - 8, int(sprite.position.y * 4) - 8, col_img.get_width() * 4 + 16, col_img.get_height() * 4 + 16)
	for i in 3:
		closeups.append((shots[i] as Image).get_region(cr))
	var w: int = shots[0].get_width() / 2
	var h: int = shots[0].get_height() / 2
	var sheet := Image.create(w * 3, h * 2, false, Image.FORMAT_RGBA8)
	for i in shots.size():
		var s: Image = shots[i]
		s.resize(w, h, Image.INTERPOLATE_NEAREST)
		sheet.blit_rect(s, Rect2i(0, 0, w, h), Vector2i((i % 3) * w, (i / 3) * h))
	sheet.save_png("res://docs/art/2d/lit_capture.png")
	shots[1].save_png("res://docs/art/2d/lit_capture_lit.png")
	var r := Rect2i(int(sprite.position.x * 4) - 8, int(sprite.position.y * 4) - 8, col_img.get_width() * 4 + 16, col_img.get_height() * 4 + 16)
	var pair := Image.create(r.size.x * 3, r.size.y, false, Image.FORMAT_RGBA8)
	for i in 3:   # baked, lit, lit with the flash, close up
		var full: Image = shots[i]
		if full.get_width() != shots[0].get_width() * 2:
			pass
		pair.blit_rect(closeups[i], Rect2i(Vector2i.ZERO, r.size), Vector2i(i * r.size.x, 0))
	pair.save_png("res://docs/art/2d/lit_capture_closeup.png")
	print("lit_capture: flip test, plain lit from the right %.3f vs flipped lit from the left %.3f (%s)" % [a, b, "PASS" if abs(a - b) < 0.02 else "CHECK"])
	print("lit_capture: energy test, key 0.5 adds %.3f, 1.0 adds %.3f, ratio %.2f (2 = energy applied once)" % [e1, e2, e2 / max(e1, 0.0001)])
	quit(0)
