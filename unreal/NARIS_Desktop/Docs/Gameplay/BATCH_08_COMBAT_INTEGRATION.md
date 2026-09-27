# NARIS — Batch 08: Combat + Hitbox + VFX Integration

## الهدف
تحويل Batch 07 من هيكل Animation إلى خط قتال event-driven صالح للتوسعة في Unreal Engine 5.x، مع إزالة الاعتماد على Actor Tags كناقل أحداث.

## المعمارية
Animation Notify -> GameplayEventComponent -> Combat/Hitbox/VFX/Audio listeners.

- `UNarisGameplayEventComponent`: Event Bus محلي للشخصية/العدو.
- `UNarisCombatComponent`: يحل Attack Row من DataTable بدل القيم الصلبة.
- `UNarisHitboxComponent`: يفتح/يغلق نافذة الضربة ويمنع تكرار إصابة نفس Actor داخل النافذة.
- `UNarisBossPhaseComponent`: انتقال أحادي الاتجاه للمراحل وإشارة Blueprint للـAI/VFX/Cinematics.

## ربط ABP_MasterCharacter
1. Anim Notify: EnableHitbox + AttackID.
2. ResolveAttack(AttackID).
3. BeginHitWindow(Socket, Radius).
4. أثناء النافذة: Sphere/Shape sweep من socket السابق إلى الحالي؛ ignore owner؛ dedupe HitActors.
5. Apply Point/Gameplay Damage + Poise + impulse.
6. Emit PlayVFX / PlaySFX بالمعرّفات من صف الهجوم.
7. DisableHitbox -> EndHitWindow.

## Bone Beast
- P1: Base attack set.
- عند <=65%: Phase 2، roar/transition montage، Bone Fury VFX، AI profile P2.
- عند <=30%: Phase 3، Aether Bone Storm، final attack set.
- Charge يستخدم Root Motion؛ hitbox على `head_core`.

## Physics Assets
- Ashen Vessel: pelvis/spine/head/upper-lower limbs، constraints محافظة، physical animation للـhit-react فقط.
- Bone Beast: bodies للرأس/الصدر/الحوض/الأطراف + tail chain؛ لا تجعل الذيل كله simulation أثناء locomotion.
- Root Wraith: simplified bodies؛ collision query للأطراف القتالية منفصل عن ragdoll bodies.

## قواعد الإنتاج
- لا Direct Cast بين ABP والـBoss/World actors.
- DataTable = tuning/configuration، Components/Interfaces = behavior.
- VFX/SFX references تمر عبر IDs/registry لتسهيل الاستبدال والـcooking.
- Server authority للضرر في multiplayer؛ cosmetics يمكن multicast/predicted لاحقًا.

## الخطوة التالية
Batch 09: AI Combat Director + Behavior Trees/StateTree + EQS + Boss phase orchestration + encounter budgets.
