class_name MatchHud
extends CanvasLayer
## The match HUD. Map design lane since 2026-11-05; the game feel lane built the first one (2026-11-04) and handed it
## over. Layout after SMITE's (docs/plan/moba-hud-reimagine-2026-11-05.md, mock-up B, Preston's pick), drawn as pixel
## art in our own look: steel plates, rivets, hazard trim and a 3 x 5 pixel font, every square a whole pixel of the
## 320 x 180 canvas (canvas_items stretch, integer scale).
##   over every unit: a health bar, unchanged from 2026-11-04 at the old 720-line scale (cam_angle_set_test.gd's BARS)
##   top centre: team kills, tower and core pips, the clock; the next wave; the nearest structure's health when near
##   top left: allies (portrait, health, slot-4 recharge diamond); the kill feed under them
##   top right: enemies (portrait; grey at low health while seen; respawn seconds when down)
##   bottom centre: your bar (portrait, health, four kit slots, attack, recall; seconds replace the key while cooling;
##     a white edge flashes when ready; a red icon while a tower aims at you)
##   bottom left: kills / deaths / assists.  bottom right: the minimap (map lane, its own layer 5)
##   the middle: the tower's aim line, low-health pulse and edge glow, respawn and recall, victory and defeat
##   above everything (layer 7): the mouse-aim ring and line, redrawn in 2D when they fall under a panel

const SLOT_NAMES := {
	"rhino": ["horn toss", "ground pound", "brace", "stampede"],
	"gorilla": ["hex shield", "none", "bound", "chest beat"], # 2026-11-09: the chest beat is the ult on 4; 2 waits on Preston
	"fennec": ["sand kick", "blink gate", "tunnel", "sonic boom"],
}
const ICON_OF := {
	"horn toss": "horn", "ground pound": "pound", "brace": "shield", "stampede": "dash",
	"hex shield": "shield", "chest beat": "dome", "bound": "dash", # the ult ends in the hex dome, so it keeps the dome's icon
	"sand kick": "horn", "blink gate": "ring", "tunnel": "pound", "sonic boom": "ring",
}
const GREEN := Color(0.42, 1.0, 0.45)
const ALLY := Color(0.35, 0.62, 1.0)
const ENEMY := Color(1.0, 0.34, 0.28)
const PLATE := Color8(26, 29, 37)
const PLATE_HI := Color8(60, 66, 80)
const PLATE_LO := Color8(14, 15, 20)
const EDGE := Color8(6, 7, 10)
const RIVET := Color8(110, 116, 132)
const HAZ_Y := Color8(236, 184, 38)
const HAZ_K := Color8(24, 24, 26)
const GOLD := Color8(255, 199, 77)
const WHITE := Color8(240, 240, 240)
const DIM := Color8(150, 156, 168)
const DOWN := Color8(100, 102, 108)
const SLOT_BG := Color8(40, 44, 54)
const ICON := Color8(214, 218, 228)
const BAR_BG := Color8(10, 10, 13)
const NEAR_STRUCTURE := 16.0
const LOW_HP := 0.28
const ASSIST_TIME := 10.0
const FLASH_TIME := 0.35
const MACHINE_BAR_TILTED := 2.3 ## see the 2026-11-04 note: clears the 35-degree rhino idle from the player's spot out
const DESIGN_H := 720.0

