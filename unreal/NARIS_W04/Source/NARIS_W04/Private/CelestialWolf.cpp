#include "CelestialWolf.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
ACelestialWolf::ACelestialWolf(){PrimaryActorTick.bCanEverTick=true;GetCharacterMovement()->MaxWalkSpeed=FollowSpeed;}
void ACelestialWolf::SetMode(ENarisWolfMode NewMode){Mode=NewMode;}
void ACelestialWolf::EchoLink(){Mode=ENarisWolfMode::EchoLink;}
void ACelestialWolf::Tick(float D){Super::Tick(D);APawn* P=UGameplayStatics::GetPlayerPawn(this,0);if(!P||Mode==ENarisWolfMode::Guard)return;FVector To=P->GetActorLocation()-GetActorLocation();float Dist=To.Size();if(Dist>FollowDistance&&Mode==ENarisWolfMode::Follow){AddMovementInput(To.GetSafeNormal(),FMath::Clamp(Dist/500.f,0.15f,1.f));}}
