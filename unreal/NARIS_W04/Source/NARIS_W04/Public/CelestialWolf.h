#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "CelestialWolf.generated.h"
UENUM(BlueprintType) enum class ENarisWolfMode:uint8{Follow,Guard,Attack,Track,EchoLink};
UCLASS(Blueprintable)
class NARIS_W04_API ACelestialWolf:public ACharacter
{
 GENERATED_BODY()
public:
 ACelestialWolf();
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Companion") ENarisWolfMode Mode=ENarisWolfMode::Follow;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Companion") float FollowDistance=260.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Companion") float FollowSpeed=560.f;
 UFUNCTION(BlueprintCallable,Category="NARIS|Companion") void SetMode(ENarisWolfMode NewMode);
 UFUNCTION(BlueprintCallable,Category="NARIS|Companion") void EchoLink();
 virtual void Tick(float DeltaSeconds) override;
};
