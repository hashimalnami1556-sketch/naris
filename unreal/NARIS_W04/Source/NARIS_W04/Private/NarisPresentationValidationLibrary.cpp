#include "NarisPresentationValidationLibrary.h"

#include "NiagaraSystem.h"

bool UNarisPresentationValidationLibrary::IsNiagaraSystemNonEmpty(
    const UNiagaraSystem* System
)
{
    return System && System->GetEmitterHandles().Num() > 0;
}
