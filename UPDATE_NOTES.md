# RoleDuel — обновление Mini App, 13 ноября 2026

Основа: commit `9d16a4c` репозитория `glebborisov748-commits/role_duel_bot`.
Изменения подготовлены для публикации в GitHub. Развёртывание на bothost.ru проверяется отдельно.

## Изменения

- Меню по долгому нажатию / правой кнопке / Enter на сообщении. Свои текстовые сообщения можно редактировать и удалять. Старые ответы персонажа при этом сохраняются; начисленные ранее XP и затраты энергии не пересчитываются. Во время генерации изменение истории блокируется.
- Реакции на ответы персонажа; повторный выбор снимает реакцию. Реакции самого персонажа показываются реже. Изменения сообщений подтягиваются при опросе даже при прежнем числе сообщений.
- Справка открывается внутри Mini App. Обучение из пяти шагов с подсветкой элементов, пропуском и повторным запуском из справки. Переключение RU/EN в настройках и при создании персонажа. Существующая немецкая локализация бота сохранена, полной немецкой локализации Mini App в исходнике нет.
- Пятый шаг создания: переписка без описаний действий / ролевая история с действиями. Настройку можно изменить в профиле. Исправлен принудительный выбор phone на сервере.
- В профиле показаны преимущества текущего тарифа, доверие и уважение. Прогресс отношений — за содержательное общение, максимум пять прибавлений в день, с паузой десять минут; покупки его не увеличивают. Новые отношения начинаются с нового персонажа. Это начальная игровая модель, не долговременная семантическая память.
- Рефералы: пригласившему 2 000 баксов, 1 энергетик, 2 сцены; новому другу 1 500 баксов. Награда после создания персонажа, один раз. Пригласить себя, указать отсутствующего пригласившего или привязать старого пользователя новым /start нельзя. Это не защита от нескольких настоящих Telegram-аккаунтов одного человека.
- Пакеты баксов за Stars: 5 000 / 10; 15 000 / 18; 50 000 / 35. Только Stars, фиксированная цена без купонов. Доставка Stars защищена от повторной обработки того же payment charge ID.
- Быстрый заказ подписчика: три положительных начисления на работе за день → 500 / 1 000 / 1 500 баксов для PRO / SUPER PRO / ELITE. Получение один раз в день по московской дате.
- Суммарный базовый вес энергетиков в колесе снижен с 2,5 до 0,85, остальные веса сохранены. Цвета секторов приглушены. Вероятности задаёт сервер; площадь секторов не обозначает вероятность.
- Постоянная выгода упаковки энергетиков вычисляется по обычным ценам. Акция отдельно показывает старую зачёркнутую цену и новую.
- Чёрные кнопки с фиолетово-розовой границей; общая картинка валюты в интерфейсных подписях вместо 💵. Содержание переписки и полей ввода не заменяется.
- В работу подключены существующие картинки курьера, препятствий, персонажей и падающих предметов. Вид фермы сохранён. Добавлены эффекты взрыва, столкновения, капли и сбора урожая. Покупка еды/напитков сопровождается эффектом и синтезированным звуком; звук отключается существующей настройкой.
- Новые изображения `assets/gift_paris.png` и `assets/gift_car.png`: генерация встроенным imagegen, прозрачный фон, матовый 3D, приглушённые сиреневые/розовые оттенки. Промпты: миниатюрный подарочный диорамный Париж с Эйфелевой башней и бантом; подарочный сиреневый спортивный автомобиль с розовым бантом, без текста и логотипов. Изображения заменяют прежние по тем же путям.
- В видимом меню Telegram оставлены /start, /help, /support; прежние команды продолжают работать.

## Что остаётся

- Голосовые сообщения, звонки и выбор голоса: нужны название сервиса, документация API, доступные голоса, формат аудио и сведения о поддержке потокового режима. Ключ следует хранить в переменных окружения хостинга. Не добавлены фиктивные неработающие кнопки.
- Полная визуальная приёмка в Telegram на iPhone/Android и реальные тестовые платежи.
- Отдельная семантическая память о событиях отношений; сейчас используется доступная история диалога.
- Реклама и видимость в поиске Telegram — отдельная задача по профилю бота и рекламной ссылке.
- Сексуальные изображения, фетиши, секс-товары и усиление откровенной игры в это обновление не входят.
- Обнаруженные ранее ограничения исходного проекта: JSON-хранилище не предназначено для нескольких одновременно пишущих процессов; очередь внешних платежей удаляет запись перед выдачей и требует отдельной транзакционной переработки. Это обновление не заявляет исправление этих двух проблем.

