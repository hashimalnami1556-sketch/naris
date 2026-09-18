#include "BoneBeast.h"
#include "NarisCombatComponent.h"
#include "NarisBossPhaseComponent.h"
ABoneBeast::ABoneBeast(){PrimaryActorTick.bCanEverTick=true;Combat=CreateDefaultSubobject<UNarisCombatComponent>(TEXT("Combat"));Phases=CreateDefaultSubobject<UNarisBossPhaseComponent>(TEXT("Phases"));Combat->MaxHealth=1800.f;Combat->Health=1800.f;Combat->MaxPoise=600.f;Combat->Poise=600.f;}
void ABoneBeast::Tick(float D){Super::Tick(D);if(Combat&&Phases)Phases->UpdatePhase(Combat->Health,Combat->MaxHealth);}
