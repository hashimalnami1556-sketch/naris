#include "NarisGameModeBase.h"
#include "NarisPlayerCharacter.h"
#include "NarisEnemyCharacter.h"
#include "NarisBossCharacter.h"
#include "NarisCompanionCharacter.h"
#include "NarisPickupActor.h"
#include "NarisQuestSubsystem.h"
#include "NarisWorldStateSubsystem.h"
#include "NarisSaveSubsystem.h"
#include "NarisInventoryComponent.h"
#include "NarisVitalsComponent.h"
#include "NarisAudioDirectorComponent.h"
#include "NarisVFXDirectorComponent.h"
#include "NarisAttackTokenCoordinator.h"
#include "NarisWorldSimulationComponent.h"
#include "NarisCheckpointActor.h"
#include "NarisRuntimeDiagnosticsSubsystem.h"
#include "NarisChapterSubsystem.h"
#include "NarisUserSettingsSubsystem.h"
#include "NarisHUD.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "Engine/DamageEvents.h"
#include "TimerManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

ANarisGameModeBase::ANarisGameModeBase()
{
 bGameStarted=ShouldStartDirectly(FCommandLine::Get());
 DefaultPawnClass=ANarisPlayerCharacter::StaticClass();
 HUDClass=ANarisHUD::StaticClass();
 AudioDirector=CreateDefaultSubobject<UNarisAudioDirectorComponent>(TEXT("AudioDirector"));
 VFXDirector=CreateDefaultSubobject<UNarisVFXDirectorComponent>(TEXT("VFXDirector"));
 AttackCoordinator=CreateDefaultSubobject<UNarisAttackTokenCoordinator>(TEXT("AttackCoordinator"));
 WorldSimulation=CreateDefaultSubobject<UNarisWorldSimulationComponent>(TEXT("WorldSimulation"));
}
int32 ANarisGameModeBase::ParseBenchmarkEnemyCount(const TCHAR* CmdLine)
{
 int32 Count=0;
 if(FParse::Value(CmdLine,TEXT("NarisBenchmarkEnemies="),Count)) return FMath::Clamp(Count,0,64);
 return 0;
}
bool ANarisGameModeBase::ShouldStartDirectly(const TCHAR* CmdLine)
{
 return FParse::Param(CmdLine,TEXT("NarisDirectPlay"))||FParse::Param(CmdLine,TEXT("NarisQuestSmoke"));
}
bool ANarisGameModeBase::ShouldSkipAshenGateForWorld(const FString& WorldPackageName)
{
 return WorldPackageName.Contains(TEXT("L_Jeddah_GIS_"))||
        WorldPackageName.Contains(TEXT("L_Jeddah_RedSea_"));
}
void ANarisGameModeBase::StartGame()
{
 if(bGameStarted) return;
 bGameStarted=true;
 if(UWorld* W=GetWorld()){
  UGameplayStatics::SetGamePaused(W,false);
  if(APlayerController* PC=UGameplayStatics::GetPlayerController(W,0)){
   PC->bShowMouseCursor=false;
   FInputModeGameOnly Mode; PC->SetInputMode(Mode);
   PC->SetIgnoreMoveInput(false); PC->SetIgnoreLookInput(false);
  }
 }
 UE_LOG(LogTemp,Display,TEXT("NARIS_FRONTEND START_GAME"));
}
void ANarisGameModeBase::BeginPlay()
{
 Super::BeginPlay();
 UWorld* W=GetWorld(); if(!W) return;
 const bool bSmoke=FParse::Param(FCommandLine::Get(),TEXT("NarisQuestSmoke"));
 const bool bDirectPlay=FParse::Param(FCommandLine::Get(),TEXT("NarisDirectPlay"));
 const bool bWorldTravel=W->URL.HasOption(TEXT("NarisWorldTravel"));
 if(bSmoke||bDirectPlay||bWorldTravel){
  if(bWorldTravel)UE_LOG(LogTemp,Display,TEXT("NARIS_WORLD_TRAVEL_START World=%s"),*W->GetOutermost()->GetName());
  bGameStarted=true;
  UGameplayStatics::SetGamePaused(this,false);
  if(APlayerController* PC=UGameplayStatics::GetPlayerController(this,0)){
   PC->bShowMouseCursor=false;
   FInputModeGameOnly Mode; PC->SetInputMode(Mode);
   PC->SetIgnoreMoveInput(false); PC->SetIgnoreLookInput(false);
   UE_LOG(LogTemp,Display,TEXT("NARIS_DIRECT_PLAY Pawn=%s ViewTarget=%s"),*GetNameSafe(PC->GetPawn()),*GetNameSafe(PC->GetViewTarget()));
  }
 }else if(APlayerController* PC=UGameplayStatics::GetPlayerController(this,0)){
  bGameStarted=false;
  UGameplayStatics::SetGamePaused(this,true);
  PC->bShowMouseCursor=true;
  FInputModeGameAndUI Mode; Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock); PC->SetInputMode(Mode);
  PC->SetIgnoreMoveInput(true); PC->SetIgnoreLookInput(true);
  UE_LOG(LogTemp,Display,TEXT("NARIS_FRONTEND READY"));
 }
 const FString WorldPackageName=W->GetOutermost()->GetName();
 if(ShouldSkipAshenGateForWorld(WorldPackageName)){
  if(WorldPackageName.Contains(TEXT("L_Jeddah_GIS_"))){
   UE_LOG(LogTemp,Display,TEXT("NARIS_JEDDAH_GIS_RUNTIME_READY World=%s AshenGateSpawn=0"),*WorldPackageName);
  }else{
   UE_LOG(LogTemp,Warning,TEXT("NARIS_LEGACY_COASTAL_CONCEPT World=%s UserSelectable=0 AshenGateSpawn=0"),*WorldPackageName);
  }
  return;
 }
 if(UGameInstance* G=GetGameInstance()){
  if(UNarisQuestSubsystem* Q=G->GetSubsystem<UNarisQuestSubsystem>()) Q->StartQuest(FName("Q_AshenGate"));
  if(UNarisWorldStateSubsystem* S=G->GetSubsystem<UNarisWorldStateSubsystem>()) S->SetFlag(FName("AshenGate_Started"),true);
 }
 FActorSpawnParameters P;
 P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
 W->SpawnActor<ANarisCompanionCharacter>(ANarisCompanionCharacter::StaticClass(),FVector(-350.f,120.f,120.f),FRotator::ZeroRotator,P);

 ANarisEnemyCharacter* E1=W->SpawnActor<ANarisEnemyCharacter>(ANarisEnemyCharacter::StaticClass(),FVector(650.f,0.f,120.f),FRotator::ZeroRotator,P);
 ANarisEnemyCharacter* E2=W->SpawnActor<ANarisEnemyCharacter>(ANarisEnemyCharacter::StaticClass(),FVector(900.f,260.f,120.f),FRotator::ZeroRotator,P);
 ANarisEnemyCharacter* E3=W->SpawnActor<ANarisEnemyCharacter>(ANarisEnemyCharacter::StaticClass(),FVector(1150.f,-220.f,120.f),FRotator::ZeroRotator,P);
 if(E1){E1->PersistentID=FName("BB_01");E1->ApplyPersistentState();}
 if(E2){E2->PersistentID=FName("BB_02");E2->ApplyPersistentState();}
 if(E3){E3->PersistentID=FName("BB_03");E3->ApplyPersistentState();}
 const int32 BenchmarkEnemyCount=ParseBenchmarkEnemyCount(FCommandLine::Get());
 if(BenchmarkEnemyCount>3){
  int32 Spawned=3;
  for(int32 Index=3;Index<BenchmarkEnemyCount;++Index){
   const float Angle=(2.f*PI*Index)/FMath::Max(1,BenchmarkEnemyCount);
   const float Radius=1200.f+150.f*(Index%3);
   const FVector Location(FMath::Cos(Angle)*Radius,FMath::Sin(Angle)*Radius,120.f);
   if(ANarisEnemyCharacter* Enemy=W->SpawnActor<ANarisEnemyCharacter>(ANarisEnemyCharacter::StaticClass(),Location,FRotator::ZeroRotator,P)){
    Enemy->PersistentID=FName(*FString::Printf(TEXT("BENCH_BB_%02d"),Index+1));
    ++Spawned;
   }
  }
  UE_LOG(LogTemp,Display,TEXT("NARIS_BENCHMARK_ENEMIES Requested=%d Spawned=%d"),BenchmarkEnemyCount,Spawned);
 }

 ANarisBossCharacter* Boss=W->SpawnActor<ANarisBossCharacter>(ANarisBossCharacter::StaticClass(),FVector(1750.f,0.f,140.f),FRotator(0.f,180.f,0.f),P);
 if(Boss){Boss->PersistentID=FName("GateWarden_01");Boss->ApplyPersistentState();}

 ANarisPickupActor* P1=W->SpawnActor<ANarisPickupActor>(ANarisPickupActor::StaticClass(),FVector(-100.f,280.f,80.f),FRotator::ZeroRotator,P);
 ANarisPickupActor* P2=W->SpawnActor<ANarisPickupActor>(ANarisPickupActor::StaticClass(),FVector(350.f,330.f,80.f),FRotator::ZeroRotator,P);
 ANarisPickupActor* P3=W->SpawnActor<ANarisPickupActor>(ANarisPickupActor::StaticClass(),FVector(850.f,-330.f,80.f),FRotator::ZeroRotator,P);
 if(P1){P1->PersistentID=FName("AS_01");P1->ApplyPersistentState();}
 if(P2){P2->PersistentID=FName("AS_02");P2->ApplyPersistentState();}
 if(P3){P3->PersistentID=FName("AS_03");P3->ApplyPersistentState();}
 const TPair<FName,FVector> CheckpointDefs[] = {
  {FName("CP_ENTRY_00"),FVector(-550.f,0.f,80.f)},
  {FName("CP_RUINS_01"),FVector(250.f,650.f,80.f)},
  {FName("CP_ROOT_02"),FVector(650.f,900.f,80.f)},
  {FName("CP_WHISPER_03"),FVector(950.f,650.f,80.f)},
  {FName("CP_SHRINE_04"),FVector(1200.f,350.f,80.f)},
  {FName("CP_CRYPT_05"),FVector(1450.f,150.f,80.f)},
  {FName("CP_BOSS_06"),FVector(1650.f,0.f,80.f)},
  {FName("CP_POSTBOSS_07"),FVector(2050.f,100.f,80.f)},
  {FName("CP_DRAGON_08"),FVector(2350.f,250.f,80.f)}
 };
 for(const TPair<FName,FVector>& Def:CheckpointDefs){
  if(ANarisCheckpointActor* CP=W->SpawnActor<ANarisCheckpointActor>(ANarisCheckpointActor::StaticClass(),Def.Value,FRotator::ZeroRotator,P)) CP->CheckpointID=Def.Key;
 }
 if(UGameInstance* G=GetGameInstance()) if(UNarisRuntimeDiagnosticsSubsystem* D=G->GetSubsystem<UNarisRuntimeDiagnosticsSubsystem>()) D->RunReleaseGate(this);

 const int32 AudioReady=AudioDirector&&AudioDirector->IsCombatAudioReady()?1:0;
 const int32 VFXReady=VFXDirector&&VFXDirector->IsCombatVFXReady()?1:0;
 UE_LOG(LogTemp,Display,TEXT("NARIS_RUNTIME_READY Companion=1 Enemies=3 Boss=1 Pickups=3 Quest=Q_AshenGate Persistence=1 Audio=%d VFX=%d"),AudioReady,VFXReady);

 if(bSmoke){
  FTimerHandle SmokeTimer;
  W->GetTimerManager().SetTimer(SmokeTimer,this,&ANarisGameModeBase::RunQuestSmoke,.35f,false);
 }
}
void ANarisGameModeBase::RunQuestSmoke()
{
 ANarisPlayerCharacter* Player=Cast<ANarisPlayerCharacter>(UGameplayStatics::GetPlayerCharacter(this,0));
 UGameInstance* G=GetGameInstance();
 if(!Player||!G){UE_LOG(LogTemp,Error,TEXT("NARIS_QUEST_SMOKE FAIL MissingPlayerOrGameInstance"));return;}

 TArray<AActor*> Enemies;
 UGameplayStatics::GetAllActorsOfClass(this,ANarisEnemyCharacter::StaticClass(),Enemies);
 FDamageEvent DamageEvent;
 int32 RegularKilled=0;
 int32 BossKilled=0;
 for(AActor* A:Enemies){
  if(ANarisBossCharacter* B=Cast<ANarisBossCharacter>(A)){B->TakeDamage(9999.f,DamageEvent,Player->GetController(),Player);++BossKilled;}
  else if(ANarisEnemyCharacter* Enemy=Cast<ANarisEnemyCharacter>(A)){Enemy->TakeDamage(9999.f,DamageEvent,Player->GetController(),Player);++RegularKilled;}
 }

 TArray<AActor*> Pickups;
 UGameplayStatics::GetAllActorsOfClass(this,ANarisPickupActor::StaticClass(),Pickups);
 for(AActor* A:Pickups) if(ANarisPickupActor* Pickup=Cast<ANarisPickupActor>(A)) Pickup->NotifyActorBeginOverlap(Player);

 UNarisQuestSubsystem* Q=G->GetSubsystem<UNarisQuestSubsystem>();
 UNarisWorldStateSubsystem* W=G->GetSubsystem<UNarisWorldStateSubsystem>();
 UNarisSaveSubsystem* Save=G->GetSubsystem<UNarisSaveSubsystem>();
 UNarisChapterSubsystem* Chapters=G->GetSubsystem<UNarisChapterSubsystem>();
 UNarisRuntimeDiagnosticsSubsystem* Diagnostics=G->GetSubsystem<UNarisRuntimeDiagnosticsSubsystem>();
 UNarisUserSettingsSubsystem* Settings=G->GetSubsystem<UNarisUserSettingsSubsystem>();
 const bool QuestOK=Q&&Q->IsQuestCompleted(FName("Q_AshenGate"));
 const bool GateOK=W&&W->GetFlag(FName("AshenGateOpened"));
 const bool RepOK=W&&W->GetFactionReputation(FName("Wardens"))==10;
 const bool AudioOK=AudioDirector&&AudioDirector->IsCombatAudioReady();
 const bool VFXOK=VFXDirector&&VFXDirector->IsCombatVFXReady();
 const bool ChapterOK=Chapters&&Chapters->IsCompleted(ENarisChapter::AshenGate)&&Chapters->IsUnlocked(ENarisChapter::BellMarsh);
 const bool ReleaseOK=Diagnostics&&Diagnostics->RunReleaseGate(this);

 int32 AshShards=0;
 if(Player->Inventory) for(const FNarisItemStack& S:Player->Inventory->Items) if(S.ItemID==FName("AshShard")) AshShards+=S.Quantity;
 const bool LootOK=AshShards>=3;

 bool SaveOK=false;
 bool PersistOK=false;
 bool ChapterSaveOK=false;
 if(Save&&Player->Vitals&&Player->Inventory&&W&&Chapters){
  Player->Vitals->Health=77.f; Player->Vitals->Energy=66.f; Player->Inventory->AddItem(FName("SmokeToken"),2);
  Chapters->SetCurrentChapter(ENarisChapter::AshenGate);
  const bool Written=Save->SavePlayer(Player,TEXT("NARIS_Smoke"));
  W->SetFlag(FName("Defeated_BB_01"),false);
  W->SetFlag(FName("Collected_AS_01"),false);
  Chapters->SetCurrentChapter(ENarisChapter::BellMarsh);
  Player->Vitals->Health=11.f; Player->Vitals->Energy=5.f; Player->Inventory->RemoveItem(FName("SmokeToken"),2);
  const bool Loaded=Save->LoadPlayer(Player,TEXT("NARIS_Smoke"));
  int32 Tokens=0; for(const FNarisItemStack& S:Player->Inventory->Items) if(S.ItemID==FName("SmokeToken")) Tokens+=S.Quantity;
  SaveOK=Written&&Loaded&&FMath::IsNearlyEqual(Player->Vitals->Health,77.f)&&FMath::IsNearlyEqual(Player->Vitals->Energy,66.f)&&Tokens==2;
  PersistOK=W->GetFlag(FName("Defeated_BB_01"))&&W->GetFlag(FName("Collected_AS_01"));
  ChapterSaveOK=Chapters->GetCurrentChapter()==ENarisChapter::AshenGate&&Chapters->IsCompleted(ENarisChapter::AshenGate)&&Chapters->IsUnlocked(ENarisChapter::BellMarsh);
  UGameplayStatics::DeleteGameInSlot(TEXT("NARIS_Smoke"),0);
 }

 bool SettingsOK=false;
 if(Settings){
  const FNarisAccessibilitySettings Original=Settings->GetAccessibility();
  FNarisAccessibilitySettings A=Original;
  A.bSubtitles=true; A.bReducedCameraMotion=true; A.UIScale=1.2f; A.AimAssistStrength=.5f;
  Settings->SetAccessibility(A);
  const FNarisAccessibilitySettings R=Settings->GetAccessibility();
  SettingsOK=R.bSubtitles&&R.bReducedCameraMotion&&FMath::IsNearlyEqual(R.UIScale,1.2f)&&FMath::IsNearlyEqual(R.AimAssistStrength,.5f);
  Settings->SetAccessibility(Original);
 }

 bool CheckpointOK=false;
 TArray<AActor*> Checkpoints;
 UGameplayStatics::GetAllActorsOfClass(this,ANarisCheckpointActor::StaticClass(),Checkpoints);
 if(Checkpoints.Num()>0){
  if(ANarisCheckpointActor* CP=Cast<ANarisCheckpointActor>(Checkpoints[0])) CP->NotifyActorBeginOverlap(Player);
  CheckpointOK=UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_SmokeCheckpoint"),0);
  UGameplayStatics::DeleteGameInSlot(TEXT("NARIS_SmokeCheckpoint"),0);
 }

 const bool Pass=RegularKilled==3&&BossKilled==1&&QuestOK&&GateOK&&RepOK&&LootOK&&SaveOK&&PersistOK&&AudioOK&&VFXOK&&ChapterOK&&ReleaseOK&&ChapterSaveOK&&SettingsOK&&CheckpointOK;
 UE_LOG(LogTemp,Display,TEXT("NARIS_QUEST_SMOKE %s Regular=%d Boss=%d Shards=%d Quest=%d Gate=%d Rep=%d Save=%d Persist=%d Audio=%d VFX=%d Chapter=%d Release=%d ChapterSave=%d Settings=%d Checkpoint=%d"),
  Pass?TEXT("PASS"):TEXT("FAIL"),RegularKilled,BossKilled,AshShards,QuestOK?1:0,GateOK?1:0,RepOK?1:0,SaveOK?1:0,PersistOK?1:0,AudioOK?1:0,VFXOK?1:0,ChapterOK?1:0,ReleaseOK?1:0,ChapterSaveOK?1:0,SettingsOK?1:0,CheckpointOK?1:0);
}

