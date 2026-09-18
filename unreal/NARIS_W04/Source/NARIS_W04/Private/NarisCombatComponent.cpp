#include "NarisCombatComponent.h"
UNarisCombatComponent::UNarisCombatComponent(){PrimaryComponentTick.bCanEverTick=false;}
FNarisCombatResult UNarisCombatComponent::ResolveHit(float BaseDamage,float PoiseDamage,bool bParried,bool bCritical){
    FNarisCombatResult R; R.bParried=bParried; R.bCritical=bCritical;
    if(bParried){AddResonance(15.f); R.bCritical=false;}
    else{
        R.Damage=bCritical?BaseDamage*1.5f:BaseDamage; R.PoiseDamage=PoiseDamage;
        Health=FMath::Clamp(Health-R.Damage,0.f,MaxHealth);
        Poise=FMath::Clamp(Poise-PoiseDamage,0.f,MaxPoise);
        R.bStaggered=Poise<=0.f; R.bExecutionWindow=R.bStaggered&&Health>0.f;
        if(R.bStaggered)ResetPoise();
    }
    OnCombatResolved.Broadcast(R); return R;
}
void UNarisCombatComponent::AddResonance(float Amount){Resonance=FMath::Clamp(Resonance+Amount,0.f,MaxResonance);}
void UNarisCombatComponent::ResetPoise(){Poise=MaxPoise;}