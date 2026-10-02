#include "NarisHUD.h"

#include "BoneBeastBoss.h"
#include "CelestialWolf.h"
#include "Engine/Canvas.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "NarisCombatComponent.h"
#include "NarisEnergyComponent.h"
#include "NarisGameUserSettings.h"
#include "NarisHeroCharacter.h"
#include "NarisInteractable.h"
#include "NarisInteractionComponent.h"
#include "NarisPlayerController.h"
#include "NarisRuntimeSubsystem.h"
#include "NarisSubtitleSubsystem.h"
#include "NarisUIStyle.h"

void ANarisHUD::DrawPanel(
    float X,
    float Y,
    float Width,
    float Height,
    const FLinearColor& Color
)
{
    DrawRect(Color, X, Y, Width, Height);
    DrawRect(FLinearColor(FNarisUIStyle::Gold().R, FNarisUIStyle::Gold().G, FNarisUIStyle::Gold().B, 0.42f), X, Y, Width, 1.f);
}

void ANarisHUD::DrawBar(
    const FString& Label,
    float Value,
    float MaxValue,
    float X,
    float Y,
    float Width,
    float Height,
    const FLinearColor& FillColor,
    float Scale
)
{
    const float Ratio = FNarisUIStyle::SafeRatio(Value, MaxValue);
    DrawText(Label, FNarisUIStyle::Muted(), X, Y - 17.f * Scale, nullptr, 0.66f * Scale, false);
    DrawRect(FLinearColor(0.025f, 0.03f, 0.04f, 0.88f), X, Y, Width, Height);
    DrawRect(FillColor, X, Y, Width * Ratio, Height);
    DrawRect(FLinearColor(1.f, 1.f, 1.f, 0.08f), X, Y, Width * Ratio, FMath::Max(1.f, Height * 0.20f));
}

void ANarisHUD::DrawPlayerVitals(ANarisHeroCharacter* Hero, float Scale, float Safe)
{
    if (!Canvas || !Hero)
    {
        return;
    }

    const float PanelW = 350.f * Scale;
    const float PanelH = 126.f * Scale;
    const float X = Safe;
    const float Y = Canvas->ClipY - Safe - PanelH;

    DrawPanel(X, Y, PanelW, PanelH, FLinearColor(0.025f, 0.032f, 0.043f, 0.74f));

    if (Hero->Combat)
    {
        DrawBar(
            NSLOCTEXT("NARIS", "HUDHealth", "Health").ToString(),
            Hero->Combat->Health,
            Hero->Combat->MaxHealth,
            X + 18.f * Scale,
            Y + 34.f * Scale,
            PanelW - 36.f * Scale,
            8.f * Scale,
            FNarisUIStyle::Danger(),
            Scale
        );

        DrawBar(
            NSLOCTEXT("NARIS", "HUDResonance", "Resonance").ToString(),
            Hero->Combat->Resonance,
            Hero->Combat->MaxResonance,
            X + 18.f * Scale,
            Y + 68.f * Scale,
            PanelW - 36.f * Scale,
            6.f * Scale,
            FNarisUIStyle::Violet(),
            Scale
        );
    }

    if (Hero->Energy)
    {
        DrawBar(
            NSLOCTEXT("NARIS", "HUDEnergy", "Energy").ToString(),
            Hero->Energy->Energy,
            Hero->Energy->MaxEnergy,
            X + 18.f * Scale,
            Y + 100.f * Scale,
            PanelW - 36.f * Scale,
            6.f * Scale,
            FNarisUIStyle::Cyan(),
            Scale
        );

        const FString EssenceText = FString::Printf(
            TEXT("%s: %s"),
            *NSLOCTEXT("NARIS", "HUDEssence", "Essence").ToString(),
            *Hero->Energy->GetActiveEssenceDisplayName().ToString()
        );
        DrawText(
            EssenceText,
            FNarisUIStyle::Bone(),
            X + PanelW - 152.f * Scale,
            Y + 82.f * Scale,
            nullptr,
            0.68f * Scale,
            false
        );
    }
}

