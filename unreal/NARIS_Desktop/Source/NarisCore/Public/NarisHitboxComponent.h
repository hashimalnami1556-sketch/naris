#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisHitboxComponent.generated.h"

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisHitboxComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable, Category="NARIS|Combat") void BeginHitWindow(FName AttackID, FName Socket, float Radius);
 UFUNCTION(BlueprintCallable, Category="NARIS|Combat") void EndHitWindow();
 UFUNCTION(BlueprintPure, Category="NARIS|Combat") bool IsHitWindowActive() const { return bActive; }
private:
 bool bActive=false; FName ActiveAttack; FName ActiveSocket; float ActiveRadius=20.f;
 TSet<TWeakObjectPtr<AActor>> HitActors;
};
