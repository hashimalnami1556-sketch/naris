#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisW04Types.h"
#include "NarisInteractable.h"
#include "BoneBeastBoss.generated.h"

class UBoneBeastDataAsset;
class UBoneBeastCombatComponent;
class UBoneBeastPhaseComponent;
class UNarisPresentationComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisBossEvent, FName, EventName);

UCLASS()
class NARIS_W04_API ABoneBeastBoss : public ACharacter, public INarisInteractable
{
    GENERATED_BODY()

public:
    ABoneBeastBoss();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    TObjectPtr<UBoneBeastCombatComponent> CombatPresentation;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    TObjectPtr<UBoneBeastPhaseComponent> PhasePresentation;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Presentation")
    TObjectPtr<UNarisPresentationComponent> Presentation;

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss")
    void StartEncounter();

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss")
    bool TryStartEncounter(AActor* InstigatorActor);

    virtual bool Interact_Implementation(AActor* InstigatorActor) override;
    virtual FText GetInteractionPrompt_Implementation() const override;

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss")
    void ResetEncounter();

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss")
    void ApplyDamageToEncounter(float Damage);

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss")
    void CompleteEncounter();

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss|Attack")
    bool RequestAttack(FName AttackId, float Damage);

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss|Attack")
    bool RequestPhaseAttack();

    UFUNCTION(BlueprintPure, Category="NARIS|Boss|Attack")
    float GetPendingAttackDamage() const { return PendingAttackDamage; }

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss|Attack")
    bool CommitAttackImpact(AActor* TargetActor);

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss|Attack")
    void CancelAttack();

    UFUNCTION(BlueprintPure, Category="NARIS|Boss")
    ENarisBossPhase GetPhase() const { return CurrentPhase; }

    UFUNCTION(BlueprintPure, Category="NARIS|Boss")
    float GetCurrentHealth() const { return CurrentHealth; }

    UFUNCTION(BlueprintPure, Category="NARIS|Boss")
    float GetConfiguredMaxHealth() const;

    UFUNCTION(BlueprintPure, Category="NARIS|Boss")
    bool IsEncounterActive() const { return bEncounterActive; }

    UFUNCTION(BlueprintPure, Category="NARIS|Boss")
    bool IsEncounterComplete() const { return bEncounterComplete; }

    UFUNCTION(BlueprintPure, Category="NARIS|Boss|Attack")
    FName GetPendingAttackId() const { return PendingAttackId; }

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    TObjectPtr<UBoneBeastDataAsset> BossData;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|SmokeFallback")
    float FallbackMaxHealth = 1800.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|SmokeFallback")
    float FallbackPhase2HealthPercent = 0.66f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|SmokeFallback")
    float FallbackPhase3HealthPercent = 0.33f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|SmokeFallback")
    FName FallbackQuestCompletionId = TEXT("Quest.W04.CorruptedHeart");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss")
    FString BossProgressId = TEXT("BoneBeast");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss")
    FString RequiredCompanionId = TEXT("CelestialWolf");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss")
    FString AutoSaveSlot = TEXT("NARIS_Auto");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss")
    bool bAutoSave = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss")
    bool bCompleteDemoOnDefeat = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|Attack")
    float Phase1AttackDamage = 18.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|Attack")
    float Phase2AttackDamage = 26.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|Attack")
    float Phase3AttackDamage = 34.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|Attack")
    bool bAutoAttack = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|Attack")
    float AttackIntervalSeconds = 2.4f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|Attack")
    float AttackRange = 520.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|SmokeFallback")
    bool bImmediateSmokeAttackImpact = true;

    UPROPERTY(BlueprintAssignable, Category="NARIS|Boss")
    FNarisBossEvent OnBossEvent;

protected:
    UPROPERTY(ReplicatedUsing=OnRep_CurrentHealth, VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    float CurrentHealth = 0.f;

    UPROPERTY(ReplicatedUsing=OnRep_CurrentPhase, VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    ENarisBossPhase CurrentPhase = ENarisBossPhase::Phase1;

    UPROPERTY(ReplicatedUsing=OnRep_EncounterActive, VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    bool bEncounterActive = false;

    UPROPERTY(ReplicatedUsing=OnRep_EncounterComplete, VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    bool bEncounterComplete = false;

private:
    UFUNCTION()
    void OnRep_CurrentHealth();

    UFUNCTION()
    void OnRep_CurrentPhase();

    UFUNCTION()
    void OnRep_EncounterActive();

    UFUNCTION()
    void OnRep_EncounterComplete();

    // Transient client-only previous HP for distinguishing initial replication
    // from subsequent combat damage. Not serialized or replicated.
    float LastReplicatedHealth = -1.f;

#if !UE_BUILD_SHIPPING
    bool bBossNetProbeApplied = false;
    float NextBossNetProbeLogTime = 0.f;
#endif

    FName PendingAttackId = NAME_None;
    float PendingAttackDamage = 0.f;
    float LastAttackRequestTime = -1000.f;

    void EvaluatePhase();
    void EmitBossEvent(FName EventName);
};
