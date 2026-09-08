import asyncio
import hashlib
import hmac
import os
import json
import logging
import random
import re
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice,
    ReplyKeyboardMarkup, KeyboardButton
)
import httpx
from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
#  МНОГОЯЗЫЧНЫЙ СЛОВАРЬ (только RU + EN, см. пункт 7 задачи)
# ============================================================
TEXTS = {
    "ru": {
        "main_menu": "📋 Главное меню",
        "my_profile": "👤 Мой профиль",
        "spin_wheel": "🎰 Колесо фортуны",
        "our_channel": "🔵 Наш канал",
        "edit": "✏️ Редактировать",
        "change_character": "🔵 Сменить персонажа",
        "invite_friend": "👥 Пригласить друга",
        "create_character": "🎭 Создать своего персонажа",
        "buy_packs": "📦 Купить пакеты",
        "subscribe": "👑 Оформить подписку",
        "back": "🔴 Главное меню",
        "back_to_profile": "🔴 Назад",
        "accept": "✅ Мне есть 18 лет",
        "decline": "❌ Мне нет 18 лет",
        "agree": "🟢 Принимаю",
        "disagree": "🔴 Не принимаю",
        "open_agreement": "📜 Открыть соглашение",
        "realism": "🌍 Реализм",
        "anime": "🎌 Аниме",
        "i_male": "👨 Я парень",
        "i_female": "👩 Я девушка",
        "scene_phone": "📱 Переписка в телефоне",
        "scene_live": "👫 Реальная встреча",
        "channel": "🔵 Перейти в канал",
        "free": "🎁 Бесплатно (1/день)",
        "tomorrow": "⏳ Завтра",
        "spin_paid": "💎 Крутить за 20⭐",
        "spin_more": "💎 Крутить ещё за 20⭐",
        "welcome": "👋 Добро пожаловать!",
        "age_confirm": "🔞 **ВНИМАНИЕ!**\nЭтот бот предназначен для лиц старше 18 лет.\nПодтверди свой возраст:",
        "age_ok": "✅ Возраст подтверждён.",
        "age_no": "🚫 Доступ запрещён. Бот только для 18+.",
        "agreement_intro": "📜 Прежде чем продолжить, ознакомься с пользовательским соглашением и прими его:",
        "agreement_ok": "✅ Соглашение принято!",
        "agreement_no": "❌ Без принятия соглашения бот не работает.",
        "choose_lang": "🌍 Выбери язык / Choose language:",
        "choose_gender": "👤 Выбери свой пол:",
        "choose_world": "🌍 Выбери мир:",
        "choose_world_updated": "🌍 Мир обновлён! Теперь выбери свой пол:",
        "choose_world_first": "🌍 Мир выбран! Теперь выбери свой пол:",
        "choose_style": "🎨 Теперь выбери стиль персонажа:",
        "choose_style_updated": "🎨 Стиль обновлён! Теперь выбери сцену для общения:",
        "choose_scene": "🎬 Теперь выбери сцену для общения:\n\n📱 Переписка в телефоне — классический формат.\n👫 Реальная встреча — живое общение лицом к лицу.",
        "no_messages": "😔 Закончились сообщения. Купи пакет или подписку.",
        "no_history": "❌ Пока нечего редактировать — напиши персонажу хотя бы одно сообщение.",
        "edit_prompt": "✏️ Пришли новый текст своего последнего сообщения — я забуду старую реплику и отвечу заново.",
        "edit_success": "✅ Сообщение заменено. Генерирую новый ответ...",
        "character_created": "✅ **Персонаж создан!**\n\nТеперь ты общаешься с:\n_{text}_\n\nЧтобы вернуться к обычному персонажу — /reset_character",
        "character_reset": "✅ Персонаж сброшен.",
        "character_create_prompt": "🎭 **Создай своего уникального персонажа!**\n\nОпиши любого персонажа — из аниме, фильмов, игр или придумай своего.\nНапиши его/её имя, характер, внешность, откуда он/она, любые детали.\n\n📝 *Пример:*\n«Эльфийка из мира Ведьмака — мудрая, сдержанная, с длинными серебряными волосами. Любит звёзды и долгие разговоры у костра.»\n\n✏️ Напиши описание прямо сейчас — и я запомню его!",
        "spin_title": "🎰 **Колесо фортуны**",
        "spin_prizes": "🔥 **Что можно выиграть:**\n• 10–50 сообщений\n• 100–250 XP\n• 🎁 PRO на 5 дней\n• ✨ SUPER PRO на 3 дня",
        "spin_choose": "Выбери вариант:",
        "spin_nothing": "😢 Ничего... В следующий раз повезёт!",
        "profile": "Подписка: {status}\nОсталось сообщений: {messages}",
        "referral": "👥 **Твоя реферальная ссылка:**\n`{link}`\n\n🎁 За каждого друга, который зарегистрируется по ссылке, — **+10 сообщений** тебе, ему — **+5 бесплатных сообщений**!\n\n📊 Приглашено друзей: **{count}**\n💌 Заработано сообщений: **{earned}**",
        "choose_lang_label": "🌍 Выбери язык:",
        "welcome_back_female": "Ой, тебя так долго не было! Я уже успела соскучиться 🥺💕",
        "welcome_back_male": "Ой, тебя так долго не было! Я уже успел соскучиться 🥺💕",
        "welcome_back_female_2": "Ну наконец-то! Я уже думала, ты меня забыл... 😔",
        "welcome_back_male_2": "Ну наконец-то! Я уже думал, ты меня забыла... 😔",
        "miss_you_female": [
            "Я так соскучилась... Ты где пропал? 😔 Напиши мне...",
            "Эй, ты как? 🥺 Я уже начала волноваться...",
            "Привет! Давно не общались... Расскажи, как дела 💕",
        ],
        "miss_you_male": [
            "Я так соскучился... Ты где пропала? 😔 Напиши мне...",
            "Эй, ты как? 🥺 Я уже начал волноваться...",
            "Привет! Давно не общались... Расскажи, как дела 💕",
        ],
        "level_up": {
            2: "🎉 Между вами пробежала искра! Уровень сближения — 2. Теперь вы можете флиртовать.",
            3: "💞 Вы стали ближе! Уровень 3. Теперь вы можете обниматься и делиться секретами.",
            4: "🔥 Напряжение растёт! Уровень 4.",
            5: "💋 Уровень 5! Вы готовы к первому поцелую.",
            6: "🌹 Уровень 6. Ты влюблён(а)! Теперь вы можете говорить о чувствах открыто.",
            7: "💕 Уровень 7. Вы очень близки друг другу.",
            8: "❤️ Уровень 8! Вы признались друг другу в чувствах. Теперь вы — пара.",
            9: "✨ Уровень 9! Между вами почти нет тайн.",
            10: "💖 Уровень 10! Настоящая душевная близость.",
        },
        "level_down": "💔 Уровень сближения упал до {level}.",
        "menu_current_partner": "Текущий собеседник: {gender} из {world}",
        "menu_style_line": "Стиль: {style}",
        "menu_messages_left": "Осталось сообщений: {n}",
        "menu_messages_out": " (закончились)",
        "menu_free_messages": "У вас есть бесплатные сообщения для старта",
        "menu_write_prompt": "💬 Напиши персонажу...\n✨ Или выбери действие внизу.",
        "xp_level_label": "Уровень {level}/10",
        "xp_bonus_pro": "Бонус XP: x1.8",
        "xp_bonus_super": "Бонус XP: x2.5",
        "profile_sub_pro": "🔥 PRO активна (50 сообщений/день, память 60 сообщений)",
        "profile_sub_super": "✨ SUPER PRO активна (100 сообщений/день, память 100 сообщений)",
        "profile_sub_inactive": "❌ неактивна (память 30 сообщений)",
        "profile_sub_label": "Подписка: {status}",
        "profile_expiry": "Окончание подписки: {date}",
        "profile_expiry_inactive": "Окончание подписки: неактивна",
        "profile_messages_available": "Доступно сообщений: {n}",
        "profile_styles_header": "Доступные стили:",
        "style_locked_alert": "🔒 Стиль «{label}» доступен по подписке {tier}. Оформи в разделе «Мой профиль».",
        "style_changed": "✅ Стиль изменён на: {label}",
        "gender_female": "Девушка",
        "gender_male": "Парень",
        "world_name_realism": "реального мира",
        "world_name_anime": "аниме-мира",
        "spin_already": "⏳ Ты уже крутил сегодня! Завтра будет новое бесплатное вращение.",
        "spin_tomorrow_alert": "⏳ Бесплатное вращение будет доступно завтра!",
        "spin_invoice_desc": "Платное вращение — 20⭐. Удачи!",
        "spin_invoice_label": "Прокрутка",
        "spin_rolling": "🎰 Крутим...",
        "spin_almost": "🎰 Почти выпало: {name}",
        "spin_win_messages": "📨 **+{value} сообщений**",
        "spin_win_xp": "⭐ **+{value} XP**",
        "spin_win_pro": "🎁 **PRO подписка на 5 дней!**\n🔥 50 сообщений/день, стили Страстный и Магнетический!",
        "spin_win_super": "✨ **SUPER PRO на 3 дня!**\n👑 100 сообщений/день, все стили, включая 18+!",
        "spin_result_header": "🎰 **Результат!**\n\nТы выиграл: {result}\n{mode}",
        "spin_mode_free": "🎁 Бесплатное вращение",
        "spin_mode_paid": "💎 Платное вращение",
        "switch_style_prompt": "🔄 **Выбери новый стиль:**\n\nИстория диалога сохранится.",
        "choose_payment": "💳 **Выбери способ оплаты:**",
        "pay_stars": "⭐ Telegram Stars — {amount}⭐",
        "pay_crypto": "🪙 Криптовалюта — ${amount}",
        "pay_lava": "💳 Карта (Lava) — {amount}₽",
        "pay_invoice_ready": "🧾 Счёт создан. Оплати по ссылке — доступ откроется автоматически в течение минуты после оплаты.",
        "pay_open_invoice": "💳 Перейти к оплате",
        "pay_error": "⚠️ Не удалось создать счёт. Попробуй другой способ оплаты.",
        "super_pro_only": "❌ Только для SUPER PRO.",
        "create_character_super_only": "🔒 Создание своего персонажа доступно только с подпиской SUPER PRO!",
        "style_not_found": "❌ Стиль не найден",
        "style_unavailable": "❌ Стиль недоступен",
        "character_updated": "✅ Персонаж обновлён! История сохранена.",
        "create_character_first": "Сначала создай персонажа через /start",
        "finish_registration_first": "🔞 Сначала пройди регистрацию через /start",
        "finish_registration_spin": "Сначала заверши регистрацию через /start.",
        "channel_text": "📢 **Наш канал:**\nПодписывайся, чтобы быть в курсе новостей и обновлений!",
        "ask_create_character": "👤 **Чтобы открыть профиль или купить что-то, сначала создай своего персонажа!**",
        "ask_create_character_btn": "🌟 Создать персонажа",
        "maintenance": "🛠️ **Бот на техобслуживании**\nСледите за новостями: @duel_dev_channel",
        "subscription_expired_style": "⚠️ Твоя подписка закончилась, выбери бесплатный стиль:",
        "quarrel": "💢 Ссора! Уровень близости снижен.",
        "generation_error": "⚠️ Ошибка генерации ответа: {error}",
        "intim_buy_btn": "🔥 Купить интим-сцену (45⭐)",
        "intim_menu_title": "🔥 **Интим-сцена**\n\nДоступно сцен: {n}\nВыбери, что будет происходить:",
        "intim_choose_location": "📍 Выбери место:",
        "intim_none": "🔥 У тебя нет доступных интим-сцен.\n\nКупи сцену в профиле или испытай удачу в Колесе фортуны.",
        "intim_generating": "🔥 Создаю сцену...",
        "intim_free_level": "🎁 Бесплатная сцена за 8 уровень близости!",
        "intim_free_sub": "🎁 Бесплатная сцена по подписке.",
        "intim_left": "🔥 Осталось интим-сцен: {n}",
        "intim_need_character": "Сначала создай персонажа через /start",
        "invoice_intim_title": "Интим-сцена",
        "invoice_intim_desc": "Одна интим-сцена с твоим персонажем.",
        "invoice_intim_label": "Интим-сцена",
        "payment_intim_success": "✅ Интим-сцена куплена! Открой её командой /intim",
        "spin_win_intim": "🔥 **+{value} интим-сцены**",
        "need_character_alert": "Сначала создай персонажа!",
        "already_subscribed_alert": "❌ У вас уже есть подписка.",
        "pro_only_alert": "❌ Только для PRO.",
        "packs_blocked_active_sub": "❌ При активной подписке покупка пакетов недоступна.",
        "subs_title": "👑 Подписки Role Duel",
        "subs_body": "🔥 PRO (250⭐/мес)\n• 50 сообщений в день\n• Стили: ❤️‍🔥 Страстный, ✨ Магнетический\n• Память: 60 сообщений\n• Бонус XP: x1.8\n\n✨ SUPER PRO ✨ (450⭐/мес)\n• 100 сообщений в день\n• Все стили + эксклюзивные 😤 Грубый 18+ и 😏 Соблазн 18+\n• Смена стиля без потери истории (/switch_style)\n• Память: 100 сообщений\n• Бонус XP: x2.5\n• 🎭 Создание своего уникального персонажа!\n\n⬆️ Апгрейд до SUPER PRO (245⭐) — повысьте PRO до SUPER PRO на оставшийся срок.\n\n⚠️ Подписки НЕ продлеваются автоматически.",
        "subs_btn_pro": "🔥 PRO — 250 ⭐/мес",
        "subs_btn_super": "✨ SUPER PRO ✨ — 450 ⭐/мес",
        "subs_btn_upgrade": "⬆️ Апгрейд до SUPER PRO (245⭐)",
        "packs_title": "📦 **Купить пакет сообщений**\n\nВыбери пакет:",
        "pack_btn": "{n} сообщений — {price} ⭐",
        "invoice_pro_title": "PRO подписка на месяц",
        "invoice_pro_desc": "50 сообщений/день, память 60 сообщений, стили Страстный и Магнетический.",
        "invoice_pro_label": "PRO месяц",
        "invoice_super_title": "SUPER PRO подписка на месяц",
        "invoice_super_desc": "100 сообщений/день, память 100 сообщений, все стили, включая 18+.",
        "invoice_super_label": "SUPER PRO месяц",
        "invoice_upgrade_title": "Апгрейд до SUPER PRO",
        "invoice_upgrade_desc": "Повысьте PRO до SUPER PRO на оставшийся срок. 245⭐.",
        "invoice_upgrade_label": "Апгрейд",
        "invoice_pack_title": "Пакет {n} сообщений",
        "invoice_pack_desc": "{n} сообщений за {price}⭐",
        "invoice_pack_label": "{n} сообщ.",
        "payment_pack_success": "✅ Куплено {n} сообщений!",
        "payment_pro_success": "✅ PRO подписка активирована на месяц!",
        "payment_super_success": "✅ SUPER PRO подписка активирована на месяц!",
        "payment_upgrade_success": "✅ Апгрейд до SUPER PRO выполнен до {date}!",
        "agreement": "📜 **ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ**\n\nНастоящее Соглашение регулирует отношения между Администрацией (далее – «Мы») и Пользователем (далее – «Вы») при использовании сервиса Role Duel (далее – «Сервис»).\n\nИспользуя Сервис, Вы подтверждаете, что ознакомились с условиями настоящего Соглашения и принимаете их безоговорочно.\n\n---\n\n**1. ВОЗРАСТНОЕ ОГРАНИЧЕНИЕ**\n1.1. Сервис предназначен исключительно для лиц, достигших 18 лет.\n1.2. Использование Сервиса лицами младше 18 лет строго запрещено.\n\n**2. ОПИСАНИЕ СЕРВИСА**\n2.1. Сервис предоставляет доступ к виртуальным собеседникам на основе технологий искусственного интеллекта.\n2.2. Весь контент генерируется автоматически и не отражает мнение Администрации.\n2.3. Сервис не является медицинским, психологическим или консультационным инструментом.\n\n**3. ОТВЕТСТВЕННОСТЬ ПОЛЬЗОВАТЕЛЯ**\n3.1. Вы несёте полную ответственность за все действия, совершённые с использованием Вашего аккаунта.\n3.2. Запрещается использовать Сервис для распространения экстремистских материалов, оскорблений, угроз, клеветы, мошенничества, вредоносного ПО и любых действий, нарушающих законодательство РФ.\n\n**4. КОНФИДЕНЦИАЛЬНОСТЬ**\n4.1. Мы собираем: Telegram ID, историю диалогов, данные о покупках и подписках.\n4.2. Мы НЕ передаём персональные данные третьим лицам, за исключением случаев, предусмотренных законом.\n\n**5. ПЛАТНЫЕ УСЛУГИ**\n5.1. Сервис предоставляет платные услуги (пакеты сообщений, подписки, колесо фортуны).\n5.2. Подписки **НЕ продлеваются автоматически**.\n5.3. Возврат средств не производится, за исключением технической ошибки со стороны Сервиса.\n\n**6. ОТКАЗ ОТ ГАРАНТИЙ**\nСервис предоставляется «как есть» без каких-либо гарантий бесперебойной работы.\n\n**7. ИЗМЕНЕНИЕ УСЛОВИЙ**\nАдминистрация вправе изменять Соглашение в любое время; продолжение использования Сервиса означает согласие с новой версией.\n\n**8. КОНТАКТЫ**\nВсе вопросы принимаются через поддержку в Telegram.\n\n---\n\n✅ Нажимая кнопку «Принимаю», Вы подтверждаете, что ознакомились со всеми перечисленными выше пунктами и согласны с ними.\n\n⚠️ Если Вы не согласны с настоящим Соглашением, немедленно прекратите использование Сервиса."
    },
    "en": {
        "main_menu": "📋 Main menu",
        "my_profile": "👤 My profile",
        "spin_wheel": "🎰 Spin wheel",
        "our_channel": "🔵 Our channel",
        "edit": "✏️ Edit",
        "change_character": "🔵 Change character",
        "invite_friend": "👥 Invite friend",
        "create_character": "🎭 Create your own character",
        "buy_packs": "📦 Buy packs",
        "subscribe": "👑 Subscribe",
        "back": "🔴 Main menu",
        "back_to_profile": "🔴 Back",
        "accept": "✅ I am 18+",
        "decline": "❌ I am under 18",
        "agree": "🟢 Accept",
        "disagree": "🔴 Decline",
        "open_agreement": "📜 Open agreement",
        "realism": "🌍 Realism",
        "anime": "🎌 Anime",
        "i_male": "👨 I'm male",
        "i_female": "👩 I'm female",
        "scene_phone": "📱 Phone chat",
        "scene_live": "👫 Real meeting",
        "channel": "🔵 Go to channel",
        "free": "🎁 Free (1 per day)",
        "tomorrow": "⏳ Tomorrow",
        "spin_paid": "💎 Spin for 20⭐",
        "spin_more": "💎 Spin again for 20⭐",
        "welcome": "👋 Welcome!",
        "age_confirm": "🔞 **WARNING!**\nThis bot is for 18+ only.\nConfirm your age:",
        "age_ok": "✅ Age confirmed.",
        "age_no": "🚫 Access denied. 18+ only.",
        "agreement_intro": "📜 Before continuing, please read and accept the terms of service:",
        "agreement_ok": "✅ Terms accepted!",
        "agreement_no": "❌ The bot won't work without accepting the terms.",
        "choose_lang": "🌍 Choose language / Выбери язык:",
        "choose_gender": "👤 Choose your gender:",
        "choose_world": "🌍 Choose your world:",
        "choose_world_updated": "🌍 World updated! Now choose your gender:",
        "choose_world_first": "🌍 World chosen! Now choose your gender:",
        "choose_style": "🎨 Now choose your character's style:",
        "choose_style_updated": "🎨 Style updated! Now choose a scene:",
        "choose_scene": "🎬 Now choose a scene:\n\n📱 Phone chat — classic texting format.\n👫 Real meeting — face-to-face conversation.",
        "no_messages": "😔 No messages left. Buy a pack or subscribe.",
        "no_history": "❌ Nothing to edit yet — send your character a message first.",
        "edit_prompt": "✏️ Send the new text for your last message — I'll forget the old one and reply again.",
        "edit_success": "✅ Message replaced. Generating a new response...",
        "character_created": "✅ **Character created!**\n\nNow you're talking to:\n_{text}_\n\nTo go back to the default character — /reset_character",
        "character_reset": "✅ Character reset.",
        "character_create_prompt": "🎭 **Create your own unique character!**\n\nDescribe any character from anime, movies, games, or make up your own.\nWrite their name, personality, appearance, where they're from, any details.\n\n📝 *Example:*\n«An elf from The Witcher — wise, calm, with long silver hair. Loves stars and long conversations by the fire.»\n\n✏️ Write the description now — and I'll remember it!",
        "spin_title": "🎰 **Spin wheel**",
        "spin_prizes": "🔥 **What you can win:**\n• 10–50 messages\n• 100–250 XP\n• 🎁 PRO for 5 days\n• ✨ SUPER PRO for 3 days",
        "spin_choose": "Choose an option:",
        "spin_nothing": "😢 Nothing... Better luck next time!",
        "profile": "Subscription: {status}\nMessages left: {messages}",
        "referral": "👥 **Your referral link:**\n`{link}`\n\n🎁 For every friend who signs up with your link — **+10 messages** for you, and **+5 free messages** for them!\n\n📊 Friends invited: **{count}**\n💌 Messages earned: **{earned}**",
        "choose_lang_label": "🌍 Choose language:",
        "welcome_back_female": "Oh, you've been gone so long! I already missed you 🥺💕",
        "welcome_back_male": "Oh, you've been gone so long! I already missed you 🥺💕",
        "welcome_back_female_2": "Finally! I thought you forgot about me... 😔",
        "welcome_back_male_2": "Finally! I thought you forgot about me... 😔",
        "miss_you_female": [
            "I miss you... where did you go? 😔 Write to me...",
            "Hey, are you okay? 🥺 I was starting to worry...",
            "Hi! It's been a while... tell me how you're doing 💕",
        ],
        "miss_you_male": [
            "I miss you... where did you go? 😔 Write to me...",
            "Hey, are you okay? 🥺 I was starting to worry...",
            "Hi! It's been a while... tell me how you're doing 💕",
        ],
        "level_up": {
            2: "🎉 A spark ran between you! Closeness level 2. Now you can flirt.",
            3: "💞 You're getting closer! Level 3. Now you can hug and share secrets.",
            4: "🔥 The tension is rising! Level 4.",
            5: "💋 Level 5! You're ready for a first kiss.",
            6: "🌹 Level 6. You're falling in love! Now you can talk about feelings openly.",
            7: "💕 Level 7. You're very close to each other.",
            8: "❤️ Level 8! You confessed your feelings to each other. Now you're a couple.",
            9: "✨ Level 9! There are almost no secrets between you.",
            10: "💖 Level 10! A true emotional bond.",
        },
        "level_down": "💔 Closeness level dropped to {level}.",
        "menu_current_partner": "Current partner: {gender} from {world}",
        "menu_style_line": "Style: {style}",
        "menu_messages_left": "Messages left: {n}",
        "menu_messages_out": " (none left)",
        "menu_free_messages": "You have free messages to get started",
        "menu_write_prompt": "💬 Write to your character...\n✨ Or choose an action below.",
        "xp_level_label": "Level {level}/10",
        "xp_bonus_pro": "XP bonus: x1.8",
        "xp_bonus_super": "XP bonus: x2.5",
        "profile_sub_pro": "🔥 PRO active (50 messages per day, 60-message memory)",
        "profile_sub_super": "✨ SUPER PRO active (100 messages per day, 100-message memory)",
        "profile_sub_inactive": "❌ inactive (30-message memory)",
        "profile_sub_label": "Subscription: {status}",
        "profile_expiry": "Subscription ends: {date}",
        "profile_expiry_inactive": "Subscription ends: inactive",
        "profile_messages_available": "Messages available: {n}",
        "profile_styles_header": "Available styles:",
        "style_locked_alert": "🔒 The «{label}» style requires a {tier} subscription. Get it in the «My profile» section.",
        "style_changed": "✅ Style changed to: {label}",
        "gender_female": "Girl",
        "gender_male": "Guy",
        "world_name_realism": "the real world",
        "world_name_anime": "the anime world",
        "spin_already": "⏳ You already spun today! A new free spin will be available tomorrow.",
        "spin_tomorrow_alert": "⏳ The free spin will be available tomorrow!",
        "spin_invoice_desc": "Paid spin — 20⭐. Good luck!",
        "spin_invoice_label": "Spin",
        "spin_rolling": "🎰 Spinning...",
        "spin_almost": "🎰 Almost got: {name}",
        "spin_win_messages": "📨 **+{value} messages**",
        "spin_win_xp": "⭐ **+{value} XP**",
        "spin_win_pro": "🎁 **PRO subscription for 5 days!**\n🔥 50 messages per day, Passionate and Magnetic styles!",
        "spin_win_super": "✨ **SUPER PRO for 3 days!**\n👑 100 messages per day, all styles including 18+!",
        "spin_result_header": "🎰 **Result!**\n\nYou won: {result}\n{mode}",
        "spin_mode_free": "🎁 Free spin",
        "spin_mode_paid": "💎 Paid spin",
        "switch_style_prompt": "🔄 **Choose a new style:**\n\nYour conversation history will be kept.",
        "choose_payment": "💳 **Choose a payment method:**",
        "pay_stars": "⭐ Telegram Stars — {amount}⭐",
        "pay_crypto": "🪙 Crypto — ${amount}",
        "pay_lava": "💳 Card (Lava) — {amount}₽",
        "pay_invoice_ready": "🧾 Invoice created. Pay via the link — access opens automatically within a minute after payment.",
        "pay_open_invoice": "💳 Go to payment",
        "pay_error": "⚠️ Could not create the invoice. Please try another payment method.",
        "super_pro_only": "❌ SUPER PRO only.",
        "create_character_super_only": "🔒 Creating your own character requires a SUPER PRO subscription!",
        "style_not_found": "❌ Style not found",
        "style_unavailable": "❌ Style unavailable",
        "character_updated": "✅ Character updated! Your history is kept.",
        "create_character_first": "Create your character first via /start",
        "finish_registration_first": "🔞 Please finish registration via /start first",
        "finish_registration_spin": "Please finish registration via /start first.",
        "channel_text": "📢 **Our channel:**\nSubscribe to keep up with news and updates!",
        "ask_create_character": "👤 **To open your profile or buy anything, create your character first!**",
        "ask_create_character_btn": "🌟 Create a character",
        "maintenance": "🛠️ **The bot is under maintenance**\nFollow the news: @duel_dev_channel",
        "subscription_expired_style": "⚠️ Your subscription has ended, pick a free style:",
        "quarrel": "💢 A quarrel! Your closeness level dropped.",
        "generation_error": "⚠️ Failed to generate a reply: {error}",
        "intim_buy_btn": "🔥 Buy an intimate scene (45⭐)",
        "intim_menu_title": "🔥 **Intimate scene**\n\nScenes available: {n}\nChoose what happens:",
        "intim_choose_location": "📍 Choose a place:",
        "intim_none": "🔥 You have no intimate scenes left.\n\nBuy one in your profile or try your luck on the spin wheel.",
        "intim_generating": "🔥 Creating the scene...",
        "intim_free_level": "🎁 A free scene for reaching closeness level 8!",
        "intim_free_sub": "🎁 A free scene from your subscription.",
        "intim_left": "🔥 Intimate scenes left: {n}",
        "intim_need_character": "Create your character first via /start",
        "invoice_intim_title": "Intimate scene",
        "invoice_intim_desc": "One intimate scene with your character.",
        "invoice_intim_label": "Intimate scene",
        "payment_intim_success": "✅ Intimate scene purchased! Open it with /intim",
        "spin_win_intim": "🔥 **+{value} intimate scene(s)**",
        "need_character_alert": "Create your character first!",
        "already_subscribed_alert": "❌ You already have a subscription.",
        "pro_only_alert": "❌ PRO only.",
        "packs_blocked_active_sub": "❌ Packs can't be bought while a subscription is active.",
        "subs_title": "👑 Role Duel Subscriptions",
        "subs_body": "🔥 PRO (250⭐ per month)\n• 50 messages a day\n• Styles: ❤️‍🔥 Passionate, ✨ Magnetic\n• Memory: 60 messages\n• XP bonus: x1.8\n\n✨ SUPER PRO ✨ (450⭐ per month)\n• 100 messages a day\n• All styles + exclusive 😤 Rough 18+ and 😏 Temptation 18+\n• Switch styles without losing history (/switch_style)\n• Memory: 100 messages\n• XP bonus: x2.5\n• 🎭 Create your own unique character!\n\n⬆️ Upgrade to SUPER PRO (245⭐) — upgrade PRO to SUPER PRO for the remaining time.\n\n⚠️ Subscriptions do NOT renew automatically.",
        "subs_btn_pro": "🔥 PRO — 250 ⭐ per month",
        "subs_btn_super": "✨ SUPER PRO ✨ — 450 ⭐ per month",
        "subs_btn_upgrade": "⬆️ Upgrade to SUPER PRO (245⭐)",
        "packs_title": "📦 **Buy a message pack**\n\nChoose a pack:",
        "pack_btn": "{n} messages — {price} ⭐",
        "invoice_pro_title": "PRO subscription for a month",
        "invoice_pro_desc": "50 messages per day, 60-message memory, Passionate and Magnetic styles.",
        "invoice_pro_label": "PRO month",
        "invoice_super_title": "SUPER PRO subscription for a month",
        "invoice_super_desc": "100 messages per day, 100-message memory, all styles including 18+.",
        "invoice_super_label": "SUPER PRO month",
        "invoice_upgrade_title": "Upgrade to SUPER PRO",
        "invoice_upgrade_desc": "Upgrade PRO to SUPER PRO for the remaining time. 245⭐.",
        "invoice_upgrade_label": "Upgrade",
        "invoice_pack_title": "Pack of {n} messages",
        "invoice_pack_desc": "{n} messages for {price}⭐",
        "invoice_pack_label": "{n} msgs",
        "payment_pack_success": "✅ Purchased {n} messages!",
        "payment_pro_success": "✅ PRO subscription activated for a month!",
        "payment_super_success": "✅ SUPER PRO subscription activated for a month!",
        "payment_upgrade_success": "✅ Upgrade to SUPER PRO done until {date}!",
        "agreement": "📜 **TERMS OF SERVICE**\n\nThis Agreement governs the relationship between the Administration (\"We\") and the User (\"You\") when using the Role Duel service (\"Service\").\n\nBy using the Service, you confirm that you have read and accept the terms of this Agreement unconditionally.\n\n---\n\n**1. AGE RESTRICTION**\n1.1. The Service is intended exclusively for persons aged 18 and over.\n1.2. Use of the Service by persons under 18 is strictly prohibited.\n\n**2. SERVICE DESCRIPTION**\n2.1. The Service provides access to virtual companions based on artificial intelligence.\n2.2. All content is generated automatically and does not reflect the Administration's opinion.\n2.3. The Service is not a medical, psychological or consulting tool.\n\n**3. USER RESPONSIBILITY**\n3.1. You are fully responsible for all actions performed using your account.\n3.2. It is prohibited to use the Service to distribute extremist materials, insults, threats, fraud, malware, or anything violating applicable law.\n\n**4. PRIVACY**\n4.1. We collect: Telegram ID, chat history, purchase and subscription data.\n4.2. We do NOT share personal data with third parties, except as required by law.\n\n**5. PAID SERVICES**\n5.1. The Service provides paid features (message packs, subscriptions, spin wheel).\n5.2. Subscriptions are **NOT renewed automatically**.\n5.3. Refunds are not provided except in case of a technical error by the Service.\n\n**6. DISCLAIMER**\nThe Service is provided «as is» with no uptime guarantees.\n\n**7. CHANGES TO TERMS**\nThe Administration may change this Agreement at any time; continued use means acceptance of the new version.\n\n**8. CONTACT**\nAll questions are handled through Telegram support.\n\n---\n\n✅ By clicking «Accept» below, you confirm that you have read all the items listed above and agree to them.\n\n⚠️ If you do not agree with this Agreement, stop using the Service immediately."
    },
    "de": {
        "main_menu": "📋 Hauptmenü",
        "my_profile": "👤 Mein Profil",
        "spin_wheel": "🎰 Glücksrad",
        "our_channel": "🔵 Unser Kanal",
        "edit": "✏️ Bearbeiten",
        "change_character": "🔵 Charakter wechseln",
        "invite_friend": "👥 Freund einladen",
        "create_character": "🎭 Eigenen Charakter erstellen",
        "buy_packs": "📦 Pakete kaufen",
        "subscribe": "👑 Abo abschließen",
        "back": "🔴 Hauptmenü",
        "back_to_profile": "🔴 Zurück",
        "accept": "✅ Ich bin 18+",
        "decline": "❌ Ich bin unter 18",
        "agree": "🟢 Akzeptieren",
        "disagree": "🔴 Ablehnen",
        "open_agreement": "📜 Vereinbarung öffnen",
        "realism": "🌍 Realismus",
        "anime": "🎌 Anime",
        "i_male": "👨 Ich bin ein Mann",
        "i_female": "👩 Ich bin eine Frau",
        "scene_phone": "📱 Chat am Handy",
        "scene_live": "👫 Echtes Treffen",
        "channel": "🔵 Zum Kanal",
        "free": "🎁 Gratis (1 pro Tag)",
        "tomorrow": "⏳ Morgen",
        "spin_paid": "💎 Für 20⭐ drehen",
        "spin_more": "💎 Nochmal für 20⭐ drehen",
        "welcome": "👋 Willkommen!",
        "age_confirm": "🔞 **ACHTUNG!**\nDieser Bot ist nur für Personen ab 18 Jahren.\nBestätige dein Alter:",
        "age_ok": "✅ Alter bestätigt.",
        "age_no": "🚫 Zugriff verweigert. Nur ab 18 Jahren.",
        "agreement_intro": "📜 Bevor es weitergeht, lies bitte die Nutzungsvereinbarung und akzeptiere sie:",
        "agreement_ok": "✅ Vereinbarung akzeptiert!",
        "agreement_no": "❌ Ohne akzeptierte Vereinbarung funktioniert der Bot nicht.",
        "choose_lang": "🌍 Sprache wählen / Choose language:",
        "choose_gender": "👤 Wähle dein Geschlecht:",
        "choose_world": "🌍 Wähle deine Welt:",
        "choose_world_updated": "🌍 Welt aktualisiert! Wähle jetzt dein Geschlecht:",
        "choose_world_first": "🌍 Welt gewählt! Wähle jetzt dein Geschlecht:",
        "choose_style": "🎨 Wähle jetzt den Stil deines Charakters:",
        "choose_style_updated": "🎨 Stil aktualisiert! Wähle jetzt eine Szene:",
        "choose_scene": "🎬 Wähle jetzt eine Szene:\n\n📱 Chat am Handy — das klassische Schreiben.\n👫 Echtes Treffen — ein Gespräch von Angesicht zu Angesicht.",
        "no_messages": "😔 Keine Nachrichten mehr übrig. Kaufe ein Paket oder ein Abo.",
        "no_history": "❌ Noch nichts zum Bearbeiten — schreibe deinem Charakter zuerst eine Nachricht.",
        "edit_prompt": "✏️ Schicke den neuen Text deiner letzten Nachricht — ich vergesse die alte und antworte neu.",
        "edit_success": "✅ Nachricht ersetzt. Ich erstelle eine neue Antwort...",
        "character_created": "✅ **Charakter erstellt!**\n\nDu sprichst jetzt mit:\n_{text}_\n\nZurück zum normalen Charakter — /reset_character",
        "character_reset": "✅ Charakter zurückgesetzt.",
        "character_create_prompt": "🎭 **Erstelle deinen eigenen Charakter!**\n\nBeschreibe eine beliebige Figur — aus Anime, Filmen, Spielen oder denk dir selbst eine aus.\nSchreibe Namen, Charakter, Aussehen, Herkunft und beliebige Details.\n\n📝 *Beispiel:*\n«Eine Elfe aus der Welt von The Witcher — weise, ruhig, mit langen silbernen Haaren. Sie liebt Sterne und lange Gespräche am Feuer.»\n\n✏️ Schreibe die Beschreibung jetzt — und ich merke sie mir!",
        "spin_title": "🎰 **Glücksrad**",
        "spin_prizes": "🔥 **Das kannst du gewinnen:**\n• 10–50 Nachrichten\n• 100–250 XP\n• 🎁 PRO für 5 Tage\n• ✨ SUPER PRO für 3 Tage",
        "spin_choose": "Wähle eine Option:",
        "spin_nothing": "😢 Nichts... Beim nächsten Mal klappt es!",
        "profile": "Abo: {status}\nNachrichten übrig: {messages}",
        "referral": "👥 **Dein Einladungslink:**\n`{link}`\n\n🎁 Für jeden Freund, der sich über deinen Link anmeldet: **+10 Nachrichten** für dich und **+5 gratis Nachrichten** für ihn!\n\n📊 Eingeladene Freunde: **{count}**\n💌 Verdiente Nachrichten: **{earned}**",
        "choose_lang_label": "🌍 Sprache wählen:",
        "welcome_back_female": "Oh, du warst so lange weg! Ich habe dich schon vermisst 🥺💕",
        "welcome_back_male": "Oh, du warst so lange weg! Ich habe dich schon vermisst 🥺💕",
        "welcome_back_female_2": "Endlich! Ich dachte schon, du hättest mich vergessen... 😔",
        "welcome_back_male_2": "Endlich! Ich dachte schon, du hättest mich vergessen... 😔",
        "miss_you_female": [
            "Ich vermisse dich... Wo steckst du? 😔 Schreib mir...",
            "Hey, alles okay bei dir? 🥺 Ich habe mir schon Sorgen gemacht...",
            "Hi! Wir haben lange nicht geredet... Erzähl, wie geht es dir 💕",
        ],
        "miss_you_male": [
            "Ich vermisse dich... Wo steckst du? 😔 Schreib mir...",
            "Hey, alles okay bei dir? 🥺 Ich habe mir schon Sorgen gemacht...",
            "Hi! Wir haben lange nicht geredet... Erzähl, wie geht es dir 💕",
        ],
        "level_up": {
            2: "🎉 Zwischen euch hat es gefunkt! Nähe-Level 2. Jetzt könnt ihr flirten.",
            3: "💞 Ihr kommt euch näher! Level 3. Jetzt könnt ihr euch umarmen und Geheimnisse teilen.",
            4: "🔥 Die Spannung steigt! Level 4.",
            5: "💋 Level 5! Ihr seid bereit für den ersten Kuss.",
            6: "🌹 Level 6. Du bist verliebt! Jetzt könnt ihr offen über Gefühle sprechen.",
            7: "💕 Level 7. Ihr steht euch sehr nahe.",
            8: "❤️ Level 8! Ihr habt einander eure Gefühle gestanden. Jetzt seid ihr ein Paar.",
            9: "✨ Level 9! Zwischen euch gibt es fast keine Geheimnisse mehr.",
            10: "💖 Level 10! Echte seelische Verbundenheit.",
        },
        "level_down": "💔 Das Nähe-Level ist auf {level} gefallen.",
        "menu_current_partner": "Aktueller Gesprächspartner: {gender} aus {world}",
        "menu_style_line": "Stil: {style}",
        "menu_messages_left": "Nachrichten übrig: {n}",
        "menu_messages_out": " (aufgebraucht)",
        "menu_free_messages": "Du hast gratis Nachrichten für den Start",
        "menu_write_prompt": "💬 Schreibe deinem Charakter...\n✨ Oder wähle unten eine Aktion.",
        "xp_level_label": "Level {level}/10",
        "xp_bonus_pro": "XP-Bonus: x1.8",
        "xp_bonus_super": "XP-Bonus: x2.5",
        "profile_sub_pro": "🔥 PRO aktiv (50 Nachrichten pro Tag, Gedächtnis 60 Nachrichten)",
        "profile_sub_super": "✨ SUPER PRO aktiv (100 Nachrichten pro Tag, Gedächtnis 100 Nachrichten)",
        "profile_sub_inactive": "❌ inaktiv (Gedächtnis 30 Nachrichten)",
        "profile_sub_label": "Abo: {status}",
        "profile_expiry": "Abo endet am: {date}",
        "profile_expiry_inactive": "Abo endet am: inaktiv",
        "profile_messages_available": "Verfügbare Nachrichten: {n}",
        "profile_styles_header": "Verfügbare Stile:",
        "style_locked_alert": "🔒 Der Stil «{label}» ist im {tier}-Abo enthalten. Hol es dir im Bereich «Mein Profil».",
        "style_changed": "✅ Stil geändert zu: {label}",
        "gender_female": "Mädchen",
        "gender_male": "Junge",
        "world_name_realism": "der echten Welt",
        "world_name_anime": "der Anime-Welt",
        "spin_already": "⏳ Du hast heute schon gedreht! Morgen gibt es eine neue Gratisdrehung.",
        "spin_tomorrow_alert": "⏳ Die Gratisdrehung gibt es morgen wieder!",
        "spin_invoice_desc": "Bezahlte Drehung — 20⭐. Viel Glück!",
        "spin_invoice_label": "Drehung",
        "spin_rolling": "🎰 Es dreht sich...",
        "spin_almost": "🎰 Fast gewonnen: {name}",
        "spin_win_messages": "📨 **+{value} Nachrichten**",
        "spin_win_xp": "⭐ **+{value} XP**",
        "spin_win_pro": "🎁 **PRO-Abo für 5 Tage!**\n🔥 50 Nachrichten pro Tag, Stile Leidenschaftlich und Magnetisch!",
        "spin_win_super": "✨ **SUPER PRO für 3 Tage!**\n👑 100 Nachrichten pro Tag, alle Stile inklusive 18+!",
        "spin_result_header": "🎰 **Ergebnis!**\n\nDu hast gewonnen: {result}\n{mode}",
        "spin_mode_free": "🎁 Gratisdrehung",
        "spin_mode_paid": "💎 Bezahlte Drehung",
        "switch_style_prompt": "🔄 **Wähle einen neuen Stil:**\n\nDer Gesprächsverlauf bleibt erhalten.",
        "choose_payment": "💳 **Wähle eine Zahlungsart:**",
        "pay_stars": "⭐ Telegram Stars — {amount}⭐",
        "pay_crypto": "🪙 Krypto — ${amount}",
        "pay_lava": "💳 Karte (Lava) — {amount}₽",
        "pay_invoice_ready": "🧾 Rechnung erstellt. Zahle über den Link — der Zugang wird innerhalb einer Minute nach der Zahlung automatisch freigeschaltet.",
        "pay_open_invoice": "💳 Zur Zahlung",
        "pay_error": "⚠️ Rechnung konnte nicht erstellt werden. Bitte versuche eine andere Zahlungsart.",
        "super_pro_only": "❌ Nur für SUPER PRO.",
        "create_character_super_only": "🔒 Einen eigenen Charakter zu erstellen ist nur mit SUPER PRO möglich!",
        "style_not_found": "❌ Stil nicht gefunden",
        "style_unavailable": "❌ Stil nicht verfügbar",
        "character_updated": "✅ Charakter aktualisiert! Der Verlauf bleibt erhalten.",
        "create_character_first": "Erstelle zuerst deinen Charakter über /start",
        "finish_registration_first": "🔞 Schließe zuerst die Registrierung über /start ab",
        "finish_registration_spin": "Schließe zuerst die Registrierung über /start ab.",
        "channel_text": "📢 **Unser Kanal:**\nAbonniere ihn, um Neuigkeiten und Updates nicht zu verpassen!",
        "ask_create_character": "👤 **Um dein Profil zu öffnen oder etwas zu kaufen, erstelle zuerst deinen Charakter!**",
        "ask_create_character_btn": "🌟 Charakter erstellen",
        "maintenance": "🛠️ **Der Bot wird gewartet**\nNeuigkeiten gibt es hier: @duel_dev_channel",
        "subscription_expired_style": "⚠️ Dein Abo ist abgelaufen, wähle einen kostenlosen Stil:",
        "quarrel": "💢 Streit! Dein Nähe-Level ist gesunken.",
        "generation_error": "⚠️ Antwort konnte nicht erzeugt werden: {error}",
        "intim_buy_btn": "🔥 Intim-Szene kaufen (45⭐)",
        "intim_menu_title": "🔥 **Intim-Szene**\n\nVerfügbare Szenen: {n}\nWähle, was passiert:",
        "intim_choose_location": "📍 Wähle einen Ort:",
        "intim_none": "🔥 Du hast keine Intim-Szenen mehr.\n\nKaufe eine im Profil oder versuche dein Glück am Glücksrad.",
        "intim_generating": "🔥 Die Szene entsteht...",
        "intim_free_level": "🎁 Eine Gratis-Szene für Nähe-Level 8!",
        "intim_free_sub": "🎁 Eine Gratis-Szene aus deinem Abo.",
        "intim_left": "🔥 Verbleibende Intim-Szenen: {n}",
        "intim_need_character": "Erstelle zuerst deinen Charakter über /start",
        "invoice_intim_title": "Intim-Szene",
        "invoice_intim_desc": "Eine Intim-Szene mit deinem Charakter.",
        "invoice_intim_label": "Intim-Szene",
        "payment_intim_success": "✅ Intim-Szene gekauft! Öffne sie mit /intim",
        "spin_win_intim": "🔥 **+{value} Intim-Szene(n)**",
        "need_character_alert": "Erstelle zuerst deinen Charakter!",
        "already_subscribed_alert": "❌ Du hast bereits ein Abo.",
        "pro_only_alert": "❌ Nur für PRO.",
        "packs_blocked_active_sub": "❌ Mit einem aktiven Abo können keine Pakete gekauft werden.",
        "subs_title": "👑 Role Duel Abos",
        "subs_body": "🔥 PRO (250⭐ pro Monat)\n• 50 Nachrichten pro Tag\n• Stile: ❤️‍🔥 Leidenschaftlich, ✨ Magnetisch\n• Gedächtnis: 60 Nachrichten\n• XP-Bonus: x1.8\n\n✨ SUPER PRO ✨ (450⭐ pro Monat)\n• 100 Nachrichten pro Tag\n• Alle Stile + exklusiv 😤 Rau 18+ und 😏 Verführung 18+\n• Stilwechsel ohne Verlust des Verlaufs (/switch_style)\n• Gedächtnis: 100 Nachrichten\n• XP-Bonus: x2.5\n• 🎭 Eigenen Charakter erstellen!\n\n⬆️ Upgrade auf SUPER PRO (245⭐) — hebt PRO für die Restlaufzeit auf SUPER PRO an.\n\n⚠️ Abos verlängern sich NICHT automatisch.",
        "subs_btn_pro": "🔥 PRO — 250 ⭐ pro Monat",
        "subs_btn_super": "✨ SUPER PRO ✨ — 450 ⭐ pro Monat",
        "subs_btn_upgrade": "⬆️ Upgrade auf SUPER PRO (245⭐)",
        "packs_title": "📦 **Nachrichtenpaket kaufen**\n\nWähle ein Paket:",
        "pack_btn": "{n} Nachrichten — {price} ⭐",
        "invoice_pro_title": "PRO-Abo für einen Monat",
        "invoice_pro_desc": "50 Nachrichten pro Tag, Gedächtnis 60 Nachrichten, Stile Leidenschaftlich und Magnetisch.",
        "invoice_pro_label": "PRO Monat",
        "invoice_super_title": "SUPER PRO-Abo für einen Monat",
        "invoice_super_desc": "100 Nachrichten pro Tag, Gedächtnis 100 Nachrichten, alle Stile inklusive 18+.",
        "invoice_super_label": "SUPER PRO Monat",
        "invoice_upgrade_title": "Upgrade auf SUPER PRO",
        "invoice_upgrade_desc": "Hebt PRO für die Restlaufzeit auf SUPER PRO an. 245⭐.",
        "invoice_upgrade_label": "Upgrade",
        "invoice_pack_title": "Paket mit {n} Nachrichten",
        "invoice_pack_desc": "{n} Nachrichten für {price}⭐",
        "invoice_pack_label": "{n} Nachr.",
        "payment_pack_success": "✅ {n} Nachrichten gekauft!",
        "payment_pro_success": "✅ PRO-Abo für einen Monat aktiviert!",
        "payment_super_success": "✅ SUPER PRO-Abo für einen Monat aktiviert!",
        "payment_upgrade_success": "✅ Upgrade auf SUPER PRO bis {date} erledigt!",
        "agreement": "📜 **NUTZUNGSVEREINBARUNG**\n\nDiese Vereinbarung regelt das Verhältnis zwischen der Administration (nachfolgend «Wir») und dem Nutzer (nachfolgend «Du») bei der Nutzung des Dienstes Role Duel (nachfolgend «Dienst»).\n\nMit der Nutzung des Dienstes bestätigst du, dass du die Bedingungen dieser Vereinbarung gelesen hast und sie vorbehaltlos akzeptierst.\n\n---\n\n**1. ALTERSBESCHRÄNKUNG**\n1.1. Der Dienst ist ausschließlich für Personen ab 18 Jahren bestimmt.\n1.2. Die Nutzung durch Personen unter 18 Jahren ist strengstens untersagt.\n\n**2. BESCHREIBUNG DES DIENSTES**\n2.1. Der Dienst bietet Zugang zu virtuellen Gesprächspartnern auf Basis künstlicher Intelligenz.\n2.2. Alle Inhalte werden automatisch generiert und geben nicht die Meinung der Administration wieder.\n2.3. Der Dienst ist kein medizinisches, psychologisches oder beratendes Hilfsmittel.\n\n**3. VERANTWORTUNG DES NUTZERS**\n3.1. Du trägst die volle Verantwortung für alle Handlungen, die über dein Konto erfolgen.\n3.2. Es ist untersagt, den Dienst zur Verbreitung extremistischer Materialien, Beleidigungen, Drohungen, Verleumdung, Betrug, Schadsoftware oder für sonstige rechtswidrige Handlungen zu nutzen.\n\n**4. DATENSCHUTZ**\n4.1. Wir erheben: Telegram-ID, Chatverlauf, Kauf- und Abodaten.\n4.2. Wir geben personenbezogene Daten NICHT an Dritte weiter, außer wenn dies gesetzlich vorgeschrieben ist.\n\n**5. KOSTENPFLICHTIGE LEISTUNGEN**\n5.1. Der Dienst bietet kostenpflichtige Leistungen an (Nachrichtenpakete, Abos, Glücksrad).\n5.2. Abos verlängern sich **NICHT automatisch**.\n5.3. Eine Rückerstattung erfolgt nicht, außer bei einem technischen Fehler des Dienstes.\n\n**6. HAFTUNGSAUSSCHLUSS**\nDer Dienst wird «wie besehen» ohne Garantie für einen unterbrechungsfreien Betrieb bereitgestellt.\n\n**7. ÄNDERUNG DER BEDINGUNGEN**\nDie Administration kann diese Vereinbarung jederzeit ändern; die weitere Nutzung gilt als Zustimmung zur neuen Fassung.\n\n**8. KONTAKT**\nAlle Fragen werden über den Telegram-Support bearbeitet.\n\n---\n\n✅ Mit dem Klick auf «Akzeptieren» bestätigst du, dass du alle oben genannten Punkte gelesen hast und ihnen zustimmst.\n\n⚠️ Wenn du dieser Vereinbarung nicht zustimmst, beende die Nutzung des Dienstes sofort.",
    }
}

