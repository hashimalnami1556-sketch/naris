// NAR_InventorySystem.cpp — تنفيذ نظام الجرد
#include "NAR_InventorySystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UNAR_InventorySystem::UNAR_InventorySystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f;
}

void UNAR_InventorySystem::BeginPlay()
{
	Super::BeginPlay();

	// تهيئة فتحات الجرد
	InventorySlots.Empty();
	for (int32 i = 0; i < InventorySlotCount; ++i)
	{
		FInventorySlot NewSlot;
		NewSlot.bIsEmpty = true;
		NewSlot.SlotIndex = i;
		InventorySlots.Add(NewSlot);
	}

	LoadInventory();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] نظام الجرد جاهز مع %d فتحة"), InventorySlotCount);
}

void UNAR_InventorySystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// تحديث الوزن بشكل دوري
	UpdateWeight();
}

// ============================================
// إدارة الجرد
// ============================================
bool UNAR_InventorySystem::AddItem(const FInventoryItem& Item, int32 Quantity)
{
	if (Quantity <= 0) return false;

	FInventoryItem ItemToAdd = Item;
	ItemToAdd.Quantity = Quantity;

	// محاولة إضافة إلى فتحة موجودة إذا كان العنصر قابلاً للتكديس
	if (ItemToAdd.bCanStack)
	{
		for (FInventorySlot& Slot : InventorySlots)
		{
			if (!Slot.bIsEmpty && Slot.Item.ItemID == ItemToAdd.ItemID)
			{
				int32 SpaceInSlot = Slot.Item.MaxStackSize - Slot.Item.Quantity;
				if (SpaceInSlot > 0)
				{
					int32 AddQuantity = FMath::Min(Quantity, SpaceInSlot);
					Slot.Item.Quantity += AddQuantity;
					Quantity -= AddQuantity;

					if (Quantity <= 0)
					{
						OnItemAdded.Broadcast(Item, ItemToAdd.Quantity);
						OnInventoryUpdated.Broadcast();
						UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] إضافة عنصر: %s (الكمية: %d)"),
							*Item.ItemName, ItemToAdd.Quantity);
						return true;
					}
				}
			}
		}
	}

	// إضافة إلى فتحة جديدة
	if (Quantity > 0)
	{
		int32 EmptySlotIndex = FindEmptySlot();
		if (EmptySlotIndex != -1)
		{
			InventorySlots[EmptySlotIndex].Item = ItemToAdd;
			InventorySlots[EmptySlotIndex].Item.Quantity = Quantity;
			InventorySlots[EmptySlotIndex].bIsEmpty = false;

			OnItemAdded.Broadcast(Item, Quantity);
			OnInventoryUpdated.Broadcast();
			UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] إضافة عنصر جديد: %s في فتحة %d"),
				*Item.ItemName, EmptySlotIndex);
			return true;
		}
		else
		{
			UE_LOG(LogTemp, Warning, TEXT("[NAR_Inventory] الجرد ممتلئ! لا يمكن إضافة %s"), *Item.ItemName);
			return false;
		}
	}

	return true;
}

bool UNAR_InventorySystem::RemoveItem(const FString& ItemID, int32 Quantity)
{
	if (Quantity <= 0) return false;

	for (FInventorySlot& Slot : InventorySlots)
	{
		if (!Slot.bIsEmpty && Slot.Item.ItemID == ItemID)
		{
			int32 RemoveQuantity = FMath::Min(Quantity, Slot.Item.Quantity);
			Slot.Item.Quantity -= RemoveQuantity;
			Quantity -= RemoveQuantity;

			if (Slot.Item.Quantity <= 0)
			{
				Slot.bIsEmpty = true;
			}

			if (Quantity <= 0)
			{
				OnItemRemoved.Broadcast(ItemID, RemoveQuantity);
				OnInventoryUpdated.Broadcast();
				UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] إزالة عنصر: %s (الكمية: %d)"),
					*ItemID, RemoveQuantity);
				return true;
			}
		}
	}

	return Quantity <= 0;
}

bool UNAR_InventorySystem::RemoveItemByIndex(int32 SlotIndex, int32 Quantity)
{
	if (SlotIndex < 0 || SlotIndex >= InventorySlots.Num() || InventorySlots[SlotIndex].bIsEmpty)
	{
		return false;
	}

	FString ItemID = InventorySlots[SlotIndex].Item.ItemID;
	return RemoveItem(ItemID, Quantity);
}

