// NAR_InventorySystem.h — نظام الجرد
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_InventorySystem.generated.h"

// ============================================
// أنواع العناصر
// ============================================
UENUM(BlueprintType)
enum class EItemType : uint8
{
	Weapon			UMETA(DisplayName = "سلاح"),
	Armor			UMETA(DisplayName = "دروع"),
	Potion			UMETA(DisplayName = "جرعة"),
	Ingredient		UMETA(DisplayName = "مكون"),
	Artifact		UMETA(DisplayName = "قطعة أثرية"),
	Consumable		UMETA(DisplayName = "قابل للاستهلاك"),
	QuestItem		UMETA(DisplayName = "عنصر مهمة"),
	Gem				UMETA(DisplayName = "جوهرة")
};

// ============================================
// بيانات العنصر
// ============================================
USTRUCT(BlueprintType)
struct FInventoryItem
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	FString ItemID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	FString ItemName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	FString Description = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	EItemType ItemType = EItemType::Consumable;

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	int32 Quantity = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	int32 MaxStackSize = 64;

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	int32 Weight = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	int32 SellPrice = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	bool bCanStack = true;

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	bool bIsEquipped = false;

	UPROPERTY(BlueprintReadWrite, Category = "Item")
	int32 Rarity = 1; // 1 = عادي، 2 = نادر، 3 = نادر جداً، 4 = أسطوري
};

// ============================================
// فتحة الجرد
// ============================================
USTRUCT(BlueprintType)
struct FInventorySlot
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Slot")
	FInventoryItem Item;

	UPROPERTY(BlueprintReadWrite, Category = "Slot")
	bool bIsEmpty = true;

	UPROPERTY(BlueprintReadWrite, Category = "Slot")
	int32 SlotIndex = 0;
};

// ============================================
// نظام الجرد
// ============================================
/**
 * UNAR_InventorySystem — نظام الجرد
 * يدير: العناصر + التخزين + الوزن + التجهيز
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_InventorySystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_InventorySystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ============================================
	// إدارة الجرد
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory")
	bool AddItem(const FInventoryItem& Item, int32 Quantity = 1);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory")
	bool RemoveItem(const FString& ItemID, int32 Quantity = 1);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory")
	bool RemoveItemByIndex(int32 SlotIndex, int32 Quantity = 1);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory")
	FInventoryItem GetItem(const FString& ItemID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory")
	FInventorySlot GetSlot(int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory")
	int32 GetItemCount(const FString& ItemID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory")
	bool HasItem(const FString& ItemID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory")
	void ClearInventory();

	// ============================================
	// نقل وتحويل العناصر
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Transfer")
	bool MoveItem(int32 FromSlot, int32 ToSlot, int32 Quantity = 1);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Transfer")
	bool SwapItems(int32 Slot1, int32 Slot2);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Transfer")
	bool DropItem(int32 SlotIndex, int32 Quantity = 1);

	// ============================================
	// إدارة الوزن
	// ============================================
	UFUNCTION(BlueprintPure, Category = "NAR|Inventory|Weight")
	float GetCurrentWeight() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Inventory|Weight")
	float GetMaxWeight() const { return MaxInventoryWeight; }

	UFUNCTION(BlueprintPure, Category = "NAR|Inventory|Weight")
	float GetWeightPercentage() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Inventory|Weight")
	bool IsInventoryFull() const;

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Weight")
	void SetMaxWeight(float NewMaxWeight);

	// ============================================
	// التجهيز والإزالة
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Equipment")
	bool EquipItem(int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Equipment")
	bool UnequipItem(int32 SlotIndex);

	UFUNCTION(BlueprintPure, Category = "NAR|Inventory|Equipment")
	TArray<FInventorySlot> GetEquippedItems() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Inventory|Equipment")
	int32 GetEquipmentSlots() const { return EquipmentSlots; }

	// ============================================
	// البحث والفلترة
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Search")
	TArray<FInventorySlot> FindItemsByType(EItemType Type);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Search")
	TArray<FInventorySlot> FindItemsByRarity(int32 Rarity);

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Search")
	int32 FindEmptySlot();

	// ============================================
	// الحفظ والتحميل
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Save")
	void SaveInventory();

	UFUNCTION(BlueprintCallable, Category = "NAR|Inventory|Save")
	void LoadInventory();

	// ============================================
	// الحصول على البيانات
	// ============================================
	UFUNCTION(BlueprintPure, Category = "NAR|Inventory|Data")
	TArray<FInventorySlot> GetAllItems() const { return InventorySlots; }

	UFUNCTION(BlueprintPure, Category = "NAR|Inventory|Data")
	int32 GetSlotCount() const { return InventorySlots.Num(); }

	// ============================================
	// الأحداث
	// ============================================
	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnItemAdded, FInventoryItem, Item, int32, Quantity);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Inventory|Events")
	FOnItemAdded OnItemAdded;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnItemRemoved, FString, ItemID, int32, Quantity);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Inventory|Events")
	FOnItemRemoved OnItemRemoved;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnItemMoved, int32, FromSlot, int32, ToSlot);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Inventory|Events")
	FOnItemMoved OnItemMoved;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnItemEquipped, FInventoryItem, Item, bool, bEquipped);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Inventory|Events")
	FOnItemEquipped OnItemEquipped;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnInventoryUpdated);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Inventory|Events")
	FOnInventoryUpdated OnInventoryUpdated;

protected:
	// ============================================
	// بيانات الجرد
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Inventory|Data")
	TArray<FInventorySlot> InventorySlots;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Inventory|Settings")
	int32 InventorySlotCount = 40;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Inventory|Settings")
	float MaxInventoryWeight = 100.0f;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Inventory|Settings")
	int32 EquipmentSlots = 6;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Inventory|Data")
	float CurrentWeight = 0.0f;

private:
	void UpdateWeight();
};
