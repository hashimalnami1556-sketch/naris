#include "NarisFastTravelComponent.h"
void UNarisFastTravelComponent::UnlockNode(FName NodeID){ if(!NodeID.IsNone()) UnlockedNodes.Add(NodeID); }
bool UNarisFastTravelComponent::IsNodeUnlocked(FName NodeID) const { return UnlockedNodes.Contains(NodeID); }
