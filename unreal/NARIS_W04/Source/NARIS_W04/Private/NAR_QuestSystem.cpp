// NAR_QuestSystem.cpp — تنفيذ نظام المهام
#include "NAR_QuestSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UNAR_QuestSystem::UNAR_QuestSystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f;
}

void UNAR_QuestSystem::BeginPlay()
{
	Super::BeginPlay();
	LoadQuestData();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Quest] نظام المهام جاهز"));
}

void UNAR_QuestSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	UpdateQuestTimers(DeltaTime);
	CheckQuestFailures();
}

// ============================================
// إدارة المهام
// ============================================
bool UNAR_QuestSystem::RegisterQuest(const FQuestData& QuestData)
{
	if (QuestDatabase.Contains(QuestData.QuestID))
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Quest] مهمة موجودة بالفعل: %s"), *QuestData.QuestID);
		return false;
	}

	QuestDatabase.Add(QuestData.QuestID, QuestData);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Quest] تسجيل مهمة: %s (%s)"), *QuestData.QuestName, *QuestData.QuestID);

	return true;
}

bool UNAR_QuestSystem::UnregisterQuest(const FString& QuestID)
{
	if (!QuestDatabase.Contains(QuestID))
	{
		return false;
	}

	QuestDatabase.Remove(QuestID);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Quest] إزالة مهمة: %s"), *QuestID);

	return true;
}

FQuestData UNAR_QuestSystem::GetQuest(const FString& QuestID)
{
	if (QuestDatabase.Contains(QuestID))
	{
		return QuestDatabase[QuestID];
	}

	return FQuestData();
}

TArray<FQuestData> UNAR_QuestSystem::GetAllQuests() const
{
	TArray<FQuestData> AllQuests;
	QuestDatabase.GenerateValueArray(AllQuests);
	return AllQuests;
}

TArray<FQuestData> UNAR_QuestSystem::GetActiveQuests() const
{
	TArray<FQuestData> ActiveQuests;

	for (const auto& Pair : QuestDatabase)
	{
		if (Pair.Value.State == EQuestState::Active)
		{
			ActiveQuests.Add(Pair.Value);
		}
	}

	return ActiveQuests;
}

TArray<FQuestData> UNAR_QuestSystem::GetCompletedQuests() const
{
	TArray<FQuestData> CompletedQuests;

	for (const auto& Pair : QuestDatabase)
	{
		if (Pair.Value.State == EQuestState::Completed)
		{
			CompletedQuests.Add(Pair.Value);
		}
	}

	return CompletedQuests;
}

// ============================================
// قبول وإنهاء المهام
// ============================================
bool UNAR_QuestSystem::AcceptQuest(const FString& QuestID)
{
	if (!QuestDatabase.Contains(QuestID))
	{
		return false;
	}

	FQuestData& Quest = QuestDatabase[QuestID];

	if (Quest.State != EQuestState::Inactive)
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Quest] لا يمكن قبول المهمة: %s (الحالة: %d)"), *QuestID, (int32)Quest.State);
		return false;
	}

	if (GetActiveQuestCount() >= MaxActiveQuests)
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Quest] تم الوصول للحد الأقصى للمهام النشطة"));
		return false;
	}

	Quest.State = EQuestState::Active;
	Quest.AcceptedTime = GetWorld()->GetTimeSeconds();
	Quest.RemainingTime = Quest.TimeLimit;

	OnQuestAccepted.Broadcast(Quest);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Quest] قبول مهمة: %s"), *Quest.QuestName);

	return true;
}

bool UNAR_QuestSystem::AbandonQuest(const FString& QuestID)
{
	if (!QuestDatabase.Contains(QuestID))
	{
		return false;
	}

	FQuestData& Quest = QuestDatabase[QuestID];

	if (Quest.State != EQuestState::Active)
	{
		return false;
	}

	Quest.State = EQuestState::Abandoned;
	OnQuestAbandoned.Broadcast(Quest);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Quest] التخلي عن مهمة: %s"), *QuestID);

	return true;
}

bool UNAR_QuestSystem::CompleteQuest(const FString& QuestID)
{
	if (!QuestDatabase.Contains(QuestID))
	{
		return false;
	}

	FQuestData& Quest = QuestDatabase[QuestID];

	if (Quest.State != EQuestState::Active)
	{
		return false;
	}

	// التحقق من إكمال جميع الأهداف الإلزامية
	for (const FQuestObjective& Objective : Quest.Objectives)
	{
		if (!Objective.bIsOptional && !Objective.bIsCompleted)
		{
			UE_LOG(LogTemp, Warning, TEXT("[NAR_Quest] لم تكتمل جميع الأهداف المطلوبة"));
			return false;
		}
	}

	Quest.State = EQuestState::Completed;
	Quest.CompletedTime = GetWorld()->GetTimeSeconds();
	CompletedQuestCount++;

	OnQuestCompleted.Broadcast(Quest);
	AddRecentCompletion(QuestID);

	UE_LOG(LogTemp, Warning, TEXT("[NAR_Quest] إكمال مهمة: %s (XP: %d، العملة: %d)"),
		*Quest.QuestName, Quest.Reward.RewardXP, Quest.Reward.RewardCurrency);

	return true;
}

