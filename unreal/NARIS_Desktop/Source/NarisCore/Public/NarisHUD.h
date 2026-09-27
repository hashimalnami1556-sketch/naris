#pragma once
#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "NarisHUD.generated.h"

UCLASS()
class NARISCORE_API ANarisHUD : public AHUD
{
 GENERATED_BODY()
public:
 virtual void DrawHUD() override;
 virtual void NotifyHitBoxClick(FName BoxName) override;
private:
 int32 FrontEndPage=0;
};