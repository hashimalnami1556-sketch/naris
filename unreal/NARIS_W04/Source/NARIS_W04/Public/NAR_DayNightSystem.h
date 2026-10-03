// NAR_DayNightSystem.h — نظام اليوم والليل المتقدم
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_DayNightSystem.generated.h"

// ============================================
// بيانات المرحلة الزمنية
// ============================================
USTRUCT(BlueprintType)
struct FTimePhaseData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Time")
	float StartHour = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Time")
	float EndHour = 24.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Time")
	FString PhaseName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Time")
	FLinearColor AmbientLight = FLinearColor::White;

	UPROPERTY(BlueprintReadWrite, Category = "Time")
	float LightIntensity = 1.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Time")
	float VisibilityMultiplier = 1.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Time")
	int32 EnemySpawnMultiplier = 1;
};

// ============================================
// بيانات الدورة الزمنية
// ============================================
USTRUCT(BlueprintType)
struct FDayNightCycle
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Cycle")
	float CurrentHour = 12.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Cycle")
	int32 CurrentDay = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Cycle")
	float MinutesPerGameHour = 0.5f;

	UPROPERTY(BlueprintReadWrite, Category = "Cycle")
	bool bIsDaytime = true;

	UPROPERTY(BlueprintReadWrite, Category = "Cycle")
	bool bIsNighttime = false;

	UPROPERTY(BlueprintReadWrite, Category = "Cycle")
	float TimeMultiplier = 1.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Cycle")
	float TotalGameTime = 0.0f;
};

// ============================================
// نظام اليوم والليل
// ============================================
/**
 * UNAR_DayNightSystem — نظام اليوم والليل المتقدم
 * يدير: الدورة الزمنية + تأثيرات الوقت + جدولة الأحداث
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_DayNightSystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_DayNightSystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ============================================
	// إدارة الوقت
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight")
	void SetCurrentHour(float Hour);

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight")
	void AddHours(float Hours);

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight")
	void SetTimeMultiplier(float Multiplier);

	UFUNCTION(BlueprintPure, Category = "NAR|DayNight")
	float GetCurrentHour() const { return DayNightCycle.CurrentHour; }

	UFUNCTION(BlueprintPure, Category = "NAR|DayNight")
	int32 GetCurrentDay() const { return DayNightCycle.CurrentDay; }

	UFUNCTION(BlueprintPure, Category = "NAR|DayNight")
	float GetTimeMultiplier() const { return DayNightCycle.TimeMultiplier; }

	UFUNCTION(BlueprintPure, Category = "NAR|DayNight")
	float GetTotalGameTime() const { return DayNightCycle.TotalGameTime; }

	// ============================================
	// حالة اليوم والليل
	// ============================================
	UFUNCTION(BlueprintPure, Category = "NAR|DayNight|State")
	bool IsDay() const { return DayNightCycle.bIsDaytime; }

	UFUNCTION(BlueprintPure, Category = "NAR|DayNight|State")
	bool IsNight() const { return DayNightCycle.bIsNighttime; }

	UFUNCTION(BlueprintPure, Category = "NAR|DayNight|State")
	FString GetTimePhase() const;

	UFUNCTION(BlueprintPure, Category = "NAR|DayNight|State")
	FString GetFormattedTime() const;

	UFUNCTION(BlueprintPure, Category = "NAR|DayNight|State")
	float GetDayProgress() const;

	// ============================================
	// التأثيرات البيئية
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Effects")
	void UpdateLighting();

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Effects")
	FLinearColor GetAmbientLightColor() const;

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Effects")
	float GetLightIntensity() const;

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Effects")
	float GetVisibilityMultiplier() const;

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Effects")
	int32 GetEnemySpawnMultiplier() const;

	// ============================================
	// التحقق من الأوقات المهمة
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Check")
	bool IsTimeInRange(float StartHour, float EndHour);

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Check")
	bool IsDawn();

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Check")
	bool IsMorning();

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Check")
	bool IsNoon();

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Check")
	bool IsAfternoon();

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Check")
	bool IsDusk();

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Check")
	bool IsMidnight();

	// ============================================
	// جدولة الأحداث
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Scheduling")
	void ScheduleEvent(const FString& EventName, float TriggerHour);

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Scheduling")
	void CancelEvent(const FString& EventName);

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Scheduling")
	int32 GetScheduledEventCount() const;

	// ============================================
	// الحفظ والتحميل
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Save")
	void SaveCycle();

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Save")
	void LoadCycle();

	UFUNCTION(BlueprintCallable, Category = "NAR|DayNight|Save")
	void ResetCycle();

	// ============================================
	// الأحداث
	// ============================================
	DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnDayStarted);
	UPROPERTY(BlueprintAssignable, Category = "NAR|DayNight|Events")
	FOnDayStarted OnDayStarted;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnNightStarted);
	UPROPERTY(BlueprintAssignable, Category = "NAR|DayNight|Events")
	FOnNightStarted OnNightStarted;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTimeChanged, float, NewHour);
	UPROPERTY(BlueprintAssignable, Category = "NAR|DayNight|Events")
	FOnTimeChanged OnTimeChanged;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDayChanged, int32, NewDay);
	UPROPERTY(BlueprintAssignable, Category = "NAR|DayNight|Events")
	FOnDayChanged OnDayChanged;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnDawn);
	UPROPERTY(BlueprintAssignable, Category = "NAR|DayNight|Events")
	FOnDawn OnDawn;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnDusk);
	UPROPERTY(BlueprintAssignable, Category = "NAR|DayNight|Events")
	FOnDusk OnDusk;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnScheduledEvent, FString, EventName);
	UPROPERTY(BlueprintAssignable, Category = "NAR|DayNight|Events")
	FOnScheduledEvent OnScheduledEvent;

protected:
	// ============================================
	// بيانات الدورة
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|DayNight|Data")
	FDayNightCycle DayNightCycle;

	// ============================================
	// مراحل الوقت
	// ============================================
	UPROPERTY(EditDefaultsOnly, Category = "NAR|DayNight|Phases")
	TArray<FTimePhaseData> TimePhases;

	// ============================================
	// الأحداث المجدولة
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|DayNight|Data")
	TMap<FString, float> ScheduledEvents;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|DayNight|Data")
	TArray<FString> ExecutedEvents;

	// ============================================
	// الإعدادات
	// ============================================
	UPROPERTY(EditDefaultsOnly, Category = "NAR|DayNight|Settings")
	float DayStartHour = 6.0f;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|DayNight|Settings")
	float NightStartHour = 18.0f;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|DayNight|Settings")
	float DawnStartHour = 5.0f;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|DayNight|Settings")
	float DuskStartHour = 17.0f;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|DayNight|Settings")
	float CycleLength = 24.0f;

private:
	void UpdateDayNightCycle(float DeltaTime);
	void CheckPhaseTransition();
	void CheckScheduledEvents();
	void ApplyPhaseEffects();

	bool bWasDay = true;
	bool bWasNight = false;
};
