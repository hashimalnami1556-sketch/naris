#include "NarisEnvironmentDirectorComponent.h"
UNarisEnvironmentDirectorComponent::UNarisEnvironmentDirectorComponent(){ PrimaryComponentTick.bCanEverTick=false; }
void UNarisEnvironmentDirectorComponent::SetTimeOfDay(float NewHour){ TimeOfDay=FMath::Fmod(FMath::Max(0.f,NewHour),24.f); }
void UNarisEnvironmentDirectorComponent::SetWeather(ENarisWeatherType NewWeather,float Intensity){ Weather=NewWeather; WeatherIntensity=FMath::Clamp(Intensity,0.f,1.f); OnWeatherChanged.Broadcast(Weather,WeatherIntensity); }
