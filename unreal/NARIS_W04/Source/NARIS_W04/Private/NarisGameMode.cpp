#include "NarisGameMode.h"

#include "NarisHUD.h"
#include "NarisHeroCharacter.h"
#include "NarisPlayerController.h"

ANarisGameMode::ANarisGameMode()
{
    DefaultPawnClass = ANarisHeroCharacter::StaticClass();
    PlayerControllerClass = ANarisPlayerController::StaticClass();
    HUDClass = ANarisHUD::StaticClass();
}
