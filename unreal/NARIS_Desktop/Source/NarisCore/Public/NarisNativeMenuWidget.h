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
 virtual void NativeConstruct() override;

private:
 enum class EPage : uint8 { Main, Settings };
 EPage CurrentPage=EPage::Main;
 UPROPERTY() TObjectPtr<UBorder> Backdrop;
 UPROPERTY() TObjectPtr<UVerticalBox> MenuPanel;
 UPROPERTY() TObjectPtr<UButton> InitialFocusButton;

 void BuildPage(EPage Page);
 UButton* AddButton(const FText& Label);
 void AddHeading(const FText& Text, int32 FontSize, const FLinearColor& Color);
 UFUNCTION() void StartNewJourney();
 UFUNCTION() void ContinueJourney();
 UFUNCTION() void OpenSettings();
 UFUNCTION() void BackToMain();
 UFUNCTION() void ExitGame();
 UFUNCTION() void SetHighQuality();
 UFUNCTION() void SetMediumQuality();
 UFUNCTION() void ToggleSubtitles();
 UFUNCTION() void ToggleHighContrast();
};