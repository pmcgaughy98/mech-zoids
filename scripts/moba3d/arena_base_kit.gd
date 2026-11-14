extends Node
## Explicit test basic only. Unfinished models do not borrow another animal's kit.
var current:=""
var basic_range:=6.0
var basic_cooldown:=.9
var basic_damage:=30.0
static func install(player: Node3D) -> void:
	var old:=player.get_node_or_null("Kit")
	if old!=null:player.remove_child(old);old.queue_free()
	player.sprite.stop_action()
	var kit: Node=load("res://scripts/moba3d/arena_base_kit.gd").new()
	kit.name="Kit";player.add_child(kit)
func basic_attack(target: Node3D=null) -> bool:
	var p:=get_parent() as Node3D
	if p.busy or not p.alive or p.has_meta("held_by"):return false
	if target==null:
		for n in MatchTeams.enemies_of(p):
			if MatchTeams.hittable(n) and MatchTeams.edge_distance(p,n)<=basic_range and MatchTeams.clear_line(p,p.global_position,n.global_position):
				target=n;break
	if not MatchTeams.hittable(target):return false
	p.facing=MatchTeams.flat(target.global_position-p.global_position).normalized()
	var shot:=TestShot.fire(p.get_parent(),p.global_position,target.global_position,p.team=="red",target)
	shot.team=p.team;shot.source=p;shot.hp_damage=basic_damage;shot.reach=basic_range+3
	if p.body!=null:p.body.nudge(-p.facing*.04,.13)
	return true
