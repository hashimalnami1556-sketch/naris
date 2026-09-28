#include "NarisHitboxComponent.h"
void UNarisHitboxComponent::BeginHitWindow(FName AttackID, FName Socket, float Radius){ bActive=true; ActiveAttack=AttackID; ActiveSocket=Socket; ActiveRadius=Radius; HitActors.Reset(); }
void UNarisHitboxComponent::EndHitWindow(){ bActive=false; ActiveAttack=NAME_None; HitActors.Reset(); }
