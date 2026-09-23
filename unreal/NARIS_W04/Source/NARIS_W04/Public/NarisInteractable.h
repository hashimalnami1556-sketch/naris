#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "NarisInteractable.generated.h"

UINTERFACE(BlueprintType)
class NARIS_W04_API UNarisInteractable : public UInterface
{
    GENERATED_BODY()
};

class NARIS_W04_API INarisInteractable
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="NARIS|Interaction")
    bool Interact(AActor* InstigatorActor);

    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="NARIS|Interaction")
    FText GetInteractionPrompt() const;
};
