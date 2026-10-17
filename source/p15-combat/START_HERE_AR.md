# NARIS P15 — ربط التحكم والحركة داخل Unreal 5.7

هذه حزمة كود وأصول محدّثة. لم تُثبّت تلقائيًا على جهازك ولم تُجمّع داخل Unreal في هذه الجلسة، ولا تحتوي EXE. راجع نتيجة الاختبارات الحالية في Reports/verification.json.

## الإعداد الذي نُفّذ في الكود

| الإعداد | القيمة الافتراضية الجديدة |
|---|---:|
| سرعة المشي | 400 سم/ث |
| التسارع | 1600 سم/ث² |
| تباطؤ الفرملة | 1000 سم/ث² |
| احتكاك الأرض | 5 |
| احتكاك الفرملة المستقل | 2 |
| معدل دوران الجسم | 450 درجة/ث |
| تسارع اتجاه القفل | 1800 درجة/ث² |
| ثابت تنعيم الإدخال | 25ms |
| تخزين أوامر القتال | 150ms |
| قفل الإصابة | 200ms |
| CameraLagSpeed / RotationLagSpeed الحرة | 6 / 8 |
| CameraLagSpeed / RotationLagSpeed في القتال | 18 / 20 |

قيم LagSpeed الأعلى تقلل تأخر الكاميرا. ثابت تنعيم الإدخال لا يثبت زمن الاستجابة من الجهاز إلى الشاشة. قيم المشي أعلاه نقاط بداية تحتاج قياسًا.

## التركيب والربط

1. أغلق Editor، واستخدم نسخة احتياطية من مشروع UE 5.7 بلغة C++. انسخ Plugins/NarisCombat كاملة بدل النسخة السابقة، ثم جمّع Editor. لا تخلط ملفات إضافتين ولا تضف مالكي صحة W04 وP15 إلى الشخصية نفسها.
2. أضف NarisP15CombatComponent وNarisP15MovementInputComponent إلى Character تجريبي. إضافة المكوّن هي الاختيار الصريح لهذا المسار؛ لا تُستبدل شخصيات W04 أو خرائطها تلقائيًا. المكوّن الجديد يفعّل ملف الحركة والكاميرا افتراضيًا، لكن Blueprint قد يحتفظ بقيم سابقة محفوظة: راجعها في Details.
3. اربط Enhanced Input Axis2D: حدث Triggered إلى SetMoveInput، وCompleted/Canceled إلى ResetMoveInput. X يمين وY أمام. أزل أي AddMovementInput آخر للمحور نفسه. لا تكرر DeadZone والمنحنى في المكوّن وEnhanced Input معًا.
4. اربط هجوم/مراوغة/صد بضغطة Started. قبل الإيقاف أو فتح الواجهة أو فقدان التركيز أو تبديل التحكم، استدع ResetMoveInput وClearBufferedInput صراحة؛ لا تعتمد على Tick أثناء الإيقاف.
5. عيّن Mesh وSkeleton وAnimation Blueprint وMontages متوافقة، مع RateScale=1 وSlot فعلي وweapon_base/weapon_tip. شغّل GetSetupIssues على مكوّن القتال وعلى مكوّن الحركة. نقص ربط الكاميرا يُعالج بتحديد CameraBoomComponentName أو تعطيل ملف الكاميرا، وليس بإنشاء كاميرا ثانية.
6. أضف NARIS P15 Attack Window إلى المونتاج خلال إطارات التلامس فقط. للإلغاء الاختياري أضف NARIS P15 Cancel Window بعد الزمن صفر، بمدة موجبة دون تداخل نوافذ. اربط RequestCancelCurrentAction بزر الإلغاء. دون نافذة نشطة يُرفض الطلب.
7. الإلغاء هنا يوقف عرض الحركة والدفاع والضرب، ويحتفظ بالكلفة والتعافي الأصلي؛ لا يمنح هجومًا/مراوغة جديدة فورًا. الإصابة المقبولة تقفل التحكم 0.2 ثانية أو حتى انتهاء التعافي السابق إن كان أبعد. HitRecoverySeconds=0 يعطّل قفل الإصابة عمدًا.
8. استخدم SetCombatMode وSetLockOnTarget؛ مرّر Null لفك القفل. يرفض السيرفر هدفًا غير صالح أو الشخصية نفسها أو هدفًا خارج العالم/مدى 2500 سم. أثناء القفل لا تضف Look Yaw آخر ينافس المكوّن. CharacterMovement يظل مسؤولًا عن دوران الممثل.
9. تستخدم الكاميرا SpringArm موجودة. إذا وُجد أكثر من ذراع، اختر اسم المكوّن بالضبط. تأكد من أن إعداد الكاميرا الحالي يستخدم اتجاه Controller إذا أردت أن يتبع القفل. لا يغيّر الكود طول الذراع أو التصادم أو موضع الكاميرا. تُستعاد الإعدادات الأصلية عند إزالة المكوّن.
10. انسخ Animation Blueprint قبل تغيير صنفه الأب إلى NarisP15LocomotionAnimInstance، واحفظ أي منطق موروث تحتاجه. المتغيرات Speed وDirectionDegrees تغذي Blend Space ثنائي المحور؛ Starting/Stopping/Pivoting وFacingYawDelta وShouldTurnInPlace تغذي انتقالات وحركات موجودة فعلًا. ابدأ بمزج 0.1–0.2 ثانية. Slot القتال يجب أن يُقيّم داخل المخطط.

