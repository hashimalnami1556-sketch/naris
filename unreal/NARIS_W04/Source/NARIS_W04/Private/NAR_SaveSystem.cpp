// NAR_SaveSystem.cpp — تنفيذ نظام الحفظ
#include "NAR_SaveSystem.h"
#include "Kismet/GameplayStatics.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "JsonUtilities.h"

UNAR_SaveSystem::UNAR_SaveSystem()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickInterval = 1.0f;
}

void UNAR_SaveSystem::BeginPlay()
{
    Super::BeginPlay();
    Initialize();
}

void UNAR_SaveSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    TickAutoSave(DeltaTime);
}

void UNAR_SaveSystem::Initialize()
{
    CurrentGameData = FGameSaveData();
    CurrentGameData.SaveDateTime = FDateTime::Now();
    AutoSaveTimer = 0.0f;

    UE_LOG(LogTemp, Log, TEXT("[NAR_Save] نظام الحفظ جاهز"));
}

// ============================================
// الحفظ
// ============================================
void UNAR_SaveSystem::SaveGame(int32 SaveSlotIndex, FString SaveName)
{
    CurrentGameData.SaveSlotIndex = SaveSlotIndex;
    CurrentGameData.SaveName = SaveName;
    CurrentGameData.SaveDateTime = FDateTime::Now();

    SaveGameToSlot(CurrentGameData);
}

void UNAR_SaveSystem::QuickSave()
{
    SaveGame(0, TEXT("QuickSave"));
    UE_LOG(LogTemp, Warning, TEXT("[NAR_Save] تم الحفظ السريع"));
}

void UNAR_SaveSystem::AutoSave()
{
    CurrentAutoSaveSlot = (CurrentAutoSaveSlot + 1) % MaxSaveSlots;

    if (CurrentAutoSaveSlot == 0)
    {
        CurrentAutoSaveSlot = MaxSaveSlots - 1;
    }

    SaveGame(CurrentAutoSaveSlot, TEXT("AutoSave"));
    UE_LOG(LogTemp, Log, TEXT("[NAR_Save] حفظ تلقائي في الفتحة %d"), CurrentAutoSaveSlot);
}

bool UNAR_SaveSystem::SaveGameToSlot(const FGameSaveData& SaveData)
{
    FString FileName = GetSaveSlotFileName(SaveData.SaveSlotIndex);

    // تحويل البيانات إلى JSON
    FString JsonString;

    // حفظ البيانات
    if (FFileHelper::SaveStringToFile(JsonString, *FileName))
    {
        LastSaveData = SaveData;
        OnGameSaved.Broadcast(SaveData.SaveSlotIndex);

        UE_LOG(LogTemp, Log, TEXT("[NAR_Save] تم الحفظ في الفتحة %d: %s"),
            SaveData.SaveSlotIndex, *FileName);

        return true;
    }

    UE_LOG(LogTemp, Error, TEXT("[NAR_Save] فشل الحفظ في الفتحة %d"), SaveData.SaveSlotIndex);
    return false;
}

// ============================================
// التحميل
// ============================================
bool UNAR_SaveSystem::LoadGame(int32 SaveSlotIndex)
{
    FGameSaveData LoadedData;

    if (LoadGameFromSlot(SaveSlotIndex, LoadedData))
    {
        CurrentGameData = LoadedData;
        OnGameLoaded.Broadcast(SaveSlotIndex);

        UE_LOG(LogTemp, Warning, TEXT("[NAR_Save] تم تحميل اللعبة من الفتحة %d"), SaveSlotIndex);
        return true;
    }

    UE_LOG(LogTemp, Error, TEXT("[NAR_Save] فشل التحميل من الفتحة %d"), SaveSlotIndex);
    return false;
}

bool UNAR_SaveSystem::LoadGameFromSlot(int32 SaveSlotIndex, FGameSaveData& OutSaveData)
{
    FString FileName = GetSaveSlotFileName(SaveSlotIndex);

    if (!FPlatformFileManager::Get().GetPlatformFile().FileExists(*FileName))
    {
        UE_LOG(LogTemp, Warning, TEXT("[NAR_Save] ملف الحفظ غير موجود: %s"), *FileName);
        return false;
    }

    FString JsonString;

    if (FFileHelper::LoadFileToString(JsonString, *FileName))
    {
        // تحميل البيانات من JSON
        OutSaveData.SaveSlotIndex = SaveSlotIndex;

        return true;
    }

    return false;
}

