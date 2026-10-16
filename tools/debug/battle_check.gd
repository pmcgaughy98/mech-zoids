extends SceneTree
## Plays 200 seeded battles per setup with the real battle rules and reports what decides them.
## Proves every battle ends, and that the deck and Charge change who wins.
## Run: Godot --headless --path . --script res://tools/debug/battle_check.gd

const Logic := preload("res://scripts/battle/battle_logic.gd")
const Commands := preload("res://scripts/data/commands.gd")

const SEEDS := 200
var fails := 0


func _initialize() -> void:
	print("battle_check: Lion type (player) vs Raptor type (enemy), %d seeds each" % SEEDS)
	var rates := {}
	for policy in ["basic", "deck", "charge", "smart"]:
		rates[policy] = _series(policy, "smart")
	var mirror: int = rates.smart
	print("\nbattle_check: Lion type vs Hawk type (flyer), canyon battle")
	var flyer_deck := ["shield_wall", "power_surge"]
	var without := _series("smart", "smart", "hawk_s", Commands.STARTER_DECK, flyer_deck)
	var with_lock := _series("smart", "smart", "hawk_s", Commands.STARTER_DECK + ["air_lock"], flyer_deck)
	print("")
	_ok("every battle ended by a knockout, none by the %d-round stop" % Logic.MAX_ROUNDS, _timeouts == 0)
	_ok("the deck alone wins more than plain attacks (%d%% vs %d%%)" % [rates.deck, rates.basic], rates.deck > rates.basic)
	_ok("Charge alone wins more than plain attacks (%d%% vs %d%%)" % [rates.charge, rates.basic], rates.charge > rates.basic)
	_ok("deck and Charge together win the most (%d%%)" % rates.smart, rates.smart >= max(rates.deck, rates.charge))
	_ok("smart vs smart is not a walkover for either side (player wins %d%%)" % mirror, mirror >= 20 and mirror <= 80)
	_ok("Air Lock, the first battle's reward, helps against the flyer (%d%% vs %d%%)" % [with_lock, without],
		with_lock >= without + 10)
	_ok("the canyon is winnable but not a walkover with Air Lock (%d%%)" % with_lock, with_lock >= 30 and with_lock <= 85)
	print("\nbattle_check: %s" % ("PASS" if fails == 0 else "FAIL (%d)" % fails))
	quit(1 if fails > 0 else 0)


var _timeouts := 0


## Plays SEEDS battles; returns the player's win rate in percent and prints averages.
func _series(player_policy: String, enemy_policy: String, enemy := "raptor_s",
		player_deck: Array = Commands.STARTER_DECK, enemy_deck: Array = Commands.STARTER_DECK) -> int:
	var wins := 0
	var rounds := 0
	var commands := 0
	var charges := 0
	for s in SEEDS:
		var b := Logic.new()
		b.setup(["lion_m"], [enemy], player_deck, enemy_deck, 1000 + s)
		while b.winner == "":
			var u := b.begin_turn()
			if u.is_empty():
				break
			var c := b.choose(u, player_policy if u.side == "player" else enemy_policy)
			if c.command != "":
				b.play_command(u, c.command)
			b.do_action(u, c)
		if b.round_no >= Logic.MAX_ROUNDS:
			_timeouts += 1
		wins += 1 if b.winner == "player" else 0
		rounds += b.round_no
		commands += b.stats.commands
		charges += b.stats.charges
	var rate := int(round(100.0 * wins / SEEDS))
	print("  player %-6s vs enemy %-6s  player wins %3d%%   avg rounds %.1f   commands %.1f   charges %.1f" % [
		player_policy, enemy_policy, rate, float(rounds) / SEEDS, float(commands) / SEEDS, float(charges) / SEEDS])
	return rate


func _ok(what: String, good: bool) -> void:
	print("  %s  %s" % ["ok  " if good else "FAIL", what])
	if not good:
		fails += 1
