// NAR_DialogueSystem.h — نظام الحوار المتقدم
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_DialogueSystem.generated.h"

UENUM(BlueprintType)
enum class EDialogueEmotionType : uint8
{
	Neutral			UMETA(DisplayName = "محايد"),
	Happy			UMETA(DisplayName = "سعيد"),
	Angry			UMETA(DisplayName = "غاضب"),
	Sad				UMETA(DisplayName = "حزين"),
	Surprised		UMETA(DisplayName = "مندهش"),
	Confused		UMETA(DisplayName = "مرتبك")
};

UENUM(BlueprintType)
enum class EDialogueChoiceType : uint8
{
	Normal			UMETA(DisplayName = "عادي"),
	Quest			UMETA(DisplayName = "عرض مهمة"),
	Skill			UMETA(DisplayName = "تعليم مهارة")
};

USTRUCT(BlueprintType)
struct FDialogueChoice
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString ChoiceText = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	EDialogueChoiceType ChoiceType = EDialogueChoiceType::Normal;

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString NextNodeID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	int32 ReputationImpact = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString RequiredQuestID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	bool bIsAvailable = true;
};

USTRUCT(BlueprintType)
struct FDialogueNode
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString NodeID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString SpeakerName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString DialogueText = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	EDialogueEmotionType Emotion = EDialogueEmotionType::Neutral;

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString VoiceLineID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	TArray<FDialogueChoice> Choices;

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	bool bIsEnd = false;

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	float DisplayDuration = 5.0f;
};

USTRUCT(BlueprintType)
struct FDialogueTree
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString DialogueID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString NPCName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	TArray<FDialogueNode> Nodes;

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString StartNodeID = FString();
};

USTRUCT(BlueprintType)
struct FConversation
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString ConversationID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString NPCID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	FString CurrentNodeID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	TArray<FString> VisitedNodes;

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	bool bIsActive = false;

	UPROPERTY(BlueprintReadWrite, Category = "Dialogue")
	float StartTime = 0.0f;
};

UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_DialogueSystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_DialogueSystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	UFUNCTION(BlueprintCallable, Category = "NAR|Dialogue")
	bool RegisterDialogueTree(const FDialogueTree& DialogueTree);

	UFUNCTION(BlueprintCallable, Category = "NAR|Dialogue")
	bool StartDialogue(const FString& DialogueID, const FString& NPCID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Dialogue")
	bool SelectChoice(const FString& ConversationID, int32 ChoiceIndex);

	UFUNCTION(BlueprintCallable, Category = "NAR|Dialogue")
	FDialogueNode GetCurrentNode(const FString& ConversationID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Dialogue")
	bool EndDialogue(const FString& ConversationID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Dialogue")
	TArray<FDialogueChoice> GetAvailableChoices(const FString& ConversationID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Dialogue")
	bool PlayVoiceLine(const FString& VoiceLineID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Dialogue")
	FString GetDialogueText(const FString& ConversationID);

	UFUNCTION(BlueprintPure, Category = "NAR|Dialogue")
	bool IsDialogueActive(const FString& ConversationID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Dialogue")
	void SaveDialogueState();

	UFUNCTION(BlueprintCallable, Category = "NAR|Dialogue")
	void LoadDialogueState();

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDialogueStarted, FConversation, Conversation);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Dialogue|Events")
	FOnDialogueStarted OnDialogueStarted;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDialogueEnded, FConversation, Conversation);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Dialogue|Events")
	FOnDialogueEnded OnDialogueEnded;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnNodeChanged, FString, ConversationID, FDialogueNode, Node);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Dialogue|Events")
	FOnNodeChanged OnNodeChanged;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnChoiceSelected, FString, ConversationID, FDialogueChoice, Choice);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Dialogue|Events")
	FOnChoiceSelected OnChoiceSelected;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnEmotionChanged, FString, ConversationID, EDialogueEmotionType, Emotion);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Dialogue|Events")
	FOnEmotionChanged OnEmotionChanged;

protected:
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Dialogue|Data")
	TMap<FString, FDialogueTree> DialogueTrees;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Dialogue|Data")
	TMap<FString, FConversation> ActiveConversations;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Dialogue|Data")
	int32 TotalDialoguesStarted = 0;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Dialogue|Settings")
	int32 MaxActiveConversations = 5;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Dialogue|Settings")
	float DialogueTimeout = 120.0f;

private:
	FDialogueTree* FindDialogueTree(const FString& DialogueID);
	FDialogueNode* FindNode(const FString& DialogueID, const FString& NodeID);
	void UpdateConversations(float DeltaTime);
};
