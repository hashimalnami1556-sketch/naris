#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisInteractable.h"
#include "CelestialWolf.generated.h"

class AActor;
class ABoneBeastBoss;
class UNarisPresentationComponent;

UENUM(BlueprintType)
enum class ENarisWolfMode : uint8
{
    Follow,
    Guard,
    Attack,
    Track,
    EchoLink
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FNarisWolfBonded);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(
    FNarisWolfModeChanged,
    ENarisWolfMode,
    NewMode
);

UCLASS(Blueprintable)
class NARIS_W04_API ACelestialWolf : public ACharacter, public INarisInteractable
{
    GENERATED_BODY()

public:
    ACelestialWolf();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Presentation")
    TObjectPtr<UNarisPresentationComponent> Presentation;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    ENarisWolfMode Mode = ENarisWolfMode::Guard;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion|Movement")
    float FollowDistance = 260.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion|Movement")
    float FollowSpeed = 560.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion|Combat")
    float AttackAcquireRadius = 1200.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion|Combat")
    float AttackRange = 180.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion|Combat")
    float AttackDamage = 18.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion|Combat")
    float AttackCooldownSeconds = 1.25f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion|Combat")
    bool bImmediateSmokeAttackImpact = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion|Track")
    float TrackAcceptanceRadius = 120.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion|EchoLink")
    float EchoLinkDistance = 320.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion|EchoLink")
    float EchoLinkPulseSeconds = 2.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    FString CompanionId = TEXT("CelestialWolf");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    FString RequiredGateId = TEXT("W04_AshGate");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    FString AutoSaveSlot = TEXT("NARIS_Auto");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    bool bAutoSave = true;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Companion")
    bool bBonded = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Companion|Track")
    TObjectPtr<AActor> TrackTarget = nullptr;

    UPROPERTY(BlueprintAssignable, Category="Companion")
    FNarisWolfBonded OnBonded;

    UPROPERTY(BlueprintAssignable, Category="Companion")
    FNarisWolfModeChanged OnModeChanged;

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion")
    void SetMode(ENarisWolfMode NewMode);

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion")
    void EchoLink();

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion|Combat")
    bool CommitAttackImpact();

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion|Combat")
    void CancelAttack();

    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|Companion|Combat")
    void OnAttackRequested();

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion")
    void CycleMode();

    UFUNCTION(BlueprintPure, Category="NARIS|Companion")
    FText GetModeDisplayName() const;

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion")
    void SetTrackTarget(AActor* NewTarget);

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion")
    bool BondWithPlayer(AActor* InstigatorActor);

    virtual bool Interact_Implementation(AActor* InstigatorActor) override;
    virtual FText GetInteractionPrompt_Implementation() const override;

private:
    FVector GuardAnchor = FVector::ZeroVector;
    float LastAttackTime = -1000.f;
    float LastEchoPulseTime = -1000.f;
    UPROPERTY(Transient)
    TObjectPtr<ABoneBeastBoss> PendingAttackTarget = nullptr;

    void MoveTowards(const FVector& Destination, float AcceptanceRadius);
    ABoneBeastBoss* FindAttackTarget() const;
    bool RequestAttack(ABoneBeastBoss* Target);
    void TickFollow();
    void TickGuard();
    void TickAttack();
    void TickTrack();
    void TickEchoLink();
};
