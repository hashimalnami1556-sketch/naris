#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisAdvancedWorldTypes.h"
#include "NarisEnvironmentDirectorComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNarisWeatherChanged, ENarisWeatherType, Weather, float, Intensity);

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisEnvironmentDirectorComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UNarisEnvironmentDirectorComponent();
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Environment", meta=(ClampMin="0",ClampMax="24")) float TimeOfDay=12.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Environment") ENarisWeatherType Weather=ENarisWeatherType::Clear;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Environment", meta=(ClampMin="0",ClampMax="1")) float WeatherIntensity=0.f;
 UPROPERTY(BlueprintAssignable) FNarisWeatherChanged OnWeatherChanged;
 UFUNCTION(BlueprintCallable) void SetTimeOfDay(float NewHour);
 UFUNCTION(BlueprintCallable) void SetWeather(ENarisWeatherType NewWeather, float Intensity);
};
