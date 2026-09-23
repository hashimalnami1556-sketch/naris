#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NarisRuntimeSmokeDirector.generated.h"

UCLASS()
class NARIS_W04_API ANarisRuntimeSmokeDirector : public AActor
{
    GENERATED_BODY()

public:
    ANarisRuntimeSmokeDirector();

protected:
    virtual void BeginPlay() override;

private:
    void RunSmoke();
    void FinishSmoke(bool bPassed, const TMap<FString, bool>& Steps, const FString& Detail);
    FString ResolveReportPath() const;
};
