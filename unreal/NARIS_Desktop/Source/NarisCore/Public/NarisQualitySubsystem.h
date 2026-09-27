#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisQualitySubsystem.generated.h"
UCLASS() class NARISCORE_API UNarisQualitySubsystem: public UGameInstanceSubsystem { GENERATED_BODY() public: UFUNCTION(BlueprintCallable) void ApplyRecommendedQuality(); UFUNCTION(BlueprintPure) float GetFrameTimeBudgetMs() const { return 16.67f; } };
