#include "NarisP15MovementInputComponent.h"
#include "NarisP15CombatComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/SpringArmComponent.h"
#include "Net/UnrealNetwork.h"
#include "HAL/PlatformTime.h"
#include "Kismet/GameplayStatics.h"

namespace
{
bool Positive(float Value) { return FMath::IsFinite(Value) && Value > 0.f; }
bool NonNegative(float Value) { return FMath::IsFinite(Value) && Value >= 0.f; }
}

UNarisP15MovementInputComponent::UNarisP15MovementInputComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.bTickEvenWhenPaused = true;
    PrimaryComponentTick.TickGroup = TG_PrePhysics;
    SetIsReplicatedByDefault(true);
}

bool UNarisP15MovementInputComponent::IsMotionConfigurationValid() const
{
    return NarisP15::MoveInputFilter::Valid(DeadZone, ResponseExponent, ResponseSeconds)
        && NarisP15::MoveInputLease::ValidTimeout(InputTimeoutSeconds)
        && (!bApplyMovementProfile || (Positive(WalkSpeed) && Positive(Acceleration)
            && Positive(BrakingDeceleration) && NonNegative(GroundFriction) && NonNegative(BrakingFriction)))
        && (!bManageRotation || (Positive(YawDegreesPerSecond) && Positive(LockYawAcceleration)))
        && Positive(MaxLockRange);
}

USpringArmComponent* UNarisP15MovementInputComponent::ResolveCameraBoom() const
{
    if (!GetOwner()) return nullptr;
    TArray<USpringArmComponent*> Booms;
    GetOwner()->GetComponents<USpringArmComponent>(Booms);
    if (CameraBoomComponentName.IsNone()) return Booms.Num() == 1 ? Booms[0] : nullptr;
    for (USpringArmComponent* Boom : Booms)
        if (Boom && Boom->GetFName() == CameraBoomComponentName) return Boom;
    return nullptr;
}

TArray<FString> UNarisP15MovementInputComponent::GetSetupIssues() const
{
    TArray<FString> Issues;
    const ACharacter* Character = Cast<ACharacter>(GetOwner());
    if (!Character || !Character->GetCharacterMovement())
        Issues.Add(TEXT("Naris movement input requires an ACharacter with CharacterMovement."));
    if (!IsMotionConfigurationValid())
        Issues.Add(TEXT("Invalid input response, movement profile, rotation limit or lock range."));
    if (bApplyCameraProfile)
    {
        if (!ResolveCameraBoom()) Issues.Add(TEXT("Choose one existing SpringArm by exact component name, or disable the camera profile."));
        if (!Positive(FreeCameraLagSpeed) || !Positive(FreeCameraRotationLagSpeed)
            || !Positive(CombatCameraLagSpeed) || !Positive(CombatCameraRotationLagSpeed))
            Issues.Add(TEXT("Camera lag speeds must be finite and positive; larger speeds mean less lag."));
    }
    return Issues;
}

void UNarisP15MovementInputComponent::BeginPlay()
{
    Super::BeginPlay();
    ACharacter* Character = Cast<ACharacter>(GetOwner());
    UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
    if (!Movement) { SetComponentTickEnabled(false); return; }
    Combat = Character->FindComponentByClass<UNarisP15CombatComponent>();
    bProfileReady = IsMotionConfigurationValid();
    if (!bProfileReady)
    {
        UE_LOG(LogTemp, Error, TEXT("NARIS control profile rejected. Inspect GetSetupIssues before playing."));
        return;
    }
    ManagedMovement = Movement;
    Movement->AddTickPrerequisiteComponent(this);
    // Do not add a Combat -> input dependency: Combat already waits for the skeletal mesh.
    bOriginalControllerYaw = Character->bUseControllerRotationYaw;
    bOriginalOrient = Movement->bOrientRotationToMovement;
    bOriginalDesired = Movement->bUseControllerDesiredRotation;
    OriginalRotationRate = Movement->RotationRate;
    bOriginalSeparateBraking = Movement->bUseSeparateBrakingFriction;
    OriginalSpeed = Movement->MaxWalkSpeed;
    OriginalAcceleration = Movement->MaxAcceleration;
    OriginalBraking = Movement->BrakingDecelerationWalking;
    OriginalGroundFriction = Movement->GroundFriction;
    OriginalBrakingFriction = Movement->BrakingFriction;
    if (bApplyMovementProfile)
    {
        Movement->MaxWalkSpeed = WalkSpeed;
        Movement->MaxAcceleration = Acceleration;
        Movement->BrakingDecelerationWalking = BrakingDeceleration;
        Movement->GroundFriction = GroundFriction;
        Movement->bUseSeparateBrakingFriction = true;
        Movement->BrakingFriction = BrakingFriction;
    }
    RefreshRotationMode(Character);
    if (bApplyCameraProfile && Positive(FreeCameraLagSpeed) && Positive(FreeCameraRotationLagSpeed)
        && Positive(CombatCameraLagSpeed) && Positive(CombatCameraRotationLagSpeed))
    {
        CameraBoom = ResolveCameraBoom();
        if (USpringArmComponent* Boom = CameraBoom.Get())
        {
            bCapturedCamera = true;
            bOriginalCameraLag = Boom->bEnableCameraLag;
            bOriginalCameraRotationLag = Boom->bEnableCameraRotationLag;
            bOriginalSubstepping = Boom->bUseCameraLagSubstepping;
            OriginalCameraLagSpeed = Boom->CameraLagSpeed;
            OriginalCameraRotationLagSpeed = Boom->CameraRotationLagSpeed;
            OriginalCameraTimeStep = Boom->CameraLagMaxTimeStep;
            Boom->bEnableCameraLag = Boom->bEnableCameraRotationLag = true;
            Boom->bUseCameraLagSubstepping = true;
            Boom->CameraLagMaxTimeStep = 1.f / 120.f;
            Boom->CameraLagSpeed = FreeCameraLagSpeed;
            Boom->CameraRotationLagSpeed = FreeCameraRotationLagSpeed;
            Boom->AddTickPrerequisiteComponent(this);
        }
    }
}

