// NAR_HUDSystem.cpp — تنفيذ نظام واجهة المستخدم
#include "NAR_HUDSystem.h"
#include "Blueprint/UserWidget.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UNAR_HUDSystem::UNAR_HUDSystem()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 0.1f;
}

void UNAR_HUDSystem::BeginPlay()
{
    Super::BeginPlay();
    Initialize();
}

void UNAR_HUDSystem::DrawHUD()
{
    Super::DrawHUD();

    if (bMainHUDVisible)
    {
        DrawDebugHUD();
    }
}

void UNAR_HUDSystem::Initialize()
{
    PlayerData = FPlayerHUDData();
    PlayerData.CharacterName = TEXT("آش");
    PlayerData.CurrentRealm = TEXT("رماد البوابة");

    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] نظام واجهة المستخدم جاهز"));
}

// ============================================
// إدارة الواجهة الرئيسية
// ============================================
void UNAR_HUDSystem::ShowMainHUD()
{
    bMainHUDVisible = true;

    if (MainHUDWidget)
    {
        MainHUDWidget->SetVisibility(ESlateVisibility::Visible);
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إظهار الواجهة الرئيسية"));
}

void UNAR_HUDSystem::HideMainHUD()
{
    bMainHUDVisible = false;

    if (MainHUDWidget)
    {
        MainHUDWidget->SetVisibility(ESlateVisibility::Hidden);
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إخفاء الواجهة الرئيسية"));
}

void UNAR_HUDSystem::ToggleMainHUD()
{
    if (bMainHUDVisible)
    {
        HideMainHUD();
    }
    else
    {
        ShowMainHUD();
    }
}

// ============================================
// تحديث البيانات
// ============================================
void UNAR_HUDSystem::UpdatePlayerHealth(int32 CurrentHealth, int32 MaxHealth)
{
    PlayerData.HealthEnergy.CurrentHealth = CurrentHealth;
    PlayerData.HealthEnergy.MaxHealth = MaxHealth;
    PlayerData.HealthEnergy.HealthPercentage = MaxHealth > 0 ? (float)CurrentHealth / MaxHealth : 0.0f;

    OnHUDUpdated.Broadcast();
}

void UNAR_HUDSystem::UpdatePlayerEnergy(int32 CurrentEnergy, int32 MaxEnergy)
{
    PlayerData.HealthEnergy.CurrentEnergy = CurrentEnergy;
    PlayerData.HealthEnergy.MaxEnergy = MaxEnergy;
    PlayerData.HealthEnergy.EnergyPercentage = MaxEnergy > 0 ? (float)CurrentEnergy / MaxEnergy : 0.0f;

    OnHUDUpdated.Broadcast();
}

void UNAR_HUDSystem::UpdatePlayerLevel(int32 Level, int32 XP)
{
    PlayerData.Level = Level;
    PlayerData.XP = XP;

    OnHUDUpdated.Broadcast();
}

void UNAR_HUDSystem::UpdateShardCount(int32 Shards)
{
    PlayerData.ShardCount = Shards;
    OnHUDUpdated.Broadcast();
}

void UNAR_HUDSystem::UpdateRealm(const FString& RealmName)
{
    PlayerData.CurrentRealm = RealmName;
    OnHUDUpdated.Broadcast();
}

void UNAR_HUDSystem::UpdateTimeOfDay(float Time)
{
    PlayerData.TimeOfDay = Time;
    OnHUDUpdated.Broadcast();
}

void UNAR_HUDSystem::UpdateAllPlayerData(const FPlayerHUDData& NewPlayerData)
{
    PlayerData = NewPlayerData;
    OnHUDUpdated.Broadcast();
}

// ============================================
// الرسائل والإشعارات
// ============================================
void UNAR_HUDSystem::ShowNotification(const FString& Message, float Duration)
{
    OnNotificationShown.Broadcast(Message);
    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إشعار: %s"), *Message);
}

void UNAR_HUDSystem::ShowWarning(const FString& Message, float Duration)
{
    OnNotificationShown.Broadcast(Message);
    UE_LOG(LogTemp, Warning, TEXT("[NAR_HUD] تحذير: %s"), *Message);
}

void UNAR_HUDSystem::ShowError(const FString& Message, float Duration)
{
    OnNotificationShown.Broadcast(Message);
    UE_LOG(LogTemp, Error, TEXT("[NAR_HUD] خطأ: %s"), *Message);
}

void UNAR_HUDSystem::ShowDamageNumber(int32 Damage, FVector WorldLocation, bool bIsCritical)
{
    if (bIsCritical)
    {
        UE_LOG(LogTemp, Warning, TEXT("[NAR_HUD] ضرر حرج: %d في الموقع (%.0f, %.0f, %.0f)"),
            Damage, WorldLocation.X, WorldLocation.Y, WorldLocation.Z);
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] ضرر: %d في الموقع (%.0f, %.0f, %.0f)"),
            Damage, WorldLocation.X, WorldLocation.Y, WorldLocation.Z);
    }
}

