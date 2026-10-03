#include "NarisEnvironmentQuestTrigger.h"

#include "Components/BoxComponent.h"
#include "Engine/GameInstance.h"
#include "GameFramework/Pawn.h"
#include "NarisRuntimeSubsystem.h"

ANarisEnvironmentQuestTrigger::ANarisEnvironmentQuestTrigger()
{
    PrimaryActorTick.bCanEverTick = false;

    TriggerBounds = CreateDefaultSubobject<UBoxComponent>(TEXT("TriggerBounds"));
    RootComponent = TriggerBounds;
    TriggerBounds->SetBoxExtent(FVector(250.f, 250.f, 180.f));
    TriggerBounds->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    TriggerBounds->SetCollisionResponseToAllChannels(ECR_Ignore);
    TriggerBounds->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
    TriggerBounds->SetGenerateOverlapEvents(true);

    TriggerBounds->OnComponentBeginOverlap.AddDynamic(
        this,
        &ANarisEnvironmentQuestTrigger::HandleBeginOverlap
    );
}

void ANarisEnvironmentQuestTrigger::BeginPlay()
{
    Super::BeginPlay();

    if (!bOneTime || TriggerId.IsNone())
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GI ? GI->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;
    if (!Runtime)
    {
        return;
    }

    bConsumed = Runtime->HasNarrativeTriggered(GetPersistenceKey());
    if (bConsumed && TriggerBounds)
    {
        TriggerBounds->SetGenerateOverlapEvents(false);
    }
}

FString ANarisEnvironmentQuestTrigger::GetPersistenceKey() const
{
    return FString::Printf(
        TEXT("EnvironmentTrigger.%s"),
        *TriggerId.ToString()
    );
}

void ANarisEnvironmentQuestTrigger::HandleBeginOverlap(
    UPrimitiveComponent* OverlappedComponent,
    AActor* OtherActor,
    UPrimitiveComponent* OtherComp,
    int32 OtherBodyIndex,
    bool bFromSweep,
    const FHitResult& SweepResult
)
{
    APawn* Pawn = Cast<APawn>(OtherActor);
    if (!Pawn || !Pawn->IsPlayerControlled() || bConsumed)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GI ? GI->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;
    if (!Runtime)
    {
        return;
    }

    if (!RequiredQuest.IsNone()
        && !Runtime->IsQuestActive(RequiredQuest.ToString()))
    {
        return;
    }

    bool bChangedState = false;

    if (!QuestToStart.IsNone())
    {
        bChangedState |= Runtime->StartQuest(
            QuestToStart.ToString(),
            0
        );
    }

    if (!QuestToStart.IsNone() && QuestStepToSet >= 0)
    {
        bChangedState |= Runtime->SetQuestStep(
            QuestToStart.ToString(),
            QuestStepToSet
        );
    }
    else if (!RequiredQuest.IsNone() && QuestStepToSet >= 0)
    {
        bChangedState |= Runtime->SetQuestStep(
            RequiredQuest.ToString(),
            QuestStepToSet
        );
    }

    OnEnvironmentTriggered(TriggerType, TargetId);

    if (bOneTime && !TriggerId.IsNone())
    {
        bChangedState |= Runtime->TriggerNarrative(GetPersistenceKey());
        bConsumed = true;
        TriggerBounds->SetGenerateOverlapEvents(false);
    }

    if (bAutoSave && bChangedState)
    {
        Runtime->SaveState(Runtime->DefaultAutoSaveSlot);
    }
}
