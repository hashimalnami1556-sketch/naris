#include "NarisP15CombatComponent.h"

#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/DamageType.h"
#include "Kismet/GameplayStatics.h"
#include "Net/UnrealNetwork.h"

UNarisP15CombatComponent::UNarisP15CombatComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    SetIsReplicatedByDefault(true);
}

void UNarisP15CombatComponent::BeginPlay()
{
    Super::BeginPlay();
    ACharacter* Character = Cast<ACharacter>(GetOwner());
    CharacterMesh = Character ? Character->GetMesh() : nullptr;
    if (!GetOwner() || !GetOwner()->HasAuthority()) return;
    if (!CharacterMesh)
    {
        UE_LOG(LogTemp, Error, TEXT("NARIS P15 requires an ACharacter with a skeletal mesh."));
        return;
    }
    const UAnimMontage* Montages[] = {LightAttackMontage, DodgeMontage, ParryMontage};
    for (const UAnimMontage* Montage : Montages)
    {
        if (Montage && (!FMath::IsFinite(Montage->RateScale) || !FMath::IsNearlyEqual(Montage->RateScale, 1.f)))
        {
            UE_LOG(LogTemp, Error, TEXT("NARIS P15 montages must use RateScale 1 for authoritative timing."));
            return;
        }
    }
    NarisP15::Config Config;
    Config.MaxHealth = MaxHealth; Config.MaxStamina = MaxStamina;
    Config.AttackCost = LightAttackCost; Config.DodgeCost = DodgeCost; Config.ParryCost = ParryCost;
    Config.RegenPerSecond = StaminaRegenPerSecond; Config.RegenDelay = RegenDelaySeconds;
    Config.DodgeInvulnerabilityStart = DodgeInvulnerabilityStart;
    Config.DodgeInvulnerabilityEnd = DodgeInvulnerabilityEnd;
    if (LightAttackMontage) Config.AttackDuration = LightAttackMontage->GetPlayLength();
    if (DodgeMontage) Config.DodgeDuration = DodgeMontage->GetPlayLength();
    if (ParryMontage) Config.ParryDuration = ParryMontage->GetPlayLength();
    bReady = Rules.Initialize(Config) && FMath::IsFinite(TraceRadius) && TraceRadius > 0.f
        && FMath::IsFinite(MaxWeaponReach) && MaxWeaponReach > 0.f
        && FMath::IsFinite(LightAttackDamage) && LightAttackDamage > 0.f;
    if (!bReady)
    {
        UE_LOG(LogTemp, Error, TEXT("NARIS P15 rejected invalid combat configuration."));
        return;
    }
    // حتى السيرفر المخصص يحتاج تحديث العظام وإشعارات الحركة.
    CharacterMesh->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    AddTickPrerequisiteComponent(CharacterMesh);
    GetOwner()->OnTakeAnyDamage.AddDynamic(this, &UNarisP15CombatComponent::HandleAnyDamage);
    if (!GetOwner()->GetIsReplicated() && GetNetMode() != NM_Standalone)
        UE_LOG(LogTemp, Warning, TEXT("NARIS P15 owner must replicate for network RPCs."));
    SyncVitals();
}

void UNarisP15CombatComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(UNarisP15CombatComponent, Health);
    DOREPLIFETIME(UNarisP15CombatComponent, Stamina);
    DOREPLIFETIME(UNarisP15CombatComponent, MaxHealth);
    DOREPLIFETIME(UNarisP15CombatComponent, MaxStamina);
}

void UNarisP15CombatComponent::OnRep_Vitals()
{
    if (IsDead() && CharacterMesh && CharacterMesh->GetAnimInstance())
        CharacterMesh->GetAnimInstance()->Montage_Stop(.1f);
    OnVitalsChanged();
}

void UNarisP15CombatComponent::SyncVitals()
{
    const bool bChanged = Health != Rules.GetHealth() || Stamina != Rules.GetStamina();
    Health = Rules.GetHealth(); Stamina = Rules.GetStamina();
    if (bChanged) OnVitalsChanged();
}

UAnimMontage* UNarisP15CombatComponent::GetMontage(ENarisP15Action Action) const
{
    switch (Action)
    {
    case ENarisP15Action::LightAttack: return LightAttackMontage;
    case ENarisP15Action::Dodge: return DodgeMontage;
    case ENarisP15Action::Parry: return ParryMontage;
    default: return nullptr;
    }
}

void UNarisP15CombatComponent::RequestLightAttack() { RequestAction(ENarisP15Action::LightAttack); }
void UNarisP15CombatComponent::RequestDodge() { RequestAction(ENarisP15Action::Dodge); }
void UNarisP15CombatComponent::RequestParry() { RequestAction(ENarisP15Action::Parry); }

void UNarisP15CombatComponent::RequestAction(ENarisP15Action Action)
{
    if (!GetOwner()) return;
    if (GetOwner()->HasAuthority()) CommitAction(Action);
    else if (GetOwner()->HasLocalNetOwner()) ServerRequestAction(Action);
}

void UNarisP15CombatComponent::ServerRequestAction_Implementation(ENarisP15Action Action) { CommitAction(Action); }