const FONT := {
	"A": ["010", "101", "111", "101", "101"], "B": ["110", "101", "110", "101", "110"],
	"C": ["011", "100", "100", "100", "011"], "D": ["110", "101", "101", "101", "110"],
	"E": ["111", "100", "110", "100", "111"], "F": ["111", "100", "110", "100", "100"],
	"G": ["011", "100", "101", "101", "011"], "H": ["101", "101", "111", "101", "101"],
	"I": ["111", "010", "010", "010", "111"], "J": ["001", "001", "001", "101", "010"],
	"K": ["101", "101", "110", "101", "101"], "L": ["100", "100", "100", "100", "111"],
	"M": ["101", "111", "101", "101", "101"], "N": ["110", "101", "101", "101", "101"],
	"O": ["010", "101", "101", "101", "010"], "P": ["110", "101", "110", "100", "100"],
	"Q": ["010", "101", "101", "110", "011"], "R": ["110", "101", "110", "101", "101"],
	"S": ["011", "100", "010", "001", "110"], "T": ["111", "010", "010", "010", "010"],
	"U": ["101", "101", "101", "101", "111"], "V": ["101", "101", "101", "101", "010"],
	"W": ["101", "101", "101", "111", "101"], "X": ["101", "101", "010", "101", "101"],
	"Y": ["101", "101", "010", "010", "010"], "Z": ["111", "001", "010", "100", "111"],
	"0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
	"2": ["110", "001", "010", "100", "111"], "3": ["110", "001", "010", "001", "110"],
	"4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "110", "001", "110"],
	"6": ["011", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"],
	"8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "110"],
	":": ["0", "1", "0", "1", "0"], "/": ["001", "001", "010", "100", "100"],
	".": ["0", "0", "0", "0", "1"], ",": ["0", "0", "0", "1", "1"], "-": ["000", "000", "111", "000", "000"],
	">": ["100", "010", "001", "010", "100"], "+": ["000", "010", "111", "010", "000"],
	"!": ["1", "1", "1", "0", "1"], "'": ["1", "1", "0", "0", "0"], " ": ["00", "00", "00", "00", "00"],
}
const DIG := {
	"0": [".##.", "#..#", "#..#", "#..#", "#..#", ".##."], "1": [".#..", "##..", ".#..", ".#..", ".#..", "###."],
	"2": [".##.", "#..#", "..#.", ".#..", "#...", "####"], "3": ["###.", "...#", ".##.", "...#", "...#", "###."],
	"4": ["#..#", "#..#", "####", "...#", "...#", "...#"], "5": ["####", "#...", "###.", "...#", "...#", "###."],
	"6": [".##.", "#...", "###.", "#..#", "#..#", ".##."], "7": ["####", "...#", "..#.", ".#..", ".#..", ".#.."],
	"8": [".##.", "#..#", ".##.", "#..#", "#..#", ".##."], "9": [".##.", "#..#", "#..#", ".###", "...#", ".##."],
	".": [".", ".", ".", ".", ".", "#"],
}
const ICONS := {
	"horn": ["........#", ".......##", "......##.", ".....##..", "....###..", "...###...", "..####...", ".#####...", "#######.."],
	"pound": ["...###...", "...###...", "...###...", ".#######.", "..#####..", "...###...", "....#....", ".........", "#########"],
	"shield": ["#########", "#.......#", "#.#####.#", "#.#####.#", "#.#####.#", ".#.###.#.", ".#.###.#.", "..#.#.#..", "....#...."],
	"dash": [".........", "#...#....", ".#...#...", "..#...#..", "...#...#.", "..#...#..", ".#...#...", "#...#....", "........."],
	"dome": [".........", "...###...", "..#...#..", ".#.....#.", ".#.###.#.", "#..#.#..#", "#.......#", "#########", "........."],
	"ring": ["..#####..", ".#.....#.", "#..###..#", "#.#...#.#", "#.#.#.#.#", "#.#...#.#", "#..###..#", ".#.....#.", "..#####.."],
}
const DIAMOND := ["..#..", ".###.", "#####", ".###.", "..#.."]
const PIT_RING := [".###.", "#...#", "#...#", "#...#", ".###."] ## a side pit, open to take
const PIT_SHUT := [".###.", "#####", "#####", "#####", ".###."] ## a side pit, locked for its owners
const BEACON_GLYPH := ["..#..", ".###.", "##.##", ".###.", "..#.."] ## the plaza beacon
const BEACON_WARN := 30.0 ## its countdown shows this many seconds before it comes up
const WARN := ["...#...", "..###..", "..#.#..", ".##.##.", ".#####.", "##.#.##", "#######"]

var director: MatchDirector
var warning := false ## a tower is aiming at the player (the checks read it)
var _bars: Control
var _canvas: Control
var _over: Control
var _feed: Array = []
var _font: Font
var _k := 1.0
var _glyphs: Texture2D
var _glyph_at := {}
var _digits: Texture2D
var _digit_at := {}
var _hazard: Texture2D
var _ports := {}
var _kills := {"blue": 0, "red": 0}
var _kda := [0, 0, 0]
var _hit_at := {}
var _hooked := {}
var _cd_was := {}
var _flash := {}
var _map_rect := Rect2()
var _pits: Array = [] ## the arena's ArenaPit nodes, found once they exist
var _beacon = null ## the plaza ArenaBeacon once it exists (untyped: found by group)


func _ready() -> void:
	layer = 4
	_font = ThemeDB.fallback_font
	var made := _atlas(FONT, 5)
	_glyphs = made[0]
	_glyph_at = made[1]
	made = _atlas(DIG, 6)
	_digits = made[0]
	_digit_at = made[1]
	var hz := Image.create(4, 2, false, Image.FORMAT_RGBA8)
	for y in 2:
		for x in 4:
			hz.set_pixel(x, y, HAZ_Y if floori((x + y) / 2.0) % 2 == 0 else HAZ_K)
	_hazard = ImageTexture.create_from_image(hz)
	_bars = _layer_control(_paint_bars)
	add_child(_bars)
	_canvas = _layer_control(_paint)
	_canvas.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	add_child(_canvas)
	var top := CanvasLayer.new()
	top.layer = 7
	add_child(top)
	_over = _layer_control(_paint_aim)
	top.add_child(_over)
	director.feed.connect(func(text: String, colour: Color) -> void:
		_feed.push_front({"text": text, "colour": colour, "t": 0.0})
		if _feed.size() > 5:
			_feed.pop_back())
	director.unit_died.connect(_on_unit_died)


func _layer_control(painter: Callable) -> Control:
	var c := Control.new()
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	c.draw.connect(painter)
	return c


func _atlas(font: Dictionary, h: int) -> Array:
	var w := 0
	for c in font:
		w += String(font[c][0]).length() + 1
	var img := Image.create(w, h, false, Image.FORMAT_RGBA8)
	var at := {}
	var x := 0
	for c in font:
		var rows: Array = font[c]
		var gw := String(rows[0]).length()
		for r in rows.size():
			var row: String = rows[r]
			for q in gw:
				if row[q] == "1" or row[q] == "#":
					img.set_pixel(x + q, r, Color.WHITE)
		at[c] = Rect2(x, 0, gw, h)
		x += gw + 1
	return [ImageTexture.create_from_image(img), at]


func _process(delta: float) -> void:
	for f in _feed:
		f["t"] += delta
	_feed = _feed.filter(func(f: Dictionary) -> bool: return f["t"] < 7.0)
	warning = director.player_targeted_by() != null
	var view := get_viewport().get_visible_rect().size
	_k = view.y / DESIGN_H
	_bars.scale = Vector2.ONE * _k
	_bars.size = view / _k
	_canvas.size = view
	_over.size = view
	_watch_machines(delta)
	_hook_pits()
	_bars.queue_redraw()
	_canvas.queue_redraw()
	_over.queue_redraw()


func feed_lines() -> Array:
	return _feed.map(func(f: Dictionary) -> String: return f["text"])


func _watch_machines(delta: float) -> void:
	var p := director.player
	if p == null:
		return
	for m: Node3D in director.machines:
		if not _hooked.has(m) and is_instance_valid(m) and m.has_signal("damaged") and MatchTeams.is_enemy(m, p):
			_hooked[m] = true
			m.damaged.connect(func(_amount: float, by: Node3D) -> void:
				if by == director.player:
					_hit_at[m] = director.elapsed)
	for slot in ["1", "2", "3", "4"]:
		var left := float(p.cooldowns.get(slot, 0.0))
		if float(_cd_was.get(slot, 0.0)) > 0.0 and left <= 0.0:
			_flash[slot] = FLASH_TIME
		_cd_was[slot] = left
		_flash[slot] = maxf(float(_flash.get(slot, 0.0)) - delta, 0.0)


func _on_unit_died(u: Node3D, by: Node3D) -> void:
	if not (u in director.machines):
		return
	var t := MatchTeams.team_of(u)
	if t == "":
		return
	_kills["red" if t == "blue" else "blue"] += 1
	var p := director.player
	if u == p:
		_kda[1] += 1
	elif MatchTeams.is_enemy(u, p):
		if by == p:
			_kda[0] += 1
		elif _hit_at.has(u) and director.elapsed - float(_hit_at[u]) <= ASSIST_TIME:
			_kda[2] += 1
	_hit_at.erase(u)


func _tw(s: String, dig := false) -> int:
	var at := _digit_at if dig else _glyph_at
	var w := 0
	for c in s.to_upper():
		var r: Rect2 = at[c] if at.has(c) else Rect2(0, 0, 2, 1)
		w += int(r.size.x) + 1
	return maxi(w - 1, 0)


func _text(c: Control, pos: Vector2, s: String, col: Color, style := 0, k := 1, dig := false) -> void:
	var tex := _digits if dig else _glyphs
	var at := _digit_at if dig else _glyph_at
	var offs: Array = []
	if style == 1:
		offs = [Vector2(1, 1)]
	elif style == 2:
		offs = [Vector2(-1, -1), Vector2(0, -1), Vector2(1, -1), Vector2(-1, 0), Vector2(1, 0), Vector2(-1, 1), Vector2(0, 1), Vector2(1, 1)]
	var dark := EDGE
	dark.a = col.a
	pos = pos.floor()
	for pass_i in 2:
		var x := pos.x
		for ch in s.to_upper():
			if not at.has(ch):
				x += 3 * k
				continue
			var src: Rect2 = at[ch]
			var dst := Rect2(Vector2(x, pos.y), src.size * k)
			if pass_i == 0:
				for o: Vector2 in offs:
					c.draw_texture_rect_region(tex, Rect2(dst.position + o, dst.size), src, dark)
			else:
				c.draw_texture_rect_region(tex, dst, src, col)
			x += (src.size.x + 1) * k


func _px(x: float, y: float, col: Color) -> void:
	_canvas.draw_rect(Rect2(x, y, 1, 1), col)


func _frame(r: Rect2, col: Color) -> void:
	_canvas.draw_rect(Rect2(r.position.x - 1, r.position.y - 1, r.size.x + 2, 1), col)
	_canvas.draw_rect(Rect2(r.position.x - 1, r.end.y, r.size.x + 2, 1), col)
	_canvas.draw_rect(Rect2(r.position.x - 1, r.position.y, 1, r.size.y), col)
	_canvas.draw_rect(Rect2(r.end.x, r.position.y, 1, r.size.y), col)


func _plate(r: Rect2, trim := false, rivets := true) -> void:
	_canvas.draw_rect(r.grow(1.0), EDGE)
	_canvas.draw_rect(r, PLATE)
	_canvas.draw_rect(Rect2(r.position, Vector2(r.size.x, 1)), PLATE_HI)
	_canvas.draw_rect(Rect2(r.position.x, r.end.y - 1, r.size.x, 1), PLATE_LO)
	if trim:
		_canvas.draw_texture_rect(_hazard, Rect2(r.position, Vector2(r.size.x, 2)), true)
	if rivets and r.size.x >= 30 and r.size.y >= 14:
		var t := 2.0 if trim else 0.0
		for p: Vector2 in [Vector2(r.position.x + 2, r.position.y + 2 + t), Vector2(r.end.x - 3, r.position.y + 2 + t),
				Vector2(r.position.x + 2, r.end.y - 3), Vector2(r.end.x - 3, r.end.y - 3)]:
			_px(p.x, p.y, RIVET)


func _pbar(r: Rect2, share: float, col: Color) -> void:
	_canvas.draw_rect(r, BAR_BG)
	var n := roundf(r.size.x * clampf(share, 0.0, 1.0))
	if n <= 0.0:
		return
	_canvas.draw_rect(Rect2(r.position, Vector2(n, r.size.y)), col)
	_canvas.draw_rect(Rect2(r.position, Vector2(n, 1)), col.lerp(Color.WHITE, 0.4))
	if r.size.y >= 3:
		_canvas.draw_rect(Rect2(r.position.x, r.end.y - 1, n, 1), col.darkened(0.3))


func _glyph(at: Vector2, rows: Array, col: Color) -> void:
	for r in rows.size():
		var row: String = rows[r]
		for q in row.length():
			if row[q] == "#":
				_px(at.x + q, at.y + r, col)


func _port(kind: String, size: int, grey: bool) -> Texture2D:
	var key := "%s/%d/%s" % [kind, size, grey]
	if _ports.has(key):
		return _ports[key]
	var tex: Texture2D = null
	var dirn: String = {"gorilla": "ape"}.get(kind, kind)
	var path := "res://art/machines/%s/%s_frames.tres" % [dirn, dirn]
	if ResourceLoader.exists(path):
		var sf: SpriteFrames = load(path)
		var anim: StringName = &"idle_s" if sf.has_animation(&"idle_s") else StringName(sf.get_animation_names()[0])
		var src := sf.get_frame_texture(anim, 0)
		if src != null:
			var img := src.get_image()
			if img.is_compressed():
				img.decompress()
			img.convert(Image.FORMAT_RGBA8)
			var used := img.get_used_rect()
			if used.size.x > 0:
				var side := mini(used.size.x, used.size.y)
				img = img.get_region(Rect2i(used.position.x + (used.size.x - side) / 2, used.position.y, side, side))
				img.resize(size, size, Image.INTERPOLATE_LANCZOS)
				var bg := Image.create(size, size, false, Image.FORMAT_RGBA8)
				bg.fill(Color8(44, 48, 60))
				bg.blend_rect(img, Rect2i(0, 0, size, size), Vector2i.ZERO)
				if grey:
					for y in size:
						for x in size:
							var v := bg.get_pixel(x, y).get_luminance() * 0.5 + 0.12
							bg.set_pixel(x, y, Color(v, v, v + 0.02))
				tex = ImageTexture.create_from_image(bg)
	_ports[key] = tex
	return tex


func _portrait(at: Vector2, size: int, kind: String, rim: Color, state := "", secs := 0) -> void:
	_canvas.draw_rect(Rect2(at, Vector2(size, size)), rim)
	var inner := size - 2
	var tex := _port(kind, inner, state != "")
	if tex != null:
		_canvas.draw_texture_rect(tex, Rect2(at + Vector2.ONE, Vector2(inner, inner)), false,
				Color(0.5, 0.5, 0.5) if state == "down" else Color.WHITE)
	if state == "down":
		var s := str(secs)
		_text(_canvas, Vector2(at.x + floorf((size - _tw(s)) / 2.0), at.y + floorf((size - 5) / 2.0)), s, WHITE, 1)


func _diamond(at: Vector2, share: float) -> void:
	for r in 5:
		for q in 5:
			if DIAMOND[r][q] == "#":
				var lit := share >= 1.0 or (4 - r) / 4.0 < share
				_px(at.x + q, at.y + r, GOLD if lit else Color8(60, 58, 52))
	if share >= 1.0:
		_px(at.x + 2, at.y + 1, WHITE)


func _slot(at: Vector2, n: int, key: String, icon: String, left: float, total: float, flash: float, small := false,
		empty := false) -> void:
	_canvas.draw_rect(Rect2(at - Vector2.ONE, Vector2(n + 2, n + 2)), EDGE)
	if empty: # a kit's slot named "none": nothing on this key yet. Sunk, hatched, the key dimmed; no sweep or flash
		_canvas.draw_rect(Rect2(at, Vector2(n, n)), PLATE_LO)
		for k in range(2, n * 2, 4):
			for t in range(1, n - 1):
				if k - t >= 1 and k - t < n - 1:
					_canvas.draw_rect(Rect2(at.x + k - t, at.y + t, 1, 1), PLATE)
		_text(_canvas, at + Vector2(1, 1), key, DOWN, 1)
		return
	_canvas.draw_rect(Rect2(at, Vector2(n, n)), SLOT_BG)
	_canvas.draw_rect(Rect2(at, Vector2(n, 1)), PLATE_HI)
	if icon != "":
		_glyph(at + Vector2(floorf((n - 9) / 2.0), floorf((n - 9) / 2.0) + 1), ICONS[icon], ICON)
	var cooling := left > 0.0 and total > 0.0
	if cooling:
		var share := clampf(left / total, 0.0, 1.0)
		var cx := at.x + n / 2.0
		var cy := at.y + n / 2.0
		for yy in n:
			for xx in n:
				var a := fposmod(rad_to_deg(atan2(at.x + xx + 0.5 - cx, -(at.y + yy + 0.5 - cy))), 360.0)
				if a < share * 360.0:
					_canvas.draw_rect(Rect2(at.x + xx, at.y + yy, 1, 1), Color(0, 0, 0, 0.7))
	if small:
		_text(_canvas, Vector2(at.x + floorf((n - _tw(key)) / 2.0), at.y + floorf((n - 5) / 2.0)), key, GOLD, 1)
	elif cooling:
		var s := str(ceili(left)) if left >= 1.0 else ("%.1f" % left).substr(1)
		_text(_canvas, Vector2(at.x + floorf((n - _tw(s, true)) / 2.0), at.y + floorf((n - 6) / 2.0)), s, WHITE, 2, 1, true)
	elif key != "":
		_text(_canvas, at + Vector2(1, 1), key, GOLD, 1)
	if flash > 0.0:
		_frame(Rect2(at, Vector2(n, n)), Color(1, 1, 1, clampf(flash / FLASH_TIME, 0.0, 1.0)))


func _mmss(s: float) -> String:
	return "%d:%02d" % [int(s) / 60, int(s) % 60]


func _rel(team: String) -> Color:
	return ALLY if team == director.player.team else ENEMY


func _paint() -> void:
	if director == null or director.player == null:
		return
	var vs := _canvas.size
	_middle_back(vs)
	_top(vs)
	_allies_and_feed()
	_enemies(vs)
	_player_bar(vs)
	_kda_panel(vs)
	_middle_front(vs)


func _top(vs: Vector2) -> void:
	var own: String = director.player.team
	var other := "red" if own == "blue" else "blue"
	var cx := floorf(vs.x / 2.0)
	var sx := cx - 38.0
	_plate(Rect2(sx, 2, 76, 10), false, false)
	_text(_canvas, Vector2(cx - floorf(_tw("00:00") / 2.0), 4), _mmss(director.elapsed), WHITE)
	_text(_canvas, Vector2(sx + 3, 4), str(_kills[own]), ALLY)
	var ks := str(_kills[other])
	_text(_canvas, Vector2(sx + 73 - _tw(ks), 4), ks, ENEMY)
	for side in [[own, sx + 11 + (_tw(str(_kills[own])) - 3)], [other, sx + 57 - (_tw(ks) - 3)]]:
		var team: String = side[0]
		var x0: float = side[1]
		var tw_s: MatchStructure = director.structures.get(team.capitalize() + "Tower")
		var co_s: MatchStructure = director.structures.get(team.capitalize() + "Core")
		var col := _rel(team)
		var tcol := col if tw_s != null and tw_s.alive else DOWN
		if tw_s != null and tw_s.alive and _off(tw_s) > 0.0: # switched off by the beacon: blinks dark
			tcol = col.darkened(0.6) if fmod(director.elapsed, 0.6) < 0.3 else DOWN
		_canvas.draw_rect(Rect2(x0, 5, 3, 4), tcol)
		_glyph(Vector2(x0 + 4, 4), DIAMOND, col if co_s != null and co_s.alive else DOWN)
	var wave := "WAVE " + _mmss(ceilf(maxf(director.next_wave - director.elapsed, 0.0)))
	_text(_canvas, Vector2(cx - floorf(_tw(wave) / 2.0), 14), wave, DIM, 2)
	var by := 29.0 if _beacon_row(cx) else 22.0
	var near := _near_structure()
	if near != null:
		var label_s := "%s %s" % [near.team, near.kind]
		if _off(near) > 0.0:
			label_s += " off %d" % ceili(_off(near))
		var col := _rel(near.team)
		if near.kind == "core" and not near.can_be_hit():
			col = col.darkened(0.45)
		_text(_canvas, Vector2(cx - floorf(_tw(label_s) / 2.0), by), label_s, col, 2)
		_canvas.draw_rect(Rect2(cx - 30, by + 6, 60, 4), EDGE)
		_pbar(Rect2(cx - 29, by + 7, 58, 2), near.hp / near.max_hp, col)
	for p in _pits: # either side of the wave timer: your half's pit on the left, theirs on the right
		_pit_marker(Vector2(cx - 31 if p.home_team == own else cx + 26, 14), p)


## A side pit in the top stack: a ring in the owner's colour (gold while nobody holds it), filled while it is
## locked, blinking the taker's colour with a fill line under it while a team is taking it.
func _pit_marker(at: Vector2, p: ArenaPit) -> void:
	var col: Color = GOLD.darkened(0.3) if p.owner_team == "" else _rel(p.owner_team)
	var taking: bool = p.capturing != "" and p.progress > 0.0
	if taking and fmod(director.elapsed, 0.5) < 0.25:
		col = _rel(p.capturing)
	_glyph(at, PIT_SHUT if p.locked_left > 0.0 else PIT_RING, col)
	if taking:
		_canvas.draw_rect(Rect2(at.x, at.y + 6, 5, 1), EDGE)
		_canvas.draw_rect(Rect2(at.x, at.y + 6, floorf(5.0 * p.progress), 1), _rel(p.capturing))


func _hook_pits() -> void:
	if _pits.is_empty():
		for p in get_tree().get_nodes_in_group("arena_pits"):
			_pits.append(p)
			p.pit_taken.connect(_on_pit_taken.bind(p))
	if _beacon == null:
		_beacon = get_tree().get_first_node_in_group("arena_beacons")
		if _beacon != null:
			_beacon.beacon_up.connect(_on_beacon_up)
			_beacon.beacon_taken.connect(_on_beacon_taken)


func _on_beacon_up() -> void:
	_push_feed("The beacon is up", GOLD)


func _on_beacon_taken(team: String) -> void:
	_push_feed("%s took the beacon" % team.capitalize(), MatchTeams.COLOURS.get(team, WHITE))


## The plaza beacon's row under the wave timer: its countdown in the last 30 s before it comes up, then
## "BEACON UP" with a blinking mark (and a fill line in the taker's colour while a team takes it). Hidden
## otherwise. True when it drew, so the near-structure bar moves down a row.
func _beacon_row(cx: float) -> bool:
	if _beacon == null or not is_instance_valid(_beacon):
		return false
	var s := ""
	var col: Color = GOLD
	var taking: bool = _beacon.active and _beacon.capturing != "" and _beacon.progress > 0.0
	if _beacon.active:
		s = "BEACON UP"
		if taking:
			col = _rel(_beacon.capturing)
	elif _beacon.up_in() <= BEACON_WARN:
		s = "BEACON " + _mmss(ceilf(_beacon.up_in()))
	else:
		return false
	var wide := _tw(s) + 7
	var x := cx - floorf(wide / 2.0)
	var blink: bool = _beacon.active and fmod(director.elapsed, 0.6) < 0.3
	_glyph(Vector2(x, 21), BEACON_GLYPH, col.lightened(0.4) if blink else col)
	_text(_canvas, Vector2(x + 7, 21), s, col, 2)
	if taking:
		_canvas.draw_rect(Rect2(x, 27, wide, 1), EDGE)
		_canvas.draw_rect(Rect2(x, 27, floorf(wide * _beacon.progress), 1), col)
	return true


## Seconds a structure stays switched off by the beacon (game feel's MatchStructure.off_left; 0 without it).
func _off(s) -> float:
	var v = s.get("off_left") if s != null else null
	return float(v) if v != null else 0.0


func _push_feed(text: String, colour: Color) -> void:
	_feed.push_front({"text": text, "colour": colour, "t": 0.0})
	if _feed.size() > 5:
		_feed.pop_back()


func _on_pit_taken(team: String, p: ArenaPit) -> void:
	var what := "back its pit" if p.home_team == team else "the %s pit" % p.home_team
	_feed.push_front({"text": "%s took %s" % [team.capitalize(), what], "colour": MatchTeams.COLOURS.get(team, WHITE), "t": 0.0})
	if _feed.size() > 5:
		_feed.pop_back()


func _near_structure() -> MatchStructure:
	var p: Node3D = director.player
	var best: MatchStructure = null
	var best_d := NEAR_STRUCTURE
	for s: MatchStructure in director.structures.values():
		if not s.alive or (s.team == p.team and s.hp >= s.max_hp):
			continue  # your own structures only once they are hurt: at base the full core bar is noise
		var d := MatchTeams.flat(s.global_position - p.global_position).length()
		if d < best_d:
			best_d = d
			best = s
	return best


func _side(team_is_own: bool) -> Array:
	var p: Node3D = director.player
	var out: Array = []
	for m: Node3D in director.machines:
		if not is_instance_valid(m) or m == p:
			continue
		if (m.team == p.team) == team_is_own:
			out.append(m)
	return out


func _respawn_secs(m: Node3D) -> int:
	return ceili(maxf(float(director.respawn_at.get(m, director.elapsed)) - director.elapsed, 0.0))


func _allies_and_feed() -> void:
	var allies := _side(true)
	for i in allies.size():
		var m: Node3D = allies[i]
		var y := 3.0 + i * 17.0
		var kind := MatchTeams.machine_kind(m)
		_plate(Rect2(3, y, 42, 15), false, false)
		_portrait(Vector2(4, y + 1), 13, kind, ALLY, "" if m.alive else "down", _respawn_secs(m))
		_pbar(Rect2(19, y + 5, 18, 3), m.hp / m.max_hp if m.alive else 0.0, ALLY)
		var total := MatchRules.cooldown(kind, "4")
		var left := float(m.cooldowns.get("4", 0.0))
		_diamond(Vector2(39, y + 4), 1.0 - (left / total if total > 0.0 else 0.0))
	var fy := 3.0 + allies.size() * 17.0 + 4.0
	for f in _feed:
		var a := clampf(7.0 - float(f["t"]), 0.0, 1.0)
		var s := String(f["text"])
		_canvas.draw_rect(Rect2(3, fy - 1, _tw(s) + 4, 7), Color(0, 0, 0, 0.45 * a))
		var col: Color = f["colour"]
		col.a = a
		_text(_canvas, Vector2(5, fy), s, col)
		fy += 8.0


func _enemies(vs: Vector2) -> void:
	var foes := _side(false)
	if foes.is_empty():
		return
	var ex := vs.x - 3.0 - (foes.size() * 15.0 - 2.0)
	_plate(Rect2(ex - 1, 2, foes.size() * 15.0, 15), false, false)
	for i in foes.size():
		var m: Node3D = foes[i]
		var state := ""
		if not m.alive:
			state = "down"
		elif m.hp / m.max_hp < LOW_HP and director.team_sees(director.player.team, m):
			state = "low"
		_portrait(Vector2(ex + i * 15.0, 3), 13, MatchTeams.machine_kind(m), ENEMY, state, _respawn_secs(m))


func _bar_rect(vs: Vector2) -> Rect2:
	return Rect2(floorf(vs.x / 2.0) - 62.0, vs.y - 31.0, 124, 29)


func _player_bar(vs: Vector2) -> void:
	var p: Node3D = director.player
	var r := _bar_rect(vs)
	_plate(r, true)
	var kind := MatchTeams.machine_kind(p)
	_portrait(r.position + Vector2(3, 5), 21, kind, GREEN, "" if p.alive else "down", _respawn_secs(p))
	var hx := r.position.x + 27.0
	var hw := 93.0
	var s := "%d/%d" % [ceili(maxf(p.hp, 0.0)), int(p.max_hp)]
	var share: float = p.hp / maxf(p.max_hp, 1.0)
	var col := GREEN
	if p.alive and share < LOW_HP:
		col = GREEN.lerp(ENEMY, 0.5 + 0.5 * sin(director.elapsed * TAU * 1.5))
	_pbar(Rect2(hx, r.position.y + 4, hw - _tw(s) - 3, 7), share, col)
	_text(_canvas, Vector2(hx + hw - _tw(s), r.position.y + 5), s, WHITE)
	var names: Array = SLOT_NAMES.get(kind, ["", "", "", ""])
	var sy := r.position.y + 14.0
	for i in 4:
		var slot := str(i + 1)
		_slot(Vector2(hx + i * 16.0, sy), 13, slot, ICON_OF.get(names[i], ""), float(p.cooldowns.get(slot, 0.0)),
				MatchRules.cooldown(kind, slot), float(_flash.get(slot, 0.0)), false, names[i] == "none")
	_slot(Vector2(hx + 66, sy + 2), 11, "SP", "", p.attack_cd, director.basic_cooldown_of(p), 0.0, true) # each kit's own basic (game feel, 2026-11-05)
	_slot(Vector2(hx + 80, sy + 2), 11, "B", "", 0.0, 0.0, 0.0, true)
	var rec := float(director.recalls.get(p, -1.0))
	if rec >= 0.0:
		_canvas.draw_rect(Rect2(hx + 80, sy + 11, 11.0 * clampf(rec / MatchRules.recall_time, 0.0, 1.0), 2), GREEN)
	if warning and fmod(director.elapsed, 0.5) < 0.34:
		_glyph(r.position + Vector2(18, -4), WARN, ENEMY)


func _kda_panel(vs: Vector2) -> void:
	var r := Rect2(3, vs.y - 13.0, 52, 10)
	_plate(r, false, false)
	_text(_canvas, r.position + Vector2(2, 2), "%d/%d/%d" % _kda, WHITE)
	_text(_canvas, Vector2(r.end.x - 2 - _tw("KDA"), r.position.y + 2), "KDA", DIM)


func _middle_back(vs: Vector2) -> void:
	var p: Node3D = director.player
	var cam := _canvas.get_viewport().get_camera_3d()
	var s := director.player_targeted_by()
	if s != null and cam != null and p.alive:
		var a := s.global_position + Vector3.UP * 3.2
		var b: Vector3 = p.global_position + Vector3.UP * MACHINE_BAR_TILTED * p.sprite.size_scale()
		if not cam.is_position_behind(a) and not cam.is_position_behind(b):
			var sa := cam.unproject_position(a)
			var sb := cam.unproject_position(b) - Vector2(0, 3)
			sa.y = maxf(sa.y, 34.0)
			var n := mini(int(maxf(absf(sb.x - sa.x), absf(sb.y - sa.y))), 600)  # capped: a point near the camera plane projects far off screen
			for i in n + 1:
				if (i >> 1) % 2 == 0:
					var t := float(i) / maxf(n, 1)
					_px(roundf(lerpf(sa.x, sb.x, t)), roundf(lerpf(sa.y, sb.y, t)), ENEMY)
	if p.alive and p.hp / maxf(p.max_hp, 1.0) < LOW_HP:
		var pulse := 0.6 + 0.4 * sin(director.elapsed * TAU * 1.5)
		for i in 5:
			var c := Color(1.0, 0.15, 0.1, (0.16 - i * 0.03) * pulse)
			_canvas.draw_rect(Rect2(0, i, vs.x, 1), c)
			_canvas.draw_rect(Rect2(0, vs.y - 1 - i, vs.x, 1), c)
			_canvas.draw_rect(Rect2(i, 0, 1, vs.y), c)
			_canvas.draw_rect(Rect2(vs.x - 1 - i, 0, 1, vs.y), c)


func _middle_front(vs: Vector2) -> void:
	var p: Node3D = director.player
	if not p.alive and director.winner == "":
		_canvas.draw_rect(Rect2(Vector2.ZERO, vs), Color(0, 0, 0, 0.35))
		_centred(vs, 62, "DESTROYED", ENEMY, 1, 2)
		_centred(vs, 80, "BACK AT BASE IN %d" % _respawn_secs(p), WHITE, 1)
	if director.recalls.has(p):
		var k: float = director.recalls[p] / MatchRules.recall_time
		_centred(vs, 108, "RECALLING", WHITE, 1)
		_canvas.draw_rect(Rect2(floorf(vs.x / 2.0) - 29, 115, 58, 5), EDGE)
		_pbar(Rect2(floorf(vs.x / 2.0) - 28, 116, 56, 3), k, ALLY)
	if director.winner != "":
		_canvas.draw_rect(Rect2(Vector2.ZERO, vs), Color(0, 0, 0, 0.55))
		var won: bool = director.winner == p.team
		_centred(vs, 62, "VICTORY" if won else "DEFEAT", GREEN if won else ENEMY, 1, 4)
		var loser := "red" if director.winner == "blue" else "blue"
		_centred(vs, 90, "%s CORE DESTROYED.  ENTER: PLAY AGAIN" % loser, WHITE, 1)


func _centred(vs: Vector2, y: float, s: String, col: Color, style := 1, k := 1) -> void:
	_text(_canvas, Vector2(floorf((vs.x - _tw(s) * k) / 2.0), y), s, col, style, k)


func _panels(vs: Vector2) -> Array:
	if _map_rect.size == Vector2.ZERO and director.arena != null:
		var layer_node := director.arena.find_child("Minimap", true, false)
		var map: Control = layer_node.get_node_or_null("Map") if layer_node != null else null
		if map != null:
			_map_rect = Rect2(map.position, map.size)
	var out := [_bar_rect(vs).grow(1.0), Rect2(2, vs.y - 14.0, 54, 12)]
	if _map_rect.size != Vector2.ZERO:
		out.append(_map_rect.grow(1.0))
	return out


func _paint_aim() -> void:
	var p: Node3D = director.player if director != null else null
	if p == null or not p.has_method("aim_point"):
		return
	if not p.has_method("aim_marker_visible") or not p.aim_marker_visible():  # the game feel lane's public flag
		return
	var cam := _over.get_viewport().get_camera_3d()
	if cam == null:
		return
	var aim: Vector3 = p.aim_point()
	if cam.is_position_behind(aim):
		return
	var sp := cam.unproject_position(aim)
	var under := false
	for r: Rect2 in _panels(_over.size):
		if r.has_point(sp):
			under = true
	if not under:
		return
	var feet := cam.unproject_position(p.global_position)
	var rad := maxf((cam.unproject_position(aim + cam.global_basis.x * 0.38) - sp).length(), 3.0)
	_over.draw_line(feet, sp, Color(1, 1, 1, 0.75), 1.0)
	_over.draw_arc(sp, rad, 0.0, TAU, 24, Color(0, 0, 0, 0.6), 2.0)
	_over.draw_arc(sp, rad, 0.0, TAU, 24, Color(1, 1, 1, 0.95), 1.0)


func _paint_bars() -> void:
	if director == null or director.player == null:
		return
	var cam := _bars.get_viewport().get_camera_3d()
	if cam == null:
		return
	var vs := _bars.size
	for u: Node3D in get_tree().get_nodes_in_group("match_unit"):
		_world_bar(cam, u, vs)


func _bar(r: Rect2, share: float, col: Color) -> void:
	_bars.draw_rect(r.grow(1.0), Color(0, 0, 0, 0.75))
	_bars.draw_rect(Rect2(r.position, Vector2(r.size.x * clampf(share, 0.0, 1.0), r.size.y)), col)


func _label(pos: Vector2, s: String, size: int, col: Color) -> void:
	_bars.draw_string(_font, pos + Vector2(1, 1), s, HORIZONTAL_ALIGNMENT_LEFT, -1.0, size, Color(0, 0, 0, col.a * 0.8))
	_bars.draw_string(_font, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1.0, size, col)


func _unit_colour(u: Node3D) -> Color:
	if u == director.player:
		return GREEN
	var t := MatchTeams.team_of(u)
	if t == "":
		return MatchTeams.COLOURS[""]
	return MatchTeams.COLOURS["blue"] if t == director.player.team else MatchTeams.COLOURS["red"]


func _world_bar(cam: Camera3D, u: Node3D, vs: Vector2) -> void:
	if u.get("alive") != true or not u.is_visible_in_tree() or u.get("seen") == false:
		return
	var k := str(u.get("kind"))
	var h := 1.3
	var w := 30.0
	var t := 4.0
	match k:
		"machine":
			h = (MACHINE_BAR_TILTED if u.sprite.tilts_any() else 1.9) * u.sprite.size_scale()
			w = 64.0
			t = 6.0
		"monster":
			h = 1.9
			w = 44.0
			t = 5.0
		"tower", "core":
			h = 4.2 if k == "tower" else 4.4
			w = 90.0 if k == "tower" else 110.0
			t = 7.0
	if k == "minion" and u.has_method("bar_height"):
		h = u.bar_height()
	var at := u.global_position + Vector3.UP * h
	if cam.is_position_behind(at):
		return
	var sp := cam.unproject_position(at) / _k
	if sp.x < -w or sp.x > vs.x + w or sp.y < -10.0 or sp.y > vs.y:
		return
	var col := _unit_colour(u)
	if k == "core" and not u.can_be_hit():
		col = col.darkened(0.55)
	_bar(Rect2(sp.x - w / 2.0, sp.y, w, t), u.hp / u.max_hp, col)
	if _off(u) > 0.0: # switched off by the plaza beacon
		_label(Vector2(sp.x - w / 2.0, sp.y - 4.0), "OFF %d" % ceili(_off(u)), 14, Color(1, 1, 1, 0.9))
	if k == "machine" and u != director.player:
		_label(Vector2(sp.x - w / 2.0, sp.y - 3.0), MatchTeams.machine_kind(u), 11, col.lightened(0.25))
