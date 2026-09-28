#include "NarisCodexSubsystem.h"
bool UNarisCodexSubsystem::UnlockEntry(FName ID){ if(ID.IsNone()) return false; const bool bNew=!Unlocked.Contains(ID); Unlocked.Add(ID); return bNew; }
bool UNarisCodexSubsystem::IsUnlocked(FName ID) const { return Unlocked.Contains(ID); }
