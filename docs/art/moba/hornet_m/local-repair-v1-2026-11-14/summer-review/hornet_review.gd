extends Node3D

var capturing := true

func _ready():
    var joints := {}
    for model_name in ["DownloadedRig", "RestoredHornet"]:
        var model := get_node(model_name)
        var skeletons := model.find_children("*", "Skeleton3D", true, false)
        assert(skeletons.size() == 1, "Expected one skeleton")
        var skeleton := skeletons[0] as Skeleton3D
        assert(skeleton.get_bone_count() == 51, "Expected original 51 joints")
        joints[model_name] = skeleton.get_bone_count()
    print("SUMMER HORNET RIG CHECK PASS: ", JSON.stringify(joints))
    var outdir := "res://evidence"
    DirAccess.make_dir_recursive_absolute(outdir)
    var camera := $ReviewCamera as Camera3D
    for view in [
        ["comparison-front", Vector3(0,3.4,10), Vector3(0,0.95,0), 8.2],
        ["comparison-back", Vector3(0,3.4,-10), Vector3(0,0.95,0), 8.2],
        ["restored-front", Vector3(5.4,2.9,6), Vector3(5.4,0.9,0), 3.5],
        ["restored-back", Vector3(5.4,2.9,-6), Vector3(5.4,0.9,0), 3.5],
        ["restored-left", Vector3(-0.6,2.9,0), Vector3(5.4,0.9,0), 3.5],
        ["restored-right", Vector3(11.4,2.9,0), Vector3(5.4,0.9,0), 3.5],
        ["restored-underside", Vector3(5.4,-4.5,4), Vector3(5.4,0.7,0), 3.5]
    ]:
        var is_comparison: bool = view[0].begins_with("comparison")
        for model_name in ["OriginalSource", "SixLegTouchup", "DownloadedRig", "RestoredHornet"]:
            get_node(model_name).visible = is_comparison or model_name == "RestoredHornet"
            get_node(model_name + "Label").visible = is_comparison
        camera.position = view[1]
        camera.look_at(view[2])
        camera.size = view[3]
        for i in range(5):
            await get_tree().process_frame
        await RenderingServer.frame_post_draw
        var path: String = outdir + "/" + view[0] + ".png"
        var error := get_viewport().get_texture().get_image().save_png(path)
        assert(error == OK, "Cannot save review frame")
        print("SUMMER HORNET FRAME: ", path)
    camera.position = Vector3(0,3.4,10)
    camera.look_at(Vector3(0,0.95,0))
    camera.size = 8.2
    for model_name in ["OriginalSource", "SixLegTouchup", "DownloadedRig", "RestoredHornet"]:
        get_node(model_name).visible = true
        get_node(model_name + "Label").visible = true
    capturing = false
    print("SUMMER HORNET REVIEW PASS: four native versions, 51-joint restored rig, seven runtime frames")

func _unhandled_key_input(event):
    if capturing or not event.is_pressed():
        return
    var camera := $ReviewCamera as Camera3D
    if event.keycode == KEY_F:
        camera.position = Vector3(0,3.4,10)
        camera.look_at(Vector3(0,0.95,0))
        camera.size = 8.2
    elif event.keycode == KEY_B:
        camera.position = Vector3(0,3.4,-10)
        camera.look_at(Vector3(0,0.95,0))
        camera.size = 8.2
    elif event.keycode == KEY_R:
        camera.position = Vector3(5.4,2.9,6)
        camera.look_at(Vector3(5.4,0.9,0))
        camera.size = 3.5