void UNAR_HUDSystem::ShowHealNumber(int32 Heal, FVector WorldLocation)
{
    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] شفاء: %d في الموقع (%.0f, %.0f, %.0f)"),
        Heal, WorldLocation.X, WorldLocation.Y, WorldLocation.Z);
}

// ============================================
// القوائم
// ============================================
void UNAR_HUDSystem::ShowPauseMenu()
{
    bPauseMenuOpen = true;

    if (PauseMenuWidget)
    {
        PauseMenuWidget->SetVisibility(ESlateVisibility::Visible);
    }

    OnPauseMenuToggled.Broadcast();
    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إظهار قائمة الإيقاف"));
}

void UNAR_HUDSystem::HidePauseMenu()
{
    bPauseMenuOpen = false;

    if (PauseMenuWidget)
    {
        PauseMenuWidget->SetVisibility(ESlateVisibility::Hidden);
    }

    OnPauseMenuToggled.Broadcast();
    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إخفاء قائمة الإيقاف"));
}

void UNAR_HUDSystem::ShowInventoryMenu()
{
    bInventoryOpen = true;

    if (InventoryWidget)
    {
        InventoryWidget->SetVisibility(ESlateVisibility::Visible);
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إظهار قائمة الجرد"));
}

void UNAR_HUDSystem::HideInventoryMenu()
{
    bInventoryOpen = false;

    if (InventoryWidget)
    {
        InventoryWidget->SetVisibility(ESlateVisibility::Hidden);
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إخفاء قائمة الجرد"));
}

void UNAR_HUDSystem::ShowMapMenu()
{
    bMapOpen = true;

    if (MapWidget)
    {
        MapWidget->SetVisibility(ESlateVisibility::Visible);
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إظهار قائمة الخريطة"));
}

void UNAR_HUDSystem::HideMapMenu()
{
    bMapOpen = false;

    if (MapWidget)
    {
        MapWidget->SetVisibility(ESlateVisibility::Hidden);
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إخفاء قائمة الخريطة"));
}

void UNAR_HUDSystem::ShowQuestMenu()
{
    bQuestMenuOpen = true;

    if (QuestWidget)
    {
        QuestWidget->SetVisibility(ESlateVisibility::Visible);
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إظهار قائمة المهام"));
}

void UNAR_HUDSystem::HideQuestMenu()
{
    bQuestMenuOpen = false;

    if (QuestWidget)
    {
        QuestWidget->SetVisibility(ESlateVisibility::Hidden);
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إخفاء قائمة المهام"));
}

void UNAR_HUDSystem::ShowSettingsMenu()
{
    bSettingsOpen = true;
    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إظهار قائمة الإعدادات"));
}

void UNAR_HUDSystem::HideSettingsMenu()
{
    bSettingsOpen = false;
    UE_LOG(LogTemp, Log, TEXT("[NAR_HUD] إخفاء قائمة الإعدادات"));
}

// ============================================
// وظائف داخلية
// ============================================
void UNAR_HUDSystem::DrawDebugHUD()
{
    // رسم معلومات التصحيح على الشاشة
    FString DebugText = FString::Printf(
        TEXT("الشخصية: %s | المستوى: %d | الصحة: %d/%d | الطاقة: %d/%d | الشظايا: %d"),
        *PlayerData.CharacterName,
        PlayerData.Level,
        PlayerData.HealthEnergy.CurrentHealth,
        PlayerData.HealthEnergy.MaxHealth,
        PlayerData.HealthEnergy.CurrentEnergy,
        PlayerData.HealthEnergy.MaxEnergy,
        PlayerData.ShardCount
    );

    DrawText(DebugText, FLinearColor::White, 10.0f, 10.0f, nullptr, 1.0f, false);
}
