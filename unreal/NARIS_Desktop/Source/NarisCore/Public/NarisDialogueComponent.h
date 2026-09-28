#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisDialogueComponent.generated.h"

UCLASS(ClassGroup=(Naris),meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisDialogueComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Naris|Dialogue") FName DialogueStartNode;
 UFUNCTION(BlueprintCallable) void BeginDialogue(AActor* Listener);
 UFUNCTION(BlueprintCallable) bool SelectChoice(FName ChoiceID);
 UFUNCTION(BlueprintPure) FName GetCurrentNode() const { return CurrentNode; }
private:
 UPROPERTY() FName CurrentNode;
 UPROPERTY() TObjectPtr<AActor> CurrentListener;
};
