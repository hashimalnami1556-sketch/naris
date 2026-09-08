// NAR_InteractionSystem.cpp — تنفيذ نظام التفاعلات
#include "NAR_InteractionSystem.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"

UNAR_InteractionSystem::UNAR_InteractionSystem()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickInterval = 0.1f;
}

void UNAR_InteractionSystem::BeginPlay()
{
    Super::BeginPlay();
    Initialize();
}

void UNAR_InteractionSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    InteractionCheckTimer += DeltaTime;

    if (InteractionCheckTimer >= InteractionCheckInterval)
    {
        InteractionCheckTimer = 0.0f;
    }
}

void UNAR_InteractionSystem::Initialize()
{
    RegisteredInteractables.Empty();
    ActiveWaystones.Empty();

    UE_LOG(LogTemp, Log, TEXT("[NAR_Interaction] نظام التفاعلات جاهز"));
}

// ============================================
// إدارة التفاعلات
// ============================================
void UNAR_InteractionSystem::RegisterInteractable(AActor* Actor, const FInteractableData& InteractionData)
{
    if (!Actor) return;

    RegisteredInteractables.Add(Actor, InteractionData);

    UE_LOG(LogTemp, Log, TEXT("[NAR_Interaction] تم تسجيل تفاعل: %s (%s)"),
        *Actor->GetName(), *InteractionData.DisplayName);
}

void UNAR_InteractionSystem::UnregisterInteractable(AActor* Actor)
{
    if (!Actor) return;

    RegisteredInteractables.Remove(Actor);
    ActiveWaystones.Remove(Actor);

    UE_LOG(LogTemp, Log, TEXT("[NAR_Interaction] تم إلغاء تسجيل تفاعل: %s"), *Actor->GetName());
}

void UNAR_InteractionSystem::TriggerInteraction(AActor* InteractableActor)
{
    if (!InteractableActor || !RegisteredInteractables.Contains(InteractableActor))
    {
        return;
    }

    FInteractableData* InteractionData = RegisteredInteractables.Find(InteractableActor);

    if (InteractionData && InteractionData->bOneTimeUse && InteractionData->bHasBeenUsed)
    {
        UE_LOG(LogTemp, Warning, TEXT("[NAR_Interaction] تفاعل تم استخدامه بالفعل: %s"),
            *InteractableActor->GetName());
        return;
    }

    OnInteractionTriggered.Broadcast(InteractableActor);

    switch (InteractionData->Type)
    {
        case EInteractionType::Waystone:
            InteractWithWaystone(InteractableActor);
            break;
        case EInteractionType::Chest:
            OpenChest(InteractableActor);
            break;
        case EInteractionType::Shard:
            CollectShard(InteractableActor);
            break;
        default:
            break;
    }

    if (InteractionData->bOneTimeUse)
    {
        InteractionData->bHasBeenUsed = true;
    }

    UE_LOG(LogTemp, Log, TEXT("[NAR_Interaction] تم تشغيل التفاعل: %s"),
        *InteractableActor->GetName());
}

// ============================================
// البحث عن التفاعلات
// ============================================
AActor* UNAR_InteractionSystem::FindNearestInteractable(FVector FromLocation, float SearchRadius)
{
    AActor* NearestActor = nullptr;
    float NearestDistance = SearchRadius;

    for (auto& Pair : RegisteredInteractables)
    {
        AActor* Actor = Pair.Key;
        if (!Actor) continue;

        float Distance = FVector::Dist(FromLocation, Actor->GetActorLocation());

        if (Distance < NearestDistance)
        {
            NearestDistance = Distance;
            NearestActor = Actor;
        }
    }

    return NearestActor;
}

void UNAR_InteractionSystem::GetNearbyInteractables(FVector FromLocation, float SearchRadius, TArray<AActor*>& OutInteractables)
{
    OutInteractables.Empty();

    for (auto& Pair : RegisteredInteractables)
    {
        AActor* Actor = Pair.Key;
        if (!Actor) continue;

        float Distance = FVector::Dist(FromLocation, Actor->GetActorLocation());

        if (Distance <= SearchRadius)
        {
            OutInteractables.Add(Actor);
        }
    }
}

bool UNAR_InteractionSystem::GetInteractableData(AActor* Actor, FInteractableData& OutData) const
{
    const FInteractableData* Data = RegisteredInteractables.Find(Actor);

    if (Data)
    {
        OutData = *Data;
        return true;
    }

    return false;
}

// ============================================
// نقاط الحفظ (Waystones)
// ============================================
void UNAR_InteractionSystem::InteractWithWaystone(AActor* WaystoneActor)
{
    if (!WaystoneActor) return;

    SetWaystoneActive(WaystoneActor, true);

    OnWaystoneActivated.Broadcast(WaystoneActor);

    UE_LOG(LogTemp, Warning, TEXT("[NAR_Interaction] تم تفعيل نقطة الحفظ: %s"),
        *WaystoneActor->GetName());
}

