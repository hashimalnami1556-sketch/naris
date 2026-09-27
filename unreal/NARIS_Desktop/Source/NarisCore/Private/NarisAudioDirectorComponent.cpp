#include "NarisAudioDirectorComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "UObject/ConstructorHelpers.h"

UNarisAudioDirectorComponent::UNarisAudioDirectorComponent()
{
 static ConstructorHelpers::FObjectFinder<USoundBase> A(TEXT("/Game/Audio/SFX/SFX_Attack_Whoosh.SFX_Attack_Whoosh"));
 static ConstructorHelpers::FObjectFinder<USoundBase> H(TEXT("/Game/Audio/SFX/SFX_Hit_Impact.SFX_Hit_Impact"));
 static ConstructorHelpers::FObjectFinder<USoundBase> P(TEXT("/Game/Audio/SFX/SFX_Parry.SFX_Parry"));
 static ConstructorHelpers::FObjectFinder<USoundBase> D(TEXT("/Game/Audio/SFX/SFX_Dodge.SFX_Dodge"));
 static ConstructorHelpers::FObjectFinder<USoundBase> L(TEXT("/Game/Audio/SFX/SFX_Pickup.SFX_Pickup"));
 static ConstructorHelpers::FObjectFinder<USoundBase> Q(TEXT("/Game/Audio/SFX/SFX_QuestComplete.SFX_QuestComplete"));
 static ConstructorHelpers::FObjectFinder<USoundBase> B(TEXT("/Game/Audio/SFX/SFX_BossPhase.SFX_BossPhase"));
 static ConstructorHelpers::FObjectFinder<USoundBase> S(TEXT("/Game/Audio/SFX/SFX_Save.SFX_Save"));
 static ConstructorHelpers::FObjectFinder<USoundBase> O(TEXT("/Game/Audio/SFX/SFX_Load.SFX_Load"));
 AttackWhoosh=A.Object; HitImpact=H.Object; Parry=P.Object; Dodge=D.Object; Pickup=L.Object;
 QuestComplete=Q.Object; BossPhase=B.Object; SaveSound=S.Object; LoadSound=O.Object;
}
USoundBase* UNarisAudioDirectorComponent::Resolve(FName E) const
{
 if(E==FName("Attack")) return AttackWhoosh;
 if(E==FName("Hit")) return HitImpact;
 if(E==FName("Parry")) return Parry;
 if(E==FName("Dodge")) return Dodge;
 if(E==FName("Pickup")) return Pickup;
 if(E==FName("QuestComplete")) return QuestComplete;
 if(E==FName("BossPhase")) return BossPhase;
 if(E==FName("Save")) return SaveSound;
 if(E==FName("Load")) return LoadSound;
 return nullptr;
}
void UNarisAudioDirectorComponent::PlaySFX(FName E,FVector L,float V)
{
 if(USoundBase* S=Resolve(E)){
  UGameplayStatics::PlaySoundAtLocation(this,S,L,FRotator::ZeroRotator,FMath::Clamp(V,0.f,2.f));
  UE_LOG(LogTemp,Verbose,TEXT("NARIS_AUDIO_EVENT %s"),*E.ToString());
 }
}
void UNarisAudioDirectorComponent::SetCombatIntensity(float V)
{
 CombatIntensity=FMath::Clamp(V,0.f,1.f);
 UE_LOG(LogTemp,Verbose,TEXT("NARIS Combat Intensity: %.2f"),CombatIntensity);
}
void UNarisAudioDirectorComponent::PushMusicState(FName StateID)
{
 UE_LOG(LogTemp,Verbose,TEXT("NARIS Music State: %s"),*StateID.ToString());
}
bool UNarisAudioDirectorComponent::IsCombatAudioReady() const
{
 return AttackWhoosh&&HitImpact&&Parry&&Dodge&&Pickup&&QuestComplete&&BossPhase&&SaveSound&&LoadSound;
}