#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisInventoryComponent.generated.h"
USTRUCT(BlueprintType) struct FNarisItemStack { GENERATED_BODY() UPROPERTY(EditAnywhere,BlueprintReadWrite) FName ItemID; UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 Quantity=1; };
UCLASS(ClassGroup=(NARIS),meta=(BlueprintSpawnableComponent)) class NARISCORE_API UNarisInventoryComponent: public UActorComponent { GENERATED_BODY() public: UPROPERTY(SaveGame,BlueprintReadOnly) TArray<FNarisItemStack> Items; UFUNCTION(BlueprintCallable) bool AddItem(FName ID,int32 Qty); UFUNCTION(BlueprintCallable) bool RemoveItem(FName ID,int32 Qty); };
