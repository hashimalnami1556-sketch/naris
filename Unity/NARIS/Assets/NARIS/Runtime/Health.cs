using System;
using UnityEngine;
namespace Naris {
public sealed class Health : MonoBehaviour {
    public float maximum = 100;
    public float Current { get; private set; }
    public bool Dead => Current <= 0;
    public event Action Died;
    void Awake() { Current = maximum; }
    public void Restore(float value) { Current = Mathf.Clamp(value, 0, maximum); }
    public void Damage(float value) {
        if (Dead || value <= 0) return;
        Current = Mathf.Max(0, Current - value);
        NarisAudio.Play("impact_01",.25f);
        if (Dead) Died?.Invoke();
    }
}
}
