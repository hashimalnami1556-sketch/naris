// NAR_InteractionSystem.h — نظام التفاعلات
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_InteractionSystem.generated.h"

// ============================================
// أنواع التفاعلات
// ============================================
UENUM(BlueprintType)
enum class EInteractionType : uint8
{
    Waystone        UMETA(DisplayName = "نقطة حفظ"),
    Chest           UMETA(DisplayName = "صندوق"),
    Shard           UMETA(DisplayName = "شظية"),
    Torch           UMETA(DisplayName = "مشعل"),
    Door            UMETA(DisplayName = "باب"),
    NPC             UMETA(DisplayName = "شخصية"),
    Crafting        UMETA(DisplayName = "صياغة"),
    Altar           UMETA(DisplayName = "مذبح")
};

// ============================================
// بيانات الجائزة
// ============================================
USTRUCT(BlueprintType)
struct FRewardData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Reward")
    int32 ShardCount = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Reward")
    int32 XPAmount = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Reward")
    TArray<FString> Items;

    UPROPERTY(BlueprintReadWrite, Category = "Reward")
    int32 HealthRestore = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Reward")
    int32 EnergyRestore = 0;
};

// ============================================
// بيانات التفاعل
// ============================================
USTRUCT(BlueprintType)
struct FInteractableData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Interaction")
    EInteractionType Type = EInteractionType::Waystone;

    UPROPERTY(BlueprintReadWrite, Category = "Interaction")
    FString DisplayName = TEXT("تفاعل");

    UPROPERTY(BlueprintReadWrite, Category = "Interaction")
    FString Description = TEXT("");

    UPROPERTY(BlueprintReadWrite, Category = "Interaction")
    float InteractionDistance = 200.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Interaction")
    float InteractionDuration = 0.5f;

    UPROPERTY(BlueprintReadWrite, Category = "Interaction")
    bool bOneTimeUse = false;

    UPROPERTY(BlueprintReadWrite, Category = "Interaction")
    FRewardData Reward;

    UPROPERTY(BlueprintReadWrite, Category = "Interaction")
    bool bHasBeenUsed = false;
};

/**
 * UNAR_InteractionSystem — نظام التفاعلات
 * يدير: التفاعلات مع البيئة (صناديق، نقاط حفظ، شظايا، إلخ)
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_InteractionSystem : public UActorComponent
{
    GENERATED_BODY()

public:
    UNAR_InteractionSystem();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    // ============================================
    // التهيئة
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction")
    void Initialize();

    // ============================================
    // إدارة التفاعلات
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction")
    void RegisterInteractable(AActor* Actor, const FInteractableData& InteractionData);

    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction")
    void UnregisterInteractable(AActor* Actor);

    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction")
    void TriggerInteraction(AActor* InteractableActor);

    // ============================================
    // البحث عن التفاعلات
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction")
    AActor* FindNearestInteractable(FVector FromLocation, float SearchRadius = 500.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction")
    void GetNearbyInteractables(FVector FromLocation, float SearchRadius, TArray<AActor*>& OutInteractables);

    UFUNCTION(BlueprintPure, Category = "NAR|Interaction")
    bool GetInteractableData(AActor* Actor, FInteractableData& OutData) const;

    // ============================================
    // نقاط الحفظ (Waystones)
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction|Waystone")
    void InteractWithWaystone(AActor* WaystoneActor);

    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction|Waystone")
    void SetWaystoneActive(AActor* WaystoneActor, bool bActive);

    UFUNCTION(BlueprintPure, Category = "NAR|Interaction|Waystone")
    bool IsWaystoneActive(AActor* WaystoneActor) const;

    UFUNCTION(BlueprintPure, Category = "NAR|Interaction|Waystone")
    void GetAllWaystones(TArray<AActor*>& OutWaystones) const;

    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction|Waystone")
    void TeleportToWaystone(AActor* SourceWaystone, AActor* DestinationWaystone);

    // ============================================
    // الصناديق (Chests)
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction|Chest")
    void OpenChest(AActor* ChestActor);

    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction|Chest")
    void SetChestLocked(AActor* ChestActor, bool bLocked);

    UFUNCTION(BlueprintPure, Category = "NAR|Interaction|Chest")
    bool IsChestLocked(AActor* ChestActor) const;

    UFUNCTION(BlueprintPure, Category = "NAR|Interaction|Chest")
    bool IsChestEmpty(AActor* ChestActor) const;

    // ============================================
    // الشظايا (Shards)
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction|Shard")
    void CollectShard(AActor* ShardActor);

    UFUNCTION(BlueprintCallable, Category = "NAR|Interaction|Shard")
    void CreateShardPickup(FVector Location, int32 ShardAmount = 1);

    // ============================================
    // أحداث
    // ============================================
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnInteractionTriggered, AActor*, InteractableActor);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Interaction|Events")
    FOnInteractionTriggered OnInteractionTriggered;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnWaystoneActivated, AActor*, WaystoneActor);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Interaction|Events")
    FOnWaystoneActivated OnWaystoneActivated;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnChestOpened, AActor*, ChestActor, FRewardData, Reward);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Interaction|Events")
    FOnChestOpened OnChestOpened;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnShardCollected, int32, ShardAmount);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Interaction|Events")
    FOnShardCollected OnShardCollected;

protected:
    UPROPERTY(BlueprintReadOnly, Category = "NAR|Interaction|Data")
    TMap<AActor*, FInteractableData> RegisteredInteractables;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|Interaction|Data")
    TSet<AActor*> ActiveWaystones;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Interaction|Settings")
    float InteractionCheckInterval = 0.1f;

private:
    float InteractionCheckTimer = 0.0f;
};
