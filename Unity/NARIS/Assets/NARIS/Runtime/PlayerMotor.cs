using UnityEngine;
namespace Naris {
[RequireComponent(typeof(CharacterController), typeof(Health))]
public sealed class PlayerMotor : MonoBehaviour {
    public float speed = 6;
    public float Stamina { get; private set; } = 100;
    CharacterController controller;
    Health health;
    float vertical, yaw, pitch = 18, attackAt, dodgeUntil;
    Vector3 dodgeDirection;
    public Transform view;
    void Awake() { controller = GetComponent<CharacterController>(); health = GetComponent<Health>(); }
    void Update() {
        if (Time.timeScale == 0 || health.Dead) return;
        var input=NarisInput.Read();
        yaw += input.Look.x * 2;
        pitch = Mathf.Clamp(pitch - input.Look.y * 2, -15, 60);
        transform.rotation = Quaternion.Euler(0, yaw, 0);
        var move = Vector3.ClampMagnitude(transform.right * input.Move.x + transform.forward * input.Move.y, 1);
        bool sprint = input.Sprint && move.sqrMagnitude > .01f && Stamina > 1;
        if (input.Dodge && Stamina >= 25 && Time.time >= dodgeUntil) {
            Stamina -= 25; dodgeUntil = Time.time + .22f;
            GetComponent<ActorVisual>()?.Action("Dodge",.22f);
            dodgeDirection = move.sqrMagnitude > .01f ? move : transform.forward;
        }
        Stamina = Mathf.Clamp(Stamina + (sprint ? -20 : 16) * Time.deltaTime, 0, 100);
        vertical = controller.isGrounded ? -2 : vertical - 24 * Time.deltaTime;
        Vector3 velocity = Time.time < dodgeUntil ? dodgeDirection * 16 : move * speed * (sprint ? 1.5f : 1);
        controller.Move((velocity + Vector3.up * vertical) * Time.deltaTime);
        if (input.Attack && Time.time >= attackAt && Stamina >= 10) Attack();
        if (transform.position.y < -10) health.Damage(1000);
    }
    void LateUpdate() {
        if (!view) return;
        var pivot = transform.position + Vector3.up * 1.6f;
        var rotation = Quaternion.Euler(pitch, yaw, 0);
        view.position = pivot + rotation * new Vector3(0, 1, -5);
        view.rotation = Quaternion.LookRotation(pivot + transform.forward * 3 - view.position);
    }
    void Attack() {
        attackAt = Time.time + .4f; Stamina -= 10;
        GetComponent<ActorVisual>()?.Action("Attack_Light",.4f); NarisAudio.Play("whoosh_01");
        foreach (var enemy in FindObjectsByType<EnemyBrain>(FindObjectsSortMode.None)) {
            var delta = enemy.transform.position - transform.position; delta.y = 0;
            if (delta.magnitude < 3 && Vector3.Angle(transform.forward, delta) < 70)
                enemy.GetComponent<Health>().Damage(35);
        }
    }
    public bool Dodging => Time.time < dodgeUntil;
}
}
