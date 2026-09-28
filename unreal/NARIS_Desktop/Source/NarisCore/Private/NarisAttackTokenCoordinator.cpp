#include "NarisAttackTokenCoordinator.h"
#include "Engine/World.h"
#include "TimerManager.h"

UNarisAttackTokenCoordinator::UNarisAttackTokenCoordinator()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UNarisAttackTokenCoordinator::BeginPlay()
{
    Super::BeginPlay();
    ActiveAttackers.Reserve(MaxSimultaneousAttackers);
}

bool UNarisAttackTokenCoordinator::RequestAttackToken(AActor* Requester)
{
    if (!IsValid(Requester)) return false;
    PurgeInvalid();
    if (ActiveAttackers.Contains(Requester)) { ArmLease(Requester); return true; }
    if (ActiveAttackers.Num() < MaxSimultaneousAttackers)
    {
        ActiveAttackers.Add(Requester); ArmLease(Requester);
        OnTokenChanged.Broadcast(Requester, true); return true;
    }
    WaitingQueue.AddUnique(Requester);
    return false;
}
void UNarisAttackTokenCoordinator::ReleaseAttackToken(AActor* Requester)
{
    if (!Requester) return;
    const bool bWasActive = ActiveAttackers.Remove(Requester) > 0;
    WaitingQueue.Remove(Requester);
    if (FTimerHandle* H = LeaseTimers.Find(Requester)) if (UWorld* W = GetWorld()) W->GetTimerManager().ClearTimer(*H);
    LeaseTimers.Remove(Requester);
    if (bWasActive) OnTokenChanged.Broadcast(Requester, false);
    GrantNext();
}

bool UNarisAttackTokenCoordinator::HasAttackToken(AActor* Requester) const
{
    return IsValid(Requester) && ActiveAttackers.Contains(Requester);
}

void UNarisAttackTokenCoordinator::ResetCoordinator()
{
    if (UWorld* W = GetWorld()) for (auto& Pair : LeaseTimers) W->GetTimerManager().ClearTimer(Pair.Value);
    ActiveAttackers.Reset(); WaitingQueue.Reset(); LeaseTimers.Reset();
}

void UNarisAttackTokenCoordinator::ExpireToken(TWeakObjectPtr<AActor> Requester)
{
    if (Requester.IsValid()) ReleaseAttackToken(Requester.Get());
    else { PurgeInvalid(); GrantNext(); }
}
void UNarisAttackTokenCoordinator::GrantNext()
{
    PurgeInvalid();
    while (ActiveAttackers.Num() < MaxSimultaneousAttackers && WaitingQueue.Num() > 0)
    {
        AActor* Next = WaitingQueue[0].Get();
        WaitingQueue.RemoveAt(0);
        if (IsValid(Next)) RequestAttackToken(Next);
    }
}

void UNarisAttackTokenCoordinator::PurgeInvalid()
{
    ActiveAttackers.RemoveAll([](const TObjectPtr<AActor>& A){ return !IsValid(A.Get()); });
    WaitingQueue.RemoveAll([](const TObjectPtr<AActor>& A){ return !IsValid(A.Get()); });
}

void UNarisAttackTokenCoordinator::ArmLease(AActor* Requester)
{
    if (!GetWorld() || !IsValid(Requester)) return;
    FTimerHandle& Handle = LeaseTimers.FindOrAdd(Requester);
    GetWorld()->GetTimerManager().ClearTimer(Handle);
    TWeakObjectPtr<AActor> WeakRequester(Requester);
    FTimerDelegate D; D.BindUObject(this, &UNarisAttackTokenCoordinator::ExpireToken, WeakRequester);
    GetWorld()->GetTimerManager().SetTimer(Handle, D, TokenLeaseSeconds, false);
}
