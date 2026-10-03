// NAR_HUDSystem.h — نظام واجهة المستخدم
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "NAR_HUDSystem.generated.h"

// ============================================
// بيانات الصحة والطاقة
// ============================================
USTRUCT(BlueprintType)
struct FHealthEnergyData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    int32 CurrentHealth = 100;

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    int32 MaxHealth = 100;

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    int32 CurrentEnergy = 100;

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    int32 MaxEnergy = 100;

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    float HealthPercentage = 1.0f;

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    float EnergyPercentage = 1.0f;
};

// ============================================
// بيانات اللاعب
// ============================================
USTRUCT(BlueprintType)
struct FPlayerHUDData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    FString CharacterName = TEXT("");

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    int32 Level = 1;

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    int32 XP = 0;

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    int32 ShardCount = 0;

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    FHealthEnergyData HealthEnergy;

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    FString CurrentRealm = TEXT("رماد البوابة");

    UPROPERTY(BlueprintReadWrite, Category = "HUD")
    float TimeOfDay = 12.0f;
};

/**
 * UNAR_HUDSystem — نظام واجهة المستخدم
 * يدير: شرائط الصحة والطاقة + قائمة القدرات + الخريطة المصغرة + تتبع المهام
 */
UCLASS()
class NARISREALMS_API UNAR_HUDSystem : public AHUD
{
    GENERATED_BODY()

public:
    UNAR_HUDSystem();

    virtual void BeginPlay() override;
    virtual void DrawHUD() override;

    // ============================================
    // التهيئة
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|HUD")
    void Initialize();

    // ============================================
    // إدارة الواجهة الرئيسية
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Main")
    void ShowMainHUD();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Main")
    void HideMainHUD();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Main")
    void ToggleMainHUD();

    UFUNCTION(BlueprintPure, Category = "NAR|HUD|Main")
    bool IsMainHUDVisible() const { return bMainHUDVisible; }

    // ============================================
    // تحديث البيانات
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Update")
    void UpdatePlayerHealth(int32 CurrentHealth, int32 MaxHealth);

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Update")
    void UpdatePlayerEnergy(int32 CurrentEnergy, int32 MaxEnergy);

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Update")
    void UpdatePlayerLevel(int32 Level, int32 XP);

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Update")
    void UpdateShardCount(int32 Shards);

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Update")
    void UpdateRealm(const FString& RealmName);

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Update")
    void UpdateTimeOfDay(float Time);

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Update")
    void UpdateAllPlayerData(const FPlayerHUDData& PlayerData);

    // ============================================
    // الرسائل والإشعارات
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Messages")
    void ShowNotification(const FString& Message, float Duration = 3.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Messages")
    void ShowWarning(const FString& Message, float Duration = 3.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Messages")
    void ShowError(const FString& Message, float Duration = 3.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Messages")
    void ShowDamageNumber(int32 Damage, FVector WorldLocation, bool bIsCritical = false);

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Messages")
    void ShowHealNumber(int32 Heal, FVector WorldLocation);

    // ============================================
    // القوائم
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Menu")
    void ShowPauseMenu();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Menu")
    void HidePauseMenu();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Menu")
    void ShowInventoryMenu();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Menu")
    void HideInventoryMenu();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Menu")
    void ShowMapMenu();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Menu")
    void HideMapMenu();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Menu")
    void ShowQuestMenu();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Menu")
    void HideQuestMenu();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Menu")
    void ShowSettingsMenu();

    UFUNCTION(BlueprintCallable, Category = "NAR|HUD|Menu")
    void HideSettingsMenu();

    // ============================================
    // حالة الواجهة
    // ============================================
    UFUNCTION(BlueprintPure, Category = "NAR|HUD|State")
    bool IsPauseMenuOpen() const { return bPauseMenuOpen; }

    UFUNCTION(BlueprintPure, Category = "NAR|HUD|State")
    bool IsInventoryOpen() const { return bInventoryOpen; }

    UFUNCTION(BlueprintPure, Category = "NAR|HUD|State")
    bool IsMapOpen() const { return bMapOpen; }

    UFUNCTION(BlueprintPure, Category = "NAR|HUD|State")
    FPlayerHUDData GetPlayerHUDData() const { return PlayerData; }

    // ============================================
    // أحداث
    // ============================================
    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnHUDUpdated);
    UPROPERTY(BlueprintAssignable, Category = "NAR|HUD|Events")
    FOnHUDUpdated OnHUDUpdated;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnNotificationShown, FString, Message);
    UPROPERTY(BlueprintAssignable, Category = "NAR|HUD|Events")
    FOnNotificationShown OnNotificationShown;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnPauseMenuToggled);
    UPROPERTY(BlueprintAssignable, Category = "NAR|HUD|Events")
    FOnPauseMenuToggled OnPauseMenuToggled;

protected:
    // ============================================
    // بيانات الواجهة
    // ============================================
    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|Data")
    FPlayerHUDData PlayerData;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|State")
    bool bMainHUDVisible = true;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|State")
    bool bPauseMenuOpen = false;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|State")
    bool bInventoryOpen = false;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|State")
    bool bMapOpen = false;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|State")
    bool bQuestMenuOpen = false;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|State")
    bool bSettingsOpen = false;

    // ============================================
    // مكونات الواجهة
    // ============================================
    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|Widgets")
    class UUserWidget* MainHUDWidget = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|Widgets")
    class UUserWidget* PauseMenuWidget = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|Widgets")
    class UUserWidget* InventoryWidget = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|Widgets")
    class UUserWidget* MapWidget = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|HUD|Widgets")
    class UUserWidget* QuestWidget = nullptr;

    // ============================================
    // أصناف الواجهة
    // ============================================
    UPROPERTY(EditDefaultsOnly, Category = "NAR|HUD|Classes")
    TSubclassOf<class UUserWidget> MainHUDClass = nullptr;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|HUD|Classes")
    TSubclassOf<class UUserWidget> PauseMenuClass = nullptr;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|HUD|Classes")
    TSubclassOf<class UUserWidget> InventoryClass = nullptr;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|HUD|Classes")
    TSubclassOf<class UUserWidget> MapClass = nullptr;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|HUD|Classes")
    TSubclassOf<class UUserWidget> QuestClass = nullptr;

private:
    void DrawDebugHUD();
};
