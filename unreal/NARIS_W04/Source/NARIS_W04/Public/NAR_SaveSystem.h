// NAR_SaveSystem.h — نظام الحفظ الكامل
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_SaveSystem.generated.h"

// ============================================
// بيانات الحفظ
// ============================================
USTRUCT(BlueprintType)
struct FGameSaveData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    float TimePlayedSeconds = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    float GameTimeOfDay = 12.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    FVector PlayerLocation = FVector::ZeroVector;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    FRotator PlayerRotation = FRotator::ZeroRotator;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    int32 CurrentLevel = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    int32 PlayerHealth = 100;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    int32 PlayerEnergy = 100;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    int32 PlayerLevel = 1;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    int32 PlayerXP = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    int32 ShardCount = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    int32 EnemiesDefeated = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    int32 QuestsCompleted = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    FDateTime SaveDateTime = FDateTime::Now();

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    int32 SaveSlotIndex = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    FString SaveName = TEXT("AutoSave");

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    TArray<int32> CompletedQuestIDs;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    TArray<int32> UnlockedAchievementIDs;

    UPROPERTY(BlueprintReadWrite, Category = "Save")
    TMap<FString, int32> InventoryItems;
};

/**
 * UNAR_SaveSystem — نظام الحفظ
 * يدير: الحفظ والتحميل + فتحات الحفظ المتعددة + البيانات الدائمة
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_SaveSystem : public UActorComponent
{
    GENERATED_BODY()

public:
    UNAR_SaveSystem();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    // ============================================
    // التهيئة
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Save")
    void Initialize();

    // ============================================
    // الحفظ
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Save")
    void SaveGame(int32 SaveSlotIndex = 0, FString SaveName = TEXT("Save"));

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Save")
    void QuickSave();

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Save")
    void AutoSave();

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Save")
    bool SaveGameToSlot(const FGameSaveData& SaveData);

    // ============================================
    // التحميل
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Load")
    bool LoadGame(int32 SaveSlotIndex = 0);

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Load")
    bool LoadGameFromSlot(int32 SaveSlotIndex, FGameSaveData& OutSaveData);

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Load")
    FGameSaveData GetLastSaveData() const { return LastSaveData; }

    // ============================================
    // إدارة فتحات الحفظ
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Slots")
    void DeleteSaveSlot(int32 SaveSlotIndex);

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Slots")
    bool DoesSaveSlotExist(int32 SaveSlotIndex) const;

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Slots")
    int32 GetTotalSaveSlots() const { return MaxSaveSlots; }

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Slots")
    void GetAllSaveSlots(TArray<FGameSaveData>& OutSaveDataArray);

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Slots")
    void ClearAllSaves();

    // ============================================
    // إدارة البيانات
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Data")
    void UpdatePlayerData(int32 Health, int32 Energy, int32 Level, int32 XP);

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Data")
    void UpdatePlayerLocation(FVector NewLocation, FRotator NewRotation);

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Data")
    void AddShards(int32 Amount);

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Data")
    void AddEnemyDefeated();

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Data")
    void AddQuestCompleted(int32 QuestID);

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Data")
    void UnlockAchievement(int32 AchievementID);

    UFUNCTION(BlueprintCallable, Category = "NAR|Save|Data")
    void AddInventoryItem(FString ItemName, int32 Quantity = 1);

    UFUNCTION(BlueprintPure, Category = "NAR|Save|Data")
    FGameSaveData GetCurrentGameData() const { return CurrentGameData; }

    // ============================================
    // أحداث
    // ============================================
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnGameSaved, int32, SaveSlot);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Save|Events")
    FOnGameSaved OnGameSaved;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnGameLoaded, int32, SaveSlot);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Save|Events")
    FOnGameLoaded OnGameLoaded;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSaveDeleted, int32, SaveSlot);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Save|Events")
    FOnSaveDeleted OnSaveDeleted;

protected:
    UPROPERTY(BlueprintReadOnly, Category = "NAR|Save|Data")
    FGameSaveData CurrentGameData;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|Save|Data")
    FGameSaveData LastSaveData;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Save|Settings")
    int32 MaxSaveSlots = 10;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Save|Settings")
    float AutoSaveInterval = 300.0f; // 5 دقائق

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Save|Settings")
    FString SaveGamePath = TEXT("Saves/");

private:
    float AutoSaveTimer = 0.0f;
    int32 CurrentAutoSaveSlot = -1;

    FString GetSaveSlotFileName(int32 SlotIndex) const;
    void TickAutoSave(float DeltaTime);
};
