#pragma once

// NARIS W04 scaffold contract.
// Intended for migration into the Unreal C++ source tree.

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "BoneBeastBossController.generated.h"

UENUM(BlueprintType)
enum class ENarisBossPhase : uint8
{
    Phase1,
    Phase2,
    Phase3,
    Dead
};

UCLASS()
class NARIS_API ABoneBeastBossController : public ACharacter
{
    GENERATED_BODY()

public:
    ABoneBeastBossController();

    UFUNCTION(BlueprintCallable)
    void StartEncounter();

    UFUNCTION(BlueprintCallable)
    void ApplyEncounterDamage(float Damage);

    UFUNCTION(BlueprintCallable)
    void CompleteEncounter();

    UFUNCTION(BlueprintPure)
    ENarisBossPhase GetPhase() const { return CurrentPhase; }

protected:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    float MaxHealth = 0.0f; // TUNE

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    float CurrentHealth = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    ENarisBossPhase CurrentPhase = ENarisBossPhase::Phase1;

    UFUNCTION(BlueprintImplementableEvent)
    void OnBossEvent(FName EventName);

private:
    void EvaluatePhase();
    void EmitBossEvent(FName EventName);
};
