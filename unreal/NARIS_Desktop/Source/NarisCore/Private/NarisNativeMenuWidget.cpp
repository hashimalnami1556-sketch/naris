#include "NarisNativeMenuWidget.h"
#include "NarisGameModeBase.h"
#include "NarisPlayerCharacter.h"
#include "NarisSaveSubsystem.h"
#include "NarisUserSettingsSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/SizeBox.h"
#include "Components/Spacer.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Fonts/SlateFontInfo.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"

void UNarisNativeMenuWidget::NativeOnInitialized()
{
 Super::NativeOnInitialized();
 SetFlowDirectionPreference(EFlowDirectionPreference::RightToLeft);
 UCanvasPanel* Root=WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(),TEXT("MenuRoot"));
 WidgetTree->RootWidget=Root;
 Backdrop=WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(),TEXT("AshBackdrop"));
 Backdrop->SetBrushColor(FLinearColor(.006f,.009f,.014f,.94f));
 Backdrop->SetHorizontalAlignment(HAlign_Center);
 Backdrop->SetVerticalAlignment(VAlign_Center);
 Backdrop->SetFlowDirectionPreference(EFlowDirectionPreference::RightToLeft);
 UCanvasPanelSlot* BackdropSlot=Root->AddChildToCanvas(Backdrop);
 BackdropSlot->SetAnchors(FAnchors(0.f,0.f,1.f,1.f));
 BackdropSlot->SetOffsets(FMargin(0.f));
 MenuPanel=WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(),TEXT("MenuPanel"));
 MenuPanel->SetFlowDirectionPreference(EFlowDirectionPreference::RightToLeft);
 Backdrop->SetContent(MenuPanel);
 BuildPage(EPage::Main);
 FVector2D ViewportSize(1920.f,1080.f);
 if(GEngine&&GEngine->GameViewport) GEngine->GameViewport->GetViewportSize(ViewportSize);
 const float Scale=FMath::Clamp(ViewportSize.Y/1080.f,.82f,1.2f);
 SetRenderScale(FVector2D(Scale));
 if(InitialFocusButton) InitialFocusButton->SetKeyboardFocus();
}

void UNarisNativeMenuWidget::AddHeading(const FText& Text,int32 FontSize,const FLinearColor& Color)
{
 UTextBlock* Label=WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
 Label->SetText(Text);
 Label->SetColorAndOpacity(FSlateColor(Color));
 Label->SetJustification(ETextJustify::Center);
 Label->SetFlowDirectionPreference(EFlowDirectionPreference::RightToLeft);
 FSlateFontInfo Font;
 Font.Size=FontSize;
 Label->SetFont(Font);
 if(UVerticalBoxSlot* HeadingSlot=MenuPanel->AddChildToVerticalBox(Label)){
  HeadingSlot->SetPadding(FMargin(16.f,4.f));
  HeadingSlot->SetHorizontalAlignment(HAlign_Fill);
 }
}