void ANarisHUD::DrawObjectiveCard(
    UNarisRuntimeSubsystem* Runtime,
    float Scale,
    float Safe
)
{
    if (!Canvas || !Runtime)
    {
        return;
    }

    const FString QuestId = TEXT("Quest.W04.CorruptedHeart");
    if (!Runtime->IsQuestActive(QuestId) && !Runtime->IsQuestCompleted(QuestId))
    {
        return;
    }

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
                Objective = NSLOCTEXT("NARIS", "HUDQuestCorruptedHeartStep1", "Follow the First Whisper.");
                break;
            case 2:
                Objective = NSLOCTEXT("NARIS", "HUDQuestCorruptedHeartStep2", "Pass through the Ash Gate.");
                break;
            case 3:
                Objective = NSLOCTEXT("NARIS", "HUDQuestCorruptedHeartStep3", "Enter the Bone Beast arena.");
                break;
            default:
                break;
        }
    }

    const bool bWolfBonded = Runtime->IsCompanionUnlocked(TEXT("CelestialWolf"));

    const float W = 410.f * Scale;
    const float H = 112.f * Scale;
    const float X = Canvas->ClipX - Safe - W;
    const float Y = Safe;

    DrawPanel(X, Y, W, H, FLinearColor(0.025f, 0.032f, 0.043f, 0.70f));
    DrawText(
        NSLOCTEXT("NARIS", "HUDQuestCorruptedHeart", "Corrupted Heart").ToString(),
        FNarisUIStyle::Gold(),
        X + 18.f * Scale,
        Y + 14.f * Scale,
        nullptr,
        0.72f * Scale,
        false
    );
    DrawText(
        Objective.ToString(),
        FNarisUIStyle::Bone(),
        X + 18.f * Scale,
        Y + 45.f * Scale,
        nullptr,
        0.78f * Scale,
        false
    );

    FString CompanionLine = bWolfBonded
        ? NSLOCTEXT("NARIS", "HUDWolfBonded", "Celestial Wolf: Bonded").ToString()
        : NSLOCTEXT("NARIS", "HUDWolfUnbonded", "Celestial Wolf: Unbonded").ToString();

    if (bWolfBonded && GetWorld())
    {
        for (TActorIterator<ACelestialWolf> WolfIt(GetWorld()); WolfIt; ++WolfIt)
        {
            if (ACelestialWolf* Wolf = *WolfIt)
            {
                CompanionLine = FString::Printf(
                    TEXT("%s: %s"),
                    *NSLOCTEXT("NARIS", "HUDWolfMode", "Wolf Mode").ToString(),
                    *Wolf->GetModeDisplayName().ToString()
                );
                break;
            }
        }
    }

    DrawText(
        CompanionLine,
        bWolfBonded ? FNarisUIStyle::Cyan() : FNarisUIStyle::Muted(),
        X + 18.f * Scale,
        Y + 78.f * Scale,
        nullptr,
        0.66f * Scale,
        false
    );
}

void ANarisHUD::DrawInteractionPrompt(ANarisHeroCharacter* Hero, float Scale)
{
    if (!Canvas || !Hero || !Hero->Interaction)
    {
        return;
    }

    AActor* Target = Hero->Interaction->FindNearestInteractable();
    if (!Target || !Target->GetClass()->ImplementsInterface(UNarisInteractable::StaticClass()))
    {
        return;
    }

    const ANarisPlayerController* NarisController = Cast<ANarisPlayerController>(PlayerOwner);
    const FText ActionKey = NarisController
        ? NarisController->GetActionKeyDisplayName(TEXT("Interact"))
        : FText::FromString(TEXT("E"));

    const FText Prompt = INarisInteractable::Execute_GetInteractionPrompt(Target);
    const FString Text = FString::Printf(TEXT("[%s] %s"), *ActionKey.ToString(), *Prompt.ToString());

    const UNarisGameUserSettings* Settings = UNarisGameUserSettings::GetNarisGameUserSettings();
    const bool bHighContrast = Settings && Settings->bHighContrastInteractions;
    const FLinearColor Gold = FNarisUIStyle::Gold();

    const float W = 420.f * Scale;
    const float H = 48.f * Scale;
    const float X = (Canvas->ClipX - W) * 0.5f;
    const float Y = Canvas->ClipY - 190.f * Scale;

    DrawPanel(X, Y, W, H, FLinearColor(0.02f, 0.025f, 0.035f, 0.78f));
    DrawText(
        Text,
        bHighContrast ? FLinearColor::White : Gold,
        X + 18.f * Scale,
        Y + 14.f * Scale,
        nullptr,
        bHighContrast ? 1.2f : 1.05f,
        false
    );
}

