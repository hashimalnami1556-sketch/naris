extends RefCounted
class_name NarisHealth

var maximum: float
var current: float

func _init(max_health: float = 100.0) -> void:
    # Never allow NaN/Infinity to enter gameplay state.
    maximum = maxf(max_health, 1.0) if is_finite(max_health) else 100.0
    current = maximum

func apply_damage(amount: float) -> float:
    if not is_finite(amount) or amount <= 0.0 or current <= 0.0:
        return 0.0
    var applied := minf(amount, current)
    current = maxf(0.0, current - applied)
    return applied

func heal(amount: float) -> float:
    if not is_finite(amount) or amount <= 0.0 or current <= 0.0:
        return 0.0
    var applied := minf(amount, maximum - current)
    current = minf(maximum, current + applied)
    return applied

func is_dead() -> bool:
    return current <= 0.0
