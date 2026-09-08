// NAR_WeatherSystem.cpp — تنفيذ نظام الطقس
#include "NAR_WeatherSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UNAR_WeatherSystem::UNAR_WeatherSystem()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickInterval = 0.1f;
}

void UNAR_WeatherSystem::BeginPlay()
{
    Super::BeginPlay();
    Initialize();
}

void UNAR_WeatherSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    UpdateTimeOfDay(DeltaTime);
    UpdateWeather(DeltaTime);
    UpdateFlood(DeltaTime);
    UpdateSandstorm(DeltaTime);
}

void UNAR_WeatherSystem::Initialize()
{
    CurrentState = FWeatherState();
    WeatherTimer = WeatherChangeInterval;

    UE_LOG(LogTemp, Log, TEXT("[NAR_Weather] نظام الطقس جاهز"));
}

void UNAR_WeatherSystem::SetWeather(EWeatherType NewWeather, float Intensity, float Duration)
{
    EWeatherType OldWeather = CurrentState.CurrentWeather;
    CurrentState.CurrentWeather = NewWeather;
    WeatherTimer = Duration;

    ApplyWeatherEffects();
    OnWeatherChanged.Broadcast(OldWeather, NewWeather);

    UE_LOG(LogTemp, Warning, TEXT("[NAR_Weather] تغيير الطقس: %d (الكثافة: %.2f)"),
        static_cast<int32>(NewWeather), Intensity);
}

void UNAR_WeatherSystem::TransitionToWeather(EWeatherType NewWeather, float TransitionDuration)
{
    if (bTransitioning) return;

    bTransitioning = true;
    TransitionFromWeather = CurrentState.CurrentWeather;
    TransitionToWeather = NewWeather;
    TransitionProgress = 0.0f;
    TransitionDuration = TransitionDuration;

    UE_LOG(LogTemp, Log, TEXT("[NAR_Weather] انتقال الطقس: %d -> %d"),
        static_cast<int32>(TransitionFromWeather),
        static_cast<int32>(TransitionToWeather));
}

void UNAR_WeatherSystem::GenerateRandomWeather()
{
    TArray<EWeatherType> PossibleWeathers = {
        EWeatherType::Clear,
        EWeatherType::RainLight,
        EWeatherType::RainHeavy,
        EWeatherType::Fog,
        EWeatherType::Dust,
        EWeatherType::WindStrong,
    };

    int32 RandomIndex = FMath::RandRange(0, PossibleWeathers.Num() - 1);
    EWeatherType RandomWeather = PossibleWeathers[RandomIndex];
    float RandomIntensity = FMath::RandRange(0.2f, 1.0f);
    float RandomDuration = FMath::RandRange(60.0f, 300.0f);

    SetWeather(RandomWeather, RandomIntensity, RandomDuration);
}

void UNAR_WeatherSystem::SetTimeOfDay(float NewTime)
{
    CurrentState.TimeOfDay = FMath::Clamp(NewTime, 0.0f, 24.0f);
    CurrentState.CurrentPhase = GetPhaseForTime(CurrentState.TimeOfDay);
}

void UNAR_WeatherSystem::SetTimeScale(float Scale)
{
    TimeScale = FMath::Max(0.0f, Scale);
}

void UNAR_WeatherSystem::StartFlood(float MaxLevel, float Duration)
{
    if (bFloodActive) return;

    bFloodActive = true;
    FloodMaxLevel = MaxLevel;
    FloodDuration = Duration;
    FloodTimer = 0.0f;
    CurrentState.FloodLevel = 0.0f;

    OnFloodStarted.Broadcast(MaxLevel);
    UE_LOG(LogTemp, Warning, TEXT("[NAR_Weather] بدء الفيضان! المستوى الأقصى: %.1f"), MaxLevel);
}

void UNAR_WeatherSystem::StopFlood()
{
    if (!bFloodActive) return;

    bFloodActive = false;
    CurrentState.FloodLevel = 0.0f;

    OnFloodEnded.Broadcast();
    UE_LOG(LogTemp, Log, TEXT("[NAR_Weather] انتهى الفيضان"));
}

void UNAR_WeatherSystem::StartSandstorm(float Intensity, float Duration)
{
    if (bSandstormActive) return;

    bSandstormActive = true;
    SandstormDuration = Duration;
    SandstormTimer = 0.0f;
    CurrentState.SandstormIntensity = Intensity;

    UE_LOG(LogTemp, Warning, TEXT("[NAR_Weather] بدء عاصفة رملية! الكثافة: %.2f"), Intensity);
}

void UNAR_WeatherSystem::StopSandstorm()
{
    if (!bSandstormActive) return;

    bSandstormActive = false;
    CurrentState.SandstormIntensity = 0.0f;

    UE_LOG(LogTemp, Log, TEXT("[NAR_Weather] انتهت العاصفة الرملية"));
}

float UNAR_WeatherSystem::GetVisibilityModifier() const
{
    float Modifier = 1.0f;

    switch (CurrentState.CurrentWeather)
    {
        case EWeatherType::Fog:
            Modifier = 0.5f;
            break;
        case EWeatherType::Sandstorm:
            Modifier = 0.3f;
            break;
        case EWeatherType::RainHeavy:
            Modifier = 0.7f;
            break;
        case EWeatherType::Dust:
            Modifier = 0.85f;
            break;
        case EWeatherType::Snow:
            Modifier = 0.95f;
            break;
        default:
            Modifier = 1.0f;
            break;
    }

    if (CurrentState.CurrentPhase == ETimePhase::Night)
    {
        Modifier *= 0.6f;
    }

    return Modifier;
}

