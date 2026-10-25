extends Node
class_name NarisCombatFSM
## P21 deterministic FSM. Advanced by the caller at physics tick.
signal state_changed(previous: int, current: int)
signal died
signal health_changed(current: float, maximum: float)
signal stamina_changed(current: float, maximum: float)

enum State { IDLE, ATTACK, BLOCK, DODGE, STUN, DEAD }

const MAX_HEALTH: float = 100.0
const MAX_STAMINA: float = 100.0
const ATTACK_COST: float = 20.0
const DODGE_COST: float = 25.0
const BLOCK_CHIP: float = 0.25
const ATTACK_START: float = 0.16
const ATTACK_END: float = 0.40
const DODGE_IFRAME_START: float = 0.07
const DODGE_IFRAME_END: float = 0.32

var state: State = State.IDLE
var health: float = MAX_HEALTH
var stamina: float = MAX_STAMINA
var elapsed: float = 0.0
var duration: float = 0.0
var damage_window: bool = false
var invulnerable: bool = false
var _hit_targets: Dictionary = {}

func transition(next: State, seconds: float = 0.0) -> bool:
    if state == State.DEAD and next != State.DEAD:
        return false
    var previous: State = state
    state = next
    elapsed = 0.0
    duration = maxf(seconds, 0.0)
    damage_window = false
    invulnerable = false
    _hit_targets.clear()
    if previous != state:
        state_changed.emit(previous, state)
    if previous != State.DEAD and state == State.DEAD:
        died.emit()
    return true

func request_attack() -> bool:
    if state != State.IDLE or stamina < ATTACK_COST:
        return false
    if not transition(State.ATTACK, 0.65):
        return false
    stamina -= ATTACK_COST
    stamina_changed.emit(stamina, MAX_STAMINA)
    return true

func request_dodge() -> bool:
    if state != State.IDLE or stamina < DODGE_COST:
        return false
    if not transition(State.DODGE, 0.48):
        return false
    stamina -= DODGE_COST
    stamina_changed.emit(stamina, MAX_STAMINA)
    return true

func set_block(active: bool) -> bool:
    if active and state == State.IDLE:
        return transition(State.BLOCK)
    if not active and state == State.BLOCK:
        return transition(State.IDLE)
    return false

func tick(delta: float) -> void:
    if delta <= 0.0 or state == State.DEAD:
        return
    if state == State.IDLE:
        var previous_stamina: float = stamina
        stamina = minf(MAX_STAMINA, stamina + 14.0 * delta)
        if not is_equal_approx(previous_stamina, stamina):
            stamina_changed.emit(stamina, MAX_STAMINA)
    elapsed += delta
    damage_window = state == State.ATTACK and elapsed >= ATTACK_START and elapsed < ATTACK_END
    invulnerable = state == State.DODGE and elapsed >= DODGE_IFRAME_START and elapsed < DODGE_IFRAME_END
    if duration > 0.0 and elapsed >= duration:
        transition(State.IDLE)

func register_attack_hit(target_id: int) -> bool:
    if state != State.ATTACK or not damage_window or _hit_targets.has(target_id):
        return false
    _hit_targets[target_id] = true
    return true

func consume_attack_hit() -> bool:
    return register_attack_hit(-1)

func receive_hit(amount: float) -> bool:
    if amount <= 0.0 or state == State.DEAD or invulnerable:
        return false
    var actual: float = amount * (BLOCK_CHIP if state == State.BLOCK else 1.0)
    health = maxf(0.0, health - actual)
    health_changed.emit(health, MAX_HEALTH)
    if health <= 0.0:
        transition(State.DEAD)
    elif state != State.BLOCK:
        transition(State.STUN, 0.38)
    return true

func restore(saved_health: float, saved_stamina: float) -> void:
    var previous: State = state
    health = clampf(saved_health, 0.0, MAX_HEALTH)
    stamina = clampf(saved_stamina, 0.0, MAX_STAMINA)
    state = State.DEAD if health <= 0.0 else State.IDLE
    elapsed = 0.0
    duration = 0.0
    damage_window = false
    invulnerable = false
    _hit_targets.clear()
    if previous != state:
        state_changed.emit(previous, state)
    health_changed.emit(health, MAX_HEALTH)
    stamina_changed.emit(stamina, MAX_STAMINA)
    if previous != State.DEAD and state == State.DEAD:
        died.emit()