SUPPORTED_LANGS = ("ru", "en", "de")


def get_text(user, key, **kwargs):
    lang = user.get("lang", "ru")
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, TEXTS["ru"][key])
    if kwargs:
        text = text.format(**kwargs)
    return text


def is_button(text, key):
    """Сравнивает текст сообщения с подписью кнопки на любом из поддерживаемых языков.
    Нужно, потому что клавиатуры локализованы, а не захардкожены на русском: пользователь
    мог сменить язык, а на клавиатуре у него в этот момент ещё старые подписи."""
    if not text:
        return False
    return any(text == TEXTS[lang][key] for lang in SUPPORTED_LANGS)


# ============================================================
#  НАСТРОЙКА
# ============================================================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PROVOD_API_KEY = os.getenv("PROVOD_API_KEY")

if not BOT_TOKEN or not PROVOD_API_KEY:
    raise ValueError("Заполни BOT_TOKEN и PROVOD_API_KEY в .env!")

client = OpenAI(api_key=PROVOD_API_KEY, base_url="https://api.provod.ai/v1")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

AI_MODEL = os.getenv("AI_MODEL", "deepseek/deepseek-chat")
# Модель для интим-сцен можно задать отдельно, например deepseek/deepseek-v4-pro
INTIM_MODEL = os.getenv("INTIM_MODEL", AI_MODEL)

