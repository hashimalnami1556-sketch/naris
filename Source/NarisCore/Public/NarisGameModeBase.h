#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "NarisGameModeBase.generated.h"
class UNarisAudioDirectorComponent;
class UNarisVFXDirectorComponent;
class UNarisAttackTokenCoordinator;
class UNarisWorldSimulationComponent;

UCLASS()
class NARISCORE_API ANarisGameModeBase : public AGameModeBase
{
 GENERATED_BODY()
public:
 ANarisGameModeBase();
 UFUNCTION(BlueprintCallable) void StartGame();
 UFUNCTION(BlueprintPure) bool IsGameStarted() const { return bGameStarted; }
 static int32 ParseBenchmarkEnemyCount(const TCHAR* CmdLine);
 static bool ShouldStartDirectly(const TCHAR* CmdLine);
 static bool ShouldSkipAshenGateForWorld(const FString& WorldPackageName);
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisAudioDirectorComponent> AudioDirector;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisVFXDirectorComponent> VFXDirector;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisAttackTokenCoordinator> AttackCoordinator;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UNarisWorldSimulationComponent> WorldSimulation;
protected:
 virtual void BeginPlay() override;
private:
 bool bGameStarted=false;
 void RunQuestSmoke();
 void RunBellMarshSmoke();
};

