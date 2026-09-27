#include "NarisCameraFeedbackComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
UNarisCameraFeedbackComponent::UNarisCameraFeedbackComponent(){PrimaryComponentTick.bCanEverTick=true;}
void UNarisCameraFeedbackComponent::BeginPlay(){Super::BeginPlay();if(AActor* O=GetOwner()){Camera=O->FindComponentByClass<UCameraComponent>();SpringArm=O->FindComponentByClass<USpringArmComponent>();if(Camera.IsValid())BaseFOV=Camera->FieldOfView;if(SpringArm.IsValid())BaseArm=SpringArm->TargetArmLength;}}
void UNarisCameraFeedbackComponent::TickComponent(float D,ELevelTick T,FActorComponentTickFunction* F){Super::TickComponent(D,T,F);FOVKick=FMath::FInterpTo(FOVKick,0.f,D,12.f);ArmKick=FMath::FInterpTo(ArmKick,0.f,D,14.f);if(Camera.IsValid())Camera->SetFieldOfView(BaseFOV+FOVKick);if(SpringArm.IsValid())SpringArm->TargetArmLength=BaseArm+ArmKick;}
void UNarisCameraFeedbackComponent::PulseHit(float S){S=FMath::Clamp(S,0.f,1.5f);FOVKick=FMath::Max(FOVKick,2.8f*S);ArmKick=FMath::Min(ArmKick,-18.f*S);}
void UNarisCameraFeedbackComponent::PulseParry(){FOVKick=4.5f;ArmKick=-28.f;}
void UNarisCameraFeedbackComponent::PulseDodge(){FOVKick=5.5f;ArmKick=22.f;}
