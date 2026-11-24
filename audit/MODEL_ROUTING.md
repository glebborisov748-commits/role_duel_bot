# Model routing — November 24, 2026

Normal chat starts on the exact `deepseek-v3.2` ID used in the supplied comparison.
A one-time saved migration overrides an old normal-chat environment setting.
Existing explicitly configured scene models are preserved; without one, scenes
inherit normal chat until a separate model is selected. No new premium scene
model, new prompt, content-filter bypass or paid comparison was activated.

Chief-only controls, in the chief's private bot chat:

- `/ai_models` — current settings, separate chat/scene picker and inheritance button.
- `/ai_model chat ID` — set normal chat from the live provider catalog.
- `/ai_model hot ID` — set the scene route independently.
- `/ai_model hot same` — follow the normal-chat route.

Catalog lookup accepts exact IDs/canonical slugs only, rejects unavailable or
ambiguous entries and does not submit completions. Paginated picker callbacks
contain short session tokens rather than potentially overlong provider IDs.
Expired/stale menus and non-chief/group callbacks cannot change the settings.
Choices persist in the existing data store; a failed save restores the previous
in-memory selection. Already-running requests retain their original model for
language-repair and timeout retries. There is no automatic upgrade/fallback to a
different model when a pinned ID fails.

Validation: offline regression suite plus `tests/check_model_routing_runtime.py`
for real dispatch, legacy-environment migration, independent routes, JSON
persistence, picker pagination, authorization/stale-menu guards, selection without
paid requests, missing-model failure, and model changes during repair retries.
Live Provod completions and production hosting are not exercised from this workspace.

Results: 235 offline unit regressions passed. Both the model-routing runtime
check and the existing benchmark-command runtime check passed with mocked
providers, including 24 fake benchmark completions and no live paid calls.
