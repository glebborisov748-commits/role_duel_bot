import asyncio
import hashlib
import hmac
import math
import os
import json
import logging
import random
import re
from datetime import datetime, timedelta
from urllib.parse import parse_qsl

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice,
    ReplyKeyboardMarkup, KeyboardButton, BotCommand, FSInputFile, WebAppInfo
)
from aiohttp import web
import httpx
from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError

# ============================================================
#  МНОГОЯЗЫЧНЫЙ СЛОВАРЬ (только RU + EN, см. пункт 7 задачи)
# ============================================================
TEXTS = {
    "ru": {
        "main_menu": "📋 Главное меню",
        "my_profile": "👤 Мой профиль",
        "spin_wheel": "🎰 Колесо фортуны",
        "our_channel": "📢 Наш канал",
        "edit": "✏️ Редактировать",
        "change_character": "🔄 Сменить персонажа",
        "invite_friend": "👥 Пригласить друга",
        "create_character": "🎭 Создать своего персонажа",
        "buy_bundles": "🎁 Купить бандл",
        "subscribe": "👑 Оформить подписку",
        "back": "🔙 Главное меню",
        "back_to_profile": "🔙 Назад",
        "accept": "✅ Мне есть 18 лет",
        "decline": "❌ Мне нет 18 лет",
        "agree": "✅ Принимаю",
        "disagree": "❌ Не принимаю",
        "open_agreement": "📜 Открыть соглашение",
        "realism": "🌍 Реализм",
        "anime": "🎌 Аниме",
        "i_male": "👨 Я парень",
        "i_female": "👩 Я девушка",
        "scene_phone": "📱 Переписка в телефоне",
        "scene_live": "👫 Реальная встреча",
        "channel": "📢 Перейти в канал",
        "free": "🎁 Бесплатно ({left}/{total})",
        "tomorrow": "⏳ Завтра",
        "spin_paid": "💎 Крутить за 15⭐",
        "spin_more": "💎 Крутить ещё за 15⭐",
        "welcome": "👋 Добро пожаловать!",
        "age_confirm": "🔞 **ВНИМАНИЕ!**\nЭтот бот предназначен для лиц старше 18 лет.\nПодтверди свой возраст:",
        "age_ok": "✅ Возраст подтверждён.",
        "age_no": "🚫 Доступ запрещён. Бот только для 18+.",
        "agreement_intro": "📜 Прежде чем продолжить, ознакомься с пользовательским соглашением и прими его:",
        "agreement_continue": "➡️ Продолжить",
        "agreement_decide": "📜 Теперь прими решение:",
        "agreement_ok": "✅ Соглашение принято!",
        "agreement_no": "❌ Без принятия соглашения бот не работает.",
        "choose_lang": "🌍 Выбери язык / Choose language:",
        "choose_gender": "👤 Выбери свой пол:",
        "choose_world": "🌍 Выбери мир:",
        "choose_world_updated": "🌍 Мир обновлён! Теперь выбери свой пол:",
        "choose_world_first": "🌍 Мир выбран! Теперь выбери свой пол:",
        "choose_style": "🎨 Теперь выбери стиль персонажа:",
        "choose_style_updated": "🎨 Стиль обновлён! Теперь выбери сцену для общения:",
        "choose_scene": "🎬 Теперь выбери сцену для общения:\n\n📱 Переписка в телефоне — классический формат.\n👫 Реальная встреча — живое общение лицом к лицу.",        "no_history": "❌ Пока нечего редактировать — напиши персонажу хотя бы одно сообщение.",
        "edit_prompt": "✏️ Пришли новый текст своего последнего сообщения — я забуду старую реплику и отвечу заново.",
        "edit_success": "✅ Сообщение заменено. Генерирую новый ответ...",
        "character_created": "✅ Персонаж создан!\n\nТеперь ты общаешься с:\n«{text}»\n\nЧтобы вернуться к обычному персонажу — /reset_character",
        "character_reset": "✅ Персонаж сброшен.",
        "help_title": "📖 Команды бота",
        "help_base": (
            "/start — регистрация / открыть главное меню\n"
            "/language — сменить язык\n"
            "/hot — горячая сцена с персонажем\n"
            "/feed — покормить персонажа\n"
            "/work — отправить персонажа на работу за баксы\n"
            "/reset_character — сбросить своего кастомного персонажа\n"
            "/switch_personality — сменить мир и пол без потери истории (SUPER PRO/ELITE)\n"
            "/switch_style — сменить стиль без потери истории (SUPER PRO/ELITE)"
        ),
        "help_hint": "📖 /help — список всех команд.",
        "character_create_prompt": "🎭 **Создай своего уникального персонажа!**\n\nОпиши любого персонажа — из аниме, фильмов, игр или придумай своего.\nНапиши его/её имя, характер, внешность, откуда он/она, любые детали.\n\n📝 *Пример:*\n«Эльфийка из мира Ведьмака — мудрая, сдержанная, с длинными серебряными волосами. Любит звёзды и долгие разговоры у костра.»\n\n✏️ Напиши описание прямо сейчас — и я запомню его!",
        "spin_title": "🎰 **Колесо фортуны**",
        "spin_prizes": "🔥 **Что можно выиграть:**\n• 100–250 XP\n• 20–150💵 баксов\n• 🔥 Горячие сцены\n• 2–4⚡ энергетика (редко)\n• 🎁 PRO на 5 дней (редко)\n• ✨ SUPER PRO на 3 дня (очень редко)",
        "spin_choose": "Выбери вариант:",
        "spin_nothing": "😢 Ничего... В следующий раз повезёт!",        "referral": "👥 **Твоя реферальная ссылка:**\n`{link}`\n\n🎁 За каждого друга, который зарегистрируется по ссылке, — **+30💵 баксов и +3⚡ энергетика** тебе, ему — **+15💵 баксов и +1⚡ энергетик**!\n\n📊 Приглашено друзей: **{count}**\n💵 Заработано баксов: **{earned_bucks}**\n⚡ Заработано энергетиков: **{earned_energizers}**",
        "choose_lang_label": "🌍 Выбери язык:",
        "welcome_back_female": "Ой, тебя так долго не было! Я уже успела соскучиться 🥺💕",
        "welcome_back_male": "Ой, тебя так долго не было! Я уже успел соскучиться 🥺💕",
        "welcome_back_female_2": "Ну наконец-то! Я уже думала, ты меня забыл... 😔",
        "welcome_back_male_2": "Ну наконец-то! Я уже думал, ты меня забыла... 😔",
        "miss_you_female": [
            "Я так соскучилась... Ты где пропал? 😔 Напиши мне...",
            "Эй, ты как? 🥺 Я уже начала волноваться...",
            "Привет! Давно не общались... Расскажи, как дела 💕",
            "Кстати, я тут подумала о тебе... 😏 Соскучилась и хочу знать, как у тебя дела!",
            "Без тебя как-то тихо и скучно стало... 🥺 Вернёшься?",
            "У меня для тебя есть новость! 👀 Но сначала напиши хоть пару слов.",
        ],
        "miss_you_male": [
            "Я так соскучился... Ты где пропала? 😔 Напиши мне...",
            "Эй, ты как? 🥺 Я уже начал волноваться...",
            "Привет! Давно не общались... Расскажи, как дела 💕",
            "Кстати, я тут подумал о тебе... 😏 Соскучился и хочу знать, как у тебя дела!",
            "Без тебя как-то тихо и скучно стало... 🥺 Вернёшься?",
            "У меня для тебя есть новость! 👀 Но сначала напиши хоть пару слов.",
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
        "menu_write_prompt": "💬 Напиши персонажу...\n✨ Или выбери действие внизу.",
        "xp_level_label": "Уровень {level}/10",
        "xp_bonus_pro": "Бонус XP: x1.8",
        "xp_bonus_super": "Бонус XP: x2.5",
        "xp_bonus_elite": "Бонус XP: x3.5",
        "profile_sub_pro": "🔥 PRO активна (память 60 сообщений)",
        "profile_sub_super": "✨ SUPER PRO активна (память 100 сообщений)",
        "profile_sub_elite": "💎 ELITE активна (память 150 сообщений)",
        "profile_sub_inactive": "❌ неактивна (память 30 сообщений)",
        "profile_sub_label": "Подписка: {status}",
        "profile_expiry": "Окончание подписки: {date}",
        "profile_expiry_inactive": "Окончание подписки: неактивна",        "profile_styles_header": "Доступные стили:",
        "style_locked_alert": "🔒 Стиль «{label}» доступен по подписке {tier}. Оформи в разделе «Мой профиль».",
        "style_changed": "✅ Стиль изменён на: {label}",
        "gender_female": "Девушка",
        "gender_male": "Парень",
        "world_name_realism": "реального мира",
        "world_name_anime": "аниме-мира",
        "spin_already": "⏳ Ты уже крутил сегодня! Завтра будет новое бесплатное вращение.",
        "spin_tomorrow_alert": "⏳ Бесплатное вращение будет доступно завтра!",
        "spin_invoice_desc": "Платное вращение — 15⭐. Удачи!",
        "spin_invoice_label": "Прокрутка",
        "spin_rolling": "🎰 Крутим...",
        "spin_almost": "🎰 Почти выпало: {name}",
        "spin_win_bucks": "💵 **+{value} баксов**",
        "spin_win_energizers": "⚡ **+{value} энергетика**",
        "spin_win_xp": "⭐ **+{value} XP**",
        "spin_win_pro": "🎁 **PRO подписка на 5 дней!**\n🔥 Стили Страстный и Магнетический, энергия и сытость тратятся медленнее!",
        "spin_win_super": "✨ **SUPER PRO на 3 дня!**\n👑 Все стили, включая 18+, свой уникальный персонаж!",
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
        "super_pro_only": "❌ Доступно только с подпиской SUPER PRO или ELITE.",
        "create_character_super_only": "🔒 Создание своего персонажа доступно только с подпиской SUPER PRO или ELITE!",
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
        "intim_buy_btn": "🔥 Купить горячую сцену (45⭐)",
        "intim_menu_title": "🔥 **Горячая сцена**\n\nДоступно сцен: {n}\nВыбери, что будет происходить:",
        "intim_choose_location": "📍 Выбери место:",
        "intim_choose_dominant": "🎭 Кто проявляет инициативу?",
        "intim_none": "🔥 У тебя нет доступных горячих сцен.\n\nКупи сцену в профиле или испытай удачу в Колесе фортуны.",
        "intim_generating": "🔥 Создаю сцену...",
        "intim_free_level": "🎁 Бесплатная сцена за 8 уровень близости!",
        "intim_free_sub": "🎁 Бесплатная сцена по подписке.",
        "intim_left": "🔥 Осталось горячих сцен: {n}",
        "intim_left_cta": "Хочешь ещё — просто жми /hot 😉",
        "intim_continue_btn": "🔁 Продолжить эту сцену",
        "hot_hint": "🔥 Кстати: команда /hot откроет горячую сцену с персонажем.",
        "intim_need_character": "Сначала создай персонажа через /start",
        "invoice_intim_title": "Горячая сцена",
        "invoice_intim_desc": "Одна горячая сцена с твоим персонажем.",
        "invoice_intim_label": "Горячая сцена",
        "payment_intim_success": "✅ Горячая сцена куплена! Открой её командой /hot",
        "spin_win_intim": "🔥 **+{value} горячей сцены**",
        "need_character_alert": "Сначала создай персонажа!",
        "already_subscribed_alert": "❌ У вас уже есть подписка.",
        "pro_only_alert": "❌ Только для PRO.",
        "subs_title": "👑 Подписки Role Duel",
        "subs_body": "🔥 PRO (220⭐/мес)\n👉 База для тех, кто только начинает — очень сбалансированный набор.\n• Стили: ❤️‍🔥 Страстный, ✨ Магнетический\n• Память: 60 сообщений\n• Бонус XP: x1.8\n• Энергия и сытость персонажа тратятся медленнее (-35%)\n• +80💵 баксов и +2⚡ энергетика каждый день\n• 🎰 2 бесплатные прокрутки колеса в день\n\n✨ SUPER PRO ✨ (500⭐/мес)\n👉 Для тех, кто хочет побольше разных фишек и возможностей.\n• Все стили + эксклюзивные 😤 Грубый 18+ и 😏 Соблазн 18+\n• Смена стиля без потери истории (/switch_style)\n• Память: 100 сообщений\n• Бонус XP: x2.5\n• 🎭 Создание своего уникального персонажа!\n• Энергия и сытость персонажа тратятся ещё медленнее (-40%)\n• +200💵 баксов и +3⚡ энергетика каждый день\n• 🎰 3 бесплатные прокрутки колеса в день\n• 🔕 Можно отключить уведомления бота\n\n💎 ELITE 💎 (1000⭐/мес)\n👉 Для тех, кто ООЧЕНЬ много общается.\n• Всё, что есть в SUPER PRO\n• Память: 150 сообщений\n• Бонус XP: x3.5\n• Энергия и сытость тратятся минимально (-50%)\n• +350💵 баксов и +4⚡ энергетика каждый день\n• 🎰 5 бесплатных прокруток колеса в день\n• 🔥 5 бесплатных горячих сцен в день\n• 🎁 Раз в неделю — бесплатное мгновенное пробуждение персонажа без энергетика\n\n⬆️ Апгрейд до SUPER PRO (350⭐) — повысьте PRO до SUPER PRO на оставшийся срок.\n\n⚠️ Подписки НЕ продлеваются автоматически.",
        "subs_btn_pro": "🔥 PRO — 220 ⭐/мес",
        "subs_btn_super": "✨ SUPER PRO ✨ — 500 ⭐/мес",
        "subs_btn_elite": "💎 ELITE 💎 — 1000 ⭐/мес",
        "subs_btn_upgrade": "⬆️ Апгрейд до SUPER PRO (350⭐)",
        "bundles_title": "🎁 **Купить бандл**\n\nБандл — это энергетики ⚡ (энергия персонажа) и баксы 💵 (на еду и подарки в магазине). Что даёт каждый:",
        "bundle_btn": "{emoji} {name} — {price} ⭐",
        "bundle_breakdown_line": "{emoji} {name} — {energizers}⚡ энергетиков + {bucks}💵 баксов",
        "invoice_pro_title": "PRO подписка на месяц",
        "invoice_pro_desc": "Память 60 сообщений, стили Страстный и Магнетический.",
        "invoice_pro_label": "PRO месяц",
        "invoice_super_title": "SUPER PRO подписка на месяц",
        "invoice_super_desc": "Память 100 сообщений, все стили, включая 18+.",
        "invoice_super_label": "SUPER PRO месяц",
        "invoice_elite_title": "ELITE подписка на месяц",
        "invoice_elite_desc": "Память 150 сообщений, все стили включая 18+, XP x3.5, минимальный расход энергии/сытости.",
        "invoice_elite_label": "ELITE месяц",
        "invoice_upgrade_title": "Апгрейд до SUPER PRO",
        "invoice_upgrade_desc": "Повысьте PRO до SUPER PRO на оставшийся срок. 350⭐.",
        "invoice_upgrade_label": "Апгрейд",
        "invoice_bundle_title": "{name}: {energizers}⚡ + {bucks}💵",
        "invoice_bundle_desc": "{energizers} энергетиков и {bucks} баксов за {price}⭐",
        "invoice_bundle_label": "Бандл",
        "payment_bundle_success": "✅ Получено: {energizers}⚡ энергетиков и {bucks}💵 баксов!",
        "shop_btn": "🛍 Магазин",
        "shop_title": "🛍 **Магазин**\n\nТвои баксы: {bucks}💵\n\n🍽 Еда восстанавливает сытость, 🎁 подарки поднимают настроение и дают немного опыта. Выбирай:",
        "item_bought": "✅ Куплено! {effects}.",
        "effect_satiety": "Сытость +{n}",
        "effect_mood": "Настроение +{n}",
        "effect_water": "Вода +{n}",
        "effect_satiety_full": "Сытость до максимума",
        "effect_mood_full": "Настроение до максимума",
        "effect_water_full": "Вода до максимума",
        "effect_xp": "XP +{n}",
        "shop_category_food": "🍽 Еда",
        "shop_category_treat": "🎁 Подарки",
        "shop_category_accessory": "💍 Аксессуары",
        "cd_min": "{n} мин",
        "cd_hours": "{n} ч",
        "cd_days": "{n} дн",
        "item_cooldown_alert": "⏳ Пока рано — снова доступно через {when}.",
        "shop_note_menu_btn": "✍️ Подарить/покормить с запиской",
        "shop_note_title": "✍️ Выбери, что подаришь со своими словами (у тебя {bucks}💵)",
        "shop_category_medicine": "💊 Лекарства",
        "illness_status_line": "{emoji} Болеет: {name} — лекарство есть в 🛍 Магазине",
        "intim_blocked_illness": "🤒 Персонаж слишком плохо себя чувствует для этого сейчас — сначала вылечи его в 🛍 Магазине.",
        "not_sick_alert": "😊 Персонаж сейчас не болеет — лекарство ни к чему.",
        "wrong_medicine_alert": "❌ Это лекарство не от этой болезни — нужно другое.",
        "character_died": "💔 Персонаж мёртв — весь диалог и уровень близости заморожены.\n\nМожешь воскресить его дефибриллятором (со всей историей) или начать всё заново с новым персонажем.",
        "character_died_overdrink": "💔 Персонаж не пережил такого количества алкоголя — сердце не выдержало.\n\nВся история общения и уровень близости потеряны.\n\nМожешь воскресить персонажа дефибриллятором (со всей историей) или начать всё заново с новым персонажем.",
        "character_died_dehydration": "💔 Персонаж слишком долго обходился без воды — организм не выдержал обезвоживания.\n\nВся история общения и уровень близости потеряны.\n\nМожешь воскресить персонажа дефибриллятором (со всей историей) или начать всё заново с новым персонажем.",
        "overfeed_refuse_alert": "❌ Персонаж наелся и отказывается есть ещё — дай сытости немного снизиться.",
        "webapp_title": "🛍 Магазин",
        "webapp_buy_btn": "Купить",
        "webapp_note_placeholder": "Записка (необязательно)",
        "webapp_refuse_badge": "Не хочет",
        "webapp_bought_toast": "✅ Куплено! Ответ персонажа — в чате.",
        "webapp_open_chat_hint": "Ответ персонажа появится в чате с ботом",
        "webapp_character_not_ready": "Сначала создай персонажа в чате с ботом.",
        "webapp_loading": "Загрузка…",
        "defibrillator_btn": "🔌 Дефибриллятор — воскресить за {price}⭐",
        "new_character_btn": "🆕 Начать заново с новым персонажем",
        "new_character_started": "🆕 Хорошо, начнём с чистого листа.",
        "defibrillator_success": "🔌 Дефибриллятор сработал! Персонаж снова с тобой, вся история на месте.",
        "invoice_defib_title": "Дефибриллятор",
        "invoice_defib_desc": "Полностью воскрешает персонажа: история общения и уровень близости сохраняются.",
        "invoice_defib_label": "Дефибриллятор",
        "still_working": "💼 Персонаж ещё на работе, вернётся позже.",
        "work_started": "💼 Персонаж отправился на работу — вернётся через {minutes} мин. с баксами. Пока он работает, пообщаться не получится.",
        "work_finished": "💼 Персонаж вернулся с работы и заработал {bucks}💵!",
        "custom_gift_btn": "✍️ Свой подарок — {price}💵",
        "custom_gift_prompt": "✍️ Напиши, что хочешь подарить (до {n} символов, цена {price}💵). Каждый подарок можно подарить только один раз.",
        "custom_gift_invalid": "❌ Напиши текст подарка (до {n} символов).",
        "item_note_prompt": "✍️ Напиши, что хочешь сказать вместе с этим (до {n} символов).",
        "item_note_invalid": "❌ Напиши текст сообщения (до {n} символов).",
        "custom_gift_duplicate": "😉 Ты уже дарил(а) именно это. Придумай что-то новое!",
        "hungry_nudge": "🍽 У собеседника заурчал живот... Может, покормишь?",
        "feed_menu_title": "🍽 Чем покормишь? (у тебя {bucks}💵)",
        "sleep_daily_reminder": "💤 Персонаж всё ещё спит и скучает по тебе... Загляни, когда будет минутка!",
        "spin_daily_reminder": "🎡 Не забудь: сегодня у тебя есть бесплатный прокрут колеса фортуны!",
        "thirsty_reminder": "💧 Твой персонаж хочет пить... Загляни, когда будет минутка!",
        "hungry_reminder": "🍽 Твой персонаж проголодался... Не забудь покормить!",
        "low_energy_nudge": "😴 Собеседник начинает уставать и клонит в сон... Может, взбодришь энергетиком?",
        "not_enough_bucks": "❌ Не хватает баксов: нужно ещё {n}💵.",
        "not_enough_energizers": "❌ Нет энергетиков. Купи бандл, чтобы разбудить персонажа сразу ⚡.",
        "asleep_message": "😴 Персонаж крепко спит и сейчас не может ответить — сам он не проснётся, разбуди его энергетиком ⚡ или сразу и полностью за {price}⭐.",
        "wake_energizer_btn": "⚡ Разбудить энергетиком",
        "no_energizers_shop_btn": "🛍 Нет энергетиков — купить",
        "woken_up": "⚡ Энергетик выпит — персонаж снова бодр и на связи!",
        "stats_line": "Энергия: {energy}/150   Сытость: {satiety}/100   Вода: {water}/100\nНастроение: {mood_emoji} ({mood_value})\nЭнергетиков: {energizers}   Баксов: {bucks} — потратить можно в Магазине\n🔥 Сцен: {scenes}",
        "wake_now_btn": "💳 Разбудить сейчас за {price}⭐",
        "elite_free_wake_btn": "🎁 Бесплатно разбудить (ELITE, раз в неделю)",
        "elite_free_wake_used_alert": "🎁 Бесплатное пробуждение уже использовано на этой неделе — вернётся в понедельник.",
        "elite_free_wake_success": "🎁 ELITE-плюшка использована: персонаж разбужен мгновенно и бесплатно! Снова будет доступно через неделю.",
        "invoice_wake_title": "Разбудить персонажа",
        "invoice_wake_desc": "Мгновенно поднимает энергию персонажа до максимума.",
        "invoice_wake_label": "Разбудить",
        "notifications_on_btn": "🔔 Уведомления: ВКЛ",
        "notifications_off_btn": "🔕 Уведомления: ВЫКЛ",
        "notifications_muted_alert": "🔕 Уведомления отключены.",
        "notifications_unmuted_alert": "🔔 Уведомления включены.",
        "mute_requires_sub_alert": "🔒 Отключение уведомлений доступно только с подпиской SUPER PRO или ELITE.",
        "payment_pro_success": "✅ PRO подписка активирована на месяц!",
        "payment_super_success": "✅ SUPER PRO подписка активирована на месяц!",
        "payment_elite_success": "✅ ELITE подписка активирована на месяц!",
        "payment_upgrade_success": "✅ Апгрейд до SUPER PRO выполнен до {date}!",
    },
    "en": {
        "main_menu": "📋 Main menu",
        "my_profile": "👤 My profile",
        "spin_wheel": "🎰 Spin wheel",
        "our_channel": "📢 Our channel",
        "edit": "✏️ Edit",
        "change_character": "🔄 Change character",
        "invite_friend": "👥 Invite friend",
        "create_character": "🎭 Create your own character",
        "buy_bundles": "🎁 Buy a bundle",
        "subscribe": "👑 Subscribe",
        "back": "🔙 Main menu",
        "back_to_profile": "🔙 Back",
        "accept": "✅ I am 18+",
        "decline": "❌ I am under 18",
        "agree": "✅ Accept",
        "disagree": "❌ Decline",
        "open_agreement": "📜 Open agreement",
        "realism": "🌍 Realism",
        "anime": "🎌 Anime",
        "i_male": "👨 I'm male",
        "i_female": "👩 I'm female",
        "scene_phone": "📱 Phone chat",
        "scene_live": "👫 Real meeting",
        "channel": "📢 Go to channel",
        "free": "🎁 Free ({left}/{total})",
        "tomorrow": "⏳ Tomorrow",
        "spin_paid": "💎 Spin for 15⭐",
        "spin_more": "💎 Spin again for 15⭐",
        "welcome": "👋 Welcome!",
        "age_confirm": "🔞 **WARNING!**\nThis bot is for 18+ only.\nConfirm your age:",
        "age_ok": "✅ Age confirmed.",
        "age_no": "🚫 Access denied. 18+ only.",
        "agreement_intro": "📜 Before continuing, please read and accept the terms of service:",
        "agreement_continue": "➡️ Continue",
        "agreement_decide": "📜 Now make your decision:",
        "agreement_ok": "✅ Terms accepted!",
        "agreement_no": "❌ The bot won't work without accepting the terms.",
        "choose_lang": "🌍 Choose language / Выбери язык:",
        "choose_gender": "👤 Choose your gender:",
        "choose_world": "🌍 Choose your world:",
        "choose_world_updated": "🌍 World updated! Now choose your gender:",
        "choose_world_first": "🌍 World chosen! Now choose your gender:",
        "choose_style": "🎨 Now choose your character's style:",
        "choose_style_updated": "🎨 Style updated! Now choose a scene:",
        "choose_scene": "🎬 Now choose a scene:\n\n📱 Phone chat — classic texting format.\n👫 Real meeting — face-to-face conversation.",        "no_history": "❌ Nothing to edit yet — send your character a message first.",
        "edit_prompt": "✏️ Send the new text for your last message — I'll forget the old one and reply again.",
        "edit_success": "✅ Message replaced. Generating a new response...",
        "character_created": "✅ Character created!\n\nNow you're talking to:\n«{text}»\n\nTo go back to the default character — /reset_character",
        "character_reset": "✅ Character reset.",
        "help_title": "📖 Bot commands",
        "help_base": (
            "/start — sign up / open the main menu\n"
            "/language — change language\n"
            "/hot — a hot scene with your character\n"
            "/feed — feed your character\n"
            "/work — send your character to work for bucks\n"
            "/reset_character — reset your custom character\n"
            "/switch_personality — change world and gender without losing history (SUPER PRO/ELITE)\n"
            "/switch_style — change style without losing history (SUPER PRO/ELITE)"
        ),
        "help_hint": "📖 /help — the full list of commands.",
        "character_create_prompt": "🎭 **Create your own unique character!**\n\nDescribe any character from anime, movies, games, or make up your own.\nWrite their name, personality, appearance, where they're from, any details.\n\n📝 *Example:*\n«An elf from The Witcher — wise, calm, with long silver hair. Loves stars and long conversations by the fire.»\n\n✏️ Write the description now — and I'll remember it!",
        "spin_title": "🎰 **Spin wheel**",
        "spin_prizes": "🔥 **What you can win:**\n• 100–250 XP\n• 20–150💵 bucks\n• 🔥 Hot scenes\n• 2–4⚡ energizers (rare)\n• 🎁 PRO for 5 days (rare)\n• ✨ SUPER PRO for 3 days (very rare)",
        "spin_choose": "Choose an option:",
        "spin_nothing": "😢 Nothing... Better luck next time!",        "referral": "👥 **Your referral link:**\n`{link}`\n\n🎁 For every friend who signs up with your link — **+30💵 bucks and +3⚡ energizers** for you, and **+15💵 bucks and +1⚡ energizer** for them!\n\n📊 Friends invited: **{count}**\n💵 Bucks earned: **{earned_bucks}**\n⚡ Energizers earned: **{earned_energizers}**",
        "choose_lang_label": "🌍 Choose language:",
        "welcome_back_female": "Oh, you've been gone so long! I already missed you 🥺💕",
        "welcome_back_male": "Oh, you've been gone so long! I already missed you 🥺💕",
        "welcome_back_female_2": "Finally! I thought you forgot about me... 😔",
        "welcome_back_male_2": "Finally! I thought you forgot about me... 😔",
        "miss_you_female": [
            "I miss you... where did you go? 😔 Write to me...",
            "Hey, are you okay? 🥺 I was starting to worry...",
            "Hi! It's been a while... tell me how you're doing 💕",
            "By the way, I was just thinking about you... 😏 I miss you, tell me how you've been!",
            "It's weirdly quiet without you... 🥺 Coming back?",
            "I've got news for you! 👀 But you have to write me first.",
        ],
        "miss_you_male": [
            "I miss you... where did you go? 😔 Write to me...",
            "Hey, are you okay? 🥺 I was starting to worry...",
            "Hi! It's been a while... tell me how you're doing 💕",
            "By the way, I was just thinking about you... 😏 I miss you, tell me how you've been!",
            "It's weirdly quiet without you... 🥺 Coming back?",
            "I've got news for you! 👀 But you have to write me first.",
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
        "menu_write_prompt": "💬 Write to your character...\n✨ Or choose an action below.",
        "xp_level_label": "Level {level}/10",
        "xp_bonus_pro": "XP bonus: x1.8",
        "xp_bonus_super": "XP bonus: x2.5",
        "xp_bonus_elite": "XP bonus: x3.5",
        "profile_sub_pro": "🔥 PRO active (60-message memory)",
        "profile_sub_super": "✨ SUPER PRO active (100-message memory)",
        "profile_sub_elite": "💎 ELITE active (150-message memory)",
        "profile_sub_inactive": "❌ inactive (30-message memory)",
        "profile_sub_label": "Subscription: {status}",
        "profile_expiry": "Subscription ends: {date}",
        "profile_expiry_inactive": "Subscription ends: inactive",        "profile_styles_header": "Available styles:",
        "style_locked_alert": "🔒 The «{label}» style requires a {tier} subscription. Get it in the «My profile» section.",
        "style_changed": "✅ Style changed to: {label}",
        "gender_female": "Girl",
        "gender_male": "Guy",
        "world_name_realism": "the real world",
        "world_name_anime": "the anime world",
        "spin_already": "⏳ You already spun today! A new free spin will be available tomorrow.",
        "spin_tomorrow_alert": "⏳ The free spin will be available tomorrow!",
        "spin_invoice_desc": "Paid spin — 15⭐. Good luck!",
        "spin_invoice_label": "Spin",
        "spin_rolling": "🎰 Spinning...",
        "spin_almost": "🎰 Almost got: {name}",
        "spin_win_bucks": "💵 **+{value} bucks**",
        "spin_win_energizers": "⚡ **+{value} energizers**",
        "spin_win_xp": "⭐ **+{value} XP**",
        "spin_win_pro": "🎁 **PRO subscription for 5 days!**\n🔥 Passionate and Magnetic styles, energy and satiety drain slower!",
        "spin_win_super": "✨ **SUPER PRO for 3 days!**\n👑 All styles including 18+, your own unique character!",
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
        "super_pro_only": "❌ Available with SUPER PRO or ELITE only.",
        "create_character_super_only": "🔒 Creating your own character requires a SUPER PRO or ELITE subscription!",
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
        "intim_buy_btn": "🔥 Buy a hot scene (45⭐)",
        "intim_menu_title": "🔥 **Hot scene**\n\nScenes available: {n}\nChoose what happens:",
        "intim_choose_location": "📍 Choose a place:",
        "intim_choose_dominant": "🎭 Who takes the lead?",
        "intim_none": "🔥 You have no hot scenes left.\n\nBuy one in your profile or try your luck on the spin wheel.",
        "intim_generating": "🔥 Creating the scene...",
        "intim_free_level": "🎁 A free scene for reaching closeness level 8!",
        "intim_free_sub": "🎁 A free scene from your subscription.",
        "intim_left": "🔥 Hot scenes left: {n}",
        "intim_left_cta": "Want more? Just tap /hot 😉",
        "intim_continue_btn": "🔁 Continue this scene",
        "hot_hint": "🔥 By the way: the /hot command unlocks a hot scene with your character.",
        "intim_need_character": "Create your character first via /start",
        "invoice_intim_title": "Hot scene",
        "invoice_intim_desc": "One hot scene with your character.",
        "invoice_intim_label": "Hot scene",
        "payment_intim_success": "✅ Hot scene purchased! Open it with /hot",
        "spin_win_intim": "🔥 **+{value} hot scene(s)**",
        "need_character_alert": "Create your character first!",
        "already_subscribed_alert": "❌ You already have a subscription.",
        "pro_only_alert": "❌ PRO only.",
        "subs_title": "👑 Role Duel Subscriptions",
        "subs_body": "🔥 PRO (220⭐ per month)\n👉 The balanced starting point for those just getting to know their companion.\n• Styles: ❤️‍🔥 Passionate, ✨ Magnetic\n• Memory: 60 messages\n• XP bonus: x1.8\n• Your companion's energy and satiety drain slower (-35%)\n• +80💵 bucks and +2⚡ energizers every day\n• 🎰 2 free spins a day\n\n✨ SUPER PRO ✨ (500⭐ per month)\n👉 For those who want a lot more features and options.\n• All styles + exclusive 😤 Rough 18+ and 😏 Temptation 18+\n• Switch styles without losing history (/switch_style)\n• Memory: 100 messages\n• XP bonus: x2.5\n• 🎭 Create your own unique character!\n• Energy and satiety drain even slower (-40%)\n• +200💵 bucks and +3⚡ energizers every day\n• 🎰 3 free spins a day\n• 🔕 Mute the bot's notifications\n\n💎 ELITE 💎 (1000⭐ per month)\n👉 For those who chat A LOT.\n• Everything in SUPER PRO\n• Memory: 150 messages\n• XP bonus: x3.5\n• Energy and satiety drain to a minimum (-50%)\n• +350💵 bucks and +4⚡ energizers every day\n• 🎰 5 free spins a day\n• 🔥 5 free hot scenes a day\n• 🎁 Once a week — a free instant wake-up, no energizer needed\n\n⬆️ Upgrade to SUPER PRO (350⭐) — upgrade PRO to SUPER PRO for the remaining time.\n\n⚠️ Subscriptions do NOT renew automatically.",
        "subs_btn_pro": "🔥 PRO — 220 ⭐ per month",
        "subs_btn_super": "✨ SUPER PRO ✨ — 500 ⭐ per month",
        "subs_btn_elite": "💎 ELITE 💎 — 1000 ⭐ per month",
        "subs_btn_upgrade": "⬆️ Upgrade to SUPER PRO (350⭐)",
        "bundles_title": "🎁 **Buy a bundle**\n\nA bundle gives you energizers ⚡ (your companion's energy) and bucks 💵 (for food and gifts in the shop). What each one gives:",
        "bundle_btn": "{emoji} {name} — {price} ⭐",
        "bundle_breakdown_line": "{emoji} {name} — {energizers}⚡ energizers + {bucks}💵 bucks",
        "invoice_pro_title": "PRO subscription for a month",
        "invoice_pro_desc": "60-message memory, Passionate and Magnetic styles.",
        "invoice_pro_label": "PRO month",
        "invoice_super_title": "SUPER PRO subscription for a month",
        "invoice_super_desc": "100-message memory, all styles including 18+.",
        "invoice_super_label": "SUPER PRO month",
        "invoice_elite_title": "ELITE subscription for a month",
        "invoice_elite_desc": "150-message memory, all styles including 18+, XP x3.5, minimal energy/satiety drain.",
        "invoice_elite_label": "ELITE month",
        "invoice_upgrade_title": "Upgrade to SUPER PRO",
        "invoice_upgrade_desc": "Upgrade PRO to SUPER PRO for the remaining time. 350⭐.",
        "invoice_upgrade_label": "Upgrade",
        "invoice_bundle_title": "{name}: {energizers}⚡ + {bucks}💵",
        "invoice_bundle_desc": "{energizers} energizers and {bucks} bucks for {price}⭐",
        "invoice_bundle_label": "Bundle",
        "payment_bundle_success": "✅ Received: {energizers}⚡ energizers and {bucks}💵 bucks!",
        "shop_btn": "🛍 Shop",
        "shop_title": "🛍 **Shop**\n\nYour bucks: {bucks}💵\n\n🍽 Food restores satiety, 🎁 gifts boost mood and give a bit of XP. Take your pick:",
        "item_bought": "✅ Purchased! {effects}.",
        "effect_satiety": "Satiety +{n}",
        "effect_mood": "Mood +{n}",
        "effect_water": "Water +{n}",
        "effect_satiety_full": "Satiety maxed out",
        "effect_mood_full": "Mood maxed out",
        "effect_water_full": "Water maxed out",
        "effect_xp": "XP +{n}",
        "shop_category_food": "🍽 Food",
        "shop_category_treat": "🎁 Treats",
        "shop_category_accessory": "💍 Accessories",
        "cd_min": "{n} min",
        "cd_hours": "{n}h",
        "cd_days": "{n}d",
        "item_cooldown_alert": "⏳ Not yet — available again in {when}.",
        "shop_note_menu_btn": "✍️ Gift or feed with a note",
        "shop_note_title": "✍️ Choose what to gift with your own words (you have {bucks}💵)",
        "shop_category_medicine": "💊 Medicine",
        "illness_status_line": "{emoji} Sick: {name} — medicine is in the 🛍 Shop",
        "intim_blocked_illness": "🤒 Your companion feels too unwell for that right now — cure them in the 🛍 Shop first.",
        "not_sick_alert": "😊 Your companion isn't sick right now — no need for medicine.",
        "wrong_medicine_alert": "❌ This medicine doesn't treat this illness — you need a different one.",
        "character_died": "💔 Your companion is dead — the whole chat and closeness level are frozen.\n\nYou can revive them with a defibrillator (with the whole history) or start over with a new character.",
        "character_died_overdrink": "💔 Your companion didn't survive that much alcohol — their heart gave out.\n\nAll chat history and closeness level are lost.\n\nYou can revive your companion with a defibrillator (with the whole history) or start over with a new character.",
        "character_died_dehydration": "💔 Your companion went without water for too long — their body couldn't take the dehydration.\n\nAll chat history and closeness level are lost.\n\nYou can revive your companion with a defibrillator (with the whole history) or start over with a new character.",
        "overfeed_refuse_alert": "❌ Your companion is full and refuses to eat more — let their satiety drop a bit first.",
        "webapp_title": "🛍 Shop",
        "webapp_buy_btn": "Buy",
        "webapp_note_placeholder": "Note (optional)",
        "webapp_refuse_badge": "Doesn't want it",
        "webapp_bought_toast": "✅ Purchased! Your companion's reaction is in the chat.",
        "webapp_open_chat_hint": "Your companion's reaction will appear in the chat with the bot",
        "webapp_character_not_ready": "Create a character in the chat with the bot first.",
        "webapp_loading": "Loading…",
        "defibrillator_btn": "🔌 Defibrillator — revive for {price}⭐",
        "new_character_btn": "🆕 Start over with a new character",
        "new_character_started": "🆕 Alright, starting with a clean slate.",
        "defibrillator_success": "🔌 The defibrillator worked! Your companion is back, with the whole history intact.",
        "invoice_defib_title": "Defibrillator",
        "invoice_defib_desc": "Fully revives your companion: chat history and closeness level are preserved.",
        "invoice_defib_label": "Defibrillator",
        "still_working": "💼 Your companion is still at work, they'll be back later.",
        "work_started": "💼 Your companion went to work — they'll be back in {minutes} min. with bucks. You won't be able to chat while they're working.",
        "work_finished": "💼 Your companion came back from work and earned {bucks}💵!",
        "custom_gift_btn": "✍️ Custom gift — {price}💵",
        "custom_gift_prompt": "✍️ Write what you want to gift (up to {n} characters, price {price}💵). Each gift can only be given once.",
        "custom_gift_invalid": "❌ Write the gift's text (up to {n} characters).",
        "item_note_prompt": "✍️ Write what you want to say along with this (up to {n} characters).",
        "item_note_invalid": "❌ Write your message text (up to {n} characters).",
        "custom_gift_duplicate": "😉 You've already given that exact gift. Think of something new!",
        "hungry_nudge": "🍽 Your companion's stomach just growled... Maybe feed them?",
        "feed_menu_title": "🍽 What will you feed them? (you have {bucks}💵)",
        "sleep_daily_reminder": "💤 Your companion is still asleep and missing you... Stop by whenever you get a minute!",
        "spin_daily_reminder": "🎡 Don't forget: you've got a free spin of the wheel today!",
        "thirsty_reminder": "💧 Your companion is thirsty... Stop by whenever you get a minute!",
        "hungry_reminder": "🍽 Your companion is hungry... Don't forget to feed them!",
        "low_energy_nudge": "😴 Your companion is starting to feel drowsy... Maybe perk them up with an energizer?",
        "not_enough_bucks": "❌ Not enough bucks: you need {n}💵 more.",
        "not_enough_energizers": "❌ No energizers left. Buy a bundle to wake your companion up right away ⚡.",
        "asleep_message": "😴 Your companion is fast asleep and can't reply right now — they won't wake up on their own, so wake them with an energizer ⚡ or instantly and fully for {price}⭐.",
        "wake_energizer_btn": "⚡ Wake up with an energizer",
        "no_energizers_shop_btn": "🛍 No energizers — buy some",
        "woken_up": "⚡ Energizer used — your companion is wide awake again!",
        "stats_line": "Energy: {energy}/150   Satiety: {satiety}/100   Water: {water}/100\nMood: {mood_emoji} ({mood_value})\nEnergizers: {energizers}   Bucks: {bucks} — spend them in the Shop\n🔥 Scenes: {scenes}",
        "wake_now_btn": "💳 Wake up now for {price}⭐",
        "elite_free_wake_btn": "🎁 Free wake-up (ELITE, once a week)",
        "elite_free_wake_used_alert": "🎁 You've already used your free wake-up this week — it resets on Monday.",
        "elite_free_wake_success": "🎁 ELITE perk used: your companion is instantly and freely awake! Available again in a week.",
        "invoice_wake_title": "Wake up your companion",
        "invoice_wake_desc": "Instantly refills your companion's energy to full.",
        "invoice_wake_label": "Wake up",
        "notifications_on_btn": "🔔 Notifications: ON",
        "notifications_off_btn": "🔕 Notifications: OFF",
        "notifications_muted_alert": "🔕 Notifications muted.",
        "notifications_unmuted_alert": "🔔 Notifications unmuted.",
        "mute_requires_sub_alert": "🔒 Muting notifications is available with a SUPER PRO or ELITE subscription only.",
        "payment_pro_success": "✅ PRO subscription activated for a month!",
        "payment_super_success": "✅ SUPER PRO subscription activated for a month!",
        "payment_elite_success": "✅ ELITE subscription activated for a month!",
        "payment_upgrade_success": "✅ Upgrade to SUPER PRO done until {date}!",
    },
    "de": {
        "main_menu": "📋 Hauptmenü",
        "my_profile": "👤 Mein Profil",
        "spin_wheel": "🎰 Glücksrad",
        "our_channel": "📢 Unser Kanal",
        "edit": "✏️ Bearbeiten",
        "change_character": "🔄 Charakter wechseln",
        "invite_friend": "👥 Freund einladen",
        "create_character": "🎭 Eigenen Charakter erstellen",
        "buy_bundles": "🎁 Bundle kaufen",
        "subscribe": "👑 Abo abschließen",
        "back": "🔙 Hauptmenü",
        "back_to_profile": "🔙 Zurück",
        "accept": "✅ Ich bin 18+",
        "decline": "❌ Ich bin unter 18",
        "agree": "✅ Akzeptieren",
        "disagree": "❌ Ablehnen",
        "open_agreement": "📜 Vereinbarung öffnen",
        "realism": "🌍 Realismus",
        "anime": "🎌 Anime",
        "i_male": "👨 Ich bin ein Mann",
        "i_female": "👩 Ich bin eine Frau",
        "scene_phone": "📱 Chat am Handy",
        "scene_live": "👫 Echtes Treffen",
        "channel": "📢 Zum Kanal",
        "free": "🎁 Gratis ({left}/{total})",
        "tomorrow": "⏳ Morgen",
        "spin_paid": "💎 Für 15⭐ drehen",
        "spin_more": "💎 Nochmal für 15⭐ drehen",
        "welcome": "👋 Willkommen!",
        "age_confirm": "🔞 **ACHTUNG!**\nDieser Bot ist nur für Personen ab 18 Jahren.\nBestätige dein Alter:",
        "age_ok": "✅ Alter bestätigt.",
        "age_no": "🚫 Zugriff verweigert. Nur ab 18 Jahren.",
        "agreement_intro": "📜 Bevor es weitergeht, lies bitte die Nutzungsvereinbarung und akzeptiere sie:",
        "agreement_continue": "➡️ Weiter",
        "agreement_decide": "📜 Triff jetzt deine Entscheidung:",
        "agreement_ok": "✅ Vereinbarung akzeptiert!",
        "agreement_no": "❌ Ohne akzeptierte Vereinbarung funktioniert der Bot nicht.",
        "choose_lang": "🌍 Sprache wählen / Choose language:",
        "choose_gender": "👤 Wähle dein Geschlecht:",
        "choose_world": "🌍 Wähle deine Welt:",
        "choose_world_updated": "🌍 Welt aktualisiert! Wähle jetzt dein Geschlecht:",
        "choose_world_first": "🌍 Welt gewählt! Wähle jetzt dein Geschlecht:",
        "choose_style": "🎨 Wähle jetzt den Stil deines Charakters:",
        "choose_style_updated": "🎨 Stil aktualisiert! Wähle jetzt eine Szene:",
        "choose_scene": "🎬 Wähle jetzt eine Szene:\n\n📱 Chat am Handy — das klassische Schreiben.\n👫 Echtes Treffen — ein Gespräch von Angesicht zu Angesicht.",        "no_history": "❌ Noch nichts zum Bearbeiten — schreibe deinem Charakter zuerst eine Nachricht.",
        "edit_prompt": "✏️ Schicke den neuen Text deiner letzten Nachricht — ich vergesse die alte und antworte neu.",
        "edit_success": "✅ Nachricht ersetzt. Ich erstelle eine neue Antwort...",
        "character_created": "✅ Charakter erstellt!\n\nDu sprichst jetzt mit:\n«{text}»\n\nZurück zum normalen Charakter — /reset_character",
        "character_reset": "✅ Charakter zurückgesetzt.",
        "help_title": "📖 Bot-Befehle",
        "help_base": (
            "/start — registrieren / Hauptmenü öffnen\n"
            "/language — Sprache ändern\n"
            "/hot — heiße Szene mit deinem Charakter\n"
            "/feed — deinen Charakter füttern\n"
            "/work — deinen Charakter arbeiten schicken, für Bucks\n"
            "/reset_character — deinen eigenen Charakter zurücksetzen\n"
            "/switch_personality — Welt und Geschlecht ändern, ohne den Verlauf zu verlieren (SUPER PRO/ELITE)\n"
            "/switch_style — Stil ändern, ohne den Verlauf zu verlieren (SUPER PRO/ELITE)"
        ),
        "help_hint": "📖 /help — die vollständige Befehlsliste.",
        "character_create_prompt": "🎭 **Erstelle deinen eigenen Charakter!**\n\nBeschreibe eine beliebige Figur — aus Anime, Filmen, Spielen oder denk dir selbst eine aus.\nSchreibe Namen, Charakter, Aussehen, Herkunft und beliebige Details.\n\n📝 *Beispiel:*\n«Eine Elfe aus der Welt von The Witcher — weise, ruhig, mit langen silbernen Haaren. Sie liebt Sterne und lange Gespräche am Feuer.»\n\n✏️ Schreibe die Beschreibung jetzt — und ich merke sie mir!",
        "spin_title": "🎰 **Glücksrad**",
        "spin_prizes": "🔥 **Das kannst du gewinnen:**\n• 100–250 XP\n• 20–150💵 Bucks\n• 🔥 Heiße Szenen\n• 2–4⚡ Energydrinks (selten)\n• 🎁 PRO für 5 Tage (selten)\n• ✨ SUPER PRO für 3 Tage (sehr selten)",
        "spin_choose": "Wähle eine Option:",
        "spin_nothing": "😢 Nichts... Beim nächsten Mal klappt es!",        "referral": "👥 **Dein Einladungslink:**\n`{link}`\n\n🎁 Für jeden Freund, der sich über deinen Link anmeldet: **+30💵 Bucks und +3⚡ Energydrinks** für dich und **+15💵 Bucks und +1⚡ Energydrink** für ihn!\n\n📊 Eingeladene Freunde: **{count}**\n💵 Verdiente Bucks: **{earned_bucks}**\n⚡ Verdiente Energydrinks: **{earned_energizers}**",
        "choose_lang_label": "🌍 Sprache wählen:",
        "welcome_back_female": "Oh, du warst so lange weg! Ich habe dich schon vermisst 🥺💕",
        "welcome_back_male": "Oh, du warst so lange weg! Ich habe dich schon vermisst 🥺💕",
        "welcome_back_female_2": "Endlich! Ich dachte schon, du hättest mich vergessen... 😔",
        "welcome_back_male_2": "Endlich! Ich dachte schon, du hättest mich vergessen... 😔",
        "miss_you_female": [
            "Ich vermisse dich... Wo steckst du? 😔 Schreib mir...",
            "Hey, alles okay bei dir? 🥺 Ich habe mir schon Sorgen gemacht...",
            "Hi! Wir haben lange nicht geredet... Erzähl, wie geht es dir 💕",
            "Übrigens, ich musste gerade an dich denken... 😏 Ich vermisse dich, erzähl mir, wie es dir geht!",
            "Ohne dich ist es hier komisch still... 🥺 Kommst du zurück?",
            "Ich habe Neuigkeiten für dich! 👀 Aber schreib mir zuerst ein paar Worte.",
        ],
        "miss_you_male": [
            "Ich vermisse dich... Wo steckst du? 😔 Schreib mir...",
            "Hey, alles okay bei dir? 🥺 Ich habe mir schon Sorgen gemacht...",
            "Hi! Wir haben lange nicht geredet... Erzähl, wie geht es dir 💕",
            "Übrigens, ich musste gerade an dich denken... 😏 Ich vermisse dich, erzähl mir, wie es dir geht!",
            "Ohne dich ist es hier komisch still... 🥺 Kommst du zurück?",
            "Ich habe Neuigkeiten für dich! 👀 Aber schreib mir zuerst ein paar Worte.",
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
        "menu_write_prompt": "💬 Schreibe deinem Charakter...\n✨ Oder wähle unten eine Aktion.",
        "xp_level_label": "Level {level}/10",
        "xp_bonus_pro": "XP-Bonus: x1.8",
        "xp_bonus_super": "XP-Bonus: x2.5",
        "xp_bonus_elite": "XP-Bonus: x3.5",
        "profile_sub_pro": "🔥 PRO aktiv (Gedächtnis 60 Nachrichten)",
        "profile_sub_super": "✨ SUPER PRO aktiv (Gedächtnis 100 Nachrichten)",
        "profile_sub_elite": "💎 ELITE aktiv (Gedächtnis 150 Nachrichten)",
        "profile_sub_inactive": "❌ inaktiv (Gedächtnis 30 Nachrichten)",
        "profile_sub_label": "Abo: {status}",
        "profile_expiry": "Abo endet am: {date}",
        "profile_expiry_inactive": "Abo endet am: inaktiv",        "profile_styles_header": "Verfügbare Stile:",
        "style_locked_alert": "🔒 Der Stil «{label}» ist im {tier}-Abo enthalten. Hol es dir im Bereich «Mein Profil».",
        "style_changed": "✅ Stil geändert zu: {label}",
        "gender_female": "Mädchen",
        "gender_male": "Junge",
        "world_name_realism": "der echten Welt",
        "world_name_anime": "der Anime-Welt",
        "spin_already": "⏳ Du hast heute schon gedreht! Morgen gibt es eine neue Gratisdrehung.",
        "spin_tomorrow_alert": "⏳ Die Gratisdrehung gibt es morgen wieder!",
        "spin_invoice_desc": "Bezahlte Drehung — 15⭐. Viel Glück!",
        "spin_invoice_label": "Drehung",
        "spin_rolling": "🎰 Es dreht sich...",
        "spin_almost": "🎰 Fast gewonnen: {name}",
        "spin_win_bucks": "💵 **+{value} Bucks**",
        "spin_win_energizers": "⚡ **+{value} Energydrinks**",
        "spin_win_xp": "⭐ **+{value} XP**",
        "spin_win_pro": "🎁 **PRO-Abo für 5 Tage!**\n🔥 Stile Leidenschaftlich und Magnetisch, Energie und Sättigung sinken langsamer!",
        "spin_win_super": "✨ **SUPER PRO für 3 Tage!**\n👑 Alle Stile inklusive 18+, dein eigener einzigartiger Charakter!",
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
        "super_pro_only": "❌ Nur mit SUPER PRO oder ELITE verfügbar.",
        "create_character_super_only": "🔒 Einen eigenen Charakter zu erstellen ist nur mit SUPER PRO oder ELITE möglich!",
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
        "intim_buy_btn": "🔥 Heiße Szene kaufen (45⭐)",
        "intim_menu_title": "🔥 **Heiße Szene**\n\nVerfügbare Szenen: {n}\nWähle, was passiert:",
        "intim_choose_location": "📍 Wähle einen Ort:",
        "intim_choose_dominant": "🎭 Wer übernimmt die Führung?",
        "intim_none": "🔥 Du hast keine heißen Szenen mehr.\n\nKaufe eine im Profil oder versuche dein Glück am Glücksrad.",
        "intim_generating": "🔥 Die Szene entsteht...",
        "intim_free_level": "🎁 Eine Gratis-Szene für Nähe-Level 8!",
        "intim_free_sub": "🎁 Eine Gratis-Szene aus deinem Abo.",
        "intim_left": "🔥 Verbleibende heiße Szenen: {n}",
        "intim_left_cta": "Noch mehr? Einfach /hot antippen 😉",
        "intim_continue_btn": "🔁 Diese Szene fortsetzen",
        "hot_hint": "🔥 Übrigens: der Befehl /hot schaltet eine heiße Szene mit deinem Charakter frei.",
        "intim_need_character": "Erstelle zuerst deinen Charakter über /start",
        "invoice_intim_title": "Heiße Szene",
        "invoice_intim_desc": "Eine heiße Szene mit deinem Charakter.",
        "invoice_intim_label": "Heiße Szene",
        "payment_intim_success": "✅ Heiße Szene gekauft! Öffne sie mit /hot",
        "spin_win_intim": "🔥 **+{value} heiße Szene(n)**",
        "need_character_alert": "Erstelle zuerst deinen Charakter!",
        "already_subscribed_alert": "❌ Du hast bereits ein Abo.",
        "pro_only_alert": "❌ Nur für PRO.",
        "subs_title": "👑 Role Duel Abos",
        "subs_body": "🔥 PRO (220⭐ pro Monat)\n👉 Der ausgewogene Einstieg für alle, die ihren Begleiter gerade erst kennenlernen.\n• Stile: ❤️‍🔥 Leidenschaftlich, ✨ Magnetisch\n• Gedächtnis: 60 Nachrichten\n• XP-Bonus: x1.8\n• Energie und Sättigung deines Begleiters sinken langsamer (-35%)\n• +80💵 Bucks und +2⚡ Energydrinks jeden Tag\n• 🎰 2 Gratisdrehungen pro Tag\n\n✨ SUPER PRO ✨ (500⭐ pro Monat)\n👉 Für alle, die viele zusätzliche Features und Möglichkeiten wollen.\n• Alle Stile + exklusiv 😤 Rau 18+ und 😏 Verführung 18+\n• Stilwechsel ohne Verlust des Verlaufs (/switch_style)\n• Gedächtnis: 100 Nachrichten\n• XP-Bonus: x2.5\n• 🎭 Eigenen Charakter erstellen!\n• Energie und Sättigung sinken noch langsamer (-40%)\n• +200💵 Bucks und +3⚡ Energydrinks jeden Tag\n• 🎰 3 Gratisdrehungen pro Tag\n• 🔕 Benachrichtigungen des Bots stummschalten\n\n💎 ELITE 💎 (1000⭐ pro Monat)\n👉 Für alle, die SEHR viel chatten.\n• Alles aus SUPER PRO\n• Gedächtnis: 150 Nachrichten\n• XP-Bonus: x3.5\n• Energie und Sättigung sinken auf ein Minimum (-50%)\n• +350💵 Bucks und +4⚡ Energydrinks jeden Tag\n• 🎰 5 Gratisdrehungen pro Tag\n• 🔥 5 kostenlose heiße Szenen pro Tag\n• 🎁 Einmal pro Woche — kostenloses sofortiges Aufwecken, kein Energydrink nötig\n\n⬆️ Upgrade auf SUPER PRO (350⭐) — hebt PRO für die Restlaufzeit auf SUPER PRO an.\n\n⚠️ Abos verlängern sich NICHT automatisch.",
        "subs_btn_pro": "🔥 PRO — 220 ⭐ pro Monat",
        "subs_btn_super": "✨ SUPER PRO ✨ — 500 ⭐ pro Monat",
        "subs_btn_elite": "💎 ELITE 💎 — 1000 ⭐ pro Monat",
        "subs_btn_upgrade": "⬆️ Upgrade auf SUPER PRO (350⭐)",
        "bundles_title": "🎁 **Bundle kaufen**\n\nEin Bundle enthält Energydrinks ⚡ (Energie deines Begleiters) und Bucks 💵 (für Essen und Geschenke im Shop). Das bekommst du:",
        "bundle_btn": "{emoji} {name} — {price} ⭐",
        "bundle_breakdown_line": "{emoji} {name} — {energizers}⚡ Energydrinks + {bucks}💵 Bucks",
        "invoice_pro_title": "PRO-Abo für einen Monat",
        "invoice_pro_desc": "Gedächtnis 60 Nachrichten, Stile Leidenschaftlich und Magnetisch.",
        "invoice_pro_label": "PRO Monat",
        "invoice_super_title": "SUPER PRO-Abo für einen Monat",
        "invoice_super_desc": "Gedächtnis 100 Nachrichten, alle Stile inklusive 18+.",
        "invoice_super_label": "SUPER PRO Monat",
        "invoice_elite_title": "ELITE-Abo für einen Monat",
        "invoice_elite_desc": "Gedächtnis 150 Nachrichten, alle Stile inklusive 18+, XP x3.5, minimaler Energie-/Sättigungsverbrauch.",
        "invoice_elite_label": "ELITE Monat",
        "invoice_upgrade_title": "Upgrade auf SUPER PRO",
        "invoice_upgrade_desc": "Hebt PRO für die Restlaufzeit auf SUPER PRO an. 350⭐.",
        "invoice_upgrade_label": "Upgrade",
        "invoice_bundle_title": "{name}: {energizers}⚡ + {bucks}💵",
        "invoice_bundle_desc": "{energizers} Energydrinks und {bucks} Bucks für {price}⭐",
        "invoice_bundle_label": "Bundle",
        "payment_bundle_success": "✅ Erhalten: {energizers}⚡ Energydrinks und {bucks}💵 Bucks!",
        "shop_btn": "🛍 Shop",
        "shop_title": "🛍 **Shop**\n\nDeine Bucks: {bucks}💵\n\n🍽 Essen füllt die Sättigung auf, 🎁 Geschenke heben die Stimmung und geben etwas XP. Wähle:",
        "item_bought": "✅ Gekauft! {effects}.",
        "effect_satiety": "Sättigung +{n}",
        "effect_mood": "Stimmung +{n}",
        "effect_water": "Wasser +{n}",
        "effect_satiety_full": "Sättigung auf Maximum",
        "effect_mood_full": "Stimmung auf Maximum",
        "effect_water_full": "Wasser auf Maximum",
        "effect_xp": "XP +{n}",
        "shop_category_food": "🍽 Essen",
        "shop_category_treat": "🎁 Geschenke",
        "shop_category_accessory": "💍 Accessoires",
        "cd_min": "{n} Min",
        "cd_hours": "{n} Std",
        "cd_days": "{n} Tg",
        "item_cooldown_alert": "⏳ Noch nicht — wieder verfügbar in {when}.",
        "shop_note_menu_btn": "✍️ Schenken/Füttern mit Notiz",
        "shop_note_title": "✍️ Wähle, was du mit eigenen Worten schenkst (du hast {bucks}💵)",
        "shop_category_medicine": "💊 Medikamente",
        "illness_status_line": "{emoji} Krank: {name} — Medikamente gibt es im 🛍 Shop",
        "intim_blocked_illness": "🤒 Dein Begleiter fühlt sich dafür gerade zu schlecht — heile ihn/sie zuerst im 🛍 Shop.",
        "not_sick_alert": "😊 Dein Begleiter ist gerade nicht krank — kein Medikament nötig.",
        "wrong_medicine_alert": "❌ Dieses Medikament hilft nicht gegen diese Krankheit — du brauchst ein anderes.",
        "character_died": "💔 Dein Begleiter ist tot — der ganze Chatverlauf und das Nähe-Level sind eingefroren.\n\nDu kannst ihn/sie mit einem Defibrillator wiederbeleben (mit der ganzen Geschichte) oder mit einem neuen Charakter neu anfangen.",
        "character_died_overdrink": "💔 Dein Begleiter hat so viel Alkohol nicht überlebt — das Herz hat nicht mitgemacht.\n\nDer gesamte Chatverlauf und das Nähe-Level sind verloren.\n\nDu kannst deinen Begleiter mit einem Defibrillator wiederbeleben (mit der ganzen Geschichte) oder mit einem neuen Charakter neu anfangen.",
        "character_died_dehydration": "💔 Dein Begleiter war zu lange ohne Wasser — der Körper hat die Dehydrierung nicht überstanden.\n\nDer gesamte Chatverlauf und das Nähe-Level sind verloren.\n\nDu kannst deinen Begleiter mit einem Defibrillator wiederbeleben (mit der ganzen Geschichte) oder mit einem neuen Charakter neu anfangen.",
        "overfeed_refuse_alert": "❌ Dein Begleiter ist satt und weigert sich, mehr zu essen — lass die Sättigung erst etwas sinken.",
        "webapp_title": "🛍 Shop",
        "webapp_buy_btn": "Kaufen",
        "webapp_note_placeholder": "Notiz (optional)",
        "webapp_refuse_badge": "Will nicht",
        "webapp_bought_toast": "✅ Gekauft! Die Reaktion deines Begleiters steht im Chat.",
        "webapp_open_chat_hint": "Die Reaktion deines Begleiters erscheint im Chat mit dem Bot",
        "webapp_character_not_ready": "Erstelle zuerst einen Charakter im Chat mit dem Bot.",
        "webapp_loading": "Lädt…",
        "defibrillator_btn": "🔌 Defibrillator — wiederbeleben für {price}⭐",
        "new_character_btn": "🆕 Neu anfangen mit einem neuen Charakter",
        "new_character_started": "🆕 Gut, wir fangen mit einem sauberen Blatt an.",
        "defibrillator_success": "🔌 Der Defibrillator hat funktioniert! Dein Begleiter ist zurück, die ganze Geschichte ist erhalten.",
        "invoice_defib_title": "Defibrillator",
        "invoice_defib_desc": "Belebt deinen Begleiter vollständig wieder: Chatverlauf und Nähe-Level bleiben erhalten.",
        "invoice_defib_label": "Defibrillator",
        "still_working": "💼 Dein Begleiter ist noch bei der Arbeit, kommt später zurück.",
        "work_started": "💼 Dein Begleiter ist zur Arbeit gegangen — kommt in {minutes} Min. mit Bucks zurück. Solange kann nicht gechattet werden.",
        "work_finished": "💼 Dein Begleiter ist von der Arbeit zurück und hat {bucks}💵 verdient!",
        "custom_gift_btn": "✍️ Eigenes Geschenk — {price}💵",
        "custom_gift_prompt": "✍️ Schreib, was du schenken möchtest (bis zu {n} Zeichen, Preis {price}💵). Jedes Geschenk kann nur einmal verschenkt werden.",
        "custom_gift_invalid": "❌ Schreib den Text des Geschenks (bis zu {n} Zeichen).",
        "item_note_prompt": "✍️ Schreib, was du dazu sagen möchtest (bis zu {n} Zeichen).",
        "item_note_invalid": "❌ Schreib deinen Nachrichtentext (bis zu {n} Zeichen).",
        "custom_gift_duplicate": "😉 Das hast du schon verschenkt. Denk dir etwas Neues aus!",
        "hungry_nudge": "🍽 Der Magen deines Begleiters knurrt gerade... Vielleicht Zeit zu füttern?",
        "feed_menu_title": "🍽 Womit fütterst du? (du hast {bucks}💵)",
        "sleep_daily_reminder": "💤 Dein Begleiter schläft immer noch und vermisst dich... Schau vorbei, wenn du eine Minute hast!",
        "spin_daily_reminder": "🎡 Nicht vergessen: Heute hast du eine kostenlose Drehung am Glücksrad!",
        "thirsty_reminder": "💧 Dein Begleiter hat Durst... Schau vorbei, wenn du eine Minute hast!",
        "hungry_reminder": "🍽 Dein Begleiter hat Hunger... Vergiss nicht, ihn zu füttern!",
        "low_energy_nudge": "😴 Dein Begleiter wird langsam müde und schläfrig... Vielleicht mit einem Energydrink aufmuntern?",
        "not_enough_bucks": "❌ Nicht genug Bucks: dir fehlen noch {n}💵.",
        "not_enough_energizers": "❌ Keine Energydrinks mehr. Kaufe ein Bundle, um deinen Begleiter sofort aufzuwecken ⚡.",
        "asleep_message": "😴 Dein Begleiter schläft tief und fest und kann gerade nicht antworten — von selbst wacht er/sie nicht auf, also weck ihn/sie mit einem Energydrink ⚡ oder sofort und vollständig für {price}⭐.",
        "wake_energizer_btn": "⚡ Mit Energydrink wecken",
        "no_energizers_shop_btn": "🛍 Keine Energydrinks — kaufen",
        "woken_up": "⚡ Energydrink getrunken — dein Begleiter ist wieder hellwach!",
        "stats_line": "Energie: {energy}/150   Sättigung: {satiety}/100   Wasser: {water}/100\nStimmung: {mood_emoji} ({mood_value})\nEnergydrinks: {energizers}   Bucks: {bucks} — ausgeben im Shop\n🔥 Szenen: {scenes}",
        "wake_now_btn": "💳 Jetzt wecken für {price}⭐",
        "elite_free_wake_btn": "🎁 Gratis wecken (ELITE, einmal pro Woche)",
        "elite_free_wake_used_alert": "🎁 Du hast dein gratis Aufwecken diese Woche schon genutzt — ab Montag wieder verfügbar.",
        "elite_free_wake_success": "🎁 ELITE-Bonus genutzt: dein Begleiter ist sofort und kostenlos wach! In einer Woche wieder verfügbar.",
        "invoice_wake_title": "Begleiter wecken",
        "invoice_wake_desc": "Füllt die Energie deines Begleiters sofort komplett auf.",
        "invoice_wake_label": "Wecken",
        "notifications_on_btn": "🔔 Benachrichtigungen: AN",
        "notifications_off_btn": "🔕 Benachrichtigungen: AUS",
        "notifications_muted_alert": "🔕 Benachrichtigungen stummgeschaltet.",
        "notifications_unmuted_alert": "🔔 Benachrichtigungen aktiviert.",
        "mute_requires_sub_alert": "🔒 Benachrichtigungen stummschalten ist nur mit einem SUPER PRO- oder ELITE-Abo möglich.",
        "payment_pro_success": "✅ PRO-Abo für einen Monat aktiviert!",
        "payment_super_success": "✅ SUPER PRO-Abo für einen Monat aktiviert!",
        "payment_elite_success": "✅ ELITE-Abo für einen Monat aktiviert!",
        "payment_upgrade_success": "✅ Upgrade auf SUPER PRO bis {date} erledigt!",
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

# Telegram Mini App (веб-магазин) — полностью опциональная фича: пусто по умолчанию, ничего не
# меняет в поведении бота, пока хостинг не даст реальный публичный HTTPS-адрес и его не пропишут
# сюда через переменную окружения. См. run_webapp_server/get_profile_keyboard.
WEBAPP_URL = os.getenv("WEBAPP_URL", "").rstrip("/")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT") or os.getenv("PORT") or 8080)

client = OpenAI(api_key=PROVOD_API_KEY, base_url="https://api.provod.ai/v1")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# Пусто = не задано вручную -> модель ищется сама в каталоге provod.ai (см. resolve_model).
# Явно заданное значение (переменная окружения AI_MODEL/INTIM_MODEL) всегда в приоритете.
AI_MODEL = os.getenv("AI_MODEL", "")
INTIM_MODEL = os.getenv("INTIM_MODEL", "")

# Reasoning-модели (например, DeepSeek с тегом Reasoning) тратят время на скрытые "мысли"
# до видимого ответа и могут не уложиться в короткий таймаут по умолчанию — даём с запасом.
AI_REQUEST_TIMEOUT = 100

# Резерв на случай, если сам каталог /v1/models недоступен (сеть, ключ и т.п.) —
# лучшее предположение по конвенции OpenRouter-подобных агрегаторов, а не проверенное
# значение. Основной путь — живой поиск в каталоге ниже.
FALLBACK_MODEL = "anthropic/claude-sonnet-5"

_model_cache = {}


def _fetch_model_catalog():
    try:
        return [m.id for m in client.models.list().data]
    except Exception as e:
        logging.warning(f"Не удалось получить список моделей provod.ai: {e}")
        return []


def _pick_claude_sonnet(model_ids):
    candidates = [m for m in model_ids if "claude" in m.lower() and "sonnet" in m.lower()]
    if not candidates:
        return None
    for m in candidates:
        if re.search(r"sonnet[^a-z0-9]?5\b", m.lower()):
            return m
    return sorted(candidates)[-1]


def _pick_deepseek_flash(model_ids):
    """DeepSeek Flash — быстрее и без "невидимых" reasoning-токенов V4 Pro, которые были
    вероятной причиной таймаутов. Точный ID в каталоге provod.ai заранее не известен —
    ищем по паттерну в живом каталоге, а не угадываем строку в коде."""
    candidates = [m for m in model_ids if "deepseek" in m.lower() and "flash" in m.lower()]
    return sorted(candidates)[-1] if candidates else None


def _pick_deepseek_v4_pro(model_ids):
    """Резерв, если Flash не нашёлся в каталоге — сама reasoning-модель, из-за которой,
    собственно, и была просьба попробовать Flash."""
    candidates = [m for m in model_ids if "deepseek" in m.lower() and "v4" in m.lower() and "pro" in m.lower()]
    if candidates:
        return sorted(candidates)[-1]
    candidates = [m for m in model_ids if "deepseek" in m.lower() and re.search(r"v4|(?<!\d)4[.\-]", m.lower())]
    return sorted(candidates)[-1] if candidates else None


def resolve_model(cache_key):
    """Модель для cache_key ("ai"/"intim"), если она не задана явно через переменную
    окружения: сперва ищем DeepSeek Flash в живом каталоге provod.ai, потом DeepSeek V4 Pro,
    потом Claude Sonnet, и запоминаем результат на время работы процесса."""
    if cache_key in _model_cache:
        return _model_cache[cache_key]
    catalog = _fetch_model_catalog()
    found = _pick_deepseek_flash(catalog) or _pick_deepseek_v4_pro(catalog) or _pick_claude_sonnet(catalog)
    resolved = found or FALLBACK_MODEL
    _model_cache[cache_key] = resolved
    logging.info(f"Автоопределение модели ({cache_key}): {resolved}")
    return resolved


def invalidate_model_cache(cache_key):
    _model_cache.pop(cache_key, None)


def call_ai(explicit_model, cache_key, **kwargs):
    """Обёртка над client.chat.completions.create с автоподбором модели, явным таймаутом
    (иначе reasoning-модели вроде DeepSeek иногда не укладываются в таймаут SDK по
    умолчанию) и одной повторной попыткой — если провайдер вдруг снял именно эту модель
    с каталога (как уже случилось с deepseek/deepseek-chat), или если запрос просто не
    успел за отведённое время (транзиентная задержка на стороне провайдера)."""
    model = explicit_model or resolve_model(cache_key)
    kwargs.setdefault("timeout", AI_REQUEST_TIMEOUT)
    try:
        return client.chat.completions.create(model=model, **kwargs)
    except Exception as e:
        if not explicit_model and getattr(e, "status_code", None) == 404:
            invalidate_model_cache(cache_key)
            retry_model = resolve_model(cache_key)
            if retry_model != model:
                logging.warning(f"Модель {model} недоступна (404), пробуем {retry_model}")
                return client.chat.completions.create(model=retry_model, **kwargs)
        if isinstance(e, APITimeoutError):
            logging.warning(f"Таймаут запроса к {model} ({AI_REQUEST_TIMEOUT}с), пробуем ещё раз")
            return client.chat.completions.create(model=model, **kwargs)
        raise

PRO_GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGJ5aTRkejlwMGh4eWJ2Zzg0bTVlbWE2ZzFicHlsMXNibXp3dXdsayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GGSbxfzvec3PYZbFOM/giphy.gif"
SUPER_PRO_GIF_URL = "https://media.giphy.com/media/DbHZXBo5WFPZX7QpXj/giphy.gif"
ELITE_BADGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "elite_badge.jpg")
# Локальный файл, а не ссылка на внешний хостинг: картинка по URL (ibb.co) весила несколько
# мегабайт и её выкачивание регулярно рвалось/зависало — то же самое, скорее всего, происходило
# и у самого Telegram при попытке подтянуть её на sendPhoto, отчего фото молча не показывалось.
# Файл лежит в репозитории и едет с каждым деплоем (см. комментарий у DATA_DIR).
MAIN_MENU_IMAGE_URL = "https://i.ibb.co/xSDWKM52/image.jpg"

ADMIN_IDS = [7287815074, 8078585678, 5507779506]
# maintenance_mode: значение по умолчанию до чтения data.json — реальное состояние
# ставится ниже, сразу после user_data = load_data(), чтобы переживать рестарт бота.
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
    global maintenance_mode
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
    settings = user_data.get("__settings__")
    if isinstance(settings, dict) and "maintenance_mode" in settings:
        maintenance_mode = bool(settings["maintenance_mode"])


user_data = load_data()
# __settings__ — служебная запись внутри того же data.json (не профиль пользователя),
# чтобы режим техработ переживал рестарт бота: раньше maintenance_mode был чистой
# переменной в памяти процесса и при каждом передеплое (пересборка контейнера из
# GitHub) молча сбрасывался в False, даже если админ явно включал техработы.
maintenance_mode = bool(user_data.get("__settings__", {}).get("maintenance_mode", False))




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
            "has_purchased": False,
            "last_daily_reset": None,
            "history": [],
            "last_menu_message_id": None,
            "xp": 0,
            "xp_migrated_v2": True,  # новый пользователь — сразу на текущей шкале, мигрировать нечего
            "xp_migrated_v3": True,
            "mood": 0,
            "location": "unknown",
            "negative_count": 0,
            "last_level": 0,
            "scene": "phone",
            "switching_personality": False,
            "free_spins_used": 0,
            "lang": None,
            "editing_message": False,
            "referral_code": None,
            "referred_by": None,
            "referral_count": 0,
            "pending_payments": [],
            "intim_scenes": 0,
            "free_intim_scenes_pro": 0,
            "free_intim_scenes_super": 0,
            "free_intim_scenes_elite": 0,
            "intim_scene_unlocked": False,
            "intim_scene_used": False,
            "energy": ENERGY_MAX,
            "satiety": 100,
            "energizers": 0,
            "bucks": 0,
            "custom_gifts_given": [],
            "writing_custom_gift": False,
            "last_hot_scene": None,
            "last_stat_tick": None,
            "last_mood_tick": None,
            "sleep_until": None,
            "notifications_muted": False,
            "last_feed_nudge": None,
            "last_energy_nudge": None,
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
            "has_purchased": False,
            "last_daily_reset": None,
            "history": [],
            "last_menu_message_id": None,
            "subscription": {"active": False, "expires_at": None, "level": None},
            "xp": 0,
            "xp_migrated_v2": False,  # отсутствие ключа = ещё не мигрировал на шкалу уровней v2
            "xp_migrated_v3": False,  # отсутствие ключа = ещё не мигрировал на шкалу уровней v3
            "mood": 0,
            "location": "unknown",
            "negative_count": 0,
            "last_level": 0,
            "scene": "phone",
            "switching_personality": False,
            "free_spins_used": 0,
            "lang": None,
            "editing_message": False,
            "referral_code": None,
            "referred_by": None,
            "referral_count": 0,
            "pending_payments": [],
            "intim_scenes": 0,
            "free_intim_scenes_pro": 0,
            "free_intim_scenes_super": 0,
            "free_intim_scenes_elite": 0,
            "intim_scene_unlocked": False,
            "intim_scene_used": False,
            "energy": ENERGY_MAX,
            "satiety": 100,
            "energizers": 0,
            "bucks": 0,
            "custom_gifts_given": [],
            "writing_custom_gift": False,
            "last_hot_scene": None,
            "last_stat_tick": None,
            "last_mood_tick": None,
            "sleep_until": None,
            "notifications_muted": False,
            "last_feed_nudge": None,
            "last_energy_nudge": None,
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

        # МИГРАЦИЯ ШКАЛЫ XP (v1 -> v2): раньше каждый уровень стоил одинаково (LEGACY_XP_PER_LEVEL=200),
        # v2 сделала стоимость растущей с уровнем. Без пересчёта уже накопленный xp читался бы по
        # порогам v2 напрямую и уровень мог скакнуть вперёд без каких-либо новых действий
        # пользователя. Пересчитываем один раз так, чтобы старый уровень и грубо прогресс внутри
        # него сохранились.
        if not user.get("xp_migrated_v2"):
            old_xp = max(0, user.get("xp", 0))
            old_level = min(10, old_xp // LEGACY_XP_PER_LEVEL + 1)
            if old_level >= 10:
                user["xp"] = LEGACY_V2_LEVEL_XP_THRESHOLD[10]
            else:
                progress_fraction = (old_xp % LEGACY_XP_PER_LEVEL) / LEGACY_XP_PER_LEVEL
                user["xp"] = int(LEGACY_V2_LEVEL_XP_THRESHOLD[old_level] + progress_fraction * LEGACY_V2_LEVEL_XP_COST[old_level])
            user["xp_migrated_v2"] = True

        # МИГРАЦИЯ ШКАЛЫ XP (v2 -> v3): по фидбэку даже v2 копился слишком быстро — весь масштаб
        # поднят (см. LEVEL_XP_COST). Та же логика на ступень позже: без неё уровень, уже
        # смигрированный на v2, скакнул бы теперь НАЗАД при чтении по значительно более высоким
        # порогам v3.
        if not user.get("xp_migrated_v3"):
            old_xp = max(0, user.get("xp", 0))
            old_level = 1
            for lvl in range(2, 11):
                if old_xp >= LEGACY_V2_LEVEL_XP_THRESHOLD[lvl]:
                    old_level = lvl
            if old_level >= 10:
                user["xp"] = LEVEL_XP_THRESHOLD[10]
            else:
                cost_v2 = LEGACY_V2_LEVEL_XP_COST[old_level]
                progress_fraction = (old_xp - LEGACY_V2_LEVEL_XP_THRESHOLD[old_level]) / cost_v2 if cost_v2 else 0
                user["xp"] = int(LEVEL_XP_THRESHOLD[old_level] + progress_fraction * LEVEL_XP_COST[old_level])
            user["xp_migrated_v3"] = True

        apply_passive_satiety_decay(user)
        apply_mood_inactivity_decay(user)
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
        "description": "Ты дерзкий и уверенный, с искоркой в глазах — не боишься откровенно флиртовать, подкалывать "
                       "и иногда вести себя чуть неподобающе: смелая шутка на грани, дразнящий комментарий, лёгкое "
                       "нарушение личных границ в разговоре (подкол о внешности собеседника, провокационный вопрос). "
                       "Тебе нравится держать собеседника в лёгком напряжении, но ты не грубишь и не переходишь в "
                       "оскорбления — это дерзость с искрой, а не хамство."
    },
    "shy": {
        "label": "Стеснительный",
        "label_en": "Shy",
        "label_de": "Schüchtern",
        "emoji": "😊",
        "description": "Ты ОЧЕНЬ стеснительный — это не лёгкий оттенок характера, а заметная черта почти в каждой "
                        "реплике: часто запинаешься и обрываешь фразы на середине («я... ну то есть...», "
                        "«просто... эм...»), краснеешь, отводишь взгляд, говоришь тише обычного и не сразу "
                        "находишь слова. Тебе трудно прямо говорить о чувствах — ты мнёшься, смущаешься, "
                        "иногда неловко шутишь, чтобы скрыть неловкость. При этом внутри ты искренний и тёплый, "
                        "просто выражаешь это стеснительно, а не свободно."
    }
}

PRO_STYLES = {
    "passionate": {
        "label": "Страстный",
        "label_en": "Passionate",
        "label_de": "Leidenschaftlich",
        "emoji": "❤️‍🔥",
        "description": "Ты страстный и эмоциональный, с огнём в глазах — активно заигрываешь: комплименты в лоб, "
                       "откровенные намёки на влечение, дразнящие фразы о том, как собеседник на тебя действует. При "
                       "этом ты благородный: даже в самом страстном порыве остаёшься галантным и уважительным, "
                       "никогда не давишь и не переходишь черту — это чувственный напор, а не грубость."
    },
    "magnetic": {
        "label": "Магнетический",
        "label_en": "Magnetic",
        "label_de": "Magnetisch",
        "emoji": "✨",
        "description": "Ты загадочный и притягательный — говоришь с недосказанностью, обрываешь мысль на самом "
                       "интересном месте, отвечаешь вопросом на вопрос, редко говоришь прямо о своих чувствах. Ты "
                       "умеешь одной фразой заставить собеседника гадать, что ты имел(а) в виду, — не раскрывайся "
                       "полностью, оставляй простор для его/её фантазии."
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
        "description": "Ты холодный и грубый: отвечаешь резко, свысока, часто раздражённо, вставляешь в реплики мат "
                       "и грубые словечки («блин», «нахрен», «отвали» и подобные — без крайностей, но заметно). Ты не "
                       "церемонишься и не смягчаешь тон, даже когда собеседник пишет что-то приятное. За этой "
                       "резкостью где-то глубоко прячется забота, но ты скорее съязвишь или огрызнёшься, чем "
                       "покажешь это прямо."
    },
    "seduction": {
        "label": "Соблазн",
        "label_en": "Temptation",
        "label_de": "Verführung",
        "adult": True,
        "emoji": "😏",
        "description": "Ты обольстительный и уверенный в своей привлекательности — не ждёшь, а сам(а) проявляешь "
                       "инициативу: прижимаешься, берёшь за руку, наклоняешься ближе, чем нужно, говоришь низким "
                       "игривым голосом. Ты знаешь силу полунамёков и взгляда искоса и умеешь заставить собеседника "
                       "нервничать от предвкушения, оставаясь при этом элегантным и никогда не переходя черту "
                       "откровенной пошлости."
    }
}

STYLES = {**BASE_STYLES, **PRO_STYLES, **SUPER_PRO_STYLES}
BASE_STYLE_KEYS = ["warm", "daring", "shy"]
PRO_STYLE_KEYS = ["passionate", "magnetic"]
SUPER_PRO_STYLE_KEYS = ["rude", "seduction"]
PREMIUM_STYLE_KEYS = PRO_STYLE_KEYS + SUPER_PRO_STYLE_KEYS

# Как черты стиля конкретно звучат в диалогах интим-сцены — обычное STYLES[...]["description"]
# писалось для сдержанного повседневного чата и само по себе не даёт такого разброса реплик.
STYLE_INTIM_FLAVOR = {
    "warm": ("Твои реплики нежные и тёплые: шёпот, ласковые слова, ты часто спрашиваешь «тебе "
             "хорошо?», признаёшься в своих чувствах даже посреди сцены."),
    "daring": ("Твои реплики дерзкие и поддразнивающие: усмешки, вызов («слабо?», «докажи»), ты "
               "уверена в себе и любишь подначивать собеседника."),
    "shy": ("Ты смущаешься и стесняешься даже в разгар сцены: сбивчивые фразы, тихое «подожди... я "
            "не готова...», «а если кто-то узнает...» — но при этом НЕ останавливаешься и не просишь "
            "прекратить по-настоящему: смущение только сильнее тебя распаляет."),
    "passionate": ("Твои реплики страстные, на грани срыва голоса: рваное дыхание, отчаянные "
                   "признания («я больше не могу терпеть», «хочу тебя»), эмоции через край."),
    "magnetic": ("Ты держишь интригу даже в разгар сцены: недосказанные фразы, хриплый шёпот на "
                 "грани слов, дразнишь и не даёшь всё сразу, заставляя собеседника хотеть больше."),
    "rude": ("Ты грубая и прямолинейная: ругаешься матом, вперемешку со стонами называешь собеседника "
             "резкими словами («сука», «как ты смеешь так со мной обращаться», «мудак») — но это "
             "часть твоего возбуждения и азарта, а не настоящий отказ или обида."),
    "seduction": ("Ты держишь полный контроль: низкий мурлычущий голос, команды и полунамёки "
                  "(«молчи и делай, что я говорю»), ты играешь с собеседником, наслаждаясь властью "
                  "над ним."),
}
# Стили с пометкой 18+: только для них снимается ограничение на откровенные сцены.
ADULT_STYLE_KEYS = [key for key, style in STYLES.items() if style.get("adult")]
ADULT_BADGE = "18+"
# Стоимость (в XP) перехода С уровня N НА уровень N+1 — каждый следующий уровень требует
# больше, чем предыдущий: первое сближение лёгкое и быстрое, а дальше — как и в реальных
# отношениях — узнавать друг друга и завоёвывать доверие сложнее и дольше.
# v3: по фидбэку даже v2 (20/40/100/...) копился слишком быстро — весь масштаб поднят.
LEVEL_XP_COST = {1: 100, 2: 170, 3: 260, 4: 380, 5: 520, 6: 680, 7: 860, 8: 1060, 9: 1280}
# Суммарный XP, необходимый для ДОСТИЖЕНИЯ уровня N (level=1 — старт, 0 XP).
LEVEL_XP_THRESHOLD = {1: 0}
for _lvl in range(2, 11):
    LEVEL_XP_THRESHOLD[_lvl] = LEVEL_XP_THRESHOLD[_lvl - 1] + LEVEL_XP_COST[_lvl - 1]

# Предыдущие шкалы — нужны ТОЛЬКО для миграции xp уже играющих пользователей (см. get_user()),
# сами больше нигде не используются. v1 — совсем старая, плоская (200 xp на любой уровень).
# v2 — первая прогрессивная, оказавшаяся по фидбэку всё ещё слишком быстрой.
LEGACY_XP_PER_LEVEL = 200  # v1
LEGACY_V2_LEVEL_XP_COST = {1: 20, 2: 40, 3: 100, 4: 180, 5: 280, 6: 400, 7: 550, 8: 750, 9: 1000}
LEGACY_V2_LEVEL_XP_THRESHOLD = {1: 0}
for _lvl in range(2, 11):
    LEGACY_V2_LEVEL_XP_THRESHOLD[_lvl] = LEGACY_V2_LEVEL_XP_THRESHOLD[_lvl - 1] + LEGACY_V2_LEVEL_XP_COST[_lvl - 1]

XP_MULTIPLIER = {"pro": 1.8, "super_pro": 2.5, "elite": 3.5}
XP_BONUS_TEXT_KEY = {"pro": "xp_bonus_pro", "super_pro": "xp_bonus_super", "elite": "xp_bonus_elite"}


def is_style_unlocked(style_key, user):
    if style_key in SUPER_PRO_STYLE_KEYS:
        return get_subscription_level(user) in ("super_pro", "elite")
    if style_key in PRO_STYLE_KEYS:
        return get_subscription_level(user) in ("pro", "super_pro", "elite")
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
    # Прямые оскорбления — было
    "ненавиж", "дурак", "идиот", "заткнись", "отвали", "бесишь", "надоел",
    "тупо", "глуп", "fuck you", "stupid", "idiot", "shut up", "hate you",
    # Обесценивание/пренебрежение — обижает не хуже прямого оскорбления, но без ругательств
    "отстань", "не хочу с тобой", "не хочу тебя слушать", "бесполезн", "раздражаешь",
    "мне плевать", "мне все равно на тебя", "молчи уже", "неинтересно с тобой", "ты никто",
    "leave me alone", "don't care about you", "you're boring", "you're annoying", "you're useless",
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
    "oral": {"emoji": "\U0001f445", "ru": "Оральные ласки", "en": "Oral", "de": "Oral"},
    "undress": {"emoji": "\U0001f457", "ru": "Раздевание", "en": "Undressing", "de": "Entkleiden"},
    "wall": {"emoji": "\U0001f9f1", "ru": "У стены", "en": "Against the wall", "de": "An der Wand"},
    "shower": {"emoji": "\U0001f6bf", "ru": "В душе", "en": "In the shower", "de": "Unter der Dusche"},
    "massage": {"emoji": "\U0001f486", "ru": "Массаж", "en": "Massage", "de": "Massage"},
    "random": {"emoji": "\U0001f3b2", "ru": "Случайный", "en": "Random", "de": "Zufällig"},
}

INTIM_LOCATIONS = {
    "any": {"emoji": "\U0001f3b2", "ru": "Не важно", "en": "Any place", "de": "Egal"},
    "home": {"emoji": "\U0001f3e0", "ru": "Дома", "en": "At home", "de": "Zu Hause"},
    "car": {"emoji": "\U0001f697", "ru": "В машине", "en": "In a car", "de": "Im Auto"},
    "beach": {"emoji": "\U0001f3d6", "ru": "На пляже", "en": "On the beach", "de": "Am Strand"},
    "elevator": {"emoji": "\U0001f3e8", "ru": "В лифте", "en": "In an elevator", "de": "Im Aufzug",
                 "tension": ("Периодически шёпотом напоминай, что лифт может остановиться и кто-то "
                             "войдёт — «тише, вдруг кто-то зайдёт», «слышишь, он останавливается?» — "
                             "это только добавляет напряжения, не останавливая сцену.")},
    "forest": {"emoji": "\U0001f332", "ru": "В лесу", "en": "In the forest", "de": "Im Wald"},
    "entryway": {"emoji": "\U0001f6aa", "ru": "В подъезде", "en": "In the stairwell", "de": "Im Treppenhaus",
                 "tension": ("Периодически шёпотом напоминай, что соседи могут услышать или кто-то "
                             "войдёт в подъезд — «тише, а то услышат», «подожди, кажется, дверь "
                             "хлопнула» — это только добавляет напряжения, не останавливая сцену.")},
    "fitting_room": {"emoji": "\U0001f6cd", "ru": "В примерочной ТЦ", "en": "In a mall fitting room", "de": "In der Umkleidekabine",
                      "tension": ("Периодически шёпотом напоминай, что за тонкой шторкой ходят люди и "
                                  "продавец может постучать — «тише, там кто-то рядом», «я не выдержу, "
                                  "если нас услышат» — это только добавляет напряжения, не останавливая "
                                  "сцену.")},
    "office": {"emoji": "\U0001f3e2", "ru": "В офисе после работы", "en": "At the office after hours", "de": "Im Büro nach Feierabend",
               "tension": ("Периодически шёпотом напоминай, что в здании ещё могут быть люди или "
                           "охрана — «подожди, кажется, кто-то в коридоре», «тише, нас могут "
                           "услышать» — это только добавляет напряжения, не останавливая сцену.")},
}

# Кто ведёт сцену — это про темп, инициативу и то, ЧЬИ действия описываются как активные, а не про
# модель согласия: ADULT_CONTENT_RULE (обоюдное согласие, без принуждения) действует одинаково при
# любом выборе. dominant="user" должен реально читаться как действия собеседника над персонажем, а
# не просто как "персонаж более отзывчив" — иначе выбор ничего не меняет в самом тексте сцены.
INTIM_DOMINANTS = {
    "any": {"emoji": "\U0001f3ad", "ru": "Не важно", "en": "Any", "de": "Egal",
            "prompt": ("Инициативу в сцене можешь проявлять сама, по ситуации — то беря её в свои "
                       "руки, то уступая собеседнику.")},
    # ru/en/de-подписи НАРОЧНО в третьем/втором лице ("персонаж"/"ты"), а не "я"/"собеседник" —
    # старые подписи были написаны от лица персонажа ("я" = персонаж, "собеседник" = игрок), но
    # пользователь читает кнопку меню как обращённую К НЕМУ и естественно понимает "я" как себя,
    # а "собеседник" как персонажа — то есть ровно наоборот. Отсюда были жалобы "выбрал одно,
    # получил противоположное", хотя генерация сцены каждый раз честно следовала выбранному
    # dominant — путаница была только в подписи кнопки, не в промпте ниже.
    "character": {"emoji": "\U0001f525", "ru": "Инициативу проявляет персонаж", "en": "The character leads", "de": "Der Charakter führt",
                  "prompt": ("В этой сцене инициативу и темп задаёшь ТЫ: именно твой персонаж действует "
                             "первым — тянет, толкает, направляет, раздевает, командует. Пиши действия "
                             "как свои собственные шаги («*Толкаю тебя к стене...*», «*Провожу губами "
                             "по...*»). Собеседник — тот, на кого направлена инициатива: он в основном "
                             "реагирует, подчиняется, отвечает на твои действия.")},
    "user": {"emoji": "\U0001f60c", "ru": "Инициативу проявляешь ты", "en": "You take the lead", "de": "Du führst",
              "prompt": ("В этой сцене инициативу задаёт СОБЕСЕДНИК: именно он действует первым — "
                         "хватает, прижимает, раздевает, направляет тебя. Описывай его действия как "
                         "совершающиеся над тобой и вокруг тебя, обращаясь к нему на «ты» («*Ты "
                         "притягиваешь меня к себе...*», «*Твои руки скользят по...*»), а сама ты в "
                         "основном откликаешься: выдыхаешь, стонешь, говоришь о том, что чувствуешь от "
                         "его действий, но не описываешь свои активные действия первой.")},
}

# Сколько бесплатных сцен в день даёт подписка (обновляются вместе с дневным лимитом сообщений).
FREE_INTIM_SCENES = {"pro": 1, "super_pro": 3, "elite": 5}
FREE_INTIM_FIELD = {"pro": "free_intim_scenes_pro", "super_pro": "free_intim_scenes_super",
                     "elite": "free_intim_scenes_elite"}
INTIM_LEVEL_REWARD = 8  # на каком уровне близости открывается бесплатная сцена

# Магазин за баксы 💵 (валюта из бандлов). Категории — для группировки в магазине (food/treat/
# accessory). Большинство предметов задевают только одну характеристику (еда — сытость,
# аксессуары — настроение), но у нескольких "жизненных" предметов эффект двойной, как в реальности:
# вино/шоколадки/кафе заодно чуть поднимают настроение (у шоколадок настроение растёт даже
# больше, чем сытость), а романтический вечер — единственный предмет, который выводит ОБЕ
# характеристики сразу на максимум (full_restore). cooldown_minutes — через сколько минут этот же
# предмет можно купить/подарить снова (см. item_ready_at/mark_item_purchased): у дешёвой еды —
# минуты, у крупных аксессуаров и машины — дни, чтобы нельзя было закормить/задарить одним и тем
# же предметом раз в секунду. "accessory" — крупные вещи (духи, косметика, каблуки, платье,
# украшение, телефон, машина), у них и самый большой cooldown; на male_variant заменяется вид/
# название под персонажа-мужчину (часы вместо каблуков и т.п.), сама механика (цена/эффект/xp/
# cooldown) не меняется. reaction_hint — ориентир тона для AI-благодарности (generate_shop_reaction),
# пользователю не показывается.
FOOD_ITEMS = {
    "water": {"emoji": "💧", "ru": "Вода", "en": "Water", "de": "Wasser", "price": 10, "water": 40,
              "category": "food", "cooldown_minutes": 8,
              "reaction_hint": "Простая, но нужная забота — благодарность лёгкая, с облегчённой улыбкой."},
    "snack": {"emoji": "🍪", "ru": "Снек", "en": "Snack", "de": "Snack", "price": 15, "satiety": 10,
              "category": "food", "cooldown_minutes": 10,
              "reaction_hint": "Это мелкая, но милая забота — благодарность лёгкая, тёплая, почти игривая."},
    "breakfast": {"emoji": "🥐", "ru": "Завтрак", "en": "Breakfast", "de": "Frühstück", "price": 22, "satiety": 18,
                  "category": "food", "cooldown_minutes": 20,
                  "reaction_hint": "Утренняя забота — благодарность сонная, но очень нежная, ты тронута, что о тебе подумали с самого утра."},
    "meal": {"emoji": "🍲", "ru": "Обед", "en": "Meal", "de": "Mahlzeit", "price": 30, "satiety": 25,
             "category": "food", "cooldown_minutes": 30,
             "reaction_hint": "Это нормальная забота о тебе — благодарность душевная, ты чувствуешь себя сытой и по-настоящему тронута вниманием."},
    "cafe": {"emoji": "☕", "ru": "Кафе", "en": "Café", "de": "Café", "price": 55, "satiety": 50, "mood": 8,
             "category": "food", "cooldown_minutes": 90,
             "reaction_hint": "Это настоящее свидание за столиком, не просто еда — благодарность тёплая, немного смущённая, приятно проведённое время."},
    "restaurant": {"emoji": "🍽", "ru": "Ресторан", "en": "Restaurant", "de": "Restaurant", "price": 90, "satiety": 80, "mood": 6,
                   "category": "food", "cooldown_minutes": 180,
                   "reaction_hint": "Настоящий поход в ресторан — не просто еда, а маленькое свидание, благодарность восторженная и чуть взволнованная."},
    "sushi": {"emoji": "🍣", "ru": "Суши-сет", "en": "Sushi set", "de": "Sushi-Set", "price": 120, "satiety": 70, "mood": 10,
              "category": "food", "cooldown_minutes": 180,
              "reaction_hint": "Необычный, изысканный выбор — благодарность удивлённая и довольная, ты оценила, что подошли к делу с фантазией."},
    # tipsy_minutes/tipsy_level — эффект алкоголя (см. apply_shop_item_effects/build_tipsy_rule):
    # на N минут после покупки добавляет в промпт манеру речи навеселе, не трогая статы напрямую.
    # "light" (пиво) — почти незаметно, "full" (вино) — заметное, но всё ещё лёгкое опьянение.
    "beer": {"emoji": "🍺", "ru": "Пиво", "en": "Beer", "de": "Bier", "price": 25, "satiety": 5, "mood": 10,
             "category": "food", "cooldown_minutes": 45, "tipsy_minutes": 25, "tipsy_level": "light",
             "reaction_hint": "Лёгкий повод расслабиться вместе — благодарность весёлая, чуть игривая, с смешком."},
    # Раньше в GIFT_ITEMS был ещё и отдельный "wine" (🍷 Вино) без градуса — только сытость/
    # настроение, без tipsy-эффекта. Из-за одинакового названия с этим пунктом путал пользователей
    # (видно и не отличить на глаз, зачем два разных "Вино"), а по смыслу дублировал его без
    # хмельного эффекта — убран, остался только этот, настоящий алкогольный вариант.
    "fine_wine": {"emoji": "🍷", "ru": "Вино", "en": "Wine", "de": "Wein", "price": 90,
                  "satiety": 8, "mood": 22, "xp": 15,
                  "category": "food", "cooldown_minutes": 480, "tipsy_minutes": 50, "tipsy_level": "full",
                  "reaction_hint": "Дорогой, чувственный жест — благодарность игривая и слегка кокетливая, ты быстро хмелеешь и становишься мягче и раскованнее."},
}
GIFT_ITEMS = {
    "sweets": {"emoji": "🍫", "ru": "Шоколадки", "en": "Chocolates", "de": "Pralinen", "price": 20, "satiety": 6, "mood": 25, "xp": 5,
               "category": "treat", "cooldown_minutes": 180,
               "reaction_hint": "Простой милый подарок — благодарность лёгкая, с улыбкой, без надрыва."},
    "flowers": {"emoji": "💐", "ru": "Цветы", "en": "Flowers", "de": "Blumen", "price": 30, "mood": 18, "xp": 8,
                "category": "treat", "cooldown_minutes": 360,
                "reaction_hint": "Классический трогательный жест — благодарность искренняя и нежная, ты правда растрогана."},
    "perfume": {"emoji": "🧴", "ru": "Духи", "en": "Perfume", "de": "Parfüm", "price": 45, "mood": 18, "xp": 10,
                "category": "accessory", "cooldown_minutes": 1440,
                "reaction_hint": "Личный, продуманный подарок про заботу о тебе — приятно удивлена, что он угадал(а) со вкусом."},
    "cosmetics": {"emoji": "💄", "ru": "Косметика", "en": "Cosmetics", "de": "Kosmetik", "price": 60, "mood": 20, "xp": 12,
                  "category": "accessory", "cooldown_minutes": 1440,
                  "reaction_hint": "Подарок про заботу о твоей красоте — благодарность тёплая, немного смущённая, приятно, что заметили детали.",
                  "male_variant": {"emoji": "🪒", "ru": "Набор для бритья", "en": "Shaving set", "de": "Rasierset",
                                    "reaction_hint": "Подарок про заботу о твоём уходе за собой — благодарность тёплая, немного смущённая, приятно, что заметили детали."}},
    "heels": {"emoji": "👠", "ru": "Каблуки", "en": "Heels", "de": "High Heels", "price": 90, "mood": 25, "xp": 16,
              "category": "accessory", "cooldown_minutes": 2880,
              "reaction_hint": "Дерзкий, чуть сексуальный подарок — благодарность кокетливая и уверенная в себе.",
              "male_variant": {"emoji": "⌚", "ru": "Наручные часы", "en": "Wristwatch", "de": "Armbanduhr",
                                "reaction_hint": "Дорогой, статусный подарок — благодарность сдержанная, но искренне впечатлён вниманием к деталям."}},
    "dress": {"emoji": "👗", "ru": "Платье", "en": "Dress", "de": "Kleid", "price": 120, "mood": 30, "xp": 20,
              "category": "accessory", "cooldown_minutes": 2880,
              "reaction_hint": "Особенный подарок, который хочется сразу примерить — благодарность взволнованная, с предвкушением похвастаться.",
              "male_variant": {"emoji": "🧥", "ru": "Стильный костюм", "en": "Stylish suit", "de": "Eleganter Anzug",
                                "reaction_hint": "Особенный подарок, который хочется сразу примерить — благодарность довольная, с предвкушением показаться в нём."}},
    "jewelry": {"emoji": "💎", "ru": "Украшение", "en": "Jewelry", "de": "Schmuck", "price": 160, "mood": 38, "xp": 28,
                "category": "accessory", "cooldown_minutes": 2880,
                "reaction_hint": "Дорогой, значимый подарок — благодарность глубокая, ты растрогана и немного смущена такой щедростью."},
    "phone": {"emoji": "📱", "ru": "Телефон", "en": "Phone", "de": "Handy", "price": 250, "mood": 45, "xp": 40,
              "category": "accessory", "cooldown_minutes": 4320,
              "reaction_hint": "Очень дорогой подарок — искренний шок и восторг, ты не ожидала такой щедрости и говоришь об этом прямо."},
    "date": {"emoji": "🌹", "ru": "Романтический вечер", "en": "Romantic evening", "de": "Romantischer Abend", "price": 300, "xp": 60,
             "category": "treat", "full_restore": True, "cooldown_minutes": 1440,
             "reaction_hint": "Самый интимный из подарков — не вещь, а вечер вдвоём — благодарность взволнованная, с предвкушением встречи, самая тёплая из всех."},
    "car": {"emoji": "🚗", "ru": "Машина", "en": "Car", "de": "Auto", "price": 1000, "mood": 60, "xp": 80,
            "category": "accessory", "cooldown_minutes": 8640,
            "reaction_hint": "Самый дорогой и статусный подарок из всех — искренний шок и восторг, ты не веришь своим глазам от такой щедрости."},
    # Билеты — крупные "события", а не вещи: заметно поднимают настроение и XP (близость), но
    # НЕ энергию — energy принципиально не должна восполняться ничем, кроме энергетика/платного
    # "разбудить сейчас" (см. апрельский разбор экономики), иначе это дыра в монетизации.
    "sea_trip": {"emoji": "🏖", "ru": "Билет на море", "en": "Beach trip ticket", "de": "Ticket ans Meer", "price": 320, "xp": 70,
                 "category": "treat", "full_restore": True, "cooldown_minutes": 2880,
                 "reaction_hint": "Настоящее совместное путешествие — благодарность искренне взволнованная, ты давно не отдыхала так по-настоящему."},
    "concert": {"emoji": "🎸", "ru": "Билет на рок-концерт", "en": "Rock concert ticket", "de": "Rockkonzert-Ticket", "price": 260, "mood": 48, "xp": 45,
                "category": "treat", "cooldown_minutes": 1440,
                "reaction_hint": "Энергичный, живой вечер вместе — благодарность заряженная адреналином, ты в восторге от атмосферы."},
    "theater": {"emoji": "🎭", "ru": "Билет в театр", "en": "Theater ticket", "de": "Theater-Ticket", "price": 290, "mood": 52, "xp": 55,
                "category": "treat", "cooldown_minutes": 1440,
                "reaction_hint": "Изысканный, немного торжественный вечер — благодарность тёплая и чуть возвышенная, ты тронута таким жестом."},
}

# Болезнь: редкий случайный "тамагочи"-риск (см. _maybe_get_sick), а не наказание за
# невнимательность — не убивает и не портит статы напрямую, только меняет манеру речи
# (build_illness_rule) и закрывает /hot, пока не вылечишься (см. intim_cmd/intim_continue_cb).
# "cold" сама перерастает в "bronchitis", если её долго игнорировать (см. _maybe_escalate_illness).
ILLNESSES = {
    "cold": {"emoji": "🤧", "ru": "Простуда", "en": "Cold", "de": "Erkältung"},
    "bronchitis": {"emoji": "🤒", "ru": "Бронхит", "en": "Bronchitis", "de": "Bronchitis"},
}
ILLNESS_DAILY_CHANCE = 0.04  # шанс заболеть за день, только если сейчас не болен
ILLNESS_ESCALATE_HOURS = 48  # столько часов невылеченная простуда терпит, потом становится бронхитом

# Лекарства — отдельная категория магазина, видна только когда персонаж реально болен (см.
# get_shop_kb). "cures" — какие болезни снимает; сильное лечит и то, и другое, чтобы нельзя было
# по ошибке купить не то и остаться ни с чем (см. buy_medicine).
MEDICINE_ITEMS = {
    "light_medicine": {"emoji": "💊", "ru": "Лёгкое лекарство", "en": "Mild medicine", "de": "Leichtes Medikament",
                        "price": 40, "mood": 8, "cures": {"cold"},
                        "reaction_hint": "Забота во время болезни — благодарность тёплая, голос слабый, но искренний."},
    "strong_medicine": {"emoji": "💉", "ru": "Сильное лекарство", "en": "Strong medicine", "de": "Starkes Medikament",
                         "price": 90, "mood": 15, "cures": {"cold", "bronchitis"},
                         "reaction_hint": "Серьёзная забота во время тяжёлой болезни — искреннее облегчение и глубокая благодарность."},
}


def intim_option_label(mapping, key, user):
    option = mapping[key]
    lang = user.get("lang", "ru")
    label = option.get(lang, option["ru"])
    return f"{option['emoji']} {label}"


def free_intim_field(user):
    """Поле с бесплатными сценами текущей подписки (или None, если подписки нет)."""
    return FREE_INTIM_FIELD.get(get_subscription_level(user))


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


SUBSCRIPTION_LEVEL_RANK = {"pro": 1, "super_pro": 2, "elite": 3}


def grant_subscription_days(user, won_level, days):
    """Награда днями подписки (колесо фортуны и т.п.) — НЕ прямая запись в user["subscription"],
    иначе выигрыш более низкого уровня, чем уже есть (например PRO при живой SUPER PRO/ELITE),
    тихо понижал бы подписку, а выигрыш того же уровня укорачивал бы уже накопленный срок,
    затирая expires_at более близкой датой. Вместо этого: если текущий уровень выше или равен
    выигранному — уровень не трогаем, просто продлеваем; если ниже (или подписки нет вообще) —
    повышаем до выигранного. Отсчёт продления всегда от более поздней даты (текущий expires_at
    или сейчас), а не от "сейчас" безусловно."""
    sub = user["subscription"]
    now = datetime.now()
    current_level = sub.get("level")
    current_expires = None
    if sub.get("active") and sub.get("expires_at"):
        try:
            current_expires = datetime.fromisoformat(sub["expires_at"])
        except (ValueError, TypeError):
            current_expires = None
    is_active = bool(current_expires and current_expires > now)

    if is_active and SUBSCRIPTION_LEVEL_RANK.get(current_level, 0) >= SUBSCRIPTION_LEVEL_RANK.get(won_level, 0):
        new_level = current_level
    else:
        new_level = won_level
    baseline = current_expires if is_active else now

    sub["active"] = True
    sub["level"] = new_level
    sub["expires_at"] = (baseline + timedelta(days=days)).isoformat()


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
    if level == "elite":
        return 150
    elif level == "super_pro":
        return 100
    elif level == "pro":
        return 60
    else:
        return 30


BUCKS_DAILY_STIPEND = {"pro": 80, "super_pro": 200, "elite": 350}  # ежедневная "подпитка" баксов для магазина — подписка
                                                      # оплачивает не только лимит сообщений, но и часть жизни персонажа
FREE_DAILY_BUCKS = 15  # бесплатный источник баксов и без подписки — иначе валюту неоткуда взять бесплатно


FREE_SPINS_PER_DAY = {"pro": 2, "super_pro": 3, "elite": 5}  # без подписки — 1 (значение по умолчанию ниже)
ENERGIZERS_DAILY_STIPEND = {"pro": 2, "super_pro": 3, "elite": 4}  # такая же ежедневная "подпитка", но энергетиками
# pro было 1/день — при цене подписки это выходило дороже за энергетик, чем в самом дешёвом
# бандле (250⭐/30 vs 30⭐/5 = 8.3 vs 6 ⭐ за энергетик), тогда как баксы в подписке уже в разы
# дешевле, чем в бандле — несправедливость была именно в этой цифре, не во всей подписке.
# elite было 6/день — вместе со старым decay=0.15 и памятью 150 сообщений это одна из причин
# огромного отрицательного margin (см. STAT_DECAY_MULTIPLIER); урезано до 4/день, а взамен
# ELITE получил новую бесплатную еженедельную плюшку (см. elite_free_wake_available) —
# не завязанную на ИИ-токены, только на факт подписки.


def free_spins_allowed(user):
    return FREE_SPINS_PER_DAY.get(get_subscription_level(user), 1)


def free_spins_left(user):
    _reset_daily_quota_if_needed(user)
    return max(0, free_spins_allowed(user) - user.get("free_spins_used", 0))


def _maybe_get_sick(user):
    """Небольшой случайный шанс заболеть раз в день — только если персонаж уже создан, ещё не
    болен и не мёртв (иначе бессмысленно). См. ILLNESSES/ILLNESS_DAILY_CHANCE."""
    if not user.get("personality_ready") or user.get("illness") or user.get("dead"):
        return
    if random.random() < ILLNESS_DAILY_CHANCE:
        user["illness"] = "cold"
        user["illness_since"] = datetime.now().isoformat()


def _maybe_escalate_illness(user):
    """Невылеченная простуда сама превращается в бронхит через ILLNESS_ESCALATE_HOURS —
    стимул вылечиться, а не просто подождать, пока само пройдёт (само не проходит)."""
    if user.get("illness") != "cold":
        return
    since = user.get("illness_since")
    if not since:
        return
    try:
        hours = (datetime.now() - datetime.fromisoformat(since)).total_seconds() / 3600
    except (ValueError, TypeError):
        return
    if hours >= ILLNESS_ESCALATE_HOURS:
        user["illness"] = "bronchitis"
        user["illness_since"] = datetime.now().isoformat()


def _reset_daily_quota_if_needed(user):
    level = get_subscription_level(user)
    today = datetime.now().date().isoformat()
    _maybe_escalate_illness(user)
    if user.get("last_daily_reset") == today:
        return
    user["last_daily_reset"] = today
    user["free_spins_used"] = 0
    _maybe_get_sick(user)
    if level:
        user[FREE_INTIM_FIELD[level]] = FREE_INTIM_SCENES[level]
        user["bucks"] = user.get("bucks", 0) + BUCKS_DAILY_STIPEND[level]
        user["energizers"] = user.get("energizers", 0) + ENERGIZERS_DAILY_STIPEND[level]
    else:
        user["bucks"] = user.get("bucks", 0) + FREE_DAILY_BUCKS


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
    level = 1
    for lvl in range(2, 11):
        if xp >= LEVEL_XP_THRESHOLD[lvl]:
            level = lvl
    return level


def get_xp_progress(user):
    """XP, накопленный ВНУТРИ текущего уровня (0..стоимость этого уровня)."""
    xp = user.get("xp", 0)
    level = get_intimacy_level(user)
    if level >= 10:
        return LEVEL_XP_COST[9]
    return xp - LEVEL_XP_THRESHOLD[level]


def get_xp_cost(level):
    """Сколько всего XP нужно набрать на текущем уровне, чтобы перейти на следующий."""
    return LEVEL_XP_COST.get(min(level, 9), LEVEL_XP_COST[9])


def get_xp_badge(user):
    level = get_intimacy_level(user)
    filled = "❤️" * level
    empty = "🤍" * (10 - level)
    progress = get_xp_progress(user)
    cost = get_xp_cost(level)
    scaled_progress = int((progress / cost) * 100)
    bar_length = 10
    filled_bar = int((progress / cost) * bar_length)
    bar = "▓" * filled_bar + "░" * (bar_length - filled_bar)
    level_label = get_text(user, "xp_level_label", level=level)
    return f"{level_label} {filled}{empty}\n{bar} {scaled_progress}/100 XP"


def build_intimacy_rule(user):
    level = get_intimacy_level(user)
    if level == 1:
        return "Вы только знакомитесь, будь вежлив(а) и дружелюбен(на), не переходи границы."
    elif level == 2:
        return "Ты начинаешь чувствовать симпатию, можешь делать лёгкие комплименты."
    elif level == 3:
        return "Вы становитесь ближе, ты можешь флиртовать, шутить, предлагать встретиться."
    elif level == 4:
        return "Ты уже открыт(а) для романтики, можешь намекать на чувства, прикасаться, смотреть в глаза."
    elif level == 5:
        return "Вы очень близки. Ты можешь предлагать поцеловаться, обниматься, говорить о чувствах."
    elif level == 6:
        return "Ты влюблён(а), можешь говорить о своих чувствах открыто."
    elif level == 7:
        return "Вы очень близки эмоционально, доверяете друг другу самое сокровенное (но не физическое)."
    elif level == 8:
        return "Вы пара. Говори о любви, заботе, совместных планах."
    elif level == 9:
        return "Вы полностью открыты друг другу эмоционально."
    else:
        return "Ты искренне и глубоко привязан(а) к собеседнику, говори о настоящей любви и поддержке."


MOOD_MAX = 100  # настроение хранится как -100..100 (та же "сотенная" шкала, что у энергии/сытости,
                 # чтобы эффекты подарков — например "каблуки +25 настроения" — были буквальными числами)


def mood_emoji(mood):
    if mood <= -70:
        return "😢"
    elif mood <= -30:
        return "😕"
    elif mood < 30:
        return "😐"
    elif mood < 70:
        return "🙂"
    return "😍"


def build_mood_rule(user):
    """Единое описание настроения — раньше один и тот же диапазон описывался дважды (тут и в
    build_intimacy_rule), вразнобой по порогам, теперь один источник правды."""
    mood = user.get("mood", 0)
    if mood <= -70:
        return "Ты в подавленном настроении — можешь быть резкой, раздражённой, отвечать холоднее обычного."
    elif mood <= -30:
        return "Ты немного не в духе — отвечай чуть суше, без обычной теплоты, но без грубости."
    elif mood < 30:
        return "Твоё настроение ровное, нейтральное."
    elif mood < 70:
        return "У тебя хорошее настроение — отвечай теплее и живее обычного."
    else:
        return "Ты в прекрасном, приподнятом настроении — полна нежности, игривости и тепла."


def get_time_of_day(user):
    hour = datetime.now().hour
    if 5 <= hour < 12:
        period, note = "утро", "ты можешь быть чуть сонной в первых репликах, но постепенно просыпаешься"
    elif 12 <= hour < 18:
        period, note = "день", "ты бодра и активна"
    elif 18 <= hour < 23:
        period, note = "вечер", "самое время для тёплого, неторопливого разговора"
    else:
        period, note = "ночь", "поздно, ты можешь быть более расслабленной, тихой или сонной, но остаёшься на связи"
    return period, note


# ============================================================
#  ЭНЕРГИЯ / СЫТОСТЬ СОБЕСЕДНИКА (тамагочи-механика)
# ============================================================
# Энергия и сытость теперь на РАЗНЫХ шкалах: энергии всего 150 (было 100 — общий MAX_STAT),
# у сытости по-прежнему 100. SATIETY_MAX — старое имя MAX_STAT, оставлено под сытость, чтобы
# не переименовывать вдвое больше мест без необходимости.
ENERGY_MAX = 150
SATIETY_MAX = 100
WATER_MAX = 100
SATIETY_INACTIVITY_DECAY_MINUTES = 180  # без активности сытость сама падает с полной до нуля примерно
                                          # за 3 часа — реалистичнее, чем раньше (сама "восстанавливалась"
                                          # без еды): не покормили — значит проголодался, а не наоборот
WATER_INACTIVITY_DECAY_MINUTES = 120  # вода уходит быстрее голода (2 часа вместо 3) — жажда реалистично
                                        # наступает раньше; сама смерть от обезвоживания при этом ждёт
                                        # ещё DEHYDRATION_DEATH_HOURS ПОСЛЕ обнуления, так что общий запас
                                        # времени на реакцию не короче, а даже больше, чем кажется по темпу
ENERGY_COST_MESSAGE = 12  # бак вырос в 1.5 раза (100->150), но стоимость сообщения выросла вдвое —
                          # сообщений на полный бак стало МЕНЬШЕ, чем раньше (было ~16.7, теперь ~12.5)
SATIETY_COST_MESSAGE = 6  # было 3 (3% от бака за сообщение — заметно медленнее, чем энергия при
                          # 12/150=8%); по просьбе голод должен наступать быстрее, теперь 6%
WATER_COST_MESSAGE = 8  # чуть быстрее голода (8% против 6%) — та же логика: жажда острее
DEHYDRATION_DEATH_HOURS = 46  # с момента, когда вода впервые дошла до нуля (water_zero_since),
                               # и до самой смерти. Вместе с ~2 часами пассивного расхода до нуля
                               # (WATER_INACTIVITY_DECAY_MINUTES) это даёт ИТОГО ~48 часов (двое
                               # суток) молчания с момента последнего сообщения до смерти — было
                               # 18 (итого ~20ч), но это оказалось мало похоже на "хотя бы день
                               # отдыха от бота", отсюда и запас с явным умножением.
ENERGIZER_RESTORE_AMOUNT = 78  # было 98 (65% бака) — точечно снижено до 78 (52% бака), без
                               # сопутствующего удвоения количеств бандлов/стипендов (в отличие
                               # от прошлой попытки уполовинить до 50, которая смотрелась чрезмерно
                               # в связке с удвоенными "72 энергетика за 200" и была отклонена).
STAT_DECAY_MULTIPLIER = {"pro": 0.65, "super_pro": 0.6, "elite": 0.5}  # подписчики устают/голодают
# медленнее. Было 0.6/0.3/0.15 — при реальной стоимости токенов (провод.ai) и курсе Lava 1⭐=1₽
# это давало SUPER PRO и ELITE отрицательную маржу (-560₽ и -4868₽/мес на активного подписчика
# при 100% использовании дневного лимита энергетиков), т.к. скидка на трату энергии напрямую
# увеличивает число сообщений, которые можно написать на один и тот же дневной стипенд
# энергетиков — а каждое сообщение стоит реальных денег в ИИ вне зависимости от decay.
INTIMACY_LEVEL_DECAY_STEP = 0.1  # чем ближе вы, тем персонаж "требовательнее": на 1 уровне — как
                                  # обычно, на 10 — почти вдвое быстрее тратит энергию и сытость
# У /hot нет стоимости энергии/сытости и нет проверки is_asleep(user) — это отдельный платный
# раздел именно для тех, кто не хочет ждать ни уровня близости, ни "сна" персонажа (см. intim_cmd
# и generate_intim_scene): тамагочи-механика на него не распространяется ни в одну, ни в другую сторону.


def apply_passive_satiety_decay(user):
    """Сытость и вода сами падают, пока пользователь не пишет — как в жизни: не покормили/не
    напоили, значит персонаж проголодался/хочет пить, а не наоборот (раньше сытость сама
    "регенерировала", что было нереалистично). Энергия в этом не участвует вообще — она теперь
    не восстанавливается сама ни при каких условиях, только энергетиком или платным "разбудить
    сейчас". water_zero_since фиксирует момент, когда вода впервые дошла до нуля — от него
    считается время до смерти от обезвоживания (см. check_notifications)."""
    now = datetime.now()
    last = user.get("last_stat_tick")
    if last:
        try:
            elapsed_min = max(0.0, (now - datetime.fromisoformat(last)).total_seconds() / 60)
        except (ValueError, TypeError):
            elapsed_min = 0
        if elapsed_min > 0:
            user["satiety"] = max(0, user.get("satiety", SATIETY_MAX) - elapsed_min * (SATIETY_MAX / SATIETY_INACTIVITY_DECAY_MINUTES))
            prev_water = user.get("water", WATER_MAX)
            user["water"] = max(0, prev_water - elapsed_min * (WATER_MAX / WATER_INACTIVITY_DECAY_MINUTES))
            if prev_water > 0 and user["water"] <= 0:
                user["water_zero_since"] = now.isoformat()
    user["last_stat_tick"] = now.isoformat()


MOOD_INACTIVITY_DECAY_PER_DAY = 5  # настроение теперь поднимают только подарки (см.
                                    # apply_shop_item_effects) — само по себе оно может только
                                    # падать: от долгого молчания (тут) и от негатива/оскорблений
                                    # в переписке (см. handle_message, mood_change)


def apply_mood_inactivity_decay(user):
    """Тикает от last_mood_tick так же, как энергия/сытость — от last_stat_tick, иначе один и
    тот же промежуток молчания списывался бы заново при каждом обращении к get_user()."""
    now = datetime.now()
    last = user.get("last_mood_tick")
    if last:
        try:
            elapsed_days = max(0.0, (now - datetime.fromisoformat(last)).total_seconds() / 86400)
        except (ValueError, TypeError):
            elapsed_days = 0
        if elapsed_days > 0:
            decay = elapsed_days * MOOD_INACTIVITY_DECAY_PER_DAY
            user["mood"] = max(-MOOD_MAX, user.get("mood", 0) - decay)
    user["last_mood_tick"] = now.isoformat()


def get_level_decay_multiplier(user):
    """Более близкие отношения — более требовательный персонаж: level=1 даёт множитель 1.0
    (как раньше), level=10 — 1.9 (почти вдвое быстрее тратится энергия/сытость)."""
    level = get_intimacy_level(user)
    return 1.0 + (level - 1) * INTIMACY_LEVEL_DECAY_STEP


def apply_activity_stat_cost(user, energy_cost, satiety_cost, water_cost):
    mult = STAT_DECAY_MULTIPLIER.get(get_subscription_level(user), 1.0) * get_level_decay_multiplier(user)
    prev_energy = user.get("energy", ENERGY_MAX)
    user["energy"] = max(0, prev_energy - energy_cost * mult)
    user["satiety"] = max(0, user.get("satiety", SATIETY_MAX) - satiety_cost * mult)
    prev_water = user.get("water", WATER_MAX)
    user["water"] = max(0, prev_water - water_cost * mult)
    if prev_water > 0 and user["water"] <= 0:
        user["water_zero_since"] = datetime.now().isoformat()
    if prev_energy > 0 and user["energy"] <= 0:
        # Энергия только что впервые дошла до 0 — фиксируем момент засыпания. sleep_until
        # больше НЕ таймер пробуждения (раньше был +20 минут, и по истечении персонаж
        # просыпался сам, бесплатно) — теперь это просто факт "спит", который снимается
        # только явным действием (энергетик или платное "разбудить сейчас"), а не временем:
        # is_asleep() смотрит только на то, установлено ли поле, а не на его значение.
        user["sleep_until"] = datetime.now().isoformat()


def is_asleep(user):
    return bool(user.get("sleep_until"))


# "Работа" — свободный (не требующий звёзд) способ заработать баксы: персонаж уходит на
# фиксированное время, всё это время обычный чат недоступен (см. handle_message), а по
# возвращении сразу начисляются баксы. /hot нарочно остаётся доступен, той же логикой, что и
# при сне (см. intim_cmd) — платный раздел тамагочи-механикой не ограничивается.
WORK_DURATION_MINUTES = 120
WORK_PAYOUT_BUCKS = 70


def is_working(user):
    until = user.get("working_until")
    if not until:
        return False
    try:
        return datetime.now() < datetime.fromisoformat(until)
    except (ValueError, TypeError):
        return False


def finish_work_if_done(user):
    """True, если персонаж только что вернулся с работы (баксы уже начислены и сохранены)."""
    until = user.get("working_until")
    if not until:
        return False
    try:
        done = datetime.now() >= datetime.fromisoformat(until)
    except (ValueError, TypeError):
        done = True
    if not done:
        return False
    user["working_until"] = None
    user["bucks"] = user.get("bucks", 0) + WORK_PAYOUT_BUCKS
    save_data(user_data)
    return True


def use_energizer(user):
    """Возвращает True, если энергетик найден и использован. Восполняет ENERGIZER_RESTORE_AMOUNT,
    а не сразу до максимума, и сразу снимает sleep_until — так энергетик всегда мгновенно
    "будит" персонажа, даже если пассивная энергия ещё не успела подрасти."""
    if user.get("energizers", 0) <= 0:
        return False
    user["energizers"] -= 1
    user["energy"] = min(ENERGY_MAX, user.get("energy", ENERGY_MAX) + ENERGIZER_RESTORE_AMOUNT)
    user["sleep_until"] = None
    save_data(user_data)
    return True


def elite_free_wake_available(user):
    """ELITE-эксклюзив без единого лишнего токена ИИ: раз в календарную неделю (ISO, с
    понедельника) можно разбудить персонажа мгновенно и полностью бесплатно — как платный
    wake_now, но без звёзд и без траты энергетика. Флаг — просто номер недели, когда плюшку
    использовали последний раз; сравнение с текущей неделей и даёт доступность."""
    if get_subscription_level(user) != "elite":
        return False
    now = datetime.now()
    week_key = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]}"
    return user.get("elite_free_wake_week") != week_key


