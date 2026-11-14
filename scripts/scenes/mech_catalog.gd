extends Control
## Shared design archive. Artist edits live in art/model_catalog/workspaces/*.blend.
const CATALOG := "res://art/model_catalog/catalog.json"
var entries: Array = []
var models: Array[Node3D] = []
var centers: Array[Vector3] = []
var model_labels: Array[Label3D] = []
var camera: Camera3D
var viewport: SubViewport
var title_label: Label
var status_label: Label
var sheet_textures: Array[TextureRect] = []
var roster_buttons: Array[Button] = []
var selected := 0
var overview := true
var yaw := 0.0
var previous_scale := Vector2i(320, 180)
var sheet_overlay: Control
var comparison: Node3D
var comparing := false
var review_sheets := false
var compare_button: Button
var sheets_button: Button

func _ready() -> void:
	previous_scale = get_tree().root.content_scale_size
	get_tree().root.content_scale_size = Vector2i(1280, 720)
	entries = JSON.parse_string(FileAccess.get_file_as_string(CATALOG))["entries"]
	_build_ui()
	_build_stage()
	for i in entries.size():
		if entries[i]["id"] == "gorilla":
			selected = i
	_select(selected)
	if "--catalog-check" in OS.get_cmdline_user_args():
		_check.call_deferred()
	if "--cobra-repair-check" in OS.get_cmdline_user_args():
		_check_cobra_repair.call_deferred()
	elif "--model-repair-check" in OS.get_cmdline_user_args():
		_check_cobra_repair.call_deferred()

func _label(text_value: String, pos: Vector2, font_size: int, width: float = 0) -> Label:
	var label := Label.new()
	label.text = text_value
	label.position = pos
	label.add_theme_font_size_override("font_size", font_size)
	if width > 0:
		label.size.x = width
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(label)
	return label

func _button(text_value: String, rect: Rect2, action: Callable) -> Button:
	var button := Button.new()
	button.text = text_value
	button.position = rect.position
	button.size = rect.size
	button.add_theme_font_size_override("font_size", 15)
	button.pressed.connect(action)
	add_child(button)
	return button

func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = Color("121b24")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)
	_label("MECH DESIGN ARCHIVE", Vector2(24, 16), 26)
	_label("Downloaded models + their four source reference views", Vector2(24, 51), 15)
	_label("%d model entries / original sheets preserved" % entries.size(), Vector2(24, 75), 14)
	var container := SubViewportContainer.new()
	container.position = Vector2(20, 107)
	container.size = Vector2(816, 447)
	container.stretch = true
	add_child(container)
	viewport = SubViewport.new()
	viewport.size = Vector2i(816, 447)
	viewport.own_world_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	container.add_child(viewport)
	title_label = _label("", Vector2(858, 18), 24, 400)
	status_label = _label("", Vector2(858, 60), 14, 396)
	for i in 4:
		var x := 858 + (i % 2) * 200
		var y := 151 + (i / 2) * 208
		_label(["FRONT", "LEFT", "BACK", "RIGHT"][i], Vector2(x, y), 13)
		var texture := TextureRect.new()
		texture.position = Vector2(x, y + 22)
		texture.size = Vector2(188, 180)
		texture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		texture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		texture.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		texture.gui_input.connect(func(event: InputEvent):
			if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
				_show_sheet(i))
		add_child(texture)
		sheet_textures.append(texture)
	_button("Lineup / Focus  [Tab]", Rect2(24, 560, 240, 30), _toggle_view)
	_button("Turn left  [Q]", Rect2(276, 560, 170, 30), func(): _turn(-45))
	_button("Turn right  [E]", Rect2(458, 560, 170, 30), func(): _turn(45))
	_button("Title  [Esc]", Rect2(640, 560, 190, 30), _back)
	var regular_index := 0
	var objective_index := 0
	if entries.any(func(entry: Dictionary): return entry.get("category", "") == "objective"):
		_label("OBJECTIVES", Vector2(24, 696), 11)
	for i in entries.size():
		var short_name: String = entries[i]["name"]
		if entries[i]["reference_only"]:
			short_name = "Shoebill alt*"
		var rect := Rect2(24 + (regular_index % 7) * 117, 602 + (regular_index / 7) * 22, 111, 22)
		if entries[i].get("category", "") == "objective":
			rect = Rect2(142 + objective_index * 190, 694, 180, 24)
			objective_index += 1
		else:
			regular_index += 1
		var button := _button(short_name, rect, _select.bind(i))
		button.add_theme_font_size_override("font_size", 12)
		button.size = rect.size
		roster_buttons.append(button)
	compare_button = _button("Compare model versions [C]", Rect2(858, 583, 396, 30), _toggle_comparison)
	sheets_button = _button("Original / review sheets [R]", Rect2(858, 621, 396, 30), _toggle_sheets)
	_label("Click a sheet to enlarge. Version comparisons use\nmatched display scale. Original sources preserved.", Vector2(858, 661), 13, 400)