UButton* UNarisNativeMenuWidget::AddButton(const FText& Text)
{
 USizeBox* Frame=WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
 Frame->SetWidthOverride(520.f);
 Frame->SetHeightOverride(58.f);
 UButton* Button=WidgetTree->ConstructWidget<UButton>(UButton::StaticClass());
 Button->SetBackgroundColor(FLinearColor(.13f,.20f,.23f,1.f));
 Button->SetColorAndOpacity(FLinearColor::White);
 Button->SetIsEnabled(true);
 UTextBlock* Label=WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
 Label->SetText(Text);
 Label->SetColorAndOpacity(FSlateColor(FLinearColor(.98f,.97f,.92f,1.f)));
 Label->SetShadowColorAndOpacity(FLinearColor::Black);
 Label->SetShadowOffset(FVector2D(1.f,1.f));
 Label->SetJustification(ETextJustify::Center);
 Label->SetFlowDirectionPreference(EFlowDirectionPreference::RightToLeft);
 FSlateFontInfo Font;
 Font.Size=22;
 Label->SetFont(Font);
 Button->AddChild(Label);
 Frame->AddChild(Button);
 if(UVerticalBoxSlot* ButtonSlot=MenuPanel->AddChildToVerticalBox(Frame)){
  ButtonSlot->SetPadding(FMargin(8.f,5.f));
  ButtonSlot->SetHorizontalAlignment(HAlign_Center);
 }
 return Button;
}
void UNarisNativeMenuWidget::BuildPage(EPage Page)
{
 CurrentPage=Page;
 MenuPanel->ClearChildren();
 InitialFocusButton=nullptr;
 if(Page==EPage::Main){
  AddHeading(NSLOCTEXT("NARIS","MenuTitle","ملحمة نارس | CALL OF NARIS"),40,FLinearColor(.78f,.61f,.27f,1.f));
  AddHeading(NSLOCTEXT("NARIS","MenuSubtitle","عالم الأساطير | RECORDS OF ASH"),20,FLinearColor(.39f,.82f,.85f,1.f));
  AddHeading(NSLOCTEXT("NARIS","MenuChapter","بوابة الرماد | CHAPTER I"),16,FLinearColor(.64f,.66f,.68f,1.f));
  if(UVerticalBoxSlot* SpacerSlot=MenuPanel->AddChildToVerticalBox(WidgetTree->ConstructWidget<USpacer>())) SpacerSlot->SetPadding(FMargin(0.f,10.f));
  InitialFocusButton=AddButton(NSLOCTEXT("NARIS","NewJourney","ابدأ رحلة جديدة | NEW JOURNEY"));
  InitialFocusButton->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::StartNewJourney);
  UButton* Continue=AddButton(NSLOCTEXT("NARIS","ContinueJourney","متابعة الرحلة | CONTINUE"));
  const bool HasSave=UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Autosave"),0)||UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Auto"),0);
  Continue->SetIsEnabled(HasSave);
  Continue->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ContinueJourney);
  UButton* Settings=AddButton(NSLOCTEXT("NARIS","Settings","الإعدادات | SETTINGS"));
  Settings->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::OpenSettings);
  UButton* Exit=AddButton(NSLOCTEXT("NARIS","Exit","خروج | EXIT"));
  Exit->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ExitGame);
 } else if(Page==EPage::Pause){
  AddHeading(NSLOCTEXT("NARIS","PauseTitle","اللعبة متوقفة | PAUSED"),36,FLinearColor(.78f,.61f,.27f,1.f));
  InitialFocusButton=AddButton(NSLOCTEXT("NARIS","Resume","متابعة اللعب | RESUME"));
  InitialFocusButton->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ResumeGame);
  UButton* Settings=AddButton(NSLOCTEXT("NARIS","PauseSettings","الإعدادات | SETTINGS"));
  Settings->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::OpenSettings);
  UButton* Save=AddButton(NSLOCTEXT("NARIS","QuickSave","حفظ سريع | QUICK SAVE"));
  Save->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::QuickSaveGame);
  UButton* Load=AddButton(NSLOCTEXT("NARIS","QuickLoad","تحميل سريع | QUICK LOAD"));
  Load->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::QuickLoadGame);
  UButton* Exit=AddButton(NSLOCTEXT("NARIS","Exit","خروج | EXIT"));
  Exit->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ExitGame);
 } else if(Page==EPage::GameOver){
  AddHeading(NSLOCTEXT("NARIS","GameOverTitle","انتهت الرحلة | GAME OVER"),38,FLinearColor(.78f,.61f,.27f,1.f));
  AddHeading(NSLOCTEXT("NARIS","GameOverHint","استعد من آخر نقطة حفظ | LOAD CHECKPOINT"),18,FLinearColor(.64f,.66f,.68f,1.f));
  InitialFocusButton=AddButton(NSLOCTEXT("NARIS","RetryCheckpoint","إعادة المحاولة | RETRY CHECKPOINT"));
  InitialFocusButton->SetIsEnabled(UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Auto"),0));
  InitialFocusButton->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::RetryCheckpoint);
  UButton* Exit=AddButton(NSLOCTEXT("NARIS","Exit","خروج | EXIT"));
  Exit->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ExitGame);
 }else{
  AddHeading(NSLOCTEXT("NARIS","SettingsTitle","الإعدادات | SETTINGS"),34,FLinearColor(.78f,.61f,.27f,1.f));
  AddHeading(NSLOCTEXT("NARIS","SettingsHint","تُحفظ التفضيلات تلقائيًا | SAVED AUTOMATICALLY"),16,FLinearColor(.64f,.66f,.68f,1.f));
  UButton* High=AddButton(NSLOCTEXT("NARIS","HighQuality","جودة عالية | HIGH QUALITY"));
  High->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::SetHighQuality);
  UButton* Medium=AddButton(NSLOCTEXT("NARIS","MediumQuality","جودة متوسطة | MEDIUM QUALITY"));
  Medium->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::SetMediumQuality);
  UButton* Subtitles=AddButton(NSLOCTEXT("NARIS","ToggleSubtitles","الترجمة النصية | SUBTITLES"));
  Subtitles->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ToggleSubtitles);
  UButton* Contrast=AddButton(NSLOCTEXT("NARIS","ToggleContrast","التباين العالي | HIGH CONTRAST"));
  Contrast->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ToggleHighContrast);
  InitialFocusButton=AddButton(NSLOCTEXT("NARIS","Back","رجوع | BACK"));
  InitialFocusButton->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::BackToMain);
 }
 if(InitialFocusButton) InitialFocusButton->SetKeyboardFocus();
}
void UNarisNativeMenuWidget::StartNewJourney()
{
 RemoveFromParent();
 if(ANarisGameModeBase* GameMode=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this))) GameMode->StartGame();
}

