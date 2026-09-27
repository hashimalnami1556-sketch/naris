#include "NarisDialogueComponent.h"
void UNarisDialogueComponent::BeginDialogue(AActor* Listener){ CurrentListener=Listener; CurrentNode=DialogueStartNode; }
bool UNarisDialogueComponent::SelectChoice(FName ChoiceID){ return !ChoiceID.IsNone() && !CurrentNode.IsNone(); }
