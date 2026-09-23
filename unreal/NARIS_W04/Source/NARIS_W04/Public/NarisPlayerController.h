#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "NarisPlayerController.generated.h"

UENUM(BlueprintType)
enum class ENarisMenuContext : uint8
{
    FrontEnd,
    Pause
};

UENUM(BlueprintType)
enum class ENarisPauseMenuPage : uint8
{
    Main,
    Settings,
    Controls
};

struct FInputKeyParams;

UCLASS()
class NARIS_W04_API ANarisPlayerController : public APlayerController
{
    GENERATED_BODY()

public:
    ANarisPlayerController();

    virtual void BeginPlay() override;
    virtual void SetupInputComponent() override;
    virtual bool InputKey(const FInputKeyParams& Params) override;

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void OpenFrontEndMenu();

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void CloseFrontEndMenu();

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void TogglePauseMenu();

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void OpenPauseMenu();

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void ClosePauseMenu();

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    bool IsPauseMenuOpen() const { return bPauseMenuOpen; }

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    bool IsFrontEndMenuOpen() const { return bFrontEndMenuOpen; }

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    bool IsSystemMenuOpen() const
    {
        return bPauseMenuOpen || bFrontEndMenuOpen;
    }

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    ENarisMenuContext GetMenuContext() const { return MenuContext; }

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    bool CanContinueGame() const;

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    ENarisPauseMenuPage GetPauseMenuPage() const { return PauseMenuPage; }

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    int32 GetSelectedMenuIndex() const { return SelectedMenuIndex; }

    UFUNCTION(BlueprintPure, Category="NARIS|Menu|Controls")
    bool IsWaitingForGamepadRemap() const
    {
        return bWaitingForGamepadRemap;
    }

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    int32 GetVisibleMenuItemCount() const;

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    FText GetMenuTitle() const;

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    FText GetMenuItemLabel(int32 Index) const;

    UFUNCTION(BlueprintPure, Category="NARIS|Menu")
    FText GetMenuItemValue(int32 Index) const;

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void MenuUp();

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void MenuDown();

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void MenuLeft();

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void MenuRight();

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void MenuConfirm();

    UFUNCTION(BlueprintCallable, Category="NARIS|Menu")
    void MenuBack();

private:
    UPROPERTY(VisibleAnywhere, Category="NARIS|Menu")
    bool bPauseMenuOpen = false;

    UPROPERTY(VisibleAnywhere, Category="NARIS|Menu")
    ENarisPauseMenuPage PauseMenuPage = ENarisPauseMenuPage::Main;

    UPROPERTY(VisibleAnywhere, Category="NARIS|Menu")
    int32 SelectedMenuIndex = 0;

    UPROPERTY(VisibleAnywhere, Category="NARIS|Menu|Controls")
    bool bWaitingForGamepadRemap = false;

    UPROPERTY(VisibleAnywhere, Category="NARIS|Menu|Controls")
    FName PendingRemapAction = NAME_None;

    FKey GetCurrentGamepadKey(FName ActionName) const;
    void BeginGamepadRemap(FName ActionName);
    void CancelGamepadRemap();
    bool ApplyGamepadActionRemap(
        FName ActionName,
        FKey NewKey,
        bool bPersist
    );
    void ResetGamepadActionRemaps();

    void AdjustCurrentSetting(int32 Direction);
    void ApplyCurrentSettings();
    void ResetCurrentSettings();
};
