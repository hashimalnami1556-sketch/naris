// NAR_DayNightSystem.cpp — تنفيذ نظام اليوم والليل
#include "NAR_DayNightSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Math/UnrealMathUtility.h"

UNAR_DayNightSystem::UNAR_DayNightSystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f;

	// تهيئة مراحل الوقت
	TimePhases.Empty();

	// فجر (5-6)
	FTimePhaseData DawnPhase;
	DawnPhase.StartHour = 5.0f;
	DawnPhase.EndHour = 6.0f;
	DawnPhase.PhaseName = TEXT("فجر");
	DawnPhase.AmbientLight = FLinearColor(1.0f, 0.7f, 0.3f, 1.0f);
	DawnPhase.LightIntensity = 0.4f;
	DawnPhase.VisibilityMultiplier = 0.6f;
	DawnPhase.EnemySpawnMultiplier = 1;
	TimePhases.Add(DawnPhase);

	// صباح (6-12)
	FTimePhaseData MorningPhase;
	MorningPhase.StartHour = 6.0f;
	MorningPhase.EndHour = 12.0f;
	MorningPhase.PhaseName = TEXT("صباح");
	MorningPhase.AmbientLight = FLinearColor::White;
	MorningPhase.LightIntensity = 1.0f;
	MorningPhase.VisibilityMultiplier = 1.0f;
	MorningPhase.EnemySpawnMultiplier = 1;
	TimePhases.Add(MorningPhase);

	// ظهيرة (12-17)
	FTimePhaseData AfternoonPhase;
	AfternoonPhase.StartHour = 12.0f;
	AfternoonPhase.EndHour = 17.0f;
	AfternoonPhase.PhaseName = TEXT("ظهيرة");
	AfternoonPhase.AmbientLight = FLinearColor(1.0f, 1.0f, 0.9f, 1.0f);
	AfternoonPhase.LightIntensity = 1.0f;
	AfternoonPhase.VisibilityMultiplier = 1.0f;
	AfternoonPhase.EnemySpawnMultiplier = 1;
	TimePhases.Add(AfternoonPhase);

	// غسق (17-18)
	FTimePhaseData DuskPhase;
	DuskPhase.StartHour = 17.0f;
	DuskPhase.EndHour = 18.0f;
	DuskPhase.PhaseName = TEXT("غسق");
	DuskPhase.AmbientLight = FLinearColor(1.0f, 0.4f, 0.0f, 1.0f);
	DuskPhase.LightIntensity = 0.4f;
	DuskPhase.VisibilityMultiplier = 0.6f;
	DuskPhase.EnemySpawnMultiplier = 2;
	TimePhases.Add(DuskPhase);

	// ليل (18-5)
	FTimePhaseData NightPhase;
	NightPhase.StartHour = 18.0f;
	NightPhase.EndHour = 5.0f;
	NightPhase.PhaseName = TEXT("ليل");
	NightPhase.AmbientLight = FLinearColor(0.3f, 0.3f, 0.5f, 1.0f);
	NightPhase.LightIntensity = 0.2f;
	NightPhase.VisibilityMultiplier = 0.3f;
	NightPhase.EnemySpawnMultiplier = 3;
	TimePhases.Add(NightPhase);
}

void UNAR_DayNightSystem::BeginPlay()
{
	Super::BeginPlay();
	LoadCycle();
	UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] نظام اليوم والليل جاهز (الساعة: %.1f، اليوم: %d)"),
		DayNightCycle.CurrentHour, DayNightCycle.CurrentDay);
}

void UNAR_DayNightSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// تحديث دورة اليوم والليل
	UpdateDayNightCycle(DeltaTime);
	CheckPhaseTransition();
	CheckScheduledEvents();
	ApplyPhaseEffects();
}

// ============================================
// إدارة الوقت
// ============================================
void UNAR_DayNightSystem::SetCurrentHour(float Hour)
{
	float OldHour = DayNightCycle.CurrentHour;
	DayNightCycle.CurrentHour = FMath::Fmod(Hour, 24.0f);

	OnTimeChanged.Broadcast(DayNightCycle.CurrentHour);

	if (DayNightCycle.CurrentHour < OldHour)
	{
		DayNightCycle.CurrentDay++;
		OnDayChanged.Broadcast(DayNightCycle.CurrentDay);
	}

	CheckPhaseTransition();
	UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] تعيين الساعة: %.1f"), DayNightCycle.CurrentHour);
}

void UNAR_DayNightSystem::AddHours(float Hours)
{
	SetCurrentHour(DayNightCycle.CurrentHour + Hours);
}