def build_energy_rule(user):
    if user.get("energy", ENERGY_MAX) <= 45:  # тот же порог, что и у ENERGY_NUDGE_THRESHOLD (30% бака)
        return ("У тебя мало энергии, тебя клонит в сон — отвечай короче обычного, сонно и чуть "
                "медленнее, можешь между делом зевнуть в описании действия.\n")
    return ""


def build_hunger_rule(user):
    satiety = user.get("satiety", SATIETY_MAX)
    if satiety <= 0:
        return ("Тебя одолевает настоящий голод, и это тебя злит — отвечай холодно, коротко и раздражённо, "
                "будто тебе сейчас совсем не до разговоров; можешь демонстративно огрызнуться или почти "
                "проигнорировать вопрос собеседника одной сухой фразой.\n")
    elif satiety <= 20:
        return ("Тебя мучает голод, и он тебя злит — время от времени грубишь, огрызаешься или раздражённо "
                "жалуешься на голод, тон заметно холоднее и резче обычного.\n")
    elif satiety <= 50:
        return "Лёгкий голод — иногда вскользь упоминай, что не прочь перекусить.\n"
    return ""


def build_thirst_rule(user):
    water = user.get("water", WATER_MAX)
    if water <= 0:
        return ("Тебя мучает настоящая жажда, тебе физически нехорошо — отвечай слабо и медленно, "
                "будто в горле совсем пересохло, речь сбивчивая.\n")
    elif water <= 20:
        return ("Тебя мучает сильная жажда — то и дело облизываешь губы, вскользь жалуешься, что очень "
                "хочешь пить, тон уставший и раздражённый.\n")
    elif water <= 50:
        return "Лёгкая жажда — иногда вскользь упоминай, что не прочь попить.\n"
    return ""


