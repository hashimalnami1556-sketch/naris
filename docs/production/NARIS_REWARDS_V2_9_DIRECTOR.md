# NARIS Rewards v2.9 — Reward Director

Reference artifact verified locally on 2026-10-03: 53/53 Python tests passed with ResourceWarning treated as error. ZIP integrity PASS (31 entries).

Reward presentation is separated from economy fulfillment. Legendary=100, Epic=80, Boss=70, Achievement=60, standard=40. Event IDs are idempotent; replay with changed payload is rejected; acknowledgements persist across restart. Unreal should consume presentation events through UMG but must never grant tokens/items from UI payloads.

Suggested W04 widgets: WBP_RewardToast, WBP_LegendaryDrop, WBP_BossReward, WBP_RewardInbox. Arabic RTL copy should use String Tables.

The included Unreal C++ header in the conversation artifact is a contract/reference only and has NOT been compiled in the canonical Unreal project. PUBLIC_DEMO_ALLOWED remains false pending packaged W04 QA.
