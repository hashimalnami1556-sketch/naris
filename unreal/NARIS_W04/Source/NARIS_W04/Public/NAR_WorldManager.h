// NAR_WorldManager.h — مدير العالم الكامل
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NAR_WorldManager.generated.h"

// ============================================
// الأنظمة الرئيسية
// ============================================
class UNAR_WeatherSystem;
class UNAR_AudioSystem;
class UNAR_SaveSystem;
class UNAR_InteractionSystem;
class UNAR_HUDSystem;
class UNAR_EnemyAI;
class UNAR_CombatSystem;
class UNAR_QuestSystem;

// ============================================
// حالة العالم
// ============================================
USTRUCT(BlueprintType)
struct FWorldState
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "World")
    FString CurrentRealm = TEXT("رماد البوابة");

    UPROPERTY(BlueprintReadWrite, Category = "World")
    float TimeOfDay = 12.0f;

    UPROPERTY(BlueprintReadWrite, Category = "World")
    int32 EnemiesDefeated = 0;

    UPROPERTY(BlueprintReadWrite, Category = "World")
    int32 ActiveEnemies = 0;

    UPROPERTY(BlueprintReadWrite, Category = "World")
    bool bGamePaused = false;

    UPROPERTY(BlueprintReadWrite, Category = "World")
    bool bNightTime = false;

    UPROPERTY(BlueprintReadWrite, Category = "World")
    float DifficultyMultiplier = 1.0f;
};

/**
 * ANAR_WorldManager — مدير العالم
 * يدير: جميع الأنظمة الأساسية + حالة العالم + التبديل بين البيئات
 */
UCLASS()
class NARISREALMS_API ANAR_WorldManager : public AActor
{
    GENERATED_BODY()

public:
    ANAR_WorldManager();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    // ============================================
    // التهيئة
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|World")
    void InitializeWorld();

    UFUNCTION(BlueprintCallable, Category = "NAR|World")
    void InitializeAllSystems();

    // ============================================
    // إدارة الأنظمة
    // ============================================
    UFUNCTION(BlueprintPure, Category = "NAR|World|Systems")
    UNAR_WeatherSystem* GetWeatherSystem() const { return WeatherSystem; }

    UFUNCTION(BlueprintPure, Category = "NAR|World|Systems")
    UNAR_AudioSystem* GetAudioSystem() const { return AudioSystem; }

    UFUNCTION(BlueprintPure, Category = "NAR|World|Systems")
    UNAR_SaveSystem* GetSaveSystem() const { return SaveSystem; }

    UFUNCTION(BlueprintPure, Category = "NAR|World|Systems")
    UNAR_InteractionSystem* GetInteractionSystem() const { return InteractionSystem; }

    UFUNCTION(BlueprintPure, Category = "NAR|World|Systems")
    UNAR_HUDSystem* GetHUDSystem() const;

    // ============================================
    // إدارة الحالة
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|World|State")
    void PauseGame();

    UFUNCTION(BlueprintCallable, Category = "NAR|World|State")
    void ResumeGame();

    UFUNCTION(BlueprintCallable, Category = "NAR|World|State")
    void TogglePause();

    UFUNCTION(BlueprintPure, Category = "NAR|World|State")
    bool IsGamePaused() const { return WorldState.bGamePaused; }

    UFUNCTION(BlueprintCallable, Category = "NAR|World|State")
    void SetDifficulty(float Multiplier);

    UFUNCTION(BlueprintPure, Category = "NAR|World|State")
    float GetDifficultyMultiplier() const { return WorldState.DifficultyMultiplier; }

    UFUNCTION(BlueprintPure, Category = "NAR|World|State")
    FWorldState GetWorldState() const { return WorldState; }

    // ============================================
    // إدارة البيئات
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|World|Realm")
    void SwitchRealm(const FString& RealmName);

    UFUNCTION(BlueprintCallable, Category = "NAR|World|Realm")
    void LoadRealm(const FString& LevelName);

    UFUNCTION(BlueprintCallable, Category = "NAR|World|Realm")
    void UnloadRealm(const FString& RealmName);

