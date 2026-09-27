#include "NarisChapterSubsystem.h"
void UNarisChapterSubsystem::UnlockChapter(ENarisChapter C){Unlocked.Add(C);OnChapterChanged.Broadcast(C,false);}
void UNarisChapterSubsystem::CompleteChapter(ENarisChapter C){Unlocked.Add(C);Completed.Add(C);OnChapterChanged.Broadcast(C,true);}
bool UNarisChapterSubsystem::IsUnlocked(ENarisChapter C)const{return C==ENarisChapter::AshenGate||Unlocked.Contains(C);}
bool UNarisChapterSubsystem::IsCompleted(ENarisChapter C)const{return Completed.Contains(C);}
bool UNarisChapterSubsystem::SetCurrentChapter(ENarisChapter C){if(!IsUnlocked(C))return false;CurrentChapter=C;OnChapterChanged.Broadcast(C,IsCompleted(C));return true;}
void UNarisChapterSubsystem::RestoreState(ENarisChapter C,const TArray<uint8>& U,const TArray<uint8>& D){Unlocked.Reset();Completed.Reset();for(uint8 V:U)Unlocked.Add((ENarisChapter)V);for(uint8 V:D)Completed.Add((ENarisChapter)V);CurrentChapter=C==ENarisChapter::None?ENarisChapter::AshenGate:C;}
