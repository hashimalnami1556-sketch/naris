#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisStage30CombatComponent.generated.h"
UENUM(BlueprintType)
enum class ENarisCombatAction : uint8 { Idle, Attacking, Dodging, Recovering, Dead };
UCLASS(ClassGroup=(Naris), meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UNarisStage30CombatComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UNarisStage30CombatComponent();
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Naris|Combat") float MaxHealth=100.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Naris|Combat") float Health=100.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Naris|Combat") float MaxStamina=100.f;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Naris|Combat") float Stamina=100.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Naris|Combat") float AttackCost=20.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Naris|Combat") float DodgeCost=25.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Naris|Combat") float RegenPerSecond=18.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Naris|Combat") float AttackDamage=25.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Naris|Combat") float AttackReachCm=180.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Naris|Combat") float RecoverySeconds=.38f;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Naris|Combat") ENarisCombatAction Action=ENarisCombatAction::Idle;
 UFUNCTION(BlueprintCallable,Category="Naris|Combat") bool TryAttack();
 UFUNCTION(BlueprintCallable,Category="Naris|Combat") bool TryDodge();
 UFUNCTION(BlueprintCallable,Category="Naris|Combat") void OpenDamageWindow();
 UFUNCTION(BlueprintCallable,Category="Naris|Combat") void CloseDamageWindow();
 UFUNCTION(BlueprintCallable,Category="Naris|Combat") void InterruptAction();
 UFUNCTION(BlueprintCallable,Category="Naris|Combat") void ReceiveCombatDamage(float Damage);
 virtual void TickComponent(float DeltaTime,ELevelTick TickType,FActorComponentTickFunction* ThisTickFunction) override;
protected:
 virtual void BeginPlay() override;
private:
 float RecoveryLeft=0.f;
 bool bDamageWindowOpen=false;
 TSet<TWeakObjectPtr<AActor>> HitActors;
};