extends Node2D
## The battle screen. Draws the machines, gauges, messages and the player's menu, and plays back the rules'
## result queue one step at a time. All the rules live in scripts/battle/battle_logic.gd.
##
## Controls: up/down to choose, Z/Enter to pick, X/Esc to go back.

const Slot := preload("res://scripts/ui/slot.gd")
const Logic := preload("res://scripts/battle/battle_logic.gd")
const Commands := preload("res://scripts/data/commands.gd")
const Machines := preload("res://scripts/data/machines.gd")
const Anim := preload("res://scripts/ui/machine_anim.gd")
const Items := preload("res://scripts/data/items.gd")
const Economy := preload("res://scripts/game/economy.gd")
const Stage := preload("res://scripts/battle/stage.gd")
const Vfx := preload("res://scripts/battle/vfx.gd")
const Recipes := preload("res://scripts/battle/vfx_recipes.gd")

# Legacy-style staging (animation pass 3, 2026-10-12): the player's machine front-left and low, the enemy
# back-right and higher; the feet rows, the zoomed-out field and the fit-to-screen rules live in
# scripts/battle/stage.gd (2026-10-15). Gauges live in the bottom panel. Each attack (2026-10-15, Preston: "fix up the
# battle scenes ... adding VFX's"): the text line first, then the attacker's clip with its weapon's effects from
# scripts/battle/vfx_recipes.gd (a melee attacker crosses to the target, a shot or beam flies); at the impact the
# target blinks white, both machines freeze for an instant, the target shakes and is knocked back, and the digits
# hop up while the health bar drains (act, then show).

const STEP_TIME := 0.7       # seconds each result step stays up
const AUTO_STEP_TIME := 0.02  # on autopilot

var logic := Logic.new()
var current: Dictionary = {}
var state := "next"          # next, turn, playback, menu, commands, done
var after_playback := "next"
var wait := 0.0
var cursor := 0
var gauges: Array = []       # per unit: {hp, ep, hp_text}
var sprites: Array = []
var message: Label
var menu_rows: Array = []
var formation: Dictionary = {}   # the formation strip's labels, by side
var staged_player := -1
var staged_enemy := -1
var menu_items: Array = []   # {text, enabled, act}
var exit_scene := "base"
var stage_root: Node2D       # background + field; the screen shake moves it
var field: Node2D            # machines and effects, zoomed out (Stage.field_scale)
var field_s := 1.0
var fx: Vfx                  # scripts/battle/vfx.gd: the effect layers and the effects themselves
var layout_dirty := false    # the window changed size; re-placed between steps, never mid-move


func _ready() -> void:
	var req: Dictionary = Run.battle_request
	if req.is_empty():  # opened on its own in the editor: a test fight
		if Run.deck.is_empty():
			Run.new_game()
		req = {"player": ["ape_l"], "enemy": ["hippo_m"], "enemy_deck": Commands.STARTER_DECK, "flag": "",
			"reward": "", "win_scene": "title"}
		Run.battle_request = req
	var seed_value := Run.battle_seed if Run.autopilot else randi()
	Run.battle_seed += 1
	logic.setup(req.player, req.enemy, [] if req.get("ban_commands", false) else Run.deck, req.enemy_deck, seed_value)
	_build()
	_show_snap(logic.queue[0].snap if logic.queue.size() > 0 else [])


