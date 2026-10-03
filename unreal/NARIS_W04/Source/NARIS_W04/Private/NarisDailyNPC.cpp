#include "NarisDailyNPC.h"

#include "AIController.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "NarisRuntimeSubsystem.h"

ANarisDailyNPC::ANarisDailyNPC()
{
    PrimaryActorTick.bCanEverTick = false;
    AIControllerClass = AAIController::StaticClass();
    AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
}

void ANarisDailyNPC::BeginPlay()
{
    Super::BeginPlay();

    // Timer-driven evaluation: never schedule navigation every frame.
    const float Interval = FMath::Clamp(ScheduleIntervalSeconds, 0.1f, 60.f);
    GetWorldTimerManager().SetTimer(
        RoutineTimer, this, &ANarisDailyNPC::UpdateRoutine, Interval, true
    );
    UpdateRoutine();
}

void ANarisDailyNPC::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    GetWorldTimerManager().ClearTimer(RoutineTimer);
    Super::EndPlay(EndPlayReason);
}

bool ANarisDailyNPC::IsScheduledAt(const FNarisNPCScheduleEntry& Entry, float WorldHour)
{
    if (!FMath::IsFinite(WorldHour) ||
        !FMath::IsFinite(Entry.StartHour) ||
        !FMath::IsFinite(Entry.EndHour))
    {
        return false;
    }

    // Validate authored hours instead of silently accepting invalid schedules.
    if (Entry.StartHour < 0.f || Entry.StartHour >= 24.f ||
        Entry.EndHour < 0.f || Entry.EndHour >= 24.f)
    {
        return false;
    }

    const float StartHour = Entry.StartHour;
    const float EndHour = Entry.EndHour;
    if (FMath::IsNearlyEqual(StartHour, EndHour))
    {
        return false; // Zero-duration entry.
    }

    WorldHour = FMath::Fmod(FMath::Fmod(WorldHour, 24.f) + 24.f, 24.f);
    if (EndHour < StartHour)
    {
        return WorldHour >= StartHour || WorldHour < EndHour;
    }
    return WorldHour >= StartHour && WorldHour < EndHour;
}

void ANarisDailyNPC::SetWorldHour(float InHour)
{
    if (!FMath::IsFinite(InHour))
    {
        return;
    }

    WorldHourOverride = FMath::Fmod(FMath::Fmod(InHour, 24.f) + 24.f, 24.f);
    UpdateRoutine();
}

void ANarisDailyNPC::SetStormActive(bool bActive)
{
    if (bStormActive == bActive)
    {
        return;
    }

    bStormActive = bActive;
    UpdateRoutine();
}

void ANarisDailyNPC::UpdateRoutine()
{
    if (!GetWorld())
    {
        return;
    }

    // Replace this fallback with the authoritative world clock when available.
    const float DayDuration = FMath::Max(1.f, GameDayDurationSeconds);
    const float WorldHour = WorldHourOverride >= 0.f
        ? WorldHourOverride
        : FMath::Fmod(GetWorld()->GetTimeSeconds(), DayDuration) * (24.f / DayDuration);

    if (bStormActive && IsValid(StormShelter))
    {
        ApplyActivity(ENarisNPCActivity::Shelter, StormShelter);
        return;
    }

    for (const FNarisNPCScheduleEntry& Entry : DailySchedule)
    {
        if (IsScheduledAt(Entry, WorldHour))
        {
            ApplyActivity(Entry.Activity, Entry.Destination);
            return;
        }
    }

    ApplyActivity(ENarisNPCActivity::Idle, nullptr);
}

void ANarisDailyNPC::ApplyActivity(ENarisNPCActivity NewActivity, AActor* Destination)
{
    if (NewActivity == CurrentActivity && CurrentDestination.Get() == Destination)
    {
        return;
    }

    CurrentActivity = NewActivity;
    CurrentDestination = Destination;

    if (AAIController* AI = Cast<AAIController>(GetController()))
    {
        AI->StopMovement();
        if (IsValid(Destination))
        {
            AI->MoveToActor(Destination, 120.f);
        }
    }

    OnActivityChanged(CurrentActivity);
}

bool ANarisDailyNPC::InteractNPC(AActor* Interactor)
{
    // Accept a controlled pawn or its player controller, not arbitrary actors.
    if (!IsValid(Interactor))
    {
        return false;
    }
    const APawn* Pawn = Cast<APawn>(Interactor);
    const APlayerController* Player = Cast<APlayerController>(Interactor);
    if ((Pawn == nullptr || !Pawn->IsPlayerControlled()) && Player == nullptr)
    {
        return false;
    }

    if (QuestToOffer.IsNone())
    {
        return false;
    }

    UGameInstance* GI = GetGameInstance();
    UNarisRuntimeSubsystem* Runtime = GI
        ? GI->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;
    if (!Runtime)
    {
        return false;
    }

    const FString QuestId = QuestToOffer.ToString();
    if (bQuestOffered || Runtime->IsQuestActive(QuestId) || Runtime->IsQuestCompleted(QuestId))
    {
        return false;
    }

    const bool bStarted = Runtime->StartQuest(QuestToOffer.ToString(), 0);
    bQuestOffered = bStarted;
    return bStarted;
}