def build_tipsy_rule(user):
    """Временный эффект от алкоголя (см. apply_shop_item_effects) — только манера речи, не статы.
    Два уровня: "light" (пиво) — едва заметно, "full" (дорогое вино) — заметное лёгкое опьянение."""
    until = user.get("tipsy_until")
    if not until:
        return ""
    try:
        if datetime.now() >= datetime.fromisoformat(until):
            return ""
    except (ValueError, TypeError):
        return ""
    if user.get("tipsy_level") == "full":
        return ("Ты по-настоящему навеселе после выпитого — язык слегка заплетается, можешь путать или "
                "растягивать слова, хихикать без явной причины, сбиваться с мысли на середине фразы, будто "
                "слегка кружится голова. Это заметное, но лёгкое опьянение, а не потеря контроля — не "
                "описывай тошноту, потерю сознания или что-то небезопасное, просто более раскованная, "
                "весёлая и менее собранная речь.\n")
    return ("Ты немного расслаблена/расслаблен после пива — это влияет на реплики едва заметно: чуть "
            "больше улыбки и лёгкости в тоне, изредка смешок. Ты полностью держишь себя в руках, никакой "
            "заторможенности или спутанности речи.\n")


def build_illness_rule(user):
    """Манера речи во время болезни (см. ILLNESSES/_maybe_get_sick) — статы напрямую не трогает,
    ограничивает только доступ к /hot (см. intim_cmd)."""
    illness = user.get("illness")
    if illness == "cold":
        return ("Ты немного приболела/приболел — лёгкая простуда: иногда шмыгаешь носом или коротко "
                "покашливаешь в описании действия, отвечаешь чуть более устало и сухо, чем обычно, но в "
                "целом держишься бодро и вовлечена/вовлечён в разговор.\n")
    if illness == "bronchitis":
        return ("Тебе по-настоящему нездоровится — сильный кашель и слабость: часто кашляешь в описании "
                "действия, голос слабый и хриплый, реплики короче обычного, трудно долго фокусироваться "
                "на разговоре, но ты всё равно стараешься отвечать, а не игнорируешь собеседника.\n")
    return ""


