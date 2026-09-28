#include "NarisDungeonGeneratorComponent.h"
TArray<FNarisDungeonRoom> UNarisDungeonGeneratorComponent::GenerateLayout(int32 Seed,int32 MinRooms,int32 MaxRooms,float BranchChance){
 FRandomStream R(Seed); const int32 Count=R.RandRange(FMath::Max(2,MinRooms),FMath::Max(MinRooms,MaxRooms));
 TArray<FNarisDungeonRoom> Out; FIntPoint P(0,0);
 for(int32 i=0;i<Count;i++){ FNarisDungeonRoom Room; Room.ID=i; Room.Grid=P; Room.bBoss=(i==Count-1); Out.Add(Room);
  if(R.FRand()<BranchChance) P.Y += (R.RandRange(0,1)==1)?1:-1; else P.X += 1; }
 return Out;
}
