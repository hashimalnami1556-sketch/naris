#include "NarisSystemMenuWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Image.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/GameInstance.h"
#include "Engine/Texture2D.h"
#include "Misc/PackageName.h"
#include "Engine/World.h"
#include "NarisPlayerController.h"
#include "NarisRuntimeSubsystem.h"

namespace NarsicUMG
{
    const FLinearColor Obsidian(0.006f, 0.007f, 0.008f, 0.965f);
    const FLinearColor BlackSteel(0.023f, 0.020f, 0.020f, 0.955f);
    const FLinearColor RaisedSteel(0.050f, 0.042f, 0.038f, 0.94f);
    const FLinearColor Bone(0.94f, 0.915f, 0.865f, 1.f);
    const FLinearColor MutedBone(0.58f, 0.54f, 0.50f, 1.f);
    const FLinearColor Bronze(0.72f, 0.46f, 0.18f, 1.f);
    const FLinearColor Ember(0.93f, 0.28f, 0.06f, 1.f);

    constexpr float ActiveIconPlateAlpha = 0.18f;
    constexpr float InactiveIconPlateAlpha = 0.025f;
    constexpr float ActiveIconGlyphAlpha = 0.68f;
    constexpr float InactiveIconGlyphAlpha = 0.24f;
}

void UNarisMenuRowButton::Configure(
    ANarisPlayerController* InController,
    int32 InIndex
)
{
    Controller = InController;
    MenuIndex = InIndex;

    OnClicked.AddUniqueDynamic(this, &UNarisMenuRowButton::HandleClicked);
    OnHovered.AddUniqueDynamic(this, &UNarisMenuRowButton::HandleHovered);
}

void UNarisMenuRowButton::HandleClicked()
{
    if (Controller)
    {
        Controller->ActivateMenuIndex(MenuIndex);
    }
}

void UNarisMenuRowButton::HandleHovered()
{
    if (Controller)
    {
        Controller->SelectMenuIndex(MenuIndex);
    }
}

void UNarisSystemMenuWidget::NativeConstruct()
{
    Super::NativeConstruct();

    CacheVectorIcons();
    if (!WidgetTree->RootWidget)
    {
        BuildInterface();
    }

    Controller = Cast<ANarisPlayerController>(GetOwningPlayer());
    // Keep the widget ticking while closed so it can reopen. Suppress
    // hit testing on both the root and its descendants during gameplay.
    SetVisibility(ESlateVisibility::HitTestInvisible);
    SetRenderOpacity(0.f);
}

void UNarisSystemMenuWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);

    if (!Controller)
    {
        Controller = Cast<ANarisPlayerController>(GetOwningPlayer());
    }

    const bool bOpen = Controller && Controller->IsSystemMenuOpen();
    // HitTestInvisible keeps NativeTick alive yet cannot intercept hidden
    // mouse input; Collapsed/Hidden could prevent this tick-driven reopen.
    SetVisibility(bOpen
        ? ESlateVisibility::SelfHitTestInvisible
        : ESlateVisibility::HitTestInvisible);
    SetRenderOpacity(bOpen ? 1.f : 0.f);

    if (!bOpen)
    {
        bLastMenuOpen = false;
        return;
    }

    RefreshInterface();
    bLastMenuOpen = true;
}

UTextBlock* UNarisSystemMenuWidget::MakeText(
    const FString& Value,
    int32 Size,
    const FLinearColor& Color
) const
{
    UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
    Text->SetText(FText::FromString(Value));
    Text->SetColorAndOpacity(FSlateColor(Color));

    FSlateFontInfo Font = Text->GetFont();
    Font.Size = Size;
    Text->SetFont(Font);
    Text->SetAutoWrapText(true);
    return Text;
}

UBorder* UNarisSystemMenuWidget::MakePanel(
    const FLinearColor& Color,
    const FMargin& Padding
) const
{
    UBorder* Panel = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
    Panel->SetBrushColor(Color);
    Panel->SetPadding(Padding);
    return Panel;
}

