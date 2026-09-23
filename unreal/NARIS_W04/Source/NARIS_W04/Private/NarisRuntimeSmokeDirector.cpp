#include "NarisRuntimeSmokeDirector.h"

#include "BoneBeastBoss.h"
#include "CelestialWolf.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "NarisAshGate.h"
#include "NarisBossArenaController.h"
#include "NarisMemoryCrystal.h"
#include "NarisRuntimeSubsystem.h"
#include "NarisWaystone.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "TimerManager.h"

namespace
{
    constexpr const TCHAR* RuntimeSmokeFlag = TEXT("NarisRuntimeSmoke");
    constexpr const TCHAR* RuntimeSmokeSlot = TEXT("NARIS_RuntimeSmoke");
}

ANarisRuntimeSmokeDirector::ANarisRuntimeSmokeDirector()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ANarisRuntimeSmokeDirector::BeginPlay()
{
    Super::BeginPlay();

    if (!FParse::Param(FCommandLine::Get(), RuntimeSmokeFlag))
    {
        return;
    }

    GetWorldTimerManager().SetTimerForNextTick(
        FTimerDelegate::CreateUObject(
            this,
            &ANarisRuntimeSmokeDirector::RunSmoke
        )
    );
}

FString ANarisRuntimeSmokeDirector::ResolveReportPath() const
{
    FString ExplicitPath;
    if (FParse::Value(
            FCommandLine::Get(),
            TEXT("NarisSmokeReport="),
            ExplicitPath
        )
        && !ExplicitPath.IsEmpty())
    {
        ExplicitPath.TrimQuotesInline();
        return FPaths::ConvertRelativePathToFull(ExplicitPath);
    }

    return FPaths::Combine(
        FPaths::ProjectSavedDir(),
        TEXT("TestReports"),
        TEXT("naris_runtime_smoke.json")
    );
}

