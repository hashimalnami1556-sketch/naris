#include "NarisHeroCharacter.h"

#include "BoneBeastBoss.h"
#include "Camera/CameraComponent.h"
#include "Components/InputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/SpringArmComponent.h"
#include "Kismet/GameplayStatics.h"
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

float ANarisHeroCharacter::TakeDamage(
    float DamageAmount,
    FDamageEvent const& DamageEvent,
    AController* EventInstigator,
    AActor* DamageCauser
)
{
    if (!Combat || DamageAmount <= 0.f)
    {
        return 0.f;
    }

    const float PoiseDamage = DamageAmount * 0.5f;
    const FNarisCombatResult Result =
        Combat->ResolveIncomingHit(DamageAmount, PoiseDamage, false);

    return Result.Damage;
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
    Input->BindAction(TEXT("EssenceNext"), IE_Pressed, this, &ANarisHeroCharacter::NextEssence);
    Input->BindAction(TEXT("EssencePrevious"), IE_Pressed, this, &ANarisHeroCharacter::PreviousEssence);
    Input->BindAction(TEXT("Interact"), IE_Pressed, this, &ANarisHeroCharacter::Interact);
    Input->BindAction(TEXT("Sprint"), IE_Pressed, this, &ANarisHeroCharacter::StartSprinting);
    Input->BindAction(TEXT("Sprint"), IE_Released, this, &ANarisHeroCharacter::StopSprinting);

    FInputActionBinding& PauseBinding =
        Input->BindAction(TEXT("Pause"), IE_Pressed, this, &ANarisHeroCharacter::TogglePause);
    PauseBinding.bExecuteWhenPaused = true;
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

bool ANarisHeroCharacter::ApplyAttackToLockedTarget(float Damage, float PoiseDamage)
{
    if (!LockOn || Damage <= 0.f)
    {
        return false;
    }

    if (!LockOn->HasTarget() && !LockOn->AcquireTarget())
    {
        return false;
    }

    AActor* TargetActor = LockOn->Target;
    if (!IsValid(TargetActor))
    {
        return false;
    }

    if (FVector::DistSquared(GetActorLocation(), TargetActor->GetActorLocation())
        > FMath::Square(MeleeRange))
    {
        return false;
    }

    if (ABoneBeastBoss* Boss = Cast<ABoneBeastBoss>(TargetActor))
    {
        if (!Boss->IsEncounterActive() || Boss->IsEncounterComplete())
        {
            return false;
        }

        Boss->ApplyDamageToEncounter(Damage);
        return true;
    }

    if (UNarisCombatComponent* TargetCombat =
            TargetActor->FindComponentByClass<UNarisCombatComponent>())
    {
        if (TargetCombat->Health <= 0.f)
        {
            return false;
        }

        TargetCombat->ResolveHit(Damage, PoiseDamage, false, false);
        return true;
    }

    return false;
}

void ANarisHeroCharacter::QueueAttack(ENarisAttackKind AttackKind)
{
    PendingAttack = AttackKind;
    bAttackHitWindowOpen = false;
    bAttackHitConsumed = false;

    OnAttackRequested(AttackKind);

    if (bImmediateSmokeAttackHit)
    {
        OpenAttackHitWindow();
        CommitPendingAttackHit();
        CloseAttackHitWindow();
    }
}

void ANarisHeroCharacter::LightAttack()
{
    QueueAttack(ENarisAttackKind::Light);
}

void ANarisHeroCharacter::HeavyAttack()
{
    QueueAttack(ENarisAttackKind::Heavy);
}

void ANarisHeroCharacter::OpenAttackHitWindow()
{
    if (PendingAttack != ENarisAttackKind::None)
    {
        bAttackHitWindowOpen = true;
        bAttackHitConsumed = false;
    }
}

void ANarisHeroCharacter::CloseAttackHitWindow()
{
    bAttackHitWindowOpen = false;
    PendingAttack = ENarisAttackKind::None;
}

bool ANarisHeroCharacter::CommitPendingAttackHit()
{
    if (!bAttackHitWindowOpen
        || bAttackHitConsumed
        || PendingAttack == ENarisAttackKind::None)
    {
        return false;
    }

    bAttackHitConsumed = true;

    float Damage = 0.f;
    float PoiseDamage = 0.f;
    float ResonanceReward = 0.f;

    switch (PendingAttack)
    {
        case ENarisAttackKind::Light:
            Damage = LightAttackDamage;
            PoiseDamage = LightAttackPoiseDamage;
            ResonanceReward = 5.f;
            break;
        case ENarisAttackKind::Heavy:
            Damage = HeavyAttackDamage;
            PoiseDamage = HeavyAttackPoiseDamage;
            ResonanceReward = 10.f;
            break;
        default:
            return false;
    }

    const bool bHit = ApplyAttackToLockedTarget(Damage, PoiseDamage);
    if (bHit && Combat)
    {
        Combat->AddResonance(ResonanceReward);
    }

    return bHit;
}

void ANarisHeroCharacter::CancelPendingAttack()
{
    PendingAttack = ENarisAttackKind::None;
    bAttackHitWindowOpen = false;
    bAttackHitConsumed = false;
}

void ANarisHeroCharacter::Dodge()
{
    if (Energy && !Energy->Spend(DodgeEnergyCost))
    {
        return;
    }

    if (Combat)
    {
        Combat->OpenInvulnerabilityWindow(DodgeInvulnerabilitySeconds);
    }

    GetCharacterMovement()->Velocity += GetActorForwardVector() * 650.f;
}

void ANarisHeroCharacter::Parry()
{
    if (Energy && !Energy->Spend(ParryEnergyCost))
    {
        return;
    }

    if (Combat)
    {
        Combat->OpenParryWindow(ParryWindowSeconds);
    }
}

void ANarisHeroCharacter::ResonanceBurst()
{
    if (Combat && Combat->Resonance >= Combat->MaxResonance)
    {
        Combat->Resonance = 0.f;

        if (Energy)
        {
            Energy->Restore(25.f);
        }
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

void ANarisHeroCharacter::NextEssence()
{
    if (Energy)
    {
        Energy->CycleEssence(1);
    }
}

void ANarisHeroCharacter::PreviousEssence()
{
    if (Energy)
    {
        Energy->CycleEssence(-1);
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

void ANarisHeroCharacter::TogglePause()
{
    const bool bPaused = UGameplayStatics::IsGamePaused(this);
    UGameplayStatics::SetGamePaused(this, !bPaused);
}

void ANarisHeroCharacter::StartSprinting()
{
    SetSprinting(true);
}

void ANarisHeroCharacter::StopSprinting()
{
    SetSprinting(false);
}
