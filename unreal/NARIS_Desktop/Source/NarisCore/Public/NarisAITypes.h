#pragma once
#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "NarisAITypes.generated.h"

UENUM(BlueprintType) enum class ENarisAIState : uint8 { Idle, Patrol, Investigate, Chase, Attack, Evade, Stunned, Enraged, Dead };
UENUM(BlueprintType) enum class ENarisCombatRole : uint8 { Vanguard, Skirmisher, Ranged, Controller, Support, Boss };

USTRUCT(BlueprintType)
struct FNarisAIProfileRow : public FTableRowBase {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere, BlueprintReadWrite) FName ProfileID;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) ENarisCombatRole Role = ENarisCombatRole::Vanguard;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) float SightRadius = 2200.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) float LoseSightRadius = 3000.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) float HearingRange = 1600.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) float PreferredRange = 250.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) float Aggression = .65f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) float RetreatHealthPct = .15f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 MaxAttackersOnTarget = 3;
};
