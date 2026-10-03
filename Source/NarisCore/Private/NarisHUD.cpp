#include "NarisHUD.h"
#include "NarisPlayerCharacter.h"
#include "NarisGameModeBase.h"
#include "NarisSaveSubsystem.h"
#include "NarisUserSettingsSubsystem.h"
#include "NarisBossCharacter.h"
#include "NarisAshGateActor.h"
#include "NarisWorldStateSubsystem.h"
#include "NarisBossPhaseComponent.h"
#include "NarisVitalsComponent.h"
#include "NarisQuestSubsystem.h"
#include "NarisNarrativeTypes.h"
#include "Engine/Canvas.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/KismetSystemLibrary.h"
#include "NarisNativeMenuWidget.h"

void ANarisHUD::BeginPlay()
{
 Super::BeginPlay();
 ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this));
 if(GM&&!GM->IsGameStarted()){
  if(APlayerController* PC=GetOwningPlayerController()){
   FrontEndWidget=CreateWidget<UNarisNativeMenuWidget>(PC,UNarisNativeMenuWidget::StaticClass());
   if(FrontEndWidget){
    FrontEndWidget->AddToViewport(100);
    UE_LOG(LogTemp,Display,TEXT("NARIS_UI_MAIN_MENU READY RTL=1 Buttons=5 WorldSelection=1"));
   }else{
    UE_LOG(LogTemp,Error,TEXT("NARIS_UI_MAIN_MENU FAIL CreateWidget"));
   }
  }
 }
 if(ANarisPlayerCharacter* Player=Cast<ANarisPlayerCharacter>(GetOwningPawn()))
  if(Player->Vitals) Player->Vitals->OnDeath.AddDynamic(this,&ANarisHUD::HandlePlayerDeath);
}

void ANarisHUD::HandlePlayerDeath()
{
 UGameplayStatics::SetGamePaused(this,true);
 if(APlayerController* PC=GetOwningPlayerController()){
  PC->bShowMouseCursor=true;
  FInputModeGameAndUI Mode;
  Mode.SetHideCursorDuringCapture(false);
  PC->SetInputMode(Mode);
  if(!FrontEndWidget) FrontEndWidget=CreateWidget<UNarisNativeMenuWidget>(PC,UNarisNativeMenuWidget::StaticClass());
  if(FrontEndWidget){FrontEndWidget->ShowGameOverPage();FrontEndWidget->AddToViewport(100);}
 }
}

bool ANarisHUD::ShouldDismissFrontEnd(bool bGameStarted, bool bGamePaused)
{
 return bGameStarted && !bGamePaused;
}