float UNAR_WeatherSystem::GetSpeedModifier() const
{
    float Modifier = 1.0f;

    switch (CurrentState.CurrentWeather)
    {
        case EWeatherType::RainHeavy:
            Modifier = 0.9f;
            break;
        case EWeatherType::Snow:
            Modifier = 0.95f;
            break;
        case EWeatherType::WindStrong:
            Modifier = 0.9f;
            break;
        case EWeatherType::Flood:
            Modifier = 0.7f;
            break;
        default:
            Modifier = 1.0f;
            break;
    }

    return Modifier;
}

float UNAR_WeatherSystem::GetDamagePerSecond() const
{
    if (bSandstormActive)
    {
        return SandstormDamagePerSecond;
    }

    return 0.0f;
}

void UNAR_WeatherSystem::UpdateTimeOfDay(float DeltaSeconds)
{
    CurrentState.TimeOfDay += (DeltaSeconds / DayLengthSeconds) * 24.0f * TimeScale;

    if (CurrentState.TimeOfDay >= 24.0f)
    {
        CurrentState.TimeOfDay -= 24.0f;
    }

    ETimePhase NewPhase = GetPhaseForTime(CurrentState.TimeOfDay);
    if (NewPhase != CurrentState.CurrentPhase)
    {
        ETimePhase OldPhase = CurrentState.CurrentPhase;
        CurrentState.CurrentPhase = NewPhase;
        OnTimePhaseChanged.Broadcast(OldPhase, NewPhase);

        const TCHAR* PhaseNames[] = { TEXT("الفجر"), TEXT("النهار"), TEXT("الغسق"), TEXT("الليل") };
        UE_LOG(LogTemp, Warning, TEXT("[NAR_Weather] مرحلة جديدة: %s"),
            PhaseNames[static_cast<int32>(NewPhase)]);
    }
}

void UNAR_WeatherSystem::UpdateWeather(float DeltaSeconds)
{
    if (bTransitioning)
    {
        TransitionProgress += DeltaSeconds / TransitionDuration;

        if (TransitionProgress >= 1.0f)
        {
            bTransitioning = false;
            SetWeather(TransitionToWeather, 0.5f, 120.0f);
        }
    }

    if (bAutoWeatherChange && !bTransitioning)
    {
        WeatherTimer -= DeltaSeconds;

        if (WeatherTimer <= 0.0f)
        {
            GenerateRandomWeather();
            WeatherTimer = WeatherChangeInterval;
        }
    }
}

void UNAR_WeatherSystem::UpdateFlood(float DeltaSeconds)
{
    if (!bFloodActive) return;

    FloodTimer += DeltaSeconds;

    if (FloodTimer < FloodDuration / 3.0f)
    {
        CurrentState.FloodLevel += FloodRiseSpeed * DeltaSeconds;
        CurrentState.FloodLevel = FMath::Min(CurrentState.FloodLevel, FloodMaxLevel);
    }
    else if (FloodTimer < FloodDuration * 2.0f / 3.0f)
    {
        CurrentState.FloodLevel = FloodMaxLevel;
    }
    else
    {
        CurrentState.FloodLevel -= FloodRiseSpeed * DeltaSeconds;
        CurrentState.FloodLevel = FMath::Max(CurrentState.FloodLevel, 0.0f);
    }

    if (FloodTimer >= FloodDuration)
    {
        StopFlood();
    }
}

void UNAR_WeatherSystem::UpdateSandstorm(float DeltaSeconds)
{
    if (!bSandstormActive) return;

    SandstormTimer += DeltaSeconds;

    if (SandstormTimer >= SandstormDuration)
    {
        StopSandstorm();
    }
}

ETimePhase UNAR_WeatherSystem::GetPhaseForTime(float Time)
{
    if (Time >= 5.0f && Time < 7.0f) return ETimePhase::Dawn;
    if (Time >= 7.0f && Time < 17.0f) return ETimePhase::Day;
    if (Time >= 17.0f && Time < 19.0f) return ETimePhase::Dusk;
    return ETimePhase::Night;
}

void UNAR_WeatherSystem::ApplyWeatherEffects()
{
    switch (CurrentState.CurrentWeather)
    {
        case EWeatherType::RainLight:
            CurrentState.RainIntensity = 0.3f;
            break;
        case EWeatherType::RainHeavy:
            CurrentState.RainIntensity = 0.7f;
            break;
        case EWeatherType::Fog:
            CurrentState.FogDensity = 0.8f;
            break;
        case EWeatherType::Dust:
            CurrentState.FogDensity = 0.2f;
            break;
        case EWeatherType::Snow:
            CurrentState.SnowIntensity = 0.4f;
            break;
        case EWeatherType::Sandstorm:
            CurrentState.SandstormIntensity = 0.9f;
            break;
        case EWeatherType::WindStrong:
            CurrentState.WindStrength = 0.6f;
            break;
        default:
            break;
    }
}