## Проверки

- `python -m py_compile app.py`
- `python -m unittest discover -s tests -v`: 12 проверок серверной логики.
- `python tests/check_runtime.py` с установленными requirements: реальный импорт приложения, сериализация состояния, однократное начисление пакета баксов при повторном событии Stars. Используются фиктивные ключи и временные данные, сеть не вызывается.
- `python tests/make_ui_fixture.py /tmp/rd-ui.json`, затем `NODE_PATH=<каталог node_modules с jsdom@26> node tests/check_dom.cjs /tmp/rd-ui.json`: DOM-проверки редактирования, удаления, реакций, профиля, преимуществ тарифа, пакетов, справки, обучения, языка, режима общения и пятого шага создания.
- Проверен синтаксис встроенных JS-скриптов через `node --check`.
- Полноценный Chromium не удалось запустить: среда запрещает socket(), необходимый браузеру. DOM-проверки не подтверждают визуальную верстку и звук. `tests/check_ui.py` оставлен для мобильной браузерной проверки в среде с установленными Playwright и Chromium.

## Обновление на bothost.ru

1. Сохранить действующую версию кода и резервную копию `DATA_DIR/data.json` вместе с `.bak`.
2. Проверить на отдельном тестовом боте с отдельным DATA_DIR. Не запускать второй polling-процесс рабочего бота.
3. Заменить код и два изображения; переменные окружения, токен и папку data не удалять.
4. Если хостинг собирает проект из GitHub, сначала отправить изменения в репозиторий, затем выполнить перезапуск/пересборку. Это не выполнено автоматически.
5. Проверить вход старого пользователя, новый реферал, смену языка, создание персонажа, реакции, магазин и тестовую оплату.
6. При ошибке вернуть прежний код и при необходимости резервную копию данных. Учитывать покупки и новые сообщения после момента копирования, не затирать их без сверки.

## Доработка по обратной связи

- После создания персонаж ждёт первого сообщения пользователя; автоматический запрос к модели и блокировка чата на время приветствия убраны. Реферальные награды сохранены.
- Обучение: 12 шагов, переходы к реальным полям профиля, кнопка «Назад», пропуск и повторный запуск из справки.
- Общий стиль кнопок распространяется на навигацию, вкладки, управление играми и модальные окна: чёрный фон, фиолетово-розовая граница, сиреневый текст с мягким свечением.
- В работе снова используются эмодзи. Исправлена общая настройка reduced motion: она отключает декоративные эффекты, но не сокращает игровое движение до 0,01 мс. Раньше объекты исчезали до проверки столкновения/доставки.
- Колесу возвращены яркие цвета; 7–9 оборотов, плавное замедление и усиление свечения во время вращения. Серверные вероятности не менялись.
- Звук смены полосы убран; доставка, столкновение, взрыв, капля и урожай получили короткие отдельные звуки. Вибрация управления и доставки усилена. Фактическую силу вибрации определяют Telegram и устройство; прослушивание на телефоне остаётся частью приёмки.
- Проверки: 12 unit-тестов, реальный импорт/повтор Stars, синтаксис 14 скриптов, мобильный Chromium для чата/профиля и всех 12 шагов обучения. Проверка `check_work_ui.py` проверяет доставку, аварию/штраф и ловлю предмета в обычном режиме и с reduced motion.
- Для проверки работы: `python tests/make_work_fixture.py /tmp/rd-work.json` (с requirements), затем `python tests/check_work_ui.py /tmp/rd-work.json` (с Playwright и Chromium).

## Варианты реплик

