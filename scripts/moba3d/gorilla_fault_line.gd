extends Node3D
## Prototype slot 2: one damage hit per unit, followed by a short slowing field. No hard CC.
const RANGE=6.0
const SPEED=9.0
const RADIUS=1.5
const LIFE=1.4
var damage:=22.0
var actor: Node3D
var art: Node3D
var waves: Array=[]
var fields: Array=[]
var hit_count:=0
var release_count:=0
func setup(p: Node3D,visual: Node3D) -> void:actor=p;art=visual
func endpoint(at: Vector3) -> Vector3:
	var v:=MatchTeams.flat(at-actor.global_position).limit_length(RANGE)
	return actor.global_position+v
func launch(at: Vector3) -> void:
	var end:=endpoint(at);var origin:=actor.global_position
	var direction:=MatchTeams.flat(end-origin).normalized()
	waves.append({"at":origin,"end":end,"direction":direction,"hit":{},"node":art.piece(1)})
	release_count+=1
func _damage_in(wave: Dictionary,from: Vector3,to: Vector3,radius: float) -> void:
	for target: Node3D in MatchTeams.enemies_of(actor):
		if not MatchTeams.hittable(target) or not target.has_method("take_damage"):continue
		var id:=target.get_instance_id()
		if wave.hit.has(id):continue
		var near:=Geometry2D.get_closest_point_to_segment(Vector2(target.global_position.x,target.global_position.z),Vector2(from.x,from.z),Vector2(to.x,to.z))
		var gap:=near.distance_to(Vector2(target.global_position.x,target.global_position.z))
		if gap>radius+target.radius() or not MatchTeams.clear_line(actor,to,target.global_position,.3) or _cage_blocks(to,target.global_position):continue
		wave.hit[id]=true
		if target.has_method("hit"):target.hit(actor,damage/MatchRules.kit_hit_damage)
		else:target.take_damage(damage,actor)
		hit_count+=1
func _physics_process(delta: float) -> void:
	if not is_instance_valid(actor):return
	for wave in waves.duplicate():
		var from: Vector3=wave.at;var motion: Vector3=wave.direction*minf(SPEED*delta,from.distance_to(wave.end))
		var to:=from+motion
		var wall:=ArenaMotion.ray(actor,from+Vector3.UP*.25,to+Vector3.UP*.25)
		var blocked:=not wall.is_empty()
		if _cage_blocks(from,to):blocked=true
		if blocked:
			art.decals.erase(wave.node);wave.node.queue_free();waves.erase(wave);continue
		_damage_in(wave,from,to,.55);wave.at=to
		art.place(wave.node,to,Vector2(1.9,1.9),.65)
		if to.distance_to(wave.end)<.001:
			_damage_in(wave,to,to,RADIUS)
			fields.append({"at":to,"time":0.0,"node":wave.node})
			art.burst(to,5,Vector2(2.4,2.4),.3,.55);waves.erase(wave)
	for field in fields.duplicate():
		field.time+=delta
		if field.time>=LIFE:
			art.decals.erase(field.node);field.node.queue_free();fields.erase(field);continue
		art.place(field.node,field.at,Vector2.ONE*RADIUS*2.3,.35*(1-smoothstep(LIFE-.3,LIFE,field.time)))
		for target: Node3D in MatchTeams.enemies_of(actor):
			if target.has_method("slow") and MatchTeams.flat(target.global_position-field.at).length()<=RADIUS+target.radius() and MatchTeams.clear_line(actor,field.at,target.global_position,.3) and not _cage_blocks(field.at,target.global_position):target.slow(.16)
func _cage_blocks(from: Vector3,to: Vector3) -> bool:
	var motion:=MatchTeams.flat(to-from);var aa:=motion.length_squared()
	if aa<.000001:return false
	for dome in HexShield.live_domes():
		if not dome.cage_all and MatchTeams.team_of(actor)==str(dome.get_meta("team","")):continue
		var offset:=MatchTeams.flat(from-dome.global_position)
		var bb:=2*offset.dot(motion);var cc: float=offset.length_squared()-dome.radius*dome.radius
		var disc: float=bb*bb-4*aa*cc
		if disc<0:continue
		for fraction in [(-bb-sqrt(disc))/(2*aa),(-bb+sqrt(disc))/(2*aa)]:
			if fraction>.0001 and fraction<=1 and dome.blocks_at(from+motion*fraction):return true
	return false
