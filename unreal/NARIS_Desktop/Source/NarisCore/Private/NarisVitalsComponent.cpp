#include "NarisVitalsComponent.h"

UNarisVitalsComponent::UNarisVitalsComponent()
{
 PrimaryComponentTick.bCanEverTick=true;
}
void UNarisVitalsComponent::TickComponent(float D,ELevelTick T,FActorComponentTickFunction* F)
{
 Super::TickComponent(D,T,F);
 if(Energy<MaxEnergy){
  Energy=FMath::Min(MaxEnergy,Energy+EnergyRegenPerSecond*D);
  OnEnergyChanged.Broadcast(Energy,MaxEnergy);
 }
}
float UNarisVitalsComponent::ApplyHealthDamage(float A)
{
 if(A<=0.f||Health<=0.f) return 0.f;
 const float Old=Health; Health=FMath::Clamp(Health-A,0.f,MaxHealth);
 OnHealthChanged.Broadcast(Health,MaxHealth);
 if(Old>0.f&&Health<=0.f) OnDeath.Broadcast();
 return Old-Health;
}
float UNarisVitalsComponent::Heal(float A)
{
 if(A<=0.f||Health<=0.f) return 0.f;
 const float Old=Health; Health=FMath::Clamp(Health+A,0.f,MaxHealth);
 OnHealthChanged.Broadcast(Health,MaxHealth); return Health-Old;
}
bool UNarisVitalsComponent::SpendEnergy(float A)
{
 if(A<=0.f) return true; if(Energy<A) return false;
 Energy-=A; OnEnergyChanged.Broadcast(Energy,MaxEnergy); return true;
}