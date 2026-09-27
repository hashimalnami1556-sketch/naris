#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NarisCheckpointActor.generated.h"
class USphereComponent; class UStaticMeshComponent;
UCLASS()
class NARISCORE_API ANarisCheckpointActor : public AActor
{
 GENERATED_BODY()
public:
 ANarisCheckpointActor();
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FName CheckpointID=FName("CP_Default");
 UPROPERTY(EditAnywhere,BlueprintReadWrite) bool bAutoSave=true;
 UPROPERTY(VisibleAnywhere) TObjectPtr<USphereComponent> Trigger;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Visual;
 virtual void NotifyActorBeginOverlap(AActor* OtherActor) override;
};