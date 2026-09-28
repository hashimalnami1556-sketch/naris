#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "NarisNarrativeTypes.h"
#include "NarisSaveGame.generated.h"
UCLASS()
class NARISCORE_API UNarisSaveGame : public USaveGame
{
 GENERATED_BODY()
public:
 UPROPERTY(SaveGame) int32 SchemaVersion=6;
 UPROPERTY(SaveGame) FString BuildID;
 UPROPERTY(SaveGame) FTransform PlayerTransform;
 UPROPERTY(SaveGame) float Health=100.f;
 UPROPERTY(SaveGame) float Energy=100.f;
 UPROPERTY(SaveGame) TMap<FName,int32> Inventory;
 UPROPERTY(SaveGame) TMap<FName,FNarisQuestRuntimeState> QuestRuntime;
 UPROPERTY(SaveGame) TMap<FName,int32> Reputation;
 UPROPERTY(SaveGame) TMap<FName,bool> WorldFlags;
 UPROPERTY(SaveGame) uint8 CurrentChapter=1;
 UPROPERTY(SaveGame) TArray<uint8> UnlockedChapters;
 UPROPERTY(SaveGame) TArray<uint8> CompletedChapters;
};