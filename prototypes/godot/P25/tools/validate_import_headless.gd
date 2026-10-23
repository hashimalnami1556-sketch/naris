extends SceneTree
# Run after editor import: godot --headless --path . --script res://tools/validate_import_headless.gd
# The gate fails closed: missing folders, empty assets and failed loads are errors.
const FOLDERS := ["res://assets/characters", "res://assets/environments"]
var rows: Array[Dictionary] = []
var missing_folders: Array[String] = []

func _initialize() -> void:
    for folder in FOLDERS:
        _scan(folder)
    var failures := 0
    for row in rows:
        if not row["loaded"]:
            failures += 1
    var passed := rows.size() > 0 and failures == 0 and missing_folders.is_empty()
    var report := {
        "gate": "P0.5",
        "godot_version": Engine.get_version_info().get("string", "unknown"),
        "assets": rows,
        "missing_folders": missing_folders,
        "loaded_count": rows.size() - failures,
        "failed_count": failures,
        "passed": passed
    }
    var output_dir := "res://reports"
    var dir_error := DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output_dir))
    if dir_error != OK:
        push_error("Cannot create report directory: %s" % dir_error)
        quit(2)
        return
    var file := FileAccess.open(output_dir.path_join("godot_import_report.json"), FileAccess.WRITE)
    if file == null:
        push_error("Cannot write import report")
        quit(2)
        return
    file.store_string(JSON.stringify(report, "  "))
    file.close()
    print("P0.5 loaded=%d failed=%d missing_folders=%d passed=%s" % [rows.size() - failures, failures, missing_folders.size(), passed])
    quit(0 if passed else 1)

func _scan(folder: String) -> void:
    var dir := DirAccess.open(folder)
    if dir == null:
        missing_folders.append(folder)
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
                var row := {
                    "path": path, "asset_kind": kind, "loaded": false,
                    "skeleton_count": 0, "skinned_meshes": 0, "animation_clips": 0
                }
                var packed := ResourceLoader.load(path, "PackedScene") as PackedScene
                if packed != null:
                    var instance := packed.instantiate()
                    if instance != null:
                        row["loaded"] = true
                        _walk(instance, row)
                        instance.free()
                row["needs_rig"] = kind == "character" and (row["skeleton_count"] == 0 or row["skinned_meshes"] == 0)
                row["ready_for_animation"] = kind == "character" and row["loaded"] and not row["needs_rig"] and row["animation_clips"] > 0
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
            var library := ap.get_animation_library(lib)
            if library != null:
                row["animation_clips"] += library.get_animation_list().size()
    for child in node.get_children():
        _walk(child, row)
