using UnityEngine;

namespace Naris {
public readonly struct PlatformProfile {
    public readonly bool KeyboardMouse, Gamepad, Touch;
    public readonly int MaxQuality;
    public readonly int TargetFps;
    public PlatformProfile(bool keyboardMouse,bool gamepad,bool touch,int maxQuality,int targetFps) {
        KeyboardMouse=keyboardMouse; Gamepad=gamepad; Touch=touch; MaxQuality=maxQuality; TargetFps=targetFps;
    }
    public static PlatformProfile For(RuntimePlatform platform) {
        switch(platform) {
            case RuntimePlatform.Android:
            case RuntimePlatform.IPhonePlayer: return new PlatformProfile(false,true,true,2,45);
            case RuntimePlatform.WebGLPlayer: return new PlatformProfile(true,true,false,2,60);
            default: return new PlatformProfile(true,true,false,4,60);
        }
    }
}

public static class PlatformBootstrap {
    public static PlatformProfile ApplyCurrent() {
        var p=PlatformProfile.For(Application.platform);
        Application.targetFrameRate=p.TargetFps;
        QualitySettings.SetQualityLevel(Mathf.Min(QualitySettings.GetQualityLevel(),p.MaxQuality),true);
        return p;
    }
}
}