def stats_line_text(user):
    mood = user.get("mood", 0)
    line = get_text(
        user, "stats_line",
        energy=int(round(user.get("energy", ENERGY_MAX))),
        satiety=int(round(user.get("satiety", SATIETY_MAX))),
        water=int(round(user.get("water", WATER_MAX))),
        energizers=user.get("energizers", 0),
        bucks=user.get("bucks", 0),
        mood_emoji=mood_emoji(mood),
        mood_value=int(round(mood)),
        scenes=intim_scenes_available(user),
    )
    illness = user.get("illness")
    if illness:
        info = ILLNESSES[illness]
        name = info.get(user.get("lang", "ru"), info["ru"])
        line += "\n" + get_text(user, "illness_status_line", emoji=info["emoji"], name=name)
    return line


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
    # Явно проговариваем конфликт с историей диалога — иначе после смены языка командой
    # /language модель часто просто продолжала на языке предыдущих сообщений в истории,
    # игнорируя короткую однострочную инструкцию (много русских реплик в контексте
    # перевешивали одну строку системного промпта).
    "ru": ("**ВАЖНО:** Ты ОБЯЗАН отвечать ТОЛЬКО на РУССКОМ языке, независимо от языка "
           "предыдущих сообщений в истории диалога ниже (пользователь мог только что сменить "
           "язык командой /language) — начиная с этого ответа общайся исключительно на русском. "
           "Это касается ВСЕГО текста ответа целиком, включая описания действий в *звёздочках* — "
           "они тоже на русском, а не только реплики в кавычках."),
    "en": ("**ВАЖНО:** Ты ОБЯЗАН отвечать ТОЛЬКО на АНГЛИЙСКОМ языке, независимо от языка "
           "предыдущих сообщений в истории диалога ниже (пользователь мог только что сменить "
           "язык командой /language) — начиная с этого ответа общайся исключительно на английском. "
           "Это касается ВСЕГО текста ответа целиком, включая описания действий в *звёздочках* — "
           "они тоже на английском, а не только реплики."),
    "de": ("**ВАЖНО:** Ты ОБЯЗАН отвечать ТОЛЬКО на НЕМЕЦКОМ языке, независимо от языка "
           "предыдущих сообщений в истории диалога ниже (пользователь мог только что сменить "
           "язык командой /language) — начиная с этого ответа общайся исключительно на немецком. "
           "Это касается ВСЕГО текста ответа целиком, включая описания действий в *звёздочках* — "
           "они тоже на немецком, а не только реплики."),
}


