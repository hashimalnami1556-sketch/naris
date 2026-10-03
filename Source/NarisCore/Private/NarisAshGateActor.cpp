#include "NarisAshGateActor.h"
#include "NarisWorldStateSubsystem.h"
#include "NarisChapterSubsystem.h"
#include "NarisPlayerCharacter.h"
#include "NarisSaveSubsystem.h"
#include "Components/BoxComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/GameInstance.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

ANarisAshGateActor::ANarisAshGateActor()
{
 PrimaryActorTick.bCanEverTick=true;
 Barrier=CreateDefaultSubobject<UBoxComponent>(TEXT("QuestBarrier"));
 RootComponent=Barrier;
 Barrier->SetBoxExtent(FVector(75.f,600.f,1050.f));
 Barrier->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
 Barrier->SetCollisionObjectType(ECC_WorldStatic);
 Barrier->SetCollisionResponseToAllChannels(ECR_Ignore);
 Barrier->SetCollisionResponseToChannel(ECC_Pawn,ECR_Block);
 Barrier->SetCanEverAffectNavigation(false);
 SetActorTickInterval(.25f);
}
void ANarisAshGateActor::BeginPlay()
{
 Super::BeginPlay();
 UE_LOG(LogTemp,Display,TEXT("NARIS_ASH_GATE_ACTIVE"));
}
void ANarisAshGateActor::Tick(float DeltaSeconds)
{
 Super::Tick(DeltaSeconds);
 UGameInstance* Instance=GetGameInstance();
 if(!Instance)return;
 UNarisWorldStateSubsystem* State=Instance->GetSubsystem<UNarisWorldStateSubsystem>();
 if(!State)return;
 if(!bOpen&&State->GetFlag(TEXT("AshenGateOpened")))
 {
  bOpen=true;
  Barrier->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  UE_LOG(LogTemp,Display,TEXT("NARIS_ASH_GATE_OPEN PassageEnabled=1"));
 }
 if(!bOpen||bEntered)return;
 ANarisPlayerCharacter* Player=Cast<ANarisPlayerCharacter>(UGameplayStatics::GetPlayerCharacter(this,0));
 if(!Player)return;
 const bool bCrossSmoke=FParse::Param(FCommandLine::Get(),TEXT("NarisGateCrossSmoke"));
 if(bCrossSmoke)
  Player->SetActorLocation(GetActorLocation()+FVector(140.f,0.f,-900.f),false,nullptr,ETeleportType::TeleportPhysics);
 const FVector Delta=Player->GetActorLocation()-GetActorLocation();
 // Only crossing to the far side of the portal, not merely defeating the boss nearby.
 if(FMath::Abs(Delta.Y)<=600.f&&FMath::Abs(Delta.Z)<=1050.f&&Delta.X>20.f&&Delta.X<PassageDistance)
 {
  bEntered=true;
  State->SetFlag(TEXT("AshenGateEntered"),true);
  if(UNarisChapterSubsystem* Chapter=Instance->GetSubsystem<UNarisChapterSubsystem>())
  {
   Chapter->UnlockChapter(ENarisChapter::BellMarsh);
   Chapter->SetCurrentChapter(ENarisChapter::BellMarsh);
  }
  bool bSaved=false;
  if(!bCrossSmoke) if(UNarisSaveSubsystem* Save=Instance->GetSubsystem<UNarisSaveSubsystem>())
   bSaved=Save->SavePlayer(Player,TEXT("NARIS_Autosave"));
  const bool bChapterOK=Instance->GetSubsystem<UNarisChapterSubsystem>() &&
   Instance->GetSubsystem<UNarisChapterSubsystem>()->GetCurrentChapter()==ENarisChapter::BellMarsh;
  UE_LOG(LogTemp,Display,TEXT("NARIS_ASH_GATE_ENTERED ChapterOK=%d Autosave=%d Smoke=%d"),bChapterOK?1:0,bSaved?1:0,bCrossSmoke?1:0);
  if(!bCrossSmoke||FParse::Param(FCommandLine::Get(),TEXT("NarisGateTravelSmoke"))){
   const FName Destination(TEXT("/Game/World/Maps/L_BellMarsh_Playable_V1"));
   UE_LOG(LogTemp,Display,TEXT("NARIS_GATE_WORLD_TRAVEL Destination=%s"),*Destination.ToString());
   UGameplayStatics::OpenLevel(this,Destination,true,TEXT("NarisWorldTravel"));
  }
 }
}
