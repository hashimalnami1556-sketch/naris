#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisCombatRules.h"
#include "NarisP15CombatComponent.generated.h"

class UAnimMontage;
class USkeletalMeshComponent;
class UDamageType;
class AController;
class UAnimInstance;

UENUM(BlueprintType)
enum class ENarisP15Action : uint8 { LightAttack, Dodge, Parry };

// اسم مستقل لتفادي تعارض UHT مع UNarisCombatComponent في مشروع W04.
UCLASS(ClassGroup=(Naris), Blueprintable, meta=(BlueprintSpawnableComponent))
class NARISCOMBAT_API UNarisP15CombatComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UNarisP15CombatComponent();

    UPROPERTY(ReplicatedUsing=OnRep_Vitals, BlueprintReadOnly, Category="Naris|Vitals") float Health = 100.f;
    UPROPERTY(ReplicatedUsing=OnRep_Vitals, BlueprintReadOnly, Category="Naris|Vitals") float Stamina = 100.f;
    UPROPERTY(EditDefaultsOnly, ReplicatedUsing=OnRep_Vitals, BlueprintReadOnly, Category="Naris|Vitals") float MaxHealth = 100.f;
    UPROPERTY(EditDefaultsOnly, ReplicatedUsing=OnRep_Vitals, BlueprintReadOnly, Category="Naris|Vitals") float MaxStamina = 100.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Combat") float LightAttackCost = 20.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Combat") float DodgeCost = 30.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Combat") float ParryCost = 15.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Combat") float StaminaRegenPerSecond = 18.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Combat") float RegenDelaySeconds = .75f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Combat") float DodgeInvulnerabilityStart = .1f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Combat") float DodgeInvulnerabilityEnd = .35f;

    UPROPERTY(EditDefaultsOnly, Category="Naris|Animation") TObjectPtr<UAnimMontage> LightAttackMontage;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Animation") TObjectPtr<UAnimMontage> DodgeMontage;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Animation") TObjectPtr<UAnimMontage> ParryMontage;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Weapon") FName WeaponBaseSocket = TEXT("weapon_base");
    UPROPERTY(EditDefaultsOnly, Category="Naris|Weapon") FName WeaponTipSocket = TEXT("weapon_tip");
    UPROPERTY(EditDefaultsOnly, Category="Naris|Weapon") FName DamageableTag = TEXT("NarisDamageable");
    UPROPERTY(EditDefaultsOnly, Category="Naris|Weapon") float TraceRadius = 12.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Weapon") float MaxWeaponReach = 300.f;
    UPROPERTY(EditDefaultsOnly, Category="Naris|Weapon") float LightAttackDamage = 25.f;

    UFUNCTION(BlueprintCallable, Category="Naris|Combat") void RequestLightAttack();
    UFUNCTION(BlueprintCallable, Category="Naris|Combat") void RequestDodge();
    UFUNCTION(BlueprintCallable, Category="Naris|Combat") void RequestParry();
    UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category="Naris|Combat") void ApplyCombatDamage(float Amount);
    UFUNCTION(BlueprintPure, Category="Naris|Combat") bool IsDead() const { return Health <= 0.f; }
    UFUNCTION(BlueprintPure, Category="Naris|Combat") TArray<FString> GetSetupIssues() const;
    UFUNCTION(BlueprintImplementableEvent, Category="Naris|Combat") void OnVitalsChanged();
    // عرض فقط؛ الصحة وإصابات السلاح يحسبها السيرفر.
    UFUNCTION(BlueprintImplementableEvent, Category="Naris|Combat") void OnActionPresented(ENarisP15Action Action);
    UFUNCTION(BlueprintImplementableEvent, Category="Naris|Combat") void OnDefenseResolved(bool bEvaded, bool bParried);

    void SetAttackWindow(bool bOpen);
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    UFUNCTION(Server, Reliable) void ServerRequestAction(ENarisP15Action Action);
    UFUNCTION(NetMulticast, Reliable) void MulticastPresentAction(ENarisP15Action Action);
    UFUNCTION(NetMulticast, Reliable) void MulticastCancelAction(UAnimMontage* Montage);
    UFUNCTION() void OnRep_Vitals();
    UFUNCTION() void HandleAnyDamage(AActor* DamagedActor, float Damage, const UDamageType* DamageType,
        AController* InstigatedBy, AActor* DamageCauser);
    UFUNCTION() void HandleMontageBlendingOut(UAnimMontage* Montage, bool bInterrupted);
    UFUNCTION() void HandleMontageEnded(UAnimMontage* Montage, bool bInterrupted);

private:
    NarisP15::Rules Rules;
    bool bReady = false;
    bool bHasPreviousTip = false;
    FVector PreviousTip = FVector::ZeroVector;
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> CharacterMesh;
    UPROPERTY() TObjectPtr<UAnimMontage> ActiveMontage;
    TWeakObjectPtr<UAnimInstance> BoundAnimInstance;
    UAnimMontage* GetMontage(ENarisP15Action Action) const;
    void RequestAction(ENarisP15Action Action);
    void CommitAction(ENarisP15Action Action);
    void SyncVitals();
    void TraceWeapon();
    void BindAnimationInstance();
    void CancelActiveAction(bool bNotifyClients = true);
};
