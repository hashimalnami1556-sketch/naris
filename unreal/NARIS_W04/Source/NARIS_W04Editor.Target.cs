using UnrealBuildTool;
using System.Collections.Generic;

public class NARIS_W04EditorTarget : TargetRules
{
    public NARIS_W04EditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V6;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_7;
        ExtraModuleNames.Add("NARIS_W04");
    }
}