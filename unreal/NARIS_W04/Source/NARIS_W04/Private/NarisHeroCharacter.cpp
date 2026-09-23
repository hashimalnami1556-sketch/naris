#include "NarisHeroCharacter.h"

#include "Camera/CameraComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/SpringArmComponent.h"
#include "NarisCombatComponent.h"
#include "NarisEnergyComponent.h"
#include "NarisInteractionComponent.h"
#include "NarisLockOnComponent.h"

ANarisHeroCharacter::ANarisHeroCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    Combat = CreateDefaultSubobject<UNarisCombatComponent>(TEXT("Combat"));
    Energy = CreateDefaultSubobject<UNarisEnergyComponent>(TEXT("Energy"));
    LockOn = CreateDefaultSubobject<UNarisLockOnComponent>(TEXT("LockOn"));
    Interaction = CreateDefaultSubobject<UNarisInteractionComponent>(TEXT("Interaction"));

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 340.f;
    CameraBoom->bUsePawnControlRotation = true;

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom);
    FollowCamera->bUsePawnControlRotation = false;

    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    bUseControllerRotationYaw = false;
}

void ANarisHeroCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (Combat && Combat->Health <= 0.f)
    {
        DisableInput(nullptr);
    }
}

void ANarisHeroCharacter::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);

    Input->BindAxis(TEXT("MoveForward"), this, &ANarisHeroCharacter::MoveForward);
    Input->BindAxis(TEXT("MoveRight"), this, &ANarisHeroCharacter::MoveRight);
    Input->BindAxis(TEXT("LookYaw"), this, &ANarisHeroCharacter::LookYaw);
    Input->BindAxis(TEXT("LookPitch"), this, &ANarisHeroCharacter::LookPitch);

    Input->BindAction(TEXT("LightAttack"), IE_Pressed, this, &ANarisHeroCharacter::LightAttack);
    Input->BindAction(TEXT("HeavyAttack"), IE_Pressed, this, &ANarisHeroCharacter::HeavyAttack);
    Input->BindAction(TEXT("Dodge"), IE_Pressed, this, &ANarisHeroCharacter::Dodge);
    Input->BindAction(TEXT("Parry"), IE_Pressed, this, &ANarisHeroCharacter::Parry);
    Input->BindAction(TEXT("ResonanceBurst"), IE_Pressed, this, &ANarisHeroCharacter::ResonanceBurst);
    Input->BindAction(TEXT("LockOn"), IE_Pressed, this, &ANarisHeroCharacter::ToggleLockOn);
    Input->BindAction(TEXT("Interact"), IE_Pressed, this, &ANarisHeroCharacter::Interact);
    Input->BindAction(TEXT("Sprint"), IE_Pressed, this, &ANarisHeroCharacter::StartSprinting);
    Input->BindAction(TEXT("Sprint"), IE_Released, this, &ANarisHeroCharacter::StopSprinting);
}

void ANarisHeroCharacter::MoveForward(float Value)
{
    if (Controller && Value != 0.f)
    {
        const FRotator Rotation(0.f, Controller->GetControlRotation().Yaw, 0.f);
        AddMovementInput(FRotationMatrix(Rotation).GetUnitAxis(EAxis::X), Value);
    }
}

void ANarisHeroCharacter::MoveRight(float Value)
{
    if (Controller && Value != 0.f)
    {
        const FRotator Rotation(0.f, Controller->GetControlRotation().Yaw, 0.f);
        AddMovementInput(FRotationMatrix(Rotation).GetUnitAxis(EAxis::Y), Value);
    }
}

void ANarisHeroCharacter::LookYaw(float Value)
{
    AddControllerYawInput(Value);
}

void ANarisHeroCharacter::LookPitch(float Value)
{
    AddControllerPitchInput(Value);
}

void ANarisHeroCharacter::LightAttack()
{
    if (Combat)
    {
        Combat->AddResonance(5.f);
    }
}

void ANarisHeroCharacter::HeavyAttack()
{
    if (Combat)
    {
        Combat->AddResonance(10.f);
    }
}

void ANarisHeroCharacter::Dodge()
{
    GetCharacterMovement()->Velocity += GetActorForwardVector() * 650.f;
}

void ANarisHeroCharacter::Parry()
{
    if (Combat)
    {
        Combat->AddResonance(15.f);
    }
}

void ANarisHeroCharacter::ResonanceBurst()
{
    if (Combat && Combat->Resonance >= Combat->MaxResonance)
    {
        Combat->Resonance = 0.f;
    }
}

void ANarisHeroCharacter::ToggleLockOn()
{
    if (!LockOn)
    {
        return;
    }

    if (LockOn->HasTarget())
    {
        LockOn->ClearTarget();
    }
    else
    {
        LockOn->AcquireTarget();
    }
}

void ANarisHeroCharacter::Interact()
{
    if (Interaction)
    {
        Interaction->Interact();
    }
}

void ANarisHeroCharacter::SetSprinting(bool bSprint)
{
    GetCharacterMovement()->MaxWalkSpeed = bSprint ? SprintSpeed : WalkSpeed;
}

void ANarisHeroCharacter::StartSprinting()
{
    SetSprinting(true);
}

void ANarisHeroCharacter::StopSprinting()
{
    SetSprinting(false);
}
