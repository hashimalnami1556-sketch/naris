#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisW04Types.h"
#include "BoneBeastBoss.generated.h"

class UBoneBeastDataAsset;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisBossEvent, FName, EventName);

UCLASS()
class NARIS_W04_API ABoneBeastBoss : public ACharacter
{
    GENERATED_BODY()

public:
    ABoneBeastBoss();

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss")
    void StartEncounter();

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss")
    void ApplyDamageToEncounter(float Damage);

    UFUNCTION(BlueprintCallable, Category="NARIS|Boss")
    void CompleteEncounter();

    UFUNCTION(BlueprintPure, Category="NARIS|Boss")
    ENarisBossPhase GetPhase() const { return CurrentPhase; }

    UFUNCTION(BlueprintPure, Category="NARIS|Boss")
    float GetCurrentHealth() const { return CurrentHealth; }

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    TObjectPtr<UBoneBeastDataAsset> BossData;

    UPROPERTY(BlueprintAssignable, Category="NARIS|Boss")
    FNarisBossEvent OnBossEvent;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    float CurrentHealth = 0.f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    ENarisBossPhase CurrentPhase = ENarisBossPhase::Phase1;

private:
    void EvaluatePhase();
    void EmitBossEvent(FName EventName);
};
