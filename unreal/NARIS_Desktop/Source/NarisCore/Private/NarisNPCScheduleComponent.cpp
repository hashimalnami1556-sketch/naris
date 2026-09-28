#include "NarisNPCScheduleComponent.h"
FName UNarisNPCScheduleComponent::ResolveActivity(float WorldHour) const { return (WorldHour>=6.f && WorldHour<18.f)?FName("Active"):FName("Rest"); }
