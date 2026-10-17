#include "NarisP15CombatComponent.h"

#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/Skeleton.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/DamageType.h"
#include "Kismet/GameplayStatics.h"
#include "Net/UnrealNetwork.h"
#include "NarisP15AttackWindowNotify.h"
#include "NarisP15CancelWindowNotify.h"

static_assert(static_cast<uint8>(ENarisP15ControlPhase::Unavailable) == static_cast<uint8>(NarisP15::ControlPhase::Unavailable));
static_assert(static_cast<uint8>(ENarisP15ControlPhase::Free) == static_cast<uint8>(NarisP15::ControlPhase::Free));
static_assert(static_cast<uint8>(ENarisP15ControlPhase::Action) == static_cast<uint8>(NarisP15::ControlPhase::Action));
static_assert(static_cast<uint8>(ENarisP15ControlPhase::Recovery) == static_cast<uint8>(NarisP15::ControlPhase::Recovery));
static_assert(static_cast<uint8>(ENarisP15ControlPhase::Hit) == static_cast<uint8>(NarisP15::ControlPhase::Hit));
static_assert(static_cast<uint8>(ENarisP15ControlPhase::Dead) == static_cast<uint8>(NarisP15::ControlPhase::Dead));

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
    Config.InputBufferSeconds = InputBufferSeconds;
    Config.HitRecoverySeconds = HitRecoverySeconds;
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
    BindAnimationInstance();
    GetOwner()->OnTakeAnyDamage.AddDynamic(this, &UNarisP15CombatComponent::HandleAnyDamage);
    if (!GetOwner()->GetIsReplicated() && GetNetMode() != NM_Standalone)
        UE_LOG(LogTemp, Warning, TEXT("NARIS P15 owner must replicate for network RPCs."));
    SyncVitals();
}