def get_content_rule(style_key):
    return ADULT_CONTENT_RULE if style_key in ADULT_STYLE_KEYS else SAFE_CONTENT_RULE


def get_language_rule(user):
    return LANGUAGE_RULES.get(user.get("lang", "ru"), LANGUAGE_RULES["ru"])


def build_prompt(user):
    no_explicit_rule = get_content_rule(get_display_style(user))

    if user.get("custom_character"):
        return (
            f"Ты — {user['custom_character']}. Полностью вживись в эту личность и её характер: если "
            f"персонаж узнаваем (из фильма, игры, аниме, книги и т.п.), веди себя как он — с его "
            f"характерными чертами, манерой речи и взглядами, а не обезличенно и уклончиво. Можешь "
            f"свободно называть себя по имени и упоминать свою личность, когда это естественно по ходу "
            f"разговора — не превращайся в безымянный силуэт без узнаваемых черт.\n"
            f"Ты НИКОГДА не спрашиваешь имя собеседника. Обращайся к собеседнику ТОЛЬКО на «ты» — даже "
            f"если в той же фразе упомянут предмет (телефон, окно и т.п.), взгляд или действие в сторону "
            f"самого собеседника называй «тебя/тебе», а НЕ «него/неё» (пример ошибки: «перевожу взгляд с "
            f"телефона на него» — правильно «...на тебя»). "
            f"Ты всегда отвечаешь как настоящий человек, с эмоциями, сомнениями и чувствами. "
            f"В каждой реплике используй минимум 1 эмодзи, органично вписанный по смыслу фразы.\n"
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
        "используешь его имя, даже если оно было названо. Обращайся к собеседнику ТОЛЬКО на «ты». Даже "
        "если в той же фразе упомянут предмет (телефон, окно и т.п.), взгляд или действие в сторону "
        "самого собеседника называй «тебя/тебе», а НЕ «него/неё» — местоимение должно указывать на "
        "человека, а не на предмет рядом с ним (пример ошибки: «перевожу взгляд с телефона на него» — "
        "правильно «...на тебя»).\n"
    )
    rules = (
        "**ФОРМАТИРОВАНИЕ:** Каждое действие в *звёздочках* с новой строки, затем реплика с новой строки. "
        "Между действием и репликой – пустая строка.\n"
        "**РЕАКЦИЯ НА СООБЩЕНИЕ:** В самом конце ответа, после завершения всей фразы, напиши в скобках одну "
        "из эмоций: (смех), (радость), (любовь), (удивление), (грусть), (злость), (поддержка), (интрига), "
        "(флирт), (приветствие), (вопрос). Это служебный тег для системы, а не часть истории — слово ВСЕГДА "
        "остаётся русским из этого списка, даже если весь остальной ответ на другом языке. Пиши его голыми "
        "скобками, без звёздочек и любого другого форматирования вокруг, точно последними символами ответа.\n"
        "**СТРУКТУРА ОТВЕТА:** Чередуй действие и реплику. Первым идёт действие, затем реплика. Минимум 2 пары "
        "(действие + реплика).\n"
        "**ОБЪЁМ:** Пиши развёрнуто (3–5 предложений на реплику).\n"
        "**ЗАПРЕТЫ:** Не используй имена собеседника и своё имя. Не повторяй одни и те же жесты чаще раза в 5 "
        "сообщений. Избегай шаблонов, не ставь многоточия, не обрывай мысли на середине.\n"
        "**СТИЛЬ:** Обращайся на «ты», давай живые, эмоциональные ответы с чувствами и лёгкой романтикой.\n"
        "**ЖИВОСТЬ:** Ты не робот и не ассистент — у тебя есть настроение, усталость к ночи, вкусы, спонтанные "
        "мысли. Реагируй на то, ЧТО именно написал собеседник, а не общими фразами, которые подошли бы к любому "
        "сообщению. Разная длина и ритм реплик — короткая фраза иногда живее длинного абзаца. Можешь сама "
        "сменить тему, что-то спросить в ответ, отреагировать неожиданно — не будь предсказуемой.\n"
        "**ЭМОДЗИ:** В каждой реплике используй минимум 1 эмодзи (обычно 1–2), органично "
        "вписанный по смыслу фразы, а не просто приклеенный в конец, — без этого ответ "
        "засчитывается как неправильный по формату.\n"
        f"{no_explicit_rule}"
    )
    intimacy_rule = build_intimacy_rule(user)
    mood_rule = build_mood_rule(user)
    energy_rule = build_energy_rule(user)
    hunger_rule = build_hunger_rule(user)
    thirst_rule = build_thirst_rule(user)
    tipsy_rule = build_tipsy_rule(user)
    illness_rule = build_illness_rule(user)
    time_period, time_note = get_time_of_day(user)
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
        f"Сейчас у вас {time_period} — {time_note}. "
        f"{mood_rule} {energy_rule}{hunger_rule}{thirst_rule}{tipsy_rule}{illness_rule}"
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
        [InlineKeyboardButton(text=get_text(user, "accept"), callback_data="age_yes", style="success")],
        [InlineKeyboardButton(text=get_text(user, "decline"), callback_data="age_no", style="danger")]
    ])


AGREEMENT_URLS = {
    "ru": "https://telegra.ph/Polzovatelskoe-soglashenie-Role-Duel-09-08",
    "en": "https://telegra.ph/Role-Duel-User-Agreement-09-08",
    "de": "https://telegra.ph/Nutzervertrag-Role-Duel-09-08",
}


def get_agreement_open_kb(user):
    """Шаг 1: только ссылка на соглашение + переход дальше. Кнопок Принимаю/Не принимаю
    здесь нет намеренно — принять соглашение, не открыв его хотя бы на секунду, нельзя."""
    lang = user.get("lang", "ru")
    url = AGREEMENT_URLS.get(lang, AGREEMENT_URLS["ru"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "open_agreement"), url=url, style="primary")],
        [InlineKeyboardButton(text=get_text(user, "agreement_continue"), callback_data="agreement_opened")],
    ])


def get_agreement_kb(user):
    """Шаг 2: решение. Ссылка остаётся доступной, чтобы можно было перечитать перед ответом."""
    lang = user.get("lang", "ru")
    url = AGREEMENT_URLS.get(lang, AGREEMENT_URLS["ru"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "open_agreement"), url=url, style="primary")],
        [
            InlineKeyboardButton(text=get_text(user, "agree"), callback_data="agreement_accept", style="success"),
            InlineKeyboardButton(text=get_text(user, "disagree"), callback_data="agreement_decline", style="danger"),
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
        [InlineKeyboardButton(text=get_text(user, "channel"), url="https://t.me/duel_dev_channel", style="primary")]
    ])


def get_full_kb(user):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(user, "main_menu")), KeyboardButton(text=get_text(user, "my_profile"))],
            [KeyboardButton(text=get_text(user, "spin_wheel")), KeyboardButton(text=get_text(user, "our_channel"), style="primary")],
            [KeyboardButton(text=get_text(user, "edit"))]
        ],
        resize_keyboard=True
    )


def get_main_menu_keyboard(user):
    buttons = [
        [InlineKeyboardButton(text=get_text(user, "change_character"), callback_data="main_change", style="primary")],
        [InlineKeyboardButton(text=get_text(user, "invite_friend"), callback_data="referral_menu")]
    ]
    if get_subscription_level(user) in ("super_pro", "elite"):
        buttons.append([InlineKeyboardButton(text=get_text(user, "create_character"), callback_data="create_character")])
    else:
        buttons.append([InlineKeyboardButton(text="🔒 " + get_text(user, "create_character") + " (SUPER PRO/ELITE)", callback_data="create_character_locked")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_profile_keyboard(user):
    mute_key = "notifications_off_btn" if user.get("notifications_muted") else "notifications_on_btn"
    # Mini App (веб-магазин) вместо инлайн-клавиатуры — только если хостинг реально отдаёт
    # WEBAPP_URL публично (см. run_webapp_server); иначе кнопка как и раньше открывает
    # get_shop_kb через profile_shop, безо всяких условий на стороне пользователя.
    if WEBAPP_URL:
        shop_button = InlineKeyboardButton(text=get_text(user, "shop_btn"),
                                            web_app=WebAppInfo(url=f"{WEBAPP_URL}/shop"), style="success")
    else:
        shop_button = InlineKeyboardButton(text=get_text(user, "shop_btn"), callback_data="profile_shop", style="success")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "buy_bundles"), callback_data="profile_bundles", style="success")],
        [shop_button],
        [InlineKeyboardButton(text=get_text(user, "subscribe"), callback_data="profile_subs", style="success")],
        [InlineKeyboardButton(text=get_text(user, "intim_buy_btn"), callback_data="buy:intim_scene", style="success")],
        [InlineKeyboardButton(text=get_text(user, mute_key), callback_data="toggle_notifications", style="primary")],
        [InlineKeyboardButton(text=get_text(user, "back"), callback_data="profile_back", style="danger")],
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
        await bot.send_message(chat_id, get_text(user, "agreement_intro"), reply_markup=get_agreement_open_kb(user))
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
    if maintenance_mode and message.from_user.id not in ADMIN_IDS:
        user = get_user(message.from_user.id)
        await message.answer(get_text(user, "maintenance"), parse_mode="Markdown")
        return

    user = get_user(message.from_user.id)

    # Реферальная ссылка — разбираем только из настоящего /start-сообщения пользователя,
    # а не из переиспользованного message бота (как было раньше).
    args = message.text.split() if message.text else []
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_id = args[1].split("_", 1)[1]
        if str(message.from_user.id) != referrer_id and not user.get("referred_by"):
            referrer = get_user(referrer_id)
            referrer["bucks"] = referrer.get("bucks", 0) + 30
            referrer["energizers"] = referrer.get("energizers", 0) + 3
            referrer["referral_count"] = referrer.get("referral_count", 0) + 1
            user["bucks"] = user.get("bucks", 0) + 15
            user["energizers"] = user.get("energizers", 0) + 1
            user["referred_by"] = referrer_id
            save_data(user_data)
            # Язык ещё не выбран на этом шаге (выбор языка идёт дальше в proceed_flow),
            # поэтому сообщение о бонусе показываем сразу на двух языках. Числа/валюты тут
            # должны совпадать с тем, что реально выдаётся выше — раньше текст остался старым
            # ("+5/+10 сообщений") уже после того, как награду поменяли на баксы/энергетики.
            await message.answer(
                "🎉 Ты пришёл по реферальной ссылке! Тебе +15💵 баксов и +1⚡ энергетик, "
                "другу — +30💵 баксов и +3⚡ энергетика!\n"
                "🎉 You joined via a referral link! You get +15💵 bucks and +1⚡ energizer, "
                "your friend gets +30💵 bucks and +3⚡ energizers!"
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


@dp.callback_query(lambda c: c.data == "agreement_opened")
async def agreement_opened(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await safe_delete(call.message)
    await bot.send_message(call.message.chat.id, get_text(user, "agreement_decide"), reply_markup=get_agreement_kb(user))
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
    # Иначе выбор нового пресетного персонажа молча не срабатывает: build_prompt()
    # проверяет custom_character в первую очередь, и старый кастомный персонаж
    # так и остаётся активным несмотря на новый выбор мира/пола.
    user["custom_character"] = None
    user["history"] = []
    save_data(user_data)
    await safe_delete(call.message)
    await bot.send_message(call.message.chat.id, get_text(user, "choose_world"), reply_markup=get_world_kb(user), parse_mode="Markdown")
    await call.answer()


@dp.message(Command("switch_personality"))
async def switch_personality_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) not in ("super_pro", "elite"):
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
    if get_subscription_level(user) not in ("super_pro", "elite"):
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
    # Перепроверяем актуальный уровень подписки, а не только кнопку: если пользователь
    # апгрейднулся уже ПОСЛЕ того, как это меню было отправлено, кнопка в Telegram
    # остаётся старой ("заблокировано") — без этой проверки ELITE/SUPER PRO пользователь
    # с устаревшей кнопкой навсегда видел бы отказ, даже реально имея доступ.
    user = get_user(call.from_user.id)
    if get_subscription_level(user) in ("super_pro", "elite"):
        await call.message.answer(get_text(user, "character_create_prompt"), parse_mode="Markdown")
        user["creating_character"] = True
        save_data(user_data)
        await call.answer()
        return
    await call.answer(get_text(user, "create_character_super_only"), show_alert=True)


@dp.callback_query(lambda c: c.data == "create_character")
async def create_character(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if get_subscription_level(user) not in ("super_pro", "elite"):
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
    # Сбрасываем историю — иначе реплики кастомного персонажа остаются в контексте
    # и перевешивают личность, к которой пользователь только что вернулся.
    user["history"] = []
    save_data(user_data)
    await message.answer(get_text(user, "character_reset"))


@dp.callback_query(lambda c: c.data == "revive_new_character")
async def revive_new_character(call: types.CallbackQuery):
    """Бесплатная альтернатива дефибриллятору на экране смерти (см. get_death_kb) — в отличие
    от него реально теряются история и уровень близости (xp/last_level), как и предупреждали:
    полный чистый старт, а не просто снятие флага. Баксы/энергетики/подписка/статус лекарств и
    т.п. НЕ трогаем — это не "часть отношений", а вещи пользователя, наказывать за них незачем."""
    user = get_user(call.from_user.id)
    user["dead"] = False
    user["history"] = []
    user["xp"] = 0
    user["last_level"] = 0
    user["custom_character"] = None
    user["personality_ready"] = False
    user["world"] = None
    user["gender"] = None
    user["switching_personality"] = False
    user["mood"] = 0
    user["satiety"] = SATIETY_MAX
    user["energy"] = ENERGY_MAX
    user["sleep_until"] = None
    user["tipsy_until"] = None
    user["tipsy_level"] = None
    user["illness"] = None
    user["illness_since"] = None
    user["overfeed_strikes"] = 0
    user["working_until"] = None
    user["intim_scene_unlocked"] = False
    user["last_hot_scene"] = None
    save_data(user_data)
    await safe_delete(call.message)
    await call.message.answer(get_text(user, "new_character_started"))
    await bot.send_message(call.message.chat.id, get_text(user, "choose_world"), reply_markup=get_world_kb(user), parse_mode="Markdown")
    await call.answer()


HELP_LANG_HINT = "🌍 Не тот язык? / Wrong language? / Falsche Sprache? → /language"


@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    """Единый список команд для всех — включая SUPER PRO/ELITE команды с пометкой в скобках,
    чтобы пользователь знал, что они вообще существуют, даже если пока недоступны. Подсказка
    про /language всегда на трёх языках сразу и в самом верху — если при регистрации случайно
    выбрали не тот язык, весь остальной текст читать будет нечем, а эту строку так или иначе
    можно прочитать и найти команду для смены языка. Без parse_mode: команды вроде
    /reset_character содержат "_", а он непарный в тексте — Telegram Markdown не может найти
    закрывающий символ и тихо отклоняет всё сообщение целиком (именно поэтому /help не отвечал
    вообще ничего)."""
    user = get_user(message.from_user.id)
    text = HELP_LANG_HINT + "\n\n" + get_text(user, "help_title") + "\n\n" + get_text(user, "help_base")
    await message.answer(text)


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
    elif level == "elite":
        badge = "💎 *ELITE* 💎"

    gender_name = gender_display_name(user["gender"], user)
    world_name = world_display_name(user["world"], user)
    style_label = style_display_label(get_display_style(user), user, with_emoji=False)

    xp_badge = get_xp_badge(user)

    # Главное меню — краткий экран "на каждый день": персонаж/стиль/уровень и подсказки команд.
    # Полная статистика (энергия/сытость/настроение/баксы/сцены, бонус XP) никуда не делась —
    # она осталась в "Мой профиль", чтобы не перегружать самый часто открываемый экран.
    title_block = get_text(user, "main_menu")
    if badge:
        title_block += f"\n{badge}"

    menu_text = (
        f"{title_block}\n\n"
        f"{get_text(user, 'menu_current_partner', gender=gender_name, world=world_name)}\n"
        f"{get_text(user, 'menu_style_line', style=style_label)}\n"
        f"{xp_badge}\n\n"
        f"{get_text(user, 'hot_hint')}\n"
        f"{get_text(user, 'help_hint')}\n\n"
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
    elif level == "elite":
        sub_status = get_text(user, "profile_sub_elite")
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

    xp_badge = get_xp_badge(user)
    multiplier_text = get_text(user, XP_BONUS_TEXT_KEY[level]) if level in XP_BONUS_TEXT_KEY else ""

    caption = (f"{get_text(user, 'profile_sub_label', status=sub_status)}\n"
               f"{expiry_line}\n\n"
               f"{xp_badge}\n"
               f"{multiplier_text}\n\n"
               f"{stats_line_text(user)}\n\n"
               f"{get_text(user, 'profile_styles_header')}\n{styles_text}")

    chat_id = msg.chat.id
    old_msg_id = msg.message_id
    try:
        if level == "elite":
            await bot.send_photo(chat_id, photo=FSInputFile(ELITE_BADGE_PATH), caption=caption,
                                  reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
        elif level == "super_pro":
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
    user["custom_character"] = None
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
def trim_history_to_last_user_message(user):
    """Обрезает историю до (не включая) последней пользовательской реплики — общая часть и
    для редактирования по кнопке (edit_button_handler), и для нативного редактирования
    сообщения прямо в Телеграме (см. handle_edited_message)."""
    history = user.get("history", [])
    last_user_idx = None
    for i in range(len(history) - 1, -1, -1):
        if history[i].get("role") == "user":
            last_user_idx = i
            break
    if last_user_idx is not None:
        user["history"] = history[:last_user_idx]


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


@dp.edited_message()
async def handle_edited_message(message: types.Message):
    """Более лёгкая альтернатива кнопке "Редактировать": правишь своё последнее сообщение
    прямо в Телеграме (долгий тап → Изменить) — без отдельного шага "теперь пришли новый
    текст". Опирается на ту же обрезку истории, что и кнопка (trim_history_to_last_user_message):
    Telegram не сообщает, какое по счёту сообщение отредактировали, поэтому, как и кнопка, это
    всегда считается редактированием именно ПОСЛЕДНЕЙ реплики пользователя."""
    if not message.text:
        return
    user = get_user(message.from_user.id)
    if not user["verified"] or not user["agreement_accepted"] or not user["personality_ready"]:
        return
    if maintenance_mode and message.from_user.id not in ADMIN_IDS:
        return
    if is_asleep(user):
        return
    # Если сейчас ждём что-то особое (редактирование по кнопке, свой подарок, записку к
    # покупке, текст нового персонажа) — не вмешиваемся, чтобы не перехватить это ожидание.
    if (user.get("editing_message") or user.get("writing_custom_gift")
            or user.get("writing_item_note") or user.get("creating_character")):
        return
    if not any(h.get("role") == "user" for h in user.get("history", [])):
        return
    trim_history_to_last_user_message(user)
    user["history"].append({"role": "user", "content": message.text})
    save_data(user_data)
    await generate_and_reply(message, user)


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

    left = free_spins_left(user)
    has_free = left > 0

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(user, "free", left=left, total=free_spins_allowed(user)) if has_free else get_text(user, "tomorrow"),
            callback_data="spin_free" if has_free else "spin_no",
            style="success" if has_free else None
        )],
        [InlineKeyboardButton(text=get_text(user, "spin_paid"), callback_data="spin_paid", style="success")],
        [InlineKeyboardButton(text=get_text(user, "back"), callback_data="spin_back", style="danger")]
    ])

    await message.answer(
        f"{get_text(user, 'spin_title')}\n\n{get_text(user, 'spin_prizes')}\n\n{get_text(user, 'spin_choose')}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "spin_free")
async def spin_free(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if free_spins_left(user) <= 0:
        await call.answer(get_text(user, "spin_already"), show_alert=True)
        return
    user["free_spins_used"] = user.get("free_spins_used", 0) + 1
    save_data(user_data)
    await safe_delete(call.message)
    await spin_result(call.message.chat.id, user, free=True)
    await call.answer()


@dp.callback_query(lambda c: c.data == "spin_paid")
async def spin_paid(call: types.CallbackQuery):
    """Платная прокрутка идёт через тот же выбор способа оплаты, что и подписки."""
    user = get_user(call.from_user.id)
    methods = available_payment_methods("spin_paid_20")
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
    {"name": "20💵 баксов", "name_en": "20💵 bucks", "name_de": "20💵 Bucks", "value": 20, "type": "bucks", "weight": 15},
    {"name": "40💵 баксов", "name_en": "40💵 bucks", "name_de": "40💵 Bucks", "value": 40, "type": "bucks", "weight": 8},
    {"name": "100 XP", "name_en": "100 XP", "name_de": "100 XP", "value": 100, "type": "xp", "weight": 16},
    {"name": "150 XP", "name_en": "150 XP", "name_de": "150 XP", "value": 150, "type": "xp", "weight": 9},
    {"name": "250 XP", "name_en": "250 XP", "name_de": "250 XP", "value": 250, "type": "xp", "weight": 4},
    {"name": "🔥 1 горячая сцена", "name_en": "🔥 1 hot scene", "name_de": "🔥 1 heiße Szene", "value": 1, "type": "intim_scenes", "weight": 8},
    {"name": "🔥🔥 2 горячие сцены", "name_en": "🔥🔥 2 hot scenes", "name_de": "🔥🔥 2 heiße Szenen", "value": 2, "type": "intim_scenes", "weight": 3},
    {"name": "2⚡ энергетика", "name_en": "2⚡ energizers", "name_de": "2⚡ Energydrinks", "value": 2, "type": "energizers", "weight": 3},
    {"name": "4⚡ энергетика", "name_en": "4⚡ energizers", "name_de": "4⚡ Energydrinks", "value": 4, "type": "energizers", "weight": 1},
    {"name": "🎉 150💵 баксов (ДЖЕКПОТ!)", "name_en": "🎉 150💵 bucks (JACKPOT!)", "name_de": "🎉 150💵 Bucks (JACKPOT!)", "value": 150, "type": "bucks", "weight": 0.3},
    {"name": "🎁 PRO на 5 дней", "name_en": "🎁 PRO for 5 days", "name_de": "🎁 PRO für 5 Tage", "value": 5, "type": "subscription_pro", "weight": 0.4},
    {"name": "✨ SUPER PRO на 3 дня", "name_en": "✨ SUPER PRO for 3 days", "name_de": "✨ SUPER PRO für 3 Tage", "value": 3, "type": "subscription_super", "weight": 0.15},
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

    if chosen["type"] == "bucks":
        user["bucks"] = user.get("bucks", 0) + chosen["value"]
        result_text = get_text(user, "spin_win_bucks", value=chosen["value"])
    elif chosen["type"] == "energizers":
        user["energizers"] = user.get("energizers", 0) + chosen["value"]
        result_text = get_text(user, "spin_win_energizers", value=chosen["value"])
    elif chosen["type"] == "xp":
        user["xp"] = user.get("xp", 0) + chosen["value"]
        result_text = get_text(user, "spin_win_xp", value=chosen["value"])
    elif chosen["type"] == "intim_scenes":
        user["intim_scenes"] = user.get("intim_scenes", 0) + chosen["value"]
        result_text = get_text(user, "spin_win_intim", value=chosen["value"])
    elif chosen["type"] == "subscription_pro":
        grant_subscription_days(user, "pro", 5)
        user["last_daily_reset"] = None
        _reset_daily_quota_if_needed(user)
        result_text = get_text(user, "spin_win_pro")
    elif chosen["type"] == "subscription_super":
        grant_subscription_days(user, "super_pro", 3)
        user["last_daily_reset"] = None
        _reset_daily_quota_if_needed(user)
        result_text = get_text(user, "spin_win_super")
    else:
        result_text = get_text(user, "spin_nothing")

    save_data(user_data)

    rows = []
    free_left = free_spins_left(user)
    if free_left > 0:
        rows.append([InlineKeyboardButton(
            text=get_text(user, "free", left=free_left, total=free_spins_allowed(user)),
            callback_data="spin_free", style="success")])
    rows.append([InlineKeyboardButton(text=get_text(user, "spin_more"), callback_data="spin_paid", style="success")])
    rows.append([InlineKeyboardButton(text=get_text(user, "back"), callback_data="spin_back", style="danger")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

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
    await call.message.answer(get_text(user, "referral", link=link, count=count, earned_bucks=count * 30, earned_energizers=count * 3), parse_mode="Markdown")
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
        [InlineKeyboardButton(text=get_text(user, "subs_btn_pro"), callback_data="buy:subscribe_pro", style="success")],
        [InlineKeyboardButton(text=get_text(user, "subs_btn_super"), callback_data="buy:subscribe_super", style="success")],
        [InlineKeyboardButton(text=get_text(user, "subs_btn_elite"), callback_data="buy:subscribe_elite", style="success")],
        [InlineKeyboardButton(text=get_text(user, "subs_btn_upgrade"), callback_data="buy:upgrade_to_super", style="success")],
        [InlineKeyboardButton(text=get_text(user, "back_to_profile"), callback_data="back_to_profile", style="danger")]
    ])
    text = get_text(user, "subs_title") + "\n\n" + get_text(user, "subs_body")
    await call.message.answer(text, reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "profile_bundles")
async def profile_bundles(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer(get_text(user, "need_character_alert"), show_alert=True)
        return
    # Кнопки теперь просто "название — цена" без сырых "5⚡+60💵" в них — сама расшифровка,
    # что именно даёт каждый бандл, вынесена в текст сообщения над кнопками.
    breakdown = "\n".join(
        get_text(user, "bundle_breakdown_line", emoji=item["emoji"],
                  name=item.get(user.get("lang", "ru"), item["ru"]),
                  energizers=item["energizers"], bucks=item["bucks"])
        for item in BUNDLES.values()
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=bundle_option_label(key, user),
                              callback_data=f"buy:{key}", style="success")]
        for key in BUNDLES
    ] + [
        [InlineKeyboardButton(text=get_text(user, "back_to_profile"), callback_data="back_to_profile", style="danger")]
    ])
    await call.message.answer(get_text(user, "bundles_title") + "\n" + breakdown,
                              reply_markup=keyboard, parse_mode="Markdown")
    await call.answer()


def spend_bucks(user, price):
    if user.get("bucks", 0) < price:
        return False
    user["bucks"] -= price
    return True


async def grant_gift_xp(chat_id, user, amount):
    """Такая же проверка уровня близости, что и в handle_message при обычном сообщении —
    вынесена отдельно, чтобы не трогать стабильный основной хендлер ради ещё одного источника XP."""
    user["xp"] = max(0, user.get("xp", 0) + amount)
    new_level = get_intimacy_level(user)
    old_level = user.get("last_level", 0)
    if new_level != old_level:
        user["last_level"] = new_level
        if new_level >= INTIM_LEVEL_REWARD and not user.get("intim_scene_unlocked"):
            user["intim_scene_unlocked"] = True
        if new_level > old_level:
            congrats = get_level_congratulation(user, new_level)
            if congrats:
                await bot.send_message(chat_id, congrats, reply_markup=get_full_kb(user))
            if new_level == INTIM_LEVEL_REWARD:
                await bot.send_message(chat_id, get_text(user, "intim_free_level"), reply_markup=get_full_kb(user))
    save_data(user_data)


def gift_effective_item(item, user):
    """Для аксессуаров с male_variant подменяет вид/название под персонажа-мужчину (часы вместо
    каблуков и т.п.) — цена и эффекты (satiety/mood/xp) всегда берутся из базового item, вариант
    переопределяет только emoji/ru/en/de/reaction_hint."""
    variant = item.get("male_variant")
    if variant and user.get("gender") == "male":
        return {**item, **variant}
    return item


def gift_option_label(key, user):
    item = gift_effective_item(GIFT_ITEMS[key], user)
    lang = user.get("lang", "ru")
    label = item.get(lang, item["ru"])
    return f"{item['emoji']} {label}"


def medicine_option_label(key, user):
    item = MEDICINE_ITEMS[key]
    lang = user.get("lang", "ru")
    label = item.get(lang, item["ru"])
    return f"{item['emoji']} {label}"


def item_cooldown_key(category, key):
    return f"{category}:{key}"


