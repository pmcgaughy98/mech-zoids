extends "res://scripts/moba3d/mech_model_3d.gd"
## Base visual bridge. Existing kit owns damage; absent ground-pound clip remains a documented gap.
var phase:=0.0
func _process(delta: float) -> void:
	phase+=delta
	var p:=get_parent()
	var s: DirectionalSprite3D=p.get_node("Sprite")
	var clip: String={"horn_jab":"horn_attack","horn_toss":"horn_attack","brace":"MF_brace_hold","stampede":"charge"}.get(s.action,"")
	if clip!="" and has_clip(clip):
		if not external_clock or action!=clip:start_external(clip)
		var t:=0.0
		if clip=="charge":t=fmod(phase*9.0/1.47,clip_length(clip))
		elif clip=="MF_brace_hold":t=fmod(phase,clip_length(clip))
		else:
			var count:=maxi(1,s.sprite_frames.get_frame_count(s.animation))
			t=clampf((s.frame+s.get_frame_progress())/count,0,1)*clip_length(clip)
		sample_external(clip,t)
		position=feel_offset
	else:
		if external_clock:finish_external()
		super._process(delta)
