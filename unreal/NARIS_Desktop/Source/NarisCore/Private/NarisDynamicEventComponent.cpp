#include "NarisDynamicEventComponent.h"
#include "Engine/World.h"
bool UNarisDynamicEventComponent::CanTriggerEvent(FName EventID, float CooldownSeconds) const {
 if (!GetWorld()) return false; const double Now=GetWorld()->GetTimeSeconds();
 const double* Last=LastTriggered.Find(EventID); return !Last || (Now-*Last)>=CooldownSeconds;
}
void UNarisDynamicEventComponent::MarkTriggered(FName EventID){ if(GetWorld()) LastTriggered.Add(EventID,GetWorld()->GetTimeSeconds()); }
