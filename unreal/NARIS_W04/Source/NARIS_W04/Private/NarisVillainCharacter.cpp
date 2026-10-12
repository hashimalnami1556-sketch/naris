#include "NarisVillainCharacter.h"

#include "AIController.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/DamageType.h"
#include "Kismet/GameplayStatics.h"
#include "NarisCombatComponent.h"
#include "UObject/ConstructorHelpers.h"

ANarisVillainCharacter::ANarisVillainCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
    AIControllerClass = AAIController::StaticClass();
    AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
    GetCapsuleComponent()->InitCapsuleSize(44.f, 96.f);
    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0.f, 450.f, 0.f);
    Combat = CreateDefaultSubobject<UNarisCombatComponent>(TEXT("Combat"));

    DevelopmentVisual = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DevelopmentVisual"));
    DevelopmentVisual->SetupAttachment(GetCapsuleComponent());
    DevelopmentVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    DevelopmentVisual->SetRelativeLocation(FVector(0.f, 0.f, -4.f));
    DevelopmentVisual->SetRelativeScale3D(FVector(0.85f, 0.65f, 1.7f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (Cube.Succeeded())
    {
        DevelopmentVisual->SetStaticMesh(Cube.Object);
    }
}

void ANarisVillainCharacter::BeginPlay()
{
    Super::BeginPlay();
    HomeLocation = GetActorLocation();
    ApplyArchetype();
    if (Combat)
    {
        Combat->OnCombatResolved.AddDynamic(this, &ANarisVillainCharacter::HandleCombatResolved);
    }
    // Only bind a real artist-authored/imported skeletal mesh when explicitly assigned.
    if (VisualMesh && GetMesh())
    {
        GetMesh()->SetSkeletalMeshAsset(VisualMesh);
    }
    // Preserve an unmistakable development proxy until a mesh is bound.
    DevelopmentVisual->SetVisibility(!GetMesh() || GetMesh()->GetSkeletalMeshAsset() == nullptr);
    NextPatrolTime = GetWorld() ? GetWorld()->GetTimeSeconds() + 1.f : 0.f;
    ChangeState(ENarisVillainState::Patrol);
}

void ANarisVillainCharacter::ApplyArchetype()
{
    float MaxHP = 110.f;
    float Speed = 270.f;
    if (VillainId == TEXT("BronzeSentinel"))
    {
        MaxHP = 245.f; Speed = 195.f; AttackDamage = 23.f; AttackRange = 210.f;
    }
    else if (VillainId == TEXT("BellWraith"))
    {
        MaxHP = 135.f; Speed = 350.f; AttackDamage = 17.f; AttackRange = 220.f;
    }
    else if (VillainId == TEXT("DrownedKnight"))
    {
        MaxHP = 300.f; Speed = 210.f; AttackDamage = 25.f; AttackRange = 230.f;
    }
    else if (VillainId == TEXT("ChainedGiant"))
    {
        MaxHP = 900.f; Speed = 160.f; AttackDamage = 46.f; AttackRange = 330.f;
        AttackWindupSeconds = 1.35f; AttackRecoverySeconds = 2.8f; bHasSecondPhase = true;
    }
    else if (VillainId == TEXT("AshGatekeeper"))
    {
        MaxHP = 1550.f; Speed = 195.f; AttackDamage = 44.f; AttackRange = 300.f;
        AttackWindupSeconds = 1.1f; AttackRecoverySeconds = 2.25f; bHasSecondPhase = true;
    }
    else if (VillainId == TEXT("EclipseReaver"))
    {
        MaxHP = 1900.f; Speed = 250.f; AttackDamage = 51.f; AttackRange = 340.f;
        AttackWindupSeconds = 0.9f; AttackRecoverySeconds = 2.0f; bHasSecondPhase = true;
    }
    if (Combat)
    {
        Combat->MaxHealth = MaxHP;
        Combat->Health = MaxHP;
        Combat->MaxPoise = bHasSecondPhase ? 240.f : 95.f;
        Combat->Poise = Combat->MaxPoise;
    }
    GetCharacterMovement()->MaxWalkSpeed = Speed;
}

void ANarisVillainCharacter::ChangeState(ENarisVillainState NewState)
{
    if (VillainState != NewState)
    {
        VillainState = NewState;
        OnVillainStateChanged(NewState);
    }
}

void ANarisVillainCharacter::StopAI()
{
    if (AAIController* AI = Cast<AAIController>(GetController()))
    {
        AI->StopMovement();
    }
}

void ANarisVillainCharacter::Die()
{
    if (VillainState == ENarisVillainState::Dead) return;
    bPendingImpact = false;
    StopAI();
    GetCharacterMovement()->StopMovementImmediately();
    GetCharacterMovement()->DisableMovement();
    GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ChangeState(ENarisVillainState::Dead);
    OnVillainDeath();
    OnVillainDefeated.Broadcast(VillainId);
    SetLifeSpan(8.f);
}

void ANarisVillainCharacter::HandleCombatResolved(FNarisCombatResult Result)
{
    if (VillainState == ENarisVillainState::Dead || !Combat) return;
    if (Combat->Health <= 0.f)
    {
        Die();
        return;
    }
    if (Result.Damage > 0.f)
    {
        OnVillainDamaged(Result.Damage, Result.bStaggered);
    }
    if (bHasSecondPhase && !bSecondPhase && Combat->Health <= Combat->MaxHealth * 0.5f)
    {
        bSecondPhase = true;
        AttackRecoverySeconds *= 0.72f;
        GetCharacterMovement()->MaxWalkSpeed *= 1.15f;
        OnVillainPhaseTwo();
    }
    if (Result.bStaggered)
    {
        bPendingImpact = false;
        StopAI();
        StaggerEndTime = GetWorld()->GetTimeSeconds() + 1.15f;
        ChangeState(ENarisVillainState::Staggered);
    }
}

float ANarisVillainCharacter::TakeDamage(float DamageAmount,
    FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
    if (VillainState == ENarisVillainState::Dead || !Combat || DamageAmount <= 0.f) return 0.f;
    return Combat->ResolveHit(DamageAmount, DamageAmount * 0.6f, false, false).Damage;
}

bool ANarisVillainCharacter::CommitAttackImpact()
{
    if (!bPendingImpact || bImpactCommitted || VillainState != ENarisVillainState::Windup
        || !TargetPlayer.IsValid() || !GetWorld()) return false;

    bImpactCommitted = true;
    bPendingImpact = false;
    APawn* Player = TargetPlayer.Get();
    const float DistanceSq = FVector::DistSquared(GetActorLocation(), Player->GetActorLocation());
    if (DistanceSq > FMath::Square(AttackRange + 55.f)) return false;
    if (AAIController* AI = Cast<AAIController>(GetController()))
    {
        if (!AI->LineOfSightTo(Player)) return false;
    }
    const float DamageDealt = UGameplayStatics::ApplyDamage(
        Player, AttackDamage * (bSecondPhase ? 1.2f : 1.f), GetController(), this,
        UDamageType::StaticClass());
    return DamageDealt > 0.f;
}

void ANarisVillainCharacter::UpdatePatrol(float Now)
{
    if (Now < NextPatrolTime) return;
    NextPatrolTime = Now + FMath::FRandRange(3.f, 5.f);
    if (AAIController* AI = Cast<AAIController>(GetController()))
    {
        const FVector Goal = HomeLocation + FVector(
            FMath::FRandRange(-PatrolRadius, PatrolRadius),
            FMath::FRandRange(-PatrolRadius, PatrolRadius), 0.f);
        AI->MoveToLocation(Goal, 85.f);
    }
}

void ANarisVillainCharacter::UpdateEngagement(float Now)
{
    APawn* Player = TargetPlayer.Get();
    if (!Player)
    {
        ChangeState(ENarisVillainState::Patrol);
        return;
    }
    const float Distance = FVector::Dist(GetActorLocation(), Player->GetActorLocation());
    if (Distance > LeashRange || FVector::DistSquared(HomeLocation, GetActorLocation())
        > FMath::Square(LeashRange))
    {
        TargetPlayer.Reset();
        StopAI();
        ChangeState(ENarisVillainState::Patrol);
        NextPatrolTime = Now;
        return;
    }
    if (Distance <= AttackRange && Now >= RecoveryEndTime)
    {
        StopAI();
        const FVector Direction = Player->GetActorLocation() - GetActorLocation();
        SetActorRotation(FRotator(0.f, Direction.Rotation().Yaw, 0.f));
        WindupEndTime = Now + AttackWindupSeconds;
        bPendingImpact = true;
        bImpactCommitted = false;
        ChangeState(ENarisVillainState::Windup);
        OnVillainAttackRequested(bSecondPhase);
        return;
    }
    ChangeState(ENarisVillainState::Chase);
    if (Now >= NextMoveOrderTime)
    {
        NextMoveOrderTime = Now + 0.65f;
        if (AAIController* AI = Cast<AAIController>(GetController()))
        {
            AI->MoveToActor(Player, FMath::Max(85.f, AttackRange * 0.7f));
        }
    }
}

void ANarisVillainCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!GetWorld() || !Combat || VillainState == ENarisVillainState::Dead) return;
    const float Now = GetWorld()->GetTimeSeconds();

    if (VillainState == ENarisVillainState::Staggered)
    {
        if (Now < StaggerEndTime) return;
        ChangeState(ENarisVillainState::Patrol);
    }
    if (VillainState == ENarisVillainState::Windup)
    {
        if (Now < WindupEndTime) return;
        if (bUseTimedSmokeAttackImpact) CommitAttackImpact();
        bPendingImpact = false;
        RecoveryEndTime = Now + AttackRecoverySeconds;
        ChangeState(ENarisVillainState::Recovery);
        return;
    }
    if (VillainState == ENarisVillainState::Recovery)
    {
        if (Now < RecoveryEndTime) return;
        ChangeState(ENarisVillainState::Chase);
    }

    APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
    const bool bCanSeePlayer = IsValid(Player) && Player != this
        && FVector::DistSquared(GetActorLocation(), Player->GetActorLocation())
            <= FMath::Square(DetectionRange)
        && (Cast<AAIController>(GetController()) == nullptr
            || Cast<AAIController>(GetController())->LineOfSightTo(Player));

    if (!TargetPlayer.IsValid() && bCanSeePlayer)
    {
        TargetPlayer = Player;
    }

    if (TargetPlayer.IsValid())
    {
        UpdateEngagement(Now);
    }
    else
    {
        ChangeState(ENarisVillainState::Patrol);
        UpdatePatrol(Now);
    }
}
