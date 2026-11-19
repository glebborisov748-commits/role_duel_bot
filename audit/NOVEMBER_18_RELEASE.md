# Release progress — 18 November 2026

## Implemented and checked

- Chief admin: Telegram ID 7287815074. Other listed admins retain support, statistics and model diagnostics. Grants, resets, maintenance, broadcasts and level changes require the chief, including callback confirmation and the shared grant helper.
- Only the chief bypasses daily work rotation. API authorization and client state agree. Everyone else gets three daily jobs plus the always-open farm. Tomorrow's work schedule is visible.
- Subscription photo quota comes from the same grant path for paid, command and wheel subscriptions. Seven- and thirty-day grants use their respective quota. Other durations use a proportional quota. Old active command grants without a surviving photo allocation receive a bounded one-time remaining-term repair; paid accounts and outstanding reservations are excluded.
- In Mini App mode, ordinary Telegram bot text is a notes space. Edited Telegram notes never invoke AI. Explicit commands and support retain their handlers.
- `/tehwork on <reason>` persists the reason and shows a plain-text maintenance warning in the bot and Mini App. `/tehwork off` clears it. Maintenance still has the memory mini-game.
- Wardrobe cabinet doors open and close; the state survives redraws within the tab. Thirty-six pre-generated complete outfit previews replace pasted product layers. Selecting/equipping does not invoke an image provider. The stand shows the principal outfit; accessories are reflected in explicitly requested character photos.
- Gender suitability enforced for catalog display, purchases, wearing and legacy active-outfit normalization. Previously purchased inventory is preserved.
- Energizer requires shaking/swiping and pulling the ring. Ring movement has resistance; opening adds a metallic click, synthesized hiss and foam. Permission choice is stored locally; iOS retains final authority over sensor permissions. Short instructions appear after inactivity. Ordinary taps on the ring do not consume an item.
- Shield lasts twelve seconds, blinks in the last three and disappears on expiry or impact. The outgoing text floats a short distance straight upwards and fades.
- Wheel has twelve distinct prize types, a measured circular centered rim, and no percentages in its prize list. Reward choice remains server-side. Photo expected cost is approximately $0.00356 per spin at $0.04 per photo, excluding other rewards and hosting/text costs.

## Verification

140 unit tests. Signed real-handler tests for billing, rotation, mining payouts and wardrobe restrictions. Browser tests at 320, 390 and 430 px for the cabinet, energizer gestures/one-time consumption, mining, slot conflicts and wheel geometry. No live payments, user broadcasts or Problembo generations were used for these checks. Outfit preview artwork was generated once during development.

## Follow-up shipped on 19 November 2026

- Prorated PRO → SUPER PRO → ELITE upgrades preserve the existing expiry and period. Active subscribers see upgrades instead of new subscription purchase cards. Stale Stars upgrades are refunded with a persisted retry queue.
- Photo packs are 3/8/20 with decreasing unit cost. The two-photo bucks exchange uses its own 72-hour cooldown. New product images are compact square anime/realistic character prints, without numeric badges, ribbons or landscapes.
- A large Premium Store entry opens from the profile. Standalone scenes, wake and defibrillator offers are removed from that sheet; existing contextual sleep/death flows remain.
- Avatar editing opens with a pencil overlay. New portrait generations cost 5 Stars and grant a separate portrait entitlement, not common chat-photo credits.
- Channel verification lives within daily quests and gates other quest rewards. Work/chat remain accessible.
- PRO can disable wheel reminders; only ELITE can disable companion initiative and hunger/thirst. The retired global notification toggle and sound-off controls are removed.
- SUPER PRO adds Accommodating; ELITE adds Enigmatic and the non-graphic, text-only Temptation personality. Custom character prose requires ELITE.
- The energizer uses an opened-state image of the same can. Pulling must sustain tension for at least 2.2 seconds before opening. Motion permission is remembered; no item is consumed by ordinary taps.
- Mining has server-owned, fogged random mazes, movement, discovered ore, mining and extraction. Side-view excavation requires digging top soil first. Rain can double the watering bonus, locked at planting; tomorrow's demand is shown.
- Wires support pointer dragging to matching shapes. The harder plug mode adds removable obstructing cables and a traced connection.
- Free trait/species setup and the chief-admin rules from the preceding release remain in place.

### Validation and limits

156 unit tests; signed-handler checks for billing, upgrades, entitlements, tier settings and quest gates; mobile flows at 320/390/430 px, including ring resistance, wire dragging, map/strata rendering, avatar menu and purchase visibility. No real payments or Problembo requests were sent by these tests. Physical motion permission still depends on the device/browser.

The 32 newer adult-shop items remain catalog-only as previously requested; their art is product imagery, not chat references or fully combined character outfits. The cabinet uses prepared principal-outfit previews; arbitrary accessory combinations are not pre-rendered exhaustively.
