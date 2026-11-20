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


## November 20: scene context and fitting follow-up

- Recent scene metadata now includes ordinary posture, expression and framing, rather than background alone. A gentle adult kiss uses a one-face viewer perspective. Raw dialogue and arbitrary model-written image prompts never become provider instructions. Camera/tripod, portrait inset, collage, lettering and watermark negatives were added; portrait defaults use a neutral backdrop.
- Latex descriptions explicitly specify opaque, skin-tight glossy rubber, fitted limbs and reflective highlights. The 32 newer adult-shop products now have separate non-explicit clothing facts, gated at level 5; raw catalog tags and preferences remain separate from image prompts. No explicit photo-generation feature was added.
- Six curated characters (Ada Wong, 2B, Diane Foxington, Chica, Nico Robin, Spike Spiegel) can be selected during creation. Canonical identities stay separate from profile avatars. Curated heroes use ordinary chat/adventures; Chica also blocks adult clothing and romance-photo poses.
- Four free cosmetic avatar choices and free upload at creation/profile. No automatic paid generation or avatar-to-identity reference. Named roleplay actions use third person; direct speech stays natural. Four stable opening suggestions respect the companion's grammatical gender and disappear after the first user message.
- 16 ordinary clothes and 16 accessories added. Generated art exported once into local WebP assets. The cabinet clips all content when closed and uses a common fitting frame. Footwear already supplied by a complete outfit occupies the shoe slot without deleting old purchases.
- 48 additional whole mannequin illustrations generated, with 47 usable complete combinations registered (one suit/scarf view omitted because the tie occupies the neck slot). Ready combinations show clothes and accessories drawn together, can be previewed freely and equipped atomically from owned inventory. Arbitrary combinations use registered garment/detail layers; these are approximate illustrations, not an exhaustive render of every possible combination or non-human anatomy. Character photos use every equipped clothing fact and selected species.
- Sending keeps the button and border still, with a short upward tier-colored bubble dissolving into small mist particles. The energizer requires seven deliberate shake impulses with flying droplets; the existing 2.2-second resistant ring pull remains.
- /tehwork_all is an alias for chief-only /tehwork; maintenance continues to block all other users, including regular administrators.

Validation: 166 unit regressions; signed creation, avatar, photo-context, catalog and preset-equip APIs with providers mocked; JavaScript syntax checks; mobile 320/390/430px checks covering cabinet clipping, complete-look switching, avatar/template onboarding, four suggestions, subscription colors, purchase/upgrade flows and the energy ritual. No live Problembo generation or real Stars payments were used for validation. Upstream provider output remains probabilistic; composition/material constraints cannot guarantee every returned image.


## November 20: mobile repairs and playable excavation

This follow-up supersedes the preceding avatar picker, custom-character tier, material previews and ring-hold details.

- Fixed actual app-route styles: horizontal red discount strikes (including energy packs), left reactions outside text, smooth full-width photo shimmer, and a short tier-colored outgoing effect anchored to the live input while the keyboard changes size. Clothing purchases stay silent.
- Re-exported product crops without neighbouring atlas rows. All complete body outfits, including bikinis and other adult-shop clothing, have coherent whole-mannequin views. Shared registration, calibrated accessory anchors, clipped cabinet doors and whole-look matching replace detached product torsos. Prepared combinations are finite; arbitrary combinations still use registered accessory/separate-garment layers. The fox dress has a plain front and its tail behind.
- Latex uses the glossy fitted material; Wet Look now means rain-soaked cotton with opaque coverage. Existing owners of the former Wet Look keep their glossy outfit through a one-time latex migration.
- Removed free preset avatars from creation: own upload or explicitly requested generation. General photo attempts can fund wardrobe/avatar generation; dedicated 5-Star portrait credits remain separate from chat photos. Failed jobs refund their reserved attempt, including concurrent subscription-grant cases.
- SUPER PRO and ELITE can describe a custom character. Fourteen curated adult references and a bounded optional identity resolver connect recognized fiction to dialogue and validated appearance. Uncertain-age references stay family-friendly; no explicit photo mode is introduced. Species labels distinguish human cat ears from an anthropomorphic feline.
- Strengthened single-scene image composition and material constraints; profile-avatar framing no longer inherits a kissing close-up. Provider output remains probabilistic.
- Smaller, lower energizer with generated hand gestures and a resistant 0.85-second ring pull after shaking; existing sound, foam and opened-can art retained.
- Mining now uses textured top-down terrain, ores, movement and a separately aimed narrow flashlight with wall occlusion. New worlds are 15×15; older worlds remain supported. Archaeology is a manual side-view digging game with a character, descending soil layers, tunnels, finds and upgrades; new digs are 9×12. Rewards and movement remain server-owned.
- Updated the guide and hosted agreement/privacy explanations.

Validation: 181 unit tests; signed creation, species, clothing, billing, upgrades and refund checks; actual app/shop/work routes and APIs at 320/390/430 px, including keyboard movement, standalone wardrobe generation, silent purchases, bikini fitting, ring resistance, mine aiming and side-view excavation. Image and Telegram providers were mocked; no real Stars payments or live Problembo calls were made.
