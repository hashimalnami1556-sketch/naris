#include "NarisPickupActor.h"
#include "NarisPlayerCharacter.h"
#include "NarisInventoryComponent.h"
#include "NarisQuestSubsystem.h"
#include "NarisWorldStateSubsystem.h"
#include "NarisNarrativeTypes.h"
#include "NarisGameModeBase.h"
#include "NarisAudioDirectorComponent.h"
#include "NarisVFXDirectorComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Kismet/GameplayStatics.h"

ANarisPickupActor::ANarisPickupActor()
{
 PrimaryActorTick.bCanEverTick=false;
 Trigger=CreateDefaultSubobject<USphereComponent>(TEXT("Trigger")); RootComponent=Trigger; Trigger->InitSphereRadius(70.f); Trigger->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
 Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh")); Mesh->SetupAttachment(Trigger); Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision); Mesh->SetRelativeScale3D(FVector(.28f));
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere")); if(Sphere.Succeeded())Mesh->SetStaticMesh(Sphere.Object);
}
FName ANarisPickupActor::PersistenceFlag() const
{
 return PersistentID.IsNone()?NAME_None:FName(*FString::Printf(TEXT("Collected_%s"),*PersistentID.ToString()));
}
void ANarisPickupActor::ApplyPersistentState()
{
 const FName Flag=PersistenceFlag(); if(Flag.IsNone()) return;
 if(UGameInstance* G=GetGameInstance()) if(UNarisWorldStateSubsystem* W=G->GetSubsystem<UNarisWorldStateSubsystem>())
  if(W->GetFlag(Flag)){UE_LOG(LogTemp,Display,TEXT("NARIS_PERSIST_SUPPRESS Pickup=%s"),*PersistentID.ToString());Destroy();}
}
void ANarisPickupActor::NotifyActorBeginOverlap(AActor* Other)
{
 Super::NotifyActorBeginOverlap(Other);
 ANarisPlayerCharacter* P=Cast<ANarisPlayerCharacter>(Other); if(!P||!P->Inventory) return;
 if(!P->Inventory->AddItem(ItemID,Quantity)) return;
 if(UGameInstance* G=P->GetGameInstance()){
  if(UNarisQuestSubsystem* Q=G->GetSubsystem<UNarisQuestSubsystem>()){
   FNarisNarrativeEvent E; E.Type=ENarisNarrativeEventType::ItemAcquired; E.TargetID=ItemID; E.Amount=Quantity; Q->PublishNarrativeEvent(E);
  }
  const FName Flag=PersistenceFlag();
  if(!Flag.IsNone()) if(UNarisWorldStateSubsystem* W=G->GetSubsystem<UNarisWorldStateSubsystem>()) W->SetFlag(Flag,true);
 }
 if(ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(this))){
  if(GM->AudioDirector) GM->AudioDirector->PlaySFX(FName("Pickup"),GetActorLocation(),.9f);
  if(GM->VFXDirector) GM->VFXDirector->SpawnVFX(FName("Pickup"),GetActorLocation(),FRotator::ZeroRotator,.45f);
 }
 UE_LOG(LogTemp,Display,TEXT("NARIS_PICKUP Item=%s Qty=%d Persistent=%s"),*ItemID.ToString(),Quantity,*PersistentID.ToString());
 Destroy();
}