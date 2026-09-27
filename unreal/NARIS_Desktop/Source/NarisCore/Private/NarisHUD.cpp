#include "NarisHUD.h"
#include "NarisPlayerCharacter.h"
#include "NarisGameModeBase.h"
#include "NarisSaveSubsystem.h"
#include "NarisUserSettingsSubsystem.h"
#include "NarisBossCharacter.h"
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
    UE_LOG(LogTemp,Display,TEXT("NARIS_UI_MAIN_MENU READY RTL=1 Buttons=4"));
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
 const float X=48.f,Y=48.f,W=320.f,H=18.f;

 DrawRect(FLinearColor(.025f,.025f,.035f,.88f),X-6,Y-6,W+12,H+12);
 DrawRect(FLinearColor(.75f,.08f,.04f,1.f),X,Y,W*FMath::Clamp(P->Vitals->Health/P->Vitals->MaxHealth,0.f,1.f),H);
 DrawText(FString::Printf(TEXT("ASHEN VESSEL  HP %.0f / %.0f"),P->Vitals->Health,P->Vitals->MaxHealth),FLinearColor::White,X,Y+25.f,nullptr,1.f);

 DrawRect(FLinearColor(.025f,.025f,.035f,.88f),X-6,Y+50.f,W+12,H+12);
 DrawRect(FLinearColor(.08f,.55f,.95f,1.f),X,Y+56.f,W*FMath::Clamp(P->Vitals->Energy/P->Vitals->MaxEnergy,0.f,1.f),H);
 DrawText(FString::Printf(TEXT("AETHER  %.0f / %.0f"),P->Vitals->Energy,P->Vitals->MaxEnergy),FLinearColor(.75f,.9f,1.f,1.f),X,Y+81.f,nullptr,1.f);

 if(AActor* Locked=P->GetLockTarget()){
  if(APlayerController* PC=GetOwningPlayerController()){
   FVector2D Screen;
   if(PC->ProjectWorldLocationToScreen(Locked->GetActorLocation()+FVector(0,0,135.f),Screen,true)){
    DrawText(TEXT("< LOCK >"),FLinearColor(1.f,.48f,.04f,1.f),Screen.X-34.f,Screen.Y-12.f,nullptr,1.05f);
   }
  }
 }

 TArray<AActor*> Bosses;
 UGameplayStatics::GetAllActorsOfClass(this,ANarisBossCharacter::StaticClass(),Bosses);
 for(AActor* A:Bosses){
  ANarisBossCharacter* Boss=Cast<ANarisBossCharacter>(A);
  if(!Boss||!Boss->Vitals||!Boss->Vitals->IsAlive()) continue;
  const float BW=FMath::Min(620.f,Canvas->ClipX*.52f),BH=20.f,BX=(Canvas->ClipX-BW)*.5f,BY=38.f;
  const float Ratio=FMath::Clamp(Boss->Vitals->Health/Boss->Vitals->MaxHealth,0.f,1.f);
  DrawRect(FLinearColor(.015f,.015f,.02f,.92f),BX-8.f,BY-8.f,BW+16.f,BH+16.f);
  DrawRect(FLinearColor(.48f,.03f,.055f,1.f),BX,BY,BW*Ratio,BH);
  const int32 Phase=Boss->Phase?Boss->Phase->CurrentPhase:1;
  DrawText(FString::Printf(TEXT("GATE WARDEN   PHASE %d   %.0f / %.0f"),Phase,Boss->Vitals->Health,Boss->Vitals->MaxHealth),FLinearColor(1.f,.78f,.52f,1.f),BX+BW*.5f-125.f,BY+26.f,nullptr,1.f);
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
   DrawRect(FLinearColor(.02f,.02f,.03f,.74f),X-8.f,Y+126.f,520.f,32.f);
   DrawText(QuestText,QuestColor,X,Y+134.f,nullptr,.92f);
  }
 }
 DrawText(TEXT("LMB COMBO   RMB PARRY   R RESONANCE   Q LOCK   SHIFT DODGE   ESC MENU   F5 SAVE   F9 LOAD"),FLinearColor(.82f,.84f,.88f,1.f),48.f,Canvas->ClipY-46.f,nullptr,.82f);
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