void UNarisSystemMenuWidget::BuildInterface()
{
    UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(
        UCanvasPanel::StaticClass(),
        TEXT("NARSIC_SystemMenuRoot")
    );
    WidgetTree->RootWidget = Root;

    UBorder* Backdrop = MakePanel(NarsicUMG::Obsidian, FMargin(0.f));
    BackdropPanel = Backdrop;
    UCanvasPanelSlot* BackdropSlot = Root->AddChildToCanvas(Backdrop);
    BackdropSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
    BackdropSlot->SetOffsets(FMargin(0.f));

    UBorder* Header = MakePanel(
        FLinearColor(0.012f, 0.012f, 0.013f, 0.92f),
        FMargin(24.f, 14.f)
    );
    UCanvasPanelSlot* HeaderSlot = Root->AddChildToCanvas(Header);
    HeaderSlot->SetAnchors(FAnchors(0.035f, 0.035f, 0.965f, 0.13f));
    HeaderSlot->SetOffsets(FMargin(0.f));

    UHorizontalBox* HeaderRow = WidgetTree->ConstructWidget<UHorizontalBox>(
        UHorizontalBox::StaticClass()
    );
    Header->SetContent(HeaderRow);

    BrandText = MakeText(TEXT("CALL OF NARIS"), 46, NarsicUMG::Bone);
    UHorizontalBoxSlot* BrandSlot = HeaderRow->AddChildToHorizontalBox(BrandText);
    BrandSlot->SetSize(FSlateChildSize(ESlateSizeRule::Automatic));
    BrandSlot->SetPadding(FMargin(2.f, 0.f, 34.f, 0.f));
    BrandSlot->SetVerticalAlignment(VAlign_Center);

    ContextText = MakeText(TEXT("MAIN MENU"), 17, NarsicUMG::Bronze);
    UHorizontalBoxSlot* ContextSlot = HeaderRow->AddChildToHorizontalBox(ContextText);
    ContextSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
    ContextSlot->SetVerticalAlignment(VAlign_Center);

    UBorder* MenuPanel = MakePanel(NarsicUMG::BlackSteel, FMargin(18.f));
    MenuPanelRef = MenuPanel;
    UCanvasPanelSlot* MenuPanelSlot = Root->AddChildToCanvas(MenuPanel);
    MenuPanelSlot->SetAnchors(FAnchors(0.035f, 0.155f, 0.605f, 0.90f));
    MenuPanelSlot->SetOffsets(FMargin(0.f));

    UVerticalBox* MenuColumn = WidgetTree->ConstructWidget<UVerticalBox>(
        UVerticalBox::StaticClass()
    );
    MenuPanel->SetContent(MenuColumn);

    for (int32 Index = 0; Index < MaxRows; ++Index)
    {
        UNarisMenuRowButton* RowButton =
            WidgetTree->ConstructWidget<UNarisMenuRowButton>(
                UNarisMenuRowButton::StaticClass()
            );
        RowButton->SetBackgroundColor(FLinearColor(1.f, 1.f, 1.f, 0.f));
        RowButton->SetVisibility(ESlateVisibility::Collapsed);
        RowButtons.Add(RowButton);

        UVerticalBoxSlot* RowSlot = MenuColumn->AddChildToVerticalBox(RowButton);
        RowSlot->SetPadding(FMargin(0.f, 0.f, 0.f, 6.f));

        UBorder* RowPanel = MakePanel(
            FLinearColor(
                NarsicUMG::RaisedSteel.R,
                NarsicUMG::RaisedSteel.G,
                NarsicUMG::RaisedSteel.B,
                0.03f
            ),
            FMargin(12.f, 7.f)
        );
        RowPanels.Add(RowPanel);
        RowButton->AddChild(RowPanel);

        UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>(
            UHorizontalBox::StaticClass()
        );
        RowPanel->SetContent(Row);

        USizeBox* IconSize = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
        IconSize->SetWidthOverride(48.f);
        IconSize->SetHeightOverride(42.f);

        UBorder* IconPlate = MakePanel(
            FLinearColor(
                NarsicUMG::Bronze.R,
                NarsicUMG::Bronze.G,
                NarsicUMG::Bronze.B,
                NarsicUMG::InactiveIconPlateAlpha
            ),
            FMargin(0.f)
        );
        IconPlates.Add(IconPlate);
        IconSize->SetContent(IconPlate);

        UTextBlock* IconText = MakeText(
            TEXT("◆"),
            20,
            FLinearColor(
                NarsicUMG::Bone.R,
                NarsicUMG::Bone.G,
                NarsicUMG::Bone.B,
                NarsicUMG::InactiveIconGlyphAlpha
            )
        );
        IconText->SetJustification(ETextJustify::Center);
        IconTexts.Add(IconText);

        // Keep a real UImage in the widget tree so imported SVG->PNG
        // Texture2D assets become renderable brush images, not text symbols.
        // The overlay retains the original readable glyph fallback if this
        // client has not imported the optional icon textures yet.
        UOverlay* IconStack = WidgetTree->ConstructWidget<UOverlay>(UOverlay::StaticClass());
        IconPlate->SetContent(IconStack);
        USizeBox* IconTextureSize = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
        IconTextureSize->SetWidthOverride(34.f);
        IconTextureSize->SetHeightOverride(34.f);
        UImage* IconImage = WidgetTree->ConstructWidget<UImage>(UImage::StaticClass());
        IconImage->SetVisibility(ESlateVisibility::Collapsed);
        IconImages.Add(IconImage);
        IconTextureSize->SetContent(IconImage);
        UOverlaySlot* ImageSlot = IconStack->AddChildToOverlay(IconTextureSize);
        ImageSlot->SetHorizontalAlignment(HAlign_Center);
        ImageSlot->SetVerticalAlignment(VAlign_Center);
        UOverlaySlot* GlyphSlot = IconStack->AddChildToOverlay(IconText);
        GlyphSlot->SetHorizontalAlignment(HAlign_Center);
        GlyphSlot->SetVerticalAlignment(VAlign_Center);

        UHorizontalBoxSlot* IconSlot = Row->AddChildToHorizontalBox(IconSize);
        IconSlot->SetSize(FSlateChildSize(ESlateSizeRule::Automatic));
        IconSlot->SetPadding(FMargin(0.f, 0.f, 14.f, 0.f));
        IconSlot->SetVerticalAlignment(VAlign_Center);

        UTextBlock* Label = MakeText(TEXT(""), 19, NarsicUMG::Bone);
        LabelTexts.Add(Label);
        UHorizontalBoxSlot* LabelSlot = Row->AddChildToHorizontalBox(Label);
        LabelSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
        LabelSlot->SetVerticalAlignment(VAlign_Center);

        UTextBlock* Value = MakeText(TEXT(""), 15, NarsicUMG::MutedBone);
        ValueTexts.Add(Value);
        UHorizontalBoxSlot* ValueSlot = Row->AddChildToHorizontalBox(Value);
        ValueSlot->SetSize(FSlateChildSize(ESlateSizeRule::Automatic));
        ValueSlot->SetPadding(FMargin(18.f, 0.f, 4.f, 0.f));
        ValueSlot->SetVerticalAlignment(VAlign_Center);
    }

    UBorder* StatusPanel = MakePanel(
        FLinearColor(0.016f, 0.014f, 0.014f, 0.96f),
        FMargin(24.f)
    );
    StatusPanelRef = StatusPanel;
    UCanvasPanelSlot* StatusSlot = Root->AddChildToCanvas(StatusPanel);
    StatusSlot->SetAnchors(FAnchors(0.635f, 0.155f, 0.965f, 0.90f));
    StatusSlot->SetOffsets(FMargin(0.f));

    UVerticalBox* StatusColumn = WidgetTree->ConstructWidget<UVerticalBox>(
        UVerticalBox::StaticClass()
    );
    StatusPanel->SetContent(StatusColumn);

    StatusTitleText = MakeText(TEXT("OPERATION STATUS"), 22, NarsicUMG::Bronze);
    StatusColumn->AddChildToVerticalBox(StatusTitleText);

    StatusBodyText = MakeText(TEXT(""), 16, NarsicUMG::Bone);
    UVerticalBoxSlot* BodySlot = StatusColumn->AddChildToVerticalBox(StatusBodyText);
    BodySlot->SetPadding(FMargin(0.f, 22.f, 0.f, 0.f));
    BodySlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

    UBorder* FooterPanel = MakePanel(
        FLinearColor(0.008f, 0.008f, 0.009f, 0.92f),
        FMargin(16.f, 9.f)
    );
    UCanvasPanelSlot* FooterSlot = Root->AddChildToCanvas(FooterPanel);
    FooterSlot->SetAnchors(FAnchors(0.035f, 0.925f, 0.965f, 0.982f));
    FooterSlot->SetOffsets(FMargin(0.f));

    FooterText = MakeText(
        TEXT("W/S OR D-PAD  NAVIGATE    ENTER/A  CONFIRM    MOUSE  CLICK    ESC/B  BACK"),
        14,
        NarsicUMG::MutedBone
    );
    FooterPanel->SetContent(FooterText);
}

