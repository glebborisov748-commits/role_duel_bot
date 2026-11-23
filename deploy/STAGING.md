# Separate test bot

Production continues running its current release while a separate deployment runs the candidate commit. A branch or a maintenance toggle alone does not create this isolation.

1. Create another bot with BotFather. Keep its token in the hosting secret store, never in git or chat.
2. Deploy the candidate branch to a second service/domain. Use a separate persistent volume named `data-staging`; never mount the production data volume or import real user data.
3. Set the variables shown in `staging.env.example`. `STAGING_BOT_TOKEN` and `STAGING_WEBAPP_URL` are mandatory and must differ from production credentials. The same provider account may be used deliberately; AI/image requests still cost money. Telegram invoice creation is blocked.
4. Start with `RD_ENV_FILE=/path/to/.env.staging python app.py`, or supply variables directly in the second service. Chief admin has access; add other testers via `STAGING_TESTER_IDS`.
5. Grant test resources with chief-admin commands. Check two-player rooms with two allowed test accounts. Check the maintenance mini-game using `/tehwork preview on`; `/tehwork preview off` exits without affecting anyone else.
6. After validation, promote that exact commit to production. Preserve and back up production storage. Keep the test service separate after promotion.

For the current repository, pushing `main` may trigger the existing production host. To test a future candidate first, deploy its feature branch to the staging service and promote only after checking it there.

A hosting outage cannot serve a maintenance page from the failed host. An independent status page requires another service/domain. No hosting deployment or second Telegram bot has been created by adding this configuration.