FInventoryItem UNAR_InventorySystem::GetItem(const FString& ItemID)
{
	for (const FInventorySlot& Slot : InventorySlots)
	{
		if (!Slot.bIsEmpty && Slot.Item.ItemID == ItemID)
		{
			return Slot.Item;
		}
	}

	return FInventoryItem();
}

FInventorySlot UNAR_InventorySystem::GetSlot(int32 SlotIndex)
{
	if (SlotIndex >= 0 && SlotIndex < InventorySlots.Num())
	{
		return InventorySlots[SlotIndex];
	}

	return FInventorySlot();
}

int32 UNAR_InventorySystem::GetItemCount(const FString& ItemID)
{
	int32 Count = 0;

	for (const FInventorySlot& Slot : InventorySlots)
	{
		if (!Slot.bIsEmpty && Slot.Item.ItemID == ItemID)
		{
			Count += Slot.Item.Quantity;
		}
	}

	return Count;
}

bool UNAR_InventorySystem::HasItem(const FString& ItemID)
{
	return GetItemCount(ItemID) > 0;
}

void UNAR_InventorySystem::ClearInventory()
{
	InventorySlots.Empty();
	CurrentWeight = 0.0f;
	OnInventoryUpdated.Broadcast();

	UE_LOG(LogTemp, Warning, TEXT("[NAR_Inventory] تم مسح الجرد بالكامل"));
}

// ============================================
// نقل وتحويل العناصر
// ============================================
bool UNAR_InventorySystem::MoveItem(int32 FromSlot, int32 ToSlot, int32 Quantity)
{
	if (FromSlot < 0 || FromSlot >= InventorySlots.Num() ||
		ToSlot < 0 || ToSlot >= InventorySlots.Num() ||
		FromSlot == ToSlot ||
		InventorySlots[FromSlot].bIsEmpty)
	{
		return false;
	}

	FInventoryItem ItemToMove = InventorySlots[FromSlot].Item;
	Quantity = FMath::Min(Quantity, ItemToMove.Quantity);

	if (InventorySlots[ToSlot].bIsEmpty)
	{
		InventorySlots[ToSlot].Item = ItemToMove;
		InventorySlots[ToSlot].Item.Quantity = Quantity;
		InventorySlots[ToSlot].bIsEmpty = false;

		InventorySlots[FromSlot].Item.Quantity -= Quantity;
		if (InventorySlots[FromSlot].Item.Quantity <= 0)
		{
			InventorySlots[FromSlot].bIsEmpty = true;
		}

		OnItemMoved.Broadcast(FromSlot, ToSlot);
		OnInventoryUpdated.Broadcast();
		return true;
	}
	else if (InventorySlots[ToSlot].Item.ItemID == ItemToMove.ItemID && InventorySlots[ToSlot].Item.bCanStack)
	{
		int32 SpaceInSlot = InventorySlots[ToSlot].Item.MaxStackSize - InventorySlots[ToSlot].Item.Quantity;
		int32 MoveQuantity = FMath::Min(Quantity, SpaceInSlot);

		InventorySlots[ToSlot].Item.Quantity += MoveQuantity;
		InventorySlots[FromSlot].Item.Quantity -= MoveQuantity;

		if (InventorySlots[FromSlot].Item.Quantity <= 0)
		{
			InventorySlots[FromSlot].bIsEmpty = true;
		}

		OnItemMoved.Broadcast(FromSlot, ToSlot);
		OnInventoryUpdated.Broadcast();
		return true;
	}

	return false;
}

bool UNAR_InventorySystem::SwapItems(int32 Slot1, int32 Slot2)
{
	if (Slot1 < 0 || Slot1 >= InventorySlots.Num() ||
		Slot2 < 0 || Slot2 >= InventorySlots.Num() ||
		Slot1 == Slot2)
	{
		return false;
	}

	FInventorySlot TempSlot = InventorySlots[Slot1];
	InventorySlots[Slot1] = InventorySlots[Slot2];
	InventorySlots[Slot2] = TempSlot;

	OnItemMoved.Broadcast(Slot1, Slot2);
	OnInventoryUpdated.Broadcast();

	UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] تبديل العناصر بين الفتحة %d والفتحة %d"), Slot1, Slot2);
	return true;
}

bool UNAR_InventorySystem::DropItem(int32 SlotIndex, int32 Quantity)
{
	if (!RemoveItemByIndex(SlotIndex, Quantity))
	{
		return false;
	}

	UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] إسقاط عنصر من الفتحة %d"), SlotIndex);
	return true;
}

