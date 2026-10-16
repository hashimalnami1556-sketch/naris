// NAR_WeatherSystem.h — نظام الطقس الكامل
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_WeatherSystem.generated.h"

// ============================================
// أنواع الطقس
// ============================================
UENUM(BlueprintType)
enum class EWeatherType : uint8
{
    Clear           UMETA(DisplayName = "صافي"),
    RainLight       UMETA(DisplayName = "مطر خفيف"),
    RainHeavy       UMETA(DisplayName = "مطر غزير"),
    Fog             UMETA(DisplayName = "ضباب"),
    Dust            UMETA(DisplayName = "غبار"),
    Snow            UMETA(DisplayName = "ثلج"),
    Sandstorm       UMETA(DisplayName = "عاصفة رملية"),
    Flood           UMETA(DisplayName = "فيضان"),
    WindStrong      UMETA(DisplayName = "رياح قوية"),
    Lightning       UMETA(DisplayName = "برق")
};

// ============================================
// مراحل اليوم
// ============================================
UENUM(BlueprintType)
enum class ETimePhase : uint8
{
    Dawn    UMETA(DisplayName = "الفجر"),
    Day     UMETA(DisplayName = "النهار"),
    Dusk    UMETA(DisplayName = "الغسق"),
    Night   UMETA(DisplayName = "الليل")
};

// ============================================
// حالة الطقس
// ============================================
USTRUCT(BlueprintType)
struct FWeatherState
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Weather")
    EWeatherType CurrentWeather = EWeatherType::Clear;

    UPROPERTY(BlueprintReadWrite, Category = "Weather")
    float RainIntensity = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Weather")
    float WindStrength = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Weather")
    float FogDensity = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Weather")
    float SandstormIntensity = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Weather")
    float SnowIntensity = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Weather")
    float FloodLevel = 0.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Weather")
    float Temperature = 22.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Weather")
    float TimeOfDay = 12.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Weather")
    ETimePhase CurrentPhase = ETimePhase::Day;
};

/**
 * UNAR_WeatherSystem — نظام الطقس
 * يدير: الطقس الديناميكي + دورة الليل/النهار + الفيضانات + العواصف
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_WeatherSystem : public UActorComponent
{
    GENERATED_BODY()

public:
    UNAR_WeatherSystem();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    // ============================================
    // التهيئة
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Weather")
    void Initialize();

    // ============================================
    // إدارة الطقس
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Weather")
    void SetWeather(EWeatherType NewWeather, float Intensity = 0.5f, float Duration = 120.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|Weather")
    void TransitionToWeather(EWeatherType NewWeather, float TransitionDuration = 3.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|Weather")
    void GenerateRandomWeather();

    UFUNCTION(BlueprintPure, Category = "NAR|Weather")
    FWeatherState GetCurrentWeatherState() const { return CurrentState; }

    UFUNCTION(BlueprintPure, Category = "NAR|Weather")
    EWeatherType GetCurrentWeather() const { return CurrentState.CurrentWeather; }

    UFUNCTION(BlueprintPure, Category = "NAR|Weather")
    ETimePhase GetCurrentTimePhase() const { return CurrentState.CurrentPhase; }

    // ============================================
    // إدارة الوقت
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Weather|Time")
    void SetTimeOfDay(float NewTime);

    UFUNCTION(BlueprintCallable, Category = "NAR|Weather|Time")
    void SetTimeScale(float Scale);

    UFUNCTION(BlueprintPure, Category = "NAR|Weather|Time")
    float GetTimeOfDay() const { return CurrentState.TimeOfDay; }

    // ============================================
    // الفيضانات
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Weather|Flood")
    void StartFlood(float MaxLevel = 300.0f, float Duration = 90.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|Weather|Flood")
    void StopFlood();

    UFUNCTION(BlueprintPure, Category = "NAR|Weather|Flood")
    float GetCurrentFloodLevel() const { return CurrentState.FloodLevel; }

    UFUNCTION(BlueprintPure, Category = "NAR|Weather|Flood")
    bool IsFloodActive() const { return bFloodActive; }

    // ============================================
    // العواصف الرملية
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Weather|Sandstorm")
    void StartSandstorm(float Intensity = 0.8f, float Duration = 45.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|Weather|Sandstorm")
    void StopSandstorm();

    UFUNCTION(BlueprintPure, Category = "NAR|Weather|Sandstorm")
    bool IsSandstormActive() const { return bSandstormActive; }

    // ============================================
    // تعديلات على اللعب
    // ============================================
    UFUNCTION(BlueprintPure, Category = "NAR|Weather|Effects")
    float GetVisibilityModifier() const;

    UFUNCTION(BlueprintPure, Category = "NAR|Weather|Effects")
    float GetSpeedModifier() const;

    UFUNCTION(BlueprintPure, Category = "NAR|Weather|Effects")
    float GetDamagePerSecond() const;

    // ============================================
    // أحداث
    // ============================================
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnWeatherChanged, EWeatherType, OldWeather, EWeatherType, NewWeather);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Weather|Events")
    FOnWeatherChanged OnWeatherChanged;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTimePhaseChanged, ETimePhase, OldPhase, ETimePhase, NewPhase);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Weather|Events")
    FOnTimePhaseChanged OnTimePhaseChanged;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnFloodStarted, float, MaxLevel);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Weather|Events")
    FOnFloodStarted OnFloodStarted;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnFloodEnded);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Weather|Events")
    FOnFloodEnded OnFloodEnded;

protected:
    UPROPERTY(BlueprintReadOnly, Category = "NAR|Weather|State")
    FWeatherState CurrentState;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Weather|Settings")
    float DayLengthSeconds = 1440.0f;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Weather|Settings")
    float TimeScale = 1.0f;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Weather|Settings")
    float WeatherChangeInterval = 180.0f;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Weather|Settings")
    bool bAutoWeatherChange = true;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Weather|Settings")
    float FloodRiseSpeed = 10.0f;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Weather|Settings")
    float SandstormDamagePerSecond = 1.0f;

private:
    float WeatherTimer = 0.0f;
    float TransitionTimer = 0.0f;
    float FloodTimer = 0.0f;
    float SandstormTimer = 0.0f;
    float FloodMaxLevel = 0.0f;
    float FloodDuration = 0.0f;
    float SandstormDuration = 0.0f;

    bool bFloodActive = false;
    bool bSandstormActive = false;
    bool bTransitioning = false;

    EWeatherType TransitionFromWeather = EWeatherType::Clear;
    EWeatherType TransitionToWeather = EWeatherType::Clear;
    float TransitionProgress = 0.0f;
    float TransitionDuration = 3.0f;

    void UpdateTimeOfDay(float DeltaSeconds);
    void UpdateWeather(float DeltaSeconds);
    void UpdateFlood(float DeltaSeconds);
    void UpdateSandstorm(float DeltaSeconds);
    ETimePhase GetPhaseForTime(float Time);
    void ApplyWeatherEffects();
};