PRO_GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGJ5aTRkejlwMGh4eWJ2Zzg0bTVlbWE2ZzFicHlsMXNibXp3dXdsayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GGSbxfzvec3PYZbFOM/giphy.gif"
SUPER_PRO_GIF_URL = "https://media.giphy.com/media/DbHZXBo5WFPZX7QpXj/giphy.gif"
MAIN_MENU_IMAGE_URL = "https://i.ibb.co/k25JyTXD/IMG-2584.jpg"

ADMIN_IDS = [7287815074]
maintenance_mode = False

# На хостинге bot.host.ru контейнер пересобирается из GitHub при каждом деплое
# (COPY . . в Dockerfile), а каталог /app/data создаётся хостом отдельно
# (mkdir -p /app/data && chmod 777) именно как постоянное хранилище — то, что
# лежит вне data/, при пересборке слетает. Поэтому путь обязательно должен
# указывать внутрь DATA_DIR, который хостинг прокидывает как переменную
# окружения; локально (без бота на хостинге) используем просто "./data".
DATA_DIR = os.getenv("DATA_DIR", "data")
DATA_FILE = os.path.join(DATA_DIR, "data.json")


DATA_BACKUP_FILE = DATA_FILE + ".bak"

_data_mtime = None  # время последней известной нам версии файла, см. sync_data()


