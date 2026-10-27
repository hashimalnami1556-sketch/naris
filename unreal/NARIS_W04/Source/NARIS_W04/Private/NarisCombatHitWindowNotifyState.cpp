#include "NarisCombatHitWindowNotifyState.h"
#include "NarisStage32CombatComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Actor.h"

void UNarisCombatHitWindowNotifyState::NotifyBegin(
 USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation,
 float TotalDuration, const FAnimNotifyEventReference& EventReference)
{
 Super::NotifyBegin(MeshComp,Animation,TotalDuration,EventReference);
 if(!IsValid(MeshComp) || !IsValid(MeshComp->GetOwner()))return;
 if(UNarisStage32CombatComponent* Combat =
    MeshComp->GetOwner()->FindComponentByClass<UNarisStage32CombatComponent>())
 {
  Combat->BeginHitWindow();
 }
}
void UNarisCombatHitWindowNotifyState::NotifyEnd(
 USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation,
 const FAnimNotifyEventReference& EventReference)
{
 Super::NotifyEnd(MeshComp,Animation,EventReference);
 if(!IsValid(MeshComp) || !IsValid(MeshComp->GetOwner()))return;
 if(UNarisStage32CombatComponent* Combat =
    MeshComp->GetOwner()->FindComponentByClass<UNarisStage32CombatComponent>())
 {
  Combat->EndHitWindow();
 }
}
