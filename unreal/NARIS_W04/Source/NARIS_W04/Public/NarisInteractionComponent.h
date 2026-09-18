#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisInteractionComponent.generated.h"
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisInteractEvent,AActor*,Actor);
UCLASS(ClassGroup=(NARIS), Blueprintable, meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UNarisInteractionComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UNarisInteractionComponent();
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Interaction") float Radius=220.f;
    UPROPERTY(BlueprintAssignable) FNarisInteractEvent OnInteracted;
    UFUNCTION(BlueprintCallable,Category="NARIS|Interaction") bool Interact();
};
