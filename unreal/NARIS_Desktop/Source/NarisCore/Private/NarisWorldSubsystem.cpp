#include "NarisWorldSubsystem.h"
void UNarisWorldSubsystem::SetActiveZone(FName ZoneID){
 if (ActiveZone == ZoneID) return;
 const FName Previous = ActiveZone; ActiveZone = ZoneID; OnZoneChanged.Broadcast(Previous, ActiveZone);
}
int32 UNarisWorldSubsystem::MakeDeterministicSeed(FName ZoneID, int32 LayerSeed) const {
 return HashCombine(HashCombine(GetTypeHash(WorldSeed), GetTypeHash(ZoneID)), GetTypeHash(LayerSeed));
}
