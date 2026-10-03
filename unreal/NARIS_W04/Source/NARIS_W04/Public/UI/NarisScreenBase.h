#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "NarisScreenBase.generated.h"

UCLASS(Abstract, Blueprintable)
class NARIS_W04_API UNarisScreenBase : public UUserWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="NARIS|UI")
    virtual void RequestClose();

    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|UI")
    void OnScreenOpened();

    UFUNCTION(BlueprintImplementableEvent, Category="NARIS|UI")
    void OnScreenClosed();
};