void UNarisSystemMenuWidget::CacheVectorIcons()
{
    static const TCHAR* Names[] = {
        TEXT("health"), TEXT("energy"), TEXT("mana"),
        TEXT("attack"), TEXT("defense"), TEXT("map")
    };
    for (const TCHAR* Name : Names)
    {
        // Stable runtime path independent of WORLD-013/014/015 review levels.
        // The editor import tool installs these six original-source textures
        // before the packaging gate; if missing, text glyphs remain usable.
        const FString PackagePath = FString::Printf(
            TEXT("/Game/NARIS/UI/Icons/%s"), Name);
        if (!FPackageName::DoesPackageExist(PackagePath))
        {
            continue;
        }
        const FString ObjectPath = PackagePath + TEXT(".") + Name;
        if (UTexture2D* Texture = LoadObject<UTexture2D>(nullptr, *ObjectPath))
        {
            VectorIconTextures.Add(FName(Name), Texture);
        }
    }
}

FString UNarisSystemMenuWidget::ResolveVectorIconName(int32 Index) const
{
    if (!Controller || Index < 0)
    {
        return FString();
    }
    const ENarisPauseMenuPage Page = Controller->GetPauseMenuPage();
    if (Page != ENarisPauseMenuPage::Main)
    {
        // Keep settings/controls row-specific symbols and their semantics.
        return FString();
    }

    if (Controller->GetMenuContext() == ENarisMenuContext::FrontEnd)
    {
        static const TCHAR* Front[] = {
            TEXT("attack"), TEXT("map"), TEXT("defense"),
            TEXT("mana"), TEXT("energy")
        };
        return Index < UE_ARRAY_COUNT(Front) ? FString(Front[Index]) : FString();
    }
    static const TCHAR* Pause[] = {
        TEXT("attack"), TEXT("energy"), TEXT("map"),
        TEXT("mana"), TEXT("defense"), TEXT("health")
    };
    return Index < UE_ARRAY_COUNT(Pause) ? FString(Pause[Index]) : FString();
}

