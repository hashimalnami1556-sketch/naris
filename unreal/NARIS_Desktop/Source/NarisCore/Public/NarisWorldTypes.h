#pragma once
#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "NarisWorldTypes.generated.h"

USTRUCT(BlueprintType)
struct FNarisWorldZoneRow : public FTableRowBase {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName ZoneID;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName BiomeID;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 StreamingPriority = 50;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName CheckpointID;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName EncounterProfile;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName EventProfile;
};

USTRUCT(BlueprintType)
struct FNarisBiomeRow : public FTableRowBase {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName BiomeID;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float Temperature = .5f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float Humidity = .5f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName PCGGraph;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName AmbientVFX;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName AmbientAudio;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName EncounterProfile;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float Density = 1.f;
};
