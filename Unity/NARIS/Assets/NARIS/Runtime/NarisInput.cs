using UnityEngine;

namespace Naris {
public readonly struct InputFrame {
    public readonly Vector2 Move;
    public readonly Vector2 Look;
    public readonly bool Sprint, Dodge, Attack, Pause, Save, Load;
    public InputFrame(float mx,float my,float lx,float ly,bool sprint,bool dodge,bool attack,bool pause,bool save,bool load) {
        Move=Vector2.ClampMagnitude(new Vector2(mx,my),1f);
        Look=new Vector2(lx,ly);
        Sprint=sprint; Dodge=dodge; Attack=attack; Pause=pause; Save=save; Load=load;
    }
}

public static class NarisInput {
    public static InputFrame Read() {
        return new InputFrame(
            Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical"),
            Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y"),
            Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.JoystickButton8),
            Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.JoystickButton1),
            Input.GetMouseButtonDown(0) || Input.GetKeyDown(KeyCode.JoystickButton2),
            Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.JoystickButton7),
            Input.GetKeyDown(KeyCode.F5), Input.GetKeyDown(KeyCode.F9));
    }
}
}