func _instantiate_model(path: String) -> Node3D:
	if ResourceLoader.exists(path):
		var packed := load(path) as PackedScene
		assert(packed != null, "Missing catalog model: " + path)
		return packed.instantiate() as Node3D
	# Full-detail review archives stay outside automatic Godot imports.
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(path, state) == OK, "Cannot read model: " + path)
	return document.generate_scene(state)

func _sheet_texture(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	var image := Image.load_from_file(path)
	assert(image != null and not image.is_empty(), "Missing review sheet: " + path)
	return ImageTexture.create_from_image(image)

func _bounds(node: Node3D) -> AABB:
	var result := AABB()
	var first := true
	for child in node.find_children("*", "MeshInstance3D", true, false):
		var mesh := child as MeshInstance3D
		var box: AABB = (node.global_transform.affine_inverse() * mesh.global_transform) * mesh.get_aabb()
		result = box if first else result.merge(box)
		first = false
	return result

func _build_stage() -> void:
	var world := Node3D.new()
	viewport.add_child(world)
	var objective_count := 0
	for entry in entries:
		if entry.get("category", "") == "objective":
			objective_count += 1
	var regular_rows := int(ceil(float(entries.size() - objective_count) / 7.0))
	var total_rows := regular_rows + (1 if objective_count > 0 else 0)
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color("253340")
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color("d2dfed")
	environment.environment.ambient_light_energy = 0.5
	world.add_child(environment)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-50, -30, 0)
	light.light_energy = 0.85
	light.shadow_enabled = true
	world.add_child(light)
	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-25, 140, 0)
	fill.light_energy = 0.25
	world.add_child(fill)
	var floor_mesh := MeshInstance3D.new()
	var floor_shape := BoxMesh.new()
	floor_shape.size = Vector3(34, 0.12, maxf(23, (total_rows - 1) * 4.6 + 6))
	floor_mesh.mesh = floor_shape
	floor_mesh.position.y = -0.18
	floor_mesh.position.z = (total_rows - 1) * 2.3 - 6.9
	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_color = Color("273944")
	floor_mesh.material_override = floor_mat
	world.add_child(floor_mesh)
	var regular_index := 0
	var objective_index := 0
	for i in entries.size():
		var holder := Node3D.new()
		if entries[i].get("category", "") == "objective":
			holder.position = Vector3((objective_index - (objective_count - 1) * 0.5) * 4.2, 0, regular_rows * 4.6 - 6.9)
			objective_index += 1
		else:
			holder.position = Vector3((regular_index % 7) * 4.2 - 12.6, 0, (regular_index / 7) * 4.6 - 6.9)
			regular_index += 1
		world.add_child(holder)
		var model := _instantiate_model(entries[i]["display_model"])
		holder.add_child(model)
		var bounds := _bounds(model)
		var fit := minf(2.9 / maxf(bounds.size.x, bounds.size.z), 2.6 / bounds.size.y)
		holder.scale = Vector3.ONE * fit
		model.position -= Vector3(bounds.get_center().x, bounds.position.y, bounds.get_center().z)
		models.append(model)
		centers.append(holder.position + Vector3(0, bounds.size.y * fit * 0.5, 0))
		var label := Label3D.new()
		label.text = entries[i]["name"]
		label.position = holder.position + Vector3(0, 0.05, 1.8)
		label.font_size = 36
		label.pixel_size = 0.009
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.no_depth_test = true
		world.add_child(label)
		model_labels.append(label)
	camera = Camera3D.new()
	camera.current = true
	camera.fov = 45
	world.add_child(camera)

func _select(index: int) -> void:
	_clear_comparison()
	selected = index
	var entry: Dictionary = entries[index]
	title_label.text = "Shoebill (alternate)" if entry["reference_only"] else entry["name"]
	if entry.get("category", "") == "objective":
		title_label.text += " / Objective"
	status_label.text = entry["status"]
	review_sheets = entry.has("review_views")
	_refresh_sheets()
	compare_button.disabled = not entry.has("review_models")
	sheets_button.disabled = not entry.has("review_views")
	for i in roster_buttons.size():
		roster_buttons[i].modulate = Color("a9e5c4") if i == selected else Color.WHITE
	_update_camera()