bool UNAR_QuestSystem::FailQuest(const FString& QuestID)
{
	if (!QuestDatabase.Contains(QuestID))
	{
		return false;
	}

	FQuestData& Quest = QuestDatabase[QuestID];

	if (!Quest.bCanFail || Quest.State != EQuestState::Active)
	{
		return false;
	}

	Quest.State = EQuestState::Failed;
	FailedQuestCount++;

	OnQuestFailed.Broadcast(Quest);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Quest] فشل المهمة: %s"), *QuestID);

	return true;
}

bool UNAR_QuestSystem::CanAcceptQuest(const FString& QuestID, int32 PlayerLevel)
{
	if (!QuestDatabase.Contains(QuestID))
	{
		return false;
	}

	const FQuestData& Quest = QuestDatabase[QuestID];

	// التحقق من مستوى اللاعب
	if (PlayerLevel < Quest.RequiredLevel)
	{
		return false;
	}

	// التحقق من المهام الأساسية
	for (const FString& PrereqID : Quest.PrerequisiteQuests)
	{
		if (QuestDatabase.Contains(PrereqID))
		{
			const FQuestData& PrereqQuest = QuestDatabase[PrereqID];
			if (PrereqQuest.State != EQuestState::Completed)
			{
				return false;
			}
		}
	}

	return Quest.State == EQuestState::Inactive;
}

// ============================================
// إدارة الأهداف
// ============================================
bool UNAR_QuestSystem::UpdateObjectiveProgress(const FString& QuestID, const FString& ObjectiveID, int32 ProgressAmount)
{
	if (!QuestDatabase.Contains(QuestID))
	{
		return false;
	}

	FQuestData& Quest = QuestDatabase[QuestID];

	for (FQuestObjective& Objective : Quest.Objectives)
	{
		if (Objective.ObjectiveID == ObjectiveID)
		{
			if (!Objective.bIsCompleted)
			{
				Objective.CurrentCount += ProgressAmount;
				Objective.CurrentCount = FMath::Min(Objective.CurrentCount, Objective.RequiredCount);

				if (Objective.CurrentCount >= Objective.RequiredCount)
				{
					Objective.bIsCompleted = true;
				}

				OnObjectiveUpdated.Broadcast(QuestID, Objective);

				// تحديث تقدم المهمة
				float QuestProgress = 0.0f;
				int32 CompletedObjectives = 0;

				for (const FQuestObjective& Obj : Quest.Objectives)
				{
					if (Obj.bIsCompleted)
					{
						CompletedObjectives++;
					}
				}

				QuestProgress = (float)CompletedObjectives / Quest.Objectives.Num();
				OnQuestProgressChanged.Broadcast(QuestID, QuestProgress);

				// إكمال تلقائي إذا كانت جميع الأهداف مكتملة
				if (bAutoCompleteOnAllObjectives && QuestProgress >= 1.0f)
				{
					CompleteQuest(QuestID);
				}

				return true;
			}
		}
	}

	return false;
}

bool UNAR_QuestSystem::CompleteObjective(const FString& QuestID, const FString& ObjectiveID)
{
	if (!QuestDatabase.Contains(QuestID))
	{
		return false;
	}

	FQuestData& Quest = QuestDatabase[QuestID];

	for (FQuestObjective& Objective : Quest.Objectives)
	{
		if (Objective.ObjectiveID == ObjectiveID)
		{
			Objective.bIsCompleted = true;
			OnObjectiveUpdated.Broadcast(QuestID, Objective);
			return true;
		}
	}

	return false;
}

FQuestObjective UNAR_QuestSystem::GetObjective(const FString& QuestID, const FString& ObjectiveID)
{
	if (QuestDatabase.Contains(QuestID))
	{
		const FQuestData& Quest = QuestDatabase[QuestID];
		for (const FQuestObjective& Objective : Quest.Objectives)
		{
			if (Objective.ObjectiveID == ObjectiveID)
			{
				return Objective;
			}
		}
	}

	return FQuestObjective();
}

TArray<FQuestObjective> UNAR_QuestSystem::GetQuestObjectives(const FString& QuestID)
{
	TArray<FQuestObjective> Objectives;

	if (QuestDatabase.Contains(QuestID))
	{
		Objectives = QuestDatabase[QuestID].Objectives;
	}

	return Objectives;
}

