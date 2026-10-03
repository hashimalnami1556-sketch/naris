#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NarisEnvironmentQuestTrigger.generated.h"

class UBoxComponent;

UENUM(BlueprintType)
enum class ENarisEnvironmentTriggerType : uint8
{
    RegionEnter,
    LandmarkDiscover,
    CaveEnter,
    MountainPeak,
    WaterEnter,
    HolySite,
    BossArena,
    SecretArea,
    TreasureRoom,
    LavaZone
};

UCLASS(Blueprintable)
class NARIS_W04_API ANarisEnvironmentQuestTrigger : public AActor
{
    GENERATED_BODY()

public:
    ANarisEnvironmentQuestTrigger();

    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Quest")
    TObjectPtr<UBoxComponent> TriggerBounds;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Quest")
    FName TriggerId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Quest")
    ENarisEnvironmentTriggerType TriggerType = ENarisEnvironmentTriggerType::RegionEnter;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Quest")
    FName TargetId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Quest")
    FName RequiredQuest;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Quest")
    FName QuestToStart;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Quest")
    int32 QuestStepToSet = -1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Quest")
    bool bOneTime = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Quest")
    bool bAutoSave = true;

    UFUNCTION(BlueprintPure, Category="NARIS|Quest")
    bool IsConsumed() const { return bConsumed; }

protected:
    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|Quest")
    void OnEnvironmentTriggered(
        ENarisEnvironmentTriggerType Type,
        FName InTargetId
    );

private:
    UFUNCTION()
    void HandleBeginOverlap(
        UPrimitiveComponent* OverlappedComponent,
        AActor* OtherActor,
        UPrimitiveComponent* OtherComp,
        int32 OtherBodyIndex,
        bool bFromSweep,
        const FHitResult& SweepResult
    );

    FString GetPersistenceKey() const;

    bool bConsumed = false;
};
