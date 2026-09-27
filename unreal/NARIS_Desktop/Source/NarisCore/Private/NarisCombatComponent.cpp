#include "NarisCombatComponent.h"
bool UNarisCombatComponent::ResolveAttack(FName RowName, FNarisAttackRow& OutAttack) const {
 if(!AttackTable) return false;
 const FNarisAttackRow* Row=AttackTable->FindRow<FNarisAttackRow>(RowName,TEXT("ResolveAttack"));
 if(!Row) return false; OutAttack=*Row; return true;
}
