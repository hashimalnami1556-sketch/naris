#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisCameraFeedbackComponent.generated.h"
class UCameraComponent; class USpringArmComponent;
UCLASS(ClassGroup=(NARIS),meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisCameraFeedbackComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 UNarisCameraFeedbackComponent();
 virtual void BeginPlay() override;
 virtual void TickComponent(float DeltaTime,ELevelTick TickType,FActorComponentTickFunction* ThisTickFunction) override;
 UFUNCTION(BlueprintCallable) void PulseHit(float Strength=1.f);
 UFUNCTION(BlueprintCallable) void PulseParry();
 UFUNCTION(BlueprintCallable) void PulseDodge();
private:
 TWeakObjectPtr<UCameraComponent> Camera;
 TWeakObjectPtr<USpringArmComponent> SpringArm;
 float BaseFOV=90.f,BaseArm=420.f,FOVKick=0.f,ArmKick=0.f;
};