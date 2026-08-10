using UnrealBuildTool;
using System.Collections.Generic;

public class NARIS_W04EditorTarget : TargetRules
{
    public NARIS_W04EditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_4;
        ExtraModuleNames.Add("NARIS_W04");
    }
}