- После создания персонажа в пустом чате предлагаются четыре первые реплики на языке интерфейса и кнопка «Написать своё». Персонаж первым не пишет.
- Примерно раз в 5–8 успешных ответов Mini App отдельно запрашивает четыре контекстных варианта продолжения. Подсказки используют последние 16 сообщений доступной истории, не блокируют ответ и не тратят игровую энергию. Это дополнительный запрос к настроенной модели.
- Нажатие переносит текст в обычное поле: пользователь может изменить его и явно отправить. Автоматической отправки нет.
- При редактировании истории, смене языка или новом сообщении устаревшие подсказки скрываются; запоздавший результат не применяется. Ошибка или таймаут дополнительного запроса не мешает разговору.
- Подсказки предназначены для обычного общения; инструкции генерации исключают графические сексуальные описания. Подтверждение возраста и соглашение не изменены.
- Проверены 16 unit-тестов, реальный импорт и мобильный браузер: четыре кнопки, перенос в поле, собственный ввод и отсутствие автоматической отправки.


## Исправления по следующей обратной связи

- Убрана единая чёрная неоновая тема для всех кнопок. Нижняя навигация снова плоская, без рамок. Управление курьером — голубое, ферма — зелёная, колесо — розово-лиловое; взлом — клавиатурные клавиши. Нажатие видно по сдвигу и яркости, у основных кнопок мягкое свечение.
- Немецкий доступен в настройках, создании персонажа, основных экранах, обучении и стартовых вариантах реплик. Существующая немецкая локализация остальных разделов сохранена. Названия готовых портретов пока используют английские подписи.
- Меню сообщений открывается около пузыря с короткой анимацией сбоку. Удержание — 280 мс. Реакции закреплены внутри нижнего края сообщения. При реакции персонажа она сохраняется и показывается до текста ответа.
- Удаление сообщения теперь удаляет всю ветку истории начиная с него, включая последующие ответы и сообщения, чтобы модель больше не получала удалённые факты через цитаты и продолжения. Перед действием есть явное подтверждение. Подсказки сбрасываются; списания и начисления не откатываются.
- Обычные ответы ограничены 1–3 предложениями; убрано требование длинных пар действий и реплик. В грубом стиле явно разрешены сильный мат и грубые подколы по контексту, без угроз, дискриминации и игнорирования просьбы остановиться.
- Новые аккаунты проверены: подписки нет. Создание персонажа не начисляет PRO; действующая подписка аккаунта сохраняется. Причина конкретной подписки на рабочем сервере требует проверки его данных.
- Кольцо и именная звезда заменены новыми матовыми 3D-картинками в стиле подарочной машины. Генерация imagegen: сиреневая коробочка с кольцом и розовой лентой; золотая звезда на сиреневой подставке с пустой именной табличкой. Изменён URL картинок магазина для обхода старого кэша.
- Работа и колесо используют новую библиотеку коротких WAV-эффектов. Для воды, газировки и хрустящей еды предусмотрены разные звуки; громкость подчиняется общей настройке. Это оригинальный процедурный синтез, а не натуральные записи. Генератор аудио в сессии недоступен; запрос открытых записей был отклонён источником (403). Реалистичные записи и оценка на телефоне остаются отдельным этапом.
- Прочитаны оба conversations-архива и memories из экспорта Claude. В них нет подробной истории последних изменений RoleDuel. Личные экспорты в репозиторий не добавлялись.

Проверки этой доработки: 18 unit-тестов; реальный импорт с немецким состоянием и отсутствием подписки у нового аккаунта; 14 встроенных JS-скриптов; мобильный Chromium для чата, меню, немецкого, плоской навигации и игр с новым звуковым движком. Реальные платежи, рабочий профиль пользователя и звучание на телефоне не проверялись.

## Ежедневные задания и интерфейс — 14 ноября 2026

