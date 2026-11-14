extends Node3D

func _ready():
    for name in ["DownloadedRig", "RepairedJellyfish"]:
        var skeletons = get_node(name).find_children("*", "Skeleton3D", true, false)
        assert(skeletons.size() == 1)
        assert(skeletons[0].get_bone_count() == 49, "Original 49 joints required")
        print("JELLYFISH RIG CHECK PASS: ", name, ", 49 bones")
    DirAccess.make_dir_recursive_absolute("res://evidence")
    var camera = $ReviewCamera
    for view in [
        ["comparison-front",Vector3(0,2.6,10),Vector3(0,.95,0),6.2],
        ["comparison-back",Vector3(0,2.6,-10),Vector3(0,.95,0),6.2],
        ["repaired-front",Vector3(2.7,2,6),Vector3(2.7,.85,0),2.5],
        ["repaired-back",Vector3(2.7,2,-6),Vector3(2.7,.85,0),2.5],
        ["repaired-left",Vector3(-3.3,1.5,0),Vector3(2.7,.85,0),2.5],
        ["repaired-right",Vector3(8.7,1.5,0),Vector3(2.7,.85,0),2.5],
        ["repaired-underside",Vector3(2.7,-6,0),Vector3(2.7,.85,0),2.5]
    ]:
        var comparison: bool = view[0].begins_with("comparison")
        for name in ["OriginalSource","DownloadedRig","RepairedJellyfish"]:
            get_node(name).visible = comparison or name == "RepairedJellyfish"
            get_node(name+"Label").visible = comparison
        camera.position = view[1]
        camera.look_at(view[2], Vector3.FORWARD if view[0].ends_with("underside") else Vector3.UP)
        camera.size = view[3]
        for i in range(5):
            await get_tree().process_frame
        await RenderingServer.frame_post_draw
        var path: String = "res://evidence/"+view[0]+".png"
        assert(get_viewport().get_texture().get_image().save_png(path) == OK)
        print("JELLYFISH FRAME SAVED: ",path)
    for name in ["OriginalSource","DownloadedRig","RepairedJellyfish"]:
        get_node(name).visible = true
        get_node(name+"Label").visible = true
    camera.position = Vector3(0,2.6,10)
    camera.look_at(Vector3(0,.95,0))
    camera.size = 6.2
    print("SUMMER JELLYFISH REVIEW PASS: three native versions, original 49-joint rig, seven runtime frames")
