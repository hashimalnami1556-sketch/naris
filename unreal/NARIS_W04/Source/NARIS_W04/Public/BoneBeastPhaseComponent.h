#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisW04Types.h"
#include "BoneBeastPhaseComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisPhaseEvent, FName, PhaseId);

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UBoneBeastPhaseComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    // Presentation/integration mirror only. ABoneBeastBoss remains the authority for phase state.
    UFUNCTION(BlueprintCallable, Category="NARIS|Boss")
    void SetAuthoritativePhase(ENarisBossPhase NewPhase);

    UFUNCTION(BlueprintPure, Category="NARIS|Boss")
    ENarisBossPhase GetMirroredPhase() const { return MirroredPhase; }

    UPROPERTY(BlueprintAssignable, Category="NARIS|Boss")
    FNarisPhaseEvent OnPhaseTransition;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Boss", meta=(AllowPrivateAccess="true"))
    ENarisBossPhase MirroredPhase = ENarisBossPhase::Phase1;
};
