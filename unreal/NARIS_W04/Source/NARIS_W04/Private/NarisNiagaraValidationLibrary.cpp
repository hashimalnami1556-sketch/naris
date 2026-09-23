#include "NarisNiagaraValidationLibrary.h"

#include "NiagaraSystem.h"

int32 UNarisNiagaraValidationLibrary::GetEmitterCount(
    const UNiagaraSystem* System
)
{
    return System
        ? System->GetEmitterHandles().Num()
        : 0;
}

bool UNarisNiagaraValidationLibrary::HasEmitters(
    const UNiagaraSystem* System
)
{
    return GetEmitterCount(System) > 0;
}
