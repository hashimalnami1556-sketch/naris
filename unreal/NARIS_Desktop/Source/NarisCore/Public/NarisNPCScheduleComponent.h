#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisNPCScheduleComponent.generated.h"
UCLASS(ClassGroup=(Naris),meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisNPCScheduleComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FName NPCID;
 UFUNCTION(BlueprintCallable) FName ResolveActivity(float WorldHour) const;
};
