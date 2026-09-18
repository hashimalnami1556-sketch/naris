#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisBossPhaseComponent.generated.h"
UENUM(BlueprintType) enum class ENarisBossPhase:uint8 { Phase1, Phase2, Phase3, Defeated };
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisBossPhaseEvent,ENarisBossPhase,Phase);
UCLASS(ClassGroup=(NARIS),Blueprintable,meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UNarisBossPhaseComponent:public UActorComponent
{
 GENERATED_BODY()
public:
 UNarisBossPhaseComponent();
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Boss") float Phase2HealthPercent=.66f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Boss") float Phase3HealthPercent=.33f;
 UPROPERTY(BlueprintReadOnly,Category="Boss") ENarisBossPhase CurrentPhase=ENarisBossPhase::Phase1;
 UPROPERTY(BlueprintAssignable) FNarisBossPhaseEvent OnPhaseChanged;
 UFUNCTION(BlueprintCallable,Category="NARIS|Boss") void UpdatePhase(float Health,float MaxHealth);
 UFUNCTION(BlueprintCallable,Category="NARIS|Boss") void Defeat();
};
