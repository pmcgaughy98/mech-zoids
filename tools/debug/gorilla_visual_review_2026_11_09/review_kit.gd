extends "res://scripts/moba3d/ape_kit.gd"
var visuals: Node
func _make_aura() -> void:
	if visuals!=null:_aura=visuals.aura(player,aura_radius)
func _pulse(c: Vector3, r: float, life: float) -> void:
	if visuals!=null:visuals.pulse(c,r,life)
# Same current kit rules/values, with explicit interruption checks before each irreversible effect.
func chest_beat_ult() -> void:
	if not _begin("chest_beat"):return
	used.emit("4")
	var b:=_body("Ult")
	if b==null:
		_end()
		return
	_ult_body=b
	_play(b,"Ult")
	var id:=_ev_id
	for i in 3:
		if not await _wait_event(b,"Ult","beat",i+1):
			if _ev_id==id:_end()
			_ult_body=null
			return
		if _ev_id!=id or not player.alive or player.stunned>0:return
		if i<2:
			_pulse(feet(),ult_radius,.35 if i==0 else .25)
			impact.emit(.3 if i==0 else .15)
			for t in targets():
				if flat(t.global_position-feet()).length()<=ult_radius and t.has_method("taunt"):t.taunt(player,ult_taunt_time)
		else:
			var dome:=_raise_dome(feet(),ult_dome_radius,true)
			dome.ward=true
			dome.ward_owner=player
			dome.ward_heal_share=dome_ward_heal
	while is_instance_valid(b) and b.action=="Ult" and _ev_id==id:await get_tree().process_frame
	_ult_body=null
	if _ev_id==id:_end()
func abort_review() -> void:
	_ev_id+=1
	_recovering=false
	_ult_body=null
	current=""
	player.busy=false
	var b:=_body()
	if b!=null:b.stop_action()

# Existing real cage rules, review effects replace the sprite impact puff.
func _raise_dome(c: Vector3, r:=-1.0, cage_all:=false) -> HexShield:
	r=dome_radius if r<=0 else r
	var dome:=HexShield.raise_dome(world(),c,r,dome_time)
	dome.set_meta("team",MatchTeams.team_of(player))
	dome._mat.shader=load("res://tools/debug/gorilla_visual_review_2026_11_09/cage_readable.gdshader")
	dome._mat.set_shader_parameter("tiles",Vector2(36,21))
	if cage_all:
		dome.cage_all=true
		dome.make_panels(ult_panels,ult_panel_health)
	else:dome.health=dome_health
	_domes.append(dome)
	var held: Array=targets()+((allies()+[player]) if cage_all else [])
	for e in held:
		if flat(e.global_position-c).length()<=r and e.has_method("trap"):e.trap(dome)
	impact.emit(.8)
	return dome
