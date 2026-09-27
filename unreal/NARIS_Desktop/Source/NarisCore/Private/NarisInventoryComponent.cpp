#include "NarisInventoryComponent.h"
bool UNarisInventoryComponent::AddItem(FName ID,int32 Qty){if(ID.IsNone()||Qty<=0)return false; for(auto& S:Items)if(S.ItemID==ID){S.Quantity+=Qty;return true;} FNarisItemStack S;S.ItemID=ID;S.Quantity=Qty;Items.Add(S);return true;}
bool UNarisInventoryComponent::RemoveItem(FName ID,int32 Qty){if(Qty<=0)return false;for(int32 i=0;i<Items.Num();++i)if(Items[i].ItemID==ID&&Items[i].Quantity>=Qty){Items[i].Quantity-=Qty;if(Items[i].Quantity==0)Items.RemoveAt(i);return true;}return false;}