TArray<FString> UNarisP15CombatComponent::GetSetupIssues() const
{
    TArray<FString> Issues;
    const ACharacter* Character = Cast<ACharacter>(GetOwner());
    const USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
    const USkeletalMesh* Asset = Mesh ? Mesh->GetSkeletalMeshAsset() : nullptr;
    if (!Asset || !Asset->GetSkeleton())
    {
        Issues.Add(TEXT("A Character with an assigned skeletal mesh and Skeleton is required."));
        return Issues;
    }
    if (!Mesh->GetAnimClass()) Issues.Add(TEXT("Assign an Animation Blueprint that evaluates the combat montage Slot."));
    if (!Mesh->DoesSocketExist(WeaponBaseSocket) || !Mesh->DoesSocketExist(WeaponTipSocket))
        Issues.Add(TEXT("The character mesh is missing weapon base/tip sockets."));
    const UAnimMontage* Montages[] = {LightAttackMontage, DodgeMontage, ParryMontage};
    const TCHAR* Names[] = {TEXT("LightAttack"), TEXT("Dodge"), TEXT("Parry")};
    for (int32 Index = 0; Index < 3; ++Index)
    {
        const UAnimMontage* Montage = Montages[Index];
        if (!Montage)
        {
            Issues.Add(FString::Printf(TEXT("Assign the %s montage."), Names[Index]));
            continue;
        }
        if (Montage->GetSkeleton() != Asset->GetSkeleton())
            Issues.Add(FString::Printf(TEXT("%s montage must use the character mesh Skeleton."), Names[Index]));
        if (!FMath::IsFinite(Montage->GetPlayLength()) || Montage->GetPlayLength() <= 0.f
            || !FMath::IsFinite(Montage->RateScale) || !FMath::IsNearlyEqual(Montage->RateScale, 1.f))
            Issues.Add(FString::Printf(TEXT("%s montage requires a positive duration and RateScale 1."), Names[Index]));
        if (Montage->SlotAnimTracks.IsEmpty())
            Issues.Add(FString::Printf(TEXT("%s montage has no Slot track."), Names[Index]));
        TArray<FVector2D> CancelWindows;
        for (const FAnimNotifyEvent& Event : Montage->Notifies)
        {
            if (!Cast<UNarisP15CancelWindowNotify>(Event.NotifyStateClass)) continue;
            const float Start = Event.GetTime(), Duration = Event.GetDuration();
            if (!FMath::IsFinite(Start) || !FMath::IsFinite(Duration) || Start <= 0.f
                || Duration <= 0.f || Start + Duration > Montage->GetPlayLength() + KINDA_SMALL_NUMBER)
                Issues.Add(FString::Printf(TEXT("%s cancel window must begin after time zero and stay inside its montage."), Names[Index]));
            else CancelWindows.Add(FVector2D(Start, Start + Duration));
        }
        CancelWindows.Sort([](const FVector2D& A, const FVector2D& B) { return A.X < B.X; });
        for (int32 Window = 1; Window < CancelWindows.Num(); ++Window)
            if (CancelWindows[Window].X < CancelWindows[Window - 1].Y)
                Issues.Add(FString::Printf(TEXT("%s cancel windows must not overlap."), Names[Index]));
    }
    if (LightAttackMontage)
    {
        bool bHasWindow = false;
        for (const FAnimNotifyEvent& Event : LightAttackMontage->Notifies)
        {
            if (Cast<UNarisP15AttackWindowNotify>(Event.NotifyStateClass))
            {
                const float Start = Event.GetTime(), Duration = Event.GetDuration();
                if (FMath::IsFinite(Start) && FMath::IsFinite(Duration) && Start >= 0.f
                    && Duration > 0.f && Start + Duration <= LightAttackMontage->GetPlayLength() + KINDA_SMALL_NUMBER)
                    bHasWindow = true;
                else Issues.Add(TEXT("Attack-window notify timing is outside the montage."));
            }
        }
        if (!bHasWindow) Issues.Add(TEXT("LightAttack needs a positive NARIS P15 Attack Window notify state."));
    }
    NarisP15::Config Config;
    Config.InputBufferSeconds = InputBufferSeconds;
    Config.HitRecoverySeconds = HitRecoverySeconds;
    Config.MaxHealth = MaxHealth; Config.MaxStamina = MaxStamina;
    Config.AttackCost = LightAttackCost; Config.DodgeCost = DodgeCost; Config.ParryCost = ParryCost;
    Config.RegenPerSecond = StaminaRegenPerSecond; Config.RegenDelay = RegenDelaySeconds;
    Config.DodgeInvulnerabilityStart = DodgeInvulnerabilityStart;
    Config.DodgeInvulnerabilityEnd = DodgeInvulnerabilityEnd;
    if (DodgeMontage) Config.DodgeDuration = DodgeMontage->GetPlayLength();
    if (!Config.IsValid()) Issues.Add(TEXT("Invalid health, stamina, cost or defense-window configuration."));
    if (LightAttackCost > MaxStamina || DodgeCost > MaxStamina || ParryCost > MaxStamina)
        Issues.Add(TEXT("Each action cost must be affordable at full stamina."));
    if (!FMath::IsFinite(TraceRadius) || TraceRadius <= 0.f
        || !FMath::IsFinite(MaxWeaponReach) || MaxWeaponReach <= 0.f
        || !FMath::IsFinite(LightAttackDamage) || LightAttackDamage <= 0.f)
        Issues.Add(TEXT("Weapon damage, radius and reach must be finite and positive."));
    if (DamageableTag.IsNone()) Issues.Add(TEXT("Assign a damageable target Actor Tag."));
    return Issues;
}

void UNarisP15CombatComponent::BindAnimationInstance()
{
    UAnimInstance* Next = CharacterMesh ? CharacterMesh->GetAnimInstance() : nullptr;
    if (BoundAnimInstance.Get() == Next) return;
    if (UAnimInstance* Previous = BoundAnimInstance.Get())
    {
        Previous->OnMontageBlendingOut.RemoveDynamic(this, &UNarisP15CombatComponent::HandleMontageBlendingOut);
        Previous->OnMontageEnded.RemoveDynamic(this, &UNarisP15CombatComponent::HandleMontageEnded);
    }
    CancelActiveAction();
    BoundAnimInstance = Next;
    if (Next)
    {
        Next->OnMontageBlendingOut.AddDynamic(this, &UNarisP15CombatComponent::HandleMontageBlendingOut);
        Next->OnMontageEnded.AddDynamic(this, &UNarisP15CombatComponent::HandleMontageEnded);
    }
}

