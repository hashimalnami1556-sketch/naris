#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisLockOnComponent.generated.h"
UCLASS(ClassGroup=(NARIS), Blueprintable, meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UNarisLockOnComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UNarisLockOnComponent();
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="LockOn") float MaxDistance=1800.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="LockOn") float MaxAngleDegrees=70.f;
    UPROPERTY(BlueprintReadOnly, Category="LockOn") TObjectPtr<AActor> Target;
    UFUNCTION(BlueprintCallable, Category="NARIS|LockOn") bool AcquireTarget();
    UFUNCTION(BlueprintCallable, Category="NARIS|LockOn") void ClearTarget();
    UFUNCTION(BlueprintPure, Category="NARIS|LockOn") bool HasTarget() const { return IsValid(Target); }
};
