#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NarisPresentationValidationLibrary.generated.h"

class UNiagaraSystem;

UCLASS()
class NARIS_W04_API UNarisPresentationValidationLibrary
    : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(
        BlueprintPure,
        Category="NARIS|Presentation|Validation"
    )
    static bool IsNiagaraSystemNonEmpty(
        const UNiagaraSystem* System
    );
};
