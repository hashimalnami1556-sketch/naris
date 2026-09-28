#include "NarisRoadNetworkComponent.h"
TArray<FName> UNarisRoadNetworkComponent::GetNeighbors(FName Node) const { TArray<FName> Out; for(const auto& E:Edges){ if(E.From==Node) Out.AddUnique(E.To); else if(E.To==Node) Out.AddUnique(E.From);} return Out; }
