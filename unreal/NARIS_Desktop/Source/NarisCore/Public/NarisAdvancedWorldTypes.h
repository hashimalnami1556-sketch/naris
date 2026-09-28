#pragma once
#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "NarisAdvancedWorldTypes.generated.h"

UENUM(BlueprintType)
enum class ENarisWeatherType : uint8 { Clear, AshStorm, Rain, AetherFog, EmberWind, Eclipse };

USTRUCT(BlueprintType)
struct FNarisTerrainProfileRow : public FTableRowBase {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName BiomeID;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float HeightScale=1200.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float NoiseScale=0.002f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float ErosionStrength=0.35f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 SeedOffset=0;
};

USTRUCT(BlueprintType)
struct FNarisFastTravelNodeRow : public FTableRowBase {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName NodeID;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName ZoneID;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector Location=FVector::ZeroVector;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) bool bUnlockedByDefault=false;
};
