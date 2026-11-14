extends TrainingDummy
## A wounded ally for the hummingbird's field test (hummingbird mech session, 2026-11-05): a training dummy on the
## player's side (group kit_ally, tinted blue) with match-style health and its number over its head, so heals show.
## Outside a match, MatchTeams.allies_of() returns the kit_ally group.

signal healed(amount: float, by: Node3D)

var max_hp := 600.0 ## MatchRules.machine_hp
var hp := 300.0 ## starts at half, so there is room to heal
var alive := true
var _label: Label3D


func _ready() -> void:
	super._ready()
	remove_from_group("kit_target")
	add_to_group("kit_ally")
	tint = MatchTeams.COLOURS["blue"]
	_label = Label3D.new()
	_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_label.pixel_size = 0.008
	_label.font_size = 48
	_label.outline_size = 12
	_label.no_depth_test = true
	_label.position.y = 2.0
	add_child(_label)


func _process(delta: float) -> void:
	super._process(delta)
	_label.text = "%s  %d / %d" % [name, roundi(hp), roundi(max_hp)]
	_label.modulate = Color(0.6, 1.0, 0.6) if hp >= max_hp else Color.WHITE


func radius() -> float:
	return BODY_R


## The same contract as machine_test_player.heal(): up to max_hp, returns what landed, healed only when it did.
func heal(amount: float, by: Node3D = null) -> float:
	if not alive or max_hp <= 0.0:
		return 0.0
	var before := hp
	hp = minf(hp + amount, max_hp)
	if hp > before:
		healed.emit(hp - before, by)
	return hp - before
