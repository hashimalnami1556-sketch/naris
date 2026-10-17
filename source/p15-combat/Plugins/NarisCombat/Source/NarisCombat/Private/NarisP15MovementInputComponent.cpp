#include "NarisP15MovementInputComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"

UNarisP15MovementInputComponent::UNarisP15MovementInputComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

void UNarisP15MovementInputComponent::BeginPlay()
{
    Super::BeginPlay();
    ACharacter* Character = Cast<ACharacter>(GetOwner());
    if (!Character) { SetComponentTickEnabled(false); return; }
    UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
    Movement->AddTickPrerequisiteComponent(this);
    if (bApplyMovementProfile)
    {
        const float Values[] = {YawDegreesPerSecond, Acceleration, BrakingDeceleration, BrakingFriction};
        for (float Value : Values)
            if (!FMath::IsFinite(Value) || Value <= 0.f)
            {
                UE_LOG(LogTemp, Error, TEXT("NARIS movement profile rejected: values must be finite and positive."));
                return;
            }
        Character->bUseControllerRotationYaw = false;
        Movement->bOrientRotationToMovement = true;
        Movement->RotationRate = FRotator(0.f, YawDegreesPerSecond, 0.f);
        Movement->MaxAcceleration = Acceleration;
        Movement->BrakingDecelerationWalking = BrakingDeceleration;
        Movement->bUseSeparateBrakingFriction = true;
        Movement->BrakingFriction = BrakingFriction;
    }
}

void UNarisP15MovementInputComponent::SetMoveInput(FVector2D Value)
{
    RawInput = Value.ContainsNaN() ? FVector2D::ZeroVector : Value;
}

void UNarisP15MovementInputComponent::ResetMoveInput()
{
    RawInput = FVector2D::ZeroVector;
    Filter.Reset();
}

void UNarisP15MovementInputComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    ACharacter* Character = Cast<ACharacter>(GetOwner());
    if (!Character || !Character->IsLocallyControlled() || !Character->GetController()
        || Character->IsMoveInputIgnored() || !Character->GetCharacterMovement()->IsMovingOnGround())
    { ResetMoveInput(); return; }
    const NarisP15::MoveInput Input = Filter.Step({RawInput.X, RawInput.Y}, DeltaTime,
        DeadZone, ResponseExponent, ResponseSeconds);
    const FRotator Yaw(0.f, Character->GetController()->GetControlRotation().Yaw, 0.f);
    Character->AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::X), Input.Y);
    Character->AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y), Input.X);
}
