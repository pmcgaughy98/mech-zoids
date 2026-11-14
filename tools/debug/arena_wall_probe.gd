extends SceneTree
## Probes the arena's wall collision against its meshes (Claude, 2026-11-04, game feel lane): rays along +x from the
## blue spawn at several z, and the mesh and collision box of the wall piece each ray hits.
## Run: Godot --headless --path . --script res://tools/debug/arena_wall_probe.gd

const SCENE := preload("res://scenes/moba3d/arena_blockout.tscn")


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var top: Node3D = SCENE.instantiate()
	root.add_child(top)
	for i in 4:
		await physics_frame
	var space: PhysicsDirectSpaceState3D = top.get_world_3d().direct_space_state
	var seen := {}
	for zi in range(-10, 11):
		var z := 70.0 + zi * 0.2
		var a := Vector3(0, 1.0, z)
		var h: Dictionary = space.intersect_ray(PhysicsRayQueryParameters3D.create(a, a + Vector3(20, 0, 0), 1))
		if h.is_empty():
			print("z %.1f: no hit" % z)
			continue
		var body: Node3D = h.collider
		print("z %.1f: hit x %.3f  normal %s  body %s" % [z, h.position.x, h.normal.snapped(Vector3.ONE * 0.01), body.get_path()])
		if seen.has(body):
			continue
		seen[body] = true
		var mi := body.get_parent() as MeshInstance3D
		var cs := body.get_child(0) as CollisionShape3D
		if mi != null and mi.mesh is BoxMesh:
			print("   mesh  size %s  basis x %s z %s  at %s" % [(mi.mesh as BoxMesh).size, mi.global_basis.x.snapped(Vector3.ONE * 0.01),
				mi.global_basis.z.snapped(Vector3.ONE * 0.01), mi.global_position.snapped(Vector3.ONE * 0.01)])
		elif mi != null:
			print("   mesh  %s aabb %s" % [mi.mesh, mi.get_aabb()])
		if cs != null and cs.shape is BoxShape3D:
			print("   shape size %s  basis x %s z %s  at %s" % [(cs.shape as BoxShape3D).size, cs.global_basis.x.snapped(Vector3.ONE * 0.01),
				cs.global_basis.z.snapped(Vector3.ONE * 0.01), cs.global_position.snapped(Vector3.ONE * 0.01)])
		elif cs != null:
			print("   shape %s at %s" % [cs.shape, cs.global_position.snapped(Vector3.ONE * 0.01)])
	quit()