void UNarisP15CombatComponent::CommitAction(ENarisP15Action Action)
{
    if (!bReady || !GetOwner()->HasAuthority() || !CharacterMesh || !CharacterMesh->GetAnimInstance()) return;
    UAnimMontage* Montage = GetMontage(Action);
    if (!Montage || !FMath::IsFinite(Montage->GetPlayLength()) || Montage->GetPlayLength() <= 0.f) return;
    NarisP15::Action Requested;
    switch (Action)
    {
    case ENarisP15Action::LightAttack:
        if (!CharacterMesh->DoesSocketExist(WeaponBaseSocket) || !CharacterMesh->DoesSocketExist(WeaponTipSocket)) return;
        Requested = NarisP15::Action::LightAttack; break;
    case ENarisP15Action::Dodge: Requested = NarisP15::Action::Dodge; break;
    case ENarisP15Action::Parry: Requested = NarisP15::Action::Parry; break;
    default: return;
    }
    if (!Rules.TryStart(Requested)) return;
    bHasPreviousTip = false;
    SyncVitals();
    MulticastPresentAction(Action);
}

void UNarisP15CombatComponent::MulticastPresentAction_Implementation(ENarisP15Action Action)
{
    if (CharacterMesh && CharacterMesh->GetAnimInstance() && GetMontage(Action))
        CharacterMesh->GetAnimInstance()->Montage_Play(GetMontage(Action));
    OnActionPresented(Action);
}

void UNarisP15CombatComponent::ApplyCombatDamage(float Amount)
{
    if (!bReady || !GetOwner() || !GetOwner()->HasAuthority()) return;
    const NarisP15::DamageOutcome Outcome = Rules.Damage(Amount);
    SyncVitals();
    if (Outcome == NarisP15::DamageOutcome::Evaded || Outcome == NarisP15::DamageOutcome::Parried)
        OnDefenseResolved(Outcome == NarisP15::DamageOutcome::Evaded, Outcome == NarisP15::DamageOutcome::Parried);
    if (Outcome == NarisP15::DamageOutcome::Killed && CharacterMesh && CharacterMesh->GetAnimInstance())
        CharacterMesh->GetAnimInstance()->Montage_Stop(.1f);
}

void UNarisP15CombatComponent::HandleAnyDamage(AActor*, float Damage, const UDamageType*, AController*, AActor*)
{
    ApplyCombatDamage(Damage);
}

void UNarisP15CombatComponent::SetAttackWindow(bool bOpen)
{
    if (!bReady || !GetOwner() || !GetOwner()->HasAuthority()) return;
    Rules.SetAttackWindow(bOpen);
    bHasPreviousTip = false;
}

void UNarisP15CombatComponent::TraceWeapon()
{
    if (!Rules.IsAttackWindowOpen() || !CharacterMesh || !GetWorld())
    {
        bHasPreviousTip = false;
        return;
    }
    if (!CharacterMesh->GetAnimInstance() || !CharacterMesh->GetAnimInstance()->Montage_IsPlaying(LightAttackMontage))
    {
        SetAttackWindow(false);
        return;
    }
    const FVector Base = CharacterMesh->GetSocketLocation(WeaponBaseSocket);
    const FVector Tip = CharacterMesh->GetSocketLocation(WeaponTipSocket);
    if (Base.ContainsNaN() || Tip.ContainsNaN()
        || FVector::DistSquared(GetOwner()->GetActorLocation(), Base) > FMath::Square(MaxWeaponReach)
        || FVector::DistSquared(GetOwner()->GetActorLocation(), Tip) > FMath::Square(MaxWeaponReach)
        || FVector::DistSquared(Base, Tip) > FMath::Square(MaxWeaponReach))
    {
        bHasPreviousTip = false;
        return;
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(NarisP15Weapon), false, GetOwner());
    FCollisionObjectQueryParams Objects;
    Objects.AddObjectTypesToQuery(ECC_Pawn);
    TArray<FHitResult> Hits;
    GetWorld()->SweepMultiByObjectType(Hits, Base, Tip, FQuat::Identity, Objects,
        FCollisionShape::MakeSphere(TraceRadius), Params);
    if (bHasPreviousTip && FVector::DistSquared(PreviousTip, Tip) <= FMath::Square(MaxWeaponReach))
    {
        TArray<FHitResult> Trail;
        GetWorld()->SweepMultiByObjectType(Trail, PreviousTip, Tip, FQuat::Identity, Objects,
            FCollisionShape::MakeSphere(TraceRadius), Params);
        Hits.Append(Trail);
    }
    PreviousTip = Tip; bHasPreviousTip = true;
    for (const FHitResult& Hit : Hits)
    {
        AActor* Target = Hit.GetActor();
        if (!IsValid(Target) || Target == GetOwner() || !Target->ActorHasTag(DamageableTag)) continue;
        FHitResult Obstruction;
        if (GetWorld()->LineTraceSingleByChannel(Obstruction, Base, Target->GetActorLocation(), ECC_Visibility, Params)
            && Obstruction.GetActor() != Target) continue;
        if (!Rules.RegisterHit(Target->GetUniqueID())) continue;
        UGameplayStatics::ApplyDamage(Target, LightAttackDamage, GetOwner()->GetInstigatorController(),
            GetOwner(), UDamageType::StaticClass());
    }
}

void UNarisP15CombatComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    if (!bReady || !GetOwner() || !GetOwner()->HasAuthority()) return;
    Rules.Tick(DeltaTime);
    SyncVitals();
    TraceWeapon();
}
