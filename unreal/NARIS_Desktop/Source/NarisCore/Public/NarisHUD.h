#pragma once
#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "NarisHUD.generated.h"

class UNarisNativeMenuWidget;

UCLASS()
class NARISCORE_API ANarisHUD : public AHUD
{
 GENERATED_BODY()
public:
 virtual void BeginPlay() override;
 virtual void DrawHUD() override;
 virtual void NotifyHitBoxClick(FName BoxName) override;
private:
 UPROPERTY() TObjectPtr<UNarisNativeMenuWidget> FrontEndWidget;
 int32 FrontEndPage=0;
};