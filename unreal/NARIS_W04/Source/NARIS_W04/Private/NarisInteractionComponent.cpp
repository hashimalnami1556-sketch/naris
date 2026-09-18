#include "NarisInteractionComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Actor.h"
UNarisInteractionComponent::UNarisInteractionComponent(){PrimaryComponentTick.bCanEverTick=false;}
bool UNarisInteractionComponent::Interact()
{
    if(!GetOwner()||!GetWorld()) return false;
    FVector O=GetOwner()->GetActorLocation(); float Best=Radius*Radius; AActor* Hit=nullptr;
    for(TActorIterator<AActor> It(GetWorld());It;++It){AActor* A=*It;if(!A||A==GetOwner())continue;float D=(A->GetActorLocation()-O).SizeSquared();if(D<Best){Best=D;Hit=A;}}
    if(Hit){OnInteracted.Broadcast(Hit);return true;} return false;
}