void UNAR_DayNightSystem::SetTimeMultiplier(float Multiplier)
{
	DayNightCycle.TimeMultiplier = FMath::Max(Multiplier, 0.1f);
	UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] تعيين مضاعف الوقت: %.2f"), DayNightCycle.TimeMultiplier);
}

// ============================================
// حالة اليوم والليل
// ============================================
FString UNAR_DayNightSystem::GetTimePhase() const
{
	for (const FTimePhaseData& Phase : TimePhases)
	{
		if (DayNightCycle.CurrentHour >= Phase.StartHour && DayNightCycle.CurrentHour < Phase.EndHour)
		{
			return Phase.PhaseName;
		}
	}

	return TEXT("ليل");
}

FString UNAR_DayNightSystem::GetFormattedTime() const
{
	int32 Hours = (int32)DayNightCycle.CurrentHour;
	int32 Minutes = (int32)((DayNightCycle.CurrentHour - Hours) * 60);

	return FString::Printf(TEXT("%02d:%02d"), Hours, Minutes);
}

float UNAR_DayNightSystem::GetDayProgress() const
{
	return DayNightCycle.CurrentHour / DayNightCycle.CycleLength;
}

// ============================================
// التأثيرات البيئية
// ============================================
void UNAR_DayNightSystem::UpdateLighting()
{
	ApplyPhaseEffects();
}

FLinearColor UNAR_DayNightSystem::GetAmbientLightColor() const
{
	for (const FTimePhaseData& Phase : TimePhases)
	{
		if (DayNightCycle.CurrentHour >= Phase.StartHour && DayNightCycle.CurrentHour < Phase.EndHour)
		{
			return Phase.AmbientLight;
		}
	}

	return FLinearColor::White;
}

float UNAR_DayNightSystem::GetLightIntensity() const
{
	for (const FTimePhaseData& Phase : TimePhases)
	{
		if (DayNightCycle.CurrentHour >= Phase.StartHour && DayNightCycle.CurrentHour < Phase.EndHour)
		{
			return Phase.LightIntensity;
		}
	}

	return 1.0f;
}

float UNAR_DayNightSystem::GetVisibilityMultiplier() const
{
	for (const FTimePhaseData& Phase : TimePhases)
	{
		if (DayNightCycle.CurrentHour >= Phase.StartHour && DayNightCycle.CurrentHour < Phase.EndHour)
		{
			return Phase.VisibilityMultiplier;
		}
	}

	return 1.0f;
}

int32 UNAR_DayNightSystem::GetEnemySpawnMultiplier() const
{
	for (const FTimePhaseData& Phase : TimePhases)
	{
		if (DayNightCycle.CurrentHour >= Phase.StartHour && DayNightCycle.CurrentHour < Phase.EndHour)
		{
			return Phase.EnemySpawnMultiplier;
		}
	}

	return 1;
}

// ============================================
// التحقق من الأوقات المهمة
// ============================================
bool UNAR_DayNightSystem::IsTimeInRange(float StartHour, float EndHour)
{
	if (StartHour <= EndHour)
	{
		return DayNightCycle.CurrentHour >= StartHour && DayNightCycle.CurrentHour < EndHour;
	}

	return DayNightCycle.CurrentHour >= StartHour || DayNightCycle.CurrentHour < EndHour;
}

bool UNAR_DayNightSystem::IsDawn()
{
	return IsTimeInRange(DawnStartHour, DawnStartHour + 1.0f);
}

bool UNAR_DayNightSystem::IsMorning()
{
	return IsTimeInRange(6.0f, 12.0f);
}

bool UNAR_DayNightSystem::IsNoon()
{
	return IsTimeInRange(12.0f, 12.5f);
}

bool UNAR_DayNightSystem::IsAfternoon()
{
	return IsTimeInRange(12.0f, 17.0f);
}

bool UNAR_DayNightSystem::IsDusk()
{
	return IsTimeInRange(DuskStartHour, DuskStartHour + 1.0f);
}

bool UNAR_DayNightSystem::IsMidnight()
{
	return IsTimeInRange(23.5f, 0.5f);
}

// ============================================
// جدولة الأحداث
// ============================================
void UNAR_DayNightSystem::ScheduleEvent(const FString& EventName, float TriggerHour)
{
	ScheduledEvents.Add(EventName, TriggerHour);
	ExecutedEvents.Empty();
	UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] جدولة حدث: %s في الساعة %.1f"), *EventName, TriggerHour);
}

