#pragma once
#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "NarisCombatTypes.generated.h"

UENUM(BlueprintType)
enum class ENarisGameplayEventType : uint8 { EnableHitbox, DisableHitbox, PlayVFX, PlaySFX, PhaseTransition, HitReact };

USTRUCT(BlueprintType)
struct FNarisAttackRow : public FTableRowBase {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName AttackID;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName MontageSection;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float Damage = 0.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float PoiseDamage = 0.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName HitboxSocket;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float HitboxRadius = 20.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float Impulse = 0.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName DamageType;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName VFX_ID;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FName SFX_ID;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) float EnergyCost = 0.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 RequiredPhase = 0;
};