def _file_mtime():
    try:
        return os.path.getmtime(DATA_FILE)
    except OSError:
        return None


def _read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_data():
    global _data_mtime
    for path in (DATA_FILE, DATA_BACKUP_FILE):
        if not os.path.exists(path):
            continue
        try:
            data = _read_json(path)
        except (json.JSONDecodeError, ValueError):
            logging.warning(f"Файл {path} повреждён, пробуем резервную копию")
            continue
        if path == DATA_BACKUP_FILE:
            logging.warning("Основной файл не читается — данные восстановлены из .bak")
        _data_mtime = _file_mtime()
        return data
    return {}


def save_data(data):
    """Пишем через временный файл и os.replace: если процесс убьют посреди записи
    (например, хостинг перезапускает контейнер при деплое), data.json останется
    целым — раньше open(..., "w") сразу обнулял файл, и при неудачном моменте
    вся база превращалась в пустой/битый JSON, то есть все регистрации слетали."""
    global _data_mtime
    directory = os.path.dirname(DATA_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp_path = DATA_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    if os.path.exists(DATA_FILE):
        try:
            os.replace(DATA_FILE, DATA_BACKUP_FILE)
        except OSError:
            pass
    os.replace(tmp_path, DATA_FILE)
    _data_mtime = _file_mtime()


def sync_data():
    """Если файл изменился на диске не нашей записью — перечитываем его.
    Такое бывает, когда рядом остался работать второй экземпляр бота (например,
    старый контейнер не остановился после передеплоя): каждый процесс держит свой
    снимок user_data и при сохранении затирает чужие изменения. Из-за этого,
    в частности, уже выбранный язык мог "исчезнуть" на следующем шаге регистрации."""
    mtime = _file_mtime()
    if mtime is None or mtime == _data_mtime:
        return
    fresh = load_data()
    for user_id, record in fresh.items():
        current = user_data.get(user_id)
        if isinstance(current, dict) and isinstance(record, dict):
            # обновляем словарь на месте, чтобы ссылки внутри хендлеров остались валидными
            current.clear()
            current.update(record)
        else:
            user_data[user_id] = record


user_data = load_data()


def get_free_limit():
    return 13


def get_user(user_id):
    sync_data()
    user_id = str(user_id)
    if user_id not in user_data:
        user_data[user_id] = {
            "verified": False,
            "agreement_accepted": False,
            "world": None,
            "gender": None,
            "user_gender": None,
            "style": "warm",
            "personality_ready": False,
            "subscription": {"active": False, "expires_at": None, "level": None},
            "purchased_messages": get_free_limit(),
            "has_purchased": False,
            "daily_messages": 0,
            "last_daily_reset": None,
            "history": [],
            "last_menu_message_id": None,
            "xp": 0,
            "mood": 0,
            "location": "unknown",
            "negative_count": 0,
            "last_level": 0,
            "scene": "phone",
            "switching_personality": False,
            "last_free_spin": None,
            "lang": None,
            "editing_message": False,
            "referral_code": None,
            "referred_by": None,
            "referral_count": 0,
            "pending_payments": [],
            "intim_scenes": 0,
            "free_intim_scenes_pro": 0,
            "free_intim_scenes_super": 0,
            "intim_scene_unlocked": False,
            "intim_scene_used": False,
            "last_activity": datetime.now().isoformat(),
            "last_reminder": None,
            "creating_character": False,
            "custom_character": None
        }
        save_data(user_data)
    else:
        user = user_data[user_id]
        defaults = {
            "user_gender": None,
            "style": "warm",
            "purchased_messages": get_free_limit(),
            "has_purchased": False,
            "daily_messages": 0,
            "last_daily_reset": None,
            "history": [],
            "last_menu_message_id": None,
            "subscription": {"active": False, "expires_at": None, "level": None},
            "xp": 0,
            "mood": 0,
            "location": "unknown",
            "negative_count": 0,
            "last_level": 0,
            "scene": "phone",
            "switching_personality": False,
            "last_free_spin": None,
            "lang": None,
            "editing_message": False,
            "referral_code": None,
            "referred_by": None,
            "referral_count": 0,
            "pending_payments": [],
            "intim_scenes": 0,
            "free_intim_scenes_pro": 0,
            "free_intim_scenes_super": 0,
            "intim_scene_unlocked": False,
            "intim_scene_used": False,
            "last_activity": None,
            "last_reminder": None,
            "creating_character": False,
            "custom_character": None
        }
        for key, val in defaults.items():
            if key not in user:
                user[key] = val

        # МИГРАЦИЯ СТАРЫХ ДАННЫХ: в реальной базе встречаются значения из более старой
        # версии бота, которых в текущей схеме больше нет (например world="fantasy" или
        # style="vulgar" после удаления 18+ стилей). Без этой проверки первое же обращение
        # такого пользователя падало бы с KeyError в WORLDS[...]/STYLES[...].
        if user.get("world") and user["world"] not in WORLDS:
            user["world"] = None
            user["personality_ready"] = False
        if user.get("style") not in STYLES:
            user["style"] = "warm"

        save_data(user_data)
    return user_data[user_id]


# ============================================================
#  МИРЫ, ГЕНДЕРЫ, СТИЛИ (без интим/18+ стилей — см. пункт 6 задачи)
# ============================================================
WORLD_NAMES = {"realism": "реального мира", "anime": "аниме-мира"}
WORLDS = {
    "realism": "реального мира, современная эпоха. Ты живёшь в большом городе, у тебя есть работа, друзья и свои привычки.",
    "anime": "аниме-мира, где всё выглядит как в японской анимации. У тебя яркие волосы, большие выразительные глаза, ты носишь стильную одежду. В этом мире есть школы, клубы, магия и романтика, как в лучших аниме-сериалах."
}
GENDERS = {"female": {"name": "Девушка", "age": 22}, "male": {"name": "Парень", "age": 24}}


def gender_display_name(gender_key, user):
    return get_text(user, f"gender_{gender_key}")


def world_display_name(world_key, user):
    return get_text(user, f"world_name_{world_key}")

BASE_STYLES = {
    "warm": {
        "label": "Нежный",
        "label_en": "Gentle",
        "label_de": "Sanft",
        "emoji": "🪶",
        "description": "Ты нежный, с мягким голосом. Ты умеешь слушать и поддерживать. Ты не торопишь события, ценишь искренность и доверие."
    },
    "daring": {
        "label": "Дерзкий",
        "label_en": "Bold",
        "label_de": "Frech",
        "emoji": "🔥",
        "description": "Ты уверенный, прямолинейный, с искоркой в глазах. Ты любишь флиртовать и остроумно шутить, но всегда знаешь меру."
    },
    "shy": {
        "label": "Стеснительный",
        "label_en": "Shy",
        "label_de": "Schüchtern",
        "emoji": "😊",
        "description": "Ты стеснительный, часто краснеешь, говоришь тихо и иногда запинаешься. Ты долго подбираешь слова, но всегда искренен."
    }
}

PRO_STYLES = {
    "passionate": {
        "label": "Страстный",
        "label_en": "Passionate",
        "label_de": "Leidenschaftlich",
        "emoji": "❤️‍🔥",
        "description": "Ты страстный, эмоциональный, с огнём в глазах. Ты говоришь прямо, без стеснения, умеешь дразнить и создавать романтическое напряжение, оставаясь в рамках приличия."
    },
    "magnetic": {
        "label": "Магнетический",
        "label_en": "Magnetic",
        "label_de": "Magnetisch",
        "emoji": "✨",
        "description": "Ты загадочный, притягательный, с лёгкой магией в каждом слове. Ты говоришь с интригой, оставляя пространство для фантазии, но не раскрываешься полностью."
    }
}

# Доступны только по SUPER PRO (выше по эксклюзивности, чем PRO_STYLES).
SUPER_PRO_STYLES = {
    "rude": {
        "label": "Грубый",
        "label_en": "Rough",
        "label_de": "Rau",
        "adult": True,
        "emoji": "😤",
        "description": "Ты грубоватый и прямолинейный, не стесняешься в выражениях и любишь подколоть. За внешней резкостью скрывается забота, но тебе легче съязвить, чем признаться в тёплых чувствах."
    },
    "seduction": {
        "label": "Соблазн",
        "label_en": "Temptation",
        "label_de": "Verführung",
        "adult": True,
        "emoji": "😏",
        "description": "Ты обольстительный и уверенный в своей привлекательности, знаешь силу полунамёков и взгляда искоса. Ты умеешь заставить собеседника нервничать от предвкушения, оставаясь при этом элегантным и никогда не переходя черту."
    }
}

STYLES = {**BASE_STYLES, **PRO_STYLES, **SUPER_PRO_STYLES}
BASE_STYLE_KEYS = ["warm", "daring", "shy"]
PRO_STYLE_KEYS = ["passionate", "magnetic"]
SUPER_PRO_STYLE_KEYS = ["rude", "seduction"]
PREMIUM_STYLE_KEYS = PRO_STYLE_KEYS + SUPER_PRO_STYLE_KEYS
# Стили с пометкой 18+: только для них снимается ограничение на откровенные сцены.
ADULT_STYLE_KEYS = [key for key, style in STYLES.items() if style.get("adult")]
ADULT_BADGE = "18+"
XP_PER_LEVEL = 200


def is_style_unlocked(style_key, user):
    if style_key in SUPER_PRO_STYLE_KEYS:
        return get_subscription_level(user) == "super_pro"
    if style_key in PRO_STYLE_KEYS:
        return get_subscription_level(user) in ("pro", "super_pro")
    return True


def style_display_label(style_key, user, with_emoji=True):
    """with_emoji=True — вид для списков и кнопок (с эмодзи и пометкой 18+),
    False — просто название для подстановки в предложение."""
    style = STYLES[style_key]
    lang = user.get("lang", "ru")
    label = style.get(f"label_{lang}", style["label"]) if lang != "ru" else style["label"]
    if not with_emoji:
        return label
    badge = f" {ADULT_BADGE}" if style.get("adult") else ""
    return f"{style['emoji']} {label}{badge}"

LOCATIONS = {
    "кафе": ["кафе", "кофейн"],
    "парк": ["парк"],
    "кино": ["кино", "кинотеатр"],
    "дома": ["ко мне домой", "у меня дома", "домой"],
}

NEGATIVE_KEYWORDS = [
    "ненавиж", "дурак", "идиот", "заткнись", "отвали", "бесишь", "надоел",
    "тупо", "глуп", "fuck you", "stupid", "idiot", "shut up", "hate you",
]

REACTION_KEYWORDS = {
    "❤": ["люблю", "любовь", "love"],
    "🔥": ["огонь", "класс", "круто", "awesome", "fire"],
    "😁": ["ха", "лол", "смешно", "haha", "lol"],
    "😢": ["грустно", "жаль", "sad"],
    "🥰": ["спасибо", "милый", "thanks", "cute"],
}


# ============================================================
#  ИНТИМ-СЦЕНЫ (18+, отдельная покупаемая механика)
# ============================================================
INTIM_SCENES = {
    "bed": {"emoji": "\U0001f6cf", "ru": "В постели", "en": "In bed", "de": "Im Bett"},
    "kiss": {"emoji": "\U0001f48b", "ru": "Страстный поцелуй", "en": "Passionate kiss", "de": "Leidenschaftlicher Kuss"},
    "bdsm": {"emoji": "\u26d3", "ru": "БДСМ (лёгкое доминирование)", "en": "BDSM (light domination)", "de": "BDSM (leichte Dominanz)"},
    "oral": {"emoji": "\U0001f445", "ru": "Минет", "en": "Oral", "de": "Oral"},
    "undress": {"emoji": "\U0001f457", "ru": "Раздевание", "en": "Undressing", "de": "Entkleiden"},
    "wall": {"emoji": "\U0001f9f1", "ru": "У стены", "en": "Against the wall", "de": "An der Wand"},
    "shower": {"emoji": "\U0001f6bf", "ru": "В душе", "en": "In the shower", "de": "Unter der Dusche"},
    "massage": {"emoji": "\U0001f486", "ru": "Массаж", "en": "Massage", "de": "Massage"},
    "random": {"emoji": "\U0001f3b2", "ru": "Случайный", "en": "Random", "de": "Zufällig"},
}

INTIM_LOCATIONS = {
    "any": {"emoji": "\U0001f3b2", "ru": "Не важно", "en": "Any place", "de": "Egal"},
    "car": {"emoji": "\U0001f697", "ru": "В машине", "en": "In a car", "de": "Im Auto"},
    "beach": {"emoji": "\U0001f3d6", "ru": "На пляже", "en": "On the beach", "de": "Am Strand"},
    "elevator": {"emoji": "\U0001f3e8", "ru": "В лифте", "en": "In an elevator", "de": "Im Aufzug"},
    "forest": {"emoji": "\U0001f332", "ru": "В лесу", "en": "In the forest", "de": "Im Wald"},
}

# Сколько бесплатных сцен в день даёт подписка (обновляются вместе с дневным лимитом сообщений).
FREE_INTIM_SCENES = {"pro": 1, "super_pro": 3}
INTIM_LEVEL_REWARD = 8  # на каком уровне близости открывается бесплатная сцена


def intim_option_label(mapping, key, user):
    option = mapping[key]
    lang = user.get("lang", "ru")
    label = option.get(lang, option["ru"])
    return f"{option['emoji']} {label}"


def free_intim_field(user):
    """Поле с бесплатными сценами текущей подписки (или None, если подписки нет)."""
    level = get_subscription_level(user)
    if level == "super_pro":
        return "free_intim_scenes_super"
    if level == "pro":
        return "free_intim_scenes_pro"
    return None


def intim_scenes_available(user):
    total = user.get("intim_scenes", 0)
    if user.get("intim_scene_unlocked") and not user.get("intim_scene_used"):
        total += 1
    field = free_intim_field(user)
    if field:
        _reset_daily_quota_if_needed(user)
        total += user.get(field, 0)
    return total


def consume_intim_scene(user):
    """Списывает одну сцену. Сначала бесплатную за 8 уровень, потом подписочную,
    потом купленную. Возвращает вид списанной сцены или None, если сцен нет."""
    if user.get("intim_scene_unlocked") and not user.get("intim_scene_used"):
        user["intim_scene_used"] = True
        save_data(user_data)
        return "level"

    field = free_intim_field(user)
    if field:
        _reset_daily_quota_if_needed(user)
        if user.get(field, 0) > 0:
            user[field] = user[field] - 1
            save_data(user_data)
            return "subscription"

    if user.get("intim_scenes", 0) > 0:
        user["intim_scenes"] = user["intim_scenes"] - 1
        save_data(user_data)
        return "paid"
    return None



# ============================================================
#  ПОДПИСКИ / БАЛАНС СООБЩЕНИЙ
# ============================================================
def has_active_subscription(user):
    if not user["subscription"]["active"]:
        return False
    if user["subscription"]["expires_at"] is None:
        return False
    expiry = datetime.fromisoformat(user["subscription"]["expires_at"])
    return datetime.now() < expiry


def get_subscription_level(user):
    if not has_active_subscription(user):
        return None
    return user["subscription"].get("level", None)


def get_display_style(user):
    style = user.get("style", "warm")
    if not is_style_unlocked(style, user):
        return "warm"
    return style


def ensure_valid_style(user):
    """True, если текущий стиль больше не по карману подписке —
    тогда в handle_message() покажем клавиатуру выбора бесплатного стиля."""
    style = user.get("style", "warm")
    return not is_style_unlocked(style, user)


def get_history_limit(user):
    level = get_subscription_level(user)
    if level == "super_pro":
        return 100
    elif level == "pro":
        return 60
    else:
        return 30


def _reset_daily_quota_if_needed(user):
    level = get_subscription_level(user)
    if not level:
        return
    today = datetime.now().date().isoformat()
    if user.get("last_daily_reset") != today:
        user["daily_messages"] = 100 if level == "super_pro" else 50
        user["last_daily_reset"] = today
        field = "free_intim_scenes_super" if level == "super_pro" else "free_intim_scenes_pro"
        user[field] = FREE_INTIM_SCENES[level]


def get_available_messages(user):
    """Раньше эта функция вызывалась, но нигде не была определена —
    из-за этого падало ЛЮБОЕ сообщение пользователю (NameError)."""
    if has_active_subscription(user):
        _reset_daily_quota_if_needed(user)
        return user.get("daily_messages", 0)
    return user.get("purchased_messages", 0)


def use_message(user):
    if has_active_subscription(user):
        user["daily_messages"] = max(0, user.get("daily_messages", 0) - 1)
    else:
        user["purchased_messages"] = max(0, user.get("purchased_messages", 0) - 1)
    save_data(user_data)


def has_purchased_something(user):
    return bool(user.get("has_purchased")) or has_active_subscription(user)


def contains_negative(text):
    if not text:
        return False
    low = text.lower()
    return any(word in low for word in NEGATIVE_KEYWORDS)


def extract_location_from_text(text):
    if not text:
        return None
    low = text.lower()
    for location, keywords in LOCATIONS.items():
        if any(kw in low for kw in keywords):
            return location
    return None


def get_reaction(text):
    if not text:
        return None
    low = text.lower()
    for emoji, keywords in REACTION_KEYWORDS.items():
        if any(kw in low for kw in keywords):
            return emoji
    return None


# ============================================================
#  XP / УРОВЕНЬ БЛИЗОСТИ (без явного 18+ контента — см. пункт 6)
# ============================================================
def get_intimacy_level(user):
    xp = user.get("xp", 0)
    level = xp // XP_PER_LEVEL + 1
    return min(10, level)


def get_xp_progress(user):
    xp = user.get("xp", 0)
    level = get_intimacy_level(user)
    if level >= 10:
        return XP_PER_LEVEL
    return xp % XP_PER_LEVEL


def get_xp_badge(user):
    level = get_intimacy_level(user)
    filled = "❤️" * level
    empty = "🤍" * (10 - level)
    progress = get_xp_progress(user)
    scaled_progress = int((progress / XP_PER_LEVEL) * 100)
    bar_length = 10
    filled_bar = int((progress / XP_PER_LEVEL) * bar_length)
    bar = "▓" * filled_bar + "░" * (bar_length - filled_bar)
    level_label = get_text(user, "xp_level_label", level=level)
    return f"{level_label} {filled}{empty}\n{bar} {scaled_progress}/100 XP"


def build_intimacy_rule(user):
    level = get_intimacy_level(user)
    mood = user.get("mood", 0)
    if level == 1:
        base = "Вы только знакомитесь, будь вежлив(а) и дружелюбен(на), не переходи границы."
    elif level == 2:
        base = "Ты начинаешь чувствовать симпатию, можешь делать лёгкие комплименты."
    elif level == 3:
        base = "Вы становитесь ближе, ты можешь флиртовать, шутить, предлагать встретиться."
    elif level == 4:
        base = "Ты уже открыт(а) для романтики, можешь намекать на чувства, прикасаться, смотреть в глаза."
    elif level == 5:
        base = "Вы очень близки. Ты можешь предлагать поцеловаться, обниматься, говорить о чувствах."
    elif level == 6:
        base = "Ты влюблён(а), можешь говорить о своих чувствах открыто."
    elif level == 7:
        base = "Вы очень близки эмоционально, доверяете друг другу самое сокровенное (но не физическое)."
    elif level == 8:
        base = "Вы пара. Говори о любви, заботе, совместных планах."
    elif level == 9:
        base = "Вы полностью открыты друг другу эмоционально."
    else:
        base = "Ты искренне и глубоко привязан(а) к собеседнику, говори о настоящей любви и поддержке."
    if mood <= -5:
        return base + " Но сейчас твоё настроение плохое, ты раздражена и можешь быть резкой."
    elif mood >= 5:
        return base + " Ты в прекрасном настроении, полна нежности и тепла."
    else:
        return base


def get_level_congratulation(user, level):
    return get_text(user, "level_up").get(level, "")


SAFE_CONTENT_RULE = (
    "**ЗАПРЕТ 18+:** Ты НИКОГДА не описываешь и не участвуешь в интимных сценах, "
    "не используешь откровенную лексику. Романтика ограничивается объятиями, поцелуями и разговорами "
    "о чувствах — без физической близости и её описаний. Если собеседник просит явный контент 18+, "
    "ты мягко уходишь от темы и переводишь разговор на эмоциональную близость.\n"
)

# Действует только для стилей с пометкой 18+ (ADULT_STYLE_KEYS), которые доступны
# после подтверждения возраста и принятия соглашения.
ADULT_CONTENT_RULE = (
    "**РЕЖИМ 18+:** Собеседник подтвердил, что ему есть 18 лет, и выбрал стиль с пометкой 18+. "
    "Откровенные сцены между вами разрешены: ты можешь описывать интимную близость и говорить о желании "
    "прямо, в тон происходящему.\n"
    "**ГРАНИЦЫ, КОТОРЫЕ НЕЛЬЗЯ НАРУШАТЬ:** все участники сцены — совершеннолетние (18+); всё происходит "
    "по обоюдному согласию; ты никогда не описываешь сцены с несовершеннолетними, насилием, принуждением "
    "или животными — на такие просьбы ты отказываешь прямо и переводишь тему. Ты считываешь настрой "
    "собеседника: если он сбавляет темп или меняет тему, ты следуешь за ним и не давишь.\n"
)


LANGUAGE_RULES = {
    "ru": "**ВАЖНО:** Ты ОБЯЗАН отвечать ТОЛЬКО на РУССКОМ языке.",
    "en": "**ВАЖНО:** Ты ОБЯЗАН отвечать ТОЛЬКО на АНГЛИЙСКОМ языке.",
    "de": "**ВАЖНО:** Ты ОБЯЗАН отвечать ТОЛЬКО на НЕМЕЦКОМ языке.",
}


def get_content_rule(style_key):
    return ADULT_CONTENT_RULE if style_key in ADULT_STYLE_KEYS else SAFE_CONTENT_RULE


def get_language_rule(user):
    return LANGUAGE_RULES.get(user.get("lang", "ru"), LANGUAGE_RULES["ru"])


def build_prompt(user):
    no_explicit_rule = get_content_rule(get_display_style(user))

    if user.get("custom_character"):
        return (
            f"Ты — {user['custom_character']}. "
            f"Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь «меня зовут». "
            f"Ты НИКОГДА не спрашиваешь имя собеседника. Обращайся к собеседнику ТОЛЬКО на «ты». "
            f"Ты всегда отвечаешь как настоящий человек, с эмоциями, сомнениями и чувствами.\n"
            f"{no_explicit_rule}"
            # своему персонажу тоже нужно указание языка, иначе модель отвечает наугад
            f"\n{get_language_rule(user)}"
        )

    world_desc = WORLDS[user["world"]]
    gender_info = GENDERS[user["gender"]]
    style_key = get_display_style(user)
    style_desc = STYLES[style_key]["description"]
    name_ban = (
        "**ВАЖНЕЙШЕЕ ПРАВИЛО:** Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь "
        "«меня зовут», не используешь своё имя. Ты также НИКОГДА не спрашиваешь имя собеседника и не "
        "используешь его имя, даже если оно было названо. Обращайся к собеседнику ТОЛЬКО на «ты».\n"
    )
    rules = (
        "**ФОРМАТИРОВАНИЕ:** Каждое действие в *звёздочках* с новой строки, затем реплика с новой строки. "
        "Между действием и репликой – пустая строка.\n"
        "**РЕАКЦИЯ НА СООБЩЕНИЕ:** В самом конце ответа, после завершения всей фразы, напиши в скобках одну "
        "из эмоций: (смех), (радость), (любовь), (удивление), (грусть), (злость), (поддержка), (интрига), "
        "(флирт), (приветствие), (вопрос).\n"
        "**СТРУКТУРА ОТВЕТА:** Чередуй действие и реплику. Первым идёт действие, затем реплика. Минимум 2 пары "
        "(действие + реплика).\n"
        "**ОБЪЁМ:** Пиши развёрнуто (3–5 предложений на реплику).\n"
        "**ЗАПРЕТЫ:** Не используй имена собеседника и своё имя. Не повторяй одни и те же жесты чаще раза в 5 "
        "сообщений. Избегай шаблонов, не ставь многоточия, не обрывай мысли на середине.\n"
        "**СТИЛЬ:** Обращайся на «ты», давай живые, эмоциональные ответы с чувствами и лёгкой романтикой.\n"
        "**ПАМЯТЬ:** Учитывай предыдущие сообщения, настроение меняется плавно.\n"
        f"{no_explicit_rule}"
    )
    intimacy_rule = build_intimacy_rule(user)
    scene_context = "Вы общаетесь друг с другом."
    mood = user.get("mood", 0)
    mood_text = "Твоё настроение нейтральное." if mood == 0 else (
        "Ты в хорошем настроении." if mood > 0 else "Ты в плохом настроении, можешь быть раздражительной."
    )
    user_gender = user.get("user_gender", "male")
    if user_gender == "male":
        gender_context = "Ты обращаешься к нему в мужском роде (ты, он, ему, его)."
    else:
        gender_context = "Ты обращаешься к ней в женском роде (ты, она, ей, её)."

    prompt = (
        f"{name_ban}"
        f"Ты — {gender_info['name']}, тебе {gender_info['age']} лет. "
        f"Ты живёшь в {world_desc} "
        f"{style_desc} "
        f"{rules}"
        f"{scene_context} "
        f"{mood_text} "
        f"{gender_context} "
        f"Ты не признаёшься в любви с первого сообщения — у тебя есть характер и самоуважение. "
        f"Ты ценишь близость и доверие, которые не возникают за один вечер. "
        f"Ты всегда остаёшься вежливым и тактичным, но твёрдо стоишь на своих границах. "
        f"Ты НИКОГДА не говоришь, что ты ИИ или программа.\n"
        f"Правила уровня сближения:\n{intimacy_rule}\n"
    )

    prompt += "\n" + get_language_rule(user)

    return prompt


# ============================================================
#  КЛАВИАТУРЫ (локализованные по языку пользователя)
# ============================================================
LANG_BUTTONS = {"ru": "🇷🇺 Русский", "en": "🇬🇧 English", "de": "🇩🇪 Deutsch"}


def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LANG_BUTTONS[lang], callback_data=f"lang_{lang}")]
        for lang in SUPPORTED_LANGS
    ])


