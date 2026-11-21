#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisGameplayTypes.h"
#include "NarisHeroCharacter.generated.h"

class AController;
class ACelestialWolf;
class UNarisCombatComponent;
class UNarisEnergyComponent;
class UNarisLockOnComponent;
class UNarisInteractionComponent;
class UNarisPresentationComponent;
class UNarisSwimmingComponent;
class UNarisWeatherGameplayComponent;
class USpringArmComponent;
class UCameraComponent;
struct FDamageEvent;

UCLASS(Blueprintable)
class NARIS_W04_API ANarisHeroCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ANarisHeroCharacter();

    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void Tick(float DeltaSeconds) override;
    virtual float TakeDamage(
        float DamageAmount,
        FDamageEvent const& DamageEvent,
        AController* EventInstigator,
        AActor* DamageCauser
    ) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UNarisCombatComponent> Combat;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UNarisEnergyComponent> Energy;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UNarisLockOnComponent> LockOn;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UNarisInteractionComponent> Interaction;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Presentation")
    TObjectPtr<UNarisPresentationComponent> Presentation;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Water")
    TObjectPtr<UNarisSwimmingComponent> Swimming;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Weather")
    TObjectPtr<UNarisWeatherGameplayComponent> WeatherGameplay;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<USpringArmComponent> CameraBoom;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UCameraComponent> FollowCamera;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement")
    float WalkSpeed = 500.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement")
    float SprintSpeed = 700.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Combat|Tuning")
    float MeleeRange = 260.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Combat|Tuning")
    float LightAttackDamage = 12.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Combat|Tuning")
    float LightAttackPoiseDamage = 15.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Combat|Tuning")
    float HeavyAttackDamage = 24.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Combat|Tuning")
    float HeavyAttackPoiseDamage = 30.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Combat|Defense")
    float ParryWindowSeconds = 0.18f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Combat|Defense")
    float DodgeInvulnerabilitySeconds = 0.28f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Combat|Energy")
    float DodgeEnergyCost = 15.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Combat|Energy")
    float ParryEnergyCost = 8.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Combat|Animation")
    bool bImmediateSmokeAttackHit = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Respawn")
    float RespawnDelaySeconds = 2.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Respawn")
    float CheckpointRespawnZOffset = 100.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Respawn")
    bool bRespawnAtCheckpoint = true;

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void LightAttack();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void HeavyAttack();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void Dodge();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void Parry();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void ResonanceBurst();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void ToggleLockOn();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat|Animation")
    void OpenAttackHitWindow();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat|Animation")
    void CloseAttackHitWindow();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat|Animation")
    bool CommitPendingAttackHit();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat|Animation")
    void CancelPendingAttack();

    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|Combat|Animation")
    void OnAttackRequested(ENarisAttackKind AttackKind);

    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|Combat|Animation")
    bool OnDodgeRequested();

    UFUNCTION(BlueprintCallable, Category="NARIS|Energy")
    void NextEssence();

    UFUNCTION(BlueprintCallable, Category="NARIS|Energy")
    void PreviousEssence();

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion")
    void CycleCompanionMode();

    UFUNCTION(BlueprintCallable, Category="NARIS|Interaction")
    void Interact();

    UFUNCTION(BlueprintCallable, Category="NARIS|Movement")
    void SetSprinting(bool bSprint);

    UFUNCTION(BlueprintCallable, Category="NARIS|Movement")
    void RefreshMovementSpeed();

    UFUNCTION(BlueprintPure, Category="NARIS|Movement")
    bool IsSprinting() const { return bIsSprinting; }

    UFUNCTION(BlueprintCallable, Category="NARIS|System")
    void TogglePause();

    UFUNCTION(BlueprintCallable, Category="NARIS|Respawn")
    void RespawnAtCheckpoint();

protected:
    void MoveForward(float Value);
    void MoveRight(float Value);
    void MoveSwimVertical(float Value);
    void LookYaw(float Value);
    void LookPitch(float Value);
    void StartSprinting();
    void StopSprinting();

private:
    // Developer-only remote-command probe state. The behavior is compiled
    // exclusively under !UE_BUILD_SHIPPING; the state does not replicate.
#if !UE_BUILD_SHIPPING
    int32 NetWolfProbePhase = 0;
    float NetWolfProbeStartTime = -1.f;
#endif

    // Client-owned Hero RPCs: a placed Wolf is server-owned and cannot
    // receive meaningful client→server RPCs directly.
    UFUNCTION(Server, Reliable)
    void ServerInteractWithWolf(ACelestialWolf* Wolf);

    UFUNCTION(Server, Reliable)
    void ServerCycleCompanionMode();

    bool ApplyAttackToLockedTarget(float Damage, float PoiseDamage);
    void QueueAttack(ENarisAttackKind AttackKind);
    void HandleDeath();

    ENarisAttackKind PendingAttack = ENarisAttackKind::None;
    bool bAttackHitWindowOpen = false;
    bool bAttackHitConsumed = false;
    bool bDeathHandled = false;
    bool bIsSprinting = false;
};
