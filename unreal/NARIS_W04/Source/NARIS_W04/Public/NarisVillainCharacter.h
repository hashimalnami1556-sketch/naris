#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisGameplayTypes.h"
#include "NarisVillainCharacter.generated.h"

class UNarisCombatComponent;
class UStaticMeshComponent;
class AAIController;
struct FDamageEvent;

UENUM(BlueprintType)
enum class ENarisVillainState : uint8
{
    Patrol, Chase, Windup, Recovery, Staggered, Dead
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisVillainDefeatEvent, FName, VillainId);

/**
 * W04 interactive enemy foundation.
 * Gameplay is native; appearance, montages and impact cues are authoring hooks.
 * The cube is an explicit development-only visual, not an approved NARIS asset.
 */
UCLASS(Blueprintable)
class NARIS_W04_API ANarisVillainCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    ANarisVillainCharacter();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual float TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent,
        AController* EventInstigator, AActor* DamageCauser) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Villain")
    FName VillainId = TEXT("AshWretch");

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Villain")
    TObjectPtr<UNarisCombatComponent> Combat;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Villain|Development")
    TObjectPtr<UStaticMeshComponent> DevelopmentVisual;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Villain|Development")
    bool bUseTimedSmokeAttackImpact = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Villain|Movement")
    float DetectionRange = 1000.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Villain|Movement")
    float LeashRange = 1600.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Villain|Movement")
    float PatrolRadius = 450.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Villain|Combat")
    float AttackRange = 200.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Villain|Combat")
    float AttackDamage = 15.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Villain|Combat")
    float AttackWindupSeconds = 0.7f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Villain|Combat")
    float AttackRecoverySeconds = 1.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Villain|Combat")
    bool bHasSecondPhase = false;

    UPROPERTY(BlueprintReadOnly, Category="NARIS|Villain")
    bool bSecondPhase = false;

    UPROPERTY(BlueprintReadOnly, Category="NARIS|Villain")
    ENarisVillainState VillainState = ENarisVillainState::Patrol;

    UPROPERTY(BlueprintAssignable, Category="NARIS|Villain")
    FNarisVillainDefeatEvent OnVillainDefeated;

    /** Call from an animation notify in the authored montage; only one hit per windup. */
    UFUNCTION(BlueprintCallable, Category="NARIS|Villain|Animation")
    bool CommitAttackImpact();

    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|Villain|Animation")
    void OnVillainStateChanged(ENarisVillainState NewState);

    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|Villain|Animation")
    void OnVillainAttackRequested(bool bPhaseTwo);

    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|Villain|Animation")
    void OnVillainDamaged(float DamageTaken, bool bStaggered);

    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|Villain|Animation")
    void OnVillainPhaseTwo();

    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|Villain|Animation")
    void OnVillainDeath();

private:
    UFUNCTION()
    void HandleCombatResolved(FNarisCombatResult Result);

    void ApplyArchetype();
    void ChangeState(ENarisVillainState NewState);
    void StopAI();
    void Die();
    void UpdatePatrol(float Now);
    void UpdateEngagement(float Now);

    FVector HomeLocation = FVector::ZeroVector;
    TWeakObjectPtr<APawn> TargetPlayer;
    float NextMoveOrderTime = 0.f;
    float NextPatrolTime = 0.f;
    float WindupEndTime = 0.f;
    float RecoveryEndTime = 0.f;
    float StaggerEndTime = 0.f;
    bool bPendingImpact = false;
    bool bImpactCommitted = false;
};