#include "NarisVFXDirectorComponent.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "UObject/ConstructorHelpers.h"

UNarisVFXDirectorComponent::UNarisVFXDirectorComponent()
{
 static ConstructorHelpers::FObjectFinder<UNiagaraSystem> R(TEXT("/Niagara/DefaultAssets/Templates/Systems/RadialBurst.RadialBurst"));
 static ConstructorHelpers::FObjectFinder<UNiagaraSystem> D(TEXT("/Niagara/DefaultAssets/Templates/Systems/DirectionalBurst.DirectionalBurst"));
 static ConstructorHelpers::FObjectFinder<UNiagaraSystem> E(TEXT("/Niagara/DefaultAssets/Templates/Systems/SimpleExplosion.SimpleExplosion"));
 RadialBurst=R.Object; DirectionalBurst=D.Object; SimpleExplosion=E.Object;
}
UNiagaraSystem* UNarisVFXDirectorComponent::Resolve(FName E) const
{
 if(E==FName("Hit")||E==FName("Pickup")) return RadialBurst;
 if(E==FName("Parry")||E==FName("Dodge")) return DirectionalBurst;
 if(E==FName("BossPhase")||E==FName("QuestComplete")) return SimpleExplosion;
 return nullptr;
}
void UNarisVFXDirectorComponent::SpawnVFX(FName E,FVector L,FRotator R,float S)
{
 if(UNiagaraSystem* N=Resolve(E)){
  UNiagaraFunctionLibrary::SpawnSystemAtLocation(this,N,L,R,FVector(FMath::Clamp(S,.1f,4.f)),true,true,ENCPoolMethod::AutoRelease,true);
  UE_LOG(LogTemp,Verbose,TEXT("NARIS_VFX_EVENT %s"),*E.ToString());
 }
}
bool UNarisVFXDirectorComponent::IsCombatVFXReady() const
{
 return RadialBurst&&DirectionalBurst&&SimpleExplosion;
}