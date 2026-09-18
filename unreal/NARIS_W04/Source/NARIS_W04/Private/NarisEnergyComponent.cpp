#include "NarisEnergyComponent.h"
UNarisEnergyComponent::UNarisEnergyComponent(){PrimaryComponentTick.bCanEverTick=false;}
bool UNarisEnergyComponent::Spend(float Amount){if(Amount<=0.f||Energy<Amount)return false;Energy-=Amount;return true;}
void UNarisEnergyComponent::Restore(float Amount){Energy=FMath::Clamp(Energy+FMath::Max(0.f,Amount),0.f,MaxEnergy);}
void UNarisEnergyComponent::SetEssence(ENarisEssence NewEssence){ActiveEssence=NewEssence;}