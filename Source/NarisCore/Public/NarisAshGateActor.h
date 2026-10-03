#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NarisAshGateActor.generated.h"
class UBoxComponent;
UCLASS()
class NARISCORE_API ANarisAshGateActor : public AActor
{
 GENERATED_BODY()
public:
 ANarisAshGateActor();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="NARIS|Gate") TObjectPtr<UBoxComponent> Barrier;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="NARIS|Gate") float PassageDistance=280.f;
 UFUNCTION(BlueprintPure,Category="NARIS|Gate") bool IsGateOpen() const {return bOpen;}
private:
 bool bOpen=false;
 bool bEntered=false;
};