void ANarisHUD::DrawBossHUD(float Scale, float Safe)
{
    if (!Canvas || !GetWorld())
    {
        return;
    }

    for (TActorIterator<ABoneBeastBoss> It(GetWorld()); It; ++It)
    {
        ABoneBeastBoss* Boss = *It;
        if (!Boss || !Boss->IsEncounterActive())
        {
            continue;
        }

        const float W = FMath::Min(Canvas->ClipX * 0.46f, 820.f * Scale);
        const float H = 56.f * Scale;
        const float X = (Canvas->ClipX - W) * 0.5f;
        const float Y = Safe;

        DrawText(
            NSLOCTEXT("NARIS", "HUDBoneBeast", "Bone Beast").ToString(),
            FNarisUIStyle::Bone(),
            X,
            Y,
            nullptr,
            0.88f * Scale,
            false
        );
        DrawBar(
            TEXT(""),
            Boss->GetCurrentHealth(),
            Boss->GetConfiguredMaxHealth(),
            X,
            Y + 28.f * Scale,
            W,
            9.f * Scale,
            FNarisUIStyle::Danger(),
            Scale
        );
        break;
    }
}

void ANarisHUD::DrawSubtitle()
{
    if (!Canvas || !GetWorld())
    {
        return;
    }

    const UNarisGameUserSettings* Settings = UNarisGameUserSettings::GetNarisGameUserSettings();
    if (Settings && !Settings->bSubtitlesEnabled)
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisSubtitleSubsystem* Subtitles = GameInstance
        ? GameInstance->GetSubsystem<UNarisSubtitleSubsystem>()
        : nullptr;

    if (!Subtitles || !Subtitles->IsSubtitleActive())
    {
        return;
    }

    const float UserScale = Settings ? FMath::Clamp(Settings->SubtitleScale, 0.75f, 2.f) : 1.f;
    const float UIScale = FNarisUIStyle::GetViewportScale(Canvas->ClipX, Canvas->ClipY);
    const float W = FMath::Min(980.f * UIScale, Canvas->ClipX * 0.70f);
    const float H = 106.f * UserScale * UIScale;
    const float X = (Canvas->ClipX - W) * 0.5f;
    const float Y = Canvas->ClipY - H - 72.f * UIScale;

    DrawPanel(X, Y, W, H, FLinearColor(0.01f, 0.015f, 0.025f, 0.90f));

    if (!Subtitles->GetSpeaker().IsEmpty())
    {
        DrawText(
            Subtitles->GetSpeaker().ToString(),
            FNarisUIStyle::Gold(),
            X + 24.f * UIScale,
            Y + 15.f * UIScale,
            nullptr,
            0.72f * UserScale * UIScale,
            false
        );
    }

    DrawText(
        Subtitles->GetLine().ToString(),
        FNarisUIStyle::Bone(),
        X + 24.f * UIScale,
        Y + 50.f * UIScale,
        nullptr,
        0.84f * UserScale * UIScale,
        false
    );
}

