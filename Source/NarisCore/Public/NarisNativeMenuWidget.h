#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "NarisNativeMenuWidget.generated.h"

class UBorder;
class UButton;
class UTextBlock;
class UVerticalBox;

UCLASS()
class NARISCORE_API UNarisNativeMenuWidget : public UUserWidget
{
 GENERATED_BODY()
public:
 virtual void NativeOnInitialized() override;
 void ShowPausePage();
 void ShowGameOverPage();

private:
 enum class EPage : uint8 { Main, Worlds, Settings, Pause, GameOver };
 EPage CurrentPage=EPage::Main;
 bool bReturnToPause=false;
 UPROPERTY() TObjectPtr<UBorder> Backdrop;
 UPROPERTY() TObjectPtr<UVerticalBox> MenuPanel;
 UPROPERTY() TObjectPtr<UButton> InitialFocusButton;

 void BuildPage(EPage Page);
 UButton* AddButton(const FText& Label);
 void AddHeading(const FText& Text, int32 FontSize, const FLinearColor& Color);
 UFUNCTION() void StartNewJourney();
 UFUNCTION() void OpenWorldSelection();
 UFUNCTION() void TravelToAshenForest();
 UFUNCTION() void TravelToExpandedForest();
 void TravelToWorld(const TCHAR* PackagePath);
 UFUNCTION() void ContinueJourney();
 UFUNCTION() void OpenSettings();
 UFUNCTION() void BackToMain();
 UFUNCTION() void ExitGame();
 UFUNCTION() void SetHighQuality();
 UFUNCTION() void SetMediumQuality();
 UFUNCTION() void ToggleSubtitles();
 UFUNCTION() void ToggleHighContrast();
 UFUNCTION() void ResumeGame();
 UFUNCTION() void QuickSaveGame();
 UFUNCTION() void QuickLoadGame();
 UFUNCTION() void RetryCheckpoint();
};
