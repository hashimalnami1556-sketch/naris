#include "NarisEnemyCharacter.h"
#include "NarisVitalsComponent.h"
#include "NarisHitReactionComponent.h"
#include "NarisQuestSubsystem.h"
#include "NarisWorldStateSubsystem.h"
#include "NarisNarrativeTypes.h"
#include "NarisPickupActor.h"
#include "NarisGameModeBase.h"
#include "NarisAttackTokenCoordinator.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/World.h"

ANarisEnemyCharacter::ANarisEnemyCharacter()
{
 PrimaryActorTick.bCanEverTick=true;
 Vitals=CreateDefaultSubobject<UNarisVitalsComponent>(TEXT("Vitals"));Vitals->MaxHealth=85.f;Vitals->Health=85.f;
 HitReaction=CreateDefaultSubobject<UNarisHitReactionComponent>(TEXT("HitReaction"));
 Visual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LegacyVisual"));Visual->SetupAttachment(RootComponent);Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);Visual->SetVisibility(false);
 static ConstructorHelpers::FObjectFinder<USkeletalMesh> Rig(TEXT("/Game/Art/Characters/RiggedV4/BoneBeast/SK_BoneBeast.SK_BoneBeast"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Idle(TEXT("/Game/Art/Characters/RiggedV4/BoneBeast/AN_Beast_Idle.AN_Beast_Idle"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Run(TEXT("/Game/Art/Characters/RiggedV4/BoneBeast/AN_Beast_Run.AN_Beast_Run"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Swipe(TEXT("/Game/Art/Characters/RiggedV4/BoneBeast/AN_Beast_Swipe.AN_Beast_Swipe"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Stunned(TEXT("/Game/Art/Characters/RiggedV4/BoneBeast/AN_Beast_Stunned.AN_Beast_Stunned"));
 if(Rig.Succeeded()){GetMesh()->SetSkeletalMeshAsset(Rig.Object);GetMesh()->SetRelativeLocation(FVector::ZeroVector);GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
 IdleAnim=Idle.Object;RunAnim=Run.Object;AttackAnim=Swipe.Object;StunnedAnim=Stunned.Object;
 if(IdleAnim){GetMesh()->SetAnimationMode(EAnimationMode::AnimationSingleNode);SetAnim(IdleAnim,true,0);}
 GetCharacterMovement()->MaxWalkSpeed=330.f;
}
FName ANarisEnemyCharacter::PersistenceFlag() const{return PersistentID.IsNone()?NAME_None:FName(*FString::Printf(TEXT("Defeated_%s"),*PersistentID.ToString()));}
void ANarisEnemyCharacter::ApplyPersistentState(){const FName Flag=PersistenceFlag();if(Flag.IsNone())return;if(UGameInstance* G=GetGameInstance())if(UNarisWorldStateSubsystem* W=G->GetSubsystem<UNarisWorldStateSubsystem>())if(W->GetFlag(Flag)){UE_LOG(LogTemp,Display,TEXT("NARIS_PERSIST_SUPPRESS Enemy=%s"),*PersistentID.ToString());Destroy();}}
bool ANarisEnemyCharacter::TryAcquireAttackToken(){if(bAttackTokenHeld)return true;if(ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this)))if(GM->AttackCoordinator){bAttackTokenHeld=GM->AttackCoordinator->RequestAttackToken(this);return bAttackTokenHeld;}return true;}
void ANarisEnemyCharacter::ReleaseAttackToken(){if(!bAttackTokenHeld)return;if(ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this)))if(GM->AttackCoordinator)GM->AttackCoordinator->ReleaseAttackToken(this);bAttackTokenHeld=false;}
void ANarisEnemyCharacter::SetAnim(UAnimSequence* A,bool L,int32 S){if(A&&AnimState!=S){GetMesh()->PlayAnimation(A,L);AnimState=S;}}
void ANarisEnemyCharacter::Tick(float D)
{
 Super::Tick(D);if(!Vitals->IsAlive()){ReleaseAttackToken();return;}Cooldown=FMath::Max(0.f,Cooldown-D);AttackAnimTime=FMath::Max(0.f,AttackAnimTime-D);
 if(bAttackTokenHeld&&AttackAnimTime<=0.f)ReleaseAttackToken();
 ACharacter* P=UGameplayStatics::GetPlayerCharacter(this,0);if(!P){ReleaseAttackToken();return;}FVector Delta=P->GetActorLocation()-GetActorLocation();Delta.Z=0.f;const float Dist=Delta.Size();
 if(Dist>AggroRange){ReleaseAttackToken();if(AttackAnimTime<=0.f)SetAnim(IdleAnim,true,0);return;}
 if(Dist>AttackRange){ReleaseAttackToken();AddMovementInput(Delta.GetSafeNormal(),1.f);SetActorRotation(Delta.Rotation());if(AttackAnimTime<=0.f)SetAnim(RunAnim,true,1);}
 else if(Cooldown<=0.f&&TryAcquireAttackToken()){SetAnim(AttackAnim,false,2);AttackAnimTime=.55f;UGameplayStatics::ApplyDamage(P,AttackDamage,GetController(),this,UDamageType::StaticClass());Cooldown=AttackCooldown;}
 else if(AttackAnimTime<=0.f)SetAnim(IdleAnim,true,0);
}
float ANarisEnemyCharacter::TakeDamage(float A,const FDamageEvent& E,AController* I,AActor* C)
{
 const float D=Vitals->ApplyHealthDamage(A);
 if(D>0.f&&Vitals->IsAlive()){const float S=HitReaction?HitReaction->ReactToHit(D,C):0.f;if(StunnedAnim&&S>=.65f){GetMesh()->PlayAnimation(StunnedAnim,false);AnimState=3;AttackAnimTime=S>=1.f?.8f:.42f;}}
 if(!Vitals->IsAlive()){
  ReleaseAttackToken();
  GetCharacterMovement()->DisableMovement();
  if(!bDeathReported){bDeathReported=true;const FName Target=GetDefeatNarrativeTarget();if(UGameInstance* G=GetGameInstance()){const FName Flag=PersistenceFlag();if(!Flag.IsNone())if(UNarisWorldStateSubsystem* W=G->GetSubsystem<UNarisWorldStateSubsystem>())W->SetFlag(Flag,true);if(bCountsAsRegularEnemy)if(UNarisQuestSubsystem* Q=G->GetSubsystem<UNarisQuestSubsystem>()){FNarisNarrativeEvent N;N.Type=ENarisNarrativeEventType::EnemyDefeated;N.TargetID=Target;Q->PublishNarrativeEvent(N);}}if(bCountsAsRegularEnemy){if(UWorld* W=GetWorld())W->SpawnActor<ANarisPickupActor>(ANarisPickupActor::StaticClass(),GetActorLocation()+FVector(0,0,70.f),FRotator::ZeroRotator);UE_LOG(LogTemp,Display,TEXT("NARIS_ENEMY_DEFEATED %s Loot=AshShard Persistent=%s"),*Target.ToString(),*PersistentID.ToString());}}
  SetLifeSpan(3.f);
 }
 return D;
}