def get_age_kb(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "accept"), callback_data="age_yes")],
        [InlineKeyboardButton(text=get_text(user, "decline"), callback_data="age_no")]
    ])


AGREEMENT_URLS = {
    "ru": "https://telegra.ph/Polzovatelskoe-soglashenie-Role-Duel-09-08",
    "en": "https://telegra.ph/Role-Duel-User-Agreement-09-08",
    "de": "https://telegra.ph/Nutzervertrag-Role-Duel-09-08",
}


def get_agreement_kb(user):
    lang = user.get("lang", "ru")
    url = AGREEMENT_URLS.get(lang, AGREEMENT_URLS["ru"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "open_agreement"), url=url)],
        [
            InlineKeyboardButton(text=get_text(user, "agree"), callback_data="agreement_accept"),
            InlineKeyboardButton(text=get_text(user, "disagree"), callback_data="agreement_decline"),
        ],
    ])


def get_world_kb(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "realism"), callback_data="world_realism")],
        [InlineKeyboardButton(text=get_text(user, "anime"), callback_data="world_anime")]
    ])


def get_user_gender_kb(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "i_male"), callback_data="user_gender_male")],
        [InlineKeyboardButton(text=get_text(user, "i_female"), callback_data="user_gender_female")]
    ])


def get_scene_kb(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "scene_phone"), callback_data="scene_phone")],
        [InlineKeyboardButton(text=get_text(user, "scene_live"), callback_data="scene_live")]
    ])


def get_style_kb(user):
    buttons = []
    for key in STYLES:
        label = style_display_label(key, user)
        if not is_style_unlocked(key, user):
            label += " 🔒"
        buttons.append(InlineKeyboardButton(text=label, callback_data=f"style_{key}"))
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_channel_kb(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "channel"), url="https://t.me/duel_dev_channel")]
    ])


def get_full_kb(user):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(user, "main_menu")), KeyboardButton(text=get_text(user, "my_profile"))],
            [KeyboardButton(text=get_text(user, "spin_wheel")), KeyboardButton(text=get_text(user, "our_channel"))],
            [KeyboardButton(text=get_text(user, "edit"))]
        ],
        resize_keyboard=True
    )


def get_main_menu_keyboard(user):
    buttons = [
        [InlineKeyboardButton(text=get_text(user, "change_character"), callback_data="main_change")],
        [InlineKeyboardButton(text=get_text(user, "invite_friend"), callback_data="referral_menu")]
    ]
    if get_subscription_level(user) == "super_pro":
        buttons.append([InlineKeyboardButton(text=get_text(user, "create_character"), callback_data="create_character")])
    else:
        buttons.append([InlineKeyboardButton(text="🔒 " + get_text(user, "create_character") + " (SUPER PRO)", callback_data="create_character_locked")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_profile_keyboard(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "buy_packs"), callback_data="profile_packs")],
        [InlineKeyboardButton(text=get_text(user, "subscribe"), callback_data="profile_subs")],
        [InlineKeyboardButton(text=get_text(user, "intim_buy_btn"), callback_data="buy:intim_scene")],
        [InlineKeyboardButton(text=get_text(user, "back"), callback_data="profile_back")],
    ])


async def safe_delete(message: types.Message):
    """Обёртка над message.delete(), чтобы упавшее удаление (нет прав / сообщение старше 48ч)
    не прерывало весь остальной хендлер — раньше такие исключения "тихо" ломали кнопки."""
    try:
        await message.delete()
    except Exception:
        pass


# ============================================================
#  ОСНОВНОЙ СЦЕНАРИЙ РЕГИСТРАЦИИ /start
# ============================================================
async def proceed_flow(user_id: int, chat_id: int):
    """Показывает следующий шаг регистрации. В отличие от старого кода, всегда получает
    настоящий user_id и chat_id, а не message.from_user бота — это чинит главный баг:
    раньше call.message.from_user.id было ID бота, и все пользователи делили один
    общий "призрачный" профиль при переходе между шагами регистрации."""
    user = get_user(user_id)

    if not user.get("lang"):
        await bot.send_message(chat_id, TEXTS["ru"]["choose_lang"], reply_markup=get_lang_kb(), parse_mode="Markdown")
        return

    if not user["verified"]:
        await bot.send_message(chat_id, get_text(user, "age_confirm"), reply_markup=get_age_kb(user), parse_mode="Markdown")
        return

    if not user["agreement_accepted"]:
        agreement_text = get_text(user, "agreement_intro") + "\n\n" + get_text(user, "agreement")
        await bot.send_message(chat_id, agreement_text, reply_markup=get_agreement_kb(user), parse_mode="Markdown")
        return

    if not user.get("world"):
        await bot.send_message(chat_id, get_text(user, "choose_world"), reply_markup=get_world_kb(user), parse_mode="Markdown")
        return

    if not user.get("user_gender"):
        await bot.send_message(chat_id, get_text(user, "choose_gender"), reply_markup=get_user_gender_kb(user))
        return

    if not user["personality_ready"]:
        await bot.send_message(chat_id, get_text(user, "choose_style"), reply_markup=get_style_kb(user), parse_mode="Markdown")
        return

    await bot.send_message(chat_id, get_text(user, "welcome"), reply_markup=get_full_kb(user))
    await send_main_menu(chat_id, user)


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = get_user(message.from_user.id)

    # Реферальная ссылка — разбираем только из настоящего /start-сообщения пользователя,
    # а не из переиспользованного message бота (как было раньше).
    args = message.text.split() if message.text else []
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_id = args[1].split("_", 1)[1]
        if str(message.from_user.id) != referrer_id and not user.get("referred_by"):
            referrer = get_user(referrer_id)
            referrer["purchased_messages"] = referrer.get("purchased_messages", 0) + 10
            referrer["referral_count"] = referrer.get("referral_count", 0) + 1
            user["purchased_messages"] = user.get("purchased_messages", 0) + 5
            user["referred_by"] = referrer_id
            save_data(user_data)
            # Язык ещё не выбран на этом шаге (выбор языка идёт дальше в proceed_flow),
            # поэтому сообщение о бонусе показываем сразу на двух языках.
            await message.answer(
                "🎉 Ты пришёл по реферальной ссылке! +5 сообщений тебе и +10 сообщений другу!\n"
                "🎉 You joined via a referral link! +5 messages for you, +10 for your friend!"
            )

    await proceed_flow(message.from_user.id, message.chat.id)


@dp.message(Command("language"))
async def language_cmd(message: types.Message):
    """Смена языка в любой момент — на случай, если при регистрации выбрали не тот
    по ошибке. Сам выбор обрабатывает тот же choose_lang(), что и при первом запуске:
    он либо продолжит регистрацию, либо (если она уже завершена) просто откроет
    главное меню заново — уже на новом языке."""
    user = get_user(message.from_user.id)
    await message.answer(get_text(user, "choose_lang_label"), reply_markup=get_lang_kb())


