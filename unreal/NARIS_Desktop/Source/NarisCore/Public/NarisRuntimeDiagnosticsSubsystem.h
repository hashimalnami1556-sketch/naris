#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisRuntimeDiagnosticsSubsystem.generated.h"
USTRUCT(BlueprintType)
struct FNarisRuntimeHealth
{
 GENERATED_BODY()
 UPROPERTY(BlueprintReadOnly) bool bWorldReady=false;
 UPROPERTY(BlueprintReadOnly) bool bAudioReady=false;
 UPROPERTY(BlueprintReadOnly) bool bVFXReady=false;
 UPROPERTY(BlueprintReadOnly) bool bSaveReady=false;
 UPROPERTY(BlueprintReadOnly) bool bQuestReady=false;
 UPROPERTY(BlueprintReadOnly) bool bAttackCoordinationReady=false;
 UPROPERTY(BlueprintReadOnly) int32 ActiveEnemies=0;
 UPROPERTY(BlueprintReadOnly) int32 ActiveBosses=0;
};
UCLASS()
class NARISCORE_API UNarisRuntimeDiagnosticsSubsystem : public UGameInstanceSubsystem
{
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) FNarisRuntimeHealth Probe(UObject* WorldContext) const;
 UFUNCTION(BlueprintCallable) bool RunReleaseGate(UObject* WorldContext) const;
};