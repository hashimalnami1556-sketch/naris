#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/PrimaryDataAsset.h"
#include "NarisPresentationComponent.generated.h"

class UNiagaraSystem;
class USoundBase;
class UCameraShakeBase;

USTRUCT(BlueprintType)
struct FNarisPresentationCue
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    FName CueId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    TObjectPtr<UNiagaraSystem> NiagaraSystem = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    TObjectPtr<USoundBase> Sound = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    TSubclassOf<UCameraShakeBase> CameraShake;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    float VolumeMultiplier = 1.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    float PitchMultiplier = 1.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    float ShakeInnerRadius = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    float ShakeOuterRadius = 1800.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    float ShakeFalloff = 1.f;
};

UCLASS(BlueprintType)
class NARIS_W04_API UNarisPresentationProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    TArray<FNarisPresentationCue> Cues;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(
    FNarisPresentationCueTriggered,
    FName,
    CueId,
    FVector,
    WorldLocation
);

UCLASS(ClassGroup=(NARIS), Blueprintable, meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UNarisPresentationComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UNarisPresentationComponent();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    TObjectPtr<UNarisPresentationProfile> Profile = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    FSoftObjectPath DefaultProfilePath;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    bool bAutoLoadDefaultProfile = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Presentation")
    TArray<FNarisPresentationCue> Cues;

    UPROPERTY(BlueprintAssignable, Category="NARIS|Presentation")
    FNarisPresentationCueTriggered OnCueTriggered;

    UFUNCTION(BlueprintCallable, Category="NARIS|Presentation")
    bool TriggerCue(FName CueId);

    UFUNCTION(BlueprintCallable, Category="NARIS|Presentation")
    bool TriggerCueAtLocation(FName CueId, FVector WorldLocation);

    UFUNCTION(BlueprintPure, Category="NARIS|Presentation")
    bool HasCue(FName CueId) const;

private:
    const FNarisPresentationCue* FindCue(FName CueId) const;
};
