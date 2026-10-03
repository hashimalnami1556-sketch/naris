#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "TimerManager.h"
#include "NarisDailyNPC.generated.h"

UENUM(BlueprintType)
enum class ENarisNPCActivity : uint8
{
    Idle, Work, Patrol, Rest, Shelter, Trade
};

USTRUCT(BlueprintType)
struct FNarisNPCScheduleEntry
{
    GENERATED_BODY()

    // Hours are within [0,24). Intervals are start-inclusive, end-exclusive.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|NPC")
    float StartHour = 8.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|NPC")
    float EndHour = 18.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|NPC")
    ENarisNPCActivity Activity = ENarisNPCActivity::Work;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|NPC")
    TObjectPtr<AActor> Destination = nullptr;
};

UCLASS(Blueprintable)
class NARIS_W04_API ANarisDailyNPC : public ACharacter
{
    GENERATED_BODY()

public:
    ANarisDailyNPC();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|NPC")
    FName NPCId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|NPC")
    TArray<FNarisNPCScheduleEntry> DailySchedule;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|NPC")
    TObjectPtr<AActor> StormShelter = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|NPC")
    FName QuestToOffer;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|NPC", meta=(ClampMin="0.1", ClampMax="60.0"))
    float ScheduleIntervalSeconds = 2.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|NPC", meta=(ClampMin="1.0"))
    float GameDayDurationSeconds = 1800.f;

    UFUNCTION(BlueprintCallable, Category="NARIS|NPC")
    void SetWorldHour(float InHour);

    UFUNCTION(BlueprintCallable, Category="NARIS|NPC")
    void SetStormActive(bool bActive);

    UFUNCTION(BlueprintCallable, Category="NARIS|NPC")
    bool InteractNPC(AActor* Interactor);

    UFUNCTION(BlueprintPure, Category="NARIS|NPC")
    ENarisNPCActivity GetCurrentActivity() const { return CurrentActivity; }

    UFUNCTION(BlueprintPure, Category="NARIS|NPC")
    static bool IsScheduledAt(const FNarisNPCScheduleEntry& Entry, float WorldHour);

protected:
    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|NPC")
    void OnActivityChanged(ENarisNPCActivity NewActivity);

private:
    void UpdateRoutine();
    void ApplyActivity(ENarisNPCActivity NewActivity, AActor* Destination);

    FTimerHandle RoutineTimer;
    ENarisNPCActivity CurrentActivity = ENarisNPCActivity::Idle;
    TWeakObjectPtr<AActor> CurrentDestination;
    float WorldHourOverride = -1.f;
    bool bStormActive = false;
    bool bQuestOffered = false;
};