void ANarisHUD::DrawContentPage(
    ANarisPlayerController* Controller,
    UNarisRuntimeSubsystem* Runtime,
    float X,
    float Y,
    float Width,
    float Height,
    float Scale
)
{
    if (!Controller || !Runtime)
    {
        return;
    }

    const FNarisSaveState State = Runtime->GetState();
    const float Left = X + 42.f * Scale;
    float RowY = Y + 104.f * Scale;

    DrawText(
        Controller->GetMenuTitle().ToString(),
        FNarisUIStyle::Gold(),
        Left,
        Y + 38.f * Scale,
        nullptr,
        1.22f * Scale,
        false
    );

    if (Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Inventory)
    {
        DrawText(
            FString::Printf(TEXT("Currency  %d"), State.Currency),
            FNarisUIStyle::Bone(),
            Left,
            RowY,
            nullptr,
            0.82f * Scale,
            false
        );
        RowY += 42.f * Scale;

        DrawText(
            NSLOCTEXT("NARIS", "InventoryEquipped", "Equipped").ToString(),
            FNarisUIStyle::Muted(),
            Left,
            RowY,
            nullptr,
            0.70f * Scale,
            false
        );
        RowY += 34.f * Scale;

        if (State.EquippedItems.Num() == 0)
        {
            DrawText(
                NSLOCTEXT("NARIS", "InventoryEmptyEquipped", "No equipment assigned.").ToString(),
                FNarisUIStyle::Bone(),
                Left,
                RowY,
                nullptr,
                0.80f * Scale,
                false
            );
        }
        else
        {
            for (const FString& Item : State.EquippedItems)
            {
                DrawText(Item, FNarisUIStyle::Bone(), Left, RowY, nullptr, 0.78f * Scale, false);
                RowY += 28.f * Scale;
            }
        }

        RowY += 50.f * Scale;
        DrawText(
            NSLOCTEXT("NARIS", "InventoryItems", "Relics & Items").ToString(),
            FNarisUIStyle::Muted(),
            Left,
            RowY,
            nullptr,
            0.70f * Scale,
            false
        );
        RowY += 34.f * Scale;

        if (State.InventoryItems.Num() == 0)
        {
            DrawText(
                NSLOCTEXT("NARIS", "InventoryEmpty", "Your inventory is empty.").ToString(),
                FNarisUIStyle::Bone(),
                Left,
                RowY,
                nullptr,
                0.80f * Scale,
                false
            );
        }
        else
        {
            const int32 MaxRows = FMath::Min(State.InventoryItems.Num(), 12);
            for (int32 Index = 0; Index < MaxRows; ++Index)
            {
                DrawText(State.InventoryItems[Index], FNarisUIStyle::Bone(), Left, RowY, nullptr, 0.78f * Scale, false);
                RowY += 28.f * Scale;
            }
        }
    }
    else if (Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Map)
    {
        DrawText(
            FString::Printf(TEXT("REGION  %s"), *State.MapId),
            FNarisUIStyle::Bone(),
            Left,
            RowY,
            nullptr,
            0.82f * Scale,
            false
        );
        RowY += 38.f * Scale;
        DrawText(
            FString::Printf(TEXT("CHECKPOINT  %s"), *State.CheckpointId),
            FNarisUIStyle::Muted(),
            Left,
            RowY,
            nullptr,
            0.74f * Scale,
            false
        );
        RowY += 54.f * Scale;

        DrawText(
            NSLOCTEXT("NARIS", "MapWaystones", "Discovered Waystones").ToString(),
            FNarisUIStyle::Gold(),
            Left,
            RowY,
            nullptr,
            0.70f * Scale,
            false
        );
        RowY += 34.f * Scale;

        if (State.UnlockedWaystones.Num() == 0)
        {
            DrawText(
                NSLOCTEXT("NARIS", "MapNoWaystones", "No waystones discovered.").ToString(),
                FNarisUIStyle::Bone(),
                Left,
                RowY,
                nullptr,
                0.78f * Scale,
                false
            );
        }
        else
        {
            const int32 VisibleWaystones = FMath::Min(State.UnlockedWaystones.Num(), 7);
            for (int32 Index = 0; Index < VisibleWaystones; ++Index)
            {
                DrawText(FString::Printf(TEXT("• %s"), *State.UnlockedWaystones[Index]), FNarisUIStyle::Bone(), Left, RowY, nullptr, 0.78f * Scale, false);
                RowY += 30.f * Scale;
            }
            if (State.UnlockedWaystones.Num() > VisibleWaystones)
            {
                DrawText(FString::Printf(TEXT("+%d more"), State.UnlockedWaystones.Num() - VisibleWaystones), FNarisUIStyle::Muted(), Left, RowY, nullptr, 0.66f * Scale, false);
            }
        }

        const float MapX = X + Width * 0.53f;
        const float MapY = Y + 105.f * Scale;
        const float MapW = Width * 0.40f;
        const float MapH = Height - 165.f * Scale;
        DrawPanel(MapX, MapY, MapW, MapH, FLinearColor(0.07f, 0.10f, 0.08f, 0.88f));
        DrawText(
            NSLOCTEXT("NARIS", "MapAshenForest", "Ashen Forest").ToString(),
            FNarisUIStyle::Gold(),
            MapX + 24.f * Scale,
            MapY + 24.f * Scale,
            nullptr,
            0.82f * Scale,
            false
        );
        DrawLine(MapX + MapW * 0.18f, MapY + MapH * 0.75f, MapX + MapW * 0.72f, MapY + MapH * 0.30f, FNarisUIStyle::Gold(), 2.f);
        DrawLine(MapX + MapW * 0.72f, MapY + MapH * 0.30f, MapX + MapW * 0.84f, MapY + MapH * 0.62f, FNarisUIStyle::Cyan(), 2.f);
    }
    else if (Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Quests)
    {
        DrawText(
            NSLOCTEXT("NARIS", "QuestActive", "Active").ToString(),
            FNarisUIStyle::Gold(),
            Left,
            RowY,
            nullptr,
            0.70f * Scale,
            false
        );
        RowY += 34.f * Scale;

        if (State.ActiveQuests.Num() == 0)
        {
            DrawText(
                NSLOCTEXT("NARIS", "QuestNoneActive", "No active quests.").ToString(),
                FNarisUIStyle::Bone(),
                Left,
                RowY,
                nullptr,
                0.78f * Scale,
                false
            );
        }
        else
        {
            const int32 VisibleActive = FMath::Min(State.ActiveQuests.Num(), 6);
            for (int32 Index = 0; Index < VisibleActive; ++Index)
            {
                const FString& Quest = State.ActiveQuests[Index];
                const int32 Step = State.QuestSteps.FindRef(Quest);
                DrawText(
                    FString::Printf(TEXT("• %s  —  Step %d"), *Quest, Step),
                    FNarisUIStyle::Bone(), Left, RowY, nullptr, 0.78f * Scale, false
                );
                RowY += 30.f * Scale;
            }
            if (State.ActiveQuests.Num() > VisibleActive)
            {
                DrawText(FString::Printf(TEXT("+%d more"), State.ActiveQuests.Num() - VisibleActive), FNarisUIStyle::Muted(), Left, RowY, nullptr, 0.66f * Scale, false);
                RowY += 28.f * Scale;
            }
        }

        RowY += 48.f * Scale;
        DrawText(
            NSLOCTEXT("NARIS", "QuestCompleted", "Completed").ToString(),
            FNarisUIStyle::Muted(),
            Left,
            RowY,
            nullptr,
            0.70f * Scale,
            false
        );
        RowY += 34.f * Scale;

        const int32 VisibleCompleted = FMath::Min(State.CompletedQuests.Num(), 5);
        for (int32 Index = 0; Index < VisibleCompleted; ++Index)
        {
            const FString& Quest = State.CompletedQuests[Index];
            DrawText(FString::Printf(TEXT("✓ %s"), *Quest), FNarisUIStyle::Muted(), Left, RowY, nullptr, 0.75f * Scale, false);
            RowY += 28.f * Scale;
        }
        if (State.CompletedQuests.Num() > VisibleCompleted)
        {
            DrawText(FString::Printf(TEXT("+%d more"), State.CompletedQuests.Num() - VisibleCompleted), FNarisUIStyle::Muted(), Left, RowY, nullptr, 0.66f * Scale, false);
        }
    }

    DrawText(
        NSLOCTEXT("NARIS", "ContentBackHint", "Back: Esc / B").ToString(),
        FNarisUIStyle::Muted(),
        Left,
        Y + Height - 44.f * Scale,
        nullptr,
        0.68f * Scale,
        false
    );
}

