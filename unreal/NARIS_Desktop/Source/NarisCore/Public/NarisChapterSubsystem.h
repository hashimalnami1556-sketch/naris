#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisChapterSubsystem.generated.h"
UENUM(BlueprintType)
enum class ENarisChapter:uint8{None=0,AshenGate=1,BellMarsh,TwilightKeep,AetherRift,CrownOfDust,FinalEmber};
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNarisChapterChanged,ENarisChapter,Chapter,bool,bCompleted);
UCLASS()
class NARISCORE_API UNarisChapterSubsystem : public UGameInstanceSubsystem
{
 GENERATED_BODY()
public:
 UPROPERTY(BlueprintAssignable) FNarisChapterChanged OnChapterChanged;
 UFUNCTION(BlueprintCallable) void UnlockChapter(ENarisChapter Chapter);
 UFUNCTION(BlueprintCallable) void CompleteChapter(ENarisChapter Chapter);
 UFUNCTION(BlueprintPure) bool IsUnlocked(ENarisChapter Chapter) const;
 UFUNCTION(BlueprintPure) bool IsCompleted(ENarisChapter Chapter) const;
 UFUNCTION(BlueprintPure) ENarisChapter GetCurrentChapter() const{return CurrentChapter;}
 UFUNCTION(BlueprintCallable) bool SetCurrentChapter(ENarisChapter Chapter);
 const TSet<ENarisChapter>& GetUnlockedSet() const{return Unlocked;}
 const TSet<ENarisChapter>& GetCompletedSet() const{return Completed;}
 void RestoreState(ENarisChapter InCurrent,const TArray<uint8>& InUnlocked,const TArray<uint8>& InCompleted);
private:
 UPROPERTY() TSet<ENarisChapter> Unlocked;
 UPROPERTY() TSet<ENarisChapter> Completed;
 UPROPERTY() ENarisChapter CurrentChapter=ENarisChapter::AshenGate;
};