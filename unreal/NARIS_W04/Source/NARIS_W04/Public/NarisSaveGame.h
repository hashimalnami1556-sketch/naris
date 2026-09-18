#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "NarisGameplayTypes.h"
#include "NarisSaveGame.generated.h"
UCLASS()
class NARIS_W04_API UNarisSaveGame:public USaveGame{
 GENERATED_BODY()
public:
 UPROPERTY(BlueprintReadWrite) FNarisSaveState State;
};