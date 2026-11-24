# Mini App UI and support — 24 November 2026

- Character creation no longer offers accessories. New custom characters default to none; existing characters and wardrobe accessories are preserved. Canonical character references retain their authored appearance.
- Sixteen generated whole mannequin images replace or extend everyday outfit previews. Equipped combinations still require ownership of all items and respect occupied slots. Other arbitrary combinations continue to use registered layers.
- Energy-pack savings wrap below the price and remain legible at mobile widths. No pack prices or resource rewards changed.
- The shared 48-hour bucks offer appears above shop categories with a generated calendar icon and a live HH:MM:SS countdown. Its reset remains at midnight Moscow time; opening the shop and buying do not restart it. The client refreshes at expiry and on returning to the page.
- Support tickets persist in the existing data store before Telegram notifications are attempted. One active ticket per user, bounded message history, FIFO within subscription priority; tickets older than a day receive the same priority to prevent starvation. Users see their position/status in the profile and after submission. No response-time guarantee is advertised.
- `/support_queue` lists the next tickets and provides a reply target for the next available one. An administrator's first reply claims a ticket in queue order. Concurrent replies are guarded; successfully delivered replies close tickets, failed delivery leaves them open for retry. Existing support reply mappings remain compatible.
- Maintenance shows its heading once. Memory-game copy says “Твой ход”, distinguishing it from support queue position.
- Outgoing message decoration rises 34px over 2.4 seconds and is removed after 2.65 seconds. The composer remains the width reference on desktop.
- While waiting for a reply: one quiet second, white eye for 0.6 seconds, then faster typing dots. New replies enter with a short fade/scale animation, once per message ID. An already-ready response is shown immediately; no provider/model change and no additional server delay.

Validation uses isolated local storage and mocked Telegram/AI/image providers. No paid model/image request or payment was used for runtime tests. Generated art was created separately with the image generation tool.

Checked: 223 offline unit regressions; `tests/check_nov24_browser.py` at 320/390/430px; desktop width/final-opacity and embedded-online regressions in `tests/check_nov23_layout.py`. Browser tests also check that changing shop tabs cannot restart the timer. Live hosting rollout is not verified from this workspace.
