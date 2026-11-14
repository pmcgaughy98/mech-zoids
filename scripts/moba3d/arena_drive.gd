extends Node
signal phase_changed(phase: String)
signal collision(target: Node3D, damage: float)
signal finished(reason: String)
const WIND=29.0/120.0
const TRAVEL=38.0/120.0
const SPEED=12.0
const FRONT=1.29904
const HALF_WIDTH=.64
const DAMAGE=24.0
var damage:=DAMAGE
var chain_slam:=false
var struck: Node3D
const SHOVE=.70
const HITSTOP=.055
var actor: Node3D
var phase:="idle"
var phase_time:=0.0
var direction:=Vector3(0,0,1)
var did_hit:=false
var distance:=0.0
var hitstop_left:=0.0
var result:=""
var valid_targets: Array=[]
var hit_count:=0
func setup(p: Node3D) -> void:actor=p
func _set_phase(p: String) -> void:
	phase=p
	phase_time=0
	phase_changed.emit(p)
func begin(aim: Vector3) -> bool:
	if phase!="idle" or not actor.alive or actor.stunned>0:return false
	direction=Vector3(aim.x,0,aim.z).normalized()
	if direction.length_squared()<.1:direction=actor.facing
	did_hit=false
	struck=null
	distance=0
	hitstop_left=0
	result=""
	actor.busy=true
	actor.facing=direction
	_set_phase("brace")
	return true
func can_cancel_recovery() -> bool:
	return phase in ["hit","brake"] and phase_time>=(.27 if phase=="hit" else .23)
func request_movement() -> bool:
	if phase=="idle":return true
	if not can_cancel_recovery():return false
	_end("recovery_cancelled")
	return true
func interrupt(reason: String) -> void:
	if phase!="idle":_end(reason)
func _end(reason: String) -> void:
	result=reason
	actor.busy=false
	_set_phase("idle")
	finished.emit(reason)
func _first_enemy(from: Vector3, motion: Vector3) -> Dictionary:
	var best:=2.0
	var who: Node3D=null
	var length:=motion.length()
	var right:=Vector3(direction.z,0,-direction.x)
	for n in valid_targets:
		if not is_instance_valid(n) or not MatchTeams.hittable(n) or MatchTeams.team_of(n)==MatchTeams.team_of(actor) or not n.has_method("knock_aside"):continue
		if chain_slam and n.get("kind")!="machine":continue
		var rel: Vector3=n.global_position-from
		var radius: float=n.radius()
		var outside:=maxf(0,absf(rel.dot(right))-HALF_WIDTH)
		if outside>radius:continue
		var along:=rel.dot(direction)
		if along < -.05:continue
		var touch:=along-sqrt(maxf(0,radius*radius-outside*outside))-FRONT
		var f:=maxf(0,touch/maxf(length,.00001))
		if f<=1 and f<best:
			best=f
			who=n
	return {} if who==null else {"target":who,"fraction":best}
func tick(delta: float) -> void:
	if phase=="idle":return
	if not actor.alive:_end("death");return
	if actor.stunned>0:_end("stun");return
	var remaining:=delta
	for loop in 12:
		if remaining<=.000001 or phase=="idle":break
		if hitstop_left>0:
			var hold:=minf(remaining,hitstop_left)
			hitstop_left-=hold
			remaining-=hold
			continue
		var duration: float=WIND if phase=="brace" else TRAVEL if phase=="drive" else (.10 if chain_slam else 50.0/120.0) if phase=="hit" else 43.0/120.0
		var step:=minf(remaining,duration-phase_time)
		if phase=="drive":
			var from:=actor.global_position
			var motion:=direction*SPEED*step
			var wanted:=MatchBodies.block(actor,from,from+motion,actor.body_radius(),chain_slam)
			var safe:=ArenaMotion.slide(actor,from,wanted-from,actor.body_radius())
			var probe_from:=from+direction*(FRONT-.18)
			var probe_safe:=ArenaMotion.slide(actor,probe_from,motion,.18)
			var probe_fraction:=clampf((probe_safe-probe_from).dot(direction)/maxf(motion.length(),.00001),0,1)
			var body_fraction:=clampf((safe-from).dot(direction)/maxf(motion.length(),.00001),0,1)
			safe=from+motion*minf(probe_fraction,body_fraction)
			actor.global_position=safe
			actor._dome_walls(from)
			for dome in HexShield.live_domes():
				if str(dome.get_meta("team",""))==actor.team and not dome.cage_all:continue
				var center: Vector3=dome.global_position
				var before:=Vector2(from.x-center.x,from.z-center.z).length()
				var offset:=Vector3(actor.global_position.x-center.x,0,actor.global_position.z-center.z)
				var inside: bool=before<=dome.radius
				var bound: float=maxf(.1,dome.radius-FRONT) if inside else dome.radius+FRONT
				if dome.blocks_at(actor.global_position) and ((inside and offset.length()>bound) or (not inside and offset.length()<bound)):
					actor.global_position=center+offset.normalized()*bound
			safe=actor.global_position
			var allowed:=clampf((safe-from).dot(direction)/maxf(motion.length(),.00001),0,1)
			var enemy:=_first_enemy(from,motion)
			if not enemy.is_empty() and float(enemy.fraction)<=allowed+.00001 and not did_hit:
				actor.global_position=from+motion*float(enemy.fraction)
				distance+=motion.length()*float(enemy.fraction)
				did_hit=true
				hit_count+=1
				var target: Node3D=enemy.target
				struck=target
				if target.has_method("take_damage"):target.take_damage(damage,actor)
				else:target.hit(actor)
				# knock_aside() also deals kit damage; use its motion helper without a second hit.
				if target.has_method("halt"):target.halt()
				if not chain_slam:
					target._from=MatchTeams.flat(target.global_position)
					target._to=target._from+direction*SHOVE
					target._height=.15
					target._move_tween().tween_method(target._shove_step,0.0,1.0,.18)
				result="enemy_hit"
				hitstop_left=HITSTOP
				_set_phase("hit")
				collision.emit(target,damage)
				remaining-=step
				continue
			distance+=(safe-from).length()
			if allowed<.995:
				result="wall_stop"
				_set_phase("brake")
				remaining-=step
				continue
		phase_time+=step
		remaining-=step
		if phase_time>=duration-.000001:
			if phase=="brace":_set_phase("drive")
			elif phase=="drive":
				result="miss"
				_set_phase("brake")
			else:_end(result)


