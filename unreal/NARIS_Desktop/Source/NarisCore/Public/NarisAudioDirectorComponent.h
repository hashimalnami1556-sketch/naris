#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisAudioDirectorComponent.generated.h"

class USoundBase;

UCLASS(ClassGroup=(NARIS),meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisAudioDirectorComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 UNarisAudioDirectorComponent();
 UFUNCTION(BlueprintCallable) void SetCombatIntensity(float Value);
 UFUNCTION(BlueprintCallable) void PushMusicState(FName StateID);
 UFUNCTION(BlueprintCallable) void PlaySFX(FName EventID,FVector Location,float Volume=1.f);
 UFUNCTION(BlueprintPure) bool IsCombatAudioReady() const;
private:
 UPROPERTY() TObjectPtr<USoundBase> AttackWhoosh;
 UPROPERTY() TObjectPtr<USoundBase> HitImpact;
 UPROPERTY() TObjectPtr<USoundBase> Parry;
 UPROPERTY() TObjectPtr<USoundBase> Dodge;
 UPROPERTY() TObjectPtr<USoundBase> Pickup;
 UPROPERTY() TObjectPtr<USoundBase> QuestComplete;
 UPROPERTY() TObjectPtr<USoundBase> BossPhase;
 UPROPERTY() TObjectPtr<USoundBase> SaveSound;
 UPROPERTY() TObjectPtr<USoundBase> LoadSound;
 float CombatIntensity=0.f;
 USoundBase* Resolve(FName EventID) const;
};