func _refresh_sheets() -> void:
	var entry: Dictionary = entries[selected]
	var source: Dictionary = entry["review_views"] if review_sheets and entry.has("review_views") else entry["views"]
	for i in 4:
		sheet_textures[i].texture = _sheet_texture(source[["front", "left", "back", "right"][i]]["path"])
	sheets_button.text = "Showing review sheets [R]" if review_sheets else "Showing original sheets [R]"

func _toggle_sheets() -> void:
	if not entries[selected].has("review_views"):
		return
	review_sheets = not review_sheets
	_refresh_sheets()

func _clear_comparison() -> void:
	comparing = false
	if is_instance_valid(comparison):
		comparison.get_parent().remove_child(comparison)
		comparison.queue_free()
	comparison = null

func _toggle_comparison() -> void:
	if comparing:
		_clear_comparison()
		_update_camera()
		return
	var entry: Dictionary = entries[selected]
	if not entry.has("review_models"):
		return
	overview = false
	comparing = true
	yaw = 22.5
	comparison = Node3D.new()
	camera.get_parent().add_child(comparison)
	var versions: Array = entry["review_models"]
	for i in versions.size():
		var version: Dictionary = versions[i]
		var holder := Node3D.new()
		holder.position.x = (i - (versions.size() - 1) * 0.5) * 3.6
		comparison.add_child(holder)
		var model := Node3D.new()
		holder.add_child(model)
		var asset := _instantiate_model(version["path"])
		model.add_child(asset)
		if version.has("display_basis"):
			var rows: Array = version["display_basis"]
			var basis := Basis(Vector3(rows[0][0], rows[1][0], rows[2][0]), Vector3(rows[0][1], rows[1][1], rows[2][1]), Vector3(rows[0][2], rows[1][2], rows[2][2]))
			asset.transform = Transform3D(basis, Vector3.ZERO) * asset.transform
		var bounds := _bounds(model)
		var fit := float(version.get("display_scale", minf(2.9 / maxf(bounds.size.x, bounds.size.z), 2.6 / bounds.size.y)))
		holder.scale = Vector3.ONE * fit
		model.position -= Vector3(bounds.get_center().x, bounds.position.y, bounds.get_center().z)
		var label := Label3D.new()
		label.text = version["label"]
		label.position = Vector3(holder.position.x, 2.6, 0)
		label.font_size = 28
		label.pixel_size = 0.009
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.no_depth_test = true
		comparison.add_child(label)
	_update_camera()

func _update_camera() -> void:
	var target := Vector3(0, 0, 0) if overview else centers[selected]
	if overview:
		var min_z := centers[0].z
		var max_z := centers[0].z
		for center in centers:
			min_z = minf(min_z, center.z)
			max_z = maxf(max_z, center.z)
		target.z = (min_z + max_z) * 0.5
	var offset := Vector3(0, 24, 18) if overview else Vector3(0, 2.6, 6.5)
	if comparing:
		target = Vector3(0, 0.9, 0)
		offset = Vector3(0, 4.5, 11)
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL if overview else Camera3D.PROJECTION_PERSPECTIVE
	camera.size = 19.5
	if comparing:
		camera.projection = Camera3D.PROJECTION_ORTHOGONAL
		var comparison_count: int = entries[selected]["review_models"].size()
		camera.size = 4.4 if comparison_count == 2 else (6.2 if comparison_count == 3 else 8.2)
	for i in models.size():
		(models[i].get_parent() as Node3D).visible = not comparing and (overview or i == selected)
		model_labels[i].visible = overview
	camera.position = target + offset.rotated(Vector3.UP, deg_to_rad(yaw))
	camera.look_at(target)

func _toggle_view() -> void:
	_clear_comparison()
	overview = not overview
	_update_camera()

func _turn(degrees: float) -> void:
	yaw += degrees
	_update_camera()

