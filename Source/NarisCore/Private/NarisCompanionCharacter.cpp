#include "NarisCompanionCharacter.h"
#include "NarisEnemyCharacter.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"

ANarisCompanionCharacter::ANarisCompanionCharacter()
{
 PrimaryActorTick.bCanEverTick=true;
 Visual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LegacyVisual"));Visual->SetupAttachment(RootComponent);Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);Visual->SetVisibility(false);
 static ConstructorHelpers::FObjectFinder<USkeletalMesh> Rig(TEXT("/Game/Art/Characters/RiggedV4/CelestialWolf/SK_CelestialWolf.SK_CelestialWolf"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Idle(TEXT("/Game/Art/Characters/RiggedV4/CelestialWolf/AN_Wolf_Idle.AN_Wolf_Idle"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Run(TEXT("/Game/Art/Characters/RiggedV4/CelestialWolf/AN_Wolf_Run.AN_Wolf_Run"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> Bite(TEXT("/Game/Art/Characters/RiggedV4/CelestialWolf/AN_Wolf_Bite.AN_Wolf_Bite"));
 static ConstructorHelpers::FObjectFinder<UAnimSequence> SoulVision(TEXT("/Game/Art/Characters/RiggedV4/CelestialWolf/AN_Wolf_SoulVision.AN_Wolf_SoulVision"));
 if(Rig.Succeeded()){GetMesh()->SetSkeletalMeshAsset(Rig.Object);GetMesh()->SetRelativeLocation(FVector::ZeroVector);GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
 const TCHAR* WolfMaterials[]={
  TEXT("/Game/NARIS_AI_Stage/Generated/PackV2/Armour/NARIS_AetherBlue.NARIS_AetherBlue"),
  TEXT("/Game/NARIS_AI_Stage/Generated/PackV2/Armour/NARIS_VoidCrystal.NARIS_VoidCrystal")
 };
 for(int32 Slot=0;Slot<2;++Slot) if(UMaterialInterface* M=LoadObject<UMaterialInterface>(nullptr,WolfMaterials[Slot])) GetMesh()->SetMaterial(Slot,M);
 IdleAnim=Idle.Object;RunAnim=Run.Object;BiteAnim=Bite.Object;SoulVisionAnim=SoulVision.Object;if(IdleAnim){GetMesh()->SetAnimationMode(EAnimationMode::AnimationSingleNode);SetAnim(IdleAnim,true,0);}
 GetCharacterMovement()->MaxWalkSpeed=440.f;
}
void ANarisCompanionCharacter::SetAnim(UAnimSequence* A,bool L,int32 S){if(A&&AnimState!=S){GetMesh()->PlayAnimation(A,L);AnimState=S;}}
void ANarisCompanionCharacter::Tick(float D)
{
 Super::Tick(D);AttackCooldown=FMath::Max(0.f,AttackCooldown-D);AttackAnimTime=FMath::Max(0.f,AttackAnimTime-D);SoulVisionCooldown=FMath::Max(0.f,SoulVisionCooldown-D);
 ACharacter* P=UGameplayStatics::GetPlayerCharacter(this,0);if(!P)return;
 ANarisEnemyCharacter* Best=nullptr;float BestD=AssistRange;TArray<AActor*> Enemies;UGameplayStatics::GetAllActorsOfClass(this,ANarisEnemyCharacter::StaticClass(),Enemies);
 for(AActor* A:Enemies){const float X=FVector::Dist(A->GetActorLocation(),GetActorLocation());if(X<BestD){BestD=X;Best=Cast<ANarisEnemyCharacter>(A);}}
 if(Best&&SoulVisionCooldown<=0.f&&BestD>260.f&&SoulVisionAnim){SetAnim(SoulVisionAnim,false,3);AttackAnimTime=1.1f;SoulVisionCooldown=6.f;UE_LOG(LogTemp,Display,TEXT("NARIS_WOLF_SOUL_VISION Target=%s"),*Best->GetName());}
 if(Best){FVector Delta=Best->GetActorLocation()-GetActorLocation();Delta.Z=0.f;if(BestD>150.f){AddMovementInput(Delta.GetSafeNormal(),1.f);SetActorRotation(Delta.Rotation());if(AttackAnimTime<=0.f)SetAnim(RunAnim,true,1);}else if(AttackCooldown<=0.f){SetAnim(BiteAnim,false,2);AttackAnimTime=.45f;UGameplayStatics::ApplyDamage(Best,8.f,GetController(),this,UDamageType::StaticClass());AttackCooldown=.9f;}else if(AttackAnimTime<=0.f)SetAnim(IdleAnim,true,0);return;}
 FVector Delta=P->GetActorLocation()-GetActorLocation();Delta.Z=0.f;if(Delta.Size()>FollowDistance){AddMovementInput(Delta.GetSafeNormal(),1.f);SetActorRotation(Delta.Rotation());if(AttackAnimTime<=0.f)SetAnim(RunAnim,true,1);}else if(AttackAnimTime<=0.f)SetAnim(IdleAnim,true,0);
}