FString UNarisSystemMenuWidget::ResolveIcon(int32 Index) const
{
    if (!Controller)
    {
        return TEXT("◆");
    }

    const ENarisPauseMenuPage Page = Controller->GetPauseMenuPage();
    const bool bFrontEnd =
        Controller->GetMenuContext() == ENarisMenuContext::FrontEnd
        && Page == ENarisPauseMenuPage::Main;

    if (bFrontEnd)
    {
        static const TCHAR* FrontIcons[] = {
            TEXT("◆"),
            TEXT("↻"),
            TEXT("◎"),
            TEXT("◌"),
            TEXT("×")
        };
        return Index >= 0 && Index < UE_ARRAY_COUNT(FrontIcons)
            ? FString(FrontIcons[Index])
            : TEXT("•");
    }

    if (Page == ENarisPauseMenuPage::Main)
    {
        static const TCHAR* PauseIcons[] = {
            TEXT("▶"),
            TEXT("▦"),
            TEXT("⌖"),
            TEXT("◇"),
            TEXT("◌"),
            TEXT("≡")
        };
        return Index >= 0 && Index < UE_ARRAY_COUNT(PauseIcons)
            ? FString(PauseIcons[Index])
            : TEXT("•");
    }

    if (Page == ENarisPauseMenuPage::Settings)
    {
        static const TCHAR* SettingsIcons[] = {
            TEXT("Q"), TEXT("V"), TEXT("F"), TEXT("M"), TEXT("♫"),
            TEXT("S"), TEXT("V"), TEXT("C"), TEXT("R"), TEXT("CC"),
            TEXT("T"), TEXT("HC"), TEXT("CV"), TEXT("%"), TEXT("✓"),
            TEXT("↺"), TEXT("‹")
        };
        return Index >= 0 && Index < UE_ARRAY_COUNT(SettingsIcons)
            ? FString(SettingsIcons[Index])
            : TEXT("•");
    }

    if (Page == ENarisPauseMenuPage::Controls)
    {
        return Index < 11 ? TEXT("●") : (Index == 11 ? TEXT("↺") : TEXT("‹"));
    }

    return Index == 0 ? TEXT("◆") : TEXT("•");
}