- Два разных задания доступны всем. Выбор сохраняется между перезапусками; вчерашние задания исключаются из следующего выбора при достаточном пуле. После 16:00 МСК новым дневным наборам не выдаются задания фермы. Прогресс учитывается по принятым сервером сообщениям, доставкам, денежным предметам, взломам, посадкам, поливам и сбору урожая. Сообщения должны содержать хотя бы четыре разных слова; повтор текста и частые сообщения не увеличивают прогресс.
- Награды: баксы, 40 энергии, энергетик или сцена. При активной PRO/SUPER PRO/ELITE только баксовая награда квеста умножается на два. Игровые множители сохранены. Энергетик и энергия подпиской не удваиваются. Если полная энергетическая награда не помещается в лимит 150, она ждёт до освобождения места в пределах этого дня.
- Колесо и задания используют календарные сутки Москвы. Открытые экраны получают обновление после 00:00; повторный вход не выдаёт награды заново. Сначала тратятся дневные бесплатные вращения, затем дополнительные; дополнительные вращения не обнуляются. Старая подписочная задача заменена квестами.
- При сне персонажа показаны доступность работы и бесплатных наград, ссылки на работу и задания. Новые раунды блэкджека требуют бодрствующего персонажа и доступных реплик; режим «молча» убран. Уже начатую ставку можно доиграть, чтобы не потерять её из-за изменения состояния во время партии. Онлайн-игры не добавлялись.
- Анимированные реакции 💖 ✨ 🔥 🎉 доступны любой активной подписке; обычные реакции бесплатны. Право проверяет сервер. Снять ранее поставленную подписочную реакцию можно и после окончания подписки.
- Меню сообщений размещается около места касания, преимущественно снизу, учитывает безопасные отступы Telegram и экранную клавиатуру. У карточек подарков, еды и лекарств удержание не открывает меню, включая пустую «Отмену».
- Убраны верхняя тонкая полоска энергии, полоска курьера и подписи «Взлом удался»/«Доставлено». Возвращён движущийся блик кнопок. Шаг про внешность подсвечивает кнопки, а не всю карточку; текст сокращён, подсказка размещается вне выделения. Шаг «Баксы и покупки» исключён из обучения; сам магазин не удалён.
- Бонусные предметы в «Заказе» больше не оплачиваются и не считаются денежными попаданиями для заданий. При бомбе координаты сохраняются до смены анимации; взрыв — короткий разлёт частиц в месте столкновения.
- Работа и колесо используют эффекты Kenney (CC0). Еда — CC0-записи StarNinjas, питьё — CC0-записи OwlishMedia; газировка дополнена тихим синтезированным шипением. Источники и лицензии в assets/audio/SOURCES.md. Аудио предварительно загружается, повторные загрузки объединяются, число одновременно звучащих эффектов ограничено. Старый генератор синтеза удалён, чтобы не перезаписать записи.
- Вибрации разделены по событиям: нажатие, доставка, успех, ошибка, взрыв и получение награды. Реальное ощущение зависит от Telegram и устройства.
- Для обычного чата устранены противоречивые инструкции о действиях. Режим действует и для собственного персонажа; разметка действий удаляется перед показом. Математические выражения со звёздочками сохраняются.
- Админ-команда: `/givebucks ID_или_@username количество`. Только ADMIN_IDS, положительное целое количество. Существующая `/grant ... bucks ...` сохранена; опечатка в типе награды больше не выдаёт случайно подписку.
- При выкладке нужен новый файл daily_quests.py вместе с app.py и аудио. Изменение механики отмычки и онлайн-игры отложены.
- Проверки: 30 unit-тестов; реальный импорт и RU/EN/DE-состояние; мобильные проверки обучения, меню и квестов на 320×640, 390×844, 430×932; доставка, авария, отсутствие выплаты за бонус и координаты взрыва в обоих режимах reduced motion. Реальные платежи и воспроизведение на iPhone/Android остаются частью приёмки.


## 2026-11-15 — quests, character care, weekly plans and anime photos

