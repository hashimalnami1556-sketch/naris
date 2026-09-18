#include "NarisLockOnComponent.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/Pawn.h"
#include "NarisCombatComponent.h"
UNarisLockOnComponent::UNarisLockOnComponent(){PrimaryComponentTick.bCanEverTick=false;}
bool UNarisLockOnComponent::AcquireTarget()
{
    APawn* OwnerPawn=Cast<APawn>(GetOwner()); if(!OwnerPawn||!GetWorld()) return false;
    const FVector Origin=OwnerPawn->GetActorLocation(), Forward=OwnerPawn->GetActorForwardVector();
    float BestScore=FLT_MAX; AActor* Best=nullptr;
    for(TActorIterator<AActor> It(GetWorld());It;++It)
    {
        AActor* Candidate=*It; if(!Candidate||Candidate==GetOwner()) continue;
        UNarisCombatComponent* Combat=Candidate->FindComponentByClass<UNarisCombatComponent>();
        if(!Combat||Combat->Health<=0.f) continue;
        FVector To=Candidate->GetActorLocation()-Origin; float Dist=To.Size();
        if(Dist>MaxDistance||Dist<1.f) continue;
        float Angle=FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(FVector::DotProduct(Forward,To.GetSafeNormal()),-1.f,1.f)));
        if(Angle>MaxAngleDegrees) continue;
        float Score=Dist+Angle*8.f; if(Score<BestScore){BestScore=Score;Best=Candidate;}
    }
    Target=Best; return IsValid(Target);
}
void UNarisLockOnComponent::ClearTarget(){Target=nullptr;}
