#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NarisBossArenaController.generated.h"

class ABoneBeastBoss;
class UBoxComponent;
class UPrimitiveComponent;
class USceneComponent;
struct FHitResult;
class UNarisPresentationComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(
    FNarisBossArenaEvent,
    FName,
    EventName
);

UCLASS(Blueprintable)
class NARIS_W04_API ANarisBossArenaController : public AActor
{
    GENERATED_BODY()

public:
    ANarisBossArenaController();

    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Arena")
    TObjectPtr<USceneComponent> SceneRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Arena")
    TObjectPtr<UBoxComponent> EntryBlocker;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Arena")
    TObjectPtr<UBoxComponent> EncounterTrigger;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Presentation")
    TObjectPtr<UNarisPresentationComponent> Presentation;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Arena")
    TObjectPtr<ABoneBeastBoss> Boss = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Arena")
    bool bArenaClosed = false;

    UPROPERTY(BlueprintAssignable, Category="NARIS|Arena")
    FNarisBossArenaEvent OnArenaEvent;

    UFUNCTION(BlueprintCallable, Category="NARIS|Arena")
    void SetBoss(ABoneBeastBoss* NewBoss);

    UFUNCTION(BlueprintCallable, Category="NARIS|Arena")
    void SetArenaClosed(bool bClosed);

private:
    UFUNCTION()
    void HandleBossEvent(FName EventName);

    UFUNCTION()
    void HandleEncounterOverlap(
        UPrimitiveComponent* OverlappedComponent,
        AActor* OtherActor,
        UPrimitiveComponent* OtherComp,
        int32 OtherBodyIndex,
        bool bFromSweep,
        const FHitResult& SweepResult
    );

    void BindBoss();
};
