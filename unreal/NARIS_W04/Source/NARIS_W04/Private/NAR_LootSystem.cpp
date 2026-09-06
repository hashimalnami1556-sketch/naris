// NAR_LootSystem.cpp — تنفيذ نظام الغنائم
#include "NAR_LootSystem.h"
#include "Engine/World.h"
#include "Math/UnrealMathUtility.h"

UNAR_LootSystem::UNAR_LootSystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.5f;
}

void UNAR_LootSystem::BeginPlay()
{
	Super::BeginPlay();
	LoadLootData();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Loot] نظام الغنائم جاهز"));
}

void UNAR_LootSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	UpdateLootLocations(DeltaTime);
}

bool UNAR_LootSystem::RegisterLootTable(const FLootTable& LootTable)
{
	if (LootTables.Contains(LootTable.TableID))
	{
		return false;
	}

	LootTables.Add(LootTable.TableID, LootTable);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Loot] تسجيل جدول غنائم: %s"), *LootTable.TableID);

	return true;
}

FLootDrop UNAR_LootSystem::GenerateLoot(const FString& TableID, FVector DropLocation)
{
	FLootDrop Drop;
	Drop.DropLocation = DropLocation;
	Drop.CreationTime = GetWorld()->GetTimeSeconds();

	if (!LootTables.Contains(TableID))
	{
		return Drop;
	}

	const FLootTable& Table = LootTables[TableID];
	int32 ItemCount = FMath::RandRange(Table.MinItems, Table.MaxItems);

	for (int32 i = 0; i < ItemCount; i++)
	{
		FLootItem Item = GenerateLootItem(Table);
		Drop.DroppedItems.Add(Item);

		if (Item.Rarity == ELootRarity::Epic || Item.Rarity == ELootRarity::Legendary)
		{
			OnRareItemFound.Broadcast(Item);
		}
	}

	OnLootGenerated.Broadcast(Drop);
	TotalLootDropped++;

	return Drop;
}

bool UNAR_LootSystem::AddLootToLocation(FVector Location, const FLootDrop& Loot)
{
	LocationLoot.Add(Location, Loot);
	return true;
}

TArray<FLootItem> UNAR_LootSystem::GetLootAtLocation(FVector Location)
{
	TArray<FLootItem> Items;

	if (LocationLoot.Contains(Location))
	{
		Items = LocationLoot[Location].DroppedItems;
	}

	return Items;
}

bool UNAR_LootSystem::PickupLoot(FVector Location, const FLootItem& Item)
{
	if (LocationLoot.Contains(Location))
	{
		FLootDrop& Drop = LocationLoot[Location];
		Drop.DroppedItems.Remove(Item);

		OnLootPickedUp.Broadcast(Item);
		UE_LOG(LogTemp, Log, TEXT("[NAR_Loot] التقاط غنيمة: %s"), *Item.ItemName);

		return true;
	}

	return false;
}

bool UNAR_LootSystem::ApplyMagicProperty(FLootItem& Item, const FMagicProperty& Property)
{
	if (FMath::Rand() % 100 < Property.PropertyChance * 100.0f)
	{
		Item.MagicProperties.Add(Property);
		Item.Value = FMath::RoundToInt(Item.Value * 1.5f);
		return true;
	}

	return false;
}

ELootRarity UNAR_LootSystem::GetItemRarity(const FString& ItemID)
{
	for (const auto& Pair : LootTables)
	{
		for (const FLootItem& Item : Pair.Value.LootItems)
		{
			if (Item.ItemID == ItemID)
			{
				return Item.Rarity;
			}
		}
	}

	return ELootRarity::Common;
}

void UNAR_LootSystem::SaveLootData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Loot] حفظ بيانات الغنائم"));
}

void UNAR_LootSystem::LoadLootData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Loot] تحميل بيانات الغنائم"));
}

FLootItem UNAR_LootSystem::GenerateLootItem(const FLootTable& Table)
{
	if (Table.LootItems.Num() == 0)
	{
		return FLootItem();
	}

	int32 Index = FMath::RandRange(0, Table.LootItems.Num() - 1);
	FLootItem Item = Table.LootItems[Index];

	// حساب الندرة العشوائية
	float RareRoll = (float)FMath::Rand() / RAND_MAX;
	if (RareRoll < Table.RareItemChance)
	{
		Item.Rarity = ELootRarity::Legendary;
		Item.Value = FMath::RoundToInt(Item.Value * 5.0f);
		Item.bIsUnique = true;
	}
	else if (RareRoll < Table.RareItemChance * 3.0f)
	{
		Item.Rarity = ELootRarity::Epic;
		Item.Value = FMath::RoundToInt(Item.Value * 2.5f);
	}

	return Item;
}

void UNAR_LootSystem::UpdateLootLocations(float DeltaTime)
{
	TArray<FVector> ExpiredLocations;

	for (auto& Pair : LocationLoot)
	{
		Pair.Value.ExpirationTime -= DeltaTime;

		if (Pair.Value.ExpirationTime <= 0.0f)
		{
			ExpiredLocations.Add(Pair.Key);
		}
	}

	for (FVector Location : ExpiredLocations)
	{
		LocationLoot.Remove(Location);
	}
}
