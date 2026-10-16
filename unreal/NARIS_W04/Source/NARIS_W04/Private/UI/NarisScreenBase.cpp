#include "UI/NarisScreenBase.h"

void UNarisScreenBase::RequestClose()
{
    OnScreenClosed();
    RemoveFromParent();
}
