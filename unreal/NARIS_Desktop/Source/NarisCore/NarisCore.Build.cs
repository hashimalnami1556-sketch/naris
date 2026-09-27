using UnrealBuildTool;
public class NarisCore : ModuleRules
{
    public NarisCore(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core", "CoreUObject", "Engine", "InputCore", "GameplayTags", "Niagara", "AIModule", "NavigationSystem", "StateTreeModule", "GameplayStateTreeModule", "PCG"
        });
    }
}
