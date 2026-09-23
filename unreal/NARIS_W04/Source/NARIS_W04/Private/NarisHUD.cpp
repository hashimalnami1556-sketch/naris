#include "NarisHUD.h"

#include "BoneBeastBoss.h"
#include "BoneBeastDataAsset.h"
#include "CelestialWolf.h"
#include "Engine/GameInstance.h"
#include "Engine/Canvas.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "NarisCombatComponent.h"
#include "NarisEnergyComponent.h"
#include "NarisHeroCharacter.h"
#include "NarisGameUserSettings.h"
#include "NarisInteractable.h"
#include "NarisInteractionComponent.h"
#include "NarisPlayerController.h"
#include "NarisRuntimeSubsystem.h"
#include "NarisSubtitleSubsystem.h"

void ANarisHUD::DrawSubtitle()
{
    if (!Canvas || !GetWorld())
    {
        return;
    }

    const UNarisGameUserSettings* Settings =
        UNarisGameUserSettings::GetNarisGameUserSettings();
    if (Settings && !Settings->bSubtitlesEnabled)
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisSubtitleSubsystem* Subtitles =
        GameInstance
            ? GameInstance->GetSubsystem<UNarisSubtitleSubsystem>()
            : nullptr;

    if (!Subtitles || !Subtitles->IsSubtitleActive())
    {
        return;
    }

    const float UserScale = Settings
        ? FMath::Clamp(Settings->SubtitleScale, 0.75f, 2.f)
        : 1.f;

    const float Width = Canvas->ClipX;
    const float Height = Canvas->ClipY;
    const float PanelWidth = FMath::Min(1100.f, Width * 0.72f);
    const float PanelHeight = 118.f * UserScale;
    const float X = (Width - PanelWidth) * 0.5f;
    const float Y = Height - PanelHeight - 62.f;

    DrawRect(
        FLinearColor(0.01f, 0.015f, 0.025f, 0.88f),
        X,
        Y,
        PanelWidth,
        PanelHeight
    );

    const FText Speaker = Subtitles->GetSpeaker();
    if (!Speaker.IsEmpty())
    {
        DrawText(
            Speaker.ToString(),
            FLinearColor(0.82f, 0.65f, 0.18f, 1.f),
            X + 28.f,
            Y + 18.f * UserScale,
            nullptr,
            0.88f * UserScale,
            false
        );
    }

    DrawText(
        Subtitles->GetLine().ToString(),
        FLinearColor::White,
        X + 28.f,
        Y + 58.f * UserScale,
        nullptr,
        0.96f * UserScale,
        false
    );
}

void ANarisHUD::DrawPauseMenu()
{
    ANarisPlayerController* Controller =
        Cast<ANarisPlayerController>(PlayerOwner);
    if (!Controller || !Controller->IsPauseMenuOpen() || !Canvas)
    {
        return;
    }

    const float Width = Canvas->ClipX;
    const float Height = Canvas->ClipY;
    const float PanelWidth = FMath::Min(760.f, Width * 0.72f);
    const float PanelHeight = FMath::Min(900.f, Height * 0.90f);
    const float X = (Width - PanelWidth) * 0.5f;
    const float Y = (Height - PanelHeight) * 0.5f;

    const FLinearColor Overlay(0.01f, 0.015f, 0.025f, 0.82f);
    const FLinearColor Panel(0.035f, 0.05f, 0.075f, 0.96f);
    const FLinearColor Gold(0.82f, 0.65f, 0.18f, 1.f);
    const FLinearColor Cyan(0.36f, 0.86f, 0.92f, 1.f);
    const FLinearColor Muted(0.65f, 0.69f, 0.75f, 1.f);

    DrawRect(Overlay, 0.f, 0.f, Width, Height);
    DrawRect(Panel, X, Y, PanelWidth, PanelHeight);

    DrawText(
        Controller->GetMenuTitle().ToString(),
        Gold,
        X + 44.f,
        Y + 36.f,
        nullptr,
        1.45f,
        false
    );

    const int32 Count = Controller->GetVisibleMenuItemCount();
    const int32 Selected = Controller->GetSelectedMenuIndex();
    const float RowHeight = Controller->GetPauseMenuPage()
        == ENarisPauseMenuPage::Main
            ? 64.f
            : FMath::Clamp(
                (PanelHeight - 200.f) / FMath::Max(Count, 1),
                24.f,
                42.f
            );
    const float StartY = Y + 110.f;

    for (int32 Index = 0; Index < Count; ++Index)
    {
        const bool bSelected = Index == Selected;
        const float RowY = StartY + Index * RowHeight;

        if (bSelected)
        {
            DrawRect(
                FLinearColor(0.16f, 0.12f, 0.035f, 0.78f),
                X + 28.f,
                RowY - 8.f,
                PanelWidth - 56.f,
                RowHeight - 4.f
            );
        }

        DrawText(
            Controller->GetMenuItemLabel(Index).ToString(),
            bSelected ? Gold : FLinearColor::White,
            X + 48.f,
            RowY,
            nullptr,
            bSelected ? 1.0f : 0.9f,
            false
        );

        const FText Value = Controller->GetMenuItemValue(Index);
        if (!Value.IsEmpty())
        {
            DrawText(
                Value.ToString(),
                bSelected ? Cyan : Muted,
                X + PanelWidth * 0.58f,
                RowY,
                nullptr,
                bSelected ? 0.95f : 0.86f,
                false
            );
        }
    }

    FString Hint;
    if (Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Main)
    {
        Hint = NSLOCTEXT(
            "NARIS",
            "PauseMenuHint",
            "Navigate: W/S or D-Pad   Confirm: Enter/A   Back: Esc/B"
        ).ToString();
    }
    else if (Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Controls)
    {
        Hint = Controller->IsWaitingForGamepadRemap()
            ? NSLOCTEXT(
                "NARIS",
                "ControlsCaptureHint",
                "Press a gamepad button. Start/B cancels capture."
              ).ToString()
            : NSLOCTEXT(
                "NARIS",
                "ControlsMenuHint",
                "Select an action and press Confirm to remap. Back: Esc/B"
              ).ToString();
    }
    else
    {
        Hint = NSLOCTEXT(
            "NARIS",
            "SettingsMenuHint",
            "Adjust: A/D or Left/Right   Confirm: Enter/A   Back: Esc/B"
        ).ToString();
    }

    DrawText(
        Hint,
        Muted,
        X + 44.f,
        Y + PanelHeight - 52.f,
        nullptr,
        0.78f,
        false
    );
}

