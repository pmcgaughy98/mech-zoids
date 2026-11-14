extends SceneTree
## Look lane, 2026-11-10: set_glow must change one mech's drum glow only, and survive set_flash and set_outline.
## Run: --headless --path . --script res://tools/debug/glow_check.gd -- <rhino glb path>
const LOOK=preload("res://scripts/moba3d/mech_look.gd")
func _load(p:String) -> Node3D:
	var d:=GLTFDocument.new(); var st:=GLTFState.new()
	if d.append_from_file(p,st)!=OK:return null
	return d.generate_scene(st)
func _energy(root:Node) -> Array:
	var out=[]
	for mi in root.find_children("*","MeshInstance3D",true,false):
		for s in mi.mesh.get_surface_count():
			var m=mi.get_active_material(s)
			if m is ShaderMaterial and m.resource_name=="Rhino drum ring glow":out.append(snappedf(m.get_shader_parameter("emission_energy"),0.001))
	return out
func _init():
	var p=OS.get_cmdline_user_args()[0]
	var a:=_load(p); var b:=_load(p)
	root.add_child(a); root.add_child(b)
	print("surfaces a=",LOOK.apply_model(a)," b=",LOOK.apply_model(b,true))
	print("start a=",_energy(a)," b=",_energy(b))
	print("set_glow(a,0.2) changed=",LOOK.set_glow(a,0.2))
	print("after a=",_energy(a)," b=",_energy(b))
	LOOK.set_flash(a,1.0); LOOK.set_flash(a,0.0)
	print("after flash a=",_energy(a)," b=",_energy(b))
	LOOK.set_outline(a,true); LOOK.set_glow(a,3.0)
	print("after outline+glow3 a=",_energy(a)," b=",_energy(b))
	var ok=_energy(a).size()>0 and _energy(a).all(func(e):return e==3.0) and _energy(b).all(func(e):return e!=3.0 and e!=0.2)
	print("GLOW_CHECK ","PASS" if ok else "FAIL")
	quit()
