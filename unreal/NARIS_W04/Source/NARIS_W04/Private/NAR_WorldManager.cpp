// NAR_WorldManager.cpp — تنفيذ مدير العالم
#include "NAR_WorldManager.h"
#include "NAR_WeatherSystem.h"
#include "NAR_AudioSystem.h"
#include "NAR_SaveSystem.h"
#include "NAR_InteractionSystem.h"
#include "NAR_HUDSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Misc/CoreDelegates.h"

ANAR_WorldManager::ANAR_WorldManager()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 0.1f;
}

void ANAR_WorldManager::BeginPlay()
{
    Super::BeginPlay();
    InitializeWorld();
}

void ANAR_WorldManager::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    UpdateGameState(DeltaTime);
    CleanupDeadEnemies();
    CheckNightTime();
}

void ANAR_WorldManager::InitializeWorld()
{
    WorldState = FWorldState();
    WorldState.CurrentRealm = DefaultRealm;

    InitializeAllSystems();

    if (bAutoLoadFirstRealm)
    {
        LoadRealm(DefaultRealm);
    }

    UE_LOG(LogTemp, Warning, TEXT("[NAR_World] تم تهيئة العالم: %s"), *DefaultRealm);
}

void ANAR_WorldManager::InitializeAllSystems()
{
    // إنشاء أو البحث عن الأنظمة الأساسية
    for (TActorIterator<AActor> ActorItr(GetWorld()); ActorItr; ++ActorItr)
    {
        if (ActorItr->FindComponentByClass<UNAR_WeatherSystem>())
        {
            WeatherSystem = ActorItr->FindComponentByClass<UNAR_WeatherSystem>();
        }
        if (ActorItr->FindComponentByClass<UNAR_AudioSystem>())
        {
            AudioSystem = ActorItr->FindComponentByClass<UNAR_AudioSystem>();
        }
        if (ActorItr->FindComponentByClass<UNAR_SaveSystem>())
        {
            SaveSystem = ActorItr->FindComponentByClass<UNAR_SaveSystem>();
        }
        if (ActorItr->FindComponentByClass<UNAR_InteractionSystem>())
        {
            InteractionSystem = ActorItr->FindComponentByClass<UNAR_InteractionSystem>();
        }
    }

    if (!WeatherSystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("[NAR_World] لم يتم العثور على نظام الطقس"));
    }
    if (!AudioSystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("[NAR_World] لم يتم العثور على نظام الصوت"));
    }
    if (!SaveSystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("[NAR_World] لم يتم العثور على نظام الحفظ"));
    }
    if (!InteractionSystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("[NAR_World] لم يتم العثور على نظام التفاعلات"));
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_World] جميع الأنظمة الأساسية جاهزة"));
}

// ============================================
// إدارة الحالة
// ============================================
void ANAR_WorldManager::PauseGame()
{
    WorldState.bGamePaused = true;
    UGameplayStatics::SetGamePaused(GetWorld(), true);
    OnGamePaused.Broadcast();

    UE_LOG(LogTemp, Warning, TEXT("[NAR_World] تم إيقاف اللعبة"));
}

void ANAR_WorldManager::ResumeGame()
{
    WorldState.bGamePaused = false;
    UGameplayStatics::SetGamePaused(GetWorld(), false);
    OnGameResumed.Broadcast();

    UE_LOG(LogTemp, Log, TEXT("[NAR_World] تم استئناف اللعبة"));
}

void ANAR_WorldManager::TogglePause()
{
    if (WorldState.bGamePaused)
    {
        ResumeGame();
    }
    else
    {
        PauseGame();
    }
}

void ANAR_WorldManager::SetDifficulty(float Multiplier)
{
    WorldState.DifficultyMultiplier = FMath::Clamp(Multiplier, 0.5f, 2.0f);
    UE_LOG(LogTemp, Warning, TEXT("[NAR_World] تعديل الصعوبة: %.2fx"),
        WorldState.DifficultyMultiplier);
}

// ============================================
// إدارة البيئات
// ============================================
void ANAR_WorldManager::SwitchRealm(const FString& RealmName)
{
    if (!AvailableRealms.Contains(RealmName))
    {
        UE_LOG(LogTemp, Error, TEXT("[NAR_World] البيئة غير موجودة: %s"), *RealmName);
        return;
    }

    WorldState.CurrentRealm = RealmName;
    LoadRealm(RealmName);
    OnRealmChanged.Broadcast(RealmName);

    UE_LOG(LogTemp, Warning, TEXT("[NAR_World] تبديل البيئة إلى: %s"), *RealmName);
}

void ANAR_WorldManager::LoadRealm(const FString& LevelName)
{
    // سيتم تحميل المستوى هنا
    UE_LOG(LogTemp, Log, TEXT("[NAR_World] تحميل البيئة: %s"), *LevelName);
}

void ANAR_WorldManager::UnloadRealm(const FString& RealmName)
{
    UE_LOG(LogTemp, Log, TEXT("[NAR_World] تفريغ البيئة: %s"), *RealmName);
}

