#include "NarisBossCharacter.h"
#include "NarisBossPhaseComponent.h"
#include "NarisVitalsComponent.h"
#include "NarisQuestSubsystem.h"
#include "NarisWorldStateSubsystem.h"
#include "NarisNarrativeTypes.h"
#include "NarisGameModeBase.h"
#include "NarisAudioDirectorComponent.h"
#include "NarisVFXDirectorComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Animation/AnimSequence.h"
#include "UObject/ConstructorHelpers.h"

ANarisBossCharacter::ANarisBossCharacter()
{
 Phase=CreateDefaultSubobject<UNarisBossPhaseComponent>(TEXT("BossPhase"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Enrage(TEXT("/Game/Art/Characters/RiggedV4/BoneBeast/AN_Beast_Enrage.AN_Beast_Enrage"));EnrageAnim=Enrage.Object;
 bCountsAsRegularEnemy=false;
 Vitals->MaxHealth=360.f; Vitals->Health=360.f;
 AttackDamage=20.f; AttackCooldown=1.0f; AggroRange=2600.f; AttackRange=220.f;
 GetCharacterMovement()->MaxWalkSpeed=280.f;
 SetActorScale3D(FVector(1.65f));
}
float ANarisBossCharacter::TakeDamage(float A,const FDamageEvent& E,AController* I,AActor* C)
{
 const float D=Super::TakeDamage(A,E,I,C);
 if(!Vitals||Vitals->MaxHealth<=0.f) return D;
 const float R=Vitals->Health/Vitals->MaxHealth;
 bool bPhaseChanged=false;
 if(R<=0.33f&&Phase->RequestPhase(3)){AttackDamage=32.f;AttackCooldown=.55f;GetCharacterMovement()->MaxWalkSpeed=430.f;bPhaseChanged=true;UE_LOG(LogTemp,Display,TEXT("NARIS_BOSS_PHASE GateWarden 3"));}
 else if(R<=0.66f&&Phase->RequestPhase(2)){AttackDamage=26.f;AttackCooldown=.75f;GetCharacterMovement()->MaxWalkSpeed=360.f;bPhaseChanged=true;UE_LOG(LogTemp,Display,TEXT("NARIS_BOSS_PHASE GateWarden 2"));}
 if(bPhaseChanged){if(EnrageAnim){GetMesh()->PlayAnimation(EnrageAnim,false);}UE_LOG(LogTemp,Display,TEXT("NARIS_BOSS_ENRAGE_ANIM Phase=%d"),Phase->CurrentPhase);}
 if(bPhaseChanged) if(ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this))){
  if(GM->AudioDirector) GM->AudioDirector->PlaySFX(FName("BossPhase"),GetActorLocation(),1.1f);
  if(GM->VFXDirector) GM->VFXDirector->SpawnVFX(FName("BossPhase"),GetActorLocation()+FVector(0,0,100.f),FRotator::ZeroRotator,1.35f);
 }

 if(!Vitals->IsAlive()&&!bBossDeathReported){
  bBossDeathReported=true;
  if(UGameInstance* G=GetGameInstance()){
   if(UNarisQuestSubsystem* Q=G->GetSubsystem<UNarisQuestSubsystem>()){
    FNarisNarrativeEvent N; N.Type=ENarisNarrativeEventType::BossDefeated; N.TargetID=FName("GateWarden"); Q->PublishNarrativeEvent(N);
   }
   if(UNarisWorldStateSubsystem* W=G->GetSubsystem<UNarisWorldStateSubsystem>()){
    W->SetFlag(FName("AshenGateOpened"),true);
    W->AddFactionReputation(FName("Wardens"),10);
   }
  }
  UE_LOG(LogTemp,Display,TEXT("NARIS_BOSS_DEFEATED GateWarden AshenGateOpened=1 ReputationWardens=+10"));
 }
 return D;
}