- Random illness is no longer rolled on daily reset/opening the app. Rolls occur during active conversation, after a 24-hour grace period and ten history entries; the first message after a break over 30 minutes cannot trigger illness. Existing illnesses remain treatable.
- Medicine doses are now 30 minutes apart. Food cooldowns are shortened; large gifts/dates are capped at 20 hours. Custom gifts have no cooldown and may repeat.
- Quest energy goes above the normal 150 baseline (150 + 40 = 190), including energizer use. Completed quests have an explicit status and a reward particle animation. Added harder courier/hack/catch/chat/farm variants and a share quest that counts opening Telegram's share flow; sending is deliberately not verified.
- Editing a user message discards all later history and regenerates the character reply. The editor now explains this. SUPER PRO/ELITE can change personality in the profile without resetting history; callbacks also verify entitlement. Removed the trust/stage card from the profile.
- Farm notifications wait until every occupied plot is mature, then mark all as notified. Work instructions occupy a fixed scrollable area. Daily shop items retain catalog order and use a highlighted border. Food is grouped as drinks/snacks/meals. Repeating subscription sale is disabled; genuine personal coupons and daily item offers remain.
- Added 7-day subscriptions: PRO 75 Stars, SUPER PRO 170 Stars, ELITE 340 Stars; monthly prices remain 220/500/1000, so monthly costs less per day. Uses existing authenticated invoice and payment delivery paths. Weekly offers currently appear in the Mini App and use Stars.
- Replies target 3–6 sentences in texting and at least two detailed actions in roleplay, with a larger generation budget. These are model instructions, not a guarantee of an exact count.
- Added anime photos via Problembo's documented image-gen/tasks contract, model `waifu-studio-2.6`. Set `PROBLEMBO_API_TOKEN` (aliases `PROBLEMBO_API_KEY` and `PROBLEMBO_TOKEN` accepted), optionally `PROBLEMBO_BASE_URL=https://problembo.com/apis/v1/client`. Photos use the selected appearance and recent context, are requested through the 40-energy button or an explicit text request, and are stored as random local image files. The request is evaluated as an adult, clothed, non-explicit image; intimate clothing/posing requires closeness 10. A rejected request costs no energy, provider failure refunds reserved energy, restart refunds interrupted reservations. No paid external generation was executed in the development environment because production credentials are unavailable.
- Video circles, voice notes/STT and voice calls are not enabled by the image model. These require separate providers/models and pricing.
- Verification: unit tests including photo success/refusal/refund, real app import and weekly grant, mobile UI, courier/catch collision checks. Production deployment and a real authenticated Problembo request require the hosting environment.


## 2026-11-15 — online games, blackjack retirement, pin lock and sound banks

