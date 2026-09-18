#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "BoneBeast.generated.h"
class UNarisCombatComponent; class UNarisBossPhaseComponent;
UCLASS(Blueprintable)
class NARIS_W04_API ABoneBeast:public ACharacter
{
 GENERATED_BODY()
public:
 ABoneBeast();
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisCombatComponent> Combat;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisBossPhaseComponent> Phases;
 virtual void Tick(float DeltaSeconds) override;
};
