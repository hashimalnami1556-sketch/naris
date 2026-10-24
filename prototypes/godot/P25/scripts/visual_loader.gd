extends RefCounted
class_name NarisVisualLoader

static func attach_visual(parent: Node3D, resource_path: String, fallback_color: Color, visual_scale: float = 1.0) -> Node3D:
    if ResourceLoader.exists(resource_path):
        var scene := load(resource_path) as PackedScene
        if scene != null:
            var instance := scene.instantiate() as Node3D
            if instance != null:
                instance.name = "ImportedVisual"
                instance.scale = Vector3.ONE * visual_scale
                parent.add_child(instance)
                return instance
    var fallback := MeshInstance3D.new()
    fallback.name = "FallbackVisual_ImportNotReady"
    var capsule := CapsuleMesh.new()
    capsule.radius = 0.38
    capsule.height = 1.7
    fallback.mesh = capsule
    var mat := StandardMaterial3D.new()
    mat.albedo_color = fallback_color
    fallback.material_override = mat
    fallback.position.y = 0.85
    parent.add_child(fallback)
    return fallback

static func play_named_animation(visual: Node, aliases: PackedStringArray, one_shot: bool = false) -> bool:
    var players: Array[AnimationPlayer] = []
    _collect_players(visual, players)
    for ap in players:
        for library_name in ap.get_animation_library_list():
            var library := ap.get_animation_library(library_name)
            if library == null:
                continue
            for anim_name in library.get_animation_list():
                var key := String(anim_name).to_lower()
                for alias in aliases:
                    if key.contains(alias.to_lower()):
                        var qualified := String(anim_name) if String(library_name).is_empty() else String(library_name) + "/" + String(anim_name)
                        if ap.current_animation != qualified or not ap.is_playing():
                            ap.play(qualified, 0.12)
                        return true
    return false

static func _collect_players(node: Node, out: Array[AnimationPlayer]) -> void:
    if node is AnimationPlayer:
        out.append(node as AnimationPlayer)
    for child in node.get_children():
        _collect_players(child, out)
