#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisMoveInput.h"
#include "NarisControlMotion.h"
#include "NarisP15MovementInputComponent.generated.h"

class ACharacter;
class UCharacterMovementComponent;
class USpringArmComponent;
class UNarisP15CombatComponent;

// Attach explicitly to a P15 test Character. This is its sole movement-input producer.
UCLASS(ClassGroup=(Naris), meta=(BlueprintSpawnableComponent))
class NARISCOMBAT_API UNarisP15MovementInputComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UNarisP15MovementInputComponent();
    UPROPERTY(EditDefaultsOnly, Category="Naris|Input") float DeadZone = .12f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Input") float ResponseExponent = 1.4f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Input") float ResponseSeconds = .025f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") bool bApplyMovementProfile = true;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") float WalkSpeed = 400.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") float Acceleration = 1600.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") float BrakingDeceleration = 1000.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") float GroundFriction = 5.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Movement") float BrakingFriction = 2.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Rotation") bool bManageRotation = true;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Rotation") float YawDegreesPerSecond = 450.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Rotation") float LockYawAcceleration = 1800.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Rotation") float MaxLockRange = 2500.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Camera") bool bApplyCameraProfile = true;
    // None accepts exactly one SpringArm; otherwise choose the exact component name.
    UPROPERTY(EditDefaultsOnly, Category="Naris|Camera") FName CameraBoomComponentName = NAME_None;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Camera") float FreeCameraLagSpeed = 6.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Camera") float FreeCameraRotationLagSpeed = 8.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Camera") float CombatCameraLagSpeed = 18.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Camera") float CombatCameraRotationLagSpeed = 20.f;

    // X = right, Y = forward. Triggered updates; Completed/Canceled must reset.
    UFUNCTION(BlueprintCallable, Category="Naris|Input") void SetMoveInput(FVector2D Value);
    UFUNCTION(BlueprintCallable, Category="Naris|Input") void ResetMoveInput();
    UFUNCTION(BlueprintCallable, Category="Naris|Control") void SetCombatMode(bool bEnabled);
    UFUNCTION(BlueprintCallable, Category="Naris|Control") void SetLockOnTarget(AActor* Target);
    UFUNCTION(BlueprintPure, Category="Naris|Control") bool IsInCombatMode() const;
    UFUNCTION(BlueprintPure, Category="Naris|Control") AActor* GetLockOnTarget() const { return LockOnTarget.Get(); }
    UFUNCTION(BlueprintPure, Category="Naris|Control") TArray<FString> GetSetupIssues() const;

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    UFUNCTION(Server, Reliable) void ServerSetCombatMode(bool bEnabled);
    UFUNCTION(Server, Reliable) void ServerSetLockOnTarget(AActor* Target);
    UFUNCTION() void OnRep_ControlMode();
private:
    UPROPERTY(ReplicatedUsing=OnRep_ControlMode) bool bCombatMode = false;
    UPROPERTY(ReplicatedUsing=OnRep_ControlMode) TObjectPtr<AActor> LockOnTarget;
    TWeakObjectPtr<UNarisP15CombatComponent> Combat;
    TWeakObjectPtr<UCharacterMovementComponent> ManagedMovement;
    TWeakObjectPtr<USpringArmComponent> CameraBoom;
    FVector2D RawInput = FVector2D::ZeroVector;
    NarisP15::MoveInputFilter Filter;
    NarisP15::YawDriver Facing;
    bool bProfileReady = false;
    bool bCapturedCamera = false;
    bool bOriginalControllerYaw = false;
    bool bOriginalOrient = false, bOriginalDesired = false, bOriginalSeparateBraking = false;
    float OriginalSpeed = 0.f, OriginalAcceleration = 0.f, OriginalBraking = 0.f;
    float OriginalGroundFriction = 0.f, OriginalBrakingFriction = 0.f;
    FRotator OriginalRotationRate = FRotator::ZeroRotator;
    bool bOriginalCameraLag = false, bOriginalCameraRotationLag = false, bOriginalSubstepping = false;
    float OriginalCameraLagSpeed = 0.f, OriginalCameraRotationLagSpeed = 0.f, OriginalCameraTimeStep = 0.f;
    bool IsValidLockTarget(AActor* Target) const;
    bool IsMotionConfigurationValid() const;
    USpringArmComponent* ResolveCameraBoom() const;
    void RefreshRotationMode(ACharacter* Character);
};
