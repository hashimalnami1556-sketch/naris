#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisRoadNetworkComponent.generated.h"
USTRUCT(BlueprintType) struct FNarisRoadEdge { GENERATED_BODY() UPROPERTY(EditAnywhere,BlueprintReadWrite) FName From; UPROPERTY(EditAnywhere,BlueprintReadWrite) FName To; UPROPERTY(EditAnywhere,BlueprintReadWrite) float Cost=1.f; UPROPERTY(EditAnywhere,BlueprintReadWrite) bool bDangerous=false; };
UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent)) class NARISCORE_API UNarisRoadNetworkComponent: public UActorComponent { GENERATED_BODY() public: UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FNarisRoadEdge> Edges; UFUNCTION(BlueprintPure) TArray<FName> GetNeighbors(FName Node) const; };