void UNarisP15MovementInputComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    ResetMoveInput();
    Facing.Reset();
    if (UCharacterMovementComponent* Movement = ManagedMovement.Get())
    {
        Movement->RemoveTickPrerequisiteComponent(this);
        if (bApplyMovementProfile)
        {
            Movement->MaxWalkSpeed = OriginalSpeed;
            Movement->MaxAcceleration = OriginalAcceleration;
            Movement->BrakingDecelerationWalking = OriginalBraking;
            Movement->GroundFriction = OriginalGroundFriction;
            Movement->bUseSeparateBrakingFriction = bOriginalSeparateBraking;
            Movement->BrakingFriction = OriginalBrakingFriction;
        }
        if (bManageRotation)
        {
            Movement->bOrientRotationToMovement = bOriginalOrient;
            Movement->bUseControllerDesiredRotation = bOriginalDesired;
            Movement->RotationRate = OriginalRotationRate;
            if (ACharacter* Character = Cast<ACharacter>(GetOwner()))
                Character->bUseControllerRotationYaw = bOriginalControllerYaw;
        }
    }
    if (USpringArmComponent* Boom = CameraBoom.Get())
    {
        Boom->RemoveTickPrerequisiteComponent(this);
        if (bCapturedCamera)
        {
            Boom->bEnableCameraLag = bOriginalCameraLag;
            Boom->bEnableCameraRotationLag = bOriginalCameraRotationLag;
            Boom->bUseCameraLagSubstepping = bOriginalSubstepping;
            Boom->CameraLagSpeed = OriginalCameraLagSpeed;
            Boom->CameraRotationLagSpeed = OriginalCameraRotationLagSpeed;
            Boom->CameraLagMaxTimeStep = OriginalCameraTimeStep;
        }
    }
    Super::EndPlay(EndPlayReason);
}

void UNarisP15MovementInputComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const
{
    Super::GetLifetimeReplicatedProps(Out);
    DOREPLIFETIME(UNarisP15MovementInputComponent, bCombatMode);
    DOREPLIFETIME(UNarisP15MovementInputComponent, LockOnTarget);
}

void UNarisP15MovementInputComponent::OnRep_ControlMode() { Facing.Reset(); }

bool UNarisP15MovementInputComponent::IsValidLockTarget(AActor* Target) const
{
    return IsValid(Target) && Target != GetOwner() && GetOwner() && Target->GetWorld() == GetWorld()
        && Positive(MaxLockRange) && !Target->GetActorLocation().ContainsNaN()
        && !GetOwner()->GetActorLocation().ContainsNaN()
        && FVector::DistSquared(Target->GetActorLocation(), GetOwner()->GetActorLocation())
            <= FMath::Square(static_cast<double>(MaxLockRange));
}

void UNarisP15MovementInputComponent::SetCombatMode(bool bEnabled)
{
    if (!GetOwner()) return;
    if (GetOwner()->HasAuthority()) { bCombatMode = bEnabled; OnRep_ControlMode(); }
    else if (GetOwner()->HasLocalNetOwner()) ServerSetCombatMode(bEnabled);
}

void UNarisP15MovementInputComponent::ServerSetCombatMode_Implementation(bool bEnabled) { SetCombatMode(bEnabled); }

void UNarisP15MovementInputComponent::SetLockOnTarget(AActor* Target)
{
    if (!GetOwner() || (Target && !IsValidLockTarget(Target))) return;
    if (GetOwner()->HasAuthority()) { LockOnTarget = Target; OnRep_ControlMode(); }
    else if (GetOwner()->HasLocalNetOwner()) ServerSetLockOnTarget(Target);
}

void UNarisP15MovementInputComponent::ServerSetLockOnTarget_Implementation(AActor* Target) { SetLockOnTarget(Target); }

