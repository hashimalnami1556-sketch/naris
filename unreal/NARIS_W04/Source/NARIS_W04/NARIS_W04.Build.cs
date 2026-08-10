using UnrealBuildTool;

public class NARIS_W04 : ModuleRules
{
    public NARIS_W04(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "GameplayTags"
        });
    }
}
