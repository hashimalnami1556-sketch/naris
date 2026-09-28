#include "NarisHitReactionComponent.h"
#include "GameFramework/Character.h"
UNarisHitReactionComponent::UNarisHitReactionComponent(){PrimaryComponentTick.bCanEverTick=true;}
void UNarisHitReactionComponent::TickComponent(float D,ELevelTick T,FActorComponentTickFunction* F){Super::TickComponent(D,T,F);CooldownRemaining=FMath::Max(0.f,CooldownRemaining-D);}
float UNarisHitReactionComponent::ReactToHit(float Damage,AActor* C)
{
 AActor* O=GetOwner(); if(!O||CooldownRemaining>0.f||Damage<=0.f) return 0.f;
 FVector Dir=-O->GetActorForwardVector();
 if(C){Dir=O->GetActorLocation()-C->GetActorLocation();Dir.Z=0.f;Dir=Dir.GetSafeNormal();}
 const float S=Damage>=HeavyHitThreshold?1.f:(Damage>=LightHitThreshold?.65f:.35f);
 LastDirection=Dir;LastStrength=S;CooldownRemaining=ReactionCooldown;
 if(ACharacter* Ch=Cast<ACharacter>(O))Ch->LaunchCharacter(Dir*(180.f+320.f*S)+FVector(0,0,50.f+70.f*S),true,false);
 OnHitReacted.Broadcast(Damage,Dir,S);return S;
}