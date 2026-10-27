#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisStage32CombatComponent.generated.h"

class UAnimMontage;
class UAnimInstance;
class USkeletalMeshComponent;

UENUM(BlueprintType)
enum class ENarisCombatState : uint8 { Idle, Attack, Dodge, Recovery, Dead };

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNarisVitalsChanged, float, Health, float, Stamina);

UCLASS(ClassGroup=(Naris), meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UNarisStage32CombatComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 UNarisStage32CombatComponent();
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Naris|Vitals") float MaxHealth=100.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Naris|Vitals") float MaxStamina=100.f;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Naris|Vitals") float Health=100.f;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Naris|Vitals") float Stamina=100.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Naris|Combat") float AttackCost=22.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Naris|Combat") float DodgeCost=28.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Naris|Combat") float AttackDamage=30.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Naris|Combat") float AttackReachCm=175.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Naris|Combat") float AttackRadiusCm=45.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Naris|Combat") float DodgeInvulnerabilitySeconds=.18f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Naris|Combat") float RecoverySeconds=.28f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Naris|Combat") float StaminaRegenPerSecond=18.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Naris|Combat") int32 TeamId=0;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Naris|Combat") bool bAllowFriendlyFire=false;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Naris|Combat") ENarisCombatState State=ENarisCombatState::Idle;
 UPROPERTY(BlueprintAssignable, Category="Naris|Combat") FNarisVitalsChanged OnVitalsChanged;
 UFUNCTION(BlueprintCallable, Category="Naris|Combat") bool StartAttack(USkeletalMeshComponent* Mesh, UAnimMontage* Montage);
 UFUNCTION(BlueprintCallable, Category="Naris|Combat") bool StartDodge(USkeletalMeshComponent* Mesh, UAnimMontage* Montage);
 UFUNCTION(BlueprintCallable, Category="Naris|Combat") void BeginHitWindow();
 UFUNCTION(BlueprintCallable, Category="Naris|Combat") void EndHitWindow();
 UFUNCTION(BlueprintCallable, Category="Naris|Combat") void CancelAction();
 UFUNCTION(BlueprintCallable, Category="Naris|Combat") void ReceiveDamageAmount(float Amount);
 UFUNCTION(BlueprintPure, Category="Naris|Combat") bool CanReceiveDamage() const;
 virtual void TickComponent(float DeltaTime,ELevelTick TickType,FActorComponentTickFunction* ThisTickFunction) override;
protected:
 virtual void BeginPlay() override;
 virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
private:
 UFUNCTION() void OnMontageEnded(UAnimMontage* Montage, bool bInterrupted);
 UPROPERTY(Transient) TObjectPtr<UAnimInstance> ActiveAnimInstance=nullptr;
 UPROPERTY(Transient) TObjectPtr<UAnimMontage> ActiveMontage=nullptr;
 float StateAge=0.f;
 bool bHitWindow=false;
 TSet<TWeakObjectPtr<AActor>> AlreadyHit;
 bool TryPlay(USkeletalMeshComponent* Mesh,UAnimMontage* Montage,float Cost,ENarisCombatState Next);
 void EnterRecovery();
 void ClearActiveMontageBinding();
 void EmitVitals();
};
