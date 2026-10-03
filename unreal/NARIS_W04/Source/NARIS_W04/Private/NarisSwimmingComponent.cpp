#include "NarisSwimmingComponent.h"

#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "NarisCombatComponent.h"
#include "NarisWaterVolume.h"

UNarisSwimmingComponent::UNarisSwimmingComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.bStartWithTickEnabled = false;
}

void UNarisSwimmingComponent::BeginPlay()
{
    Super::BeginPlay();

    CharacterOwner = Cast<ACharacter>(GetOwner());
    if (ACharacter* Character = CharacterOwner.Get())
    {
        Combat = Character->FindComponentByClass<UNarisCombatComponent>();
    }

    BreathRemaining = FMath::Max(0.1f, MaxBreath);
}

void UNarisSwimmingComponent::EnterWater(ANarisWaterVolume* WaterVolume)
{
    if (!IsValid(WaterVolume))
    {
        return;
    }

    ActiveWaterVolume = WaterVolume;
    bSwimming = true;
    SetComponentTickEnabled(true);

    if (ACharacter* Character = CharacterOwner.Get())
    {
        if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
        {
            Movement->MaxSwimSpeed = SwimSpeed;
            Movement->SetMovementMode(MOVE_Swimming);
        }
    }
}

void UNarisSwimmingComponent::ExitWater(ANarisWaterVolume* WaterVolume)
{
    if (ActiveWaterVolume.IsValid() && WaterVolume != ActiveWaterVolume.Get())
    {
        return;
    }

    ActiveWaterVolume.Reset();
    bSwimming = false;
    bUnderwater = false;
    VerticalInput = 0.f;
    BreathRemaining = FMath::Max(0.1f, MaxBreath);

    if (ACharacter* Character = CharacterOwner.Get())
    {
        if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
        {
            Movement->SetMovementMode(MOVE_Walking);
        }
    }

    SetComponentTickEnabled(false);
}

void UNarisSwimmingComponent::SetVerticalSwimInput(float Value)
{
    VerticalInput = FMath::Clamp(Value, -1.f, 1.f);
}

float UNarisSwimmingComponent::GetBreathPercent() const
{
    return MaxBreath > KINDA_SMALL_NUMBER
        ? FMath::Clamp(BreathRemaining / MaxBreath, 0.f, 1.f)
        : 0.f;
}

void UNarisSwimmingComponent::TickComponent(
    float DeltaTime,
    ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction
)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!bSwimming || !ActiveWaterVolume.IsValid())
    {
        return;
    }

    UpdateWaterState(DeltaTime);
    ApplyCurrent(DeltaTime);
    ApplyDrowning(DeltaTime);
}

void UNarisSwimmingComponent::UpdateWaterState(float DeltaTime)
{
    ACharacter* Character = CharacterOwner.Get();
    ANarisWaterVolume* Water = ActiveWaterVolume.Get();
    if (!Character || !Water)
    {
        return;
    }

    const float HeadZ = Character->GetActorLocation().Z + HeadHeightOffset;
    bUnderwater = HeadZ < Water->GetSurfaceWorldZ();

    if (bUnderwater)
    {
        BreathRemaining = FMath::Max(
            0.f,
            BreathRemaining - DeltaTime
        );
    }
    else
    {
        BreathRemaining = FMath::Min(
            FMath::Max(0.1f, MaxBreath),
            BreathRemaining + BreathRecoveryPerSecond * DeltaTime
        );
    }

    if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
    {
        const float VerticalVelocity = VerticalInput * VerticalSwimSpeed;
        Movement->Velocity.Z = FMath::FInterpTo(
            Movement->Velocity.Z,
            VerticalVelocity,
            DeltaTime,
            5.f
        );
    }
}

void UNarisSwimmingComponent::ApplyCurrent(float DeltaTime)
{
    ACharacter* Character = CharacterOwner.Get();
    ANarisWaterVolume* Water = ActiveWaterVolume.Get();
    if (!Character || !Water || Water->CurrentStrength <= 0.f)
    {
        return;
    }

    const FVector Current = Water->GetCurrentWorldDirection() * Water->CurrentStrength;
    Character->AddMovementInput(Current.GetSafeNormal(), Current.Size() * DeltaTime);
}

void UNarisSwimmingComponent::ApplyDrowning(float DeltaTime)
{
    if (!bUnderwater || BreathRemaining > 0.f)
    {
        return;
    }

    if (UNarisCombatComponent* CombatComponent = Combat.Get())
    {
        CombatComponent->Health = FMath::Max(
            0.f,
            CombatComponent->Health - DrowningDamagePerSecond * DeltaTime
        );
    }
}