func _build() -> void:
	# the stage (background, machines, effects) shakes; the panel below it does not
	stage_root = Node2D.new()
	stage_root.name = "stage"
	add_child(stage_root)
	var bg := Slot.make("res://art/battle/background.png", Vector2i(320, 180), Color("23262b"), "")
	stage_root.add_child(bg)
	if ResourceLoader.exists("res://art/battle/background.png"):   # mirrored edges: a shaken stage shows no gap
		for side in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1)]:
			var m := Sprite2D.new()
			m.texture = load("res://art/battle/background.png")
			m.centered = false
			m.flip_h = side.x != 0
			m.flip_v = side.y != 0
			m.position = side * Vector2(320, 180)
			bg.add_child(m)
	var ground := ColorRect.new()
	ground.position = Vector2(0, 92)
	ground.size = Vector2(320, 30)
	ground.color = Color("3a3f2c")
	if not ResourceLoader.exists("res://art/battle/background.png"):
		stage_root.add_child(ground)
	else:
		ground.free()
	# the zoomed-out field (scripts/battle/stage.gd): effects behind the machines, the machines, effects in front
	field = Node2D.new()
	field.name = "field"
	stage_root.add_child(field)
	fx = Vfx.new()
	fx.setup(field, stage_root, bg, Run.battle_seed)
	sprites.resize(logic.units.size())
	for pass_side in ["enemy", "player"]:   # the enemy is drawn first, so the player's machine stands in front
		for i in logic.units.size():
			var u: Dictionary = logic.units[i]
			if u.side != pass_side:
				continue
			var left: bool = u.side == "player"
			var s := Anim.machine(u.id, not left)
			s.set_meta("is_player", left)
			Vfx.prepare_flash(s)
			field.add_child(s)
			sprites[i] = s
	fx.front = Node2D.new()
	fx.front.name = "fx_front"
	field.add_child(fx.front)
	_layout()
	get_window().size_changed.connect(func() -> void: layout_dirty = true)
	var panel := ColorRect.new()
	panel.position = Vector2(0, 124)
	panel.size = Vector2(320, 56)
	panel.color = Color(0.05, 0.07, 0.12, 0.95)
	add_child(panel)
	for i in logic.units.size():
		var u: Dictionary = logic.units[i]
		var x := 180 if u.side == "player" else 246   # below the message line, clear of the menu rows
		var name_label := Slot.text(u.name, Vector2(x, 137))
		add_child(name_label)
		var g := {"hp": _bar(Vector2(x, 148), Color("3ecf5a")), "ep": _bar(Vector2(x, 154), Color("1e90ff")), "name": name_label}
		g["text"] = Slot.text("", Vector2(x, 158), Color(1, 1, 1, 0.8))
		add_child(g["text"])
		gauges.append(g)
	# the formation strip: every machine by row, health in percent, the one acting marked
	formation = {"player": Slot.text("", Vector2(4, 2), Color(1, 1, 1, 0.85)), "enemy": Slot.text("", Vector2(164, 2), Color(1, 1, 1, 0.85))}
	add_child(formation.player)
	add_child(formation.enemy)
	_stage(_first("player"), _first("enemy"))
	message = Slot.text("", Vector2(6, 125), Color("ffd400"))
	add_child(message)
	for i in 4:
		var l := Slot.text("", Vector2(10, 136 + i * 10))
		menu_rows.append(l)
		add_child(l)


## Scales the field for the window (whole screen pixels per art pixel) and stands every machine at its home (a
## destroyed one where its death pose fits). A resize waits for the gap between steps (layout_dirty), since the
## moves in flight end at positions worked out at the old scale.
func _layout() -> void:
	layout_dirty = false
	field_s = Stage.field_scale(Stage.window_scale(get_window().size))
	field.scale = Vector2(field_s, field_s)
	for i in sprites.size():
		var s: Node2D = sprites[i]
		var left: bool = s.get_meta("is_player")
		s.position = Vector2(Stage.home_x(s, left, field_s), Stage.home_y(s, left, field_s))
		s.set_meta("home_y", s.position.y)
		if logic.units[i].hp <= 0:
			s.position.y = Stage.clip_y(s, left, "death", field_s)


## The first machine of a side still standing, front line first.
func _first(side: String) -> int:
	var f: Array = logic.front_line(side)
	return logic.units.find(f[0]) if not f.is_empty() else -1


## The big stage shows one machine a side: `a` and `b` (unit indices, either order); the rest wait off stage.
func _stage(a: int, b: int) -> void:
	var pi := a if a >= 0 and logic.units[a].side == "player" else b
	var ei := a if a >= 0 and logic.units[a].side == "enemy" else b
	if pi < 0 or logic.units[pi].side != "player":
		pi = staged_player if staged_player >= 0 else _first("player")
	if ei < 0 or logic.units[ei].side != "enemy":
		ei = staged_enemy if staged_enemy >= 0 else _first("enemy")
	staged_player = pi
	staged_enemy = ei
	for i in logic.units.size():
		var on := i == pi or i == ei
		sprites[i].visible = on
		gauges[i].hp.get_parent().visible = on
		gauges[i].ep.get_parent().visible = on
		gauges[i].text.visible = on
		gauges[i].name.visible = on


