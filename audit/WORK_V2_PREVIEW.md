# Small work games and one-bot preview — November 24, 2026

## Delivered

- **Mosaic** replaces the mine in the new work version: a solvable sliding 3×3 puzzle, touch buttons and PC arrow keys, server-validated legal moves/revisions, one 110-base-buck payout per completed board, and a 30-second rest between completed jobs. Reloading does not shuffle an active board.
- **Finds depot** replaces archaeology in the new version: nine sealed crates, seven intact and two damaged, free entry, collect-or-continue decisions, and at most five intact crates per run. A damaged crate clears only that run's pending finds. Base rewards are capped at 180 and use the existing work multiplier. The server owns crate contents, rejects stale/repeated opens, and pays collection once. Visible next-crate odds reflect the remaining crate counts. Ended runs reveal their contents.
- Existing daily rotation slots and quest IDs are retained. Published quest text changes to the new mechanics without erasing earned progress. Issued mosaic jobs can be finished after rotation; depot rewards can be collected after closure. Fresh jobs remain gated by the schedule.
- Existing mine/archaeology state and purchased upgrade ranks are preserved for rollback. Outstanding legacy cargo can still be collected through the new UI; old endpoints reject further mining/digging in v2.
- A generated muted wicker basket, ice snowflake and wide-basket icon. Freeze slows already-falling and newly-spawned items, then restores their normal playback speed. The added wide-basket bonus lasts eight seconds, widens the collection area, keeps bomb hitboxes at their normal width, and awards no money itself. Missed bonus items are not penalized. Existing magnet/double/shield behavior remains.
- Compact work tabs and mobile grids, with the depot collection button kept near the viewport bottom. Removed the mine tab's recursive state-loading loop.

## Preview without a second bot

The chief's Work section defaults to a clearly marked preview with a separate
10,000-buck test balance. Work jobs, earnings, penalties, boosts and farm spending
use the nested `work_preview_profile`; the main wallet, farm and quest progress
are not used for these test actions. Current subscription/work-boost multipliers
are copied for realistic reward checks. Other users cannot select this profile.

Commands in the chief's private bot chat, also listed in `/admin_help`:

- `/test_mode on` — Work uses the isolated test profile.
- `/test_mode off` — Work uses the main profile.
- `/test_mode reset` — discard only the test profile and initialize fresh test work.
- `/work_release on` — publish the new games and order bonuses to ordinary users.
- `/work_release off` — restore the old public work UI and mechanics; retain new/old progress.

Publication is **off by default**. The chief's private preview remains available
while public work retains the current version. All choices persist in the existing
data store. `X-Work-Mode` is a scope fence, not an authorization token: the server
chooses the profile from the authenticated user's saved mode, rejects writes from
a stale scope, and the client clears queued hits on scope changes. Public API
requests cannot enable preview or publication.

This is feature/data isolation for **Work**, with shared application code and
hosting. It is not an independent deployment or an outage fallback. Other areas
of the bot continue using the main profile. This work sandbox generates no invoices
or paid AI/image requests. Future paid farm features need the same explicit sandbox
separation before they are enabled here.

## Validation

- 243 offline unit regressions, including solvability, legal/stale moves, hidden contents, odds, cashout replay protection, crate limits, cooldowns, JSON persistence, profile isolation and release rollback.
- `tests/check_work_v2_runtime.py`: actual signed API handlers with fake accounts, scope/auth checks, puzzle completion, old-game retirement, legacy cargo withdrawals, sandbox catch/farm operations, chief-only release, rotation and persistence.
- `tests/check_work_v2_browser.py`: mobile 320/390/430px layouts, solving/reloading, depot collection, main-wallet isolation, basket art, wide/freeze pickup and expiry, separate chief/public views, and switching an already-open work tab between released and rolled-back mechanics.
- No real payments or live model-provider calls. Separate image-tool generation produced the three icons. Production hosting rollout is not verified from this workspace.

Courier overhaul, new crops/fertilizer, wardrobe generation curtains and photo-based
character creation remain separate later stages.
