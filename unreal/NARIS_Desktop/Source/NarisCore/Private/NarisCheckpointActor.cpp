#include "NarisCheckpointActor.h"
#include "NarisPlayerCharacter.h"
#include "NarisSaveSubsystem.h"
#include "NarisWorldStateSubsystem.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"
ANarisCheckpointActor::ANarisCheckpointActor()
{
 Trigger=CreateDefaultSubobject<USphereComponent>(TEXT("Trigger"));RootComponent=Trigger;Trigger->InitSphereRadius(120.f);Trigger->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
 Visual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Visual"));Visual->SetupAttachment(Trigger);Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 static ConstructorHelpers::FObjectFinder<UStaticMesh> M(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));if(M.Succeeded())Visual->SetStaticMesh(M.Object);Visual->SetRelativeScale3D(FVector(.35f,.35f,.08f));
}
void ANarisCheckpointActor::NotifyActorBeginOverlap(AActor* Other)
{
 Super::NotifyActorBeginOverlap(Other);ANarisPlayerCharacter* P=Cast<ANarisPlayerCharacter>(Other);if(!P)return;
 if(UGameInstance* G=P->GetGameInstance()){if(UNarisWorldStateSubsystem* W=G->GetSubsystem<UNarisWorldStateSubsystem>())W->SetFlag(FName(*FString::Printf(TEXT("Checkpoint_%s"),*CheckpointID.ToString())),true);if(bAutoSave)if(UNarisSaveSubsystem* S=G->GetSubsystem<UNarisSaveSubsystem>())S->SavePlayer(P,FParse::Param(FCommandLine::Get(),TEXT("NarisQuestSmoke"))?TEXT("NARIS_SmokeCheckpoint"):TEXT("NARIS_Auto"));}
 UE_LOG(LogTemp,Display,TEXT("NARIS_CHECKPOINT %s"),*CheckpointID.ToString());
}