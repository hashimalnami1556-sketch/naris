#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NarisPickupActor.generated.h"
class USphereComponent;
class UStaticMeshComponent;

UCLASS()
class NARISCORE_API ANarisPickupActor : public AActor
{
 GENERATED_BODY()
public:
 ANarisPickupActor();
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FName ItemID=FName("AshShard");
 UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 Quantity=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FName PersistentID=NAME_None;
 UPROPERTY(VisibleAnywhere) TObjectPtr<USphereComponent> Trigger;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Mesh;
 virtual void NotifyActorBeginOverlap(AActor* OtherActor) override;
 UFUNCTION(BlueprintCallable) void ApplyPersistentState();
private:
 FName PersistenceFlag() const;
};