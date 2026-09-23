#include "NarisHUD.h"

#include "BoneBeastBoss.h"
#include "BoneBeastDataAsset.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "NarisCombatComponent.h"
#include "NarisEnergyComponent.h"
#include "NarisHeroCharacter.h"
#include "NarisInteractable.h"
#include "NarisInteractionComponent.h"
#include "NarisRuntimeSubsystem.h"

void ANarisHUD::DrawBar(
    const FString& Label,
    float Value,
    float MaxValue,
    float X,
    float Y,
    const FLinearColor& FillColor
)
{
    const float SafeMax = FMath::Max(MaxValue, 1.f);
    const float Ratio = FMath::Clamp(Value / SafeMax, 0.f, 1.f);
    const float Width = 320.f;
    const float Height = 18.f;

    DrawText(Label, FLinearColor::White, X, Y - 22.f, nullptr, 0.9f, false);
    DrawRect(FLinearColor(0.02f, 0.03f, 0.05f, 0.85f), X, Y, Width, Height);
    DrawRect(FillColor, X, Y, Width * Ratio, Height);
}

void ANarisHUD::DrawHUD()
{
    Super::DrawHUD();

    if (!PlayerOwner)
    {
        return;
    }

    ANarisHeroCharacter* Hero = Cast<ANarisHeroCharacter>(PlayerOwner->GetPawn());
    if (!Hero)
    {
        return;
    }

    const FLinearColor Gold(0.82f, 0.65f, 0.18f, 1.f);
    const FLinearColor Cyan(0.36f, 0.86f, 0.92f, 1.f);
    const FLinearColor Violet(0.40f, 0.14f, 0.78f, 1.f);
    const FLinearColor Ember(0.95f, 0.28f, 0.07f, 1.f);

    if (Hero->Combat)
    {
        DrawBar(
            NSLOCTEXT("NARIS", "HUDHealth", "Health").ToString(),
            Hero->Combat->Health,
            Hero->Combat->MaxHealth,
            40.f,
            60.f,
            Ember
        );
        DrawBar(
            NSLOCTEXT("NARIS", "HUDResonance", "Resonance").ToString(),
            Hero->Combat->Resonance,
            Hero->Combat->MaxResonance,
            40.f,
            120.f,
            Violet
        );
    }

    if (Hero->Energy)
    {
        DrawBar(
            NSLOCTEXT("NARIS", "HUDEnergy", "Energy").ToString(),
            Hero->Energy->Energy,
            Hero->Energy->MaxEnergy,
            40.f,
            180.f,
            Cyan
        );
    }

    if (Hero->Interaction)
    {
        AActor* Target = Hero->Interaction->FindNearestInteractable();
        if (Target && Target->GetClass()->ImplementsInterface(UNarisInteractable::StaticClass()))
        {
            const FText Prompt = INarisInteractable::Execute_GetInteractionPrompt(Target);
            const FString PromptText = FString::Printf(TEXT("[E] %s"), *Prompt.ToString());
            DrawText(PromptText, Gold, 40.f, 240.f, nullptr, 1.05f, false);
        }
    }

    UNarisRuntimeSubsystem* Runtime = nullptr;
    if (UGameInstance* GameInstance = GetWorld() ? GetWorld()->GetGameInstance() : nullptr)
    {
        Runtime = GameInstance->GetSubsystem<UNarisRuntimeSubsystem>();
    }

    if (Runtime)
    {
        const FString CompanionState = Runtime->IsCompanionUnlocked(TEXT("CelestialWolf"))
            ? NSLOCTEXT("NARIS", "HUDWolfBonded", "Celestial Wolf: Bonded").ToString()
            : NSLOCTEXT("NARIS", "HUDWolfUnbonded", "Celestial Wolf: Unbonded").ToString();

        DrawText(
            CompanionState,
            Runtime->IsCompanionUnlocked(TEXT("CelestialWolf")) ? Cyan : FLinearColor::Gray,
            40.f,
            280.f,
            nullptr,
            0.9f,
            false
        );

        if (Runtime->IsDemoCompleted())
        {
            DrawText(
                NSLOCTEXT("NARIS", "HUDDemoComplete", "W04 DEMO COMPLETE").ToString(),
                Gold,
                40.f,
                320.f,
                nullptr,
                1.25f,
                false
            );
        }
    }

    for (TActorIterator<ABoneBeastBoss> It(GetWorld()); It; ++It)
    {
        ABoneBeastBoss* Boss = *It;
        if (!Boss || (!Boss->IsEncounterActive() && !Boss->IsEncounterComplete()))
        {
            continue;
        }

        if (Boss->IsEncounterComplete())
        {
            DrawText(
                NSLOCTEXT("NARIS", "HUDBoneBeastDefeated", "Bone Beast Defeated").ToString(),
                Gold,
                40.f,
                380.f,
                nullptr,
                1.0f,
                false
            );
        }
        else
        {
            const float MaxHealth =
                Boss->BossData ? FMath::Max(Boss->BossData->MaxHealth, 1.f) : 1.f;
            DrawBar(
                NSLOCTEXT("NARIS", "HUDBoneBeast", "Bone Beast").ToString(),
                Boss->GetCurrentHealth(),
                MaxHealth,
                40.f,
                380.f,
                Ember
            );
        }
        break;
    }
}