func _formation_text(side: String, snap: Array) -> String:
	var rows := {"front": [], "back": []}
	for i in logic.units.size():
		var u: Dictionary = logic.units[i]
		if u.side != side:
			continue
		var hp: int = snap[i][0] if i < snap.size() else u.hp
		var tag: String = u.name.split(" ")[0].left(5)
		var mark := "*" if not current.is_empty() and logic.units[i] == current else ""
		rows[u.get("row", "front")].append(("x" + tag) if hp <= 0 else "%s%s %d%%" % [mark, tag, int(100.0 * hp / u.max_hp)])
	if rows.front.size() + rows.back.size() < 2:   # a lone machine needs no strip
		return ""
	return "F  %s" % "  ".join(rows.front) + ("\nB  %s" % "  ".join(rows.back) if not rows.back.is_empty() else "")


func _bar(pos: Vector2, color: Color) -> ColorRect:
	var back := ColorRect.new()
	back.position = pos
	back.size = Vector2(62, 4)
	back.color = Color(0, 0, 0, 0.6)
	add_child(back)
	var fill := ColorRect.new()
	fill.size = back.size
	fill.color = color
	back.add_child(fill)
	return fill


## The formation strip, with the machine whose turn it is marked (live gauges: the queue has played out by then).
func _show_formation() -> void:
	if not formation.has("player"):
		return
	var snap := []
	for u in logic.units:
		snap.append([u.hp, u.ep])
	formation.player.text = _formation_text("player", snap)
	formation.enemy.text = _formation_text("enemy", snap)


## `drain`: a falling health bar runs down instead of jumping (the Pokemon GBA games drain it after the blow).
func _show_snap(snap: Array, drain := false) -> void:
	if formation.has("player"):
		formation.player.text = _formation_text("player", snap)
		formation.enemy.text = _formation_text("enemy", snap)
	for i in snap.size():
		var u: Dictionary = logic.units[i]
		var hp_w: float = 62.0 * snap[i][0] / u.max_hp
		if gauges[i].has("drain"):
			gauges[i].drain.kill()
			gauges[i].erase("drain")
		if drain and hp_w < gauges[i].hp.size.x:
			gauges[i].drain = create_tween()
			gauges[i].drain.tween_property(gauges[i].hp, "size:x", hp_w, 0.45)
		else:
			gauges[i].hp.size.x = hp_w
		gauges[i].ep.size.x = 62.0 * snap[i][1] / u.max_ep
		gauges[i].text.text = "%d/%d  EP %d" % [snap[i][0], u.max_hp, snap[i][1]]
		if sprites[i].get_node_or_null("anim") == null:   # animated machines play their defeat clip instead
			sprites[i].modulate.a = 0.25 if snap[i][0] <= 0 else 1.0


func _process(delta: float) -> void:
	match state:
		"playback":
			wait -= delta
			if wait > 0.0:
				return
			if layout_dirty:
				_layout()
			if logic.queue.is_empty():
				state = after_playback
				return
			var step: Dictionary = logic.queue.pop_front()
			message.text = step.text
			if step.get("actor", -1) >= 0 and step.unit >= 0:
				_stage(step.actor, step.unit)
			elif step.unit >= 0:
				_stage(step.unit, -1)
			if step.get("actor", -1) >= 0 and step.kind in ["damage", "miss"] and not Run.autopilot:
				wait = _play_attack(step)
				return
			_show_snap(step.snap)
			if step.kind == "damage" and step.unit >= 0:
				_hit_target(step)
			elif step.kind == "item" and step.unit >= 0:
				if not Run.autopilot:
					fx.repaired(sprites[step.unit])
				_pop_text(step.unit, "+%d" % step.value, Color("7cff9a"))
			elif step.kind == "charge" and step.unit >= 0 and not Run.autopilot:
				fx.charging(sprites[step.unit])
				wait = maxf(STEP_TIME, 1.0)   # the light drawn in, then the sparkle
				return
			elif step.kind == "destroyed" and step.unit >= 0:
				_step_down(sprites[step.unit], "death", 0.0, true)
				Anim.play(sprites[step.unit], "death")
				if not Run.autopilot:   # it goes out in a string of blasts, so the step holds for them
					wait = maxf(STEP_TIME, fx.destroyed(sprites[step.unit]))
					return
			wait = AUTO_STEP_TIME if Run.autopilot else STEP_TIME
		"next":
			current = logic.begin_turn()
			_play_then("turn" if not current.is_empty() else "done")
		"turn":
			if layout_dirty:
				_layout()
			_show_formation()
			if logic.winner != "" or current.is_empty() or current.hp <= 0:
				state = "next" if logic.winner == "" else "done"
			elif current.side == "player" and not Run.autopilot:
				_stage(logic.units.find(current), logic.units.find(logic.foe_of(current)))
				_open_menu()
			else:
				var policy := "idle" if (current.side == "player" and Run.autopilot_lose) else "smart"
				var choice := logic.choose(current, policy)
				if choice.command != "":
					logic.play_command(current, choice.command)
				logic.do_action(current, choice)
				_play_then("next")
		"done":
			state = "finished"
			_finish()


