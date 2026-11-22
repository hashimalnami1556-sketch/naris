#include "NarisHeroCharacter.h"

#include "BoneBeastBoss.h"
#include "Camera/CameraComponent.h"
#include "CelestialWolf.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Components/InputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Animation/AnimInstance.h"
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
#include "NarisSwimmingComponent.h"
#include "NarisWeatherGameplayComponent.h"
#include "TimerManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

ANarisHeroCharacter::ANarisHeroCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    Combat = CreateDefaultSubobject<UNarisCombatComponent>(TEXT("Combat"));
    Energy = CreateDefaultSubobject<UNarisEnergyComponent>(TEXT("Energy"));
    LockOn = CreateDefaultSubobject<UNarisLockOnComponent>(TEXT("LockOn"));
    Interaction = CreateDefaultSubobject<UNarisInteractionComponent>(TEXT("Interaction"));
    Presentation = CreateDefaultSubobject<UNarisPresentationComponent>(TEXT("Presentation"));
    Swimming = CreateDefaultSubobject<UNarisSwimmingComponent>(TEXT("Swimming"));
    WeatherGameplay = CreateDefaultSubobject<UNarisWeatherGameplayComponent>(TEXT("WeatherGameplay"));

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 340.f;
    CameraBoom->bUsePawnControlRotation = true;

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom);
    FollowCamera->bUsePawnControlRotation = false;

    GetCharacterMovement()->JumpZVelocity = 600.f;
    GetCharacterMovement()->AirControl = 0.8f;
    GetCharacterMovement()->GravityScale = 1.5f;
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    bUseControllerRotationYaw = false;
}

void ANarisHeroCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

