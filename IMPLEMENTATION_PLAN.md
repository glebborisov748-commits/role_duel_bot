# Approved release plan — 2026-11-18

The user authorized implementation and pushes in stages. Preserve existing purchases and progress.

## Stage 1 — purchases, photo entitlements and chat
- [x] PRO 120/350 RUB (300 RUB launch promotion until December 2); SUPER PRO 270/800; ELITE 650/2000.
- [x] Included weekly/monthly photos 10/45, 20/90, 45/200. Purchased credits never expire; subscription grants expire independently.
- [x] Existing subscribers prorated on migration; old paid avatar attempts preserved; one free trial per account.
- [x] Packages 1/5/15 for 10/45/120 Stars; scene 15 Stars, scene + photo 25 Stars.
- [x] Shared first subscription bonus: 1000 bucks + 2 scenes, no energizers.
- [x] Separate purchases screen from Profile, also reached from camera when empty.
- [x] Independent 72-hour cooldowns for all three bucks exchange items.
- [x] Channel quest: server membership check, once-only 500 bucks + 1 photo + 1 scene.
- [x] Photo loading placeholder, reveal animation, full-screen photo viewer; compact reactions and visible premium notice.
- [x] Shorter message flight, independent send-button balloon, slower neon.
- [x] Starter suggestions only; context/personality/intimacy followups with quiet hours and opt out.
- [x] Admin broadcast with preview and confirmation; setlevel command.
- [x] Interactive energizer opening; recorded single water drop.

## Stage 2 — wardrobe
- [x] Generated wardrobe and photo product art atlases; source images preserved.
- [x] Catalog art, no-cost fitting display, explicit 1-credit character preview.
- [x] New catalog item equipping with ownership/level validation and compatible clothing facts.

## Stage 3 — work and games
- [x] Standalone archaeology expeditions: server-owned random loot, risk/cash-out, upgrades/tools.
- [x] Courier inertia, varied hazards, delivery at rest, gestures only.
- [x] Connect cables and separate timed cut-one-cable challenge.
- [x] Daily crop demand and coherent farm scale.
- [x] Wheel rewards, transparent probabilities, photo attempts, animation/sound polish.
- [x] Unified game chrome, more strip-game clothing, online selectable player skin.

Paid provider jobs, real Telegram payments and production notifications are not exercised in local tests.

## Implementation notes
- Promotional PRO price is 300 RUB / 250 Stars until 2026-12-02 (configurable PRO_PHOTO_PROMO_UNTIL); regular 350 RUB / 292 Stars. Other monthly Stars: 667 / 1667; weekly: 100 / 225 / 542. External USD metadata follows the existing 70 Stars/USD catalog convention; payout economics still require actual merchant data.
- Fitting uses generated product layers on a tailor stand. It is explicitly approximate; only the confirmed one-credit button submits a character image request. Clothing purchases, selections and skin choices submit no provider jobs.
- Archaeology is separate from hacking. It has server-owned hidden finds, tools, durable upgrades, run upgrades, cashout and a 60-second rest. Eight-layer expedition cap bounds loot growth.
- Lockpick no longer appears in newly selected hacking rounds; old code remains for client compatibility. Connection and timed cutting are separate tasks.
- Daily crop +50% value is locked at planting, so midnight cannot remove the advertised bonus.
- For the tested SUPER PRO luck state, the wheel awards 0.0783 photo attempts/spin in expectation: about $0.00313/spin at $0.04/photo. This excludes other rewards, text costs, fees and hosting. Exact current chances are displayed.
- Player skins are ready-made portraits shared through the authenticated room state; the opponent never receives private hidden moves.
- Broadcast: /broadcast → send content → preview → explicit Send. /cancel_broadcast cancels a draft. /setlevel ID_or_@username 1–10 adjusts intimacy XP. Existing /grant ID_or_@username energizers AMOUNT remains available.
- Water-drop recordings: CC0 Water drops by CeoxBlackj; provenance in assets/audio/SOURCES.md. Audio cache version updated.
- Release verification: 119 unit tests, real signed API integrations with fake accounts and providers, JavaScript syntax checks, mobile 320/390/430 smoke checks. Production hosting restart, real invoices, paid provider jobs, motion permissions on physical iOS devices and a live broadcast were not exercised.

## Follow-up — mining and daily rotation (implemented)
- Standalone mine with ore veins, gas, ventilation, pickaxe upgrades and persistent cargo.
- Three active works daily, common schedule, 00:00 Moscow reset; farm is always open.
- Same-day quest migration, server-side income gates and recovery of old cargo.
- Multi-slot outfits with visible locks and server validation; all inventory retained.
- New tests: tests/test_mine_rotation.py, tests/check_mine_rotation_runtime.py, tests/check_mine_rotation_ui.py.
