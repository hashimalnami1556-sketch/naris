#include "NarisHeroCharacter.h"

#include "BoneBeastBoss.h"
#include "Camera/CameraComponent.h"
#include "CelestialWolf.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Components/InputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NarisCombatComponent.h"
#include "NarisEnergyComponent.h"
#include "NarisInteractionComponent.h"
#include "NarisLockOnComponent.h"
#include "NarisPresentationComponent.h"
#include "NarisPlayerController.h"
#include "NarisRuntimeSubsystem.h"
#include "TimerManager.h"

ANarisHeroCharacter::ANarisHeroCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    Combat = CreateDefaultSubobject<UNarisCombatComponent>(TEXT("Combat"));
    Energy = CreateDefaultSubobject<UNarisEnergyComponent>(TEXT("Energy"));
    LockOn = CreateDefaultSubobject<UNarisLockOnComponent>(TEXT("LockOn"));
    Interaction = CreateDefaultSubobject<UNarisInteractionComponent>(TEXT("Interaction"));
    Presentation = CreateDefaultSubobject<UNarisPresentationComponent>(TEXT("Presentation"));

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

    if (Combat && Combat->Health <= 0.f && !bDeathHandled)
    {
        HandleDeath();
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

    if (Presentation)
    {
        if (Result.bEvaded)
        {
            Presentation->TriggerCue(TEXT("Hero.Evade"));
        }
        else if (Result.bParried)
        {
            Presentation->TriggerCue(TEXT("Hero.ParrySuccess"));
        }
        else if (Result.Damage > 0.f)
        {
            Presentation->TriggerCue(TEXT("Hero.HitReact"));
        }
    }

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
    Input->BindAction(TEXT("CompanionMode"), IE_Pressed, this, &ANarisHeroCharacter::CycleCompanionMode);
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

        if (Presentation)
        {
            const FName CueId =
                PendingAttack == ENarisAttackKind::Heavy
                    ? FName(TEXT("Hero.AttackHit.Heavy"))
                    : FName(TEXT("Hero.AttackHit.Light"));
            Presentation->TriggerCue(CueId);
        }
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

    if (Presentation)
    {
        Presentation->TriggerCue(TEXT("Hero.Dodge"));
    }
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

    if (Presentation)
    {
        Presentation->TriggerCue(TEXT("Hero.ParryWindow"));
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

        if (Presentation)
        {
            Presentation->TriggerCue(TEXT("Hero.ResonanceBurst"));
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
        if (Presentation)
        {
            Presentation->TriggerCue(TEXT("Hero.EssenceSwitch"));
        }
    }
}

void ANarisHeroCharacter::PreviousEssence()
{
    if (Energy)
    {
        Energy->CycleEssence(-1);
        if (Presentation)
        {
            Presentation->TriggerCue(TEXT("Hero.EssenceSwitch"));
        }
    }
}

void ANarisHeroCharacter::CycleCompanionMode()
{
    if (!GetWorld())
    {
        return;
    }

    for (TActorIterator<ACelestialWolf> It(GetWorld()); It; ++It)
    {
        if (ACelestialWolf* Wolf = *It)
        {
            Wolf->CycleMode();
            break;
        }
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
    if (ANarisPlayerController* PlayerController =
            Cast<ANarisPlayerController>(Controller))
    {
        PlayerController->TogglePauseMenu();
        return;
    }

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


void ANarisHeroCharacter::HandleDeath()
{
    bDeathHandled = true;

    if (Presentation)
    {
        Presentation->TriggerCue(TEXT("Hero.Death"));
    }

    if (APlayerController* PlayerController = Cast<APlayerController>(Controller))
    {
        DisableInput(PlayerController);
    }

    if (GetCharacterMovement())
    {
        GetCharacterMovement()->DisableMovement();
        GetCharacterMovement()->Velocity = FVector::ZeroVector;
    }

    if (!GetWorld())
    {
        return;
    }

    FTimerHandle RespawnTimer;
    GetWorldTimerManager().SetTimer(
        RespawnTimer,
        this,
        &ANarisHeroCharacter::RespawnAtCheckpoint,
        FMath::Max(RespawnDelaySeconds, 0.01f),
        false
    );
}

void ANarisHeroCharacter::RespawnAtCheckpoint()
{
    if (GetWorld() && bRespawnAtCheckpoint)
    {
        if (UGameInstance* GameInstance = GetWorld()->GetGameInstance())
        {
            if (UNarisRuntimeSubsystem* Runtime =
                    GameInstance->GetSubsystem<UNarisRuntimeSubsystem>())
            {
                const FNarisSaveState State = Runtime->GetState();
                if (State.bHasCheckpointLocation)
                {
                    SetActorLocation(
                        State.CheckpointLocation
                            + FVector(0.f, 0.f, CheckpointRespawnZOffset),
                        false,
                        nullptr,
                        ETeleportType::TeleportPhysics
                    );
                }
            }
        }
    }

    if (Combat)
    {
        Combat->Health = Combat->MaxHealth;
        Combat->Poise = Combat->MaxPoise;
        Combat->ClearDefenseWindows();
    }

    if (Energy)
    {
        Energy->Energy = Energy->MaxEnergy;
    }

    if (GetCharacterMovement())
    {
        GetCharacterMovement()->SetMovementMode(MOVE_Walking);
        GetCharacterMovement()->Velocity = FVector::ZeroVector;
    }

    if (APlayerController* PlayerController = Cast<APlayerController>(Controller))
    {
        EnableInput(PlayerController);
    }

    bDeathHandled = false;

    if (Presentation)
    {
        Presentation->TriggerCue(TEXT("Hero.Respawn"));
    }
}
