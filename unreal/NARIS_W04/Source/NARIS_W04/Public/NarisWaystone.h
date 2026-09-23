#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NarisInteractable.h"
#include "NarisWaystone.generated.h"

class USceneComponent;
class UStaticMeshComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FNarisWaystoneActivated);

UCLASS(Blueprintable)
class NARIS_W04_API ANarisWaystone : public AActor, public INarisInteractable
{
    GENERATED_BODY()

public:
    ANarisWaystone();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Waystone")
    TObjectPtr<USceneComponent> SceneRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Waystone")
    TObjectPtr<UStaticMeshComponent> Mesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Waystone")
    FString AssetId = TEXT("NARIS-W04-PRP-WAYSTONE-0001");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Waystone")
    FString WaystoneId = TEXT("W04_Waystone_0001");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Waystone")
    FString CheckpointId = TEXT("W04_Waystone_0001");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Waystone")
    FString MapId = TEXT("W04_AshenForest");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Waystone")
    FString AutoSaveSlot = TEXT("NARIS_Auto");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Waystone")
    bool bAutoSave = true;

    UPROPERTY(BlueprintAssignable, Category="NARIS|Waystone")
    FNarisWaystoneActivated OnActivated;

    UFUNCTION(BlueprintCallable, Category="NARIS|Waystone")
    bool ActivateWaystone(AActor* InstigatorActor);

    virtual bool Interact_Implementation(AActor* InstigatorActor) override;
    virtual FText GetInteractionPrompt_Implementation() const override;
};
