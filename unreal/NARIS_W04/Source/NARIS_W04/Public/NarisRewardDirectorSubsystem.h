#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisRewardDirectorSubsystem.generated.h"

UENUM(BlueprintType) enum class ENarisRewardKind:uint8 { Boss,Exploration,Achievement,Loot,Challenge,BattlePass };
UENUM(BlueprintType) enum class ENarisRewardRarity:uint8 { Common,Rare,Epic,Legendary };
USTRUCT(BlueprintType) struct FNarisRewardPresentationEvent {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FString EventId;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) ENarisRewardKind Kind=ENarisRewardKind::Exploration;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FString SourceId;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) ENarisRewardRarity Rarity=ENarisRewardRarity::Common;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FText Title;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FText Description;
};
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisRewardQueued,const FNarisRewardPresentationEvent&,Event);
UCLASS() class NARIS_W04_API UNarisRewardDirectorSubsystem:public UGameInstanceSubsystem {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) bool Enqueue(const FNarisRewardPresentationEvent& Event);
 UFUNCTION(BlueprintCallable) bool Peek(FNarisRewardPresentationEvent& OutEvent) const;
 UFUNCTION(BlueprintCallable) bool Acknowledge(const FString& EventId);
 UFUNCTION(BlueprintPure) int32 PendingCount() const;
 UPROPERTY(BlueprintAssignable) FNarisRewardQueued OnRewardQueued;
private:
 struct FEntry { FNarisRewardPresentationEvent Event; bool bAcked=false; int32 Sequence=0; };
 TArray<FEntry> Entries; int32 NextSequence=0;
 static int32 Priority(const FNarisRewardPresentationEvent& Event);
};