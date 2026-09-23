#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NarisInteractable.h"
#include "NarisAshGate.generated.h"

class USceneComponent;
class UStaticMeshComponent;
class UBoxComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FNarisAshGateEvent);

UCLASS(Blueprintable)
class NARIS_W04_API ANarisAshGate : public AActor, public INarisInteractable
{
    GENERATED_BODY()

public:
    ANarisAshGate();

    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|AshGate")
    TObjectPtr<USceneComponent> SceneRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|AshGate")
    TObjectPtr<UStaticMeshComponent> GateMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|AshGate")
    TObjectPtr<UBoxComponent> Blocker;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|AshGate")
    FString AssetId = TEXT("NARIS-W04-PRP-ASHGATE-0001");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|AshGate")
    FString GateId = TEXT("W04_AshGate");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|AshGate")
    FString RequiredNarrativeId = TEXT("W04_FirstWhisper");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|AshGate")
    FString AutoSaveSlot = TEXT("NARIS_Auto");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|AshGate")
    bool bAutoSave = true;

    UPROPERTY(BlueprintAssignable, Category="NARIS|AshGate")
    FNarisAshGateEvent OnGateUnlocked;

    UPROPERTY(BlueprintAssignable, Category="NARIS|AshGate")
    FNarisAshGateEvent OnGateLocked;

    UFUNCTION(BlueprintCallable, Category="NARIS|AshGate")
    bool TryUnlockGate(AActor* InstigatorActor);

    UFUNCTION(BlueprintCallable, Category="NARIS|AshGate")
    void ApplyUnlockedState();

    virtual bool Interact_Implementation(AActor* InstigatorActor) override;
    virtual FText GetInteractionPrompt_Implementation() const override;
};
