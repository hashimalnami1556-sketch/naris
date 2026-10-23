extends SceneTree
var failures := 0
var checks := 0

func _initialize() -> void:
    call_deferred("_run_tests")

func _check(condition: bool, label: String) -> void:
    checks += 1
    if not condition:
        failures += 1
        push_error("FAIL: " + label)
    else:
        print("PASS: " + label)

func _run_tests() -> void:
    var health_script := load("res://scripts/health.gd")
    var health = health_script.new(100.0)
    _check(health.current == 100.0, "initial HP")
    _check(health.apply_damage(40.0) == 40.0, "damage applied")
    _check(health.current == 60.0, "HP reduced")
    _check(health.apply_damage(-10.0) == 0.0, "negative damage rejected")
    _check(health.apply_damage(INF) == 0.0, "infinite damage rejected")
    _check(health.apply_damage(NAN) == 0.0, "NaN damage rejected")
    _check(health.heal(20.0) == 20.0, "healing")
    _check(health.heal(INF) == 0.0, "infinite healing rejected")
    _check(health.apply_damage(1000.0) == 80.0, "damage capped")
    _check(health.is_dead(), "death state")
    _check(health.heal(10.0) == 0.0, "no resurrection via heal")
    var invalid = health_script.new(NAN)
    _check(invalid.current == 100.0, "invalid maximum repaired")
    var loader_script := load("res://scripts/visual_loader.gd")
    var parent := Node3D.new()
    root.add_child(parent)
    var fallback: Node3D = loader_script.attach_visual(parent, "res://nonexistent_model.glb", Color.RED)
    _check(fallback != null, "missing asset fallback")
    _check(fallback.name == "FallbackVisual_ImportNotReady", "fallback labelled")
    _check(not loader_script.play_named_animation(parent, PackedStringArray(["attack"]), true), "missing animation returns false")
    parent.queue_free()
    print("P26 checks=%d failures=%d" % [checks, failures])
    quit(1 if failures > 0 else 0)
