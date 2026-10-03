#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisSaveSubsystem.generated.h"

UCLASS()
class NARISCORE_API UNarisSaveSubsystem : public UGameInstanceSubsystem
{
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) bool SavePlayer(class ANarisPlayerCharacter* Player, const FString& Slot="NARIS_Autosave");
 UFUNCTION(BlueprintCallable) bool LoadPlayer(class ANarisPlayerCharacter* Player, const FString& Slot="NARIS_Autosave");
 void QueueLoadAfterTravel(const FString& Slot){PendingLoadSlot=Slot;}
 FString ConsumePendingLoadSlot(){FString Slot=PendingLoadSlot;PendingLoadSlot.Empty();return Slot;}
private:
 FString PendingLoadSlot;
};
