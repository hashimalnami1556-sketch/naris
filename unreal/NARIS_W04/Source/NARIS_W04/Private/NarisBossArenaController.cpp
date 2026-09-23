#include "NarisBossArenaController.h"

#include "BoneBeastBoss.h"
#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "NarisPresentationComponent.h"

ANarisBossArenaController::ANarisBossArenaController()
{
    PrimaryActorTick.bCanEverTick = false;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    SetRootComponent(SceneRoot);

    EntryBlocker = CreateDefaultSubobject<UBoxComponent>(TEXT("EntryBlocker"));
    EntryBlocker->SetupAttachment(SceneRoot);
    EntryBlocker->SetBoxExtent(FVector(90.f, 600.f, 260.f));
    EntryBlocker->SetCollisionResponseToAllChannels(ECR_Block);
    EntryBlocker->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    EncounterTrigger =
        CreateDefaultSubobject<UBoxComponent>(TEXT("EncounterTrigger"));
    EncounterTrigger->SetupAttachment(SceneRoot);
    EncounterTrigger->SetBoxExtent(FVector(420.f, 420.f, 220.f));
    EncounterTrigger->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    EncounterTrigger->SetCollisionResponseToAllChannels(ECR_Ignore);
    EncounterTrigger->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
    EncounterTrigger->OnComponentBeginOverlap.AddDynamic(
        this,
        &ANarisBossArenaController::HandleEncounterOverlap
    );

    Presentation =
        CreateDefaultSubobject<UNarisPresentationComponent>(TEXT("Presentation"));
}

void ANarisBossArenaController::BeginPlay()
{
    Super::BeginPlay();

    if (!Boss && GetWorld())
    {
        for (TActorIterator<ABoneBeastBoss> It(GetWorld()); It; ++It)
        {
            Boss = *It;
            break;
        }
    }

    BindBoss();

    if (Boss)
    {
        SetArenaClosed(
            Boss->IsEncounterActive() && !Boss->IsEncounterComplete()
        );

        if (Boss->IsEncounterComplete() && EncounterTrigger)
        {
            EncounterTrigger->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        }
    }
}

void ANarisBossArenaController::SetBoss(ABoneBeastBoss* NewBoss)
{
    if (Boss == NewBoss)
    {
        return;
    }

    if (Boss)
    {
        Boss->OnBossEvent.RemoveDynamic(
            this,
            &ANarisBossArenaController::HandleBossEvent
        );
    }

    Boss = NewBoss;
    BindBoss();
}

void ANarisBossArenaController::BindBoss()
{
    if (!Boss)
    {
        return;
    }

    Boss->OnBossEvent.RemoveDynamic(
        this,
        &ANarisBossArenaController::HandleBossEvent
    );
    Boss->OnBossEvent.AddDynamic(
        this,
        &ANarisBossArenaController::HandleBossEvent
    );
}

void ANarisBossArenaController::SetArenaClosed(bool bClosed)
{
    bArenaClosed = bClosed;

    if (EntryBlocker)
    {
        EntryBlocker->SetCollisionEnabled(
            bArenaClosed
                ? ECollisionEnabled::QueryAndPhysics
                : ECollisionEnabled::NoCollision
        );
    }

    const FName CueId =
        bArenaClosed
            ? FName(TEXT("Arena.Lock"))
            : FName(TEXT("Arena.Unlock"));

    OnArenaEvent.Broadcast(CueId);

    if (Presentation)
    {
        Presentation->TriggerCue(CueId);
    }
}

void ANarisBossArenaController::HandleBossEvent(FName EventName)
{
    if (EventName == TEXT("EncounterStarted"))
    {
        SetArenaClosed(true);
        return;
    }

    if (EventName == TEXT("EncounterComplete")
        || EventName == TEXT("EncounterRestoredComplete"))
    {
        SetArenaClosed(false);
        return;
    }

    FName ArenaCue = NAME_None;

    if (EventName == TEXT("PhaseTransition"))
    {
        ArenaCue = TEXT("Arena.PhaseTransition");
    }
    else if (EventName == TEXT("Death"))
    {
        ArenaCue = TEXT("Arena.BossDeath");
    }
    else if (EventName == TEXT("DemoEnd"))
    {
        ArenaCue = TEXT("Arena.DemoEnd");
    }
    else if (EventName == TEXT("EncounterLocked"))
    {
        ArenaCue = TEXT("Arena.LockedFeedback");
    }

    if (!ArenaCue.IsNone())
    {
        OnArenaEvent.Broadcast(ArenaCue);

        if (Presentation)
        {
            Presentation->TriggerCue(ArenaCue);
        }
    }
}


void ANarisBossArenaController::HandleEncounterOverlap(
    UPrimitiveComponent* OverlappedComponent,
    AActor* OtherActor,
    UPrimitiveComponent* OtherComp,
    int32 OtherBodyIndex,
    bool bFromSweep,
    const FHitResult& SweepResult
)
{
    if (!Boss
        || Boss->IsEncounterActive()
        || Boss->IsEncounterComplete()
        || !IsValid(OtherActor))
    {
        return;
    }

    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!PlayerPawn || OtherActor != PlayerPawn)
    {
        return;
    }

    OnArenaEvent.Broadcast(TEXT("Arena.Enter"));
    if (Presentation)
    {
        Presentation->TriggerCue(TEXT("Arena.Enter"));
    }

    const bool bStarted = Boss->TryStartEncounter(OtherActor);
    if (bStarted && EncounterTrigger)
    {
        EncounterTrigger->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }
}
