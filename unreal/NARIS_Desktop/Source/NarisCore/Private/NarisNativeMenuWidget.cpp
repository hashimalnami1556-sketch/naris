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

void UNarisNativeMenuWidget::NativeConstruct()
{
 Super::NativeConstruct();
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
 Button->SetBackgroundColor(FLinearColor(.045f,.067f,.079f,1.f));
 Button->SetColorAndOpacity(FLinearColor::White);
 Button->SetIsEnabled(true);
 UTextBlock* Label=WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
 Label->SetText(Text);
 Label->SetColorAndOpacity(FSlateColor(FLinearColor(.91f,.90f,.86f,1.f)));
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
  AddHeading(NSLOCTEXT("NARIS","MenuTitle","ملحمة نارس"),40,FLinearColor(.78f,.61f,.27f,1.f));
  AddHeading(NSLOCTEXT("NARIS","MenuSubtitle","عالم الأساطير"),20,FLinearColor(.39f,.82f,.85f,1.f));
  AddHeading(NSLOCTEXT("NARIS","MenuChapter","بوابة الرماد  ·  الفصل الأول"),16,FLinearColor(.64f,.66f,.68f,1.f));
  if(UVerticalBoxSlot* SpacerSlot=MenuPanel->AddChildToVerticalBox(WidgetTree->ConstructWidget<USpacer>())) SpacerSlot->SetPadding(FMargin(0.f,10.f));
  InitialFocusButton=AddButton(NSLOCTEXT("NARIS","NewJourney","ابدأ رحلة جديدة"));
  InitialFocusButton->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::StartNewJourney);
  UButton* Continue=AddButton(NSLOCTEXT("NARIS","ContinueJourney","متابعة الرحلة"));
  const bool HasSave=UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Autosave"),0)||UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Auto"),0);
  Continue->SetIsEnabled(HasSave);
  Continue->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ContinueJourney);
  UButton* Settings=AddButton(NSLOCTEXT("NARIS","Settings","الإعدادات"));
  Settings->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::OpenSettings);
  UButton* Exit=AddButton(NSLOCTEXT("NARIS","Exit","خروج"));
  Exit->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ExitGame);
 }else{
  AddHeading(NSLOCTEXT("NARIS","SettingsTitle","الإعدادات"),34,FLinearColor(.78f,.61f,.27f,1.f));
  AddHeading(NSLOCTEXT("NARIS","SettingsHint","تُحفظ تفضيلات إمكانية الوصول تلقائيًا"),16,FLinearColor(.64f,.66f,.68f,1.f));
  UButton* High=AddButton(NSLOCTEXT("NARIS","HighQuality","جودة الرسوم: عالية"));
  High->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::SetHighQuality);
  UButton* Medium=AddButton(NSLOCTEXT("NARIS","MediumQuality","جودة الرسوم: متوسطة"));
  Medium->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::SetMediumQuality);
  UButton* Subtitles=AddButton(NSLOCTEXT("NARIS","ToggleSubtitles","تبديل الترجمة النصية"));
  Subtitles->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ToggleSubtitles);
  UButton* Contrast=AddButton(NSLOCTEXT("NARIS","ToggleContrast","تبديل التباين العالي"));
  Contrast->OnClicked.AddDynamic(this,&UNarisNativeMenuWidget::ToggleHighContrast);
  InitialFocusButton=AddButton(NSLOCTEXT("NARIS","Back","رجوع"));
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
 BuildPage(EPage::Settings);
}

void UNarisNativeMenuWidget::BackToMain()
{
 BuildPage(EPage::Main);
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