# تقرير NARIS Master Build
تاريخ الفحص: 27 سبتمبر 2026
الجهاز: AsusRog
المشروع: Unreal Engine 5.7.4
الفرع: production/masterbuild-20260927

## الحالة
المشروع قيد التطوير، ولم يجتز بعد قبول الإصدار النهائي. أنجز هذا التحديث حفظ إعدادات المستخدم، والتحقق من البناء والمهام والحفظ، وإنشاء حزمتَي QA وShipping Candidate. لا أضع نسبة مئوية لأن معايير القبول لم تُوزن، وبعض الأنظمة لم تُختبر بصريًا وعلى جهاز تحكم.

## ما تم إنجازه في هذا التحديث
- حفظ مستوى الجودة باستخدام GameUserSettings، وحفظ الصوت وإمكانية الوصول في ملف إعدادات المستخدم واسترجاعهما عند بدء اللعبة.
- إبقاء اختبار Settings دون أثر على قيم اللاعب: يستعيد القيم الأصلية بعد الاختبار.
- بناء NARISEditor Development بنجاح على UE 5.7.4.
- نجاح اختباري الأتمتة: NARIS.Benchmark.ParsesEnemyCount وNARIS.FrontEnd.StartsInMenuAndCanStart.
- نجاح NARIS_QUEST_SMOKE: المهام، فتح البوابة، الحفظ والاسترجاع، الفصول، إعدادات Accessibility، الصوت، VFX ونقطة التفتيش.
- نجاح إنشاء القائمة العربية عبر UMG عند إقلاع UnrealEditor-Cmd، ونجاح اختبار الإقلاع نفسه في حزمة Development (NARIS_UI_MAIN_MENU READY RTL=1 Buttons=4).
- نجاح حزمة Windows Development واختبارها بعد التغليف؛ سجل الحزمة يحتوي NARIS_QUEST_SMOKE PASS.
- نجاح بناء Windows Shipping مع كل الخرائط. هذه حزمة مرشحة داخل Staging وليست إعلان جاهزية إصدار.
- حفظ مخرجات البناء الجديدة في مجلدات منفصلة، وإضافتها إلى .gitignore حتى لا تدخل ملفات التنفيذ والـ PAK إلى Git.
- لم أدمج فرع العمل في main.

## الملفات المعدلة
- Source/NarisCore/Public/NarisUserSettingsSubsystem.h: دورة تهيئة/إيقاف النظام، قراءة/حفظ التفضيلات، وإضافة getters لمستويات الصوت.
- Source/NarisCore/Private/NarisUserSettingsSubsystem.cpp: تحميل/حفظ القيم والتحقق من حدودها، مع SaveSettings لمستوى الرسوم.
- Source/NarisCore/Private/NarisGameModeBase.cpp: إعادة إعدادات Accessibility الأصلية بعد فحص الدخان.
- Source/NarisCore/NarisCore.Build.cs: إضافة UMG وSlate وSlateCore.
- Source/NarisCore/Public/NarisHUD.h وPrivate/NarisHUD.cpp: إظهار شاشة القائمة العربية عند الإقلاع.
- Source/NarisCore/Public/NarisNativeMenuWidget.h وPrivate/NarisNativeMenuWidget.cpp: قائمة UMG عربية مع RTL وبدء/متابعة/إعدادات/خروج.
- .gitignore: استثناء مجلدات حزم QA وStaging وRelease المنشأة.

## الملفات/المخرجات الجديدة
- 06_Builds/Development/NARIS_QA_20260927/Windows/NARIS.exe
- 06_Builds/Staging/NARIS_ShippingCandidate_20260927/Windows/NARIS/Binaries/Win64/NARIS-Win64-Shipping.exe
- 07_Docs/Reports/NARIS_MASTER_BUILD_REPORT.md
- 07_Docs/Reports/NARIS_MASTER_BUILD_REPORT.html
- 08_Integration/Figma/links.md
- Source/NarisCore/Public/NarisNativeMenuWidget.h
- Source/NarisCore/Private/NarisNativeMenuWidget.cpp: ملف Figma المقروء وحالة Foundation الحالية والمتطلبات الناقصة.

## شجرة المشروع قبل التحديث
(مسارات العمل الفعلية ذات الصلة، مع اختصار مجلدات Unreal المولّدة)
NARIS/
├── Docs/                         مستندات مسطّحة ومجلدات توثيق جرى تنظيمها
├── SourceAssets/References/      صور مرجعية وأصول مصدرية محلية
├── Source/NarisCore/             كود Unreal
├── Content/                      خرائط وأصول اللعبة
├── Packages/Legacy/              حزم التحديث الأصلية محفوظة
├── Tools/                        سكربتات البناء والاختبار
└── Releases/                     إصدارات ونتائج تاريخية

## شجرة المشروع بعد التنظيم والفحص
NARIS/
├── 00_Core/  01_Design/  02_Projects/  03_Assets/
├── 04_Packages/Legacy/  05_Tools/  06_Builds/
├── 07_Docs/Reports/  08_Integration/
├── Source/  Content/  Config/  NARIS.uproject
├── SourceAssets/References/Images/ (33 صورة مرجعية موجودة على الجهاز)
└── Packages/Legacy/ (الحزم الثلاث الأصلية، دون تعديل)
وُضعت مخرجات الاختبار في 06_Builds/Development و06_Builds/Staging. حافظت على مسارات Unreal الحية كما هي لتجنّب كسر المشروع.

## ما بقي قبل قبول الإصدار
- Main Menu عربية عبر UMG C++ واتجاه RTL؛ بناء الحزمة واختبار الإقلاع headless نجحا. المتبقي HUD وPause وSettings وGame Over كواجهات UMG، خط عربي مضمّن، ثم فحص مرئي 1080p و4K ولوحة التحكم.
- ربط إعدادات Master/Music/SFX بمزيج الصوت الفعلي؛ القيم تُحفظ الآن، لكن Audio Director لا يربطها بعد بـ Sound Class أو Submix.
- ملف Figma لا يحتوي الشاشات النهائية. القائمة الحالية UMG مبنية بالكود؛ Content/UI/Widgets ما زال بلا Widget Blueprints.
- مراجعة محتوى الحزم القديمة؛ لا يمكن تكوين Unified Update صحيح من Patch فارغ ومقاطع كود متعارضة دون تنفيذ UI الفعلي.
- توحيد نسخة الجهاز مع فرع W04/main ما زال منفصلًا؛ هذا التحديث لم يدمج main ولم يرفع فرع الإنتاج.
- اختبار Shipping بصريًا وقياس أداء GPU/FPS/الذاكرة على خرائط اللعب، ثم اعتماد أو رفض المرشح.
- اعتماد الأصول الفنية والأنيميشن النهائية، وفحص قبول المسار الكامل من البداية إلى الخروج.

## ملاحظات الملفات والمراجع
- الصور التي أشار إليها الطلب عبر /workspace/scratch/.../project_sources غير متاحة في مساحة العمل الحالية، لذلك لم أعدّلها أو أعِد تسميتها.
- تحققت على AsusRog من وجود 33 صورة مرجعية داخل SourceAssets/References/Images.
- حزم Legacy لم تُطبّق تلقائيًا. Packages/README.md يوضح أن UI4.1 يحتوي Patch فارغًا وأن حزمة Offline تتعارض مع شاشة البداية.
- تقرير HTML يطابق حالة هذا التقرير وقت إنشائه.