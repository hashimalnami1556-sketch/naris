#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NarisHeroCharacter.generated.h"

class UNarisCombatComponent;
class UNarisEnergyComponent;
class UNarisLockOnComponent;
class UNarisInteractionComponent;
class USpringArmComponent;
class UCameraComponent;

UCLASS(Blueprintable)
class NARIS_W04_API ANarisHeroCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ANarisHeroCharacter();

    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UNarisCombatComponent> Combat;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UNarisEnergyComponent> Energy;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UNarisLockOnComponent> LockOn;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UNarisInteractionComponent> Interaction;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<USpringArmComponent> CameraBoom;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UCameraComponent> FollowCamera;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement")
    float WalkSpeed = 500.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement")
    float SprintSpeed = 700.f;

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void LightAttack();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void HeavyAttack();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void Dodge();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void Parry();

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void ResonanceBurst();

    UFUNCTION(BlueprintCallable, Category="NARIS|Interaction")
    void Interact();

    UFUNCTION(BlueprintCallable, Category="NARIS|Movement")
    void SetSprinting(bool bSprint);

protected:
    void MoveForward(float Value);
    void MoveRight(float Value);
    void LookYaw(float Value);
    void LookPitch(float Value);
};
