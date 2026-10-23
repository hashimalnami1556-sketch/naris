extends RefCounted
class_name NarisHealth

var maximum: float
var current: float

func _init(max_health: float = 100.0) -> void:
    maximum = maxf(max_health, 1.0)
    current = maximum

func apply_damage(amount: float) -> float:
    if not is_finite(amount):
        return 0.0
    var damage := maxf(amount, 0.0)
    var applied := minf(damage, current)
    current = maxf(0.0, current - applied)
    return applied

func is_dead() -> bool:
    return current <= 0.0
