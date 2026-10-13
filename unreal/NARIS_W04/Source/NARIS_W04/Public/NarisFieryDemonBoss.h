#pragma once

#include "CoreMinimal.h"
#include "BoneBeastBoss.h"
#include "TimerManager.h"
#include "NarisFieryDemonBoss.generated.h"

class UAnimSequence;

/** Optional Ash Gate encounter. Reuses existing boss health, saves and damage. */
UCLASS(Blueprintable)
class NARIS_W04_API ANarisFieryDemonBoss : public ABoneBeastBoss
{
    GENERATED_BODY()

public:
    ANarisFieryDemonBoss();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|FieryDemon")
    float AggroRadius = 1300.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|FieryDemon")
    float ImpactDelay = 0.55f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|FieryDemon")
    bool bChasePlayer = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|FieryDemon|Animation")
    TObjectPtr<UAnimSequence> IdleAnimation = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|FieryDemon|Animation")
    TObjectPtr<UAnimSequence> SmashAnimation = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|FieryDemon|Animation")
    TObjectPtr<UAnimSequence> NovaAnimation = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|FieryDemon|Animation")
    TObjectPtr<UAnimSequence> EnrageAnimation = nullptr;

private:
    UFUNCTION()
    void OnDemonBossEvent(FName EventName);

    void ResolveQueuedImpact();
    void RestoreIdleAnimation();

    FTimerHandle ImpactTimer;
    FTimerHandle IdleTimer;
    bool bStrikeQueued = false;
};
