#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisInteractable.h"
#include "CelestialWolf.generated.h"

UENUM(BlueprintType)
enum class ENarisWolfMode : uint8
{
    Follow,
    Guard,
    Attack,
    Track,
    EchoLink
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FNarisWolfBonded);

UCLASS(Blueprintable)
class NARIS_W04_API ACelestialWolf : public ACharacter, public INarisInteractable
{
    GENERATED_BODY()

public:
    ACelestialWolf();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    ENarisWolfMode Mode = ENarisWolfMode::Guard;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    float FollowDistance = 260.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    float FollowSpeed = 560.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    FString CompanionId = TEXT("CelestialWolf");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    FString RequiredGateId = TEXT("W04_AshGate");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    FString AutoSaveSlot = TEXT("NARIS_Auto");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    bool bAutoSave = true;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Companion")
    bool bBonded = false;

    UPROPERTY(BlueprintAssignable, Category="Companion")
    FNarisWolfBonded OnBonded;

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion")
    void SetMode(ENarisWolfMode NewMode);

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion")
    void EchoLink();

    UFUNCTION(BlueprintCallable, Category="NARIS|Companion")
    bool BondWithPlayer(AActor* InstigatorActor);

    virtual bool Interact_Implementation(AActor* InstigatorActor) override;
    virtual FText GetInteractionPrompt_Implementation() const override;
};
