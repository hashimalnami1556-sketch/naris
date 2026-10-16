using UnityEngine;
namespace Naris {
[RequireComponent(typeof(CharacterController), typeof(Health))]
public sealed class EnemyBrain : MonoBehaviour {
    public PlayerMotor target;
    CharacterController controller;
    Health health;
    float nextHit;
    void Awake() {
        controller = GetComponent<CharacterController>(); health = GetComponent<Health>();
        health.Died += () => { gameObject.SetActive(false); };
    }
    void Update() {
        if (!target || health.Dead || Time.timeScale == 0 || target.GetComponent<Health>().Dead) return;
        var delta = target.transform.position - transform.position; delta.y = 0;
        if (delta.magnitude > 18) return;
        if (delta.magnitude > 1.7f) {
            transform.forward = delta.normalized;
            controller.Move((delta.normalized * 2.5f + Vector3.down * 9) * Time.deltaTime);
        } else if (Time.time >= nextHit) {
            nextHit = Time.time + 1.2f;
            var visual=GetComponent<ActorVisual>(); if(visual)visual.Action(name.Contains("2")?"Swipe":"Bite",.5f);
            if (!target.Dodging) target.GetComponent<Health>().Damage(12);
        }
    }
}
}
