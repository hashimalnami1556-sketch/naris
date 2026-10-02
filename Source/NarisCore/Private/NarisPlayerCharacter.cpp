#include "NarisPlayerCharacter.h"
#include "NarisVitalsComponent.h"
#include "NarisInventoryComponent.h"
#include "NarisEnemyCharacter.h"
#include "NarisSaveSubsystem.h"
#include "NarisGameModeBase.h"
#include "NarisAudioDirectorComponent.h"
#include "NarisVFXDirectorComponent.h"
#include "NarisHitReactionComponent.h"
#include "NarisCameraFeedbackComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "UObject/ConstructorHelpers.h"

static UNarisAudioDirectorComponent* NarisAudioFor(const UObject* C){if(ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(C)))return GM->AudioDirector;return nullptr;}
static UNarisVFXDirectorComponent* NarisVFXFor(const UObject* C){if(ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(C)))return GM->VFXDirector;return nullptr;}

ANarisPlayerCharacter::ANarisPlayerCharacter()
{
 PrimaryActorTick.bCanEverTick=true;bUseControllerRotationYaw=false;
 GetCharacterMovement()->bOrientRotationToMovement=true;GetCharacterMovement()->RotationRate=FRotator(0,540,0);GetCharacterMovement()->MaxWalkSpeed=520.f;
 Vitals=CreateDefaultSubobject<UNarisVitalsComponent>(TEXT("Vitals"));
 Inventory=CreateDefaultSubobject<UNarisInventoryComponent>(TEXT("Inventory"));
 HitReaction=CreateDefaultSubobject<UNarisHitReactionComponent>(TEXT("HitReaction"));
 CameraFeedback=CreateDefaultSubobject<UNarisCameraFeedbackComponent>(TEXT("CameraFeedback"));
 Visual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LegacyVisual"));Visual->SetupAttachment(RootComponent);Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);Visual->SetVisibility(false);

 static ConstructorHelpers::FObjectFinder<USkeletalMesh> Rig(TEXT("/Game/Art/Characters/RiggedV4/AshenVessel/SK_AshenVessel.SK_AshenVessel"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Idle(TEXT("/Game/Art/Characters/RiggedV4/AshenVessel/AN_Ashen_Idle.AN_Ashen_Idle"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Walk(TEXT("/Game/Art/Characters/RiggedV4/AshenVessel/AN_Ashen_Walk.AN_Ashen_Walk"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Run(TEXT("/Game/Art/Characters/RiggedV4/AshenVessel/AN_Ashen_Run.AN_Ashen_Run"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Parry(TEXT("/Game/Art/Characters/RiggedV4/AshenVessel/AN_Ashen_Parry.AN_Ashen_Parry"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Resonance(TEXT("/Game/Art/Characters/RiggedV4/AshenVessel/AN_Ashen_Resonance.AN_Ashen_Resonance"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Light(TEXT("/Game/Art/Characters/RiggedV4/AshenVessel/AN_Ashen_Attack_Light.AN_Ashen_Attack_Light"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Heavy(TEXT("/Game/Art/Characters/RiggedV4/AshenVessel/AN_Ashen_Attack_Heavy.AN_Ashen_Attack_Heavy"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> DodgeAsset(TEXT("/Game/Art/Characters/RiggedV4/AshenVessel/AN_Ashen_Dodge.AN_Ashen_Dodge"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> HitAsset(TEXT("/Game/Art/Characters/RiggedV4/AshenVessel/AN_Ashen_HitReact.AN_Ashen_HitReact"));
 if(Rig.Succeeded()){GetMesh()->SetSkeletalMeshAsset(Rig.Object);GetMesh()->SetRelativeLocation(FVector::ZeroVector);GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
 const TCHAR* AshenMaterials[]={
  TEXT("/Game/NARIS_AI_Stage/Generated/PackV2/Armour/NARIS_BlackIron.NARIS_BlackIron"),
  TEXT("/Game/NARIS_AI_Stage/Generated/PackV2/Armour/NARIS_AncientGold.NARIS_AncientGold")
 };
 for(int32 Slot=0;Slot<2;++Slot) if(UMaterialInterface* M=LoadObject<UMaterialInterface>(nullptr,AshenMaterials[Slot])) GetMesh()->SetMaterial(Slot,M);
 IdleAnim=Idle.Object;WalkAnim=Walk.Object;RunAnim=Run.Object;ParryAnim=Parry.Object;ResonanceAnim=Resonance.Object;AttackLightAnim=Light.Object;AttackHeavyAnim=Heavy.Object;DodgeAnim=DodgeAsset.Object;HitReactAnim=HitAsset.Object;
 if(IdleAnim){GetMesh()->SetAnimationMode(EAnimationMode::AnimationSingleNode);GetMesh()->PlayAnimation(IdleAnim,true);AnimState=0;}

 CameraBoom=CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));CameraBoom->SetupAttachment(RootComponent);CameraBoom->TargetArmLength=460.f;CameraBoom->SetRelativeRotation(FRotator(-12.f,0.f,0.f));CameraBoom->SocketOffset=FVector(0.f,55.f,70.f);CameraBoom->bUsePawnControlRotation=true;CameraBoom->bEnableCameraLag=true;CameraBoom->CameraLagSpeed=12.f;CameraBoom->bEnableCameraRotationLag=true;CameraBoom->CameraRotationLagSpeed=14.f;
 FollowCamera=CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));FollowCamera->SetupAttachment(CameraBoom,USpringArmComponent::SocketName);FollowCamera->bUsePawnControlRotation=false;FollowCamera->FieldOfView=82.f;
}
void ANarisPlayerCharacter::Tick(float D)
{
 Super::Tick(D);ParryWindow=FMath::Max(0.f,ParryWindow-D);ComboReset=FMath::Max(0.f,ComboReset-D);AttackAnimTime=FMath::Max(0.f,AttackAnimTime-D);
 if(ComboReset<=0.f)ComboIndex=0;
 if(LockTarget.IsValid()){FVector Delta=LockTarget->GetActorLocation()-GetActorLocation();Delta.Z=0.f;if(Delta.SizeSquared()>FMath::Square(2200.f))LockTarget.Reset();else if(!Delta.IsNearlyZero())SetActorRotation(FMath::RInterpTo(GetActorRotation(),Delta.Rotation(),D,9.f));}
 if(AttackAnimTime<=0.f)UpdateLocomotionAnimation();
}
void ANarisPlayerCharacter::UpdateLocomotionAnimation()
{
 const float Speed=GetVelocity().Size2D();const int32 Desired=Speed>380.f?5:(Speed>10.f?1:0);if(AnimState==Desired)return;UAnimSequence* A=Desired==5?(RunAnim?RunAnim:WalkAnim):(Desired==1?WalkAnim:IdleAnim);if(A){GetMesh()->PlayAnimation(A,true);AnimState=Desired;}
}
void ANarisPlayerCharacter::SetupPlayerInputComponent(UInputComponent* I)
{
 Super::SetupPlayerInputComponent(I);
 I->BindAxis("MoveForward",this,&ANarisPlayerCharacter::MoveForward);I->BindAxis("MoveRight",this,&ANarisPlayerCharacter::MoveRight);I->BindAxis("Turn",this,&ANarisPlayerCharacter::Turn);I->BindAxis("LookUp",this,&ANarisPlayerCharacter::LookUp);
 I->BindAction("Jump",IE_Pressed,this,&ACharacter::Jump);I->BindAction("Attack",IE_Pressed,this,&ANarisPlayerCharacter::Attack);I->BindAction("Dodge",IE_Pressed,this,&ANarisPlayerCharacter::Dodge);I->BindAction("Resonance",IE_Pressed,this,&ANarisPlayerCharacter::Resonance);
 I->BindAction("LockOn",IE_Pressed,this,&ANarisPlayerCharacter::ToggleLock);I->BindAction("Block",IE_Pressed,this,&ANarisPlayerCharacter::BlockPressed);I->BindAction("Block",IE_Released,this,&ANarisPlayerCharacter::BlockReleased);
 I->BindAction("QuickSave",IE_Pressed,this,&ANarisPlayerCharacter::QuickSave);I->BindAction("QuickLoad",IE_Pressed,this,&ANarisPlayerCharacter::QuickLoad);
 // Main-menu Start is owned by UMG; avoid raw Enter/Gamepad input bypassing menu selection.
 FInputActionBinding& PauseBinding=I->BindAction("PauseGame",IE_Pressed,this,&ANarisPlayerCharacter::TogglePause);PauseBinding.bExecuteWhenPaused=true;
 FInputActionBinding& QuitBinding=I->BindAction("QuitGame",IE_Pressed,this,&ANarisPlayerCharacter::QuitGame);QuitBinding.bExecuteWhenPaused=true;
}
void ANarisPlayerCharacter::StartGame(){if(ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this)))GM->StartGame();}
void ANarisPlayerCharacter::TogglePause(){if(ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this))){if(!GM->IsGameStarted()){return;}}const bool bPaused=UGameplayStatics::IsGamePaused(this);UGameplayStatics::SetGamePaused(this,!bPaused);if(APlayerController* PC=Cast<APlayerController>(Controller)){PC->bShowMouseCursor=!bPaused;if(bPaused){FInputModeGameOnly M;PC->SetInputMode(M);}else{FInputModeGameAndUI M;PC->SetInputMode(M);}}}
void ANarisPlayerCharacter::QuitGame(){if(APlayerController* PC=Cast<APlayerController>(Controller))UKismetSystemLibrary::QuitGame(this,PC,EQuitPreference::Quit,false);}
void ANarisPlayerCharacter::MoveForward(float V){if(Controller&&V!=0){const FRotator R(0,Controller->GetControlRotation().Yaw,0);AddMovementInput(FRotationMatrix(R).GetUnitAxis(EAxis::X),V);}}
void ANarisPlayerCharacter::MoveRight(float V){if(Controller&&V!=0){const FRotator R(0,Controller->GetControlRotation().Yaw,0);AddMovementInput(FRotationMatrix(R).GetUnitAxis(EAxis::Y),V);}}
void ANarisPlayerCharacter::Turn(float V){if(!LockTarget.IsValid())AddControllerYawInput(V);}
void ANarisPlayerCharacter::LookUp(float V){AddControllerPitchInput(V);}
void ANarisPlayerCharacter::Attack()
{
 const float Costs[3]={10,14,20};const float Damages[3]={24,34,48};if(!Vitals->SpendEnergy(Costs[ComboIndex]))return;
 UAnimSequence* A=(ComboIndex==2&&AttackHeavyAnim)?AttackHeavyAnim:AttackLightAnim;if(A){GetMesh()->PlayAnimation(A,false);AnimState=2;AttackAnimTime=ComboIndex==2?.72f:.48f;}
 if(auto* S=NarisAudioFor(this))S->PlaySFX(FName("Attack"),GetActorLocation(),.9f);
 const FVector Start=GetActorLocation()+GetActorForwardVector()*95.f;const FVector End=Start+GetActorForwardVector()*(170.f+35.f*ComboIndex);
 TArray<FHitResult> Hits;FCollisionQueryParams Q(TEXT("NarisCombo"),false,this);bool Played=false;
 if(GetWorld()->SweepMultiByChannel(Hits,Start,End,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeSphere(110.f+10.f*ComboIndex),Q))
  for(const FHitResult& H:Hits)if(AActor* Target=H.GetActor()){UGameplayStatics::ApplyDamage(Target,Damages[ComboIndex],GetController(),this,UDamageType::StaticClass());if(!Played){const FVector L=H.ImpactPoint.IsNearlyZero()?Target->GetActorLocation():FVector(H.ImpactPoint);if(auto* S=NarisAudioFor(this))S->PlaySFX(FName("Hit"),L,1.f);if(auto* V=NarisVFXFor(this))V->SpawnVFX(FName("Hit"),L,GetActorRotation(),.65f);if(CameraFeedback)CameraFeedback->PulseHit(ComboIndex==2?1.2f:.65f);Played=true;}}
 ComboIndex=(ComboIndex+1)%3;ComboReset=1.1f;
}
void ANarisPlayerCharacter::Dodge()
{
 if(Vitals->SpendEnergy(20.f)){if(DodgeAnim){GetMesh()->PlayAnimation(DodgeAnim,false);AnimState=3;AttackAnimTime=.55f;}if(auto* A=NarisAudioFor(this))A->PlaySFX(FName("Dodge"),GetActorLocation(),.85f);if(auto* V=NarisVFXFor(this))V->SpawnVFX(FName("Dodge"),GetActorLocation(),GetActorRotation(),.75f);if(CameraFeedback)CameraFeedback->PulseDodge();LaunchCharacter(GetActorForwardVector()*720.f+FVector(0,0,90),true,true);}
}
void ANarisPlayerCharacter::Resonance(){if(!Vitals->SpendEnergy(30.f))return;if(ResonanceAnim){GetMesh()->PlayAnimation(ResonanceAnim,false);AnimState=6;AttackAnimTime=1.25f;}if(auto* A=NarisAudioFor(this))A->PlaySFX(FName("Resonance"),GetActorLocation(),1.05f);if(auto* V=NarisVFXFor(this))V->SpawnVFX(FName("Resonance"),GetActorLocation()+FVector(0,0,90.f),GetActorRotation(),1.35f);TArray<AActor*> E;UGameplayStatics::GetAllActorsOfClass(this,ANarisEnemyCharacter::StaticClass(),E);for(AActor* T:E)if(FVector::DistSquared(T->GetActorLocation(),GetActorLocation())<=FMath::Square(520.f))UGameplayStatics::ApplyDamage(T,22.f,GetController(),this,UDamageType::StaticClass());}
void ANarisPlayerCharacter::ToggleLock(){if(LockTarget.IsValid()){LockTarget.Reset();return;}TArray<AActor*> E;UGameplayStatics::GetAllActorsOfClass(this,ANarisEnemyCharacter::StaticClass(),E);float Best=1800.f;for(AActor* A:E){const float D=FVector::Dist(A->GetActorLocation(),GetActorLocation());if(D<Best){Best=D;LockTarget=A;}}}
void ANarisPlayerCharacter::BlockPressed(){bBlocking=true;ParryWindow=.22f;if(ParryAnim){GetMesh()->PlayAnimation(ParryAnim,false);AnimState=7;AttackAnimTime=.45f;}}
void ANarisPlayerCharacter::BlockReleased(){bBlocking=false;ParryWindow=0.f;}
void ANarisPlayerCharacter::QuickSave(){if(UGameInstance* G=GetGameInstance())if(UNarisSaveSubsystem* S=G->GetSubsystem<UNarisSaveSubsystem>())if(S->SavePlayer(this))if(auto* A=NarisAudioFor(this))A->PlaySFX(FName("Save"),GetActorLocation(),.8f);}
void ANarisPlayerCharacter::QuickLoad(){if(UGameInstance* G=GetGameInstance())if(UNarisSaveSubsystem* S=G->GetSubsystem<UNarisSaveSubsystem>())if(S->LoadPlayer(this))if(auto* A=NarisAudioFor(this))A->PlaySFX(FName("Load"),GetActorLocation(),.8f);}
float ANarisPlayerCharacter::TakeDamage(float A,const FDamageEvent& E,AController* I,AActor* C)
{
 if(bBlocking){if(ParryWindow>0.f){if(auto* S=NarisAudioFor(this))S->PlaySFX(FName("Parry"),GetActorLocation(),1.1f);if(auto* V=NarisVFXFor(this))V->SpawnVFX(FName("Parry"),GetActorLocation()+GetActorForwardVector()*90.f,GetActorRotation(),1.15f);if(CameraFeedback)CameraFeedback->PulseParry();if(C)UGameplayStatics::ApplyDamage(C,38.f,GetController(),this,UDamageType::StaticClass());return 0.f;}if(Vitals->SpendEnergy(8.f))A*=.35f;}
 const float D=Vitals->ApplyHealthDamage(A);if(D>0.f){const float Strength=HitReaction?HitReaction->ReactToHit(D,C):0.f;if(HitReactAnim){GetMesh()->PlayAnimation(HitReactAnim,false);AnimState=4;AttackAnimTime=.34f;}if(CameraFeedback)CameraFeedback->PulseHit(Strength);}
 if(!Vitals->IsAlive()){DisableInput(Cast<APlayerController>(GetController()));GetCharacterMovement()->DisableMovement();}
 return D;
}
