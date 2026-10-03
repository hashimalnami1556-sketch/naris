#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisWeatherGameplayComponent.generated.h"

class ANarisHeroCharacter;
class UNarisCombatComponent;

UCLASS(ClassGroup=(NARIS), Blueprintable, meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UNarisWeatherGameplayComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UNarisWeatherGameplayComponent();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintPure, Category="NARIS|Weather")
    float GetMoveSpeedMultiplier() const { return MoveSpeedMultiplier; }

    UFUNCTION(BlueprintPure, Category="NARIS|Weather")
    float GetVisibilityMultiplier() const { return VisibilityMultiplier; }

    UFUNCTION(BlueprintCallable, Category="NARIS|Weather")
    void RefreshWeatherProfile();

private:
    FTimerHandle WeatherTimer;
    TWeakObjectPtr<ANarisHeroCharacter> HeroOwner;
    TWeakObjectPtr<UNarisCombatComponent> Combat;

    float MoveSpeedMultiplier = 1.f;
    float VisibilityMultiplier = 1.f;
    float HealthDrainPerSecond = 0.f;
    float UpdateIntervalSeconds = 1.f;
};
