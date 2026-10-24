extends SceneTree
# Run after editor import: godot --headless --path . --script res://tools/validate_import_headless.gd
const FOLDERS := ["res://assets/characters", "res://assets/environments"]
var rows: Array[Dictionary] = []

func _initialize() -> void:
    for folder in FOLDERS:
        _scan(folder)
    if rows.is_empty():
        push_error("No GLB assets found; cannot pass import gate")
        quit(2)
        return
    var report := {"gate":"P0.5","godot_version":Engine.get_version_info().get("string","unknown"),"assets":rows}
    var file := FileAccess.open("res://reports/godot_import_report.json", FileAccess.WRITE)
    if file == null:
        push_error("Cannot write report")
        quit(2)
        return
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    var failures := 0
    for row in rows:
        if not row["loaded"]:
            failures += 1
    print("P0.5 imported=%d failed=%d" % [rows.size()-failures, failures])
    quit(1 if failures else 0)

func _scan(folder: String) -> void:
    var dir := DirAccess.open(folder)
    if dir == null:
        push_error("Missing folder " + folder)
        return
    dir.list_dir_begin()
    var entry := dir.get_next()
    while entry != "":
        if not entry.begins_with("."):
            var path := folder.path_join(entry)
            if dir.current_is_dir():
                _scan(path)
            elif entry.to_lower().ends_with(".glb"):
                var kind := "environment" if path.contains("/environments/") else "character"
                var row := {"path":path,"asset_kind":kind,"loaded":false,"skeleton_count":0,"skinned_meshes":0,"animation_clips":0}
                var packed := ResourceLoader.load(path,"PackedScene") as PackedScene
                if packed != null:
                    var instance := packed.instantiate()
                    if instance != null:
                        row["loaded"] = true
                        _walk(instance,row)
                        instance.free()
                row["needs_rig"] = kind == "character" and (row["skeleton_count"] == 0 or row["skinned_meshes"] == 0)
                rows.append(row)
        entry = dir.get_next()
    dir.list_dir_end()

func _walk(node: Node, row: Dictionary) -> void:
    if node is Skeleton3D:
        row["skeleton_count"] += 1
    if node is MeshInstance3D and (node as MeshInstance3D).skin != null:
        row["skinned_meshes"] += 1
    if node is AnimationPlayer:
        var ap := node as AnimationPlayer
        for lib in ap.get_animation_library_list():
            row["animation_clips"] += ap.get_animation_library(lib).get_animation_list().size()
    for child in node.get_children():
        _walk(child,row)