func _show_sheet(index: int) -> void:
	if is_instance_valid(sheet_overlay):
		sheet_overlay.queue_free()
	sheet_overlay = ColorRect.new()
	(sheet_overlay as ColorRect).color = Color("121b24")
	sheet_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(sheet_overlay)
	var texture := TextureRect.new()
	texture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	texture.texture = sheet_textures[index].texture
	texture.position = Vector2(20, 20)
	texture.size = Vector2(1240, 640)
	texture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	sheet_overlay.add_child(texture)
	var close := Button.new()
	close.text = "Close reference [Esc]"
	close.position = Vector2(500, 670)
	close.size = Vector2(280, 32)
	close.pressed.connect(func(): sheet_overlay.queue_free())
	sheet_overlay.add_child(close)

func _unhandled_key_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.keycode:
		KEY_TAB: _toggle_view()
		KEY_Q: _turn(-45)
		KEY_E: _turn(45)
		KEY_C: _toggle_comparison()
		KEY_R: _toggle_sheets()
		KEY_LEFT: _select(posmod(selected - 1, entries.size()))
		KEY_RIGHT: _select((selected + 1) % entries.size())
		KEY_ESCAPE:
			if is_instance_valid(sheet_overlay):
				sheet_overlay.queue_free()
			else:
				_back()

func _back() -> void:
	get_tree().root.content_scale_size = previous_scale
	var destination := "res://scenes/title.tscn"
	if not ResourceLoader.exists(destination):
		destination = ProjectSettings.get_setting("application/run/main_scene")
	get_tree().change_scene_to_file(destination)

func _check_cobra_repair() -> void:
	var output := "res://reports/model_catalog/cobra-repair-v1"
	var model_id := "cobra"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--review-output="):
			output = arg.trim_prefix("--review-output=")
		elif arg.begins_with("--review-model="):
			model_id = arg.trim_prefix("--review-model=")
	DirAccess.make_dir_recursive_absolute(output)
	for i in entries.size():
		if entries[i]["id"] == model_id:
			_select(i)
	assert(entries[selected]["id"] == model_id)
	var version_count := int(entries[selected]["review_models"].size())
	assert(version_count >= 2)
	overview = true
	yaw = 0
	_update_camera()
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(output.path_join("lineup.png"))
	overview = false
	_update_camera()
	for mode in ["review", "original", "comparison"]:
		if mode == "original":
			_toggle_sheets()
		elif mode == "comparison":
			_toggle_sheets()
			_toggle_comparison()
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(output.path_join(mode + ".png"))
		if mode == "comparison":
			_turn(180)
			await get_tree().process_frame
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(output.path_join("comparison-back.png"))
			_turn(-180)
	assert(comparing and comparison.get_child_count() == version_count * 2)
	for button in roster_buttons:
		assert(button.position.y + button.size.y <= 720, "Catalog button clipped below screen")
	_show_sheet(0)
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(output.path_join("review-sheet.png"))
	sheet_overlay.queue_free()
	_clear_comparison()
	_update_camera()
	for model in models:
		(model.get_parent() as Node3D).visible = false
	var fixture := _instantiate_model(entries[selected]["display_model"])
	camera.get_parent().add_child(fixture)
	var skeleton := fixture.find_child("*", true, false) as Skeleton3D
	for child in fixture.find_children("*", "Skeleton3D", true, false):
		skeleton = child as Skeleton3D
	var expected_joints := int(entries[selected].get("review_provenance", {}).get("joint_count", 21))
	assert(skeleton != null and skeleton.get_bone_count() == expected_joints)
	var chase := load("res://scripts/moba3d/chase_camera_3d.gd").new() as Camera3D
	chase.fov = 60
	camera.get_parent().add_child(chase)
	chase.set("target", fixture)
	chase.call("snap")
	chase.current = true
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(output.path_join("actual-chase-camera.png"))
	print("MODEL REPAIR CHECK PASS: ", model_id, ", ", version_count, " comparison versions, original/review sheets, ", expected_joints, "-bone rig, current ChaseCamera3D")
	get_tree().quit()

func _check() -> void:
	var output := "res://reports/model_catalog"
	DirAccess.make_dir_recursive_absolute(output)
	assert(models.size() == entries.size())
	for i in entries.size():
		_select(i)
		overview = false
		_update_camera()
		assert(_bounds(models[i]).size.length() > 0)
		for sheet in sheet_textures:
			assert(sheet.texture != null)
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(output.path_join(entries[i]["id"] + ".png"))
	overview = true
	yaw = 0
	_update_camera()
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(output.path_join("lineup.png"))
	_show_sheet(0)
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(output.path_join("reference-enlarged.png"))
	print("CATALOG CHECK PASS: ", models.size(), " models, four sheets each, focus/lineup/reference views")
	get_tree().quit()