## The attacker's clip (or a lunge for art without one) with its weapon's effects (scripts/battle/vfx.gd plays the
## recipe: the crossing, the shot, the impact and the target's reaction). The damage shows at the impact, after a
## shot's flight. Returns how long playback should hold this step.
func _play_attack(step: Dictionary) -> float:
	var actor: Node2D = sprites[step.actor]
	var target: Node2D = sprites[step.unit]
	var is_player: bool = actor.get_meta("is_player")
	var times: Array = Anim.clip_times(actor, step.clip)
	var home := Vector2(Stage.home_x(actor, is_player, field_s), actor.get_meta("home_y"))
	var base_y := float(Stage.clip_y(actor, is_player, step.clip, field_s))
	var recipe := Recipes.find(logic.units[step.actor].id, step.clip, step.get("wtype", "melee"))
	if not Anim.play(actor, step.clip):
		var t := create_tween()
		t.tween_property(actor, "position:x", home.x + 14.0 * actor.scale.x, 0.12)
		t.tween_property(actor, "position:x", home.x, 0.25)
	var hit: bool = step.kind == "damage"
	var max_y := float(roundi(Stage.PLAYER_FEET_Y / field_s) - int(actor.get_meta("feet_y")))
	var impact := fx.play_attack(actor, target, step.clip, times, recipe, hit, home, base_y, max_y)
	fx.after(impact, func() -> void:
		_show_snap(step.snap, true)
		if hit:
			_pop_number(step.unit, step.value)
		else:
			_pop_text(step.unit, "Miss", Color(1, 1, 1)))
	return maxf(float(times[1]), impact + 0.5) + 0.4


## A machine too tall for its slot in `clip` steps down for it (Stage.clip_y: just enough to keep that clip on
## screen, never past the player's row) and stays down (death; attacks step down inside Vfx.play_attack). Between
## moves it stands at its home row, so the Legacy diagonal holds (2026-10-15).
func _step_down(node: Node2D, clip: String, hold: float, stay: bool) -> void:
	if not node.has_meta("home_y"):
		return
	var home: float = node.get_meta("home_y")
	var y := float(Stage.clip_y(node, node.get_meta("is_player"), clip, field_s))
	if y <= home:
		return
	var t := create_tween()
	t.tween_property(node, "position:y", y, Stage.STEP_TIME)
	if not stay:
		t.tween_interval(maxf(0.0, hold - Stage.STEP_TIME))
		t.tween_property(node, "position:y", home, 0.2)


## Damage shown without its attack (autopilot, or a blow from a command): the blink, the shake, the number.
func _hit_target(step: Dictionary) -> void:
	if not Run.autopilot:
		var target: Node2D = sprites[step.unit]
		fx.flash(target, Color.WHITE, [1.0, 1.0, 0.0, 0.8, 0.0])
		fx.jolt(target, 2.0)
		Anim.play(target, "hit")
	_pop_number(step.unit, step.value)


## The screen point above the middle of a machine's art between moves (the field is zoomed out; the numbers are not,
## and they stay still while the stage shakes).
func _screen_top(unit: int) -> Vector2:
	var s: Node2D = sprites[unit]
	var w: int = s.get_meta("width")
	return Vector2(s.position.x + w / 2.0 * s.scale.x, Stage.art_top(s)) * field_s