## ما يبقى داخل Unreal

لم تُنتج هذه الحزمة حركات مشي أو Start/Stop/Pivot أو Turn In Place جديدة، ولا Blend Space أو Animation Blueprint بصيغة uasset. الشخصية المصححة ما زالت بالمحتوى الأصلي (18 عظمة وIdle واحدة). لا تصنع الإشارات البرمجية حركات مفقودة.

Foot IK/Foot Placement يتطلبان ربط القدمين والمفاصل والمخطط والحركات المناسبة. Motion Warping يضبط Root Motion نحو هدف؛ لا يقوم مقام تثبيت القدمين. لا يمكن اعتماد انزلاق القدم أو دقة الاصطدام بصريًا من اختبارات المنطق فقط.

ترجمة enum الحالة إلى الرسم: Free تعني سماح التحكم؛ Action حركة قتال نشطة؛ Hit إصابة؛ Recovery حركة أُلغيت مع بقاء التعافي؛ Dead وفاة؛ Unavailable إعداد غير جاهز. الحركة الحرة/البدء/التوقف/الالتفاف تأتي من إشارات الحركة المنفصلة. النسخ الشبكي للطور وأوضاع القتال لا يتضمن تنبؤًا محليًا جديدًا.

## البناء والاختبار

الأوامر التالية أمثلة؛ استبدل مساري المشروع والمحرك بما عندك:

~~~powershell
.\Scripts\build_win64.ps1 `
  -Project 'C:\NARIS_TEST\CallOfNaris.uproject' `
  -EngineRoot 'C:\Program Files\Epic Games\UE_5.7' `
  -Map '/Game/Maps/CombatTest' `
  -AssetDir "$PWD\SourceAssets" `
  -ImportSpec "$PWD\Data\import_spec.json"
~~~

فاحص خريطة القتال القائم يفحص الإعداد فقط. ضع الوسم NarisP15Playable على الشخصية الاختبارية وهدفًا منفصلًا بوسم NarisDamageable، ولا تجمع مكوّني صحة. يبقى اختبار الإدخال وتقييم Slot وأداء الشبكة غير مثبت حتى PIE.

محليًا: python Scripts/run_local_tests.py
ثم نفّذ مصفوفة Docs/CONTROL_ACCEPTANCE_AR.md داخل المحرك قبل الاعتماد. نتائج دمج المستودع موجودة في Reports/repository_checks.json؛ تبقى اختبارات Unreal منفصلة. ملفات الأصول الأصلية والمصححة ضمن حزمة التسليم المنفصلة، ولا تُنسخ إلى المستودع ضمن هذا التعديل.

مرجع الكاميرا الرسمي: https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SpringArmComponent?application_version=5.7
