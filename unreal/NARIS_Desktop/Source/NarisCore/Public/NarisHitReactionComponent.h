#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisHitReactionComponent.generated.h"
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FNarisHitReacted,float,Damage,FVector,Direction,float,Strength);
UCLASS(ClassGroup=(NARIS),meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisHitReactionComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 UNarisHitReactionComponent();
 virtual void TickComponent(float DeltaTime,ELevelTick TickType,FActorComponentTickFunction* ThisTickFunction) override;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float LightHitThreshold=20.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float HeavyHitThreshold=40.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float ReactionCooldown=.18f;
 UPROPERTY(BlueprintReadOnly) float LastStrength=0.f;
 UPROPERTY(BlueprintReadOnly) FVector LastDirection=FVector::ZeroVector;
 UPROPERTY(BlueprintAssignable) FNarisHitReacted OnHitReacted;
 UFUNCTION(BlueprintCallable) float ReactToHit(float Damage,AActor* DamageCauser);
private:
 float CooldownRemaining=0.f;
};