// ============================================
// إدارة الأعداء
// ============================================
void ANAR_WorldManager::RegisterEnemy(AActor* EnemyActor)
{
    if (!EnemyActor) return;

    RegisteredEnemies.Add(EnemyActor);
    WorldState.ActiveEnemies = RegisteredEnemies.Num();

    UE_LOG(LogTemp, Log, TEXT("[NAR_World] تسجيل عدو: %s (المجموع: %d)"),
        *EnemyActor->GetName(), WorldState.ActiveEnemies);
}

void ANAR_WorldManager::UnregisterEnemy(AActor* EnemyActor)
{
    if (!EnemyActor) return;

    RegisteredEnemies.Remove(EnemyActor);
    WorldState.ActiveEnemies = RegisteredEnemies.Num();

    UE_LOG(LogTemp, Log, TEXT("[NAR_World] إلغاء تسجيل عدو: %s (المتبقي: %d)"),
        *EnemyActor->GetName(), WorldState.ActiveEnemies);
}

void ANAR_WorldManager::OnEnemyDefeated(AActor* DefeatedEnemy)
{
    if (!DefeatedEnemy) return;

    WorldState.EnemiesDefeated++;
    UnregisterEnemy(DefeatedEnemy);
    OnEnemyDefeated.Broadcast(DefeatedEnemy, WorldState.EnemiesDefeated);

    UE_LOG(LogTemp, Warning, TEXT("[NAR_World] هزيمة عدو! (المجموع: %d)"),
        WorldState.EnemiesDefeated);
}

// ============================================
// التأثيرات البيئية
// ============================================
void ANAR_WorldManager::TriggerFlood(float Duration)
{
    if (WeatherSystem)
    {
        WeatherSystem->StartFlood(300.0f, Duration);
    }

    OnEnvironmentalTrigger.Broadcast();
    UE_LOG(LogTemp, Warning, TEXT("[NAR_World] تفعيل الفيضان!"));
}

void ANAR_WorldManager::TriggerSandstorm(float Duration)
{
    if (WeatherSystem)
    {
        WeatherSystem->StartSandstorm(0.8f, Duration);
    }

    OnEnvironmentalTrigger.Broadcast();
    UE_LOG(LogTemp, Warning, TEXT("[NAR_World] تفعيل عاصفة رملية!"));
}

void ANAR_WorldManager::TriggerLightning(FVector Location)
{
    OnEnvironmentalTrigger.Broadcast();
    UE_LOG(LogTemp, Warning, TEXT("[NAR_World] برق في الموقع: (%.0f, %.0f, %.0f)"),
        Location.X, Location.Y, Location.Z);
}

void ANAR_WorldManager::UpdateEnvironmentalEffects()
{
    if (WeatherSystem)
    {
        // تحديث تأثيرات الطقس
    }
}

// ============================================
// إعادة التعيين
// ============================================
void ANAR_WorldManager::ResetWorld()
{
    ResetAllEnemies();
    ResetAllInteractables();

    WorldState.EnemiesDefeated = 0;
    WorldState.TimeOfDay = 12.0f;

    UE_LOG(LogTemp, Warning, TEXT("[NAR_World] تم إعادة تعيين العالم"));
}

void ANAR_WorldManager::ResetAllEnemies()
{
    RegisteredEnemies.Empty();
    WorldState.ActiveEnemies = 0;
    WorldState.EnemiesDefeated = 0;

    UE_LOG(LogTemp, Log, TEXT("[NAR_World] تم إعادة تعيين جميع الأعداء"));
}

void ANAR_WorldManager::ResetAllInteractables()
{
    if (InteractionSystem)
    {
        // سيتم إعادة تعيين التفاعلات هنا
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_World] تم إعادة تعيين جميع التفاعلات"));
}

// ============================================
// وظائف داخلية
// ============================================
UNAR_HUDSystem* ANAR_WorldManager::GetHUDSystem() const
{
    return Cast<UNAR_HUDSystem>(UGameplayStatics::GetPlayerController(GetWorld(), 0)->MyHUD);
}

void ANAR_WorldManager::UpdateGameState(float DeltaTime)
{
    // تحديث الحالة العامة
    if (WeatherSystem)
    {
        WorldState.TimeOfDay = WeatherSystem->GetTimeOfDay();
    }

    UpdateEnvironmentalEffects();
}

void ANAR_WorldManager::CheckNightTime()
{
    ETimePhase CurrentPhase = ETimePhase::Day;

    if (WeatherSystem)
    {
        CurrentPhase = WeatherSystem->GetCurrentTimePhase();
    }

    bool bWasNight = WorldState.bNightTime;
    WorldState.bNightTime = (CurrentPhase == ETimePhase::Night);

    if (bWasNight != WorldState.bNightTime && WorldState.bNightTime)
    {
        UE_LOG(LogTemp, Warning, TEXT("[NAR_World] حلول الليل"));
    }
}

void ANAR_WorldManager::CleanupDeadEnemies()
{
    // إزالة الأعداء الميتين من القائمة
    for (auto It = RegisteredEnemies.CreateIterator(); It; ++It)
    {
        if (!(*It) || (*It)->IsHidden())
        {
            It.RemoveCurrent();
        }
    }

    WorldState.ActiveEnemies = RegisteredEnemies.Num();
}
