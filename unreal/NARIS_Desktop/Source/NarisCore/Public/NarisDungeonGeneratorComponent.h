#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisDungeonGeneratorComponent.generated.h"

USTRUCT(BlueprintType)
struct FNarisDungeonRoom
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) int32 ID = 0;
    UPROPERTY(BlueprintReadOnly) FIntPoint Grid = FIntPoint::ZeroValue;
    UPROPERTY(BlueprintReadOnly) bool bBoss = false;
};

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisDungeonGeneratorComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable)
    TArray<FNarisDungeonRoom> GenerateLayout(int32 Seed, int32 MinRooms, int32 MaxRooms, float BranchChance);
};