void UNAR_InteractionSystem::SetWaystoneActive(AActor* WaystoneActor, bool bActive)
{
    if (!WaystoneActor) return;

    if (bActive)
    {
        ActiveWaystones.Add(WaystoneActor);
    }
    else
    {
        ActiveWaystones.Remove(WaystoneActor);
    }
}

bool UNAR_InteractionSystem::IsWaystoneActive(AActor* WaystoneActor) const
{
    return ActiveWaystones.Contains(WaystoneActor);
}

void UNAR_InteractionSystem::GetAllWaystones(TArray<AActor*>& OutWaystones) const
{
    OutWaystones.Empty();

    for (auto& Pair : RegisteredInteractables)
    {
        if (Pair.Value.Type == EInteractionType::Waystone)
        {
            OutWaystones.Add(Pair.Key);
        }
    }
}

void UNAR_InteractionSystem::TeleportToWaystone(AActor* SourceWaystone, AActor* DestinationWaystone)
{
    if (!SourceWaystone || !DestinationWaystone) return;

    if (!IsWaystoneActive(SourceWaystone) || !IsWaystoneActive(DestinationWaystone))
    {
        UE_LOG(LogTemp, Warning, TEXT("[NAR_Interaction] لا يمكن النقل - نقطة حفظ غير مفعلة"));
        return;
    }

    // البحث عن اللاعب والنقل
    ACharacter* PlayerCharacter = UGameplayStatics::GetPlayerCharacter(GetWorld(), 0);

    if (PlayerCharacter)
    {
        FVector DestinationLocation = DestinationWaystone->GetActorLocation();
        PlayerCharacter->SetActorLocation(DestinationLocation + FVector(0, 0, 100), false, nullptr, ETeleportType::TeleportPhysics);

        UE_LOG(LogTemp, Log, TEXT("[NAR_Interaction] تم النقل من %s إلى %s"),
            *SourceWaystone->GetName(), *DestinationWaystone->GetName());
    }
}

// ============================================
// الصناديق (Chests)
// ============================================
void UNAR_InteractionSystem::OpenChest(AActor* ChestActor)
{
    if (!ChestActor || !RegisteredInteractables.Contains(ChestActor)) return;

    FInteractableData* ChestData = RegisteredInteractables.Find(ChestActor);

    if (ChestData)
    {
        OnChestOpened.Broadcast(ChestActor, ChestData->Reward);

        UE_LOG(LogTemp, Warning, TEXT("[NAR_Interaction] تم فتح الصندوق: %s (شظايا: %d)"),
            *ChestActor->GetName(), ChestData->Reward.ShardCount);
    }
}

void UNAR_InteractionSystem::SetChestLocked(AActor* ChestActor, bool bLocked)
{
    if (!ChestActor || !RegisteredInteractables.Contains(ChestActor)) return;

    FInteractableData* ChestData = RegisteredInteractables.Find(ChestActor);

    if (ChestData)
    {
        ChestData->bOneTimeUse = bLocked;
    }
}

bool UNAR_InteractionSystem::IsChestLocked(AActor* ChestActor) const
{
    const FInteractableData* ChestData = RegisteredInteractables.Find(ChestActor);

    return ChestData ? ChestData->bOneTimeUse : false;
}

bool UNAR_InteractionSystem::IsChestEmpty(AActor* ChestActor) const
{
    const FInteractableData* ChestData = RegisteredInteractables.Find(ChestActor);

    if (ChestData)
    {
        return ChestData->Reward.ShardCount == 0 &&
               ChestData->Reward.XPAmount == 0 &&
               ChestData->Reward.Items.Num() == 0;
    }

    return true;
}

// ============================================
// الشظايا (Shards)
// ============================================
void UNAR_InteractionSystem::CollectShard(AActor* ShardActor)
{
    if (!ShardActor || !RegisteredInteractables.Contains(ShardActor)) return;

    FInteractableData* ShardData = RegisteredInteractables.Find(ShardActor);

    if (ShardData)
    {
        OnShardCollected.Broadcast(ShardData->Reward.ShardCount);

        UE_LOG(LogTemp, Warning, TEXT("[NAR_Interaction] تم جمع شظية: %d"),
            ShardData->Reward.ShardCount);

        // إزالة الشظية بعد الجمع
        ShardActor->Destroy();
    }
}

void UNAR_InteractionSystem::CreateShardPickup(FVector Location, int32 ShardAmount)
{
    // سيتم تنفيذ هذا في Blueprint حيث سيتم إنشاء الـ Actor
    UE_LOG(LogTemp, Log, TEXT("[NAR_Interaction] إنشاء حقيبة شظايا في الموقع (عدد: %d)"),
        ShardAmount);
}
