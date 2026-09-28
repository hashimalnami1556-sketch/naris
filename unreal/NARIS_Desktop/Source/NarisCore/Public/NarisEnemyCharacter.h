#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisEnemyCharacter.generated.h"
class UNarisVitalsComponent; class UNarisHitReactionComponent; class UStaticMeshComponent; class UAnimSequence;
UCLASS()
class NARISCORE_API ANarisEnemyCharacter : public ACharacter
{
 GENERATED_BODY()
public:
 ANarisEnemyCharacter();
 virtual void Tick(float DeltaSeconds) override;
 virtual float TakeDamage(float DamageAmount,const FDamageEvent& DamageEvent,AController* EventInstigator,AActor* DamageCauser) override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisVitalsComponent> Vitals;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisHitReactionComponent> HitReaction;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Visual;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float AggroRange=1600.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float AttackRange=165.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float AttackDamage=12.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float AttackCooldown=1.2f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FName PersistentID=NAME_None;
 UFUNCTION(BlueprintCallable) void ApplyPersistentState();
protected:
 bool bDeathReported=false;
 bool bCountsAsRegularEnemy=true;
 virtual FName GetDefeatNarrativeTarget() const { return FName("BoneBeast"); }
private:
 UPROPERTY() TObjectPtr<UAnimSequence> IdleAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> RunAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> AttackAnim;
 UPROPERTY() TObjectPtr<UAnimSequence> StunnedAnim;
 float Cooldown=0.f,AttackAnimTime=0.f;
 bool bAttackTokenHeld=false;
 int32 AnimState=-1;
 bool TryAcquireAttackToken();
 void ReleaseAttackToken();
 void SetAnim(UAnimSequence* Anim,bool bLoop,int32 State);
 FName PersistenceFlag() const;
};