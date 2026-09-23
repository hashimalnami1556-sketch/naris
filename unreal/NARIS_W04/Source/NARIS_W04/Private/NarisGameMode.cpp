#include "NarisGameMode.h"

#include "NarisHUD.h"
#include "NarisHeroCharacter.h"

ANarisGameMode::ANarisGameMode()
{
    DefaultPawnClass = ANarisHeroCharacter::StaticClass();
    HUDClass = ANarisHUD::StaticClass();
}
