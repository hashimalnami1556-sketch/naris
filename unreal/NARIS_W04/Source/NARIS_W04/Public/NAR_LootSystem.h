// NAR_LootSystem.h — نظام الغنائم المتقدم
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_LootSystem.generated.h"

UENUM(BlueprintType)
enum class ELootRarity : uint8
{
	Common			UMETA(DisplayName = "عام"),
	Uncommon		UMETA(DisplayName = "نادر"),
	Rare			UMETA(DisplayName = "نادر جداً"),
	Epic			UMETA(DisplayName = "ملحمي"),
	Legendary		UMETA(DisplayName = "أسطوري")
};

UENUM(BlueprintType)
enum class ELootType : uint8
{
	Equipment		UMETA(DisplayName = "معدات"),
	Consumable		UMETA(DisplayName = "استهلاكي"),
	Material		UMETA(DisplayName = "مادة"),
	Quest			UMETA(DisplayName = "مهمة"),
	Currency		UMETA(DisplayName = "عملة"),
	Crafting		UMETA(DisplayName = "صناعة"),
	Rare			UMETA(DisplayName = "نادر"),
	Artifact		UMETA(DisplayName = "أثري")
};

USTRUCT(BlueprintType)
struct FMagicProperty
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	FString PropertyName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	int32 PropertyValue = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	float PropertyChance = 0.5f;
};

USTRUCT(BlueprintType)
struct FLootItem
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	FString ItemID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	FString ItemName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	ELootType LootType = ELootType::Consumable;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	ELootRarity Rarity = ELootRarity::Common;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	int32 Value = 10;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	float Durability = 100.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	float MaxDurability = 100.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	TArray<FMagicProperty> MagicProperties;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	bool bIsUnique = false;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	int32 Quantity = 1;
};

USTRUCT(BlueprintType)
struct FLootTable
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	FString TableID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	TArray<FLootItem> LootItems;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	TArray<float> DropChances;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	int32 MinItems = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	int32 MaxItems = 3;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	float RareItemChance = 0.1f;
};

USTRUCT(BlueprintType)
struct FLootDrop
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	TArray<FLootItem> DroppedItems;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	FVector DropLocation = FVector::ZeroVector;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	float ExpirationTime = 300.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Loot")
	float CreationTime = 0.0f;
};

UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_LootSystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_LootSystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	UFUNCTION(BlueprintCallable, Category = "NAR|Loot")
	bool RegisterLootTable(const FLootTable& LootTable);

	UFUNCTION(BlueprintCallable, Category = "NAR|Loot")
	FLootDrop GenerateLoot(const FString& TableID, FVector DropLocation);

	UFUNCTION(BlueprintCallable, Category = "NAR|Loot")
	bool AddLootToLocation(FVector Location, const FLootDrop& Loot);

	UFUNCTION(BlueprintCallable, Category = "NAR|Loot")
	TArray<FLootItem> GetLootAtLocation(FVector Location);

	UFUNCTION(BlueprintCallable, Category = "NAR|Loot")
	bool PickupLoot(FVector Location, const FLootItem& Item);

	UFUNCTION(BlueprintCallable, Category = "NAR|Loot")
	bool ApplyMagicProperty(FLootItem& Item, const FMagicProperty& Property);

	UFUNCTION(BlueprintCallable, Category = "NAR|Loot")
	ELootRarity GetItemRarity(const FString& ItemID);

	UFUNCTION(BlueprintPure, Category = "NAR|Loot")
	int32 GetTotalLootDropped() const { return TotalLootDropped; }

	UFUNCTION(BlueprintCallable, Category = "NAR|Loot")
	void SaveLootData();

	UFUNCTION(BlueprintCallable, Category = "NAR|Loot")
	void LoadLootData();

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnLootGenerated, FLootDrop, Loot);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Loot|Events")
	FOnLootGenerated OnLootGenerated;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnRareItemFound, FLootItem, Item);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Loot|Events")
	FOnRareItemFound OnRareItemFound;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnLootPickedUp, FLootItem, Item);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Loot|Events")
	FOnLootPickedUp OnLootPickedUp;

protected:
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Loot|Data")
	TMap<FString, FLootTable> LootTables;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Loot|Data")
	TMap<FVector, FLootDrop> LocationLoot;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Loot|Data")
	int32 TotalLootDropped = 0;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Loot|Settings")
	float LootExpirationTime = 300.0f;

private:
	FLootItem GenerateLootItem(const FLootTable& Table);
	void UpdateLootLocations(float DeltaTime);
};
