#include "NarisWorldStateSubsystem.h"
void UNarisWorldStateSubsystem::SetFlag(FName Flag,bool bValue){if(!Flag.IsNone())Flags.FindOrAdd(Flag)=bValue;}
bool UNarisWorldStateSubsystem::GetFlag(FName Flag) const {if(const bool* V=Flags.Find(Flag))return *V;return false;}
int32 UNarisWorldStateSubsystem::AddFactionReputation(FName ID,int32 Delta){int32& V=FactionReputation.FindOrAdd(ID);V=FMath::Clamp(V+Delta,-100,100);return V;}
int32 UNarisWorldStateSubsystem::GetFactionReputation(FName ID) const {if(const int32* V=FactionReputation.Find(ID))return *V;return 0;}
void UNarisWorldStateSubsystem::RestoreState(const TMap<FName,bool>& InFlags,const TMap<FName,int32>& InRep){Flags=InFlags;FactionReputation=InRep;}