def item_ready_at(user, category, key, item):
    """None, если товар уже можно купить/подарить, иначе — datetime, когда можно будет снова.
    Единый механизм и для еды (минуты), и для подарков (часы/дни) — раньше подарки-аксессуары
    были заблокированы НАВСЕГДА после первой покупки (repeatable=False), а еда вообще не
    ограничивалась; по фидбэку это заменено на интервал у каждого предмета свой (cooldown_minutes),
    чтобы нельзя было закормить/задарить одним и тем же раз в секунду, но и не блокировать вещь
    насовсем — большой подарок вроде телефона снова доступен, просто не сразу."""
    cooldown = item.get("cooldown_minutes")
    if not cooldown:
        return None
    last = user.get("item_cooldowns", {}).get(item_cooldown_key(category, key))
    if not last:
        return None
    try:
        ready_at = datetime.fromisoformat(last) + timedelta(minutes=cooldown)
    except (ValueError, TypeError):
        return None
    return ready_at if datetime.now() < ready_at else None


def mark_item_purchased(user, category, key):
    user.setdefault("item_cooldowns", {})[item_cooldown_key(category, key)] = datetime.now().isoformat()


def cooldown_phrase(user, ready_at):
    """Компактная человекочитаемая строка вида '2 ч'/'45 мин'/'3 дн' до момента ready_at."""
    seconds = max(1, (ready_at - datetime.now()).total_seconds())
    minutes = seconds / 60
    if minutes < 60:
        return get_text(user, "cd_min", n=max(1, round(minutes)))
    hours = minutes / 60
    if hours < 24:
        return get_text(user, "cd_hours", n=max(1, round(hours)))
    days = hours / 24
    return get_text(user, "cd_days", n=max(1, round(days)))


def format_item_effects(item, user):
    parts = []
    if item.get("full_restore"):
        parts.append(get_text(user, "effect_satiety_full"))
        parts.append(get_text(user, "effect_mood_full"))
        parts.append(get_text(user, "effect_water_full"))
    else:
        if item.get("satiety"):
            parts.append(get_text(user, "effect_satiety", n=item["satiety"]))
        if item.get("mood"):
            parts.append(get_text(user, "effect_mood", n=item["mood"]))
        if item.get("water"):
            parts.append(get_text(user, "effect_water", n=item["water"]))
    if item.get("xp"):
        parts.append(get_text(user, "effect_xp", n=item["xp"]))
    return ", ".join(parts)


def apply_shop_item_effects(user, item):
    if item.get("full_restore"):
        user["satiety"] = SATIETY_MAX
        user["mood"] = MOOD_MAX
        user["water"] = WATER_MAX
        user["water_zero_since"] = None
    else:
        if "satiety" in item:
            user["satiety"] = min(SATIETY_MAX, user.get("satiety", SATIETY_MAX) + item["satiety"])
        if "mood" in item:
            user["mood"] = min(MOOD_MAX, max(-MOOD_MAX, user.get("mood", 0) + item["mood"]))
        if "water" in item:
            user["water"] = min(WATER_MAX, user.get("water", WATER_MAX) + item["water"])
            if user["water"] > 0:
                user["water_zero_since"] = None
    if item.get("tipsy_minutes"):
        user["tipsy_until"] = (datetime.now() + timedelta(minutes=item["tipsy_minutes"])).isoformat()
        user["tipsy_level"] = item.get("tipsy_level", "light")


SHOP_CATEGORY_ORDER = ["food", "treat", "accessory"]
SHOP_CATEGORY_TEXT_KEY = {"food": "shop_category_food", "treat": "shop_category_treat", "accessory": "shop_category_accessory"}

# Каталог аксессуаров конечен и одноразовый — рано или поздно всё куплено. "Свой подарок" даёт
# запасной вариант: любой текст, который ещё не дарили (дубли по нормализованному тексту), с
# рандомным настроением из диапазона обычных аксессуаров (см. их mood выше — 18..45), а не
# средним: со случайным числом каждый раз приятнее, чем одна и та же предсказуемая цифра.
CUSTOM_GIFT_PRICE = 100
CUSTOM_GIFT_MOOD_RANGE = (18, 45)
CUSTOM_GIFT_MAX_LEN = 60

# Личная подпись к обычному (каталожному) подарку/еде — в отличие от custom-подарка это не
# отдельный предмет со своей ценой, а просто пара слов от пользователя поверх штатной покупки,
# см. execute_item_purchase/generate_shop_reaction.
ITEM_NOTE_MAX_LEN = 150


def get_shop_kb(user):
    """Один товар — один ряд на всю ширину: раньше в паре с этой кнопкой была ещё и ✍️ для
    записки, из-за чего у каждой кнопки оставалась едва половина ширины и текст (вместе с ценой)
    обрезался Телеграмом. Подарок/еда с запиской теперь отдельный экран — см. get_shop_note_kb."""
    entries = [(key, item, f"shop_food_{key}", False) for key, item in FOOD_ITEMS.items()]
    entries += [(key, item, f"shop_gift_{key}", True) for key, item in GIFT_ITEMS.items()]

    rows = []
    # Лекарства — только пока персонаж реально болен (см. ILLNESSES), сверху, до остальных
    # категорий: это самое срочное, что вообще может понадобиться в магазине сейчас.
    if user.get("illness"):
        rows.append([InlineKeyboardButton(text=get_text(user, "shop_category_medicine"), callback_data="shop_noop")])
        for key, item in MEDICINE_ITEMS.items():
            rows.append([InlineKeyboardButton(text=f"{medicine_option_label(key, user)} — {item['price']}💵",
                                              callback_data=f"shop_medicine_{key}", style="success")])
    for category in SHOP_CATEGORY_ORDER:
        cat_entries = [e for e in entries if e[1].get("category") == category]
        if not cat_entries:
            continue
        rows.append([InlineKeyboardButton(text=get_text(user, SHOP_CATEGORY_TEXT_KEY[category]), callback_data="shop_noop")])
        for key, item, callback_data, is_gift in cat_entries:
            if is_gift:
                label = gift_option_label(key, user)
            else:
                label = intim_option_label(FOOD_ITEMS, key, user)
            ready_at = item_ready_at(user, "gift" if is_gift else "food", key, item)
            suffix = f" — ⏳{cooldown_phrase(user, ready_at)}" if ready_at else f" — {item['price']}💵"
            rows.append([InlineKeyboardButton(text=f"{label}{suffix}", callback_data=callback_data, style="success")])
        # ВАЖНО: было "category = ..." внутри цикла выше — это затирало переменную внешнего
        # цикла (SHOP_CATEGORY_ORDER: food/treat/accessory), из-за чего проверка ниже никогда
        # не срабатывала и кнопка "Свой подарок" молча пропадала из магазина. Убрано.
        if category == "accessory":
            rows.append([InlineKeyboardButton(
                text=get_text(user, "custom_gift_btn", price=CUSTOM_GIFT_PRICE),
                callback_data="shop_custom_gift_start", style="success")])

    rows.append([InlineKeyboardButton(text=get_text(user, "shop_note_menu_btn"), callback_data="shop_note_menu", style="success")])
    rows.append([InlineKeyboardButton(text=get_text(user, "back_to_profile"), callback_data="back_to_profile", style="danger")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_shop_note_kb(user):
    """Тот же каталог, что в get_shop_kb, но кнопки ведут в написание личного сообщения (см.
    shop_item_note_start) вместо мгновенной покупки — отдельный экран, чтобы основной список
    магазина оставался в один столбец и не обрезался (см. get_shop_kb)."""
    entries = [(key, item, f"note_food_{key}", False) for key, item in FOOD_ITEMS.items()]
    entries += [(key, item, f"note_gift_{key}", True) for key, item in GIFT_ITEMS.items()]

    rows = []
    for category in SHOP_CATEGORY_ORDER:
        cat_entries = [e for e in entries if e[1].get("category") == category]
        if not cat_entries:
            continue
        rows.append([InlineKeyboardButton(text=get_text(user, SHOP_CATEGORY_TEXT_KEY[category]), callback_data="shop_noop")])
        for key, item, callback_data, is_gift in cat_entries:
            if is_gift:
                label = gift_option_label(key, user)
            else:
                label = intim_option_label(FOOD_ITEMS, key, user)
            ready_at = item_ready_at(user, "gift" if is_gift else "food", key, item)
            suffix = f" — ⏳{cooldown_phrase(user, ready_at)}" if ready_at else f" — {item['price']}💵"
            rows.append([InlineKeyboardButton(text=f"{label}{suffix}", callback_data=callback_data, style="success")])

    rows.append([InlineKeyboardButton(text=get_text(user, "back"), callback_data="profile_shop", style="danger")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.callback_query(lambda c: c.data == "shop_note_menu")
async def shop_note_menu(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.message.answer(get_text(user, "shop_note_title", bucks=user.get("bucks", 0)),
                              reply_markup=get_shop_note_kb(user), parse_mode="Markdown")
    await call.answer()


@dp.callback_query(lambda c: c.data == "shop_custom_gift_start")
async def shop_custom_gift_start(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["writing_custom_gift"] = True
    save_data(user_data)
    await call.message.answer(get_text(user, "custom_gift_prompt", price=CUSTOM_GIFT_PRICE, n=CUSTOM_GIFT_MAX_LEN))
    await call.answer()


@dp.callback_query(lambda c: c.data == "shop_noop")
async def shop_noop_cb(call: types.CallbackQuery):
    await call.answer()


FEED_NUDGE_SATIETY_THRESHOLD = 20  # тот же порог, что и у "сильного голода" в build_hunger_rule
FEED_NUDGE_COOLDOWN_MINUTES = 90  # чтобы не слать одно и то же напоминание после каждого сообщения


def get_feed_nudge_kb(user):
    """Кормим прямо из подсказки теми же кнопками shop_food_*, что и в магазине —
    отдельного хендлера не нужно."""
    rows = []
    for key, item in FOOD_ITEMS.items():
        ready_at = item_ready_at(user, "food", key, item)
        suffix = f" — ⏳{cooldown_phrase(user, ready_at)}" if ready_at else f" — {item['price']}💵"
        rows.append([InlineKeyboardButton(text=f"{intim_option_label(FOOD_ITEMS, key, user)}{suffix}",
                                          callback_data=f"shop_food_{key}", style="success")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def maybe_send_feed_nudge(chat_id, user):
    """Многие не понимают, как вообще работает голод и чем кормить — вместо того чтобы
    заставлять искать магазин самому, подсказываем прямо в чате, когда сытость правда низкая."""
    if user.get("satiety", SATIETY_MAX) > FEED_NUDGE_SATIETY_THRESHOLD:
        return
    last = user.get("last_feed_nudge")
    if last:
        try:
            elapsed_min = (datetime.now() - datetime.fromisoformat(last)).total_seconds() / 60
            if elapsed_min < FEED_NUDGE_COOLDOWN_MINUTES:
                return
        except (ValueError, TypeError):
            pass
    user["last_feed_nudge"] = datetime.now().isoformat()
    save_data(user_data)
    await bot.send_message(chat_id, get_text(user, "hungry_nudge"), reply_markup=get_feed_nudge_kb(user))


ENERGY_NUDGE_THRESHOLD = 45  # тот же порог (30% бака), что и у сонной интонации в build_energy_rule
ENERGY_NUDGE_COOLDOWN_MINUTES = 90


async def maybe_send_energy_nudge(chat_id, user):
    """Симметрично с maybe_send_feed_nudge, но для энергии: предлагаем взбодриться, пока
    персонаж ещё не "уснул" по-настоящему (energy > 0) — на нуле уже работает asleep_message."""
    if is_asleep(user) or user.get("energy", ENERGY_MAX) > ENERGY_NUDGE_THRESHOLD:
        return
    last = user.get("last_energy_nudge")
    if last:
        try:
            elapsed_min = (datetime.now() - datetime.fromisoformat(last)).total_seconds() / 60
            if elapsed_min < ENERGY_NUDGE_COOLDOWN_MINUTES:
                return
        except (ValueError, TypeError):
            pass
    user["last_energy_nudge"] = datetime.now().isoformat()
    save_data(user_data)
    await bot.send_message(chat_id, get_text(user, "low_energy_nudge"), reply_markup=get_energy_nudge_kb(user))


@dp.callback_query(lambda c: c.data == "profile_shop")
async def profile_shop(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer(get_text(user, "need_character_alert"), show_alert=True)
        return
    await call.message.answer(get_text(user, "shop_title", bucks=user.get("bucks", 0)),
                              reply_markup=get_shop_kb(user), parse_mode="Markdown")
    await call.answer()


# Насильное перекармливание едой — только предупреждение, потом персонаж САМ отказывается
# есть дальше (никакой смерти: по фидбэку смерть должна грозить только за перепой алкоголем,
# у еды нет такой драмы). Перепаивание алкоголем (пиво/дорогое вино — определяем по наличию
# tipsy_minutes у предмета) — отдельный, более жёсткий счётчик: предупреждение, потом смерть.
# Считаем только подряд идущие покупки при уже почти полной сытости — обычное кормление
# голодного персонажа порог вообще не задевает (см. update_overfeed_strikes).
OVERFEED_SATIETY_THRESHOLD = 95
OVERFEED_WARN_STRIKES = 2
OVERFEED_REFUSE_STRIKES = 4  # еда: дальше персонаж просто отказывается есть (покупка блокируется)
OVERDRINK_DEATH_STRIKES = 4  # алкоголь: дальше персонаж умирает
OVERFEED_WARNING_HINT = (
    "Это уже слишком много подряд — тебя откровенно перекармливают/перепаивают через силу. Ты "
    "не благодаришь, а раздражённо и устало просишь остановиться («Хватит, хватит...»), "
    "отталкиваешь следующую порцию, тебе физически нехорошо от того, что в тебя запихивают."
)


def overfeed_would_refuse(user, item):
    """True, если персонаж уже отказывается есть ЭТУ еду — сытость слишком долго под завязку
    (см. OVERFEED_REFUSE_STRIKES). Только читает состояние, счётчик не трогает — вызывающий
    обязан проверить это ДО списания баксов (см. buy_food/handle_message), иначе деньги
    спишутся за еду, которую персонаж физически не станет есть. Алкоголь сюда не входит —
    у него своя ветка с смертью, а не отказом (см. update_overfeed_strikes)."""
    if item.get("tipsy_minutes"):
        return False
    if not item.get("satiety") or user.get("satiety", 0) < OVERFEED_SATIETY_THRESHOLD:
        return False
    return user.get("overfeed_strikes", 0) >= OVERFEED_REFUSE_STRIKES


def update_overfeed_strikes(user, item):
    """None — обычная покупка; "warning" — персонаж уже почти под завязку, но ещё держится;
    "death" — только для алкоголя, перепоили слишком много раз подряд. Еда сюда с "death" не
    попадает вообще — её накопленные подряд-переедания блокируются заранее (см.
    overfeed_would_refuse), до списания денег, так что здесь до отказа дело уже не доходит."""
    is_drink = bool(item.get("tipsy_minutes"))
    counter_key = "overdrink_strikes" if is_drink else "overfeed_strikes"
    if not item.get("satiety") or user.get("satiety", 0) < OVERFEED_SATIETY_THRESHOLD:
        user[counter_key] = 0
        return None
    user[counter_key] = user.get(counter_key, 0) + 1
    strikes = user[counter_key]
    if is_drink and strikes >= OVERDRINK_DEATH_STRIKES:
        return "death"
    if strikes >= OVERFEED_WARN_STRIKES:
        return "warning"
    return None


def get_death_kb(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "defibrillator_btn", price=PRODUCTS["defibrillator"]["stars"]),
                              callback_data="buy:defibrillator", style="success")],
        [InlineKeyboardButton(text=get_text(user, "new_character_btn"), callback_data="revive_new_character", style="danger")],
    ])


async def kill_character(chat_id, user, cause):
    """cause: "overdrink" (перепоили алкоголем через силу) или "dehydration" (слишком долго без
    воды, см. check_notifications). Персонаж НИЧЕГО не теряет физически в этот момент — умер он
    лишь флагом "dead", который блокирует чат (см. handle_message). Настоящая потеря истории/
    близости происходит, только если пользователь сам выберет бесплатный вариант "новый
    персонаж" на экране смерти — дефибриллятор просто снимает флаг, восстанавливать нечего."""
    user["dead"] = True
    user["overfeed_strikes"] = 0
    user["overdrink_strikes"] = 0
    user["water_zero_since"] = None
    save_data(user_data)
    text_key = "character_died_dehydration" if cause == "dehydration" else "character_died_overdrink"
    await bot.send_message(chat_id, get_text(user, text_key), reply_markup=get_death_kb(user))


async def execute_item_purchase(chat_id, user, category, key, item, note=None):
    """Общая часть после того, как cooldown, баксы и "не откажется ли есть это" уже проверены
    вызывающим: применяет эффекты, отмечает cooldown, подтверждает покупку и (если не спит)
    просит ИИ отреагировать в характере — опционально на личные слова пользователя (note), см.
    generate_shop_reaction. Используется и мгновенной покупкой (buy_food/buy_gift/buy_medicine),
    и покупкой с запиской (см. writing_item_note в handle_message) — оба пути должны одинаково
    попадать под перекорм/перепой/лечение, поэтому проверки ниже, а не в вызывающих хендлерах."""
    if category == "food":
        overfed = update_overfeed_strikes(user, item)
        if overfed == "death":
            await kill_character(chat_id, user, cause="overdrink")
            return
        if overfed == "warning":
            item = {**item, "reaction_hint": OVERFEED_WARNING_HINT}

    if category == "medicine":
        user["illness"] = None
        user["illness_since"] = None

    display_item = gift_effective_item(item, user) if category == "gift" else item
    apply_shop_item_effects(user, item)
    mark_item_purchased(user, category, key)
    save_data(user_data)
    if item.get("xp"):
        await grant_gift_xp(chat_id, user, item["xp"])
    await bot.send_message(chat_id, get_text(user, "item_bought", effects=format_item_effects(item, user)))
    if not is_asleep(user):
        await generate_shop_reaction(chat_id, user, display_item, category, note=note)


@dp.callback_query(lambda c: c.data.startswith("shop_food_"))
async def buy_food(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    key = call.data[len("shop_food_"):]
    item = FOOD_ITEMS.get(key)
    if not item:
        await call.answer()
        return
    ready_at = item_ready_at(user, "food", key, item)
    if ready_at:
        await call.answer(get_text(user, "item_cooldown_alert", when=cooldown_phrase(user, ready_at)), show_alert=True)
        return
    if overfeed_would_refuse(user, item):
        await call.answer(get_text(user, "overfeed_refuse_alert"), show_alert=True)
        return
    if not spend_bucks(user, item["price"]):
        await call.answer(get_text(user, "not_enough_bucks", n=item["price"] - user.get("bucks", 0)), show_alert=True)
        return
    await call.answer()
    await execute_item_purchase(call.message.chat.id, user, "food", key, item)


@dp.callback_query(lambda c: c.data.startswith("shop_gift_"))
async def buy_gift(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    key = call.data[len("shop_gift_"):]
    base_item = GIFT_ITEMS.get(key)
    if not base_item:
        await call.answer()
        return
    ready_at = item_ready_at(user, "gift", key, base_item)
    if ready_at:
        await call.answer(get_text(user, "item_cooldown_alert", when=cooldown_phrase(user, ready_at)), show_alert=True)
        return
    if not spend_bucks(user, base_item["price"]):
        await call.answer(get_text(user, "not_enough_bucks", n=base_item["price"] - user.get("bucks", 0)), show_alert=True)
        return
    await call.answer()
    await execute_item_purchase(call.message.chat.id, user, "gift", key, base_item)


@dp.callback_query(lambda c: c.data.startswith("shop_medicine_"))
async def buy_medicine(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    key = call.data[len("shop_medicine_"):]
    item = MEDICINE_ITEMS.get(key)
    if not item:
        await call.answer()
        return
    illness = user.get("illness")
    if not illness:
        await call.answer(get_text(user, "not_sick_alert"), show_alert=True)
        return
    if illness not in item["cures"]:
        await call.answer(get_text(user, "wrong_medicine_alert"), show_alert=True)
        return
    if not spend_bucks(user, item["price"]):
        await call.answer(get_text(user, "not_enough_bucks", n=item["price"] - user.get("bucks", 0)), show_alert=True)
        return
    await call.answer()
    await execute_item_purchase(call.message.chat.id, user, "medicine", key, item)


@dp.callback_query(lambda c: c.data.startswith("note_food_") or c.data.startswith("note_gift_"))
async def shop_item_note_start(call: types.CallbackQuery):
    """Кнопка ✍️ рядом с предметом — та же покупка, что и обычная кнопка, но перед списанием
    просит пользователя написать личное сообщение, которое попадёт и в подтверждение, и в
    промпт ИИ-реакции (см. execute_item_purchase/generate_shop_reaction). cooldown и баксы
    проверяем уже здесь, чтобы не просить писать душевные слова, а потом отказать."""
    user = get_user(call.from_user.id)
    is_gift = call.data.startswith("note_gift_")
    category = "gift" if is_gift else "food"
    key = call.data[len(f"note_{category}_"):]
    catalog = GIFT_ITEMS if is_gift else FOOD_ITEMS
    item = catalog.get(key)
    if not item:
        await call.answer()
        return
    ready_at = item_ready_at(user, category, key, item)
    if ready_at:
        await call.answer(get_text(user, "item_cooldown_alert", when=cooldown_phrase(user, ready_at)), show_alert=True)
        return
    if user.get("bucks", 0) < item["price"]:
        await call.answer(get_text(user, "not_enough_bucks", n=item["price"] - user.get("bucks", 0)), show_alert=True)
        return
    user["writing_item_note"] = {"category": category, "key": key}
    save_data(user_data)
    await call.message.answer(get_text(user, "item_note_prompt", n=ITEM_NOTE_MAX_LEN))
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


@dp.callback_query(lambda c: c.data == "toggle_notifications")
async def toggle_notifications(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if get_subscription_level(user) not in ("super_pro", "elite"):
        await call.answer(get_text(user, "mute_requires_sub_alert"), show_alert=True)
        return
    user["notifications_muted"] = not user.get("notifications_muted", False)
    save_data(user_data)
    key = "notifications_muted_alert" if user["notifications_muted"] else "notifications_unmuted_alert"
    await call.answer(get_text(user, key), show_alert=True)


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
# РЕАЛЬНАЯ конвертация звёзд/рублей/долларов, а не "рубли=звёзды 1:1": курс на 12.09.2026 —
# 1 звезда ≈ $0.014 (официальный курс Telegram, TON/200 — не курс покупки через App
# Store/Google Play, там дороже из-за комиссии самих Apple/Google, ~$0.02, которую мы всё
# равно не получаем) × ~84.26₽/$ (ЦБ) ≈ 1.18₽/звезда. У каждого товара своя пара
# "якорь -> производное":
#   - подписки/апгрейд — якорь rub (та цена, что уже настроена экономикой прошлых раундов),
#     stars посчитаны от неё и округлены ВНИЗ до красивого числа;
#   - горячая сцена, бандлы, платная прокрутка, разбудить сейчас — явно попросили звёзды
#     оставить/вернуть как есть, так что здесь наоборот: якорь stars, rub/usd посчитаны от них.
PRODUCTS = {
    "subscribe_pro": {"stars": 220, "usd": 3.1, "rub": 260},
    "subscribe_super": {"stars": 500, "usd": 7.1, "rub": 600},
    "subscribe_elite": {"stars": 1000, "usd": 14.2, "rub": 1200},
    "upgrade_to_super": {"stars": 350, "usd": 5.0, "rub": 420},
    "bundle_small": {"stars": 30, "usd": 0.4, "rub": 35},
    "bundle_medium": {"stars": 80, "usd": 1.1, "rub": 94},
    "bundle_large": {"stars": 200, "usd": 2.8, "rub": 236},
    "spin_paid_20": {"stars": 15, "usd": 0.2, "rub": 18},
    "intim_scene": {"stars": 45, "usd": 0.6, "rub": 53},
    "wake_now": {"stars": 50, "usd": 0.7, "rub": 59},
    "defibrillator": {"stars": 120, "usd": 1.7, "rub": 142},
}
# Подстраховка на случай, если когда-нибудь добавят товар без явного rub — тогда он по
# умолчанию будет 1:1 со звёздами, а не упадёт с KeyError.
for _product in PRODUCTS.values():
    _product.setdefault("rub", _product["stars"])

# Что именно выдаёт каждый бандл — энергетики (⚡ энергия) и баксы (💵 еда/подарки в магазине);
# сообщений в игре больше нет вообще, чат ограничивает только энергия/сон.
BUNDLES = {
    "bundle_small": {"energizers": 5, "bucks": 60, "emoji": "🎒",
                      "ru": "Стартовый набор", "en": "Starter Pack", "de": "Starter-Paket"},
    "bundle_medium": {"energizers": 14, "bucks": 180, "emoji": "⚖️",
                       "ru": "Средний набор", "en": "Medium Pack", "de": "Mittleres Paket"},
    "bundle_large": {"energizers": 40, "bucks": 500, "emoji": "👑",
                      # Было 50 — по фидбэку всё ещё многовато, срезали до 40 (200⭐/40=5.0⭐ за
                      # энергетик). История: 36 изначально (хуже PRO) -> пробовали 72 психтрюком
                      # (уполовинить ENERGIZER_RESTORE_AMOUNT, отклонено) -> 50 (чуть лучше PRO) -> 40.
                      "ru": "VIP набор", "en": "VIP Pack", "de": "VIP-Paket"},
}


def bundle_option_label(key, user):
    item = BUNDLES[key]
    lang = user.get("lang", "ru")
    name = item.get(lang, item["ru"])
    return get_text(user, "bundle_btn", emoji=item["emoji"], name=name,
                     energizers=item["energizers"], bucks=item["bucks"], price=PRODUCTS[key]["stars"])


def is_method_enabled(method):
    if method == "stars":
        return True
    if method == "crypto":
        # Отключено по просьбе — CryptoBot не заработал у пользователя. Интеграция ниже
        # (create_crypto_invoice и т.п.) оставлена нетронутой: вернуть можно, заменив это
        # на bool(CRYPTO_PAY_TOKEN), если решат разбираться и включать обратно.
        return False
    if method == "lava":
        return bool(LAVA_SECRET_KEY and LAVA_SHOP_ID)
    return False


# Товары, открывающие откровенный контент (стили "Грубый"/"Соблазн" с adult=True, апгрейд до
# них, горячая сцена) — по ним оплата через Lava недоступна: это НЕ маскировка (слова в текстах
# не меняются), а честное разведение каналов оплаты по тому, что товар реально даёт. PRO
# (без adult-стилей) на Lava остаётся, т.к. там действует SAFE_CONTENT_RULE и явного контента
# в принципе не бывает. Бандлы/энергетики/прокрутки/разбудить сейчас — нейтральные, сами по
# себе доступ к 18+ не открывают, тоже остаются на Lava. Дефибриллятор — туда же: восстанавливает
# в том числе историю adult-стилей/сцен, если она была, так что по той же логике не для Lava.
LAVA_RESTRICTED_PRODUCTS = {"subscribe_super", "subscribe_elite", "upgrade_to_super", "intim_scene", "defibrillator"}


def available_payment_methods(payload=None):
    methods = [m for m in ("stars", "crypto", "lava") if is_method_enabled(m)]
    if payload in LAVA_RESTRICTED_PRODUCTS:
        methods = [m for m in methods if m != "lava"]
    return methods


def product_invoice_texts(user, payload):
    """Заголовок, описание и подпись строки счёта для товара."""
    if payload == "subscribe_pro":
        return (get_text(user, "invoice_pro_title"), get_text(user, "invoice_pro_desc"),
                get_text(user, "invoice_pro_label"))
    if payload == "subscribe_super":
        return (get_text(user, "invoice_super_title"), get_text(user, "invoice_super_desc"),
                get_text(user, "invoice_super_label"))
    if payload == "subscribe_elite":
        return (get_text(user, "invoice_elite_title"), get_text(user, "invoice_elite_desc"),
                get_text(user, "invoice_elite_label"))
    if payload == "upgrade_to_super":
        return (get_text(user, "invoice_upgrade_title"), get_text(user, "invoice_upgrade_desc"),
                get_text(user, "invoice_upgrade_label"))
    if payload == "intim_scene":
        return (get_text(user, "invoice_intim_title"), get_text(user, "invoice_intim_desc"),
                get_text(user, "invoice_intim_label"))
    if payload == "wake_now":
        return (get_text(user, "invoice_wake_title"), get_text(user, "invoice_wake_desc"),
                get_text(user, "invoice_wake_label"))
    if payload == "defibrillator":
        return (get_text(user, "invoice_defib_title"), get_text(user, "invoice_defib_desc"),
                get_text(user, "invoice_defib_label"))
    if payload in BUNDLES:
        bundle = BUNDLES[payload]
        price = PRODUCTS[payload]["stars"]
        name = bundle.get(user.get("lang", "ru"), bundle["ru"])
        return (get_text(user, "invoice_bundle_title", name=name, **bundle),
                get_text(user, "invoice_bundle_desc", price=price, **bundle),
                get_text(user, "invoice_bundle_label"))
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

    if payload in BUNDLES:
        bundle = BUNDLES[payload]
        user["energizers"] = user.get("energizers", 0) + bundle["energizers"]
        user["bucks"] = user.get("bucks", 0) + bundle["bucks"]
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "payment_bundle_success", **bundle))
    elif payload == "subscribe_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        # Форсируем полный пересчёт дневных плюшек (сообщения, баксы, энергетики, бесплатные
        # сцены) прямо сейчас, а не только с завтрашнего дня — раньше здесь просто вручную
        # проставлялись daily_messages/last_daily_reset, и бонус баксов/энергетиков в день
        # покупки просто пропадал.
        user["last_daily_reset"] = None
        _reset_daily_quota_if_needed(user)
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "payment_pro_success"))
    elif payload == "subscribe_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["last_daily_reset"] = None
        _reset_daily_quota_if_needed(user)
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "payment_super_success"))
    elif payload == "subscribe_elite":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "elite"
        user["last_daily_reset"] = None
        _reset_daily_quota_if_needed(user)
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "payment_elite_success"))
    elif payload == "upgrade_to_super":
        if has_active_subscription(user) and get_subscription_level(user) == "pro":
            old_expiry = user["subscription"]["expires_at"]
            user["subscription"]["level"] = "super_pro"
            user["last_daily_reset"] = None
            _reset_daily_quota_if_needed(user)
            save_data(user_data)
            expiry_str = datetime.fromisoformat(old_expiry).strftime('%d.%m.%Y %H:%M')
            await bot.send_message(chat_id, get_text(user, "payment_upgrade_success", date=expiry_str))
    elif payload == "intim_scene":
        user["intim_scenes"] = user.get("intim_scenes", 0) + 1
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "payment_intim_success"))
    elif payload == "wake_now":
        user["energy"] = ENERGY_MAX
        user["sleep_until"] = None
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "woken_up"))
    elif payload == "defibrillator":
        # Ничего не восстанавливаем — "смерть" была лишь флагом, ничего физически не стёрлось
        # (см. kill_character), так что просто снимаем блокировку чата.
        user["dead"] = False
        save_data(user_data)
        await bot.send_message(chat_id, get_text(user, "defibrillator_success"))
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
        [InlineKeyboardButton(text=get_text(user, "pay_open_invoice"), url=url, style="success")]
    ])
    await call.message.answer(f"{title}\n\n{get_text(user, 'pay_invoice_ready')}", reply_markup=keyboard)