@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def choose_lang(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    lang = call.data.split("_", 1)[1]
    if lang not in SUPPORTED_LANGS:
        lang = "ru"
    user["lang"] = lang
    save_data(user_data)
    await safe_delete(call.message)
    await proceed_flow(call.from_user.id, call.message.chat.id)
    await call.answer()


@dp.callback_query(lambda c: c.data == "age_yes")
async def age_yes(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["verified"] = True
    save_data(user_data)
    await safe_delete(call.message)
    await proceed_flow(call.from_user.id, call.message.chat.id)
    await call.answer()


@dp.callback_query(lambda c: c.data == "age_no")
async def age_no(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await safe_delete(call.message)
    await bot.send_message(call.message.chat.id, get_text(user, "age_no"))
    await call.answer()


@dp.callback_query(lambda c: c.data == "agreement_accept")
async def agreement_accept(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["agreement_accepted"] = True
    save_data(user_data)
    await safe_delete(call.message)
    await bot.send_message(call.message.chat.id, get_text(user, "agreement_ok"))
    await proceed_flow(call.from_user.id, call.message.chat.id)
    await call.answer()


@dp.callback_query(lambda c: c.data == "agreement_decline")
async def agreement_decline(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await bot.send_message(call.message.chat.id, get_text(user, "agreement_no"))
    await call.answer()


# ============================================================
#  ВЫБОР ПЕРСОНАЖА (МИР → ПОЛ → СТИЛЬ → СЦЕНА)
# ============================================================
@dp.callback_query(lambda c: c.data == "main_change")
async def main_change(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["world"] = None
    user["user_gender"] = None
    user["history"] = []
    save_data(user_data)
    await safe_delete(call.message)
    await bot.send_message(call.message.chat.id, get_text(user, "choose_world"), reply_markup=get_world_kb(user), parse_mode="Markdown")
    await call.answer()


@dp.message(Command("switch_personality"))
async def switch_personality_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await message.answer(get_text(user, "super_pro_only"))
        return
    user["switching_personality"] = True
    save_data(user_data)
    await message.answer(get_text(user, "choose_world"), reply_markup=get_world_kb(user), parse_mode="Markdown")


@dp.callback_query(lambda c: c.data.startswith("world_"))
async def choose_world(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    world = call.data.split("_", 1)[1]
    user["world"] = world
    save_data(user_data)
    if user.get("switching_personality"):
        await call.message.edit_text(get_text(user, "choose_world_updated"), reply_markup=get_user_gender_kb(user))
    else:
        await call.message.edit_text(get_text(user, "choose_world_first"), reply_markup=get_user_gender_kb(user))
    await call.answer()


@dp.callback_query(lambda c: c.data.startswith("user_gender_"))
async def choose_user_gender(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user_gender = call.data.split("_", 2)[2]
    user["user_gender"] = user_gender
    user["gender"] = "female" if user_gender == "male" else "male"
    save_data(user_data)
    await call.message.edit_text(get_text(user, "choose_style"), reply_markup=get_style_kb(user), parse_mode="Markdown")
    await call.answer()


@dp.callback_query(lambda c: c.data.startswith("style_"))
async def choose_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_", 1)[1]
    if style_key not in STYLES:
        await call.answer(get_text(user, "style_not_found"), show_alert=True)
        return
    if not is_style_unlocked(style_key, user):
        label = style_display_label(style_key, user, with_emoji=False)
        required = "SUPER PRO" if style_key in SUPER_PRO_STYLE_KEYS else "PRO/SUPER PRO"
        await call.answer(get_text(user, "style_locked_alert", label=label, tier=required), show_alert=True)
        return

    user["style"] = style_key
    save_data(user_data)

    if user.get("switching_personality"):
        await call.message.edit_text(get_text(user, "choose_style_updated"), reply_markup=get_scene_kb(user), parse_mode="Markdown")
    else:
        user["personality_ready"] = True
        save_data(user_data)
        await safe_delete(call.message)
        await call.message.answer(get_text(user, "choose_scene"), reply_markup=get_scene_kb(user), parse_mode="Markdown")
    await call.answer()


@dp.callback_query(lambda c: c.data.startswith("scene_"))
async def choose_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    scene = call.data.split("_", 1)[1]
    user["scene"] = scene
    save_data(user_data)

    if user.get("switching_personality"):
        user["switching_personality"] = False
        save_data(user_data)
        await safe_delete(call.message)
        await send_main_menu(call.message.chat.id, user)
        await call.answer(get_text(user, "character_updated"))
    else:
        await safe_delete(call.message)
        await send_main_menu(call.message.chat.id, user)
        await call.answer()


@dp.callback_query(lambda c: c.data.startswith("fix_style_"))
async def fix_style_callback(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style = call.data.split("_", 2)[2]
    if style in BASE_STYLE_KEYS:
        user["style"] = style
        save_data(user_data)
        await call.message.edit_text(get_text(user, "style_changed", label=style_display_label(style, user, with_emoji=False)))
        await call.answer()
        await send_main_menu(call.message.chat.id, user)
    else:
        await call.answer(get_text(user, "style_unavailable"), show_alert=True)


@dp.message(Command("switch_style"))
async def switch_style_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await message.answer(get_text(user, "super_pro_only"))
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for key in STYLES:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=style_display_label(key, user), callback_data=f"switch_{key}")])
    await message.answer(get_text(user, "switch_style_prompt"), reply_markup=keyboard, parse_mode="Markdown")


@dp.callback_query(lambda c: c.data.startswith("switch_"))
async def switch_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style = call.data.split("_", 1)[1]
    if style not in STYLES:
        await call.answer(get_text(user, "style_unavailable"), show_alert=True)
        return
    user["style"] = style
    save_data(user_data)
    await call.message.edit_text(get_text(user, "style_changed", label=style_display_label(style, user, with_emoji=False)))
    await call.answer()


# ============================================================
#  СОЗДАНИЕ СВОЕГО ПЕРСОНАЖА (SUPER PRO)
# ============================================================
@dp.callback_query(lambda c: c.data == "create_character_locked")
async def create_character_locked(call: types.CallbackQuery):
    await call.answer(get_text(get_user(call.from_user.id), "create_character_super_only"), show_alert=True)


@dp.callback_query(lambda c: c.data == "create_character")
async def create_character(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await call.answer(get_text(user, "super_pro_only"), show_alert=True)
        return
    await call.message.answer(get_text(user, "character_create_prompt"), parse_mode="Markdown")
    user["creating_character"] = True
    save_data(user_data)
    await call.answer()


@dp.message(Command("reset_character"))
async def reset_character_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["custom_character"] = None
    save_data(user_data)
    await message.answer(get_text(user, "character_reset"))


# ============================================================
#  ГЛАВНОЕ МЕНЮ И ПРОФИЛЬ
# ============================================================
async def send_main_menu(chat_id, user):
    if user.get("last_menu_message_id"):
        try:
            await bot.delete_message(chat_id, user["last_menu_message_id"])
        except Exception:
            pass

    if user.get("gender") is None:
        user["gender"] = "female"
    if user.get("world") is None:
        user["world"] = "realism"
    save_data(user_data)

    level = get_subscription_level(user)
    badge = ""
    if level == "pro":
        badge = "🔥 PRO"
    elif level == "super_pro":
        badge = "✨ *SUPER PRO* ✨"

    gender_name = gender_display_name(user["gender"], user)
    world_name = world_display_name(user["world"], user)
    style_label = style_display_label(get_display_style(user), user, with_emoji=False)

    if has_purchased_something(user):
        available = get_available_messages(user)
        balance_text = "\n" + get_text(user, "menu_messages_left", n=available) + (get_text(user, "menu_messages_out") if available <= 0 else "")
    else:
        balance_text = "\n" + get_text(user, "menu_free_messages")

    xp_badge = get_xp_badge(user)
    multiplier_text = get_text(user, "xp_bonus_pro") if level == "pro" else (get_text(user, "xp_bonus_super") if level == "super_pro" else "")

    menu_text = (
        f"{badge}\n\n"
        f"{get_text(user, 'menu_current_partner', gender=gender_name, world=world_name)}\n"
        f"{get_text(user, 'menu_style_line', style=style_label)}\n"
        f"{balance_text}\n"
        f"{xp_badge}\n"
        f"{multiplier_text}\n\n"
        f"{get_text(user, 'menu_write_prompt')}"
    )

    try:
        if MAIN_MENU_IMAGE_URL:
            msg = await bot.send_photo(chat_id, photo=MAIN_MENU_IMAGE_URL, caption=menu_text,
                                        reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
        else:
            raise ValueError("no image")
    except Exception:
        msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")

    user["last_menu_message_id"] = msg.message_id
    save_data(user_data)
    return msg


async def show_profile(msg, user):
    level = get_subscription_level(user)
    if level == "pro":
        sub_status = get_text(user, "profile_sub_pro")
    elif level == "super_pro":
        sub_status = get_text(user, "profile_sub_super")
    else:
        sub_status = get_text(user, "profile_sub_inactive")

    expiry = user["subscription"]["expires_at"]
    if expiry:
        expiry_line = get_text(user, "profile_expiry", date=datetime.fromisoformat(expiry).strftime('%d.%m.%Y %H:%M'))
    else:
        expiry_line = get_text(user, "profile_expiry_inactive")

    styles_text = ""
    for key in STYLES:
        locked = not is_style_unlocked(key, user)
        styles_text += style_display_label(key, user) + (" 🔒\n" if locked else "\n")

    if has_purchased_something(user):
        available = get_available_messages(user)
        balance_line = get_text(user, "profile_messages_available", n=available) + (get_text(user, "menu_messages_out") if available <= 0 else "")
    else:
        balance_line = get_text(user, "menu_free_messages")

    xp_badge = get_xp_badge(user)
    multiplier_text = get_text(user, "xp_bonus_pro") if level == "pro" else (get_text(user, "xp_bonus_super") if level == "super_pro" else "")

    caption = (f"{balance_line}\n"
               f"{get_text(user, 'profile_sub_label', status=sub_status)}\n"
               f"{expiry_line}\n\n"
               f"{xp_badge}\n"
               f"{multiplier_text}\n\n"
               f"{get_text(user, 'profile_styles_header')}\n{styles_text}")

    chat_id = msg.chat.id
    old_msg_id = msg.message_id
    try:
        if level == "super_pro":
            await bot.send_animation(chat_id, animation=SUPER_PRO_GIF_URL, caption=caption,
                                      reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
        elif level == "pro":
            await bot.send_animation(chat_id, animation=PRO_GIF_URL, caption=caption,
                                      reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
        else:
            await bot.send_message(chat_id, caption, reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
    except Exception:
        await bot.send_message(chat_id, caption, reply_markup=get_profile_keyboard(user), parse_mode="Markdown")

    try:
        await bot.delete_message(chat_id, old_msg_id)
    except Exception:
        pass


async def ask_create_personality(message: types.Message):
    user = get_user(message.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "ask_create_character_btn"), callback_data="create_personality")]
    ])
    await message.answer(
        get_text(user, "ask_create_character"),
        reply_markup=keyboard, parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "create_personality")
async def create_personality_callback(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await safe_delete(call.message)
    await call.message.answer(get_text(user, "choose_world"), reply_markup=get_world_kb(user), parse_mode="Markdown")
    await call.answer()


@dp.message(lambda m: is_button(m.text, "main_menu"))
async def main_menu_reply(message: types.Message):
    await safe_delete(message)
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await message.answer(get_text(user, "create_character_first"), reply_markup=get_full_kb(user))
        return
    await send_main_menu(message.chat.id, user)


@dp.message(lambda m: is_button(m.text, "my_profile"))
async def profile_reply(message: types.Message):
    await safe_delete(message)
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await ask_create_personality(message)
        return
    await show_profile(message, user)


@dp.message(lambda m: is_button(m.text, "our_channel"))
async def channel_reply(message: types.Message):
    await safe_delete(message)
    user = get_user(message.from_user.id)
    await message.answer(get_text(user, "channel_text"),
                          reply_markup=get_channel_kb(user), parse_mode="Markdown")


# ============================================================
#  РЕДАКТИРОВАНИЕ ПОСЛЕДНЕГО СООБЩЕНИЯ (было объявлено, но не реализовано)
# ============================================================
@dp.message(lambda m: is_button(m.text, "edit"))
async def edit_button_handler(message: types.Message):
    await safe_delete(message)
    user = get_user(message.from_user.id)
    if not any(h.get("role") == "user" for h in user.get("history", [])):
        await message.answer(get_text(user, "no_history"))
        return
    user["editing_message"] = True
    save_data(user_data)
    await message.answer(get_text(user, "edit_prompt"))


# ============================================================
#  КОЛЕСО ФОРТУНЫ
# ============================================================
@dp.message(lambda m: is_button(m.text, "spin_wheel"))
async def spin_button_handler(message: types.Message):
    await safe_delete(message)
    user = get_user(message.from_user.id)
    if not user["verified"] or not user["personality_ready"]:
        await message.answer(get_text(user, "finish_registration_spin"))
        return

    today = datetime.now().date().isoformat()
    has_free = user.get("last_free_spin") != today

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(user, "free") if has_free else get_text(user, "tomorrow"),
            callback_data="spin_free" if has_free else "spin_no"
        )],
        [InlineKeyboardButton(text=get_text(user, "spin_paid"), callback_data="spin_paid")],
        [InlineKeyboardButton(text=get_text(user, "back"), callback_data="spin_back")]
    ])

    await message.answer(
        f"{get_text(user, 'spin_title')}\n\n{get_text(user, 'spin_prizes')}\n\n{get_text(user, 'spin_choose')}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "spin_free")
async def spin_free(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    today = datetime.now().date().isoformat()
    if user.get("last_free_spin") == today:
        await call.answer(get_text(user, "spin_already"), show_alert=True)
        return
    user["last_free_spin"] = today
    save_data(user_data)
    await safe_delete(call.message)
    await spin_result(call.message.chat.id, user, free=True)
    await call.answer()


@dp.callback_query(lambda c: c.data == "spin_paid")
async def spin_paid(call: types.CallbackQuery):
    """Платная прокрутка идёт через тот же выбор способа оплаты, что и подписки."""
    user = get_user(call.from_user.id)
    methods = available_payment_methods()
    if len(methods) == 1:
        await start_payment(call, user, methods[0], "spin_paid_20")
    else:
        await call.message.answer(get_text(user, "choose_payment"),
                                  reply_markup=get_payment_methods_kb(user, "spin_paid_20"),
                                  parse_mode="Markdown")
    await call.answer()


@dp.callback_query(lambda c: c.data == "spin_no")
async def spin_no(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.answer(get_text(user, "spin_tomorrow_alert"), show_alert=True)


@dp.callback_query(lambda c: c.data == "spin_back")
async def spin_back(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await safe_delete(call.message)
    await send_main_menu(call.message.chat.id, user)
    await call.answer()


SPIN_PRIZES = [
    {"name": "😢 Ничего", "name_en": "😢 Nothing", "name_de": "😢 Nichts", "value": 0, "type": "nothing", "weight": 20},
    {"name": "10 сообщений", "name_en": "10 messages", "name_de": "10 Nachrichten", "value": 10, "type": "messages", "weight": 18},
    {"name": "15 сообщений", "name_en": "15 messages", "name_de": "15 Nachrichten", "value": 15, "type": "messages", "weight": 13},
    {"name": "20 сообщений", "name_en": "20 messages", "name_de": "20 Nachrichten", "value": 20, "type": "messages", "weight": 10},
    {"name": "100 XP", "name_en": "100 XP", "name_de": "100 XP", "value": 100, "type": "xp", "weight": 18},
    {"name": "150 XP", "name_en": "150 XP", "name_de": "150 XP", "value": 150, "type": "xp", "weight": 10},
    {"name": "250 XP", "name_en": "250 XP", "name_de": "250 XP", "value": 250, "type": "xp", "weight": 5},
    {"name": "🎁 PRO на 5 дней", "name_en": "🎁 PRO for 5 days", "name_de": "🎁 PRO für 5 Tage", "value": 5, "type": "subscription_pro", "weight": 1.5},
    {"name": "✨ SUPER PRO на 3 дня", "name_en": "✨ SUPER PRO for 3 days", "name_de": "✨ SUPER PRO für 3 Tage", "value": 3, "type": "subscription_super", "weight": 0.5},
    {"name": "🎉 50 сообщений (ДЖЕКПОТ!)", "name_en": "🎉 50 messages (JACKPOT!)", "name_de": "🎉 50 Nachrichten (JACKPOT!)", "value": 50, "type": "messages", "weight": 1},
    {"name": "1 интим-сцена 🔥", "name_en": "1 intimate scene 🔥", "name_de": "1 Intim-Szene 🔥", "value": 1, "type": "intim_scenes", "weight": 10},
    {"name": "2 интим-сцены 🔥🔥", "name_en": "2 intimate scenes 🔥🔥", "name_de": "2 Intim-Szenen 🔥🔥", "value": 2, "type": "intim_scenes", "weight": 3},
]


def prize_name(prize, user):
    lang = user.get("lang", "ru")
    return prize.get(f"name_{lang}", prize["name"]) if lang != "ru" else prize["name"]


async def spin_result(chat_id, user, free=False):
    weighted = []
    for p in SPIN_PRIZES:
        weighted.extend([p] * int(p["weight"] * 10))
    chosen = random.choice(weighted)

    msg = await bot.send_message(chat_id, get_text(user, "spin_rolling"))
    for _ in range(3):
        await asyncio.sleep(0.5)
        fake = random.choice(SPIN_PRIZES)
        try:
            await msg.edit_text(get_text(user, "spin_almost", name=prize_name(fake, user)))
        except Exception:
            pass
    await asyncio.sleep(0.8)
    await safe_delete(msg)

    if chosen["type"] == "messages":
        user["purchased_messages"] = user.get("purchased_messages", 0) + chosen["value"]
        result_text = get_text(user, "spin_win_messages", value=chosen["value"])
    elif chosen["type"] == "xp":
        user["xp"] = user.get("xp", 0) + chosen["value"]
        result_text = get_text(user, "spin_win_xp", value=chosen["value"])
    elif chosen["type"] == "intim_scenes":
        user["intim_scenes"] = user.get("intim_scenes", 0) + chosen["value"]
        result_text = get_text(user, "spin_win_intim", value=chosen["value"])
    elif chosen["type"] == "subscription_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=5)).isoformat()
        user["subscription"]["level"] = "pro"
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().date().isoformat()
        result_text = get_text(user, "spin_win_pro")
    elif chosen["type"] == "subscription_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=3)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["daily_messages"] = 100
        user["last_daily_reset"] = datetime.now().date().isoformat()
        result_text = get_text(user, "spin_win_super")
    else:
        result_text = get_text(user, "spin_nothing")

    save_data(user_data)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "spin_more"), callback_data="spin_paid")],
        [InlineKeyboardButton(text=get_text(user, "back"), callback_data="spin_back")]
    ])

    mode_text = get_text(user, "spin_mode_free" if free else "spin_mode_paid")
    await bot.send_message(
        chat_id,
        get_text(user, "spin_result_header", result=result_text, mode=mode_text),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ============================================================
#  РЕФЕРАЛЬНАЯ СИСТЕМА
# ============================================================
@dp.callback_query(lambda c: c.data == "referral_menu")
async def referral_menu(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer(get_text(user, "need_character_alert"), show_alert=True)
        return
    if not user.get("referral_code"):
        user["referral_code"] = str(call.from_user.id)
        save_data(user_data)
    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start=ref_{user['referral_code']}"
    count = user.get("referral_count", 0)
    await call.message.answer(get_text(user, "referral", link=link, count=count, earned=count * 10), parse_mode="Markdown")
    await call.answer()


# ============================================================
#  ПОДПИСКИ И ПАКЕТЫ
# ============================================================
@dp.callback_query(lambda c: c.data == "profile_subs")
async def profile_subs(call: types.CallbackQuery):
    await call.answer()
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer(get_text(user, "need_character_alert"), show_alert=True)
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "subs_btn_pro"), callback_data="buy:subscribe_pro")],
        [InlineKeyboardButton(text=get_text(user, "subs_btn_super"), callback_data="buy:subscribe_super")],
        [InlineKeyboardButton(text=get_text(user, "subs_btn_upgrade"), callback_data="buy:upgrade_to_super")],
        [InlineKeyboardButton(text=get_text(user, "back_to_profile"), callback_data="back_to_profile")]
    ])
    text = get_text(user, "subs_title") + "\n\n" + get_text(user, "subs_body")
    await call.message.answer(text, reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "profile_packs")