#if !UE_BUILD_SHIPPING
    // Explicit developer-only, one-shot input probe, executed by the local
    // client-owned Hero after possession. No gameplay save or gate is changed.
    if (!HasAuthority() && IsLocallyControlled() && GetWorld()
        && FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeInput")))
    {
        const float Now = GetWorld()->GetTimeSeconds();
        if (NetWolfProbePhase == 0)
        {
            NetWolfProbeStartTime = Now;
            NetWolfProbePhase = 1;
        }
        else if (NetWolfProbePhase == 1 && Now >= NetWolfProbeStartTime + 2.f)
        {
            // Invoke the *actual* player-owned Server RPC with a replicated
            // placed Wolf. The server, not this client, validates range.
            ACelestialWolf* Wolf = nullptr;
            for (TActorIterator<ACelestialWolf> It(GetWorld()); It; ++It)
            {
                Wolf = *It;
                break;
            }
            if (IsValid(Wolf))
            {
                if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeInputButton")))
                {
                    // Exercise the SAME Interact() method bound to user input,
                    // but trigger once via explicit QA CLI, not keyboard hardware.
                    // Server is separately started with -NarisWolfNetProbeNoSave.
                    UE_LOG(LogTemp, Display, TEXT("NARIS_WOLF_NET_PROBE event=ClientInteractButton authority=0"));
                    Interact();
                }
                else
                {
                    UE_LOG(LogTemp, Display, TEXT("NARIS_WOLF_NET_PROBE event=ClientInteractRequest actor=%s authority=0"),
                        *Wolf->GetName());
                    ServerInteractWithWolf(Wolf);
                }
            }
            else
            {
                UE_LOG(LogTemp, Warning, TEXT("NARIS_WOLF_NET_PROBE event=ClientInteractRequest missing_wolf=1"));
            }
            NetWolfProbePhase = 2;
        }
        else if (NetWolfProbePhase == 2 && Now >= NetWolfProbeStartTime + 4.f)
        {
            UE_LOG(LogTemp, Display, TEXT("NARIS_WOLF_NET_PROBE event=ClientCycleMode authority=0"));
            CycleCompanionMode();
            NetWolfProbePhase = 3;
        }
    }
#endif

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
    Input->BindAxis(TEXT("SwimVertical"), this, &ANarisHeroCharacter::MoveSwimVertical);
    Input->BindAxis(TEXT("LookYaw"), this, &ANarisHeroCharacter::LookYaw);
    Input->BindAxis(TEXT("LookPitch"), this, &ANarisHeroCharacter::LookPitch);

    Input->BindAction(TEXT("Jump"), IE_Pressed, this, &ACharacter::Jump);
    Input->BindAction(TEXT("Jump"), IE_Released, this, &ACharacter::StopJumping);

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

void ANarisHeroCharacter::MoveSwimVertical(float Value)
{
    if (Swimming)
    {
        Swimming->SetVerticalSwimInput(Value);
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
    if (Swimming && Swimming->IsSwimming())
    {
        return;
    }

    // Production dodge is animation-driven. The Blueprint/AnimBP must return
    // true only after a valid dodge montage actually starts. This prevents
    // spending energy or granting i-frames when animation playback fails.
    const bool bDodgeAnimationStarted = OnDodgeRequested();
    if (!bDodgeAnimationStarted)
    {
        return;
    }

    if (Energy && !Energy->Spend(DodgeEnergyCost))
    {
        // Montage may have started, but gameplay authority rejects the dodge
        // when the resource cost cannot be committed.
        if (UAnimInstance* AnimInstance = GetMesh() ? GetMesh()->GetAnimInstance() : nullptr)
        {
            AnimInstance->Montage_Stop(0.10f);
        }
        return;
    }

    if (Combat)
    {
        Combat->OpenInvulnerabilityWindow(DodgeInvulnerabilitySeconds);
    }

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
    if (!HasAuthority())
    {
        ServerCycleCompanionMode();
        return;
    }

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

void ANarisHeroCharacter::ServerCycleCompanionMode_Implementation()
{
#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbe")))
    {
        UE_LOG(LogTemp, Display, TEXT("NARIS_WOLF_NET_PROBE event=ServerCycleMode authority=%d"), HasAuthority() ? 1 : 0);
    }
#endif
    CycleCompanionMode();
}

void ANarisHeroCharacter::Interact()
{
    if (!Interaction)
    {
        return;
    }

    // A placed Wolf is owned by the server, not the client. Route its
    // interaction through this player-owned Hero, and revalidate proximity
    // in the authoritative world before any campaign/save-state mutation.
    if (ACelestialWolf* Wolf = Cast<ACelestialWolf>(Interaction->FindNearestInteractable()))
    {
        if (!HasAuthority())
        {
            ServerInteractWithWolf(Wolf);
            return;
        }
    }

    // Preserve existing non-Wolf interaction behavior unchanged.
    Interaction->Interact();
}

void ANarisHeroCharacter::ServerInteractWithWolf_Implementation(ACelestialWolf* Wolf)
{
    if (!HasAuthority() || !IsValid(Wolf) || !Interaction)
    {
        return;
    }

    // Re-evaluate target and distance on the server (Radius in the
    // Interaction component); never trust the client-supplied Actor alone.
    if (Interaction->FindNearestInteractable() != Wolf)
    {
#if !UE_BUILD_SHIPPING
        if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbe")))
        {
            UE_LOG(LogTemp, Display, TEXT("NARIS_WOLF_NET_PROBE event=ServerInteractRejected authority=1 reason=not_nearest_or_out_of_range"));
        }
#endif
        return;
    }

#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbe")))
    {
        UE_LOG(LogTemp, Display, TEXT("NARIS_WOLF_NET_PROBE event=ServerInteractAccepted authority=1"));
    }
    // In explicit QA mode, test the real ownership / target validation
    // but do not write companion, quest or autosave state.
    if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeNoSave")))
    {
        return;
    }
#endif

    Interaction->Interact();
}

void ANarisHeroCharacter::SetSprinting(bool bSprint)
{
    bIsSprinting = bSprint;
    RefreshMovementSpeed();
}

void ANarisHeroCharacter::RefreshMovementSpeed()
{
    float Multiplier = 1.f;
    if (WeatherGameplay)
    {
        Multiplier = WeatherGameplay->GetMoveSpeedMultiplier();
    }

    GetCharacterMovement()->MaxWalkSpeed =
        (bIsSprinting ? SprintSpeed : WalkSpeed) *
        FMath::Clamp(Multiplier, 0.25f, 1.25f);
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
