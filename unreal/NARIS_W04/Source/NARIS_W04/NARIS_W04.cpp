#include "Modules/ModuleManager.h"
#include "MoviePlayer.h"
#include "UObject/UObjectGlobals.h"
#include "HAL/FileManager.h"
#include "Misc/Paths.h"
#include "Brushes/SlateDynamicImageBrush.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/Images/SThrobber.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

// Public product branding is NARSIC; NARIS_W04 stays the technical module name.
// MoviePlayer draws during blocking map loads, when ordinary UMG cannot tick.
class FNarsicGameModule final : public FDefaultGameModuleImpl
{
public:
    virtual void StartupModule() override
    {
        FDefaultGameModuleImpl::StartupModule();
        if (IsRunningCommandlet() || IsRunningDedicatedServer() || !IsMoviePlayerEnabled())
        {
            return;
        }
        FCoreUObjectDelegates::PreLoadMap.AddRaw(this, &FNarsicGameModule::OnPreLoadMap);
        FCoreUObjectDelegates::PostLoadMapWithWorld.AddRaw(this, &FNarsicGameModule::OnPostLoadMap);
        ConfigureLoadingScreen(); // first packaged map as well as later travel
    }

    virtual void ShutdownModule() override
    {
        FCoreUObjectDelegates::PreLoadMap.RemoveAll(this);
        FCoreUObjectDelegates::PostLoadMapWithWorld.RemoveAll(this);
        PosterBrush.Reset();
        FDefaultGameModuleImpl::ShutdownModule();
    }

private:
    TSharedPtr<FSlateDynamicImageBrush> PosterBrush;

    void OnPreLoadMap(const FString& /*MapName*/)
    {
        ConfigureLoadingScreen();
    }

    void OnPostLoadMap(UWorld* /*LoadedWorld*/)
    {
        // MoviePlayer auto-completes once the map is loaded. Do not fake percentages.
    }

    void ConfigureLoadingScreen()
    {
        if (!IsMoviePlayerEnabled())
        {
            return;
        }

        const FString ArtPath = FPaths::ProjectContentDir()
            / TEXT("NARSIC/Loading/NARSIC_Transit_Approved.png");

        TSharedRef<SWidget> Artwork = SNew(SBorder)
            .BorderBackgroundColor(FLinearColor(0.008f, 0.011f, 0.016f, 1.f))
            .Padding(0);

        if (IFileManager::Get().FileExists(*ArtPath))
        {
            if (!PosterBrush.IsValid())
            {
                PosterBrush = MakeShared<FSlateDynamicImageBrush>(
                    FName(*ArtPath), FVector2D(1672.f, 941.f));
            }

            Artwork = SNew(SScaleBox)
                .Stretch(EStretch::ScaleToFit)
                [
                    SNew(SImage)
                    .Image(PosterBrush.Get())
                ];
        }

        TSharedRef<SWidget> LoadingOverlay = SNew(SOverlay)
            + SOverlay::Slot()
            .HAlign(HAlign_Fill)
            .VAlign(VAlign_Fill)
            [
                Artwork
            ]
            + SOverlay::Slot()
            .HAlign(HAlign_Fill)
            .VAlign(VAlign_Bottom)
            [
                SNew(SBorder)
                .BorderBackgroundColor(FLinearColor(0.006f, 0.009f, 0.014f, 0.96f))
                .Padding(FMargin(34.f, 20.f))
                [
                    SNew(SHorizontalBox)
                    + SHorizontalBox::Slot()
                    .AutoWidth()
                    .VAlign(VAlign_Center)
                    [
                        SNew(STextBlock)
                        .Text(FText::FromString(TEXT("NARSIC")))
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.85f, 0.79f, 0.70f, 1.f)))
                    ]
                    + SHorizontalBox::Slot()
                    .FillWidth(1.f)
                    .Padding(FMargin(32.f, 0.f))
                    .VAlign(VAlign_Center)
                    [
                        SNew(STextBlock)
                        .Text(FText::FromString(TEXT("PREPARING THE PASSAGE")))
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.70f, 0.64f, 0.57f, 1.f)))
                    ]
                    + SHorizontalBox::Slot()
                    .AutoWidth()
                    .VAlign(VAlign_Center)
                    [
                        SNew(SThrobber)
                        .NumPieces(3)
                    ]
                ]
            ];

        FLoadingScreenAttributes Attributes;
        Attributes.bAutoCompleteWhenLoadingCompletes = true;
        Attributes.bWaitForManualStop = false;
        Attributes.MinimumLoadingScreenDisplayTime = 0.f;
        Attributes.WidgetLoadingScreen = LoadingOverlay;
        GetMoviePlayer()->SetupLoadingScreen(Attributes);
    }
};

IMPLEMENT_PRIMARY_GAME_MODULE(FNarsicGameModule, NARIS_W04, "NARIS_W04");