void UNarisSystemMenuWidget::RefreshInterface()
{
    if (!Controller)
    {
        return;
    }

    // P20 title mode leaves the 3D world visible; settings and inventory
    // retain the dense, opaque layout required for legibility and controller input.
    const bool bFrontEndLayout =
        Controller->GetMenuContext() == ENarisMenuContext::FrontEnd
        && Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Main;
    if (bFrontEndLayout != bLastFrontEndLayout)
    {
        if (BackdropPanel)
        {
            BackdropPanel->SetBrushColor(
                bFrontEndLayout
                    ? FLinearColor(0.004f, 0.005f, 0.007f, 0.22f)
                    : NarsicUMG::Obsidian
            );
        }

        if (MenuPanelRef)
        {
            if (UCanvasPanelSlot* PanelSlot = Cast<UCanvasPanelSlot>(MenuPanelRef->Slot))
            {
                PanelSlot->SetAnchors(
                    bFrontEndLayout
                        ? FAnchors(0.71f, 0.27f, 0.95f, 0.83f)
                        : FAnchors(0.035f, 0.155f, 0.605f, 0.90f)
                );
            }
        }
        if (StatusPanelRef)
        {
            StatusPanelRef->SetVisibility(
                bFrontEndLayout
                    ? ESlateVisibility::Collapsed
                    : ESlateVisibility::SelfHitTestInvisible
            );
        }
        bLastFrontEndLayout = bFrontEndLayout;
    }

    const int32 Count = FMath::Clamp(
        Controller->GetVisibleMenuItemCount(),
        0,
        MaxRows
    );
    const int32 Selected = FMath::Clamp(
        Controller->GetSelectedMenuIndex(),
        0,
        FMath::Max(Count - 1, 0)
    );

    ContextText->SetText(
        Controller->GetMenuContext() == ENarisMenuContext::FrontEnd
            && Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Main
        ? NSLOCTEXT("NARIS", "UMGMainMenuContext", "MAIN MENU")
        : Controller->GetMenuTitle()
    );

    for (int32 Index = 0; Index < MaxRows; ++Index)
    {
        const bool bVisible = Index < Count;
        RowButtons[Index]->SetVisibility(
            bVisible ? ESlateVisibility::Visible : ESlateVisibility::Collapsed
        );

        if (!bVisible)
        {
            continue;
        }

        RowButtons[Index]->Configure(Controller, Index);

        const bool bSelected = Index == Selected;

        LabelTexts[Index]->SetText(Controller->GetMenuItemLabel(Index));
        ValueTexts[Index]->SetText(Controller->GetMenuItemValue(Index));

        const FString IconName = ResolveVectorIconName(Index);
        UTexture2D* IconTexture = IconName.IsEmpty()
            ? nullptr : VectorIconTextures.FindRef(FName(*IconName)).Get();
        if (IconTexture)
        {
            IconImages[Index]->SetBrushFromTexture(IconTexture);
            IconImages[Index]->SetColorAndOpacity(FLinearColor(
                1.f, 1.f, 1.f, bSelected ? 1.f : 0.72f
            ));
            IconImages[Index]->SetVisibility(ESlateVisibility::HitTestInvisible);
            IconTexts[Index]->SetVisibility(ESlateVisibility::Collapsed);
        }
        else
        {
            IconImages[Index]->SetVisibility(ESlateVisibility::Collapsed);
            IconTexts[Index]->SetVisibility(ESlateVisibility::HitTestInvisible);
            IconTexts[Index]->SetText(FText::FromString(ResolveIcon(Index)));
        }

        RowPanels[Index]->SetBrushColor(
            FLinearColor(
                NarsicUMG::RaisedSteel.R,
                NarsicUMG::RaisedSteel.G,
                NarsicUMG::RaisedSteel.B,
                bSelected ? 0.12f : 0.018f
            )
        );

        IconPlates[Index]->SetBrushColor(
            FLinearColor(
                NarsicUMG::Bronze.R,
                NarsicUMG::Bronze.G,
                NarsicUMG::Bronze.B,
                bSelected
                    ? NarsicUMG::ActiveIconPlateAlpha
                    : NarsicUMG::InactiveIconPlateAlpha
            )
        );

        IconTexts[Index]->SetColorAndOpacity(
            FSlateColor(
                FLinearColor(
                    NarsicUMG::Bone.R,
                    NarsicUMG::Bone.G,
                    NarsicUMG::Bone.B,
                    bSelected
                        ? NarsicUMG::ActiveIconGlyphAlpha
                        : NarsicUMG::InactiveIconGlyphAlpha
                )
            )
        );

        LabelTexts[Index]->SetColorAndOpacity(
            FSlateColor(
                bSelected
                    ? NarsicUMG::Bone
                    : NarsicUMG::MutedBone
            )
        );

        ValueTexts[Index]->SetColorAndOpacity(
            FSlateColor(
                bSelected
                    ? NarsicUMG::Bronze
                    : NarsicUMG::MutedBone
            )
        );
    }

    UNarisRuntimeSubsystem* Runtime = nullptr;
    if (UWorld* World = GetWorld())
    {
        if (UGameInstance* GameInstance = World->GetGameInstance())
        {
            Runtime = GameInstance->GetSubsystem<UNarisRuntimeSubsystem>();
        }
    }

    FString Status = TEXT("");
    if (Runtime)
    {
        const FNarisSaveState State = Runtime->GetState();
        if (bInventoryPage)
        {
            // The approved character/inventory reference uses the right panel
            // for actual equipment and loot, never placeholder statistics.
            Status = FText::Format(
                NSLOCTEXT("NARIS", "UMGInventoryCurrency", "Currency: {0}"),
                FText::AsNumber(State.Currency)
            ).ToString();
            Status += TEXT("\n\n");
            Status += NSLOCTEXT("NARIS", "UMGEquippedHeading", "EQUIPPED").ToString();
            Status += TEXT("\n");
            if (State.EquippedItems.IsEmpty())
            {
                Status += NSLOCTEXT("NARIS", "UMGNoEquipment", "No equipment assigned.").ToString();
            }
            else
            {
                const int32 VisibleEquipped = FMath::Min(State.EquippedItems.Num(), 5);
                for (int32 Index = 0; Index < VisibleEquipped; ++Index)
                {
                    Status += FString::Printf(TEXT("• %s\n"), *State.EquippedItems[Index]);
                }
                if (State.EquippedItems.Num() > VisibleEquipped)
                {
                    Status += FText::Format(
                        NSLOCTEXT("NARIS", "UMGExtraEquipped", "+{0} more equipped"),
                        FText::AsNumber(State.EquippedItems.Num() - VisibleEquipped)
                    ).ToString();
                }
            }

            Status += TEXT("\n\n");
            Status += NSLOCTEXT("NARIS", "UMGInventoryItemsHeading", "RELICS & ITEMS").ToString();
            Status += TEXT("\n");
            if (State.InventoryItems.IsEmpty())
            {
                Status += NSLOCTEXT("NARIS", "UMGNoInventory", "Your inventory is empty.").ToString();
            }
            else
            {
                const int32 VisibleItems = FMath::Min(State.InventoryItems.Num(), 7);
                for (int32 Index = 0; Index < VisibleItems; ++Index)
                {
                    Status += FString::Printf(TEXT("• %s\n"), *State.InventoryItems[Index]);
                }
                if (State.InventoryItems.Num() > VisibleItems)
                {
                    Status += FText::Format(
                        NSLOCTEXT("NARIS", "UMGExtraItems", "+{0} more items"),
                        FText::AsNumber(State.InventoryItems.Num() - VisibleItems)
                    ).ToString();
                }
            }
        }
        else
        {
            Status = FString::Printf(
                TEXT("REGION\n%s\n\nCHECKPOINT\n%s\n\nACTIVE QUESTS  %d\nWAYSTONES      %d\nRELICS & ITEMS %d"),
                State.MapId.IsEmpty() ? TEXT("ASHEN FOREST") : *State.MapId,
                State.CheckpointId.IsEmpty() ? TEXT("--") : *State.CheckpointId,
                State.ActiveQuests.Num(),
                State.UnlockedWaystones.Num(),
                State.InventoryItems.Num()
            );
        }
    }
    StatusBodyText->SetText(FText::FromString(Status));

    StatusTitleText->SetText(
        bInventoryPage
        ? NSLOCTEXT("NARIS", "UMGEquipmentStatus", "EQUIPMENT & INVENTORY")
        : Controller->GetMenuContext() == ENarisMenuContext::FrontEnd
            ? NSLOCTEXT("NARIS", "UMGFrontStatus", "JOURNEY STATUS")
            : NSLOCTEXT("NARIS", "UMGPauseStatus", "OPERATION STATUS")
    );

    FooterText->SetText(
        Controller->IsUsingGamepadInput()
        ? NSLOCTEXT(
            "NARIS",
            "UMGGamepadFooter",
            "D-PAD  NAVIGATE    A  CONFIRM    B  BACK"
        )
        : NSLOCTEXT(
            "NARIS",
            "UMGKeyboardFooter",
            "W/S  NAVIGATE    ENTER  CONFIRM    MOUSE  CLICK    ESC  BACK"
        )
    );

    LastVisibleCount = Count;
    LastSelectedIndex = Selected;
}
