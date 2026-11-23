# Opt-in roleplay model comparison

No model has been selected or switched by adding this tool. Real candidate generations require the Provod key that is configured on the running bot host. The development workspace has no such key; only the public catalog and mocked request/report flows were exercised here.

## Run from Telegram

Only chief admin 7287815074 can run this, in a private chat with the bot.

- `/model_test`: eight candidates, three common synthetic scenarios, 24 requests if all are available and budget permits.
- `/model_test full`: also tests a shy male character, disagreement and respecting a request to stop touching, up to 48 requests.
- `/model_test status`: progress without launching another run.
- `/model_test cancel`: stop after the current request and retain the partial report. A dispatched request may already have been billed.
- `/model_test result`: resend the last report without paid generation, including after a restart.

Default candidate set: Cydonia 24B V4.1, Venice Uncensored, Qwen3 30B A3B Instruct 2507, Aion 3.5 Mini, DeepSeek V3.2, GLM 4.5 Air, Llama 3.1 Euryale 70B v2.2 and Skyfall 36B V2. All eight exact IDs were found in the live public `/v1/models` catalog on November 23.

The command builds each system prompt once from the bot's existing prompt builder and a detached fictional profile. Every candidate receives the identical request/history for that scenario. No player's conversation, account balance, photo attempt, production-model setting or notification preference is read into the benchmark or changed. The test does not generate images or run explicit scenarios, and does not establish absence of content restrictions.

## Cost and execution limits

- Ruble rates are the user's November 23 catalog snapshot; they are not derived from dollar metadata or invented exchange rates.
- The default three-case run has a conservative planning estimate around 10.6 RUB with current bot prompts and the full output allowance. Real usage may be less. Standalone prompts are shorter and produce a different planning estimate.
- The dispatcher uses a 15-RUB estimated spending limit, 1,200 maximum output tokens per request and a ten-minute dispatch window. Input tokens are estimated before sending and reconciled against returned usage. This is not an account-side bank limit or guaranteed actual charge; provider prices/tokenization/additional billing may differ.
- Reservation is saved before dispatch. Missing usage, errors and timeouts retain a conservative estimated charge, because a timeout does not establish that the request was free. No automatic retry or production fallback occurs. Authentication/balance failures stop the whole run.
- Requests are sequential, with a budget check before each one. Duplicate command starts are prevented before the first await. Cancellation retains completed answers and in-flight reservations. Limits or missing candidates are explicit in the report.
- Public model discovery is free; successful discovery does not prove that generation is available on this account.

## Choose using the report

Open `comparison.html` in a browser. Names are hidden behind stable randomized letters. Read each response and score naturalness, character and context from 1 to 5. A ranking requires all three criteria for all scenarios and at least two completely scored candidates; incomplete answer sets are not ranked. Scores stay locally in the browser. Reveal model names after rating, and download `my-model-ratings.json` if desired.

`results.json` contains raw synthetic prompts, responses, exact requested/reported IDs, token usage, full-response latency, estimated cost, truncation/empty/error flags and literal checks for a few memory details. It contains no API key. It is not a blind file: opening it reveals model identities.

Literal checks are observations, not a quality judge. Full-response latency is not time to first token. One response per scenario is a screening pass, not statistically reliable proof of a universal best model. Before switching production, review the preferred two candidates on more turns and repeated samples. Empty/truncated output may come from reasoning/output limits or gateway issues and must not automatically be labeled censorship or poor prose.

## CLI

Use the existing hosting environment or an ignored `.env` file. Do not put secrets in shell arguments or chat.

```sh
python scripts/compare_models.py --plan
python scripts/compare_models.py --plan --bot-prompts
python scripts/compare_models.py --run --bot-prompts
```

`--plan` only reads the public catalog. `--run` sends billed requests. `--bot-prompts` imports the configured application but does not start bot polling; it needs the bot's environment. Without it, the standalone prompt is used and results are not equivalent to the production-template comparison. `--full`, `--budget` and `--output` customize a deliberate CLI run. Outputs live under `DATA_DIR/model-tests/<run>` for the command; CLI defaults to a unique local output directory.

No report text is executed as HTML. Model output is escaped and reports are self-contained without external scripts, analytics or network calls.

## Validation

214 unit regressions including exact-ID resolution, equal prompts, token-cost calculation, estimate limits, no retries, authentication abort, cancellation, pre-dispatch persistence, no secret leakage, HTML escaping and chief-only access. Offline Chromium checks cover blind names, equal-coverage ranking, local score persistence, script injection and score export. The comparison UI uses explicitly marked mock answers in these tests. No paid Provod completions were sent from this workspace.