// ============================================
// إدارة الوزن
// ============================================
float UNAR_InventorySystem::GetCurrentWeight() const
{
	return CurrentWeight;
}

float UNAR_InventorySystem::GetWeightPercentage() const
{
	return MaxInventoryWeight > 0 ? (CurrentWeight / MaxInventoryWeight) : 0.0f;
}

bool UNAR_InventorySystem::IsInventoryFull() const
{
	for (const FInventorySlot& Slot : InventorySlots)
	{
		if (Slot.bIsEmpty)
		{
			return false;
		}
	}

	return true;
}

void UNAR_InventorySystem::SetMaxWeight(float NewMaxWeight)
{
	MaxInventoryWeight = FMath::Max(NewMaxWeight, 1.0f);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] تعيين الحد الأقصى للوزن: %.1f"), MaxInventoryWeight);
}

void UNAR_InventorySystem::UpdateWeight()
{
	CurrentWeight = 0.0f;

	for (const FInventorySlot& Slot : InventorySlots)
	{
		if (!Slot.bIsEmpty)
		{
			CurrentWeight += Slot.Item.Weight * Slot.Item.Quantity;
		}
	}
}

// ============================================
// التجهيز والإزالة
// ============================================
bool UNAR_InventorySystem::EquipItem(int32 SlotIndex)
{
	if (SlotIndex < 0 || SlotIndex >= InventorySlots.Num() || InventorySlots[SlotIndex].bIsEmpty)
	{
		return false;
	}

	InventorySlots[SlotIndex].Item.bIsEquipped = true;
	OnItemEquipped.Broadcast(InventorySlots[SlotIndex].Item, true);
	OnInventoryUpdated.Broadcast();

	UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] تجهيز عنصر: %s"), *InventorySlots[SlotIndex].Item.ItemName);
	return true;
}

bool UNAR_InventorySystem::UnequipItem(int32 SlotIndex)
{
	if (SlotIndex < 0 || SlotIndex >= InventorySlots.Num() || InventorySlots[SlotIndex].bIsEmpty)
	{
		return false;
	}

	InventorySlots[SlotIndex].Item.bIsEquipped = false;
	OnItemEquipped.Broadcast(InventorySlots[SlotIndex].Item, false);
	OnInventoryUpdated.Broadcast();

	UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] إزالة تجهيز عنصر: %s"), *InventorySlots[SlotIndex].Item.ItemName);
	return true;
}

TArray<FInventorySlot> UNAR_InventorySystem::GetEquippedItems() const
{
	TArray<FInventorySlot> EquippedItems;

	for (const FInventorySlot& Slot : InventorySlots)
	{
		if (!Slot.bIsEmpty && Slot.Item.bIsEquipped)
		{
			EquippedItems.Add(Slot);
		}
	}

	return EquippedItems;
}

// ============================================
// البحث والفلترة
// ============================================
TArray<FInventorySlot> UNAR_InventorySystem::FindItemsByType(EItemType Type)
{
	TArray<FInventorySlot> FoundItems;

	for (const FInventorySlot& Slot : InventorySlots)
	{
		if (!Slot.bIsEmpty && Slot.Item.ItemType == Type)
		{
			FoundItems.Add(Slot);
		}
	}

	return FoundItems;
}

TArray<FInventorySlot> UNAR_InventorySystem::FindItemsByRarity(int32 Rarity)
{
	TArray<FInventorySlot> FoundItems;

	for (const FInventorySlot& Slot : InventorySlots)
	{
		if (!Slot.bIsEmpty && Slot.Item.Rarity == Rarity)
		{
			FoundItems.Add(Slot);
		}
	}

	return FoundItems;
}

int32 UNAR_InventorySystem::FindEmptySlot()
{
	for (int32 i = 0; i < InventorySlots.Num(); ++i)
	{
		if (InventorySlots[i].bIsEmpty)
		{
			return i;
		}
	}

	return -1;
}

// ============================================
// الحفظ والتحميل
// ============================================
void UNAR_InventorySystem::SaveInventory()
{
	// سيتم تطبيق الحفظ مع نظام الحفظ الرئيسي
	UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] حفظ الجرد"));
}

void UNAR_InventorySystem::LoadInventory()
{
	// سيتم تطبيق التحميل مع نظام الحفظ الرئيسي
	UE_LOG(LogTemp, Log, TEXT("[NAR_Inventory] تحميل الجرد"));
}
