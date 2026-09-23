#include "NarisEnergyComponent.h"

UNarisEnergyComponent::UNarisEnergyComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UNarisEnergyComponent::Spend(float Amount)
{
    if (Amount <= 0.f || Energy < Amount)
    {
        return false;
    }

    Energy -= Amount;
    return true;
}

void UNarisEnergyComponent::Restore(float Amount)
{
    Energy = FMath::Clamp(
        Energy + FMath::Max(0.f, Amount),
        0.f,
        MaxEnergy
    );
}

void UNarisEnergyComponent::SetEssence(ENarisEssence NewEssence)
{
    ActiveEssence = NewEssence;
}

void UNarisEnergyComponent::CycleEssence(int32 Direction)
{
    constexpr int32 EssenceCount = 5;
    const int32 Current = static_cast<int32>(ActiveEssence);
    const int32 Step = Direction >= 0 ? 1 : -1;
    const int32 Next = (Current + Step + EssenceCount) % EssenceCount;
    ActiveEssence = static_cast<ENarisEssence>(Next);
}

FText UNarisEnergyComponent::GetActiveEssenceDisplayName() const
{
    switch (ActiveEssence)
    {
        case ENarisEssence::NarisFlame:
            return NSLOCTEXT("NARIS", "EssenceNarisFlame", "Naris Flame");
        case ENarisEssence::Ash:
            return NSLOCTEXT("NARIS", "EssenceAsh", "Ash");
        case ENarisEssence::Aether:
            return NSLOCTEXT("NARIS", "EssenceAether", "Aether");
        case ENarisEssence::Void:
            return NSLOCTEXT("NARIS", "EssenceVoid", "Void");
        case ENarisEssence::Radiant:
            return NSLOCTEXT("NARIS", "EssenceRadiant", "Radiant");
        default:
            return NSLOCTEXT("NARIS", "EssenceUnknown", "Unknown");
    }
}
