#include "NarisThreatComponent.h"
void UNarisThreatComponent::AddThreat(AActor* S,float A){if(!S||A<=0)return; for(auto& E:Entries){if(E.Actor==S){E.Threat+=A;return;}} FNarisThreatEntry E;E.Actor=S;E.Threat=A;Entries.Add(E);}
void UNarisThreatComponent::RemoveThreat(AActor* S){Entries.RemoveAll([S](const FNarisThreatEntry&E){return E.Actor==S;});}
AActor* UNarisThreatComponent::GetHighestThreatTarget()const{AActor* B=nullptr;float V=-1;for(const auto&E:Entries){if(IsValid(E.Actor)&&E.Threat>V){V=E.Threat;B=E.Actor;}}return B;}
void UNarisThreatComponent::DecayThreat(float D,float R){for(auto&E:Entries)E.Threat=FMath::Max(0.f,E.Threat-D*R);Entries.RemoveAll([](const FNarisThreatEntry&E){return !IsValid(E.Actor)||E.Threat<=0.f;});}