void ANarisHUD::DrawPauseMenu()
{
    ANarisPlayerController* Controller = Cast<ANarisPlayerController>(PlayerOwner);
    if (!Controller || !Controller->IsSystemMenuOpen() || !Canvas)
    {
        return;
    }

    const float Scale = FNarisUIStyle::GetViewportScale(Canvas->ClipX, Canvas->ClipY);
    const float Safe = FNarisUIStyle::GetSafeMargin(Canvas->ClipX, Canvas->ClipY);
    const float W = FMath::Min(1180.f * Scale, Canvas->ClipX - Safe * 2.f);
    const float H = FMath::Min(820.f * Scale, Canvas->ClipY - Safe * 2.f);
    const float X = (Canvas->ClipX - W) * 0.5f;
    const float Y = (Canvas->ClipY - H) * 0.5f;

    DrawRect(FLinearColor(0.005f, 0.008f, 0.012f, 0.84f), 0.f, 0.f, Canvas->ClipX, Canvas->ClipY);
    DrawPanel(X, Y, W, H, FNarisUIStyle::Canvas());

    UNarisRuntimeSubsystem* Runtime = nullptr;
    if (UGameInstance* GameInstance = GetWorld() ? GetWorld()->GetGameInstance() : nullptr)
    {
        Runtime = GameInstance->GetSubsystem<UNarisRuntimeSubsystem>();
    }

    if (Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Inventory
        || Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Map
        || Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Quests)
    {
        DrawContentPage(Controller, Runtime, X, Y, W, H, Scale);
        return;
    }

    DrawText(
        Controller->GetMenuTitle().ToString(),
        FNarisUIStyle::Gold(),
        X + 44.f * Scale,
        Y + 34.f * Scale,
        nullptr,
        1.24f * Scale,
        false
    );

    const int32 Count = Controller->GetVisibleMenuItemCount();
    const int32 Selected = Controller->GetSelectedMenuIndex();
    const float StartY = Y + 106.f * Scale;
    const float RowH = Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Main
        ? 64.f * Scale
        : FMath::Clamp((H - 190.f * Scale) / FMath::Max(Count, 1), 26.f * Scale, 42.f * Scale);

    for (int32 Index = 0; Index < Count; ++Index)
    {
        const float RowY = StartY + Index * RowH;
        const bool bSelected = Index == Selected;

        if (bSelected)
        {
            DrawRect(FNarisUIStyle::Selection(), X + 28.f * Scale, RowY - 9.f * Scale, W - 56.f * Scale, RowH - 5.f * Scale);
            DrawRect(FNarisUIStyle::Gold(), X + 28.f * Scale, RowY - 9.f * Scale, 3.f * Scale, RowH - 5.f * Scale);
        }

        DrawText(
            Controller->GetMenuItemLabel(Index).ToString(),
            bSelected ? FNarisUIStyle::Bone() : FNarisUIStyle::Muted(),
            X + 50.f * Scale,
            RowY,
            nullptr,
            (bSelected ? 0.90f : 0.80f) * Scale,
            false
        );

        const FText Value = Controller->GetMenuItemValue(Index);
        if (!Value.IsEmpty())
        {
            DrawText(
                Value.ToString(),
                bSelected ? FNarisUIStyle::Cyan() : FNarisUIStyle::Muted(),
                X + W * 0.62f,
                RowY,
                nullptr,
                0.78f * Scale,
                false
            );
        }
    }

    FString Hint;
    if (Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Controls)
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
    else if (Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Settings)
    {
        Hint = NSLOCTEXT(
            "NARIS",
            "SettingsMenuHint",
            "Adjust: A/D or Left/Right   Confirm: Enter/A   Back: Esc/B"
        ).ToString();
    }
    else
    {
        Hint = Controller->GetMenuContext() == ENarisMenuContext::FrontEnd
            ? NSLOCTEXT(
                "NARIS",
                "FrontEndMenuHint",
                "Navigate: W/S or D-Pad   Confirm: Enter/A"
              ).ToString()
            : NSLOCTEXT(
                "NARIS",
                "PauseMenuHint",
                "Navigate: W/S or D-Pad   Confirm: Enter/A   Back: Esc/B"
              ).ToString();
    }

    DrawText(
        Hint,
        FNarisUIStyle::Muted(),
        X + 44.f * Scale,
        Y + H - 44.f * Scale,
        nullptr,
        0.66f * Scale,
        false
    );
}