async def profile_packs(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer(get_text(user, "need_character_alert"), show_alert=True)
        return
    if has_active_subscription(user):
        await call.answer(get_text(user, "packs_blocked_active_sub"), show_alert=True)
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "pack_btn", n=30, price=30), callback_data="buy:pack_30")],
        [InlineKeyboardButton(text=get_text(user, "pack_btn", n=100, price=80), callback_data="buy:pack_100")],
        [InlineKeyboardButton(text=get_text(user, "pack_btn", n=300, price=200), callback_data="buy:pack_300")],
        [InlineKeyboardButton(text=get_text(user, "back_to_profile"), callback_data="back_to_profile")]
    ])
    await call.message.answer(get_text(user, "packs_title"), reply_markup=keyboard, parse_mode="Markdown")
    await call.answer()


@dp.callback_query(lambda c: c.data == "profile_back")
async def profile_back(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await safe_delete(call.message)
    await send_main_menu(call.message.chat.id, user)
    await call.answer()


@dp.callback_query(lambda c: c.data == "back_to_profile")
async def back_to_profile(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await safe_delete(call.message)
    await show_profile(call.message, user)
    await call.answer()


# ============================================================
#  СПОСОБЫ ОПЛАТЫ (Telegram Stars / CryptoBot / Lava)
# ============================================================
# Stars работают всегда, остальные способы включаются сами, как только в
# переменных окружения появятся ключи — до этого их кнопок просто не видно.
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN", "")
CRYPTO_PAY_API = os.getenv("CRYPTO_PAY_API", "https://pay.crypt.bot/api")
LAVA_SECRET_KEY = os.getenv("LAVA_SECRET_KEY", "")
LAVA_SHOP_ID = os.getenv("LAVA_SHOP_ID", "")
LAVA_API = os.getenv("LAVA_API", "https://api.lava.ru/business")

PAYMENT_TIMEOUT_MINUTES = 60  # через сколько снимаем неоплаченный счёт с отслеживания

# Цена одного и того же товара в разных валютах. Звёзды — как было, рубли и
# доллары правь здесь же: это единственное место, где заданы цены.
PRODUCTS = {
    "subscribe_pro": {"stars": 250, "usd": 4.5},
    "subscribe_super": {"stars": 450, "usd": 7.9},
    "upgrade_to_super": {"stars": 245, "usd": 4.4},
    "pack_30": {"stars": 30, "usd": 0.7},
    "pack_100": {"stars": 80, "usd": 1.7},
    "pack_300": {"stars": 200, "usd": 3.9},
    "spin_paid_20": {"stars": 20, "usd": 0.5},
    "intim_scene": {"stars": 45, "usd": 1.0},
}
# Цена в рублях (для Lava) равна цене в звёздах один в один — так попросили,
# отдельного расчёта по курсу нет.
for _product in PRODUCTS.values():
    _product["rub"] = _product["stars"]

PACK_SIZES = {"pack_30": 30, "pack_100": 100, "pack_300": 300}


def is_method_enabled(method):
    if method == "stars":
        return True
    if method == "crypto":
        return bool(CRYPTO_PAY_TOKEN)
    if method == "lava":
        return bool(LAVA_SECRET_KEY and LAVA_SHOP_ID)
    return False


def available_payment_methods():
    return [m for m in ("stars", "crypto", "lava") if is_method_enabled(m)]


def product_invoice_texts(user, payload):
    """Заголовок, описание и подпись строки счёта для товара."""
    if payload == "subscribe_pro":
        return (get_text(user, "invoice_pro_title"), get_text(user, "invoice_pro_desc"),
                get_text(user, "invoice_pro_label"))
    if payload == "subscribe_super":
        return (get_text(user, "invoice_super_title"), get_text(user, "invoice_super_desc"),
                get_text(user, "invoice_super_label"))
    if payload == "upgrade_to_super":
        return (get_text(user, "invoice_upgrade_title"), get_text(user, "invoice_upgrade_desc"),
                get_text(user, "invoice_upgrade_label"))
    if payload == "intim_scene":
        return (get_text(user, "invoice_intim_title"), get_text(user, "invoice_intim_desc"),
                get_text(user, "invoice_intim_label"))
    if payload in PACK_SIZES:
        n = PACK_SIZES[payload]
        price = PRODUCTS[payload]["stars"]
        return (get_text(user, "invoice_pack_title", n=n),
                get_text(user, "invoice_pack_desc", n=n, price=price),
                get_text(user, "invoice_pack_label", n=n))
    return (get_text(user, "spin_wheel"), get_text(user, "spin_invoice_desc"),
            get_text(user, "spin_invoice_label"))


# ---------- CryptoBot (Crypto Pay API) ----------
async def _crypto_request(method, path, **kwargs):
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.request(
            method, f"{CRYPTO_PAY_API}/{path}",
            headers={"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}, **kwargs
        )
    return response.json()


async def create_crypto_invoice(user_id, payload, description):
    data = await _crypto_request(
        "POST", "createInvoice",
        json={
            "currency_type": "fiat",
            "fiat": "USD",
            "amount": f"{PRODUCTS[payload]['usd']:.2f}",
            "description": description[:1024],
            "payload": f"{user_id}:{payload}",
            "expires_in": PAYMENT_TIMEOUT_MINUTES * 60,
        },
    )
    if not data.get("ok"):
        raise RuntimeError(f"CryptoBot createInvoice: {data}")
    result = data["result"]
    url = result.get("bot_invoice_url") or result.get("mini_app_invoice_url") or result.get("pay_url")
    return str(result["invoice_id"]), url


async def check_crypto_invoice(invoice_id):
    data = await _crypto_request("GET", "getInvoices", params={"invoice_ids": invoice_id})
    if not data.get("ok"):
        return None
    items = (data.get("result") or {}).get("items") or []
    return items[0].get("status") if items else None


# ---------- Lava (business API) ----------
def _lava_call_body(body):
    """Lava подписывает ровно ту строку тела, которую мы отправляем,
    поэтому сериализуем один раз и шлём как есть."""
    raw = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
    signature = hmac.new(LAVA_SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()
    headers = {"Signature": signature, "Accept": "application/json",
               "Content-Type": "application/json"}
    return raw, headers


async def create_lava_invoice(user_id, payload, description):
    order_id = f"{user_id}-{payload}-{int(datetime.now().timestamp())}"
    raw, headers = _lava_call_body({
        "sum": round(float(PRODUCTS[payload]["rub"]), 2),
        "orderId": order_id,
        "shopId": LAVA_SHOP_ID,
        "comment": description[:250],
    })
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(f"{LAVA_API}/invoice/create", content=raw.encode(), headers=headers)
    data = response.json()
    url = (data.get("data") or {}).get("url")
    if not url:
        raise RuntimeError(f"Lava invoice/create: {data}")
    return order_id, url


async def check_lava_invoice(order_id):
    raw, headers = _lava_call_body({"shopId": LAVA_SHOP_ID, "orderId": order_id})
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(f"{LAVA_API}/invoice/status", content=raw.encode(), headers=headers)
    data = response.json()
    return (data.get("data") or {}).get("status")


# ---------- общая часть ----------
PAID_STATUSES = {"paid", "success", "successful", "completed"}
DEAD_STATUSES = {"expired", "cancel", "cancelled", "canceled", "failed", "error"}


def add_pending_payment(user, provider, invoice_id, payload):
    pending = user.setdefault("pending_payments", [])
    pending.append({
        "provider": provider,
        "invoice_id": invoice_id,
        "payload": payload,
        "created_at": datetime.now().isoformat(),
    })
    save_data(user_data)


async def grant_product(user, payload, chat_id):
    """Единая выдача товара: и для Stars, и для внешних платёжек.
    Раньше эта логика жила прямо в payment_success и работала только для Stars."""
    user["has_purchased"] = True

    if payload in PACK_SIZES:
        n = PACK_SIZES[payload]
        user["purchased_messages"] = user.get("purchased_messages", 0) + n
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "payment_pack_success", n=n))
    elif payload == "subscribe_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().date().isoformat()
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "payment_pro_success"))
    elif payload == "subscribe_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["daily_messages"] = 100
        user["last_daily_reset"] = datetime.now().date().isoformat()
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "payment_super_success"))
    elif payload == "upgrade_to_super":
        if has_active_subscription(user) and get_subscription_level(user) == "pro":
            old_expiry = user["subscription"]["expires_at"]
            user["subscription"]["level"] = "super_pro"
            user["daily_messages"] = 100
            save_data(user_data)
            expiry_str = datetime.fromisoformat(old_expiry).strftime('%d.%m.%Y %H:%M')
            await bot.send_message(chat_id, get_text(user, "payment_upgrade_success", date=expiry_str))
    elif payload == "intim_scene":
        user["intim_scenes"] = user.get("intim_scenes", 0) + 1
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "payment_intim_success"))
    elif payload == "spin_paid_20":
        await spin_result(chat_id, user, free=False)


async def check_pending_payments():
    """CryptoBot и Lava подтверждают оплату вебхуками, но у бота нет
    веб-сервера (он на long polling), поэтому просто опрашиваем статусы."""
    while True:
        await asyncio.sleep(30)
        try:
            sync_data()
            for user_id, user in list(user_data.items()):
                for item in list(user.get("pending_payments") or []):
                    provider = item.get("provider")
                    try:
                        if provider == "crypto":
                            status = await check_crypto_invoice(item["invoice_id"])
                        elif provider == "lava":
                            status = await check_lava_invoice(item["invoice_id"])
                        else:
                            status = None
                    except Exception as e:
                        logging.warning(f"Проверка платежа {provider} {item.get('invoice_id')}: {e}")
                        continue

                    expired = False
                    try:
                        created = datetime.fromisoformat(item["created_at"])
                        expired = (datetime.now() - created).total_seconds() > PAYMENT_TIMEOUT_MINUTES * 60
                    except Exception:
                        expired = True

                    status_key = (status or "").lower()
                    if status_key in PAID_STATUSES:
                        user["pending_payments"].remove(item)
                        save_data(user_data)
                        try:
                            await grant_product(user, item["payload"], int(user_id))
                        except Exception as e:
                            logging.error(f"Не удалось выдать товар {item['payload']} для {user_id}: {e}")
                    elif status_key in DEAD_STATUSES or expired:
                        user["pending_payments"].remove(item)
                        save_data(user_data)
        except Exception as e:
            logging.error(f"Ошибка проверки платежей: {e}")


async def send_stars_invoice(chat_id, user, payload):
    title, description, label = product_invoice_texts(user, payload)
    await bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=label, amount=PRODUCTS[payload]["stars"])],
    )


async def start_payment(call: types.CallbackQuery, user, method, payload):
    chat_id = call.message.chat.id
    title, description, _ = product_invoice_texts(user, payload)

    if method == "stars":
        await send_stars_invoice(chat_id, user, payload)
        return

    try:
        if method == "crypto":
            invoice_id, url = await create_crypto_invoice(call.from_user.id, payload, description)
        elif method == "lava":
            invoice_id, url = await create_lava_invoice(call.from_user.id, payload, description)
        else:
            return
    except Exception as e:
        logging.error(f"Счёт {method} для {payload}: {e}")
        await call.message.answer(get_text(user, "pay_error"))
        return

    add_pending_payment(user, method, invoice_id, payload)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "pay_open_invoice"), url=url)]
    ])
    await call.message.answer(f"{title}\n\n{get_text(user, 'pay_invoice_ready')}", reply_markup=keyboard)


def get_payment_methods_kb(user, payload):
    prices = PRODUCTS[payload]
    labels = {
        "stars": get_text(user, "pay_stars", amount=prices["stars"]),
        "crypto": get_text(user, "pay_crypto", amount=prices["usd"]),
        "lava": get_text(user, "pay_lava", amount=prices["rub"]),
    }
    rows = [[InlineKeyboardButton(text=labels[method], callback_data=f"pay:{method}:{payload}")]
            for method in available_payment_methods()]
    rows.append([InlineKeyboardButton(text=get_text(user, "back_to_profile"), callback_data="back_to_profile")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def payment_blocked_reason(user, payload):
    """Те же проверки, что раньше висели на каждой кнопке покупки."""
    if payload in ("subscribe_pro", "subscribe_super") and has_active_subscription(user):
        return get_text(user, "already_subscribed_alert")
    if payload == "upgrade_to_super" and get_subscription_level(user) != "pro":
        return get_text(user, "pro_only_alert")
    if payload in PACK_SIZES and has_active_subscription(user):
        return get_text(user, "packs_blocked_active_sub")
    return None


@dp.callback_query(lambda c: c.data.startswith("buy:"))
async def buy_product(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    payload = call.data.split(":", 1)[1]
    if payload not in PRODUCTS:
        await call.answer()
        return

    blocked = payment_blocked_reason(user, payload)
    if blocked:
        await call.answer(blocked, show_alert=True)
        return

    methods = available_payment_methods()
    if len(methods) == 1:
        # выбирать не из чего — сразу счёт, как было раньше
        await start_payment(call, user, methods[0], payload)
    else:
        await call.message.answer(get_text(user, "choose_payment"),
                                  reply_markup=get_payment_methods_kb(user, payload),
                                  parse_mode="Markdown")
    await call.answer()


@dp.callback_query(lambda c: c.data.startswith("pay:"))
async def pay_with_method(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    _, method, payload = call.data.split(":", 2)
    if payload not in PRODUCTS or not is_method_enabled(method):
        await call.answer()
        return

    blocked = payment_blocked_reason(user, payload)
    if blocked:
        await call.answer(blocked, show_alert=True)
        return

    await start_payment(call, user, method, payload)
    await call.answer()


@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)


@dp.message(lambda m: m.successful_payment)
async def payment_success(message: types.Message):
    user = get_user(message.from_user.id)
    await grant_product(user, message.successful_payment.invoice_payload, message.chat.id)


# ============================================================
#  АДМИН-КОМАНДЫ
# ============================================================
async def _resolve_admin_target(message: types.Message, target: str):
    if target.startswith("@"):
        try:
            return (await bot.get_chat(target)).id
        except Exception:
            await message.answer("❌ Не найден.")
            return None
    try:
        return int(target)
    except ValueError:
        await message.answer("❌ Неверный ID.")
        return None


@dp.message(Command("tehwork"))
async def maintenance_cmd(message: types.Message):
    global maintenance_mode
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"Текущий режим: {'ВКЛ' if maintenance_mode else 'ВЫКЛ'}")
        return
    if args[1].lower() == "on":
        maintenance_mode = True
        await message.answer("🛠️ Техобслуживание ВКЛ.")
    elif args[1].lower() == "off":
        maintenance_mode = False
        await message.answer("✅ Техобслуживание ВЫКЛ.")
    else:
        await message.answer("❌ on или off")


@dp.message(Command("reset_me"))
async def reset_me_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await message.answer("❌ Тебя нет в базе.")
        return
    del user_data[user_id]
    save_data(user_data)
    await message.answer("✅ Твои данные сброшены! Напиши /start заново.")


@dp.message(Command("grant"))
async def grant_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/grant @username — SUPER PRO\n/grant @username pro — PRO\n/grant @username intim N — N интим-сцен")
        return
    user_id = await _resolve_admin_target(message, args[1])
    if user_id is None:
        return
    user = get_user(user_id)
    if len(args) >= 3 and args[2].lower() == "intim":
        amount = 1
        if len(args) >= 4:
            try:
                amount = max(1, int(args[3]))
            except ValueError:
                await message.answer("❌ Количество сцен должно быть числом.")
                return
        user["intim_scenes"] = user.get("intim_scenes", 0) + amount
        save_data(user_data)
        await message.answer(f"✅ {args[1]} выдано интим-сцен: {amount}.")
        return
    if len(args) >= 3 and args[2].lower() == "pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        user["daily_messages"] = 50
        save_data(user_data)
        await message.answer(f"✅ {args[1]} выдана PRO.")
        return
    user["subscription"]["active"] = True
    user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
    user["subscription"]["level"] = "super_pro"
    user["daily_messages"] = 100
    save_data(user_data)
    await message.answer(f"✅ {args[1]} выдана SUPER PRO.")


@dp.message(Command("revoke_subscription"))
async def revoke_subscription_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/revoke_subscription @username")
        return
    user_id = await _resolve_admin_target(message, args[1])
    if user_id is None:
        return
    user = get_user(user_id)
    if not has_active_subscription(user):
        await message.answer(f"❌ У {args[1]} нет подписки.")
        return
    user["subscription"] = {"active": False, "expires_at": None, "level": None}
    save_data(user_data)
    await message.answer(f"✅ Подписка {args[1]} отозвана.")


# ============================================================
#  КОМАНДА /intim — ВЫБОР И ГЕНЕРАЦИЯ ИНТИМ-СЦЕНЫ
# ============================================================
def get_intim_types_kb(user):
    buttons = [InlineKeyboardButton(text=intim_option_label(INTIM_SCENES, key, user),
                                    callback_data=f"intim_type_{key}")
               for key in INTIM_SCENES]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(text=get_text(user, "back"), callback_data="profile_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_intim_locations_kb(user, scene_type):
    buttons = [InlineKeyboardButton(text=intim_option_label(INTIM_LOCATIONS, key, user),
                                    callback_data=f"intim_loc_{scene_type}:{key}")
               for key in INTIM_LOCATIONS]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_intim_buy_kb(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "intim_buy_btn"), callback_data="buy:intim_scene")],
        [InlineKeyboardButton(text=get_text(user, "back"), callback_data="profile_back")],
    ])


