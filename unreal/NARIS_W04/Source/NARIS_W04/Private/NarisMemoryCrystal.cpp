#include "NarisMemoryCrystal.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "NarisRuntimeSubsystem.h"
#include "NarisRewardDirectorSubsystem.h"
#include "NarisSubtitleSubsystem.h"

ANarisMemoryCrystal::ANarisMemoryCrystal()
{
    PrimaryActorTick.bCanEverTick = false;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    SetRootComponent(SceneRoot);

    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    Mesh->SetupAttachment(SceneRoot);
    Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
}

bool ANarisMemoryCrystal::Interact_Implementation(AActor* InstigatorActor)
{
    return ActivateMemory(InstigatorActor);
}

FText ANarisMemoryCrystal::GetInteractionPrompt_Implementation() const
{
    return NSLOCTEXT("NARIS", "MemoryCrystalInteractPrompt", "Read Memory");
}

bool ANarisMemoryCrystal::ActivateMemory(AActor* InstigatorActor)
{
    if (!GetWorld())
    {
        return false;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    if (!Runtime)
    {
        return false;
    }

    if (bOneShot && Runtime->HasNarrativeTriggered(NarrativeId))
    {
        return false;
    }

    if (!Runtime->UnlockLore(LoreId))
    {
        return false;
    }

    if (!Runtime->TriggerNarrative(NarrativeId))
    {
        return false;
    }

    if (!Runtime->StartQuest(QuestId, QuestStep))
    {
        return false;
    }

    if (!SubtitleLine.IsEmpty())
    {
        if (UNarisSubtitleSubsystem* Subtitles =
                GameInstance->GetSubsystem<UNarisSubtitleSubsystem>())
        {
            Subtitles->ShowSubtitle(
                SubtitleSpeaker,
                SubtitleLine,
                SubtitleDurationSeconds
            );
        }
    }

    if (bAutoSave && !Runtime->SaveState(AutoSaveSlot))
    {
        return false;
    }

    if (UNarisRewardDirectorSubsystem* Rewards = GameInstance->GetSubsystem<UNarisRewardDirectorSubsystem>())
    {
        FNarisRewardPresentationEvent Event;
        Event.EventId = FString::Printf(TEXT("w04.memory.%s"), *NarrativeId);
        Event.Kind = ENarisRewardKind::Exploration;
        Event.SourceId = TEXT("memory_crystal_01");
        Event.Rarity = ENarisRewardRarity::Rare;
        Event.Title = NSLOCTEXT("NARIS", "MemoryCrystalRewardTitle", "Memory Recovered");
        Event.Description = NSLOCTEXT("NARIS", "MemoryCrystalRewardBody", "An Ashen Forest memory has been restored.");
        Rewards->Enqueue(Event);
    }

    OnActivated.Broadcast();
    return true;
}