float UNAR_QuestSystem::GetObjectiveProgress(const FString& QuestID, const FString& ObjectiveID)
{
	if (QuestDatabase.Contains(QuestID))
	{
		const FQuestData& Quest = QuestDatabase[QuestID];
		for (const FQuestObjective& Objective : Quest.Objectives)
		{
			if (Objective.ObjectiveID == ObjectiveID)
			{
				return (float)Objective.CurrentCount / Objective.RequiredCount;
			}
		}
	}

	return 0.0f;
}

// ============================================
// المكافآت
// ============================================
FQuestReward UNAR_QuestSystem::GetQuestReward(const FString& QuestID)
{
	if (QuestDatabase.Contains(QuestID))
	{
		return QuestDatabase[QuestID].Reward;
	}

	return FQuestReward();
}

bool UNAR_QuestSystem::ClaimQuestReward(const FString& QuestID)
{
	if (!QuestDatabase.Contains(QuestID))
	{
		return false;
	}

	FQuestData& Quest = QuestDatabase[QuestID];

	if (Quest.State != EQuestState::Completed)
	{
		return false;
	}

	TotalRewardXP += Quest.Reward.RewardXP;
	TotalRewardCurrency += Quest.Reward.RewardCurrency;

	OnRewardClaimed.Broadcast(QuestID, Quest.Reward);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Quest] مطالبة مكافآت: %s"), *QuestID);

	return true;
}

// ============================================
// الاستعلامات
// ============================================
TArray<FQuestData> UNAR_QuestSystem::GetQuestsByType(EQuestType QuestType)
{
	TArray<FQuestData> FilteredQuests;

	for (const auto& Pair : QuestDatabase)
	{
		if (Pair.Value.QuestType == QuestType)
		{
			FilteredQuests.Add(Pair.Value);
		}
	}

	return FilteredQuests;
}

TArray<FQuestData> UNAR_QuestSystem::GetQuestsByDifficulty(EQuestDifficulty Difficulty)
{
	TArray<FQuestData> FilteredQuests;

	for (const auto& Pair : QuestDatabase)
	{
		if (Pair.Value.Difficulty == Difficulty)
		{
			FilteredQuests.Add(Pair.Value);
		}
	}

	return FilteredQuests;
}

bool UNAR_QuestSystem::IsQuestAvailable(const FString& QuestID, int32 PlayerLevel)
{
	return CanAcceptQuest(QuestID, PlayerLevel);
}

float UNAR_QuestSystem::GetCompletionPercentage() const
{
	if (QuestDatabase.Num() == 0)
	{
		return 0.0f;
	}

	return (float)CompletedQuestCount / QuestDatabase.Num() * 100.0f;
}

// ============================================
// الحفظ والتحميل
// ============================================
void UNAR_QuestSystem::SaveQuestData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Quest] حفظ بيانات المهام"));
}

void UNAR_QuestSystem::LoadQuestData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Quest] تحميل بيانات المهام"));
}

void UNAR_QuestSystem::ResetAllQuests()
{
	for (auto& Pair : QuestDatabase)
	{
		Pair.Value.State = EQuestState::Inactive;
		for (FQuestObjective& Objective : Pair.Value.Objectives)
		{
			Objective.CurrentCount = 0;
			Objective.bIsCompleted = false;
		}
	}

	CompletedQuestCount = 0;
	FailedQuestCount = 0;
	TotalRewardXP = 0;
	TotalRewardCurrency = 0;
	RecentlyCompleted.Empty();

	UE_LOG(LogTemp, Warning, TEXT("[NAR_Quest] إعادة تعيين جميع المهام"));
}

// ============================================
// وظائف داخلية
// ============================================
void UNAR_QuestSystem::UpdateQuestTimers(float DeltaTime)
{
	for (auto& Pair : QuestDatabase)
	{
		FQuestData& Quest = Pair.Value;

		if (Quest.State == EQuestState::Active && Quest.TimeLimit > 0.0f)
		{
			Quest.RemainingTime -= DeltaTime;

			if (Quest.RemainingTime <= 0.0f)
			{
				FailQuest(Quest.QuestID);
			}
		}
	}
}

void UNAR_QuestSystem::CheckQuestFailures()
{
	for (auto& Pair : QuestDatabase)
	{
		FQuestData& Quest = Pair.Value;

		// يمكن إضافة منطق فشل إضافي هنا
	}
}

int32 UNAR_QuestSystem::GetActiveQuestCount() const
{
	return GetActiveQuests().Num();
}

void UNAR_QuestSystem::AddRecentCompletion(const FString& QuestID)
{
	RecentlyCompleted.Insert(QuestID, 0);

	if (RecentlyCompleted.Num() > MaxRecentQuests)
	{
		RecentlyCompleted.RemoveAt(MaxRecentQuests);
	}
}
