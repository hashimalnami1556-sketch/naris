#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisAttackTokenCoordinator.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNarisAttackTokenChanged, AActor*, Actor, bool, bGranted);

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisAttackTokenCoordinator : public UActorComponent
{
    GENERATED_BODY()
public:
    UNarisAttackTokenCoordinator();
    UFUNCTION(BlueprintCallable) bool RequestAttackToken(AActor* Requester);
    UFUNCTION(BlueprintCallable) void ReleaseAttackToken(AActor* Requester);
    UFUNCTION(BlueprintPure) bool HasAttackToken(AActor* Requester) const;
    UFUNCTION(BlueprintPure) int32 GetActiveTokenCount() const { return ActiveAttackers.Num(); }
    UFUNCTION(BlueprintPure) int32 GetQueuedAttackerCount() const { return WaitingQueue.Num(); }
    UFUNCTION(BlueprintCallable) void ResetCoordinator();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|AI", meta=(ClampMin="1", ClampMax="8"))
    int32 MaxSimultaneousAttackers = 2;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|AI", meta=(ClampMin="0.25"))
    float TokenLeaseSeconds = 4.0f;
    UPROPERTY(BlueprintAssignable) FNarisAttackTokenChanged OnTokenChanged;
protected:
    virtual void BeginPlay() override;
private:
    UPROPERTY() TArray<TObjectPtr<AActor>> ActiveAttackers;
    UPROPERTY() TArray<TObjectPtr<AActor>> WaitingQueue;
    TMap<TWeakObjectPtr<AActor>, FTimerHandle> LeaseTimers;
    void ExpireToken(TWeakObjectPtr<AActor> Requester);
    void GrantNext();
    void PurgeInvalid();
    void ArmLease(AActor* Requester);
};
