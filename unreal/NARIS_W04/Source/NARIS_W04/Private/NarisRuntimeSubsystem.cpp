#include "NarisRuntimeSubsystem.h"
#include "NarisSaveGame.h"
#include "Kismet/GameplayStatics.h"
void UNarisRuntimeSubsystem::BeginNewGame(){State=FNarisSaveState();}
bool UNarisRuntimeSubsystem::SaveState(const FString& SlotName){
 auto* Save=Cast<UNarisSaveGame>(UGameplayStatics::CreateSaveGameObject(UNarisSaveGame::StaticClass()));
 if(!Save)return false; Save->State=State; return UGameplayStatics::SaveGameToSlot(Save,SlotName,0);
}
bool UNarisRuntimeSubsystem::LoadState(const FString& SlotName){
 if(!UGameplayStatics::DoesSaveGameExist(SlotName,0))return false;
 auto* Save=Cast<UNarisSaveGame>(UGameplayStatics::LoadGameFromSlot(SlotName,0));
 if(!Save)return false; State=Save->State; return true;
}