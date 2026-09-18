#include "NarisHeroCharacter.h"
#include "NarisCombatComponent.h"
#include "NarisEnergyComponent.h"
#include "NarisLockOnComponent.h"
#include "NarisInteractionComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/InputSettings.h"
ANarisHeroCharacter::ANarisHeroCharacter()
{
 PrimaryActorTick.bCanEverTick=true;
 Combat=CreateDefaultSubobject<UNarisCombatComponent>(TEXT("Combat"));
 Energy=CreateDefaultSubobject<UNarisEnergyComponent>(TEXT("Energy"));
 LockOn=CreateDefaultSubobject<UNarisLockOnComponent>(TEXT("LockOn"));
 Interaction=CreateDefaultSubobject<UNarisInteractionComponent>(TEXT("Interaction"));
 CameraBoom=CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom")); CameraBoom->SetupAttachment(RootComponent); CameraBoom->TargetArmLength=340.f; CameraBoom->bUsePawnControlRotation=true;
 FollowCamera=CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera")); FollowCamera->SetupAttachment(CameraBoom); FollowCamera->bUsePawnControlRotation=false;
 GetCharacterMovement()->MaxWalkSpeed=WalkSpeed; GetCharacterMovement()->bOrientRotationToMovement=true; bUseControllerRotationYaw=false;
}
void ANarisHeroCharacter::Tick(float D){Super::Tick(D);if(Combat&&Combat->Health<=0)DisableInput(nullptr);}
void ANarisHeroCharacter::SetupPlayerInputComponent(UInputComponent* I)
{
 Super::SetupPlayerInputComponent(I);
 if(UInputSettings* S=GetDefault<UInputSettings>()){for(const FInputActionKeyMapping& K:S->GetActionMappingByName(TEXT("MoveForward")))I->BindAction(K.ActionName,EInputEvent::IE_Pressed,this,&ANarisHeroCharacter::MoveForward).bConsumeInput=true;}
 I->BindAxis(TEXT("MoveForward"),this,&ANarisHeroCharacter::MoveForward); I->BindAxis(TEXT("MoveRight"),this,&ANarisHeroCharacter::MoveRight); I->BindAxis(TEXT("LookYaw"),this,&ANarisHeroCharacter::LookYaw); I->BindAxis(TEXT("LookPitch"),this,&ANarisHeroCharacter::LookPitch);
 I->BindAction(TEXT("LightAttack"),IE_Pressed,this,&ANarisHeroCharacter::LightAttack); I->BindAction(TEXT("HeavyAttack"),IE_Pressed,this,&ANarisHeroCharacter::HeavyAttack); I->BindAction(TEXT("Dodge"),IE_Pressed,this,&ANarisHeroCharacter::Dodge); I->BindAction(TEXT("Parry"),IE_Pressed,this,&ANarisHeroCharacter::Parry); I->BindAction(TEXT("ResonanceBurst"),IE_Pressed,this,&ANarisHeroCharacter::ResonanceBurst);
}
void ANarisHeroCharacter::MoveForward(float V){if(Controller&&V){FRotator R(0,Controller->GetControlRotation().Yaw,0);AddMovementInput(FRotationMatrix(R).GetUnitAxis(EAxis::X),V);}}
void ANarisHeroCharacter::MoveRight(float V){if(Controller&&V){FRotator R(0,Controller->GetControlRotation().Yaw,0);AddMovementInput(FRotationMatrix(R).GetUnitAxis(EAxis::Y),V);}}
void ANarisHeroCharacter::LookYaw(float V){AddControllerYawInput(V);}
void ANarisHeroCharacter::LookPitch(float V){AddControllerPitchInput(V);}
void ANarisHeroCharacter::LightAttack(){if(Combat)Combat->AddResonance(5.f);}
void ANarisHeroCharacter::HeavyAttack(){if(Combat)Combat->AddResonance(10.f);}
void ANarisHeroCharacter::Dodge(){GetCharacterMovement()->Velocity+=GetActorForwardVector()*650.f;}
void ANarisHeroCharacter::Parry(){if(Combat)Combat->AddResonance(15.f);}
void ANarisHeroCharacter::ResonanceBurst(){if(Combat&&Combat->Resonance>=Combat->MaxResonance){Combat->Resonance=0;}}
void ANarisHeroCharacter::SetSprinting(bool B){GetCharacterMovement()->MaxWalkSpeed=B?SprintSpeed:WalkSpeed;}