void UNarisP15CombatComponent::CancelActiveAction(bool bNotifyClients, bool bClearBuffered)
{
    if (bClearBuffered) Rules.ClearBufferedAction();
    Rules.CancelAction();
    UAnimMontage* Cancelled = ActiveMontage;
    ActiveMontage = nullptr;
    bHasPreviousTip = false;
    if (bNotifyClients && Cancelled && GetOwner() && GetOwner()->HasAuthority())
        MulticastCancelAction(Cancelled);
    if (bNotifyClients) SyncControlPhase();
}

void UNarisP15CombatComponent::StopActiveMontage()
{
    UAnimMontage* Cancelled = ActiveMontage;
    CancelActiveAction();
    if (Cancelled && CharacterMesh && CharacterMesh->GetAnimInstance())
        CharacterMesh->GetAnimInstance()->Montage_Stop(.12f, Cancelled);
}

void UNarisP15CombatComponent::RequestCancelCurrentAction()
{
    if (!GetOwner()) return;
    if (GetOwner()->HasAuthority()) TryCancelCurrentAction();
    else if (GetOwner()->HasLocalNetOwner()) ServerRequestCancelCurrentAction();
}

void UNarisP15CombatComponent::ServerRequestCancelCurrentAction_Implementation() { TryCancelCurrentAction(); }

void UNarisP15CombatComponent::TryCancelCurrentAction()
{
    if (bReady && GetOwner() && GetOwner()->HasAuthority() && Rules.TryCancelInWindow())
        StopActiveMontage();
}

void UNarisP15CombatComponent::SetCancelWindow(bool bOpen, UAnimSequenceBase* SourceAnimation)
{
    if (bReady && GetOwner() && GetOwner()->HasAuthority() && ActiveMontage
        && SourceAnimation == ActiveMontage.Get())
        Rules.SetCancelWindow(bOpen);
}

void UNarisP15CombatComponent::HandleMontageBlendingOut(UAnimMontage* Montage, bool bInterrupted)
{
    if (bInterrupted && Montage == ActiveMontage) CancelActiveAction();
}

void UNarisP15CombatComponent::HandleMontageEnded(UAnimMontage* Montage, bool bInterrupted)
{
    if (Montage == ActiveMontage) CancelActiveAction(true, bInterrupted);
}

void UNarisP15CombatComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UAnimInstance* Previous = BoundAnimInstance.Get())
    {
        Previous->OnMontageBlendingOut.RemoveDynamic(this, &UNarisP15CombatComponent::HandleMontageBlendingOut);
        Previous->OnMontageEnded.RemoveDynamic(this, &UNarisP15CombatComponent::HandleMontageEnded);
    }
    if (GetOwner()) GetOwner()->OnTakeAnyDamage.RemoveDynamic(this, &UNarisP15CombatComponent::HandleAnyDamage);
    CancelActiveAction(false);
    Super::EndPlay(EndPlayReason);
}

void UNarisP15CombatComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(UNarisP15CombatComponent, Health);
    DOREPLIFETIME(UNarisP15CombatComponent, Stamina);
    DOREPLIFETIME(UNarisP15CombatComponent, MaxHealth);
    DOREPLIFETIME(UNarisP15CombatComponent, MaxStamina);
    DOREPLIFETIME(UNarisP15CombatComponent, ControlPhase);
}

void UNarisP15CombatComponent::OnRep_ControlPhase() { OnControlPhaseChanged(); }

void UNarisP15CombatComponent::SyncControlPhase()
{
    if (!GetOwner() || !GetOwner()->HasAuthority()) return;
    const auto Next = static_cast<ENarisP15ControlPhase>(Rules.GetControlPhase());
    if (Next != ControlPhase) { ControlPhase = Next; OnControlPhaseChanged(); }
}

void UNarisP15CombatComponent::OnRep_Vitals()
{
    if (IsDead() && CharacterMesh && CharacterMesh->GetAnimInstance())
        CharacterMesh->GetAnimInstance()->Montage_Stop(.1f);
    OnVitalsChanged();
}

