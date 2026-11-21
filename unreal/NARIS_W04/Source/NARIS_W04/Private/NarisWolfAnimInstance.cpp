#include "NarisWolfAnimInstance.h"

#include "GameFramework/Pawn.h"

void UNarisWolfAnimInstance::NativeInitializeAnimation()
{
    Super::NativeInitializeAnimation();
    SmoothedSpeed = 0.f;
}

void UNarisWolfAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    const APawn* PawnOwner = TryGetPawnOwner();
    const float ActualGroundSpeed = IsValid(PawnOwner) ?
        PawnOwner->GetVelocity().Size2D() : 0.f;

    SmoothedSpeed = FMath::FInterpTo(
        SmoothedSpeed,
        ActualGroundSpeed,
        FMath::Max(0.f, DeltaSeconds),
        FMath::Max(0.f, SpeedInterpolationRate));
}