void UNAR_DayNightSystem::CancelEvent(const FString& EventName)
{
	if (ScheduledEvents.Contains(EventName))
	{
		ScheduledEvents.Remove(EventName);
		UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] إلغاء حدث: %s"), *EventName);
	}
}

int32 UNAR_DayNightSystem::GetScheduledEventCount() const
{
	return ScheduledEvents.Num();
}

// ============================================
// الحفظ والتحميل
// ============================================
void UNAR_DayNightSystem::SaveCycle()
{
	// سيتم تطبيق الحفظ مع نظام الحفظ الرئيسي
	UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] حفظ دورة اليوم والليل"));
}

void UNAR_DayNightSystem::LoadCycle()
{
	// سيتم تطبيق التحميل مع نظام الحفظ الرئيسي
	UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] تحميل دورة اليوم والليل"));
}

void UNAR_DayNightSystem::ResetCycle()
{
	DayNightCycle.CurrentHour = 12.0f;
	DayNightCycle.CurrentDay = 1;
	DayNightCycle.TotalGameTime = 0.0f;
	ExecutedEvents.Empty();
	bWasDay = true;
	bWasNight = false;

	UE_LOG(LogTemp, Warning, TEXT("[NAR_DayNight] إعادة تعيين دورة اليوم والليل"));
}

// ============================================
// وظائف داخلية
// ============================================
void UNAR_DayNightSystem::UpdateDayNightCycle(float DeltaTime)
{
	// تحديث الساعة بناءً على مضاعف الوقت
	float HourToAdd = (DeltaTime / 60.0f / DayNightCycle.MinutesPerGameHour) * DayNightCycle.TimeMultiplier;
	DayNightCycle.CurrentHour += HourToAdd;
	DayNightCycle.TotalGameTime += DeltaTime;

	// التحقق من تجاوز 24 ساعة
	if (DayNightCycle.CurrentHour >= 24.0f)
	{
		DayNightCycle.CurrentHour -= 24.0f;
		DayNightCycle.CurrentDay++;
		OnDayChanged.Broadcast(DayNightCycle.CurrentDay);
		UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] اليوم الجديد: %d"), DayNightCycle.CurrentDay);
	}
}

void UNAR_DayNightSystem::CheckPhaseTransition()
{
	bool bIsCurrentlyDay = IsTimeInRange(DayStartHour, NightStartHour);
	bool bIsCurrentlyNight = !bIsCurrentlyDay;

	DayNightCycle.bIsDaytime = bIsCurrentlyDay;
	DayNightCycle.bIsNighttime = bIsCurrentlyNight;

	// التحقق من الانتقالات
	if (bIsCurrentlyDay && !bWasDay)
	{
		OnDayStarted.Broadcast();
		UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] بدء اليوم"));
		bWasDay = true;
		bWasNight = false;
	}

	if (bIsCurrentlyNight && !bWasNight)
	{
		OnNightStarted.Broadcast();
		UE_LOG(LogTemp, Warning, TEXT("[NAR_DayNight] بدء الليل"));
		bWasNight = true;
		bWasDay = false;
	}

	// التحقق من الفجر والغسق
	static float LastHour = 0.0f;
	if (DayNightCycle.CurrentHour > DawnStartHour && LastHour < DawnStartHour)
	{
		OnDawn.Broadcast();
		UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] الفجر"));
	}

	if (DayNightCycle.CurrentHour > DuskStartHour && LastHour < DuskStartHour)
	{
		OnDusk.Broadcast();
		UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] الغسق"));
	}

	LastHour = DayNightCycle.CurrentHour;
}

void UNAR_DayNightSystem::CheckScheduledEvents()
{
	for (auto& Pair : ScheduledEvents)
	{
		const FString& EventName = Pair.Key;
		float TriggerHour = Pair.Value;

		// التحقق من عدم تنفيذ الحدث من قبل
		if (!ExecutedEvents.Contains(EventName))
		{
			// التحقق إذا كنا قريبين من ساعة التفعيل
			if (FMath::Abs(DayNightCycle.CurrentHour - TriggerHour) < 0.05f)
			{
				OnScheduledEvent.Broadcast(EventName);
				ExecutedEvents.Add(EventName);
				UE_LOG(LogTemp, Log, TEXT("[NAR_DayNight] تنفيذ حدث مجدول: %s"), *EventName);
			}
		}
	}
}

void UNAR_DayNightSystem::ApplyPhaseEffects()
{
	// يتم تطبيق التأثيرات من خلال الإشارات والأحداث
}
