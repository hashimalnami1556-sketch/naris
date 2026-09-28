#include "NarisRuntimeDiagnosticsSubsystem.h"
#include "NarisEnemyCharacter.h"
#include "NarisBossCharacter.h"
#include "NarisGameModeBase.h"
#include "NarisAudioDirectorComponent.h"
#include "NarisVFXDirectorComponent.h"
#include "NarisAttackTokenCoordinator.h"
#include "NarisSaveSubsystem.h"
#include "NarisQuestSubsystem.h"
#include "Kismet/GameplayStatics.h"
FNarisRuntimeHealth UNarisRuntimeDiagnosticsSubsystem::Probe(UObject* C)const
{
 FNarisRuntimeHealth H;if(!C)return H;H.bWorldReady=C->GetWorld()!=nullptr;
 if(ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(C))){H.bAudioReady=GM->AudioDirector&&GM->AudioDirector->IsCombatAudioReady();H.bVFXReady=GM->VFXDirector&&GM->VFXDirector->IsCombatVFXReady();H.bAttackCoordinationReady=GM->AttackCoordinator&&GM->AttackCoordinator->MaxSimultaneousAttackers==2;}
 if(UGameInstance* G=UGameplayStatics::GetGameInstance(C)){H.bSaveReady=G->GetSubsystem<UNarisSaveSubsystem>()!=nullptr;H.bQuestReady=G->GetSubsystem<UNarisQuestSubsystem>()!=nullptr;}
 TArray<AActor*> A;UGameplayStatics::GetAllActorsOfClass(C,ANarisEnemyCharacter::StaticClass(),A);H.ActiveEnemies=A.Num();A.Reset();UGameplayStatics::GetAllActorsOfClass(C,ANarisBossCharacter::StaticClass(),A);H.ActiveBosses=A.Num();return H;
}
bool UNarisRuntimeDiagnosticsSubsystem::RunReleaseGate(UObject* C)const
{
 const FNarisRuntimeHealth H=Probe(C);const bool Pass=H.bWorldReady&&H.bAudioReady&&H.bVFXReady&&H.bSaveReady&&H.bQuestReady&&H.bAttackCoordinationReady&&H.ActiveBosses>=1;
 UE_LOG(LogTemp,Display,TEXT("NARIS_RELEASE_GATE %s World=%d Audio=%d VFX=%d Save=%d Quest=%d AI=%d Enemies=%d Bosses=%d"),Pass?TEXT("PASS"):TEXT("FAIL"),H.bWorldReady?1:0,H.bAudioReady?1:0,H.bVFXReady?1:0,H.bSaveReady?1:0,H.bQuestReady?1:0,H.bAttackCoordinationReady?1:0,H.ActiveEnemies,H.ActiveBosses);
 return Pass;
}