#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisPlayerCharacter.generated.h"
class USpringArmComponent; class UCameraComponent; class UStaticMeshComponent;
class UNarisVitalsComponent; class UNarisInventoryComponent; class UNarisHitReactionComponent; class UNarisCameraFeedbackComponent; class UAnimSequence;
UCLASS()
class NARISCORE_API ANarisPlayerCharacter : public ACharacter
{
 GENERATED_BODY()
public:
 ANarisPlayerCharacter();
 virtual void Tick(float DeltaSeconds) override;
 virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
 virtual float TakeDamage(float DamageAmount,const FDamageEvent& DamageEvent,AController* EventInstigator,AActor* DamageCauser) override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisVitalsComponent> Vitals;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisInventoryComponent> Inventory;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisHitReactionComponent> HitReaction;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisCameraFeedbackComponent> CameraFeedback;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Visual;
 UFUNCTION(BlueprintPure) AActor* GetLockTarget() const { return LockTarget.Get(); }
private:
 UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> CameraBoom;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> FollowCamera;
 UPROPERTY() TObjectPtr<UAnimSequence> IdleAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> WalkAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> RunAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> ParryAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> ResonanceAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> AttackLightAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> AttackHeavyAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> DodgeAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> HitReactAnim;
 TWeakObjectPtr<AActor> LockTarget;
 bool bBlocking=false;
 float ParryWindow=0.f,ComboReset=0.f,AttackAnimTime=0.f;
 int32 ComboIndex=0,AnimState=-1;
 void MoveForward(float Value); void MoveRight(float Value); void Turn(float Value); void LookUp(float Value);
 void StartGame(); void TogglePause(); void QuitGame(); void Attack(); void Dodge(); void Resonance(); void ToggleLock(); void BlockPressed(); void BlockReleased(); void QuickSave(); void QuickLoad(); void UpdateLocomotionAnimation();
};