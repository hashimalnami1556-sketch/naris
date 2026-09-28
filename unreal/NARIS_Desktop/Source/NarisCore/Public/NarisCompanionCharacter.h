#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisCompanionCharacter.generated.h"
class UStaticMeshComponent;
class UAnimSequence;

UCLASS()
class NARISCORE_API ANarisCompanionCharacter : public ACharacter
{
 GENERATED_BODY()
public:
 ANarisCompanionCharacter();
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Visual;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float FollowDistance=260.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float AssistRange=700.f;
private:
 UPROPERTY() TObjectPtr<UAnimSequence> IdleAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> RunAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> BiteAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> SoulVisionAnim;
 float SoulVisionCooldown=4.f;
 float AttackCooldown=0.f;
 float AttackAnimTime=0.f;
 int32 AnimState=-1;
 void SetAnim(UAnimSequence* Anim,bool bLoop,int32 State);
};