using UnrealBuildTool;
using System.Collections.Generic;

public class NARIS_W04Target : TargetRules
{
    public NARIS_W04Target(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_4;
        ExtraModuleNames.Add("NARIS_W04");
    }
}
