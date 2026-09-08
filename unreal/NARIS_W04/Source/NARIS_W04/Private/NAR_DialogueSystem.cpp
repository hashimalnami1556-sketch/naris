// NAR_DialogueSystem.cpp — تنفيذ نظام الحوار
#include "NAR_DialogueSystem.h"
#include "Engine/World.h"

UNAR_DialogueSystem::UNAR_DialogueSystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f;
}

void UNAR_DialogueSystem::BeginPlay()
{
	Super::BeginPlay();
	LoadDialogueState();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Dialogue] نظام الحوار جاهز"));
}

void UNAR_DialogueSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	UpdateConversations(DeltaTime);
}

bool UNAR_DialogueSystem::RegisterDialogueTree(const FDialogueTree& DialogueTree)
{
	if (DialogueTrees.Contains(DialogueTree.DialogueID))
	{
		return false;
	}

	DialogueTrees.Add(DialogueTree.DialogueID, DialogueTree);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Dialogue] تسجيل شجرة حوار: %s (%s)"), *DialogueTree.DialogueID, *DialogueTree.NPCName);

	return true;
}

bool UNAR_DialogueSystem::StartDialogue(const FString& DialogueID, const FString& NPCID)
{
	if (!DialogueTrees.Contains(DialogueID))
	{
		return false;
	}

	if (ActiveConversations.Num() >= MaxActiveConversations)
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Dialogue] تم الوصول للحد الأقصى للحوارات النشطة"));
		return false;
	}

	const FDialogueTree& Tree = DialogueTrees[DialogueID];
	FConversation Conversation;
	Conversation.ConversationID = DialogueID;
	Conversation.NPCID = NPCID;
	Conversation.CurrentNodeID = Tree.StartNodeID;
	Conversation.bIsActive = true;
	Conversation.StartTime = GetWorld()->GetTimeSeconds();

	FString ConvID = DialogueID + FString::FromInt(ActiveConversations.Num());
	ActiveConversations.Add(ConvID, Conversation);

	OnDialogueStarted.Broadcast(Conversation);
	TotalDialoguesStarted++;

	UE_LOG(LogTemp, Log, TEXT("[NAR_Dialogue] بدء حوار: %s مع %s"), *DialogueID, *NPCID);

	return true;
}

bool UNAR_DialogueSystem::SelectChoice(const FString& ConversationID, int32 ChoiceIndex)
{
	if (!ActiveConversations.Contains(ConversationID))
	{
		return false;
	}

	FConversation& Conversation = ActiveConversations[ConversationID];
	FDialogueTree* Tree = FindDialogueTree(Conversation.ConversationID);

	if (!Tree)
	{
		return false;
	}

	FDialogueNode* CurrentNode = FindNode(Tree->DialogueID, Conversation.CurrentNodeID);
	if (!CurrentNode || ChoiceIndex >= CurrentNode->Choices.Num())
	{
		return false;
	}

	const FDialogueChoice& Choice = CurrentNode->Choices[ChoiceIndex];
	OnChoiceSelected.Broadcast(ConversationID, Choice);

	// انتقال للعقدة التالية
	Conversation.CurrentNodeID = Choice.NextNodeID;
	Conversation.VisitedNodes.Add(Choice.NextNodeID);

	FDialogueNode* NextNode = FindNode(Tree->DialogueID, Choice.NextNodeID);
	if (NextNode)
	{
		OnNodeChanged.Broadcast(ConversationID, *NextNode);
		OnEmotionChanged.Broadcast(ConversationID, NextNode->Emotion);
	}

	return true;
}

FDialogueNode UNAR_DialogueSystem::GetCurrentNode(const FString& ConversationID)
{
	if (!ActiveConversations.Contains(ConversationID))
	{
		return FDialogueNode();
	}

	const FConversation& Conversation = ActiveConversations[ConversationID];
	FDialogueTree* Tree = FindDialogueTree(Conversation.ConversationID);

	if (Tree)
	{
		FDialogueNode* Node = FindNode(Tree->DialogueID, Conversation.CurrentNodeID);
		if (Node)
		{
			return *Node;
		}
	}

	return FDialogueNode();
}

bool UNAR_DialogueSystem::EndDialogue(const FString& ConversationID)
{
	if (!ActiveConversations.Contains(ConversationID))
	{
		return false;
	}

	FConversation Conversation = ActiveConversations[ConversationID];
	ActiveConversations.Remove(ConversationID);

	OnDialogueEnded.Broadcast(Conversation);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Dialogue] إنهاء الحوار: %s"), *ConversationID);

	return true;
}

TArray<FDialogueChoice> UNAR_DialogueSystem::GetAvailableChoices(const FString& ConversationID)
{
	TArray<FDialogueChoice> Choices;

	if (!ActiveConversations.Contains(ConversationID))
	{
		return Choices;
	}

	const FConversation& Conversation = ActiveConversations[ConversationID];
	FDialogueNode CurrentNode = GetCurrentNode(ConversationID);

	for (const FDialogueChoice& Choice : CurrentNode.Choices)
	{
		if (Choice.bIsAvailable)
		{
			Choices.Add(Choice);
		}
	}

	return Choices;
}

bool UNAR_DialogueSystem::PlayVoiceLine(const FString& VoiceLineID)
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Dialogue] تشغيل صوت: %s"), *VoiceLineID);
	return true;
}

FString UNAR_DialogueSystem::GetDialogueText(const FString& ConversationID)
{
	FDialogueNode Node = GetCurrentNode(ConversationID);
	return Node.DialogueText;
}

bool UNAR_DialogueSystem::IsDialogueActive(const FString& ConversationID)
{
	if (ActiveConversations.Contains(ConversationID))
	{
		return ActiveConversations[ConversationID].bIsActive;
	}

	return false;
}

void UNAR_DialogueSystem::SaveDialogueState()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Dialogue] حفظ حالة الحوار"));
}

void UNAR_DialogueSystem::LoadDialogueState()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Dialogue] تحميل حالة الحوار"));
}

FDialogueTree* UNAR_DialogueSystem::FindDialogueTree(const FString& DialogueID)
{
	if (DialogueTrees.Contains(DialogueID))
	{
		return &DialogueTrees[DialogueID];
	}

	return nullptr;
}

FDialogueNode* UNAR_DialogueSystem::FindNode(const FString& DialogueID, const FString& NodeID)
{
	FDialogueTree* Tree = FindDialogueTree(DialogueID);
	if (!Tree)
	{
		return nullptr;
	}

	for (FDialogueNode& Node : Tree->Nodes)
	{
		if (Node.NodeID == NodeID)
		{
			return &Node;
		}
	}

	return nullptr;
}

void UNAR_DialogueSystem::UpdateConversations(float DeltaTime)
{
	TArray<FString> FinishedConversations;

	for (auto& Pair : ActiveConversations)
	{
		FConversation& Conversation = Pair.Value;

		// التحقق من انتهاء الحوار
		if (FMath::IsNearlyZero(GetDialogueText(Pair.Key).Len()))
		{
			FinishedConversations.Add(Pair.Key);
		}

		// timeout
		if (GetWorld()->GetTimeSeconds() - Conversation.StartTime > DialogueTimeout)
		{
			FinishedConversations.Add(Pair.Key);
		}
	}

	for (const FString& ConvID : FinishedConversations)
	{
		EndDialogue(ConvID);
	}
}