bool UNarisP15MovementInputComponent::IsInCombatMode() const
{
    return bCombatMode || IsValid(LockOnTarget.Get())
        || (Combat.IsValid() && Combat->ControlPhase != ENarisP15ControlPhase::Free
            && Combat->ControlPhase != ENarisP15ControlPhase::Unavailable);
}

void UNarisP15MovementInputComponent::RefreshRotationMode(ACharacter* Character)
{
    if (!bManageRotation || Character->GetLocalRole() == ROLE_SimulatedProxy) return;
    UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
    const bool bLocked = Combat.IsValid() && Combat->IsControlLocked();
    Character->bUseControllerRotationYaw = false;
    Movement->RotationRate = FRotator(0.f, YawDegreesPerSecond, 0.f);
    Movement->bOrientRotationToMovement = !bLocked && !IsInCombatMode();
    Movement->bUseControllerDesiredRotation = !bLocked && IsInCombatMode();
}

void UNarisP15MovementInputComponent::SetMoveInput(FVector2D Value)
{
    ACharacter* Character = Cast<ACharacter>(GetOwner());
    if (!Character || !Character->IsLocallyControlled() || !Character->GetController()
        || Character->IsMoveInputIgnored() || UGameplayStatics::IsGamePaused(this)
        || Value.ContainsNaN())
    { ResetMoveInput(); return; }
    if (InputController.Get() != Character->GetController()) ResetMoveInput();
    InputController = Character->GetController();
    if (!InputLease.Refresh({Value.X, Value.Y}, FPlatformTime::Seconds())) ResetMoveInput();
}

void UNarisP15MovementInputComponent::ResetMoveInput()
{
    InputLease.Reset();
    InputController.Reset();
    Filter.Reset();
}

void UNarisP15MovementInputComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    ACharacter* Character = Cast<ACharacter>(GetOwner());
    if (!Character || !bProfileReady || UGameplayStatics::IsGamePaused(this)
        || !FMath::IsFinite(DeltaTime) || DeltaTime <= 0.f)
    { Facing.Reset(); ResetMoveInput(); return; }
    if (!Combat.IsValid()) Combat = Character->FindComponentByClass<UNarisP15CombatComponent>();
    if (GetOwner()->HasAuthority() && LockOnTarget && !IsValidLockTarget(LockOnTarget.Get()))
    { LockOnTarget = nullptr; OnRep_ControlMode(); }
    RefreshRotationMode(Character);
    if (!Character->IsLocallyControlled() || !Character->GetController() || Character->IsMoveInputIgnored())
    { Facing.Reset(); ResetMoveInput(); return; }
    const bool bLocked = Combat.IsValid() && Combat->IsControlLocked();
    if (bApplyCameraProfile)
        if (USpringArmComponent* Boom = CameraBoom.Get())
        {
            const bool bCombat = IsInCombatMode();
            Boom->CameraLagSpeed = FMath::FInterpTo(Boom->CameraLagSpeed,
                bCombat ? CombatCameraLagSpeed : FreeCameraLagSpeed, DeltaTime, 12.f);
            Boom->CameraRotationLagSpeed = FMath::FInterpTo(Boom->CameraRotationLagSpeed,
                bCombat ? CombatCameraRotationLagSpeed : FreeCameraRotationLagSpeed, DeltaTime, 12.f);
        }
    if (bManageRotation && !bLocked && !Character->GetController()->IsLookInputIgnored()
        && IsValidLockTarget(LockOnTarget.Get()))
    {
        const FVector Offset = LockOnTarget->GetActorLocation() - Character->GetActorLocation();
        if (Offset.SizeSquared2D() > 1.f)
        {
            FRotator Control = Character->GetController()->GetControlRotation();
            if (Control.ContainsNaN()) { Facing.Reset(); ResetMoveInput(); return; }
            Control.Yaw = Facing.Step(Control.Yaw, Offset.Rotation().Yaw, DeltaTime,
                YawDegreesPerSecond, LockYawAcceleration);
            Character->GetController()->SetControlRotation(Control);
        }
    }
    else Facing.Reset();
    if (bLocked || Character->IsMoveInputIgnored() || !Character->GetCharacterMovement()->IsMovingOnGround())
    { ResetMoveInput(); return; }
    NarisP15::MoveInput Raw;
    if (InputController.Get() != Character->GetController()
        || !InputLease.Sample(FPlatformTime::Seconds(), InputTimeoutSeconds, Raw))
    { ResetMoveInput(); return; }
    const NarisP15::MoveInput Input = Filter.Step(Raw, DeltaTime,
        DeadZone, ResponseExponent, ResponseSeconds);
    const float ControlYaw = Character->GetController()->GetControlRotation().Yaw;
    if (!FMath::IsFinite(ControlYaw)) { ResetMoveInput(); return; }
    const FRotator Yaw(0.f, ControlYaw, 0.f);
    Character->AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::X), Input.Y);
    Character->AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y), Input.X);
}