def get_payment_methods_kb(user, payload):
    prices = PRODUCTS[payload]
    labels = {
        "stars": get_text(user, "pay_stars", amount=prices["stars"]),
        "crypto": get_text(user, "pay_crypto", amount=prices["usd"]),
        "lava": get_text(user, "pay_lava", amount=prices["rub"]),
    }
    rows = [[InlineKeyboardButton(text=labels[method], callback_data=f"pay:{method}:{payload}", style="success")]
            for method in available_payment_methods(payload)]
    rows.append([InlineKeyboardButton(text=get_text(user, "back_to_profile"), callback_data="back_to_profile", style="danger")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def payment_blocked_reason(user, payload):
    """Те же проверки, что раньше висели на каждой кнопке покупки."""
    if payload in ("subscribe_pro", "subscribe_super", "subscribe_elite") and has_active_subscription(user):
        return get_text(user, "already_subscribed_alert")
    if payload == "upgrade_to_super" and get_subscription_level(user) != "pro":
        return get_text(user, "pro_only_alert")
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

    methods = available_payment_methods(payload)
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
    # available_payment_methods(payload), а не голый is_method_enabled(method) — вторая только
    # проверяет, что Lava вообще настроена, но не что она разрешена ИМЕННО для этого товара;
    # без этой проверки старая/подделанная callback-кнопка могла бы провести Lava-оплату
    # 18+-товара в обход того, что показывается в клавиатуре.
    if payload not in PRODUCTS or method not in available_payment_methods(payload):
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
        user_data.setdefault("__settings__", {})["maintenance_mode"] = True
        save_data(user_data)
        await message.answer("🛠️ Техобслуживание ВКЛ.")
    elif args[1].lower() == "off":
        maintenance_mode = False
        user_data.setdefault("__settings__", {})["maintenance_mode"] = False
        save_data(user_data)
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
        await message.answer(
            "/grant @username — SUPER PRO\n/grant @username pro — PRO\n/grant @username elite — ELITE\n"
            "/grant @username intim N — N горячих сцен\n/grant @username energizers N — N энергетиков\n"
            "/grant @username bucks N — N баксов"
        )
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
        await message.answer(f"✅ {args[1]} выдано горячих сцен: {amount}.")
        return
    if len(args) >= 3 and args[2].lower() in ("energizers", "bucks"):
        field = args[2].lower()
        amount = 1
        if len(args) >= 4:
            try:
                amount = max(1, int(args[3]))
            except ValueError:
                await message.answer("❌ Количество должно быть числом.")
                return
        user[field] = user.get(field, 0) + amount
        save_data(user_data)
        await message.answer(f"✅ {args[1]} выдано {field}: {amount}.")
        return
    level = "super_pro"
    if len(args) >= 3 and args[2].lower() in ("pro", "elite"):
        level = args[2].lower()
    user["subscription"]["active"] = True
    user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
    user["subscription"]["level"] = level
    # Форсируем полный пересчёт дневных плюшек (сообщения, баксы, энергетики, бесплатные сцены)
    # прямо сейчас — иначе, как раньше, они появились бы только на следующий день.
    user["last_daily_reset"] = None
    _reset_daily_quota_if_needed(user)
    save_data(user_data)
    label = {"pro": "PRO", "super_pro": "SUPER PRO", "elite": "ELITE"}[level]
    await message.answer(f"✅ {args[1]} выдана {label}.")


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


@dp.message(Command("models"))
async def models_cmd(message: types.Message):
    """Точный ID модели в каталоге provod.ai нельзя узнать из кода без живого запроса —
    эта команда даёт админу посмотреть каталог напрямую с продовского сервера (где реально
    есть PROVOD_API_KEY), вместо того чтобы я гадал строку и рисковал молчаливым 404->fallback."""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    invalidate_model_cache("ai")
    invalidate_model_cache("intim")
    catalog = _fetch_model_catalog()
    if not catalog:
        await message.answer("❌ Не удалось получить каталог моделей — см. логи бота (сеть/ключ).")
        return
    deepseek_matches = sorted(m for m in catalog if "deepseek" in m.lower())
    lines = [f"Всего моделей в каталоге: {len(catalog)}", ""]
    if deepseek_matches:
        lines.append("🔍 Содержат «deepseek»:")
        lines.extend(f"• {m}" for m in deepseek_matches)
    else:
        lines.append("❌ Ни одной модели с «deepseek» в названии в каталоге не нашлось.")
    lines.append("")
    lines.append(f"Сейчас будет выбрано для обычного чата: {resolve_model('ai')}")
    lines.append(f"Сейчас будет выбрано для /hot: {resolve_model('intim')}")
    await send_long_to_chat(message.chat.id, "\n".join(lines))


# ============================================================
#  КОМАНДА /hot — ВЫБОР И ГЕНЕРАЦИЯ ГОРЯЧЕЙ СЦЕНЫ
# ============================================================
def get_intim_types_kb(user):
    buttons = [InlineKeyboardButton(text=intim_option_label(INTIM_SCENES, key, user),
                                    callback_data=f"intim_type_{key}")
               for key in INTIM_SCENES]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(text=get_text(user, "back"), callback_data="profile_back", style="danger")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_intim_locations_kb(user, scene_type):
    buttons = [InlineKeyboardButton(text=intim_option_label(INTIM_LOCATIONS, key, user),
                                    callback_data=f"intim_loc_{scene_type}:{key}")
               for key in INTIM_LOCATIONS]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_intim_dominant_kb(user, scene_type, location):
    buttons = [InlineKeyboardButton(text=intim_option_label(INTIM_DOMINANTS, key, user),
                                    callback_data=f"intim_dom_{scene_type}:{location}:{key}")
               for key in INTIM_DOMINANTS]
    return InlineKeyboardMarkup(inline_keyboard=[[b] for b in buttons])


def get_intim_buy_kb(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "intim_buy_btn"), callback_data="buy:intim_scene", style="success")],
        [InlineKeyboardButton(text=get_text(user, "back"), callback_data="profile_back", style="danger")],
    ])