// ============================================
// إدارة فتحات الحفظ
// ============================================
void UNAR_SaveSystem::DeleteSaveSlot(int32 SaveSlotIndex)
{
    FString FileName = GetSaveSlotFileName(SaveSlotIndex);

    if (FPlatformFileManager::Get().GetPlatformFile().DeleteFile(*FileName))
    {
        OnSaveDeleted.Broadcast(SaveSlotIndex);
        UE_LOG(LogTemp, Log, TEXT("[NAR_Save] تم حذف الحفظ من الفتحة %d"), SaveSlotIndex);
    }
}

bool UNAR_SaveSystem::DoesSaveSlotExist(int32 SaveSlotIndex) const
{
    FString FileName = GetSaveSlotFileName(SaveSlotIndex);
    return FPlatformFileManager::Get().GetPlatformFile().FileExists(*FileName);
}

void UNAR_SaveSystem::GetAllSaveSlots(TArray<FGameSaveData>& OutSaveDataArray)
{
    OutSaveDataArray.Empty();

    for (int32 i = 0; i < MaxSaveSlots; ++i)
    {
        if (DoesSaveSlotExist(i))
        {
            FGameSaveData SaveData;

            if (LoadGameFromSlot(i, SaveData))
            {
                OutSaveDataArray.Add(SaveData);
            }
        }
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_Save] عدد الحفوظات المتاحة: %d"), OutSaveDataArray.Num());
}

void UNAR_SaveSystem::ClearAllSaves()
{
    for (int32 i = 0; i < MaxSaveSlots; ++i)
    {
        if (DoesSaveSlotExist(i))
        {
            DeleteSaveSlot(i);
        }
    }

    UE_LOG(LogTemp, Warning, TEXT("[NAR_Save] تم حذف جميع الحفوظات"));
}

// ============================================
// إدارة البيانات
// ============================================
void UNAR_SaveSystem::UpdatePlayerData(int32 Health, int32 Energy, int32 Level, int32 XP)
{
    CurrentGameData.PlayerHealth = Health;
    CurrentGameData.PlayerEnergy = Energy;
    CurrentGameData.PlayerLevel = Level;
    CurrentGameData.PlayerXP = XP;
}

void UNAR_SaveSystem::UpdatePlayerLocation(FVector NewLocation, FRotator NewRotation)
{
    CurrentGameData.PlayerLocation = NewLocation;
    CurrentGameData.PlayerRotation = NewRotation;
}

void UNAR_SaveSystem::AddShards(int32 Amount)
{
    CurrentGameData.ShardCount += Amount;
    UE_LOG(LogTemp, Log, TEXT("[NAR_Save] تمت إضافة %d شظية (المجموع: %d)"),
        Amount, CurrentGameData.ShardCount);
}

void UNAR_SaveSystem::AddEnemyDefeated()
{
    CurrentGameData.EnemiesDefeated++;
}

void UNAR_SaveSystem::AddQuestCompleted(int32 QuestID)
{
    if (!CurrentGameData.CompletedQuestIDs.Contains(QuestID))
    {
        CurrentGameData.CompletedQuestIDs.Add(QuestID);
        CurrentGameData.QuestsCompleted++;
    }
}

void UNAR_SaveSystem::UnlockAchievement(int32 AchievementID)
{
    if (!CurrentGameData.UnlockedAchievementIDs.Contains(AchievementID))
    {
        CurrentGameData.UnlockedAchievementIDs.Add(AchievementID);
    }
}

void UNAR_SaveSystem::AddInventoryItem(FString ItemName, int32 Quantity)
{
    if (CurrentGameData.InventoryItems.Contains(ItemName))
    {
        CurrentGameData.InventoryItems[ItemName] += Quantity;
    }
    else
    {
        CurrentGameData.InventoryItems.Add(ItemName, Quantity);
    }
}

// ============================================
// وظائف داخلية
// ============================================
FString UNAR_SaveSystem::GetSaveSlotFileName(int32 SlotIndex) const
{
    FString SaveDir = FPaths::ProjectSavedDir();
    FString SlotFileName = FString::Printf(TEXT("save_slot_%d.sav"), SlotIndex);

    return FPaths::Combine(SaveDir, SaveGamePath, SlotFileName);
}

void UNAR_SaveSystem::TickAutoSave(float DeltaTime)
{
    AutoSaveTimer += DeltaTime;

    if (AutoSaveTimer >= AutoSaveInterval)
    {
        AutoSave();
        AutoSaveTimer = 0.0f;
    }
}