    UFUNCTION(BlueprintPure, Category = "NAR|World|Realm")
    FString GetCurrentRealm() const { return WorldState.CurrentRealm; }

    UFUNCTION(BlueprintPure, Category = "NAR|World|Realm")
    TArray<FString> GetAvailableRealms() const { return AvailableRealms; }

    // ============================================
    // إدارة الأعداء
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|World|Enemies")
    void RegisterEnemy(AActor* EnemyActor);

    UFUNCTION(BlueprintCallable, Category = "NAR|World|Enemies")
    void UnregisterEnemy(AActor* EnemyActor);

    UFUNCTION(BlueprintCallable, Category = "NAR|World|Enemies")
    void OnEnemyDefeated(AActor* DefeatedEnemy);

    UFUNCTION(BlueprintPure, Category = "NAR|World|Enemies")
    int32 GetActiveEnemyCount() const { return WorldState.ActiveEnemies; }

    UFUNCTION(BlueprintPure, Category = "NAR|World|Enemies")
    int32 GetTotalEnemiesDefeated() const { return WorldState.EnemiesDefeated; }

    // ============================================
    // التأثيرات البيئية
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|World|Environmental")
    void TriggerFlood(float Duration = 90.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|World|Environmental")
    void TriggerSandstorm(float Duration = 45.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|World|Environmental")
    void TriggerLightning(FVector Location);

    UFUNCTION(BlueprintCallable, Category = "NAR|World|Environmental")
    void UpdateEnvironmentalEffects();

    // ============================================
    // إعادة التعيين
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|World|Reset")
    void ResetWorld();

    UFUNCTION(BlueprintCallable, Category = "NAR|World|Reset")
    void ResetAllEnemies();

    UFUNCTION(BlueprintCallable, Category = "NAR|World|Reset")
    void ResetAllInteractables();

    // ============================================
    // أحداث
    // ============================================
    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnGamePaused);
    UPROPERTY(BlueprintAssignable, Category = "NAR|World|Events")
    FOnGamePaused OnGamePaused;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnGameResumed);
    UPROPERTY(BlueprintAssignable, Category = "NAR|World|Events")
    FOnGameResumed OnGameResumed;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnRealmChanged, FString, NewRealm);
    UPROPERTY(BlueprintAssignable, Category = "NAR|World|Events")
    FOnRealmChanged OnRealmChanged;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnEnemyDefeated, AActor*, Enemy, int32, TotalDefeated);
    UPROPERTY(BlueprintAssignable, Category = "NAR|World|Events")
    FOnEnemyDefeated OnEnemyDefeated;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnEnvironmentalTrigger);
    UPROPERTY(BlueprintAssignable, Category = "NAR|World|Events")
    FOnEnvironmentalTrigger OnEnvironmentalTrigger;

protected:
    // ============================================
    // الأنظمة الأساسية
    // ============================================
    UPROPERTY(BlueprintReadOnly, Category = "NAR|World|Systems")
    UNAR_WeatherSystem* WeatherSystem = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|World|Systems")
    UNAR_AudioSystem* AudioSystem = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|World|Systems")
    UNAR_SaveSystem* SaveSystem = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|World|Systems")
    UNAR_InteractionSystem* InteractionSystem = nullptr;

    // ============================================
    // حالة العالم
    // ============================================
    UPROPERTY(BlueprintReadOnly, Category = "NAR|World|State")
    FWorldState WorldState;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|World|State")
    TSet<AActor*> RegisteredEnemies;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|World|State")
    TArray<FString> AvailableRealms = {
        TEXT("رماد البوابة"),
        TEXT("مستنقع الجرس"),
        TEXT("قلعة الغسق")
    };

    // ============================================
    // الإعدادات
    // ============================================
    UPROPERTY(EditDefaultsOnly, Category = "NAR|World|Settings")
    float TimeScale = 1.0f;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|World|Settings")
    bool bAutoLoadFirstRealm = true;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|World|Settings")
    FString DefaultRealm = TEXT("رماد البوابة");

private:
    void UpdateGameState(float DeltaTime);
    void CheckNightTime();
    void CleanupDeadEnemies();
};