void UNarisNativeMenuWidget::ContinueJourney()
{
 ANarisGameModeBase* GameMode=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this));
 if(GameMode) GameMode->StartGame();
 APlayerController* Controller=GetOwningPlayer();
 ANarisPlayerCharacter* Player=Controller?Cast<ANarisPlayerCharacter>(Controller->GetPawn()):nullptr;
 if(Player){
  if(UGameInstance* Instance=GetGameInstance()){
   if(UNarisSaveSubsystem* Save=Instance->GetSubsystem<UNarisSaveSubsystem>()){
    const FString SaveSlot=UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Autosave"),0)?TEXT("NARIS_Autosave"):TEXT("NARIS_Auto");
    Save->LoadPlayer(Player,SaveSlot);
   }
  }
 }
 RemoveFromParent();
}
void UNarisNativeMenuWidget::OpenSettings()
{
 bReturnToPause=(CurrentPage==EPage::Pause);
 BuildPage(EPage::Settings);
}

void UNarisNativeMenuWidget::BackToMain()
{
 if(bReturnToPause){bReturnToPause=false;BuildPage(EPage::Pause);return;}
 BuildPage(EPage::Main);
}

void UNarisNativeMenuWidget::ShowPausePage(){BuildPage(EPage::Pause);}
void UNarisNativeMenuWidget::ShowGameOverPage(){BuildPage(EPage::GameOver);}
void UNarisNativeMenuWidget::ResumeGame()
{
 UGameplayStatics::SetGamePaused(this,false);
 if(APlayerController* Controller=GetOwningPlayer()){
  Controller->bShowMouseCursor=false;
  FInputModeGameOnly Mode;
  Controller->SetInputMode(Mode);
 }
 RemoveFromParent();
}
void UNarisNativeMenuWidget::QuickSaveGame()
{
 APlayerController* Controller=GetOwningPlayer();
 ANarisPlayerCharacter* Player=Controller?Cast<ANarisPlayerCharacter>(Controller->GetPawn()):nullptr;
 if(Player) if(UGameInstance* Instance=GetGameInstance())
  if(UNarisSaveSubsystem* Save=Instance->GetSubsystem<UNarisSaveSubsystem>())
   Save->SavePlayer(Player,TEXT("NARIS_Autosave"));
}
void UNarisNativeMenuWidget::QuickLoadGame()
{
 APlayerController* Controller=GetOwningPlayer();
 ANarisPlayerCharacter* Player=Controller?Cast<ANarisPlayerCharacter>(Controller->GetPawn()):nullptr;
 if(!Player) return;
 if(UGameInstance* Instance=GetGameInstance()) if(UNarisSaveSubsystem* Save=Instance->GetSubsystem<UNarisSaveSubsystem>()){
  const FString SaveSlot=UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Autosave"),0)?TEXT("NARIS_Autosave"):TEXT("NARIS_Auto");
  if(UGameplayStatics::DoesSaveGameExist(SaveSlot,0)) Save->LoadPlayer(Player,SaveSlot);
 }
}
void UNarisNativeMenuWidget::RetryCheckpoint()
{
 APlayerController* Controller=GetOwningPlayer();
 ANarisPlayerCharacter* Player=Controller?Cast<ANarisPlayerCharacter>(Controller->GetPawn()):nullptr;
 if(!Player) return;
 if(UGameInstance* Instance=GetGameInstance()) if(UNarisSaveSubsystem* Save=Instance->GetSubsystem<UNarisSaveSubsystem>()){
  if(!UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Auto"),0)||!Save->LoadPlayer(Player,TEXT("NARIS_Auto"))) return;
 }
 UGameplayStatics::SetGamePaused(this,false);
 Controller->bShowMouseCursor=false;
 FInputModeGameOnly Mode;
 Controller->SetInputMode(Mode);
 RemoveFromParent();
}
void UNarisNativeMenuWidget::ExitGame()
{
 if(APlayerController* Controller=GetOwningPlayer())
  UKismetSystemLibrary::QuitGame(this,Controller,EQuitPreference::Quit,false);
}
void UNarisNativeMenuWidget::SetHighQuality()
{
 if(UGameInstance* Instance=GetGameInstance())
  if(UNarisUserSettingsSubsystem* Settings=Instance->GetSubsystem<UNarisUserSettingsSubsystem>())
   Settings->ApplyQualityPreset(3);
}

void UNarisNativeMenuWidget::SetMediumQuality()
{
 if(UGameInstance* Instance=GetGameInstance())
  if(UNarisUserSettingsSubsystem* Settings=Instance->GetSubsystem<UNarisUserSettingsSubsystem>())
   Settings->ApplyQualityPreset(2);
}
void UNarisNativeMenuWidget::ToggleSubtitles()
{
 if(UGameInstance* Instance=GetGameInstance())
  if(UNarisUserSettingsSubsystem* Settings=Instance->GetSubsystem<UNarisUserSettingsSubsystem>()){
   FNarisAccessibilitySettings Values=Settings->GetAccessibility();
   Values.bSubtitles=!Values.bSubtitles;
   Settings->SetAccessibility(Values);
  }
}
void UNarisNativeMenuWidget::ToggleHighContrast()
{
 if(UGameInstance* Instance=GetGameInstance())
  if(UNarisUserSettingsSubsystem* Settings=Instance->GetSubsystem<UNarisUserSettingsSubsystem>()){
   FNarisAccessibilitySettings Values=Settings->GetAccessibility();
   Values.bHighContrastHUD=!Values.bHighContrastHUD;
   Settings->SetAccessibility(Values);
  }
}