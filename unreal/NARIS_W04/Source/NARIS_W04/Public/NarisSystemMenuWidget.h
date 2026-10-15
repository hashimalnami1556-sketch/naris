#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/Button.h"
#include "NarisSystemMenuWidget.generated.h"

class ANarisPlayerController;
class UBorder;
class UTextBlock;
class UVerticalBox;
class UHorizontalBox;

UCLASS()
class NARIS_W04_API UNarisMenuRowButton : public UButton
{
    GENERATED_BODY()

public:
    void Configure(ANarisPlayerController* InController, int32 InIndex);

private:
    UFUNCTION()
    void HandleClicked();

    UFUNCTION()
    void HandleHovered();

    UPROPERTY(Transient)
    TObjectPtr<ANarisPlayerController> Controller;

    int32 MenuIndex = 0;
};

UCLASS()
class NARIS_W04_API UNarisSystemMenuWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
    static constexpr int32 MaxRows = 17;

    void BuildInterface();
    void RefreshInterface();
    FString ResolveIcon(int32 Index) const;
    UTextBlock* MakeText(const FString& Value, int32 Size, const FLinearColor& Color) const;
    UBorder* MakePanel(const FLinearColor& Color, const FMargin& Padding) const;

    UPROPERTY(Transient)
    TObjectPtr<ANarisPlayerController> Controller;

    UPROPERTY(Transient)
    TObjectPtr<UBorder> BackdropPanel;

    UPROPERTY(Transient)
    TObjectPtr<UBorder> MenuPanelRef;

    UPROPERTY(Transient)
    TObjectPtr<UBorder> StatusPanelRef;

    UPROPERTY(Transient)
    TObjectPtr<UTextBlock> BrandText;

    UPROPERTY(Transient)
    TObjectPtr<UTextBlock> ContextText;

    UPROPERTY(Transient)
    TObjectPtr<UTextBlock> StatusTitleText;

    UPROPERTY(Transient)
    TObjectPtr<UTextBlock> StatusBodyText;

    UPROPERTY(Transient)
    TObjectPtr<UTextBlock> FooterText;

    UPROPERTY(Transient)
    TArray<TObjectPtr<UNarisMenuRowButton>> RowButtons;

    UPROPERTY(Transient)
    TArray<TObjectPtr<UBorder>> RowPanels;

    UPROPERTY(Transient)
    TArray<TObjectPtr<UBorder>> IconPlates;

    UPROPERTY(Transient)
    TArray<TObjectPtr<UTextBlock>> IconTexts;

    UPROPERTY(Transient)
    TArray<TObjectPtr<UTextBlock>> LabelTexts;

    UPROPERTY(Transient)
    TArray<TObjectPtr<UTextBlock>> ValueTexts;

    int32 LastVisibleCount = INDEX_NONE;
    int32 LastSelectedIndex = INDEX_NONE;
    bool bLastMenuOpen = false;
    bool bLastFrontEndLayout = false;
};