void ANarisHUD::DrawHUD()
{
 Super::DrawHUD(); if(!Canvas) return;
 ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this));
 if(GM&&!GM->IsGameStarted()){
  if(FrontEndWidget&&FrontEndWidget->IsInViewport()) return;
  const float CX=Canvas->ClipX*.5f,CY=Canvas->ClipY*.5f;
  DrawRect(FLinearColor(.004f,.006f,.010f,1.f),0,0,Canvas->ClipX,Canvas->ClipY);
  DrawRect(FLinearColor(.025f,.050f,.060f,.36f),0,0,Canvas->ClipX,Canvas->ClipY*.38f);
  DrawRect(FLinearColor(.12f,.055f,.018f,.26f),0,Canvas->ClipY*.70f,Canvas->ClipX,Canvas->ClipY*.30f);
  const float PW=FMath::Min(980.f,Canvas->ClipX*.82f),PH=FMath::Min(580.f,Canvas->ClipY*.78f);
  const float PX=CX-PW*.5f,PY=CY-PH*.5f;
  DrawRect(FLinearColor(.010f,.016f,.024f,.94f),PX,PY,PW,PH);
  DrawRect(FLinearColor(.62f,.42f,.12f,1.f),PX,PY,PW,2.f);
  DrawRect(FLinearColor(.12f,.55f,.62f,.65f),PX,PY+PH-2.f,PW,2.f);
  DrawText(TEXT("NARIS"),FLinearColor(.86f,.70f,.34f,1.f),PX+54.f,PY+52.f,nullptr,2.8f);
  DrawText(TEXT("CALL OF NARIS"),FLinearColor(.92f,.94f,.96f,1.f),PX+58.f,PY+132.f,nullptr,1.45f);
  DrawText(TEXT("RECORDS OF ASH"),FLinearColor(.42f,.86f,.92f,1.f),PX+60.f,PY+178.f,nullptr,1.0f);
  DrawText(TEXT("ASHEN FOREST  /  CHAPTER I"),FLinearColor(.58f,.62f,.68f,1.f),PX+60.f,PY+224.f,nullptr,.82f);
  const float MX=PX+PW-390.f,MW=320.f,MH=54.f;
  if(FrontEndPage==0){
   const bool bContinue=UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Autosave"),0)||UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Auto"),0);
   const TCHAR* Labels[4]={TEXT("NEW JOURNEY"),TEXT("CONTINUE"),TEXT("SETTINGS"),TEXT("EXIT")};
   const FName Names[4]={FName("StartGame"),FName("ContinueGame"),FName("OpenSettings"),FName("ExitGame")};
   for(int32 i=0;i<4;++i){const float MY=PY+150.f+i*70.f;const bool Enabled=(i!=1)||bContinue;DrawRect(FLinearColor(.040f,.060f,.075f,Enabled?1.f:.45f),MX,MY,MW,MH);DrawRect(i==0?FLinearColor(.46f,.90f,.95f,1.f):FLinearColor(.28f,.31f,.36f,1.f),MX,MY,MW,2.f);DrawText(Labels[i],Enabled?FLinearColor(.94f,.96f,.98f,1.f):FLinearColor(.35f,.38f,.42f,1.f),MX+34.f,MY+16.f,nullptr,1.05f);if(Enabled)AddHitBox(FVector2D(MX,MY),FVector2D(MW,MH),Names[i],true,i);}
   DrawText(TEXT("ENTER / A  START     ESC  EXIT"),FLinearColor(.46f,.50f,.56f,1.f),MX,PY+PH-58.f,nullptr,.76f);
  }else{
   DrawText(TEXT("SETTINGS"),FLinearColor(.86f,.70f,.34f,1.f),MX,PY+118.f,nullptr,1.35f);
   struct FRow{const TCHAR* Label;FName Name;};const FRow Rows[]={{TEXT("QUALITY: HIGH"),FName("QualityHigh")},{TEXT("QUALITY: MEDIUM"),FName("QualityMedium")},{TEXT("TOGGLE SUBTITLES"),FName("ToggleSubtitles")},{TEXT("TOGGLE HIGH CONTRAST"),FName("ToggleContrast")},{TEXT("BACK"),FName("BackMain")}};
   for(int32 i=0;i<5;++i){const float MY=PY+175.f+i*58.f;DrawRect(FLinearColor(.040f,.060f,.075f,1.f),MX,MY,MW,46.f);DrawText(Rows[i].Label,FLinearColor(.92f,.94f,.96f,1.f),MX+24.f,MY+13.f,nullptr,.92f);AddHitBox(FVector2D(MX,MY),FVector2D(MW,46.f),Rows[i].Name,true,i);}
  }
  DrawText(TEXT("NARIS STUDIOS  |  ALNAMI COMPANY"),FLinearColor(.30f,.33f,.38f,1.f),PX+58.f,PY+PH-42.f,nullptr,.70f);
  return;
 }
 if(ShouldDismissFrontEnd(!GM || GM->IsGameStarted(), UGameplayStatics::IsGamePaused(this)))
  if(FrontEndWidget && FrontEndWidget->IsInViewport()) FrontEndWidget->RemoveFromParent();
 ANarisPlayerCharacter* P=Cast<ANarisPlayerCharacter>(GetOwningPawn()); if(!P||!P->Vitals) return;
 if(UGameplayStatics::IsGamePaused(this)){
  if(!FrontEndWidget||!FrontEndWidget->IsInViewport()){
   if(APlayerController* PC=GetOwningPlayerController()){
    if(!FrontEndWidget) FrontEndWidget=CreateWidget<UNarisNativeMenuWidget>(PC,UNarisNativeMenuWidget::StaticClass());
    if(FrontEndWidget){FrontEndWidget->ShowPausePage();FrontEndWidget->AddToViewport(100);}
   }
  }
  return;
 }
 const float S=FMath::Clamp(FMath::Min(Canvas->ClipX/1600.f,Canvas->ClipY/900.f),.65f,1.35f);
 const FLinearColor Gold(.79f,.61f,.29f,.98f),Ivory(.91f,.88f,.77f,.98f),Ash(.025f,.039f,.051f,.80f),Ice(.23f,.69f,.92f,.96f);
 const float HX=24.f*S, HY=30.f*S, HW=314.f*S;
 const float H=FMath::Clamp(P->Vitals->Health/FMath::Max(1.f,P->Vitals->MaxHealth),0.f,1.f);
 const float AetherFill=FMath::Clamp(P->Vitals->Energy/FMath::Max(1.f,P->Vitals->MaxEnergy),0.f,1.f);
 // Actual player data: portrait medallion, HP and Aether (no fictional party stats).
 DrawRect(Ash,HX,HY,HW,132.f*S);
 DrawRect(Gold,HX,HY,HW,2.f*S);
 DrawRect(Gold,HX+14.f*S,HY+17.f*S,58.f*S,60.f*S);
 DrawRect(FLinearColor(.045f,.060f,.080f,1.f),HX+17.f*S,HY+20.f*S,52.f*S,54.f*S);
 DrawText(TEXT("N"),Gold,HX+32.f*S,HY+30.f*S,nullptr,1.25f*S);
 DrawText(TEXT("NARIS  |  ASHEN VESSEL"),Ivory,HX+86.f*S,HY+18.f*S,nullptr,.92f*S);
 DrawText(FString::Printf(TEXT("HP  %.0f / %.0f"),P->Vitals->Health,P->Vitals->MaxHealth),Ivory,HX+86.f*S,HY+46.f*S,nullptr,.75f*S);
 DrawRect(FLinearColor(.09f,.10f,.11f,.98f),HX+86.f*S,HY+68.f*S,210.f*S,9.f*S);
 DrawRect(FLinearColor(.70f,.12f,.10f,.98f),HX+86.f*S,HY+68.f*S,210.f*S*H,9.f*S);
 DrawRect(FLinearColor(.05f,.08f,.10f,.98f),HX+86.f*S,HY+87.f*S,210.f*S,6.f*S);
 DrawRect(Ice,HX+86.f*S,HY+87.f*S,210.f*S*AetherFill,6.f*S);
 DrawText(TEXT("AETHER / RESONANCE"),FLinearColor(.50f,.76f,.83f,.95f),HX+86.f*S,HY+102.f*S,nullptr,.64f*S);
 // The current build implements one companion; do not invent three additional party members.
 DrawRect(Ash,HX,HY+143.f*S,HW,49.f*S);
 DrawRect(Ice,HX+10.f*S,HY+155.f*S,25.f*S,25.f*S);
 DrawText(TEXT("W"),FLinearColor(.04f,.08f,.11f,1.f),HX+16.f*S,HY+160.f*S,nullptr,.63f*S);
 DrawText(TEXT("CELESTIAL WOLF  |  COMPANION"),Ivory,HX+45.f*S,HY+157.f*S,nullptr,.78f*S);
 // Actual 2D radar: projects gameplay coordinates, not a decorative fake screenshot.
 const float MW=202.f*S,MapX=Canvas->ClipX-MW-26.f*S,MY=25.f*S;
 DrawRect(Ash,MapX,MY,MW,234.f*S);
 DrawRect(Gold,MapX,MY,MW,2.f*S);
 DrawText(TEXT("ASHEN DEPTHS"),Gold,MapX+18.f*S,MY+12.f*S,nullptr,.90f*S);
 const float RX=MapX+18.f*S,RY=MY+46.f*S,RW=166.f*S;
 DrawRect(FLinearColor(.055f,.062f,.070f,.95f),RX,RY,RW,RW);
 for(int32 Grid=1;Grid<4;++Grid){
  const float O=RW*(float(Grid)/4.f);
  DrawLine(RX+O,RY,RX+O,RY+RW,FLinearColor(.20f,.24f,.24f,.44f),1.f);
  DrawLine(RX,RY+O,RX+RW,RY+O,FLinearColor(.20f,.24f,.24f,.44f),1.f);
 }
 const FVector PlayerPos=P->GetActorLocation();
 const float PX=RX+RW*.5f,PY=RY+RW*.5f;
 DrawRect(Gold,PX-5.f*S,PY-5.f*S,10.f*S,10.f*S);
 DrawText(TEXT("N"),Ivory,RX+RW*.5f-4.f*S,RY+5.f*S,nullptr,.69f*S);
 TArray<AActor*> MapBosses;
 UGameplayStatics::GetAllActorsOfClass(this,ANarisBossCharacter::StaticClass(),MapBosses);
 for(AActor* M:MapBosses){
  if(!M)continue;
  const FVector D=M->GetActorLocation()-PlayerPos;
  const float TX=FMath::Clamp(PX+(D.Y/2900.f)*RW,RX+6.f*S,RX+RW-6.f*S);
  const float TY=FMath::Clamp(PY-(D.X/2900.f)*RW,RY+6.f*S,RY+RW-6.f*S);
  DrawRect(FLinearColor(.95f,.18f,.12f,1.f),TX-4.f*S,TY-4.f*S,8.f*S,8.f*S);
  break;
 }
 if(AActor* Gate=UGameplayStatics::GetActorOfClass(this,ANarisAshGateActor::StaticClass())){
  const FVector Delta=Gate->GetActorLocation()-PlayerPos;
  const float TX=FMath::Clamp(PX+(Delta.Y/2900.f)*RW,RX+6.f*S,RX+RW-6.f*S);
  const float TY=FMath::Clamp(PY-(Delta.X/2900.f)*RW,RY+6.f*S,RY+RW-6.f*S);
  const bool bGateOpen=Cast<ANarisAshGateActor>(Gate)->IsGateOpen();
  DrawRect(bGateOpen?Ice:Gold,TX-5.f*S,TY-5.f*S,10.f*S,10.f*S);
  DrawText(FString::Printf(TEXT("GATE  %.0fm  %s"),Delta.Size()/100.f,bGateOpen?TEXT("OPEN"):TEXT("SEALED")),bGateOpen?Ice:Gold,RX,MY+218.f*S,nullptr,.57f*S);
 }else DrawText(TEXT("ASHEN DEPTHS / NORTH"),FLinearColor(.64f,.68f,.72f,1.f),RX,MY+218.f*S,nullptr,.58f*S);
 // Accessible PC combat action chips: labels reflect real bound input actions.
 const float Y=Canvas->ClipY-118.f*S;
 struct FChip{const TCHAR* Label;const TCHAR* Key;};
 const FChip Chips[]={{TEXT("STRIKE"),TEXT("LMB")},{TEXT("PARRY"),TEXT("RMB")},{TEXT("DODGE"),TEXT("SHIFT")},{TEXT("FOCUS"),TEXT("R")}};
 const float CW=86.f*S;
 const float FirstX=Canvas->ClipX-4.f*CW-37.f*S;
 for(int32 I=0;I<4;++I){
  const float X=FirstX+I*(CW+5.f*S);
  DrawRect(FLinearColor(.028f,.038f,.049f,.77f),X,Y,CW,72.f*S);
  DrawRect(I==3?Ice:Gold,X,Y,CW,2.f*S);
  DrawText(Chips[I].Label,Ivory,X+9.f*S,Y+18.f*S,nullptr,.65f*S);
  DrawText(Chips[I].Key,I==3?Ice:Gold,X+12.f*S,Y+43.f*S,nullptr,.75f*S);
 }
 DrawRect(FLinearColor(.013f,.021f,.028f,.67f),Canvas->ClipX*.30f,Canvas->ClipY-37.f*S,Canvas->ClipX*.40f,28.f*S);
 DrawText(TEXT("CALL OF NARIS  |  RECORDS OF ASH"),FLinearColor(.69f,.71f,.71f,.87f),Canvas->ClipX*.32f,Canvas->ClipY-32.f*S,nullptr,.68f*S);

 if(AActor* Locked=P->GetLockTarget()){
  if(APlayerController* PC=GetOwningPlayerController()){
   FVector2D Screen;
   if(PC->ProjectWorldLocationToScreen(Locked->GetActorLocation()+FVector(0,0,135.f),Screen,true)){
    const float R=18.f;
    const FLinearColor Rune(.82f,.50f,.18f,.88f);
    DrawRect(Rune,Screen.X-R,Screen.Y-R,10.f,2.f); DrawRect(Rune,Screen.X+R-10.f,Screen.Y-R,10.f,2.f);
    DrawRect(Rune,Screen.X-R,Screen.Y+R,10.f,2.f); DrawRect(Rune,Screen.X+R-10.f,Screen.Y+R,10.f,2.f);
   }
  }
 }

 TArray<AActor*> Bosses;
 UGameplayStatics::GetAllActorsOfClass(this,ANarisBossCharacter::StaticClass(),Bosses);
 for(AActor* A:Bosses){
  ANarisBossCharacter* Boss=Cast<ANarisBossCharacter>(A);
  if(!Boss||!Boss->Vitals||!Boss->Vitals->IsAlive()) continue;
  const float BW=FMath::Min(680.f,Canvas->ClipX*.46f),BX=(Canvas->ClipX-BW)*.5f,BY=54.f;
  const float Ratio=FMath::Clamp(Boss->Vitals->Health/Boss->Vitals->MaxHealth,0.f,1.f);
  const int32 Phase=Boss->Phase?Boss->Phase->CurrentPhase:1;
  DrawText(TEXT("GATE WARDEN"),FLinearColor(.82f,.72f,.56f,.92f),BX,BY-24.f,nullptr,.86f);
  DrawRect(FLinearColor(.015f,.014f,.018f,.62f),BX,BY,BW,6.f);
  DrawRect(FLinearColor(.52f,.075f,.045f,.94f),BX,BY,BW*Ratio,6.f);
  for(int32 Mark=1;Mark<3;++Mark){
   const float MX=BX+BW*(float(Mark)/3.f);
   DrawRect(FLinearColor(.72f,.54f,.30f,Phase>Mark?.86f:.24f),MX-1.f,BY-3.f,2.f,12.f);
  }
  break;
 }

 if(UGameInstance* G=P->GetGameInstance()){
  if(UNarisQuestSubsystem* Q=G->GetSubsystem<UNarisQuestSubsystem>()){
   const FName Quest(TEXT("Q_AshenGate"));
   const int32 Shards=Q->GetObjectiveProgress(Quest,FName("AshShard"),ENarisNarrativeEventType::ItemAcquired);
   const int32 Beasts=Q->GetObjectiveProgress(Quest,FName("BoneBeast"),ENarisNarrativeEventType::EnemyDefeated);
   const int32 Boss=Q->GetObjectiveProgress(Quest,FName("GateWarden"),ENarisNarrativeEventType::BossDefeated);
   const bool Done=Q->IsQuestCompleted(Quest);
   const FString QuestText=Done?FString(TEXT("ASHEN GATE OPEN")):FString::Printf(TEXT("ASHEN GATE  |  SHARDS %d/3  |  BEASTS %d/3  |  WARDEN %d/1"),FMath::Min(Shards,3),FMath::Min(Beasts,3),FMath::Min(Boss,1));
   const FLinearColor QuestColor=Done?FLinearColor(.2f,1.f,.5f,1.f):FLinearColor(1.f,.82f,.25f,1.f);
   const float QS=FMath::Clamp(FMath::Min(Canvas->ClipX/1600.f,Canvas->ClipY/900.f),.65f,1.35f);
   const float QX=24.f*QS,QY=242.f*QS,QW=314.f*QS;
   DrawRect(FLinearColor(.023f,.031f,.041f,.79f),QX,QY,QW,100.f*QS);
   DrawRect(FLinearColor(.79f,.60f,.26f,.95f),QX,QY,4.f*QS,100.f*QS);
   bool bGateEntered=false;
   if(UNarisWorldStateSubsystem* State=G->GetSubsystem<UNarisWorldStateSubsystem>())
    bGateEntered=State->GetFlag(TEXT("AshenGateEntered"));
   DrawText(bGateEntered?TEXT("BELL MARSH  |  CHAPTER II"):TEXT("ASHEN GATE  |  CHAPTER I"),QuestColor,QX+17.f*QS,QY+12.f*QS,nullptr,.91f*QS);
   DrawText(bGateEntered?TEXT("NEXT CHAPTER UNLOCKED"):(Done?TEXT("CROSS THE OPEN GATE"):TEXT("DEFEAT THE GATE WARDEN")),FLinearColor(.88f,.87f,.78f,1.f),QX+17.f*QS,QY+40.f*QS,nullptr,.75f*QS);
   DrawText(FString::Printf(TEXT("SHARDS %d/3   BEASTS %d/3   WARDEN %d/1"),FMath::Min(Shards,3),FMath::Min(Beasts,3),FMath::Min(Boss,1)),FLinearColor(.61f,.72f,.77f,1.f),QX+17.f*QS,QY+70.f*QS,nullptr,.66f*QS);
  }
 }
}
void ANarisHUD::NotifyHitBoxClick(FName BoxName)
{
 Super::NotifyHitBoxClick(BoxName);
 ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this));
 if(BoxName==FName("StartGame")){if(GM)GM->StartGame();return;}
 if(BoxName==FName("ContinueGame")){
  if(GM)GM->StartGame();
  if(ANarisPlayerCharacter* P=Cast<ANarisPlayerCharacter>(GetOwningPawn())) if(UGameInstance* G=P->GetGameInstance()) if(UNarisSaveSubsystem* S=G->GetSubsystem<UNarisSaveSubsystem>()){
   if(UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Autosave"),0))S->LoadPlayer(P,TEXT("NARIS_Autosave"));
   else if(UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Auto"),0))S->LoadPlayer(P,TEXT("NARIS_Auto"));
  }
  return;
 }
 if(BoxName==FName("OpenSettings")){FrontEndPage=1;return;}
 if(BoxName==FName("BackMain")){FrontEndPage=0;return;}
 if(BoxName==FName("ExitGame")){if(APlayerController* PC=GetOwningPlayerController())UKismetSystemLibrary::QuitGame(this,PC,EQuitPreference::Quit,false);return;}
 if(UGameInstance* G=GetGameInstance()) if(UNarisUserSettingsSubsystem* S=G->GetSubsystem<UNarisUserSettingsSubsystem>()){
  if(BoxName==FName("QualityHigh")){S->ApplyQualityPreset(3);return;}
  if(BoxName==FName("QualityMedium")){S->ApplyQualityPreset(2);return;}
  FNarisAccessibilitySettings A=S->GetAccessibility();
  if(BoxName==FName("ToggleSubtitles")){A.bSubtitles=!A.bSubtitles;S->SetAccessibility(A);return;}
  if(BoxName==FName("ToggleContrast")){A.bHighContrastHUD=!A.bHighContrastHUD;S->SetAccessibility(A);return;}
 }
}

