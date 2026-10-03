#include "NarisWaterVolume.h"

#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "NarisSwimmingComponent.h"

ANarisWaterVolume::ANarisWaterVolume()
{
    PrimaryActorTick.bCanEverTick = false;

    WaterBounds = CreateDefaultSubobject<UBoxComponent>(TEXT("WaterBounds"));
    RootComponent = WaterBounds;
    WaterBounds->SetBoxExtent(FVector(500.f, 500.f, 200.f));
    WaterBounds->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    WaterBounds->SetCollisionResponseToAllChannels(ECR_Ignore);
    WaterBounds->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
    WaterBounds->SetGenerateOverlapEvents(true);

    SurfaceMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SurfaceMesh"));
    SurfaceMesh->SetupAttachment(RootComponent);
    SurfaceMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    WaterBounds->OnComponentBeginOverlap.AddDynamic(
        this, &ANarisWaterVolume::HandleBeginOverlap
    );
    WaterBounds->OnComponentEndOverlap.AddDynamic(
        this, &ANarisWaterVolume::HandleEndOverlap
    );
}

float ANarisWaterVolume::GetSurfaceWorldZ() const
{
    return GetActorLocation().Z + SurfaceOffset;
}

FVector ANarisWaterVolume::GetCurrentWorldDirection() const
{
    return GetActorTransform().TransformVectorNoScale(CurrentDirection).GetSafeNormal();
}

void ANarisWaterVolume::HandleBeginOverlap(
    UPrimitiveComponent* OverlappedComponent,
    AActor* OtherActor,
    UPrimitiveComponent* OtherComp,
    int32 OtherBodyIndex,
    bool bFromSweep,
    const FHitResult& SweepResult
)
{
    if (!bSwimmable || !IsValid(OtherActor))
    {
        return;
    }

    if (UNarisSwimmingComponent* Swimming =
            OtherActor->FindComponentByClass<UNarisSwimmingComponent>())
    {
        Swimming->EnterWater(this);
    }
}

void ANarisWaterVolume::HandleEndOverlap(
    UPrimitiveComponent* OverlappedComponent,
    AActor* OtherActor,
    UPrimitiveComponent* OtherComp,
    int32 OtherBodyIndex
)
{
    if (!IsValid(OtherActor))
    {
        return;
    }

    if (UNarisSwimmingComponent* Swimming =
            OtherActor->FindComponentByClass<UNarisSwimmingComponent>())
    {
        Swimming->ExitWater(this);
    }
}
