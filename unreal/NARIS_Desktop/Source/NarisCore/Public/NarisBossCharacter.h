#pragma once
#include "CoreMinimal.h"
#include "NarisEnemyCharacter.h"
#include "NarisBossCharacter.generated.h"
class UNarisBossPhaseComponent;
class UAnimSequence;

UCLASS()
class NARISCORE_API ANarisBossCharacter : public ANarisEnemyCharacter
{
 GENERATED_BODY()
public:
 ANarisBossCharacter();
 virtual float TakeDamage(float DamageAmount,const FDamageEvent& DamageEvent,AController* EventInstigator,AActor* DamageCauser) override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisBossPhaseComponent> Phase;
protected:
 virtual FName GetDefeatNarrativeTarget() const override { return FName("GateWarden"); }
private:
 bool bBossDeathReported=false;
 UPROPERTY() TObjectPtr<UAnimSequence> EnrageAnim;
};