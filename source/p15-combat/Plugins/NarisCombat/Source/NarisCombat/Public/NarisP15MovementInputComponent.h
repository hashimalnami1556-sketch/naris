#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisMoveInput.h"
#include "NarisP15MovementInputComponent.generated.h"

// اختياري: يستخدم بدلاً من AddMovementInput المباشر، وليس بالتوازي معه.
UCLASS(ClassGroup=(Naris), meta=(BlueprintSpawnableComponent))
class NARISCOMBAT_API UNarisP15MovementInputComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UNarisP15MovementInputComponent();
    UPROPERTY(EditDefaultsOnly, Category="Naris|Input") float DeadZone = .12f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Input") float ResponseExponent = 1.4f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Input") float ResponseSeconds = .04f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") bool bApplyMovementProfile = false;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") float YawDegreesPerSecond = 450.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") float Acceleration = 1600.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") float BrakingDeceleration = 1400.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") float BrakingFriction = 2.f;
    // X = right, Y = forward. Bind Triggered plus Completed/Canceled -> ResetMoveInput.
    UFUNCTION(BlueprintCallable, Category="Naris|Input") void SetMoveInput(FVector2D Value);
    UFUNCTION(BlueprintCallable, Category="Naris|Input") void ResetMoveInput();
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
protected:
    virtual void BeginPlay() override;
private:
    FVector2D RawInput = FVector2D::ZeroVector;
    NarisP15::MoveInputFilter Filter;
};