func _pop_text(unit: int, text: String, color: Color) -> void:
	var top := _screen_top(unit)
	# just under the art's visible top, and low enough that the 14-row rise stays on screen (2026-10-15: from the
	# canvas top, tall machines' numbers started above the screen and never showed)
	var y: float = maxf(16.0, top.y + 2)
	var l := Slot.text(text, Vector2(top.x - 6, y), color)
	add_child(l)
	var t := create_tween()
	t.tween_property(l, "position:y", y - 14, 0.6)
	t.parallel().tween_property(l, "modulate:a", 0.0, 0.6).set_delay(0.3)
	t.tween_callback(l.queue_free)


## Damage digits hop up one after another, settle, then fade (Zoids Legacy: each digit starts two frames after the
## last, hops 8 px over 8 frames and lives about 45 frames).
func _pop_number(unit: int, value: int) -> void:
	var top := _screen_top(unit)
	var text := str(value)
	var probe := Slot.text(text, Vector2.ZERO)
	var font := probe.get_theme_font("font")
	var widths: Array = []
	var total := 0.0
	for ch in text:
		widths.append(font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, 8).x)
		total += widths[-1]
	probe.free()
	var x := roundf(top.x - total / 2.0)
	var y: float = roundf(maxf(16.0, top.y + 2))
	for i in text.length():
		var l := Slot.text(text[i], Vector2(x, y), Color("ffd400"))
		x += widths[i]
		add_child(l)
		var t := create_tween()
		t.tween_interval(i * 2.0 / 60.0)
		t.tween_property(l, "position:y", y - 8, 4.0 / 60.0).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
		t.tween_property(l, "position:y", y, 4.0 / 60.0).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
		t.tween_interval(0.45)
		t.tween_property(l, "modulate:a", 0.0, 0.2)
		t.tween_callback(l.queue_free)


func _play_then(next_state: String) -> void:
	after_playback = next_state
	state = "playback"
	wait = 0.0


func _finish() -> void:
	var req: Dictionary = Run.battle_request
	var won := logic.winner == "player"
	# The scene you land in plays this talk: "after_<flag>" on a win, the tow-home talk on a loss.
	Run.last_battle = {"winner": logic.winner, "flag": req.flag,
		"dialogue": ("after_" + req.flag) if won else "debrief_loss"}
	Run.battles.append({"winner": logic.winner, "flag": req.flag, "rounds": logic.round_no,
		"commands": logic.stats.commands, "charges": logic.stats.charges})
	exit_scene = req.win_scene if won else "base"
	message.text = ("Victory! " if won else "Defeat. ") + "Press Z to continue."
	var awards: Array = Run.apply_battle_result(logic.units, logic.winner, req)   # experience, pulse, credits, cores
	if not awards.is_empty():
		message.text = ("Victory! " if won else "Defeat. ") + awards[0] + " Press Z."
	if won and req.flag != "":
		Run.set_flag(req.flag)
	if won and req.reward != "" and not Run.owned.has(req.reward):
		Run.give_command(req.reward)
		message.text = "Victory! New command: %s. Press Z." % Commands.COMMANDS[req.reward].name
	if Run.autopilot:
		Run.goto(exit_scene)
	else:
		state = "await_exit"


# --- The player's menu ----------------------------------------------------------------------------

func _open_menu() -> void:
	state = "menu"
	cursor = 0
	message.text = "%s: what now?" % current.name
	menu_items = []
	for i in current.weapons.size():
		var w: Dictionary = current.weapons[i]
		var reach := "" if logic.can_use(current, w) else "  (back row)"
		menu_items.append({"text": "%s  %s %d  EP %d%s" % [w.name, w.type, w.power, w.ep, reach],
			"enabled": logic._affordable(current, i), "act": {"kind": "attack", "weapon": i}})
	menu_items.append({"text": "Charge  +%d EP, brace" % (current.ep_regen * 3), "enabled": true, "act": {"kind": "charge"}})
	var left: int = logic.deck.player.size()
	menu_items.append({"text": "Deck command  (%d left)" % left, "enabled": logic.can_play_command("player"),
		"act": {"kind": "commands"}})
	var held := 0
	for id in Items.RECOVERY:
		held += int(Run.items.get(id, 0))
	menu_items.append({"text": "Items  (%d)" % held, "enabled": held > 0, "act": {"kind": "items"}})
	_draw_menu()


