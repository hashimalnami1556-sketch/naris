#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NarisInteractable.h"
#include "NarisMemoryCrystal.generated.h"

class USceneComponent;
class UStaticMeshComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FNarisMemoryCrystalActivated);

UCLASS(Blueprintable)
class NARIS_W04_API ANarisMemoryCrystal : public AActor, public INarisInteractable
{
    GENERATED_BODY()

public:
    ANarisMemoryCrystal();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Memory")
    TObjectPtr<USceneComponent> SceneRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Memory")
    TObjectPtr<UStaticMeshComponent> Mesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Memory")
    FString AssetId = TEXT("NARIS-W04-PRP-MEMORYCRYSTAL-0001");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Memory")
    FString LoreId = TEXT("W04_Lore_MemoryCrystal_0001");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Memory")
    FString NarrativeId = TEXT("W04_FirstWhisper");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Memory")
    FString QuestId = TEXT("Quest.W04.CorruptedHeart");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Memory")
    int32 QuestStep = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Memory")
    FString AutoSaveSlot = TEXT("NARIS_Auto");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Memory")
    bool bOneShot = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Memory")
    bool bAutoSave = true;

    UPROPERTY(BlueprintAssignable, Category="NARIS|Memory")
    FNarisMemoryCrystalActivated OnActivated;

    UFUNCTION(BlueprintCallable, Category="NARIS|Memory")
    bool ActivateMemory(AActor* InstigatorActor);

    virtual bool Interact_Implementation(AActor* InstigatorActor) override;
    virtual FText GetInteractionPrompt_Implementation() const override;
};