void ANarisHUD::DrawHUD()
{
    Super::DrawHUD();

    if (!Canvas || !PlayerOwner)
    {
        return;
    }

    ANarisPlayerController* Controller = Cast<ANarisPlayerController>(PlayerOwner);
    if (Controller && Controller->IsFrontEndMenuOpen())
    {
        DrawSubtitle();
        DrawPauseMenu();
        return;
    }

    ANarisHeroCharacter* Hero = Cast<ANarisHeroCharacter>(PlayerOwner->GetPawn());
    UNarisRuntimeSubsystem* Runtime = nullptr;
    if (UGameInstance* GameInstance = GetWorld() ? GetWorld()->GetGameInstance() : nullptr)
    {
        Runtime = GameInstance->GetSubsystem<UNarisRuntimeSubsystem>();
    }

    if (Hero && (!Controller || !Controller->IsSystemMenuOpen()))
    {
        const float Scale = FNarisUIStyle::GetViewportScale(Canvas->ClipX, Canvas->ClipY);
        const float Safe = FNarisUIStyle::GetSafeMargin(Canvas->ClipX, Canvas->ClipY);

        DrawPlayerVitals(Hero, Scale, Safe);
        DrawObjectiveCard(Runtime, Scale, Safe);
        DrawInteractionPrompt(Hero, Scale);
        DrawBossHUD(Scale, Safe);

        if (Runtime && Runtime->IsDemoCompleted())
        {
            const FString Complete = NSLOCTEXT("NARIS", "HUDDemoComplete", "W04 DEMO COMPLETE").ToString();
            DrawText(
                Complete,
                FNarisUIStyle::Gold(),
                Canvas->ClipX * 0.5f - 110.f * Scale,
                Canvas->ClipY * 0.18f,
                nullptr,
                1.05f * Scale,
                false
            );
        }
    }

    DrawSubtitle();
    DrawPauseMenu();
}
