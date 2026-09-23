#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NarisNiagaraValidationLibrary.generated.h"

class UNiagaraSystem;

UCLASS()
class NARIS_W04_API UNarisNiagaraValidationLibrary
    : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintPure, Category="NARIS|VFX|Validation")
    static int32 GetEmitterCount(const UNiagaraSystem* System);

    UFUNCTION(BlueprintPure, Category="NARIS|VFX|Validation")
    static bool HasEmitters(const UNiagaraSystem* System);
};
