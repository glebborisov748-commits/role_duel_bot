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

## Remaining from the broader request

- Term-preserving priced upgrades through ELITE; active subscription purchase presentation; new photo packs 3/8/20, dedicated 5-Star portrait generation and profile pencil menu.
- Larger paid-section entry and contextual wake/defibrillator purchase placement; two-photo bucks exchange.
- Enforce channel quest as the prerequisite within daily quests.
- Notification controls by tier and ELITE hunger/water setting; subscription copy and additional requested styles.
- Free trait selectors in onboarding rather than presets, ELITE custom prose character decision.
- Side-view archaeology, dark maze mining, new wire modes and further farm events.

These remaining items are not claimed as shipped by this release.
