#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisW04Types.h"
#include "NarisInteractable.h"
#include "BoneBeastBoss.generated.h"

class UBoneBeastDataAsset;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisBossEvent, FName, EventName);

UCLASS()
class NARIS_W04_API ABoneBeastBoss : public ACharacter, public INarisInteractable
{
    GENERATED_BODY()

public:
    ABoneBeastBoss();

    virtual void BeginPlay() override;

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

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    TObjectPtr<UBoneBeastDataAsset> BossData;

    // Smoke/runtime fallback used only when no authored BoneBeastDataAsset is assigned.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|SmokeFallback")
    float FallbackMaxHealth = 1800.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|SmokeFallback")
    float FallbackPhase2HealthPercent = 0.66f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|SmokeFallback")
    float FallbackPhase3HealthPercent = 0.33f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Boss|SmokeFallback")
    FName FallbackQuestCompletionId = TEXT("W04_CorruptedHeart");

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

    UPROPERTY(BlueprintAssignable, Category="NARIS|Boss")
    FNarisBossEvent OnBossEvent;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    float CurrentHealth = 0.f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    ENarisBossPhase CurrentPhase = ENarisBossPhase::Phase1;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    bool bEncounterActive = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    bool bEncounterComplete = false;

private:
    void EvaluatePhase();
    void EmitBossEvent(FName EventName);
};
