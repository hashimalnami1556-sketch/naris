#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NarisWaterVolume.generated.h"

class UBoxComponent;
class UStaticMeshComponent;

UCLASS(Blueprintable)
class NARIS_W04_API ANarisWaterVolume : public AActor
{
    GENERATED_BODY()

public:
    ANarisWaterVolume();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Water")
    TObjectPtr<UBoxComponent> WaterBounds;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Water")
    TObjectPtr<UStaticMeshComponent> SurfaceMesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    FName WaterBodyId = TEXT("Water.Default");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    float SurfaceOffset = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    float CurrentStrength = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    FVector CurrentDirection = FVector::ForwardVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    bool bSwimmable = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    float HazardDamagePerSecond = 0.f;

    UFUNCTION(BlueprintPure, Category="NARIS|Water")
    float GetSurfaceWorldZ() const;

    UFUNCTION(BlueprintPure, Category="NARIS|Water")
    FVector GetCurrentWorldDirection() const;

private:
    UFUNCTION()
    void HandleBeginOverlap(
        UPrimitiveComponent* OverlappedComponent,
        AActor* OtherActor,
        UPrimitiveComponent* OtherComp,
        int32 OtherBodyIndex,
        bool bFromSweep,
        const FHitResult& SweepResult
    );

    UFUNCTION()
    void HandleEndOverlap(
        UPrimitiveComponent* OverlappedComponent,
        AActor* OtherActor,
        UPrimitiveComponent* OtherComp,
        int32 OtherBodyIndex
    );
};
