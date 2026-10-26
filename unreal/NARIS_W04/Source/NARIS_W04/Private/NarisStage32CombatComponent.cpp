#include "NarisStage32CombatComponent.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"

UNarisStage32CombatComponent::UNarisStage32CombatComponent(){PrimaryComponentTick.bCanEverTick=true;}
void UNarisStage32CombatComponent::BeginPlay(){
 Super::BeginPlay();
 MaxHealth=FMath::Max(1.f,MaxHealth);MaxStamina=FMath::Max(0.f,MaxStamina);
 Health=MaxHealth;Stamina=MaxStamina;EmitVitals();
}
void UNarisStage32CombatComponent::EndPlay(const EEndPlayReason::Type Reason){
 ClearActiveMontageBinding();Super::EndPlay(Reason);
}
void UNarisStage32CombatComponent::EmitVitals(){OnVitalsChanged.Broadcast(Health,Stamina);}
void UNarisStage32CombatComponent::ClearActiveMontageBinding(){
 if(IsValid(ActiveAnimInstance) && IsValid(ActiveMontage)){
  FOnMontageEnded EmptyDelegate;
  ActiveAnimInstance->Montage_SetEndDelegate(EmptyDelegate,ActiveMontage);
 }
 ActiveAnimInstance=nullptr;ActiveMontage=nullptr;
}
bool UNarisStage32CombatComponent::TryPlay(USkeletalMeshComponent* Mesh,UAnimMontage* Montage,float Cost,ENarisCombatState Next){
 if(State!=ENarisCombatState::Idle || Health<=0.f || !FMath::IsFinite(Cost) || Cost<0.f || Stamina<Cost ||
    !IsValid(Mesh) || !IsValid(Montage) || !IsValid(Mesh->GetAnimInstance()))return false;
 UAnimInstance* Anim=Mesh->GetAnimInstance();
 if(Anim->Montage_Play(Montage)<=0.f)return false;
 // Commit stamina only after animation playback succeeds.
 Stamina-=Cost;State=Next;StateAge=0.f;bHitWindow=false;AlreadyHit.Reset();
 ActiveAnimInstance=Anim;ActiveMontage=Montage;
 FOnMontageEnded Delegate;
 Delegate.BindUObject(this,&UNarisStage32CombatComponent::OnMontageEnded);
 Anim->Montage_SetEndDelegate(Delegate,Montage);
 EmitVitals();return true;
}
bool UNarisStage32CombatComponent::StartAttack(USkeletalMeshComponent* Mesh,UAnimMontage* Montage){
 return TryPlay(Mesh,Montage,AttackCost,ENarisCombatState::Attack);
}
bool UNarisStage32CombatComponent::StartDodge(USkeletalMeshComponent* Mesh,UAnimMontage* Montage){
 return TryPlay(Mesh,Montage,DodgeCost,ENarisCombatState::Dodge);
}
void UNarisStage32CombatComponent::BeginHitWindow(){
 if(State==ENarisCombatState::Attack)bHitWindow=true;
}
void UNarisStage32CombatComponent::EndHitWindow(){bHitWindow=false;}
void UNarisStage32CombatComponent::EnterRecovery(){
 bHitWindow=false;AlreadyHit.Reset();
 if(State!=ENarisCombatState::Dead){State=ENarisCombatState::Recovery;StateAge=0.f;}
}
void UNarisStage32CombatComponent::OnMontageEnded(UAnimMontage* Montage,bool bInterrupted){
 if(Montage!=ActiveMontage)return;
 ClearActiveMontageBinding();
 if(State==ENarisCombatState::Attack || State==ENarisCombatState::Dodge)EnterRecovery();
}
void UNarisStage32CombatComponent::CancelAction(){
 if(State==ENarisCombatState::Dead)return;
 // Do not forcibly stop a montage in an external AnimBP; caller may stop it.
 ClearActiveMontageBinding();EnterRecovery();
}
bool UNarisStage32CombatComponent::CanReceiveDamage() const {
 return State!=ENarisCombatState::Dead &&
        !(State==ENarisCombatState::Dodge && StateAge<DodgeInvulnerabilitySeconds);
}
void UNarisStage32CombatComponent::ReceiveDamageAmount(float Amount){
 if(!FMath::IsFinite(Amount) || Amount<=0.f || !CanReceiveDamage())return;
 Health=FMath::Max(0.f,Health-Amount);
 if(Health<=0.f){
  ClearActiveMontageBinding();State=ENarisCombatState::Dead;bHitWindow=false;AlreadyHit.Reset();
 }else{CancelAction();}
 EmitVitals();
}
void UNarisStage32CombatComponent::TickComponent(float Dt,ELevelTick T,FActorComponentTickFunction* Fn){
 Super::TickComponent(Dt,T,Fn);
 if(State==ENarisCombatState::Dead || !FMath::IsFinite(Dt) || Dt<=0.f)return;
 StateAge+=Dt;
 if(State==ENarisCombatState::Recovery && StateAge>=RecoverySeconds){
  State=ENarisCombatState::Idle;StateAge=0.f;
 }
 if(State==ENarisCombatState::Idle){
  const float Before=Stamina;
  Stamina=FMath::Min(MaxStamina,Stamina+FMath::Max(0.f,StaminaRegenPerSecond)*Dt);
  if(!FMath::IsNearlyEqual(Before,Stamina))EmitVitals();
 }
 if(State!=ENarisCombatState::Attack || !bHitWindow || !IsValid(GetOwner()) || !GetWorld())return;
 const FVector Start=GetOwner()->GetActorLocation()+FVector(0,0,75.f);
 const FVector End=Start+GetOwner()->GetActorForwardVector()*AttackReachCm;
 FCollisionQueryParams Query(SCENE_QUERY_STAT(NarisStage32Hit),false,GetOwner());
 TArray<FHitResult> Hits;
 if(!GetWorld()->SweepMultiByChannel(Hits,Start,End,FQuat::Identity,ECC_Pawn,
     FCollisionShape::MakeSphere(FMath::Max(1.f,AttackRadiusCm)),Query))return;
 for(const FHitResult& Hit:Hits){
  AActor* Other=Hit.GetActor();
  if(!IsValid(Other) || AlreadyHit.Contains(Other))continue;
  auto* Target=Other->FindComponentByClass<UNarisStage32CombatComponent>();
  if(!IsValid(Target) || (!bAllowFriendlyFire && TeamId==Target->TeamId))continue;
  AlreadyHit.Add(Other);Target->ReceiveDamageAmount(AttackDamage);
 }
}
