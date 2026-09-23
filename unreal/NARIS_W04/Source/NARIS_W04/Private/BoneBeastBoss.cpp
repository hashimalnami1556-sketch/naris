#include "BoneBeastBoss.h"

#include "BoneBeastDataAsset.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "NarisRuntimeSubsystem.h"

ABoneBeastBoss::ABoneBeastBoss()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ABoneBeastBoss::BeginPlay()
{
    Super::BeginPlay();

    if (!GetWorld())
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    if (Runtime && Runtime->IsBossDefeated(BossProgressId))
    {
        CurrentHealth = 0.f;
        CurrentPhase = ENarisBossPhase::Dead;
        bEncounterActive = false;
        bEncounterComplete = true;
        EmitBossEvent(TEXT("EncounterRestoredComplete"));
        if (Runtime->IsDemoCompleted())
        {
            EmitBossEvent(TEXT("DemoEnd"));
        }
    }
}

void ABoneBeastBoss::StartEncounter()
{
    if (!BossData || BossData->MaxHealth <= 0.f || bEncounterActive || bEncounterComplete)
    {
        return;
    }

    if (!GetWorld())
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    if (!Runtime || !Runtime->IsCompanionUnlocked(RequiredCompanionId))
    {
        EmitBossEvent(TEXT("EncounterLocked"));
        return;
    }

    if (Runtime->IsBossDefeated(BossProgressId))
    {
        CurrentHealth = 0.f;
        CurrentPhase = ENarisBossPhase::Dead;
        bEncounterComplete = true;
        EmitBossEvent(TEXT("EncounterRestoredComplete"));
        return;
    }

    CurrentHealth = BossData->MaxHealth;
    CurrentPhase = ENarisBossPhase::Phase1;
    bEncounterActive = true;
    bEncounterComplete = false;
    EmitBossEvent(TEXT("EncounterStarted"));
}

void ABoneBeastBoss::ResetEncounter()
{
    if (!BossData || bEncounterComplete)
    {
        return;
    }

    CurrentHealth = BossData->MaxHealth;
    CurrentPhase = ENarisBossPhase::Phase1;
    bEncounterActive = false;
    EmitBossEvent(TEXT("EncounterReset"));
}

void ABoneBeastBoss::ApplyDamageToEncounter(float Damage)
{
    if (!bEncounterActive || bEncounterComplete || CurrentPhase == ENarisBossPhase::Dead || Damage <= 0.f)
    {
        return;
    }

    CurrentHealth = FMath::Max(0.f, CurrentHealth - Damage);
    EmitBossEvent(TEXT("DamageTaken"));

    if (CurrentHealth <= 0.f)
    {
        CurrentHealth = 0.f;
        CurrentPhase = ENarisBossPhase::Dead;
        bEncounterActive = false;
        EmitBossEvent(TEXT("Death"));
        CompleteEncounter();
        return;
    }

    EvaluatePhase();
}

void ABoneBeastBoss::CompleteEncounter()
{
    if (bEncounterComplete || CurrentPhase != ENarisBossPhase::Dead || !GetWorld())
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    if (!Runtime || !Runtime->MarkBossDefeated(BossProgressId))
    {
        EmitBossEvent(TEXT("CompletionStateFailed"));
        return;
    }

    if (BossData && !BossData->QuestCompletionId.IsNone())
    {
        Runtime->CompleteQuest(BossData->QuestCompletionId.ToString());
    }

    if (bCompleteDemoOnDefeat)
    {
        Runtime->CompleteDemo();
    }

    bEncounterComplete = true;
    EmitBossEvent(TEXT("EncounterComplete"));

    if (bCompleteDemoOnDefeat)
    {
        EmitBossEvent(TEXT("DemoEnd"));
    }

    if (bAutoSave && !Runtime->SaveState(AutoSaveSlot))
    {
        EmitBossEvent(TEXT("AutoSaveFailed"));
    }
}

void ABoneBeastBoss::EvaluatePhase()
{
    if (!BossData || BossData->Phases.Num() == 0 || CurrentPhase == ENarisBossPhase::Dead)
    {
        return;
    }

    const float MaxHP = FMath::Max(BossData->MaxHealth, 1.f);
    const float HealthRatio = CurrentHealth / MaxHP;
    int32 NewPhaseIndex = 0;

    for (int32 Index = 0; Index < BossData->Phases.Num(); ++Index)
    {
        if (HealthRatio <= BossData->Phases[Index].HealthThreshold)
        {
            NewPhaseIndex = Index;
        }
    }

    const int32 MaxSupportedPhaseIndex = FMath::Min(BossData->Phases.Num() - 1, 2);
    NewPhaseIndex = FMath::Clamp(NewPhaseIndex, 0, MaxSupportedPhaseIndex);
    const ENarisBossPhase NewPhase = static_cast<ENarisBossPhase>(NewPhaseIndex);

    if (NewPhase != CurrentPhase)
    {
        CurrentPhase = NewPhase;
        EmitBossEvent(FName(*FString::Printf(TEXT("Phase%d"), NewPhaseIndex + 1)));
        EmitBossEvent(TEXT("PhaseTransition"));
    }
}

void ABoneBeastBoss::EmitBossEvent(FName EventName)
{
    OnBossEvent.Broadcast(EventName);
}