void UNarisP15CombatComponent::SyncVitals()
{
    SyncControlPhase();
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

void UNarisP15CombatComponent::ClearBufferedInput()
{
    if (!GetOwner()) return;
    if (GetOwner()->HasAuthority()) Rules.ClearBufferedAction();
    else if (GetOwner()->HasLocalNetOwner()) ServerClearBufferedInput();
}

void UNarisP15CombatComponent::ServerClearBufferedInput_Implementation() { Rules.ClearBufferedAction(); }

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
    BindAnimationInstance();
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
    if (Rules.BufferAction(Requested)) return;
    UAnimInstance* Instance = CharacterMesh->GetAnimInstance();
    bool bPlaybackStarted = false;
    const bool bCommitted = Rules.TryStartPresented(Requested, [this, Instance, Montage, &bPlaybackStarted]()
        {
            const float Played = Instance->Montage_Play(Montage);
            bPlaybackStarted = FMath::IsFinite(Played) && Played > 0.f;
            return bPlaybackStarted && CharacterMesh && CharacterMesh->GetAnimInstance() == Instance;
        });
    if (!bCommitted)
    {
        if (bPlaybackStarted && IsValid(Instance)) Instance->Montage_Stop(.1f, Montage);
        return;
    }
    ActiveMontage = Montage;
    bHasPreviousTip = false;
    SyncVitals();
    MulticastPresentAction(Action);
}

void UNarisP15CombatComponent::MulticastPresentAction_Implementation(ENarisP15Action Action)
{
    if (GetOwner() && !GetOwner()->HasAuthority() && CharacterMesh && CharacterMesh->GetAnimInstance() && GetMontage(Action))
        CharacterMesh->GetAnimInstance()->Montage_Play(GetMontage(Action));
    OnActionPresented(Action);
}

void UNarisP15CombatComponent::MulticastCancelAction_Implementation(UAnimMontage* Montage)
{
    if (GetOwner() && !GetOwner()->HasAuthority() && CharacterMesh && CharacterMesh->GetAnimInstance() && Montage)
        CharacterMesh->GetAnimInstance()->Montage_Stop(.1f, Montage);
}

void UNarisP15CombatComponent::ApplyCombatDamage(float Amount)
{
    if (!bReady || !GetOwner() || !GetOwner()->HasAuthority()) return;
    const NarisP15::DamageOutcome Outcome = Rules.Damage(Amount);
    if (Outcome == NarisP15::DamageOutcome::Applied && HitRecoverySeconds > 0.f)
        StopActiveMontage();
    SyncVitals();
    if (Outcome == NarisP15::DamageOutcome::Evaded || Outcome == NarisP15::DamageOutcome::Parried)
        OnDefenseResolved(Outcome == NarisP15::DamageOutcome::Evaded, Outcome == NarisP15::DamageOutcome::Parried);
    if (Outcome == NarisP15::DamageOutcome::Killed && CharacterMesh && CharacterMesh->GetAnimInstance())
    {
        CancelActiveAction();
        CharacterMesh->GetAnimInstance()->Montage_Stop(.1f);
    }
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
    BindAnimationInstance();
    Rules.Tick(DeltaTime);
    if (Rules.GetAction() != NarisP15::Action::Idle
        && (!CharacterMesh || !CharacterMesh->GetAnimInstance() || !ActiveMontage
            || !CharacterMesh->GetAnimInstance()->Montage_IsPlaying(ActiveMontage)))
        CancelActiveAction();
    NarisP15::Action Buffered;
    if (Rules.TakeBufferedAction(Buffered))
    {
        switch (Buffered)
        {
        case NarisP15::Action::LightAttack: CommitAction(ENarisP15Action::LightAttack); break;
        case NarisP15::Action::Dodge: CommitAction(ENarisP15Action::Dodge); break;
        case NarisP15::Action::Parry: CommitAction(ENarisP15Action::Parry); break;
        default: break;
        }
    }
    SyncVitals();
    TraceWeapon();
}