func _open_commands() -> void:
	state = "commands"
	cursor = 0
	menu_items = []
	for id in logic.deck.player:
		menu_items.append({"text": Commands.COMMANDS[id].name, "enabled": true, "act": {"kind": "command", "id": id}})
	_draw_menu()


## Which enemy a weapon hits, when more than one is in reach (melee: the front line only).
func _open_targets(weapon: int) -> void:
	state = "targets"
	cursor = 0
	menu_items = []
	for t in logic.valid_targets(current, current.weapons[weapon]):
		menu_items.append({"text": "%s  %d/%d  %s row" % [t.name, t.hp, t.max_hp, t.get("row", "front")], "enabled": true,
			"act": {"kind": "attack", "weapon": weapon, "target": logic.units.find(t)}})
	_draw_menu()


## Recovery items (scripts/data/items.gd): using one takes the turn.
func _open_items() -> void:
	state = "items"
	cursor = 0
	menu_items = []
	for id in Items.RECOVERY:
		if int(Run.items.get(id, 0)) > 0:
			menu_items.append({"text": "%s  x%d" % [Items.RECOVERY[id].name, Run.items[id]], "enabled": true, "act": {"kind": "item", "id": id}})
	_draw_menu()


func _draw_menu() -> void:
	# Show a window of 4 rows around the cursor.
	var start: int = clamp(cursor - 3, 0, max(0, menu_items.size() - 4))
	for r in menu_rows.size():
		var i: int = start + r
		if i >= menu_items.size():
			menu_rows[r].text = ""
			continue
		var item: Dictionary = menu_items[i]
		menu_rows[r].text = ("> " if i == cursor else "  ") + item.text
		menu_rows[r].modulate.a = 1.0 if item.enabled else 0.4
	if state == "commands" and menu_items.size() > 0:
		message.text = Commands.COMMANDS[menu_items[cursor].act.id].text
	elif state == "targets" and menu_items.size() > 0:
		message.text = "Target: %s" % logic.units[menu_items[cursor].act.target].name
		_stage(logic.units.find(current), menu_items[cursor].act.target)
	elif state == "items" and menu_items.size() > 0:
		message.text = Items.RECOVERY[menu_items[cursor].act.id].text


func _clear_menu() -> void:
	for r in menu_rows:
		r.text = ""


func _unhandled_input(event: InputEvent) -> void:
	if state == "await_exit" and event.is_action_pressed("ui_accept"):
		state = "leaving"
		Run.goto(exit_scene)
		return
	if state != "menu" and state != "commands" and state != "items" and state != "targets":
		return
	if event.is_action_pressed("ui_down"):
		cursor = (cursor + 1) % menu_items.size()
		_draw_menu()
	elif event.is_action_pressed("ui_up"):
		cursor = (cursor - 1 + menu_items.size()) % menu_items.size()
		_draw_menu()
	elif event.is_action_pressed("ui_cancel") and (state == "commands" or state == "items" or state == "targets"):
		_open_menu()
	elif event.is_action_pressed("ui_accept"):
		var item: Dictionary = menu_items[cursor]
		if not item.enabled:
			return
		match item.act.kind:
			"commands":
				_open_commands()
			"items":
				_open_items()
			"attack":
				if not item.act.has("target"):
					var ts: Array = logic.valid_targets(current, current.weapons[item.act.weapon])
					if ts.size() > 1:
						_open_targets(item.act.weapon)
						return
				_clear_menu()
				logic.do_action(current, item.act)
				_play_then("next")
			"item":
				var restored := Economy.use_on_unit(Run, item.act.id, current)
				logic.use_item(current, Items.RECOVERY[item.act.id].name, max(0, restored), "HP" if Items.RECOVERY[item.act.id].has("heal_pct") else "EP")
				_clear_menu()
				_play_then("next")
			"command":
				logic.play_command(current, item.act.id)
				_clear_menu()
				_play_then("menu_again")
			_:
				_clear_menu()
				logic.do_action(current, item.act)
				_play_then("next")


func _physics_process(_delta: float) -> void:
	# After a command plays back, the same machine still has its action.
	if state == "menu_again":
		_open_menu()