- Removed blackjack from the game catalog, chat callbacks, Mini App, and API. Startup and play-state migration refund each unresolved legacy stake exactly once; already settled rounds are not refunded.
- Added Liar's Dice (two players, five dice each, ones not wild, ascending quantity/face bids and challenges), Connect Four (7×6), and chess. Each supports a free easy computer opponent, random online matchmaking, and private friend rooms. RPS supports the same online modes; online 18+ is a virtual wardrobe game, with explicit consent and SUPER PRO/ELITE entitlement required for both participants. No real photos, real undressing, or peer-to-peer chat are involved. Cities, truth-or-dare and movies retain their existing companion modes.
- Stakes: 0, 100, 500, 1000 or 5000 in-game bucks per participant. Computer games are free. Stakes enter escrow in the same atomic JSON save as the room; the winner receives exactly the pot, draws and cancelled/expired queues refund deposits. Game multipliers never mint extra PvP winnings. Only authenticated room members can move. Revisions reject stale and duplicate turns; secret RPS submissions cannot be changed, do not reveal the other player's choice or extend the round deadline.
- `/online` and `/api/online` implement live state polling, automatic reconnect, server-side legal moves, resignations, promotion choices, castling, en passant, checkmate, automatic chess draws and claims for repetition/fifty-move rule. A separate deadline loop settles games even when both clients close the app. Turn limits: chess 5 minutes per move, Dice/Connect Four 90 seconds, RPS 45 seconds per round. Search expires after 2 minutes; private waiting rooms after 10 minutes. Random matching requires a recently polling host, preventing a stale closed search from matching later.
- Friend rooms have an 8-character code and a Telegram `/start match_CODE` link. The second participant previews the game/stake and confirms the stake before joining. New accounts complete the regular age/agreement/character flow; their invitation code remains available in the online lobby.
- Rooms and escrow survive bot restarts in `__settings__.online_rooms` alongside existing account data. The current deployment must use one bot writer/process for this JSON data file. No claim of multi-worker database support is made. Finished rooms expire after 24 hours. Failed saves restore in-memory room/balance changes.
- Replaced the green-zone lock timing game with four/five pin tumblers: find the binding pin, set light tension, lift to the shear point, recover from oversetting by releasing torque. Excessive torque/overlifting damages the pick; three failures break it. Reduced-motion does not alter mechanics. Localized RU/EN/DE controls and instructions.
- Added 22 audio files: three nonrepeating variants each for code keys, electrical wire hiss/crackle, metal pins, dice, chess pieces, and dropped counters, plus pin break, unlock, matchmaking, and reveal. Existing work code and wires now have distinct event mappings. Electrical hiss is synthesized; the other banks use edited/layered CC0 Kenney recordings. Existing food/drink recordings are retained. Sound settings are shared across sections; static cache versions are bumped.
- New dependency: `chess==1.11.2` (python-chess, GPL-3.0-or-later, https://github.com/niklasf/python-chess). Rebuild/install requirements before launching this update. Added `online_games.py`, `online_ui.py`, and reproducible sound build script `scripts/build_game_audio.py`.
- Verification: engine/API tests cover escrow/refunds/restart, wrong-room access, expired turns, consent/entitlements, save failure rollback, hidden choices/dice, legal chess moves and special rules, C4 and Dice wins, and computer matches. Two authenticated Chromium clients completed invite and random matches, payout/reload checks, RPS secrecy, chess moves and dice rendering. Pin lock checked at 320/390/430 px. Existing courier/collision checks passed with normal and reduced motion; embedded JavaScript syntax and all WAV files checked. Production Telegram clients and hosting deployment have not been exercised here.

## 2026-11-15 — scene portraits, compact photo requests, subscription terms and energy capacity

- Mini App scenes can include one **ordinary clothed anime portrait** after each successful new part or continuation. The text appears first; the portrait has a separate pending/ready/error state and attaches below that part. The optional checkbox defaults on when anime generation is configured and 40 energy is available; its 40-energy cost is shown before starting. Disabling it preserves text-only scenes. Old clients without the explicit photo flag are not charged.
- The scene portrait planner extracts only allowlisted neutral environment/lighting enums. The image provider receives a fixed adult clothed portrait prompt using the selected appearance, never the scene text or intimate actions. Explicit images were not enabled. Uses the existing Problembo `waifu-studio-2.6` integration/token configuration.
- Independent photo job IDs prevent stale results attaching to another scene. Double starts do not reserve twice. If text generation fails both the scene entitlement and image reservation are refunded; image failure preserves the text and refunds image energy. Interrupted/stale image reservations recover once. The photo job blocks starting another part until it finishes. Polling includes the last scene/photo state so the image appears without reopening the page.
- Removed the large chat photo button; replaced it with a compact prompt hint. Recognizes “Скинь свою фотку”, “Покажи себя”, “Можешь прислать фото”, “Send me a selfie”, and similar explicit requests. Insufficient energy/configuration produces an explanatory notice instead of letting the character pretend to be physically in front of the user.
- Ordinary photo planning now evaluates the current request plus location, excluding unrelated old dialogue that could cause false refusals. Generic clothed selfies are explicitly permitted at any relationship level. Existing content restrictions remain in effect; real production Problembo refusal causes cannot be confirmed without hosting logs/token access.
- Added a compact “Напоить энергетиком” control in chat, profile, and scene view. **Latest user correction:** energy additions are capped at 150; an energizer is disabled and cannot be consumed at/above 150. Below capacity it restores up to 78, with the actual amount in the confirmation. Completed energy quests wait until the entire reward fits, preserving the unclaimed reward. Photo refunds also respect capacity. This supersedes the overflow behavior described in the earlier update.
- Each subscription tier has one card with weekly activation on the left and monthly activation on the right. Prices and verified payment delivery remain the existing weekly/monthly products. Monthly card payment remains available through the term button's payment-method popup when configured.
- Ordinary chat instructions explicitly allow natural Russian contractions (“ща”, “щас”, “сек”, “ок”, “ага”) without forcing them into every sentence. Texting mode states that the conversation is remote and a request to show oneself means a photo request.
- Checks: 63 unit tests, actual app import and direct energizer endpoint checks, JavaScript syntax, and mobile UI at 320/390/430 px covering subscription grouping, disabled full-energy controls, using an energizer while awake, scene text before portrait, and automatic image appearance. Existing mobile menu/tutorial checks also pass. Provider calls in development tests are mocked; no real authenticated Problembo generation or production deployment was executed here.