void ANarisRuntimeSmokeDirector::RunSmoke()
{
    TMap<FString, bool> Steps;
    FString Detail;

    UWorld* World = GetWorld();
    UGameInstance* GameInstance = World ? World->GetGameInstance() : nullptr;
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    Steps.Add(TEXT("runtime_subsystem"), Runtime != nullptr);
    if (!Runtime)
    {
        FinishSmoke(false, Steps, TEXT("Runtime subsystem unavailable"));
        return;
    }

    ANarisWaystone* Waystone = nullptr;
    ANarisMemoryCrystal* MemoryCrystal = nullptr;
    ANarisAshGate* AshGate = nullptr;
    ACelestialWolf* Wolf = nullptr;
    ABoneBeastBoss* BoneBeast = nullptr;
    ANarisBossArenaController* Arena = nullptr;

    for (TActorIterator<ANarisWaystone> It(World); It; ++It)
    {
        Waystone = *It;
        break;
    }
    for (TActorIterator<ANarisMemoryCrystal> It(World); It; ++It)
    {
        MemoryCrystal = *It;
        break;
    }
    for (TActorIterator<ANarisAshGate> It(World); It; ++It)
    {
        AshGate = *It;
        break;
    }
    for (TActorIterator<ACelestialWolf> It(World); It; ++It)
    {
        Wolf = *It;
        break;
    }
    for (TActorIterator<ABoneBeastBoss> It(World); It; ++It)
    {
        BoneBeast = *It;
        break;
    }
    for (TActorIterator<ANarisBossArenaController> It(World); It; ++It)
    {
        Arena = *It;
        break;
    }

    Steps.Add(TEXT("waystone_actor"), Waystone != nullptr);
    Steps.Add(TEXT("memory_crystal_actor"), MemoryCrystal != nullptr);
    Steps.Add(TEXT("ash_gate_actor"), AshGate != nullptr);
    Steps.Add(TEXT("celestial_wolf_actor"), Wolf != nullptr);
    Steps.Add(TEXT("bone_beast_actor"), BoneBeast != nullptr);
    Steps.Add(TEXT("boss_arena_actor"), Arena != nullptr);

    if (!Waystone || !MemoryCrystal || !AshGate || !Wolf || !BoneBeast || !Arena)
    {
        FinishSmoke(false, Steps, TEXT("Required W04 smoke actors are missing"));
        return;
    }

    UGameplayStatics::DeleteGameInSlot(RuntimeSmokeSlot, 0);
    Runtime->BeginNewGame();

    Waystone->AutoSaveSlot = RuntimeSmokeSlot;
    MemoryCrystal->AutoSaveSlot = RuntimeSmokeSlot;
    AshGate->AutoSaveSlot = RuntimeSmokeSlot;
    Wolf->AutoSaveSlot = RuntimeSmokeSlot;
    BoneBeast->AutoSaveSlot = RuntimeSmokeSlot;

    const bool bWaystone = Waystone->ActivateWaystone(this);
    Steps.Add(TEXT("waystone_activate"), bWaystone);

    const bool bMemory = MemoryCrystal->ActivateMemory(this);
    Steps.Add(TEXT("memory_crystal_activate"), bMemory);

    const bool bGate = AshGate->TryUnlockGate(this);
    Steps.Add(TEXT("ash_gate_unlock"), bGate);

    const bool bWolf = Wolf->BondWithPlayer(this);
    Steps.Add(TEXT("celestial_wolf_bond"), bWolf);

    const bool bBossStarted = BoneBeast->TryStartEncounter(this);
    Steps.Add(TEXT("bone_beast_start"), bBossStarted);
    Steps.Add(
        TEXT("arena_closed_on_encounter"),
        bBossStarted && Arena->bArenaClosed
    );

    if (bBossStarted)
    {
        BoneBeast->ApplyDamageToEncounter(BoneBeast->GetConfiguredMaxHealth());
    }

    const bool bBossComplete = BoneBeast->IsEncounterComplete();
    Steps.Add(TEXT("bone_beast_complete"), bBossComplete);
    Steps.Add(
        TEXT("arena_open_after_completion"),
        bBossComplete && !Arena->bArenaClosed
    );

    const FNarisSaveState BeforeReload = Runtime->GetState();

    const bool bStateComplete =
        BeforeReload.CheckpointId == TEXT("W04_Waystone_0001")
        && BeforeReload.UnlockedLore.Contains(TEXT("W04_Lore_MemoryCrystal_0001"))
        && BeforeReload.TriggeredNarratives.Contains(TEXT("W04_FirstWhisper"))
        && BeforeReload.UnlockedGates.Contains(TEXT("W04_AshGate"))
        && BeforeReload.UnlockedCompanions.Contains(TEXT("CelestialWolf"))
        && BeforeReload.CompletedQuests.Contains(TEXT("Quest.W04.CorruptedHeart"))
        && BeforeReload.DefeatedBosses.Contains(TEXT("BoneBeast"))
        && BeforeReload.bDemoCompleted;
    Steps.Add(TEXT("progression_state_complete"), bStateComplete);

    const bool bSmokeSaveExists =
        UGameplayStatics::DoesSaveGameExist(RuntimeSmokeSlot, 0);
    Steps.Add(TEXT("smoke_save_exists"), bSmokeSaveExists);

    Runtime->BeginNewGame();
    const FNarisSaveState Cleared = Runtime->GetState();
    const bool bNewGameCleared =
        !Cleared.bDemoCompleted
        && Cleared.DefeatedBosses.IsEmpty()
        && Cleared.UnlockedCompanions.IsEmpty()
        && Cleared.UnlockedGates.IsEmpty()
        && Cleared.TriggeredNarratives.IsEmpty();
    Steps.Add(TEXT("new_game_clears_progression"), bNewGameCleared);

    const bool bLoad = Runtime->LoadState(RuntimeSmokeSlot);
    Steps.Add(TEXT("load_smoke_save"), bLoad);

    const FNarisSaveState AfterReload = Runtime->GetState();
    const bool bRoundTrip =
        AfterReload.CheckpointId == BeforeReload.CheckpointId
        && AfterReload.UnlockedLore.Contains(TEXT("W04_Lore_MemoryCrystal_0001"))
        && AfterReload.TriggeredNarratives.Contains(TEXT("W04_FirstWhisper"))
        && AfterReload.UnlockedGates.Contains(TEXT("W04_AshGate"))
        && AfterReload.UnlockedCompanions.Contains(TEXT("CelestialWolf"))
        && AfterReload.CompletedQuests.Contains(TEXT("Quest.W04.CorruptedHeart"))
        && AfterReload.DefeatedBosses.Contains(TEXT("BoneBeast"))
        && AfterReload.bDemoCompleted;
    Steps.Add(TEXT("save_load_round_trip"), bRoundTrip);

    bool bPassed = true;
    for (const TPair<FString, bool>& Pair : Steps)
    {
        bPassed &= Pair.Value;
    }

    Detail = bPassed
        ? TEXT("W04 runtime progression and save/load smoke passed")
        : TEXT("One or more W04 runtime smoke checks failed");

    FinishSmoke(bPassed, Steps, Detail);
    UGameplayStatics::DeleteGameInSlot(RuntimeSmokeSlot, 0);
}

void ANarisRuntimeSmokeDirector::FinishSmoke(
    bool bPassed,
    const TMap<FString, bool>& Steps,
    const FString& Detail
)
{
    TSharedRef<FJsonObject> Root = MakeShared<FJsonObject>();
    Root->SetStringField(
        TEXT("schema"),
        TEXT("naris.w04.runtime-smoke.v1")
    );
    Root->SetStringField(
        TEXT("status"),
        bPassed ? TEXT("pass") : TEXT("fail")
    );
    Root->SetStringField(TEXT("detail"), Detail);
    Root->SetStringField(TEXT("map"), GetWorld() ? GetWorld()->GetMapName() : TEXT(""));

    TSharedRef<FJsonObject> StepObject = MakeShared<FJsonObject>();
    for (const TPair<FString, bool>& Pair : Steps)
    {
        StepObject->SetBoolField(Pair.Key, Pair.Value);
    }
    Root->SetObjectField(TEXT("steps"), StepObject);

    FString Payload;
    const TSharedRef<TJsonWriter<>> Writer =
        TJsonWriterFactory<>::Create(&Payload);
    FJsonSerializer::Serialize(Root, Writer);

    const FString ReportPath = ResolveReportPath();
    IFileManager::Get().MakeDirectory(
        *FPaths::GetPath(ReportPath),
        true
    );

    const bool bWrote = FFileHelper::SaveStringToFile(
        Payload,
        *ReportPath,
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM
    );

    UE_LOG(
        LogTemp,
        Display,
        TEXT("NARIS_RUNTIME_SMOKE status=%s report=%s wrote=%s"),
        bPassed ? TEXT("pass") : TEXT("fail"),
        *ReportPath,
        bWrote ? TEXT("true") : TEXT("false")
    );

    FPlatformMisc::RequestExit(false);
}
