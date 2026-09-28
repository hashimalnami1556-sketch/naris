#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/DataTable.h"
#include "NarisCombatTypes.h"
#include "NarisCombatComponent.generated.h"

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisCombatComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Combat") TObjectPtr<UDataTable> AttackTable;
 UFUNCTION(BlueprintCallable, Category="NARIS|Combat") bool ResolveAttack(FName RowName, FNarisAttackRow& OutAttack) const;
};
