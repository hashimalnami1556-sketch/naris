#include "NarisP15LocomotionAnimInstance.h"
#include "NarisP15MovementInputComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"

void UNarisP15LocomotionAnimInstance::NativeInitializeAnimation()
{
    Super::NativeInitializeAnimation();
    Signals.Reset();
}

void UNarisP15LocomotionAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);
    ACharacter* Character = Cast<ACharacter>(TryGetPawnOwner());
    UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
    Speed = DirectionDegrees = LeanDegrees = FacingYawDelta = 0.f;
    bStarting = bStopping = bPivoting = bFalling = bInCombat = bShouldTurnInPlace = false;
    ControlPhase = ENarisP15ControlPhase::Unavailable;
    if (!Movement || !FMath::IsFinite(DeltaSeconds) || DeltaSeconds <= 0.f)
    { Signals.Reset(); return; }
    const FTransform Transform = Character->GetActorTransform();
    const FVector Velocity = Transform.InverseTransformVectorNoScale(Character->GetVelocity());
    const FVector Acceleration = Transform.InverseTransformVectorNoScale(Movement->GetCurrentAcceleration());
    const auto Sample = Signals.Step(Velocity.X, Velocity.Y, Acceleration.X, Acceleration.Y,
        Movement->IsFalling(), DeltaSeconds);
    Speed = Sample.Speed;
    DirectionDegrees = Sample.DirectionDegrees;
    LeanDegrees = Sample.LeanDegrees;
    bStarting = Sample.Starting;
    bStopping = Sample.Stopping;
    bPivoting = Sample.Pivoting;
    bFalling = Sample.Falling;
    if (const auto* Combat = Character->FindComponentByClass<UNarisP15CombatComponent>())
        ControlPhase = Combat->ControlPhase;
    else ControlPhase = ENarisP15ControlPhase::Free;
    if (const auto* Controls = Character->FindComponentByClass<UNarisP15MovementInputComponent>())
        bInCombat = Controls->IsInCombatMode();
    if (Character->GetController())
        FacingYawDelta = NarisP15::ShortestYawDelta(Character->GetActorRotation().Yaw,
            Character->GetController()->GetControlRotation().Yaw);
    bShouldTurnInPlace = bInCombat && ControlPhase == ENarisP15ControlPhase::Free && !bFalling
        && Speed < 15.f && FMath::Abs(FacingYawDelta) > 75.f;
}