void ANarisHUD::DrawBar(
    const FString& Label,
    float Value,
    float MaxValue,
    float X,
    float Y,
    const FLinearColor& FillColor
)
{
    const float SafeMax = FMath::Max(MaxValue, 1.f);
    const float Ratio = FMath::Clamp(Value / SafeMax, 0.f, 1.f);
    const float Width = 320.f;
    const float Height = 18.f;

    DrawText(Label, FLinearColor::White, X, Y - 22.f, nullptr, 0.9f, false);
    DrawRect(FLinearColor(0.02f, 0.03f, 0.05f, 0.85f), X, Y, Width, Height);
    DrawRect(FillColor, X, Y, Width * Ratio, Height);
}

void ANarisHUD::DrawHUD()
{
    Super::DrawHUD();

    if (!PlayerOwner)
    {
        return;
    }

    ANarisHeroCharacter* Hero = Cast<ANarisHeroCharacter>(PlayerOwner->GetPawn());
    if (!Hero)
    {
        return;
    }

    const FLinearColor Gold(0.82f, 0.65f, 0.18f, 1.f);
    const FLinearColor Cyan(0.36f, 0.86f, 0.92f, 1.f);
    const FLinearColor Violet(0.40f, 0.14f, 0.78f, 1.f);
    const FLinearColor Ember(0.95f, 0.28f, 0.07f, 1.f);

    if (Hero->Combat)
    {
        DrawBar(
            NSLOCTEXT("NARIS", "HUDHealth", "Health").ToString(),
            Hero->Combat->Health,
            Hero->Combat->MaxHealth,
            40.f,
            60.f,
            Ember
        );
        DrawBar(
            NSLOCTEXT("NARIS", "HUDResonance", "Resonance").ToString(),
            Hero->Combat->Resonance,
            Hero->Combat->MaxResonance,
            40.f,
            120.f,
            Violet
        );
    }

    if (Hero->Energy)
    {
        DrawBar(
            NSLOCTEXT("NARIS", "HUDEnergy", "Energy").ToString(),
            Hero->Energy->Energy,
            Hero->Energy->MaxEnergy,
            40.f,
            180.f,
            Cyan
        );

        const FString EssenceText = FString::Printf(
            TEXT("%s: %s"),
            *NSLOCTEXT("NARIS", "HUDEssence", "Essence").ToString(),
            *Hero->Energy->GetActiveEssenceDisplayName().ToString()
        );
        DrawText(EssenceText, Cyan, 40.f, 215.f, nullptr, 0.9f, false);
    }

    if (Hero->Interaction)
    {
        AActor* Target = Hero->Interaction->FindNearestInteractable();
        if (Target && Target->GetClass()->ImplementsInterface(UNarisInteractable::StaticClass()))
        {
            const UNarisGameUserSettings* Settings =
                UNarisGameUserSettings::GetNarisGameUserSettings();
            const bool bHighContrast =
                Settings && Settings->bHighContrastInteractions;

            const FText Prompt = INarisInteractable::Execute_GetInteractionPrompt(Target);
            const FString PromptText = FString::Printf(TEXT("[E] %s"), *Prompt.ToString());
            DrawText(
                PromptText,
                bHighContrast ? FLinearColor::White : Gold,
                40.f,
                240.f,
                nullptr,
                bHighContrast ? 1.2f : 1.05f,
                false
            );
        }
    }

    UNarisRuntimeSubsystem* Runtime = nullptr;
    if (UGameInstance* GameInstance = GetWorld() ? GetWorld()->GetGameInstance() : nullptr)
    {
        Runtime = GameInstance->GetSubsystem<UNarisRuntimeSubsystem>();
    }

    if (Runtime)
    {
        const FString CompanionState = Runtime->IsCompanionUnlocked(TEXT("CelestialWolf"))
            ? NSLOCTEXT("NARIS", "HUDWolfBonded", "Celestial Wolf: Bonded").ToString()
            : NSLOCTEXT("NARIS", "HUDWolfUnbonded", "Celestial Wolf: Unbonded").ToString();

        DrawText(
            CompanionState,
            Runtime->IsCompanionUnlocked(TEXT("CelestialWolf")) ? Cyan : FLinearColor::Gray,
            40.f,
            295.f,
            nullptr,
            0.9f,
            false
        );

        if (Runtime->IsCompanionUnlocked(TEXT("CelestialWolf")))
        {
            for (TActorIterator<ACelestialWolf> WolfIt(GetWorld()); WolfIt; ++WolfIt)
            {
                ACelestialWolf* Wolf = *WolfIt;
                if (Wolf)
                {
                    const FString ModeText = FString::Printf(
                        TEXT("%s: %s"),
                        *NSLOCTEXT("NARIS", "HUDWolfMode", "Wolf Mode").ToString(),
                        *Wolf->GetModeDisplayName().ToString()
                    );
                    DrawText(ModeText, Cyan, 40.f, 320.f, nullptr, 0.85f, false);
                    break;
                }
            }
        }

        const FString QuestId = TEXT("Quest.W04.CorruptedHeart");
        if (Runtime->IsQuestActive(QuestId) || Runtime->IsQuestCompleted(QuestId))
        {
            DrawText(
                NSLOCTEXT("NARIS", "HUDQuestCorruptedHeart", "Corrupted Heart").ToString(),
                Gold,
                40.f,
                345.f,
                nullptr,
                0.95f,
                false
            );

            FText Objective = NSLOCTEXT(
                "NARIS",
                "HUDQuestCorruptedHeartUnknown",
                "Follow the Corrupted Heart."
            );

            if (Runtime->IsQuestCompleted(QuestId))
            {
                Objective = NSLOCTEXT(
                    "NARIS",
                    "HUDQuestCorruptedHeartComplete",
                    "Corrupted Heart cleansed."
                );
            }
            else
            {
                switch (Runtime->GetQuestStep(QuestId))
                {
                    case 1:
                        Objective = NSLOCTEXT(
                            "NARIS",
                            "HUDQuestCorruptedHeartStep1",
                            "Follow the First Whisper."
                        );
                        break;
                    case 2:
                        Objective = NSLOCTEXT(
                            "NARIS",
                            "HUDQuestCorruptedHeartStep2",
                            "Pass through the Ash Gate."
                        );
                        break;
                    case 3:
                        Objective = NSLOCTEXT(
                            "NARIS",
                            "HUDQuestCorruptedHeartStep3",
                            "Enter the Bone Beast arena."
                        );
                        break;
                    default:
                        break;
                }
            }

            DrawText(
                Objective.ToString(),
                FLinearColor::White,
                40.f,
                370.f,
                nullptr,
                0.82f,
                false
            );
        }

        if (Runtime->IsDemoCompleted())
        {
            DrawText(
                NSLOCTEXT("NARIS", "HUDDemoComplete", "W04 DEMO COMPLETE").ToString(),
                Gold,
                40.f,
                450.f,
                nullptr,
                1.25f,
                false
            );
        }
    }

    for (TActorIterator<ABoneBeastBoss> It(GetWorld()); It; ++It)
    {
        ABoneBeastBoss* Boss = *It;
        if (!Boss || (!Boss->IsEncounterActive() && !Boss->IsEncounterComplete()))
        {
            continue;
        }

        if (Boss->IsEncounterComplete())
        {
            DrawText(
                NSLOCTEXT("NARIS", "HUDBoneBeastDefeated", "Bone Beast Defeated").ToString(),
                Gold,
                40.f,
                465.f,
                nullptr,
                1.0f,
                false
            );
        }
        else
        {
            const float MaxHealth = Boss->GetConfiguredMaxHealth();
            DrawBar(
                NSLOCTEXT("NARIS", "HUDBoneBeast", "Bone Beast").ToString(),
                Boss->GetCurrentHealth(),
                MaxHealth,
                40.f,
                405.f,
                Ember
            );
        }
        break;
    }

    DrawSubtitle();
    DrawPauseMenu();
}