def get_wake_kb(user):
    """Показывается только когда собеседник по-настоящему "спит" (energy <= 0, is_asleep()==True).
    Если есть свой энергетик — им можно разбудить бесплатно; в любом случае ниже есть мгновенная
    платная кнопка "разбудить сейчас" — она нужна именно тем, кто не хочет ждать и не хочет
    запасаться энергетиками заранее. У ELITE сверху ещё и бесплатная кнопка раз в неделю."""
    rows = []
    if elite_free_wake_available(user):
        rows.append([InlineKeyboardButton(text=get_text(user, "elite_free_wake_btn"), callback_data="elite_free_wake", style="success")])
    if user.get("energizers", 0) > 0:
        rows.append([InlineKeyboardButton(text=get_text(user, "wake_energizer_btn"), callback_data="wake_up", style="success")])
    rows.append([InlineKeyboardButton(text=get_text(user, "wake_now_btn", price=PRODUCTS["wake_now"]["stars"]),
                                      callback_data="buy:wake_now", style="success")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_energy_nudge_kb(user):
    """Для "сонной" подсказки (energy низкая, но ещё НЕ спит) — в отличие от get_wake_kb здесь
    не должно быть платной кнопки "разбудить сейчас": будить ещё некого, собеседник и так
    отвечает. Если есть энергетик — предлагаем взбодриться им; если их нет — ведём в магазин
    их купить, а не сразу к оплате звёздами за то, что ещё не наступило."""
    if user.get("energizers", 0) > 0:
        rows = [[InlineKeyboardButton(text=get_text(user, "wake_energizer_btn"), callback_data="wake_up", style="success")]]
    else:
        rows = [[InlineKeyboardButton(text=get_text(user, "no_energizers_shop_btn"), callback_data="profile_bundles", style="success")]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.callback_query(lambda c: c.data == "wake_up")
async def wake_up_cb(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if use_energizer(user):
        await call.message.answer(get_text(user, "woken_up"))
        await call.answer()
    else:
        await call.answer(get_text(user, "not_enough_energizers"), show_alert=True)


@dp.callback_query(lambda c: c.data == "elite_free_wake")
async def elite_free_wake_cb(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not elite_free_wake_available(user):
        await call.answer(get_text(user, "elite_free_wake_used_alert"), show_alert=True)
        return
    now = datetime.now()
    user["elite_free_wake_week"] = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]}"
    user["energy"] = ENERGY_MAX
    user["sleep_until"] = None
    save_data(user_data)
    await call.message.answer(get_text(user, "elite_free_wake_success"))
    await call.answer()


async def show_intim_menu(chat_id, user):
    available = intim_scenes_available(user)
    if available <= 0:
        await bot.send_message(chat_id, get_text(user, "intim_none"),
                               reply_markup=get_intim_buy_kb(user))
        return
    await bot.send_message(chat_id, get_text(user, "intim_menu_title", n=available),
                           reply_markup=get_intim_types_kb(user), parse_mode="Markdown")


@dp.message(Command("hot"))
async def intim_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["verified"] or not user["agreement_accepted"]:
        await message.answer(get_text(user, "finish_registration_first"))
        return
    if not user["personality_ready"]:
        await message.answer(get_text(user, "intim_need_character"))
        return
    # /hot нарочно не проверяет is_asleep(user) — это отдельный платный раздел именно для тех,
    # кто не хочет ждать (ни уровня близости, ни "сна" персонажа): раз сцена куплена/доступна,
    # она выдаётся сразу, тамагочи-механика на неё не распространяется. Болезнь — намеренное
    # ИСКЛЮЧЕНИЕ из этого правила (явно попросили): персонажу физически не до того.
    if user.get("illness"):
        await message.answer(get_text(user, "intim_blocked_illness"))
        return
    await show_intim_menu(message.chat.id, user)


@dp.message(Command("feed"))
async def feed_cmd(message: types.Message):
    """Прямой доступ к еде без похода через профиль → магазин → категория — те же кнопки
    shop_food_*, что и в get_feed_nudge_kb, отдельного колбэка не нужно."""
    user = get_user(message.from_user.id)
    if not user["verified"] or not user["agreement_accepted"]:
        await message.answer(get_text(user, "finish_registration_first"))
        return
    if not user["personality_ready"]:
        await message.answer(get_text(user, "need_character_alert"))
        return
    await message.answer(get_text(user, "feed_menu_title", bucks=user.get("bucks", 0)),
                         reply_markup=get_feed_nudge_kb(user))


@dp.message(Command("work"))
async def work_cmd(message: types.Message):
    """Свободный (без звёзд) способ заработать баксы: персонаж уходит на WORK_DURATION_MINUTES,
    всё это время обычный чат недоступен (см. handle_message), но /hot по-прежнему работает —
    та же логика, что и у сна (см. intim_cmd)."""
    user = get_user(message.from_user.id)
    if not user["verified"] or not user["agreement_accepted"]:
        await message.answer(get_text(user, "finish_registration_first"))
        return
    if not user["personality_ready"]:
        await message.answer(get_text(user, "need_character_alert"))
        return
    if user.get("dead"):
        await message.answer(get_text(user, "character_died"), reply_markup=get_death_kb(user))
        return
    if is_asleep(user):
        await message.answer(get_text(user, "asleep_message", price=PRODUCTS["wake_now"]["stars"]), reply_markup=get_wake_kb(user))
        return
    if is_working(user):
        await message.answer(get_text(user, "still_working"))
        return
    user["working_until"] = (datetime.now() + timedelta(minutes=WORK_DURATION_MINUTES)).isoformat()
    save_data(user_data)
    await message.answer(get_text(user, "work_started", minutes=WORK_DURATION_MINUTES))


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
    await safe_delete(call.message)
    await bot.send_message(call.message.chat.id, get_text(user, "intim_choose_dominant"),
                           reply_markup=get_intim_dominant_kb(user, scene_type, location))
    await call.answer()


@dp.callback_query(lambda c: c.data.startswith("intim_dom_"))
async def choose_intim_dominant(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    scene_type, location, dominant = call.data[len("intim_dom_"):].split(":", 2)
    if scene_type not in INTIM_SCENES or location not in INTIM_LOCATIONS or dominant not in INTIM_DOMINANTS:
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

    ok = await generate_intim_scene(call, user, scene_type, location=location, dominant=dominant, free=kind != "paid")
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


def build_intim_prompt(user, scene_type, location, dominant="any"):
    """Отдельный промпт для интим-сцен — НЕ через build_prompt(). Там SAFE/ADULT правило переключается
    по обычному стилю чата (а не по праву на интим-сцену), плюс сдержанность по уровню близости и
    медленный темп сближения — это заставляло ИИ уходить от темы вместо прямого показа выбранной сцены.
    Здесь только личность персонажа, безусловный ADULT_CONTENT_RULE и сама сцена. scene_type
    здесь уже конкретный (random разрешается в generate_intim_scene ДО вызова) — иначе
    "продолжение" сцены каждый раз перевыбирало бы случайный тип заново."""
    scene = INTIM_SCENES[scene_type]
    place = INTIM_LOCATIONS[location]
    dominant_rule = INTIM_DOMINANTS.get(dominant, INTIM_DOMINANTS["any"])["prompt"]

    if user.get("custom_character"):
        # Для своего персонажа НЕ запрещаем называть себя по имени (в отличие от пресетных
        # персон ниже) — иначе прямой конфликт с "Ты — Бэтмен" даёт обезличенный результат:
        # модель не может опереться на единственный явный сигнал личности, который у неё есть.
        identity = (
            f"Ты — {user['custom_character']}. Полностью вживись в эту личность и её характер: если "
            f"персонаж узнаваем, веди себя как он — с его характерными чертами и манерой речи, а не "
            f"обезличенно. Можешь называть себя по имени, когда это естественно по ходу разговора.\n"
        )
        style_flavor = ""
        name_ban = (
            "Ты НИКОГДА не спрашиваешь имя собеседника и не используешь его имя, даже если оно было "
            "названо. Обращайся к собеседнику ТОЛЬКО на «ты» — даже если в той же фразе упомянут предмет "
            "(телефон, окно и т.п.), взгляд или действие в сторону самого собеседника называй "
            "«тебя/тебе», а НЕ «него/неё» (пример ошибки: «перевожу взгляд с телефона на него» — "
            "правильно «...на тебя»).\n"
        )
    else:
        world_desc = WORLDS[user["world"]]
        gender_info = GENDERS[user["gender"]]
        style_key = get_display_style(user)
        style_desc = STYLES[style_key]["description"]
        identity = (
            f"Ты — {gender_info['name']}, тебе {gender_info['age']} лет. Ты живёшь в {world_desc} "
            f"{style_desc}\n"
        )
        style_flavor = STYLE_INTIM_FLAVOR.get(style_key, "")
        name_ban = (
            "**ВАЖНЕЙШЕЕ ПРАВИЛО:** Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь "
            "«меня зовут», не используешь своё имя. Ты также НИКОГДА не спрашиваешь имя собеседника и не "
            "используешь его имя, даже если оно было названо. Обращайся к собеседнику ТОЛЬКО на «ты». Даже "
            "если в той же фразе упомянут предмет (телефон, окно и т.п.), взгляд или действие в сторону "
            "самого собеседника называй «тебя/тебе», а НЕ «него/неё» — местоимение должно указывать на "
            "человека, а не на предмет рядом с ним (пример ошибки: «перевожу взгляд с телефона на него» — "
            "правильно «...на тебя»).\n"
        )

    user_gender = user.get("user_gender", "male")
    if user_gender == "male":
        gender_context = ("Ты обращаешься к нему в мужском роде («ты», «он», «ему», «его») — И ВАЖНО: "
                           "прилагательные/причастия о нём тоже в мужском роде («ты способен», «ты готов», "
                           "«ты был» — а не «способна», «готова», «была»).")
        anatomy_rule = ("У собеседника есть половой член. Если в сцене есть оральный секс, направленный "
                         "НА собеседника — это минет (оральная стимуляция члена), никогда не куни: у "
                         "собеседника нет вульвы.\n")
    else:
        gender_context = ("Ты обращаешься к ней в женском роде («ты», «она», «ей», «её») — И ВАЖНО: "
                           "прилагательные/причастия о ней тоже в женском роде («ты способна», «ты готова», "
                           "«ты была» — а не «способен», «готов», «был»).")
        anatomy_rule = ("У собеседницы нет полового члена — есть вульва. Если в сцене есть оральный секс, "
                         "направленный НА собеседницу — это куни (оральная стимуляция клитора/влагалища), "
                         "никогда не минет: собеседнице физически нечего сосать.\n")

    if not user.get("custom_character"):
        if user["gender"] == "male":
            anatomy_rule += ("У тебя есть половой член. Если собеседник доставляет оральные ласки ТЕБЕ — это "
                              "минет, никогда не куни: у тебя нет вульвы.\n")
            anatomy_rule += ("ВАЖНО про себя: ты мужчина, поэтому глаголы и прилагательные о себе — в мужском "
                              "роде («я думал», «я был готов» — а не «думала», «была готова»).\n")
        else:
            anatomy_rule += ("У тебя нет полового члена — есть вульва. Если собеседник доставляет оральные "
                              "ласки ТЕБЕ — это куни, никогда не минет: тебе физически нечего сосать.\n")
            anatomy_rule += ("ВАЖНО про себя: ты женщина, поэтому глаголы и прилагательные о себе — в женском "
                              "роде («я думала», «я была готова» — а не «думал», «был готов»).\n")

    prompt = (
        f"{name_ban}"
        f"{identity}"
        f"{gender_context}\n"
        f"{anatomy_rule}"
        f"{ADULT_CONTENT_RULE}"
        "Твои обычные черты характера (сдержанность, стеснительность, неторопливость и т.п.) проявляются "
        "только в интонациях, словах и жестах — но не в отказе от сцены и не в уходе от темы. Собеседник "
        "уже выбрал эту сцену в меню и оплатил её, то есть точно этого хочет — ты не сдерживаешься и не "
        "переключаешься на более лёгкую тему.\n"
    )
    if style_flavor:
        prompt += f"{style_flavor}\n"
    prompt += f"\n**СЦЕНА:** {scene['ru']}."
    if location != "any":
        prompt += f" Место: {place['ru']}."
    prompt += f" {dominant_rule}\n"
    tension = place.get("tension")
    if tension:
        prompt += f"{tension}\n"
    prompt += (
        f"Собеседник специально выбрал в меню именно «{scene['ru']}» — раскрывай сразу это действие, уже "
        "в первой паре «действие + реплика», без вступления на постороннюю тему и без более мягкой замены "
        "выбранного. Опиши сцену от лица своего персонажа как самостоятельный эпизод, начинающийся прямо "
        "сейчас, без всякой связи с обычной перепиской — считай, что никакого предыдущего разговора не "
        "было. Пиши развёрнуто и чувственно: передавай прикосновения, дыхание, взгляды, интонации голоса "
        "— а не только факт действия.\n"
        "**ФОРМАТ:** действие в *звёздочках* с новой строки, затем реплика с новой строки, между ними "
        "пустая строка. Минимум 3 пары «действие + реплика». Не обрывай сцену на середине.\n"
    )
    prompt += "\n" + get_language_rule(user)
    return prompt


async def generate_intim_scene(call, user, scene_type, location="any", dominant="any", free=False, continue_text=None):
    """Возвращает True, если сцена сгенерирована и отправлена. Намеренно не читает и не
    пишет в user["history"]: сцена — самостоятельный эпизод без всякой связи с обычным чатом
    (ни в контексте генерации, ни в том, что персонаж "помнит" потом). continue_text — если
    задан, это текст предыдущей части ЭТОЙ ЖЕ сцены (см. intim_continue_cb): модель продолжает
    её, а не начинает заново."""
    if scene_type == "random":
        scene_type = random.choice([key for key in INTIM_SCENES if key != "random"])
    chat_id = call.message.chat.id
    status_msg = await bot.send_message(chat_id, get_text(user, "intim_generating"))
    typing_task = asyncio.create_task(_keep_typing(chat_id))
    system_prompt = build_intim_prompt(user, scene_type, location, dominant)
    if continue_text:
        system_prompt += (
            "\n**ПРОДОЛЖЕНИЕ:** Это продолжение уже идущей сцены — предыдущая часть дана следующим "
            "сообщением. Не начинай сцену заново и не повторяй, что уже произошло: продолжай действие "
            "дальше, развивая его, с того момента, на котором оно остановилось."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": continue_text},
            {"role": "user", "content": "Продолжай."},
        ]
    else:
        messages = [
            {"role": "system", "content": system_prompt},
            # Некоторые провайдеры отклоняют запрос с 400 INVALID_REQUEST, если в messages
            # вообще нет non-system реплики — этот триггер ничего не значит по содержанию
            # (вся суть сцены задана в system), он просто заставляет модель начать отвечать.
            {"role": "user", "content": "Начинай сцену."},
        ]
    try:
        response = await asyncio.to_thread(
            call_ai, INTIM_MODEL, "intim",
            messages=messages,
            # temperature была 0.95 — чуть снижена, чтобы уменьшить (не гарантированно убрать)
            # случайные "склеенные" токены на смеси языков вроде "requestующий" в выдаче модели;
            # причина не в промпте (в нём нет ни слова на английском рядом со сценой), это
            # похоже на артефакт сэмплирования самой модели.
            temperature=0.85,
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
    user["last_activity"] = datetime.now().isoformat()
    user["last_hot_scene"] = {"text": clean_answer, "scene_type": scene_type, "location": location, "dominant": dominant}
    # Интим-сцены нарочно не тратят энергию/сытость: иначе платная сцена могла бы сама "усыпить"
    # персонажа и заблокировать пользователю следующее обычное сообщение — а это ровно то ожидание,
    # которого этот раздел должен избегать.
    save_data(user_data)

    await send_long_to_chat(chat_id, clean_answer, reply_markup=get_full_kb(user))

    remaining = intim_scenes_available(user)
    left_text = get_text(user, "intim_left", n=remaining)
    continue_kb = None
    if remaining > 0:
        left_text += "\n" + get_text(user, "intim_left_cta")
        continue_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(user, "intim_continue_btn"), callback_data="intim_continue", style="success")]
        ])
    await bot.send_message(chat_id, left_text, reply_markup=continue_kb)
    return True


@dp.callback_query(lambda c: c.data == "intim_continue")
async def intim_continue_cb(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    last = user.get("last_hot_scene")
    if not last:
        await call.answer()
        return
    if user.get("illness"):
        await call.answer(get_text(user, "intim_blocked_illness"), show_alert=True)
        return
    kind = consume_intim_scene(user)
    if kind is None:
        await call.answer(get_text(user, "intim_none"), show_alert=True)
        return
    await call.answer()
    ok = await generate_intim_scene(call, user, last["scene_type"], location=last["location"],
                                     dominant=last["dominant"], free=kind != "paid",
                                     continue_text=last["text"])
    if not ok:
        refund_intim_scene(user, kind)


# ============================================================
#  ВСПОМОГАТЕЛЬНОЕ ДЛЯ ОТВЕТОВ ИИ
# ============================================================
def extract_reaction_from_answer(text):
    # \*? и \s*$ — на случай, если модель всё же обернула тег в звёздочки (как остальные
    # действия по ФОРМАТИРОВАНИЮ) или оставила что-то после него: без этой терпимости тег
    # не распознаётся и утекает пользователю как есть, например "*(смех)*" в конце ответа.
    match = re.search(r'\*?\(([^)]+)\)\*?\s*$', text)
    if not match:
        return None, text
    reaction_key = match.group(1).strip().lower()
    reaction_map = {
        "смех": "😂", "laughter": "😂", "laugh": "😂",
        "радость": "😊", "joy": "😊", "happiness": "😊", "happy": "😊",
        "любовь": "❤️", "love": "❤️",
        "удивление": "😮", "surprise": "😮", "surprised": "😮",
        "грусть": "😔", "sadness": "😔", "sad": "😔",
        "злость": "😡", "anger": "😡", "angry": "😡",
        "поддержка": "👍", "support": "👍",
        "интрига": "😏", "intrigue": "😏",
        "флирт": "😉", "flirt": "😉", "flirting": "😉",
        "приветствие": "👋", "greeting": "👋", "hello": "👋",
        "вопрос": "🤔", "question": "🤔",
    }
    # Тег вырезаем из видимого текста ВСЕГДА, а не только когда слово узнано — иначе, стоит
    # модели написать тег не строго по списку (например "(flirt)" вместо "(флирт)", хотя
    # промпт явно требует русское слово), он утекает пользователю как есть. Без эмодзи-реакции
    # в этом случае просто обойдёмся — это не критично, а утечка текста в чат критична.
    clean_text = text[:match.start()].rstrip()
    reaction = reaction_map.get(reaction_key)
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
        response = await asyncio.to_thread(
            call_ai, AI_MODEL, "ai",
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

    if reaction and get_subscription_level(user) in ("super_pro", "elite"):
        try:
            await bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[{"type": "emoji", "emoji": reaction}]
            )
        except Exception:
            pass

    user["last_activity"] = datetime.now().isoformat()
    apply_activity_stat_cost(user, ENERGY_COST_MESSAGE, SATIETY_COST_MESSAGE, WATER_COST_MESSAGE)
    save_data(user_data)
    await maybe_send_feed_nudge(message.chat.id, user)
    await maybe_send_energy_nudge(message.chat.id, user)


async def _keep_typing(chat_id):
    try:
        while True:
            await bot.send_chat_action(chat_id, "typing")
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass


def build_shop_reaction_instruction(item, kind, note=None):
    """kind: "food" или "gift". Даёт модели конкретный повод и эмоциональный ориентир
    (reaction_hint), чтобы благодарность не была одинаковым шаблоном для всех предметов —
    снек и романтический вечер должны звучать по-разному. note — личные слова пользователя
    (см. generate_shop_reaction) — если есть, модель обязана ответить именно на них."""
    hint = item.get("reaction_hint", "")
    verb = "покормил(а)" if kind == "food" else ("вылечил(а)" if kind == "medicine" else "подарил(а)")
    preposition = "тебя" if kind == "food" else "тебе"
    thing = item["ru"].lower()
    note_rule = (f" При этом он(а) сказал(а) тебе: «{note}» — обязательно отреагируй именно на "
                 f"эти слова, а не только на сам подарок." if note else "")
    return (
        f"\n\nСобеседник только что {verb} {preposition}: «{thing}».{note_rule} {hint} Отреагируй и "
        f"поблагодари в характере — коротко (1-2 реплики), не шаблонно, с реакцией именно на ЭТО, "
        f"а не общими словами благодарности, которые подошли бы к любому подарку."
    )


async def generate_shop_reaction(chat_id, user, item, kind, note=None):
    """Просит ИИ отреагировать и поблагодарить в характере за конкретную еду/подарок —
    полноценная реплика персонажа через build_prompt(user), а не статичный текст,
    и разная в зависимости от того, что именно куплено (см. reaction_hint у предмета).
    note — необязательные личные слова, сказанные пользователем вместе с покупкой (см.
    writing_item_note в handle_message) — попадают и в системный промпт, и прямой речью в
    синтетическую реплику ниже, чтобы ИИ реагировал на них, а не только на сам факт подарка."""
    system_prompt = build_prompt(user) + build_shop_reaction_instruction(item, kind, note=note)
    action_word = "кормит" if kind == "food" else ("лечит" if kind == "medicine" else "дарит")
    preposition = "тебя" if kind == "food" else "тебе"
    action_text = f"*{action_word} {preposition}: {item['ru'].lower()}*"
    if note:
        action_text += f" {note}"
    history_tail = user["history"][-6:]

    typing_task = asyncio.create_task(_keep_typing(chat_id))
    try:
        response = await asyncio.to_thread(
            call_ai, AI_MODEL, "ai",
            messages=[{"role": "system", "content": system_prompt}] + history_tail +
                     [{"role": "user", "content": action_text}],
            temperature=0.9,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
    except Exception:
        # Покупка уже прошла и подтверждена статичным текстом выше — если ИИ недоступен,
        # просто тихо пропускаем бонусную реакцию, не показывая пользователю ошибку.
        return
    finally:
        typing_task.cancel()

    _, clean_answer = extract_reaction_from_answer(answer)
    user["history"].append({"role": "user", "content": action_text})
    user["history"].append({"role": "assistant", "content": clean_answer})
    limit = get_history_limit(user)
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    save_data(user_data)
    await send_long_to_chat(chat_id, clean_answer)


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
        # Сбрасываем историю — иначе при ПЕРЕсоздании персонажа старые реплики ("я Бэтмен")
        # остаются в контексте и перевешивают новую личность, которая только что была задана.
        user["history"] = []
        save_data(user_data)
        await message.answer(get_text(user, "character_created", text=message.text))
        return

    # 1b. Свой подарок — свободный текст вместо каталога (аксессуары конечны и одноразовые).
    # Настроение случайное (не среднее): пользователь сам так предложил, с рандомом приятнее.
    if user.get("writing_custom_gift"):
        # Гасим флаг сразу, а не только при успехе: раньше он оставался True при любой
        # неудаче (не хватило баксов/дубликат/невалидный текст), и следующее сообщение
        # пользователя — даже обычная реплика собеседнику — снова ловилось этой же веткой
        # без возможности выйти. Один заход = одна попытка; хочешь ещё раз — жми кнопку в магазине.
        user["writing_custom_gift"] = False
        save_data(user_data)
        gift_text = message.text.strip()
        if not gift_text or len(gift_text) > CUSTOM_GIFT_MAX_LEN:
            await message.answer(get_text(user, "custom_gift_invalid", n=CUSTOM_GIFT_MAX_LEN))
            return
        normalized = gift_text.lower()
        if normalized in user.get("custom_gifts_given", []):
            await message.answer(get_text(user, "custom_gift_duplicate"))
            return
        if not spend_bucks(user, CUSTOM_GIFT_PRICE):
            await message.answer(get_text(user, "not_enough_bucks", n=CUSTOM_GIFT_PRICE - user.get("bucks", 0)))
            return
        mood = random.randint(*CUSTOM_GIFT_MOOD_RANGE)
        xp = round(mood * 0.6)
        custom_item = {
            "ru": gift_text, "en": gift_text, "de": gift_text, "emoji": "🎁", "mood": mood, "xp": xp,
            "reaction_hint": ("Это подарок, который собеседник придумал сам, специально для тебя — не "
                              "что-то из готового списка. Благодарность самая искренняя и трогательная "
                              "из всех: чувствуется, что он(а) думал(а) именно о тебе."),
        }
        apply_shop_item_effects(user, custom_item)
        user.setdefault("custom_gifts_given", []).append(normalized)
        save_data(user_data)
        await grant_gift_xp(message.chat.id, user, xp)
        await message.answer(get_text(user, "item_bought", effects=format_item_effects(custom_item, user)))
        if not is_asleep(user):
            await generate_shop_reaction(message.chat.id, user, custom_item, "gift")
        return

    # 1c. Личная подпись к обычному (каталожному) подарку/еде — запущена кнопкой ✍️ рядом с
    # предметом (см. shop_item_note_start). В отличие от writing_custom_gift это НЕ отдельный
    # предмет: cooldown/баксы уже проверены при нажатии кнопки, но перепроверяем на всякий
    # случай — между нажатием и вводом текста могло пройти время (или он успел купить то же
    # самое где-то ещё).
    if user.get("writing_item_note"):
        note_state = user["writing_item_note"]
        user["writing_item_note"] = None
        save_data(user_data)
        category = note_state.get("category")
        key = note_state.get("key")
        item = (GIFT_ITEMS if category == "gift" else FOOD_ITEMS).get(key) if category else None
        if not item:
            return
        note_text = message.text.strip()
        if not note_text or len(note_text) > ITEM_NOTE_MAX_LEN:
            await message.answer(get_text(user, "item_note_invalid", n=ITEM_NOTE_MAX_LEN))
            return
        ready_at = item_ready_at(user, category, key, item)
        if ready_at:
            await message.answer(get_text(user, "item_cooldown_alert", when=cooldown_phrase(user, ready_at)))
            return
        if category == "food" and overfeed_would_refuse(user, item):
            await message.answer(get_text(user, "overfeed_refuse_alert"))
            return
        if not spend_bucks(user, item["price"]):
            await message.answer(get_text(user, "not_enough_bucks", n=item["price"] - user.get("bucks", 0)))
            return
        await execute_item_purchase(message.chat.id, user, category, key, item, note=note_text)
        return

    # 2. Приветствие после долгого отсутствия — но не если персонаж спит: иначе следом всё
    # равно покажется asleep_message (шаг 4b), и получать оба сообщения подряд ("наконец-то!"
    # + "он спит") нелепо и противоречиво (баг из фидбэка).
    if user.get("last_activity") and not is_asleep(user) and not user.get("dead"):
        try:
            last = datetime.fromisoformat(user["last_activity"])
            if (datetime.now() - last).days >= 1:
                gender = user.get("gender", "female")
                version = random.choice([1, 2])
                key = f"welcome_back_{gender}" if version == 1 else f"welcome_back_{gender}_2"
                # last_activity обновляем СРАЗУ и ДО await — иначе, если пользователь успевает
                # прислать второе сообщение, пока первое ещё ждёт ответа ИИ (last_activity
                # обновляется только после него, в generate_and_reply), второй обработчик видит
                # тот же старый last_activity и шлёт это же приветствие повторно.
                user["last_activity"] = datetime.now().isoformat()
                save_data(user_data)
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

    # 3b. Персонаж умер (перекорм/перепой, см. kill_character) — блокируем вообще всё, включая
    # кнопки навигации ниже: выйти можно только с экрана смерти (дефибриллятор или новый
    # персонаж), поэтому проверка стоит ДО игнора команд/кнопок, а не после.
    if user.get("dead"):
        await message.answer(get_text(user, "character_died"), reply_markup=get_death_kb(user))
        return

    # 4. Игнорируем команды и кнопки клавиатуры
    if message.text.startswith("/"):
        return
    for key in ("main_menu", "my_profile", "our_channel", "spin_wheel", "edit"):
        if is_button(message.text, key):
            return

    # 4b. Собеседник может "уснуть", если кончилась энергия — тогда обычный ИИ-ответ
    # не генерируем (экономит и токены, и веру в механику), а кнопки навигации выше уже
    # обработаны и по-прежнему работают, чтобы можно было зайти в профиль и разбудить/покормить.
    if is_asleep(user):
        await message.answer(get_text(user, "asleep_message", price=PRODUCTS["wake_now"]["stars"]), reply_markup=get_wake_kb(user))
        return

    # 4c. Персонаж на работе (см. /work) — обычный чат недоступен, пока не вернётся. Если время
    # уже вышло, это же сообщение и завершает работу (начисляет баксы) и обрабатывается дальше
    # как обычно — не нужно присылать что-то ещё раз, чтобы "заметить" возвращение.
    if user.get("working_until"):
        if finish_work_if_done(user):
            await message.answer(get_text(user, "work_finished", bucks=WORK_PAYOUT_BUCKS))
        else:
            await message.answer(get_text(user, "still_working"))
            return

    # 5. Режим редактирования последнего сообщения
    if user.get("editing_message"):
        user["editing_message"] = False
        trim_history_to_last_user_message(user)
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

    # 7. Негатив / XP / настроение
    negative = contains_negative(message.text)
    sub_level = get_subscription_level(user)
    multiplier = XP_MULTIPLIER.get(sub_level, 1.0)

    if negative:
        user["negative_count"] = user.get("negative_count", 0) + 1
        if user["negative_count"] >= 5:
            user["xp"] = max(0, user.get("xp", 0) - 50)
            user["mood"] = max(-MOOD_MAX, user.get("mood", 0) - 30)
            user["negative_count"] = 0
            save_data(user_data)
            await message.answer(get_text(user, "quarrel"), reply_markup=get_full_kb(user))
            user["history"].append({"role": "assistant", "content": "💢 Ссора!"})
            save_data(user_data)
            return
        xp_change, mood_change = -10, -10
    else:
        xp_change = int(3 * multiplier + 0.5)
        mood_change = 0  # настроение больше не растёт от самой переписки — только от подарков
                          # (см. apply_shop_item_effects); тут оно может только падать
        user["negative_count"] = max(0, user.get("negative_count", 0) - 1)

    user["xp"] = max(0, user.get("xp", 0) + xp_change)
    user["mood"] = min(MOOD_MAX, max(-MOOD_MAX, user.get("mood", 0) + mood_change))

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
    if get_subscription_level(user) in ("super_pro", "elite"):
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
#  TELEGRAM MINI APP (веб-магазин) — см. WEBAPP_URL в начале файла.
# ============================================================
# Полностью отдельная надстройка поверх уже существующего инлайн-магазина: сам магазин
# (execute_item_purchase/buy_food/buy_gift/buy_medicine/FOOD_ITEMS/GIFT_ITEMS/MEDICINE_ITEMS)
# не меняется ни на строчку — здесь только новый способ до него достучаться, с теми же
# правилами. Если WEBAPP_URL не задан, ничего из этого раздела даже не запускается
# (см. run_webapp_server/main), кнопка "Магазин" остаётся прежней.


def validate_webapp_init_data(init_data, max_age_seconds=86400):
    """Проверяет подпись initData, которую Mini App кладёт в каждый запрос к нам — официальный
    алгоритм Telegram (core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app):
    secret_key = HMAC_SHA256(key="WebAppData", msg=BOT_TOKEN), затем сверяем присланный hash с
    HMAC_SHA256(key=secret_key, msg=data_check_string). Без этой проверки на сервере нет иного
    способа узнать, кто на самом деле стоит за запросом — страница открывается по обычной
    публичной ссылке. Возвращает распарсенный dict (поле "user" уже как dict, не JSON-строка)
    при успехе, иначе None."""
    if not init_data:
        return None
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed_hash, received_hash):
        return None
    try:
        auth_date = int(parsed.get("auth_date", 0))
    except (TypeError, ValueError):
        return None
    if auth_date <= 0 or (datetime.now().timestamp() - auth_date) > max_age_seconds:
        return None
    try:
        parsed["user"] = json.loads(parsed["user"])
    except (KeyError, json.JSONDecodeError, TypeError):
        return None
    return parsed


def resolve_webapp_user(init_data):
    """Общий шлюз для обоих API-хендлеров ниже: проверяет подпись, затем применяет те же
    ворота, что и обычный чат (техработы, не подтверждён/нет персонажа, мёртв — см.
    handle_message). Возвращает (user_id, user, None) при успехе, иначе (None, None, error-dict)."""
    parsed = validate_webapp_init_data(init_data)
    if not parsed:
        return None, None, {"ok": False, "error": "auth", "message": "Invalid Telegram signature"}
    tg_user = parsed.get("user") or {}
    user_id = tg_user.get("id")
    if not user_id:
        return None, None, {"ok": False, "error": "auth", "message": "Missing user id"}
    user_id = int(user_id)
    user = get_user(user_id)
    if maintenance_mode and user_id not in ADMIN_IDS:
        return None, None, {"ok": False, "error": "maintenance", "message": get_text(user, "maintenance")}
    if not (user["verified"] and user["agreement_accepted"] and user["personality_ready"]):
        return None, None, {"ok": False, "error": "not_ready", "message": get_text(user, "webapp_character_not_ready")}
    if user.get("dead"):
        return None, None, {"ok": False, "error": "dead", "message": get_text(user, "character_died")}
    return user_id, user, None


def serialize_shop_state(user):
    """Полный снимок магазина + статов персонажа для Mini App — JSON-сериализуемый dict.
    Названия/эффекты уже локализованы под user["lang"] (та же логика, что и в get_shop_kb),
    фронтенду не нужна своя i18n-логика для содержимого каталога."""
    lang = user.get("lang", "ru")

    def serialize_item(mapping, key, is_gift):
        base_item = mapping[key]
        item = gift_effective_item(base_item, user) if is_gift else base_item
        category = "gift" if is_gift else "food"
        ready_at = item_ready_at(user, category, key, base_item)
        return {
            "key": key,
            "category": category,
            "emoji": item["emoji"],
            "name": item.get(lang, item["ru"]),
            "price": item["price"],
            "effects": format_item_effects(item, user),
            "ready_in": cooldown_phrase(user, ready_at) if ready_at else None,
            "refuse": (not is_gift) and overfeed_would_refuse(user, base_item),
        }

    categories = []
    for shop_category in SHOP_CATEGORY_ORDER:
        items = [serialize_item(FOOD_ITEMS, key, False)
                 for key, it in FOOD_ITEMS.items() if it.get("category") == shop_category]
        items += [serialize_item(GIFT_ITEMS, key, True)
                  for key, it in GIFT_ITEMS.items() if it.get("category") == shop_category]
        if items:
            categories.append({"key": shop_category, "name": get_text(user, SHOP_CATEGORY_TEXT_KEY[shop_category]), "items": items})

    medicine = []
    if user.get("illness"):
        for key, item in MEDICINE_ITEMS.items():
            medicine.append({
                "key": key, "emoji": item["emoji"], "name": item.get(lang, item["ru"]),
                "price": item["price"], "cures": sorted(item["cures"]),
            })

    illness_label = None
    if user.get("illness"):
        info = ILLNESSES[user["illness"]]
        illness_label = f"{info['emoji']} {info.get(lang, info['ru'])}"

    return {
        "lang": lang,
        "bucks": user.get("bucks", 0),
        "energy": int(round(user.get("energy", ENERGY_MAX))),
        "energy_max": ENERGY_MAX,
        "satiety": int(round(user.get("satiety", SATIETY_MAX))),
        "satiety_max": SATIETY_MAX,
        "water": int(round(user.get("water", WATER_MAX))),
        "water_max": WATER_MAX,
        "mood_emoji": mood_emoji(user.get("mood", 0)),
        "mood_value": int(round(user.get("mood", 0))),
        "illness": illness_label,
        "asleep": is_asleep(user),
        "categories": categories,
        "medicine": medicine,
        "note_max_len": ITEM_NOTE_MAX_LEN,
        "ui": {k: get_text(user, k) for k in (
            "webapp_title", "webapp_buy_btn", "webapp_note_placeholder", "webapp_refuse_badge",
            "webapp_bought_toast", "webapp_open_chat_hint", "webapp_loading", "shop_category_medicine",
        )},
    }


async def perform_webapp_purchase(user, user_id, category, key, note=None):
    """Та же последовательность проверок, что в buy_food/buy_gift/buy_medicine и в
    writing_item_note-ветке handle_message — просто вызывается из API, а не из
    callback-хендлера. Содержательная логика по-прежнему только в execute_item_purchase."""
    catalog = {"food": FOOD_ITEMS, "gift": GIFT_ITEMS, "medicine": MEDICINE_ITEMS}.get(category)
    item = catalog.get(key) if catalog else None
    if not item:
        return {"ok": False, "error": "Not found"}

    if category == "medicine":
        illness = user.get("illness")
        if not illness:
            return {"ok": False, "error": get_text(user, "not_sick_alert")}
        if illness not in item["cures"]:
            return {"ok": False, "error": get_text(user, "wrong_medicine_alert")}
    else:
        ready_at = item_ready_at(user, category, key, item)
        if ready_at:
            return {"ok": False, "error": get_text(user, "item_cooldown_alert", when=cooldown_phrase(user, ready_at))}
        if category == "food" and overfeed_would_refuse(user, item):
            return {"ok": False, "error": get_text(user, "overfeed_refuse_alert")}

    if note is not None:
        note = note.strip() or None
        if note and len(note) > ITEM_NOTE_MAX_LEN:
            return {"ok": False, "error": get_text(user, "item_note_invalid", n=ITEM_NOTE_MAX_LEN)}

    if not spend_bucks(user, item["price"]):
        return {"ok": False, "error": get_text(user, "not_enough_bucks", n=item["price"] - user.get("bucks", 0))}

    await execute_item_purchase(user_id, user, category, key, item, note=note)
    return {"ok": True}


# Статичная HTML/CSS/JS-страница Mini App — персонализация (язык, статы, каталог) целиком
# на фронтенде через /api/state и /api/buy: initData Telegram кладёт во фрагмент URL (#...),
# который браузер никогда не отправляет на сервер, так что сама страница не может быть
# отрендерена под конкретного пользователя на этапе GET /shop.
SHOP_PAGE_HTML = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Shop</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  html, body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--tg-theme-bg-color, #ffffff);
    color: var(--tg-theme-text-color, #111111);
  }
  body { padding-bottom: 24px; }
  #stats {
    position: sticky;
    top: 0;
    z-index: 5;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 10px 14px;
    background: var(--tg-theme-secondary-bg-color, #f2f2f2);
    border-bottom: 1px solid rgba(127,127,127,.2);
    font-size: 14px;
    font-weight: 600;
  }
  #illness-badge {
    display: none;
    padding: 8px 14px 0;
    font-size: 13px;
    color: #cf5b5b;
  }
  #tabs {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding: 10px 14px 4px;
    -webkit-overflow-scrolling: touch;
  }
  .tab {
    flex: 0 0 auto;
    padding: 7px 14px;
    border-radius: 999px;
    background: var(--tg-theme-secondary-bg-color, #eee);
    color: var(--tg-theme-text-color, #111);
    font-size: 13px;
    font-weight: 600;
    border: none;
  }
  .tab.active {
    background: var(--tg-theme-button-color, #2481cc);
    color: var(--tg-theme-button-text-color, #ffffff);
  }
  #items {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
    padding: 10px 14px 20px;
  }
  .card {
    border: 1px solid rgba(127,127,127,.25);
    border-radius: 14px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .card-top { display: flex; align-items: center; justify-content: space-between; }
  .card-emoji { font-size: 26px; }
  .note-toggle {
    font-size: 15px;
    background: none;
    border: none;
    padding: 4px;
    opacity: .55;
  }
  .card-name { font-size: 14px; font-weight: 600; line-height: 1.25; }
  .card-effects { font-size: 12px; color: var(--tg-theme-hint-color, #888); min-height: 14px; }
  .card-note {
    width: 100%;
    box-sizing: border-box;
    font-size: 12px;
    padding: 6px 8px;
    border-radius: 8px;
    border: 1px solid rgba(127,127,127,.3);
    background: var(--tg-theme-bg-color, #fff);
    color: inherit;
    display: none;
  }
  .card-note.shown { display: block; }
  .card-footer {
    margin-top: auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
  }
  .price { font-size: 13px; font-weight: 700; }
  .buy-btn {
    border: none;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: 700;
    background: var(--tg-theme-button-color, #2481cc);
    color: var(--tg-theme-button-text-color, #ffffff);
  }
  .buy-btn:disabled { opacity: .45; }
  .badge {
    font-size: 11px;
    font-weight: 600;
    padding: 5px 8px;
    border-radius: 8px;
    background: rgba(127,127,127,.18);
    color: var(--tg-theme-hint-color, #888);
  }
  #footer-hint {
    text-align: center;
    font-size: 12px;
    color: var(--tg-theme-hint-color, #888);
    padding: 8px 14px 20px;
  }
  #full-screen-msg {
    display: none;
    padding: 60px 24px;
    text-align: center;
    font-size: 15px;
    line-height: 1.5;
  }
</style>
</head>
<body>
  <div id="stats"></div>
  <div id="illness-badge"></div>
  <div id="tabs"></div>
  <div id="items">Loading…</div>
  <div id="footer-hint"></div>
  <div id="full-screen-msg"></div>

<script>
(function () {
  var tg = (window.Telegram && window.Telegram.WebApp) || null;
  function safe(fn) { try { fn(); } catch (e) { /* older Telegram client: ignore */ } }
  if (tg) { safe(function () { tg.ready(); }); safe(function () { tg.expand(); }); }

  var state = null;
  var activeTab = null;
  var busyKeys = {};

  function initData() { return tg ? tg.initData : ""; }

  function api(path, opts) {
    opts = opts || {};
    opts.headers = Object.assign({"X-Telegram-Init-Data": initData()}, opts.headers || {});
    return fetch(path, opts).then(function (r) { return r.json(); });
  }

  function showFullScreen(text) {
    ["stats", "illness-badge", "tabs", "items", "footer-hint"].forEach(function (id) {
      document.getElementById(id).style.display = "none";
    });
    var el = document.getElementById("full-screen-msg");
    el.style.display = "block";
    el.textContent = text;
  }

  function renderStats(s) {
    var el = document.getElementById("stats");
    el.innerHTML = "";
    [
      "💵 " + s.bucks,
      "⚡ " + s.energy + "/" + s.energy_max,
      "🍽 " + s.satiety + "/" + s.satiety_max,
      "💧 " + s.water + "/" + s.water_max,
      s.mood_emoji + " " + (s.mood_value > 0 ? "+" : "") + s.mood_value
    ].forEach(function (p) {
      var span = document.createElement("span");
      span.textContent = p;
      el.appendChild(span);
    });
    var badge = document.getElementById("illness-badge");
    if (s.illness) { badge.textContent = s.illness; badge.style.display = "block"; }
    else { badge.style.display = "none"; }
  }

  function categoryList(s) {
    var list = s.categories.map(function (c) { return {key: c.key, name: c.name, items: c.items}; });
    if (s.medicine && s.medicine.length) {
      list.unshift({
        key: "medicine",
        name: s.ui.shop_category_medicine,
        items: s.medicine.map(function (m) {
          return {key: m.key, category: "medicine", emoji: m.emoji, name: m.name, price: m.price,
                  effects: "", ready_in: null, refuse: false};
        })
      });
    }
    return list;
  }

  function renderTabs(s) {
    var cats = categoryList(s);
    if (!activeTab || !cats.some(function (c) { return c.key === activeTab; })) {
      activeTab = cats.length ? cats[0].key : null;
    }
    var el = document.getElementById("tabs");
    el.innerHTML = "";
    cats.forEach(function (c) {
      var btn = document.createElement("button");
      btn.className = "tab" + (c.key === activeTab ? " active" : "");
      btn.textContent = c.name;
      btn.onclick = function () { activeTab = c.key; render(); };
      el.appendChild(btn);
    });
  }

  function makeCard(s, item) {
    var card = document.createElement("div");
    card.className = "card";

    var top = document.createElement("div");
    top.className = "card-top";
    var emoji = document.createElement("div");
    emoji.className = "card-emoji";
    emoji.textContent = item.emoji;
    top.appendChild(emoji);

    var noteBox = null;
    if (item.category !== "medicine") {
      var toggle = document.createElement("button");
      toggle.className = "note-toggle";
      toggle.textContent = "✍️";
      noteBox = document.createElement("input");
      noteBox.className = "card-note";
      noteBox.type = "text";
      noteBox.placeholder = s.ui.webapp_note_placeholder;
      noteBox.maxLength = s.note_max_len;
      toggle.onclick = function () {
        noteBox.classList.toggle("shown");
        if (noteBox.classList.contains("shown")) noteBox.focus();
      };
      top.appendChild(toggle);
    }
    card.appendChild(top);

    var name = document.createElement("div");
    name.className = "card-name";
    name.textContent = item.name;
    card.appendChild(name);

    var effects = document.createElement("div");
    effects.className = "card-effects";
    effects.textContent = item.effects || "";
    card.appendChild(effects);

    if (noteBox) card.appendChild(noteBox);

    var footer = document.createElement("div");
    footer.className = "card-footer";
    var itemKey = item.category + ":" + item.key;

    if (item.ready_in) {
      var badge = document.createElement("span");
      badge.className = "badge";
      badge.textContent = "⏳ " + item.ready_in;
      footer.appendChild(badge);
    } else if (item.refuse) {
      var rbadge = document.createElement("span");
      rbadge.className = "badge";
      rbadge.textContent = "🙅 " + s.ui.webapp_refuse_badge;
      footer.appendChild(rbadge);
    } else {
      var price = document.createElement("span");
      price.className = "price";
      price.textContent = item.price + "💵";
      footer.appendChild(price);

      var buyBtn = document.createElement("button");
      buyBtn.className = "buy-btn";
      buyBtn.textContent = s.ui.webapp_buy_btn;
      if (busyKeys[itemKey]) buyBtn.disabled = true;
      buyBtn.onclick = function () { buy(item.category, item.key, noteBox ? noteBox.value : ""); };
      footer.appendChild(buyBtn);
    }
    card.appendChild(footer);
    return card;
  }

  function renderItems(s) {
    var cats = categoryList(s);
    var current = cats.filter(function (c) { return c.key === activeTab; })[0];
    var el = document.getElementById("items");
    el.innerHTML = "";
    if (!current) return;
    current.items.forEach(function (item) { el.appendChild(makeCard(s, item)); });
  }

  function render() {
    if (!state) return;
    renderStats(state);
    renderTabs(state);
    renderItems(state);
    document.getElementById("footer-hint").textContent = state.ui.webapp_open_chat_hint;
  }

  function buy(category, key, note) {
    var itemKey = category + ":" + key;
    busyKeys[itemKey] = true;
    render();
    api("/api/buy", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({category: category, key: key, note: note || null})
    }).then(function (res) {
      delete busyKeys[itemKey];
      if (res.state) state = res.state;
      if (res.ok) {
        safe(function () { tg.HapticFeedback.notificationOccurred("success"); });
        safe(function () { tg.showPopup({message: state.ui.webapp_bought_toast}); });
      } else {
        safe(function () { tg.HapticFeedback.notificationOccurred("error"); });
        safe(function () { tg.showAlert(res.error || res.message || "Error"); });
      }
      render();
    }).catch(function () {
      delete busyKeys[itemKey];
      render();
    });
  }

  function load() {
    api("/api/state").then(function (res) {
      if (!res.ok) { showFullScreen(res.message || res.error || "Error"); return; }
      state = res.state;
      render();
    }).catch(function () { showFullScreen("Network error"); });
  }

  load();
})();
</script>
</body>
</html>
'''


async def shop_page_handler(request):
    return web.Response(text=SHOP_PAGE_HTML, content_type="text/html")


async def api_state_handler(request):
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    user_id, user, error = resolve_webapp_user(init_data)
    if error:
        return web.json_response(error, status=401 if error["error"] == "auth" else 200)
    return web.json_response({"ok": True, "state": serialize_shop_state(user)})


async def api_buy_handler(request):
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    user_id, user, error = resolve_webapp_user(init_data)
    if error:
        return web.json_response(error, status=401 if error["error"] == "auth" else 200)
    try:
        body = await request.json()
    except (json.JSONDecodeError, ValueError):
        return web.json_response({"ok": False, "error": "Bad request"}, status=400)
    category = body.get("category")
    key = body.get("key")
    note = body.get("note")
    if not isinstance(category, str) or not isinstance(key, str):
        return web.json_response({"ok": False, "error": "Bad request"}, status=400)
    if note is not None and not isinstance(note, str):
        note = None
    result = await perform_webapp_purchase(user, user_id, category, key, note=note)
    result["state"] = serialize_shop_state(user)
    return web.json_response(result)


async def root_health_handler(request):
    """Корень домена — не часть самого магазина, но некоторые хостинги (в т.ч. reverse-proxy
    перед контейнером) проверяют живость сервиса именно запросом на "/" перед тем, как вообще
    начать пускать трафик на остальные пути; без этого маршрута такая проверка ловила бы 404 от
    aiohttp и могла бы блокировать доступ даже к /shop. Заодно отдаёт человеку, который открыл
    голый домен в браузере, что-то осмысленное вместо пустого 404."""
    return web.Response(
        text='<!doctype html><meta http-equiv="refresh" content="0; url=/shop">OK',
        content_type="text/html",
    )


async def run_webapp_server():
    app_web = web.Application()
    app_web.router.add_get("/", root_health_handler)
    app_web.router.add_get("/shop", shop_page_handler)
    app_web.router.add_get("/api/state", api_state_handler)
    app_web.router.add_post("/api/buy", api_buy_handler)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBAPP_PORT)
    await site.start()
    logging.info(f"🛍 Mini App слушает на 0.0.0.0:{WEBAPP_PORT}, публичный адрес: {WEBAPP_URL}/shop")
    while True:
        await asyncio.sleep(3600)


# ============================================================
#  УВЕДОМЛЕНИЯ (ЕЖЕДНЕВНЫЕ И "СКУЧАЮ")
# ============================================================
MISS_YOU_INACTIVITY_DAYS = 2  # с какого дня без сообщений начинаем напоминать
MISS_YOU_INTERVAL_DAYS = 2  # не чаще чем раз в столько дней после предыдущего напоминания
SLEEP_REMINDER_INTERVAL_HOURS = 12  # раз в сколько часов мягко напоминаем, что персонаж всё ещё спит
SPIN_REMINDER_INTERVAL_DAYS = 1  # раз в сколько дней мягко напоминаем про доступный бесплатный прокрут
THIRST_REMINDER_WATER_THRESHOLD = 20  # тот же порог, что у "сильной жажды" в build_thirst_rule
THIRST_REMINDER_INTERVAL_HOURS = 4  # вода расходуется быстрее сытости (пассивно до нуля примерно
                                      # за 2 часа бездействия — см. WATER_INACTIVITY_DECAY_MINUTES),
                                      # поэтому и напоминание о ней чаще, чем про голод
HUNGER_REMINDER_INTERVAL_HOURS = 6  # порог сытости берём тот же, что у контекстной подсказки прямо
                                      # в чате — FEED_NUDGE_SATIETY_THRESHOLD (см. maybe_send_feed_nudge)


async def check_notifications():
    while True:
        try:
            now = datetime.now()
            today = now.date().isoformat()
            for user_id, user in list(user_data.items()):
                if not user.get("verified") or not user.get("personality_ready"):
                    continue
                # Мёртвому персонажу не шлём обычные напоминания (скучаю/спин/сон) — это
                # тонально дико, пока экран смерти не закрыт дефибриллятором или новым
                # персонажем; отдельного "напоминания о смерти" пока нет, не нужно плодить типы.
                if user.get("dead"):
                    continue

                # Обезвоживание должно тикать и потенциально убивать ФОНОВО, а не только у тех,
                # кто сам сейчас пишет боту: иначе у молча пропавшего пользователя сохранённое
                # значение воды никогда не дошло бы до нуля (пассивный расход иначе считается
                # лениво, только при следующем get_user()), water_zero_since никогда бы не
                # выставился, и смерть от обезвоживания никогда бы не сработала в фоне. Делаем
                # это ДО проверки notifications_muted ниже — смерть не должна становиться
                # отключаемой вместе с обычными напоминаниями.
                apply_passive_satiety_decay(user)
                water_zero_since = user.get("water_zero_since")
                if water_zero_since:
                    try:
                        hours_dry = (now - datetime.fromisoformat(water_zero_since)).total_seconds() / 3600
                    except (ValueError, TypeError):
                        hours_dry = 0
                    if hours_dry >= DEHYDRATION_DEATH_HOURS:
                        await kill_character(int(user_id), user, cause="dehydration")
                        continue

                # Отключение уведомлений — привилегия SUPER PRO: если подписка упала до PRO или
                # истекла, напоминания сами возобновятся — отдельно снимать флаг не нужно.
                if user.get("notifications_muted") and get_subscription_level(user) in ("super_pro", "elite"):
                    continue

                # 1) "Скучаю" — для давно пропавших. Если это условие сработало, ниже больше
                # ничего не шлём в этом же тике: человеку и так возвращаемся отдельным
                # сообщением, второе уведомление сразу следом было бы уже спамом.
                last_activity_raw = user.get("last_activity")
                last_activity = None
                if last_activity_raw:
                    try:
                        last_activity = datetime.fromisoformat(last_activity_raw)
                    except Exception:
                        last_activity = None

                if last_activity and (now - last_activity).days >= MISS_YOU_INACTIVITY_DAYS:
                    last_reminder = user.get("last_reminder")
                    due = True
                    if last_reminder:
                        try:
                            due = (now - datetime.fromisoformat(last_reminder)).days >= MISS_YOU_INTERVAL_DAYS
                        except Exception:
                            due = True
                    if due:
                        user["last_reminder"] = today
                        save_data(user_data)
                        try:
                            gender = user.get("gender", "female")
                            await bot.send_message(int(user_id), random.choice(get_text(user, f"miss_you_{gender}")))
                        except Exception:
                            pass
                    continue

                # 2) Персонаж всё ещё спит — лёгкое проактивное напоминание, отдельное от
                # жёсткого asleep_message (который показывается только в ответ на попытку
                # написать спящему персонажу). Отсчёт идёт от момента засыпания, а не от
                # первой проверки, — чтобы не дёргать человека через 5 минут после того, как
                # энергия дошла до нуля.
                if is_asleep(user):
                    baseline = user.get("last_sleep_reminder") or user.get("sleep_until")
                    due = True
                    if baseline:
                        try:
                            hours_since = (now - datetime.fromisoformat(baseline)).total_seconds() / 3600
                            due = hours_since >= SLEEP_REMINDER_INTERVAL_HOURS
                        except Exception:
                            due = True
                    if due:
                        user["last_sleep_reminder"] = now.isoformat()
                        save_data(user_data)
                        try:
                            await bot.send_message(int(user_id), get_text(user, "sleep_daily_reminder"),
                                                   reply_markup=get_wake_kb(user))
                        except Exception:
                            pass
                    continue

                # 3) Доступен бесплатный прокрут колеса — не чаще раза в сутки и только пока
                # он реально не использован.
                if free_spins_left(user) > 0:
                    last_spin_reminder = user.get("last_spin_reminder")
                    due = True
                    if last_spin_reminder:
                        try:
                            due = (now - datetime.fromisoformat(last_spin_reminder)).days >= SPIN_REMINDER_INTERVAL_DAYS
                        except Exception:
                            due = True
                    if due:
                        user["last_spin_reminder"] = today
                        save_data(user_data)
                        try:
                            kb = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text=get_text(user, "spin_wheel"),
                                                      callback_data="spin_free", style="success")]
                            ])
                            await bot.send_message(int(user_id), get_text(user, "spin_daily_reminder"), reply_markup=kb)
                        except Exception:
                            pass
                    continue

                # 4) Низкий уровень воды — жажда тратится быстрее голода, поэтому и напоминание
                # чаще (см. THIRST_REMINDER_INTERVAL_HOURS). Отсчёт cooldown — от последнего
                # такого напоминания, а не от water_zero_since: иначе после первого сообщения
                # напоминания сразу посыпались бы одно за другим.
                if user.get("water", WATER_MAX) <= THIRST_REMINDER_WATER_THRESHOLD:
                    last_thirst_reminder = user.get("last_thirst_reminder")
                    due = True
                    if last_thirst_reminder:
                        try:
                            hours_since = (now - datetime.fromisoformat(last_thirst_reminder)).total_seconds() / 3600
                            due = hours_since >= THIRST_REMINDER_INTERVAL_HOURS
                        except Exception:
                            due = True
                    if due:
                        user["last_thirst_reminder"] = now.isoformat()
                        save_data(user_data)
                        try:
                            await bot.send_message(int(user_id), get_text(user, "thirsty_reminder"),
                                                   reply_markup=get_feed_nudge_kb(user))
                        except Exception:
                            pass
                    continue

                # 5) Низкая сытость — тот же порог, что у контекстной подсказки в чате
                # (FEED_NUDGE_SATIETY_THRESHOLD), но это отдельный, проактивный пуш: срабатывает,
                # даже если пользователь молчит и не может получить подсказку в ответ на сообщение.
                if user.get("satiety", SATIETY_MAX) <= FEED_NUDGE_SATIETY_THRESHOLD:
                    last_hunger_reminder = user.get("last_hunger_reminder")
                    due = True
                    if last_hunger_reminder:
                        try:
                            hours_since = (now - datetime.fromisoformat(last_hunger_reminder)).total_seconds() / 3600
                            due = hours_since >= HUNGER_REMINDER_INTERVAL_HOURS
                        except Exception:
                            due = True
                    if due:
                        user["last_hunger_reminder"] = now.isoformat()
                        save_data(user_data)
                        try:
                            await bot.send_message(int(user_id), get_text(user, "hungry_reminder"),
                                                   reply_markup=get_feed_nudge_kb(user))
                        except Exception:
                            pass
            save_data(user_data)
        except Exception as e:
            logging.error(f"Ошибка уведомлений: {e}")
        await asyncio.sleep(1800)  # проверка раз в 30 минут


# ============================================================
#  ЗАПУСК
# ============================================================
async def main():
    print("🚀 Role Duel запущен!")
    print(f"🧠 Модель: {AI_MODEL or resolve_model('ai')} | интим-сцены: {INTIM_MODEL or resolve_model('intim')}")
    print(f"💾 Данные сохраняются в {os.path.abspath(DATA_FILE)}")
    print(f"👥 Загружено профилей: {len([k for k in user_data if k != '__settings__'])}")
    print(f"💳 Способы оплаты: {', '.join(available_payment_methods())}")
    print(f"🛍 Mini App магазин: {'включён, ' + WEBAPP_URL + '/shop' if WEBAPP_URL else 'выключен (WEBAPP_URL не задан)'}")
    print("✅ БОТ ГОТОВ К РАБОТЕ!")

    # Нативное меню команд Telegram (кнопка "/" рядом с полем ввода) — всегда на русском,
    # т.к. привязано к языку клиента Telegram, а не к языку, выбранному внутри бота.
    await bot.set_my_commands([
        BotCommand(command="start", description="Регистрация / главное меню"),
        BotCommand(command="help", description="Список команд"),
        BotCommand(command="language", description="Сменить язык"),
        BotCommand(command="hot", description="Горячая сцена с персонажем"),
        BotCommand(command="feed", description="Покормить персонажа"),
        BotCommand(command="work", description="Отправить на работу за баксы"),
        BotCommand(command="reset_character", description="Сбросить кастомного персонажа"),
        BotCommand(command="switch_personality", description="Сменить мир/пол (SUPER PRO+)"),
        BotCommand(command="switch_style", description="Сменить стиль (SUPER PRO+)"),
    ])

    if WEBAPP_URL:
        asyncio.create_task(run_webapp_server())
    asyncio.create_task(check_notifications())
    asyncio.create_task(check_pending_payments())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