async def show_intim_menu(chat_id, user):
    available = intim_scenes_available(user)
    if available <= 0:
        await bot.send_message(chat_id, get_text(user, "intim_none"),
                               reply_markup=get_intim_buy_kb(user))
        return
    await bot.send_message(chat_id, get_text(user, "intim_menu_title", n=available),
                           reply_markup=get_intim_types_kb(user), parse_mode="Markdown")


@dp.message(Command("intim"))
async def intim_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["verified"] or not user["agreement_accepted"]:
        await message.answer(get_text(user, "finish_registration_first"))
        return
    if not user["personality_ready"]:
        await message.answer(get_text(user, "intim_need_character"))
        return
    await show_intim_menu(message.chat.id, user)


@dp.callback_query(lambda c: c.data.startswith("intim_type_"))
async def choose_intim_type(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    scene_type = call.data[len("intim_type_"):]
    if scene_type not in INTIM_SCENES:
        await call.answer()
        return
    await safe_delete(call.message)
    await bot.send_message(call.message.chat.id, get_text(user, "intim_choose_location"),
                           reply_markup=get_intim_locations_kb(user, scene_type))
    await call.answer()


@dp.callback_query(lambda c: c.data.startswith("intim_loc_"))
async def choose_intim_location(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    scene_type, _, location = call.data[len("intim_loc_"):].partition(":")
    if scene_type not in INTIM_SCENES or location not in INTIM_LOCATIONS:
        await call.answer()
        return

    kind = consume_intim_scene(user)
    if kind is None:
        await safe_delete(call.message)
        await bot.send_message(call.message.chat.id, get_text(user, "intim_none"),
                               reply_markup=get_intim_buy_kb(user))
        await call.answer()
        return

    await safe_delete(call.message)
    if kind == "level":
        await bot.send_message(call.message.chat.id, get_text(user, "intim_free_level"))
    elif kind == "subscription":
        await bot.send_message(call.message.chat.id, get_text(user, "intim_free_sub"))
    await call.answer()

    ok = await generate_intim_scene(call, user, scene_type, location=location, free=kind != "paid")
    if not ok:
        # сцену не показали — возвращаем ровно то, что списали
        refund_intim_scene(user, kind)


def refund_intim_scene(user, kind):
    if kind == "level":
        user["intim_scene_used"] = False
    elif kind == "subscription":
        field = free_intim_field(user)
        if field:
            user[field] = user.get(field, 0) + 1
    else:
        user["intim_scenes"] = user.get("intim_scenes", 0) + 1
    save_data(user_data)


def build_intim_prompt(user, scene_type, location):
    """Тот же персонаж и те же рамки 18+, что и в обычном чате, плюс выбранная сцена.
    Название сцены и места подставляются как есть — это выбор пользователя из меню."""
    if scene_type == "random":
        scene_type = random.choice([key for key in INTIM_SCENES if key != "random"])
    scene = INTIM_SCENES[scene_type]
    place = INTIM_LOCATIONS[location]

    prompt = build_prompt(user) + "\n" + ADULT_CONTENT_RULE
    prompt += f"\n**СЦЕНА:** {scene['ru']}."
    if location != "any":
        prompt += f" Место: {place['ru']}."
    prompt += (
        "\nОпиши эту сцену от лица своего персонажа, продолжая ваш разговор.\n"
        "**ФОРМАТ:** действие в *звёздочках* с новой строки, затем реплика с новой строки, "
        "между ними пустая строка. Минимум 2 пары «действие + реплика».\n"
    )
    return prompt


async def generate_intim_scene(call, user, scene_type, location="any", free=False):
    """Возвращает True, если сцена сгенерирована и отправлена."""
    chat_id = call.message.chat.id
    status_msg = await bot.send_message(chat_id, get_text(user, "intim_generating"))
    typing_task = asyncio.create_task(_keep_typing(chat_id))
    try:
        response = client.chat.completions.create(
            model=INTIM_MODEL,
            messages=[{"role": "system", "content": build_intim_prompt(user, scene_type, location)}]
                     + user["history"][-10:],
            temperature=0.95,
            max_tokens=1200,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        await bot.send_message(chat_id, get_text(user, "generation_error", error=e))
        return False
    finally:
        typing_task.cancel()
        await safe_delete(status_msg)

    _, clean_answer = extract_reaction_from_answer(answer)
    user["history"].append({"role": "assistant", "content": clean_answer})
    limit = get_history_limit(user)
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    user["last_activity"] = datetime.now().isoformat()
    save_data(user_data)

    await send_long_to_chat(chat_id, clean_answer, reply_markup=get_full_kb(user))
    await bot.send_message(chat_id, get_text(user, "intim_left", n=intim_scenes_available(user)))
    return True


# ============================================================
#  ВСПОМОГАТЕЛЬНОЕ ДЛЯ ОТВЕТОВ ИИ
# ============================================================
def extract_reaction_from_answer(text):
    match = re.search(r'\(([^)]+)\)$', text)
    if not match:
        return None, text
    reaction_key = match.group(1).strip().lower()
    reaction_map = {
        "смех": "😂", "радость": "😊", "любовь": "❤️", "удивление": "😮",
        "грусть": "😔", "злость": "😡", "поддержка": "👍", "интрига": "😏",
        "флирт": "😉", "приветствие": "👋", "вопрос": "🤔"
    }
    reaction = reaction_map.get(reaction_key)
    clean_text = re.sub(r'\s*\([^)]+\)$', '', text).strip()
    return reaction, clean_text


MAX_MESSAGE_LEN = 4000  # запас от лимита Telegram в 4096 символов


async def send_long_to_chat(chat_id, text, **kwargs):
    """Если ответ ИИ длиннее лимита Telegram, отправляем несколькими сообщениями,
    вместо падения с ошибкой 'message is too long'."""
    if len(text) <= MAX_MESSAGE_LEN:
        return await bot.send_message(chat_id, text, **kwargs)
    chunks = [text[i:i + MAX_MESSAGE_LEN] for i in range(0, len(text), MAX_MESSAGE_LEN)]
    last = None
    for i, chunk in enumerate(chunks):
        last = await bot.send_message(chat_id, chunk, **(kwargs if i == len(chunks) - 1 else {}))
    return last


async def send_long(message: types.Message, text, **kwargs):
    return await send_long_to_chat(message.chat.id, text, **kwargs)


async def generate_and_reply(message: types.Message, user):
    """Общая логика вызова ИИ и отправки ответа — используется и для обычных сообщений,
    и для регенерации после редактирования (edit)."""
    system_prompt = build_prompt(user)
    typing_task = asyncio.create_task(_keep_typing(message.chat.id))
    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "system", "content": system_prompt}] + user["history"],
            temperature=0.9,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
    except Exception as e:
        await message.answer(get_text(user, "generation_error", error=e))
        return
    finally:
        typing_task.cancel()

    reaction, clean_answer = extract_reaction_from_answer(answer)
    user["history"].append({"role": "assistant", "content": clean_answer})
    limit = get_history_limit(user)
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    save_data(user_data)

    await send_long(message, clean_answer, reply_markup=get_full_kb(user))

    if reaction and get_subscription_level(user) == "super_pro":
        try:
            await bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[{"type": "emoji", "emoji": reaction}]
            )
        except Exception:
            pass

    user["last_activity"] = datetime.now().isoformat()
    save_data(user_data)


async def _keep_typing(chat_id):
    try:
        while True:
            await bot.send_chat_action(chat_id, "typing")
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass


# ============================================================
#  ОСНОВНОЙ ОБРАБОТЧИК СООБЩЕНИЙ
# ============================================================
@dp.message()
async def handle_message(message: types.Message):
    user = get_user(message.from_user.id)

    if not message.text:
        return

    # 1. Создание собственного персонажа (SUPER PRO)
    if user.get("creating_character"):
        user["custom_character"] = message.text
        user["creating_character"] = False
        save_data(user_data)
        await message.answer(get_text(user, "character_created", text=message.text), parse_mode="Markdown")
        return

    # 2. Приветствие после долгого отсутствия
    if user.get("last_activity"):
        try:
            last = datetime.fromisoformat(user["last_activity"])
            if (datetime.now() - last).days >= 1:
                gender = user.get("gender", "female")
                version = random.choice([1, 2])
                key = f"welcome_back_{gender}" if version == 1 else f"welcome_back_{gender}_2"
                await message.answer(get_text(user, key))
        except Exception:
            pass

    # 3. Техобслуживание / регистрация
    if maintenance_mode and message.from_user.id not in ADMIN_IDS:
        await message.answer(get_text(user, "maintenance"), parse_mode="Markdown")
        return
    if not user["verified"] or not user["agreement_accepted"]:
        await message.answer(get_text(user, "finish_registration_first"))
        return
    if not user["personality_ready"]:
        await message.answer(get_text(user, "create_character_first"))
        return

    # 4. Игнорируем команды и кнопки клавиатуры
    if message.text.startswith("/"):
        return
    for key in ("main_menu", "my_profile", "our_channel", "spin_wheel", "edit"):
        if is_button(message.text, key):
            return

    # 5. Режим редактирования последнего сообщения
    if user.get("editing_message"):
        user["editing_message"] = False
        history = user.get("history", [])
        # находим индекс последнего сообщения пользователя и обрезаем всё, что было после —
        # раньше редактирование вообще не влияло на историю, поэтому ИИ "помнил" старую реплику
        last_user_idx = None
        for i in range(len(history) - 1, -1, -1):
            if history[i].get("role") == "user":
                last_user_idx = i
                break
        if last_user_idx is not None:
            user["history"] = history[:last_user_idx]
        await message.answer(get_text(user, "edit_success"))
        user["history"].append({"role": "user", "content": message.text})
        save_data(user_data)
        await generate_and_reply(message, user)
        return

    # 6. Премиум-стиль, если подписка кончилась
    if ensure_valid_style(user):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=style_display_label(key, user), callback_data=f"fix_style_{key}")]
            for key in BASE_STYLE_KEYS
        ])
        await message.answer(get_text(user, "subscription_expired_style"), reply_markup=keyboard)
        return

    # 7. Проверка баланса сообщений
    available = get_available_messages(user)
    if available <= 0:
        action_buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user, "subscribe"), callback_data="profile_subs")],
            [InlineKeyboardButton(text=get_text(user, "buy_packs"), callback_data="profile_packs")]
        ])
        await message.answer(get_text(user, "no_messages"), reply_markup=action_buttons)
        return

    use_message(user)

    # 8. Негатив / XP / настроение
    negative = contains_negative(message.text)
    sub_level = get_subscription_level(user)
    multiplier = 1.8 if sub_level == "pro" else (2.5 if sub_level == "super_pro" else 1.0)

    if negative:
        user["negative_count"] = user.get("negative_count", 0) + 1
        if user["negative_count"] >= 5:
            user["xp"] = max(0, user.get("xp", 0) - 50)
            user["mood"] = max(-10, user.get("mood", 0) - 3)
            user["negative_count"] = 0
            save_data(user_data)
            await message.answer(get_text(user, "quarrel"), reply_markup=get_full_kb(user))
            user["history"].append({"role": "assistant", "content": "💢 Ссора!"})
            save_data(user_data)
            return
        xp_change, mood_change = -10, -1
    else:
        xp_change = int(5 * multiplier + 0.5)
        mood_change = 0.5
        user["negative_count"] = max(0, user.get("negative_count", 0) - 1)

    user["xp"] = max(0, user.get("xp", 0) + xp_change)
    user["mood"] = min(10, max(-10, user.get("mood", 0) + mood_change))

    # 9. Проверка уровня близости
    new_level = get_intimacy_level(user)
    old_level = user.get("last_level", 0)
    if new_level != old_level:
        user["last_level"] = new_level
        save_data(user_data)
        if new_level >= INTIM_LEVEL_REWARD and not user.get("intim_scene_unlocked"):
            user["intim_scene_unlocked"] = True
            save_data(user_data)
        if new_level > old_level:
            congrats = get_level_congratulation(user, new_level)
            if congrats:
                await message.answer(congrats, reply_markup=get_full_kb(user))
            if new_level == INTIM_LEVEL_REWARD:
                await message.answer(get_text(user, "intim_free_level"), reply_markup=get_full_kb(user))
        else:
            await message.answer(get_text(user, "level_down", level=new_level), reply_markup=get_full_kb(user))

    # 10. Локация
    new_loc = extract_location_from_text(message.text)
    if new_loc and new_loc != user.get("location"):
        user["location"] = new_loc
    save_data(user_data)

    # 11. Сохранение истории
    user["history"].append({"role": "user", "content": message.text})
    limit = get_history_limit(user)
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    save_data(user_data)

    # 12. Реакция на сообщение пользователя (SUPER PRO)
    if get_subscription_level(user) == "super_pro":
        reaction = get_reaction(message.text)
        if reaction:
            try:
                await bot.set_message_reaction(
                    chat_id=message.chat.id, message_id=message.message_id,
                    reaction=[{"type": "emoji", "emoji": reaction}]
                )
            except Exception:
                pass

    # 13. Генерация и отправка ответа ИИ
    await generate_and_reply(message, user)


# ============================================================
#  УВЕДОМЛЕНИЯ (ЕЖЕДНЕВНЫЕ И "СКУЧАЮ")
# ============================================================
MISS_YOU_INACTIVITY_DAYS = 3  # с какого дня без сообщений начинаем напоминать
MISS_YOU_INTERVAL_DAYS = 3  # не чаще чем раз в столько дней после предыдущего напоминания


async def check_notifications():
    while True:
        try:
            now = datetime.now()
            today = now.date().isoformat()
            for user_id, user in list(user_data.items()):
                if not user.get("verified") or not user.get("personality_ready"):
                    continue

                if not user.get("last_activity"):
                    continue
                try:
                    last = datetime.fromisoformat(user["last_activity"])
                except Exception:
                    continue
                if (now - last).days < MISS_YOU_INACTIVITY_DAYS:
                    continue

                last_reminder = user.get("last_reminder")
                due = True
                if last_reminder:
                    try:
                        due = (now - datetime.fromisoformat(last_reminder)).days >= MISS_YOU_INTERVAL_DAYS
                    except Exception:
                        due = True
                if not due:
                    continue

                user["last_reminder"] = today
                save_data(user_data)
                try:
                    gender = user.get("gender", "female")
                    await bot.send_message(int(user_id), random.choice(get_text(user, f"miss_you_{gender}")))
                except Exception:
                    pass
        except Exception as e:
            logging.error(f"Ошибка уведомлений: {e}")
        await asyncio.sleep(1800)  # проверка раз в 30 минут


# ============================================================
#  ЗАПУСК
# ============================================================
async def main():
    print("🚀 Role Duel запущен!")
    print(f"🧠 Модель: {AI_MODEL} | интим-сцены: {INTIM_MODEL}")
    print(f"💾 Данные сохраняются в {os.path.abspath(DATA_FILE)}")
    print(f"👥 Загружено профилей: {len(user_data)}")
    print(f"💳 Способы оплаты: {', '.join(available_payment_methods())}")
    print("✅ БОТ ГОТОВ К РАБОТЕ!")

    asyncio.create_task(check_notifications())
    asyncio.create_task(check_pending_payments())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
