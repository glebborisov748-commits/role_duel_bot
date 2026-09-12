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

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice,
    ReplyKeyboardMarkup, KeyboardButton, BotCommand, FSInputFile
)
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
        "intim_continue_btn": "🔁 Продолжить сцену",
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
        "subs_body": "🔥 PRO (250⭐/мес)\n• Стили: ❤️‍🔥 Страстный, ✨ Магнетический\n• Память: 60 сообщений\n• Бонус XP: x1.8\n• Энергия и сытость персонажа тратятся медленнее (-40%)\n• +80💵 баксов и +2⚡ энергетика каждый день\n• 🎰 2 бесплатные прокрутки колеса в день\n\n✨ SUPER PRO ✨ (450⭐/мес)\n• Все стили + эксклюзивные 😤 Грубый 18+ и 😏 Соблазн 18+\n• Смена стиля без потери истории (/switch_style)\n• Память: 100 сообщений\n• Бонус XP: x2.5\n• 🎭 Создание своего уникального персонажа!\n• Энергия и сытость персонажа тратятся ещё медленнее (-70%)\n• +200💵 баксов и +3⚡ энергетика каждый день\n• 🎰 3 бесплатные прокрутки колеса в день\n• 🔕 Можно отключить уведомления бота\n\n💎 ELITE 💎 (800⭐/мес)\n• Всё, что есть в SUPER PRO\n• Память: 150 сообщений\n• Бонус XP: x3.5\n• Энергия и сытость тратятся минимально (-85%)\n• +350💵 баксов и +6⚡ энергетиков каждый день\n• 🎰 5 бесплатных прокруток колеса в день\n• 🔥 5 бесплатных горячих сцен в день\n\n⬆️ Апгрейд до SUPER PRO (245⭐) — повысьте PRO до SUPER PRO на оставшийся срок.\n\n⚠️ Подписки НЕ продлеваются автоматически.",
        "subs_btn_pro": "🔥 PRO — 250 ⭐/мес",
        "subs_btn_super": "✨ SUPER PRO ✨ — 450 ⭐/мес",
        "subs_btn_elite": "💎 ELITE 💎 — 800 ⭐/мес",
        "subs_btn_upgrade": "⬆️ Апгрейд до SUPER PRO (245⭐)",
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
        "invoice_upgrade_desc": "Повысьте PRO до SUPER PRO на оставшийся срок. 245⭐.",
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
        "effect_satiety_full": "Сытость до максимума",
        "effect_mood_full": "Настроение до максимума",
        "effect_xp": "XP +{n}",
        "gift_already_owned": "😉 У тебя уже есть этот подарок — персонажу не нужен второй такой же.",
        "shop_category_food": "🍽 Еда",
        "shop_category_treat": "🎁 Подарки",
        "shop_category_accessory": "💍 Аксессуары",
        "shop_item_owned": " ✅ уже есть",
        "custom_gift_btn": "✍️ Свой подарок — {price}💵",
        "custom_gift_prompt": "✍️ Напиши, что хочешь подарить (до {n} символов, цена {price}💵). Каждый подарок можно подарить только один раз.",
        "custom_gift_invalid": "❌ Напиши текст подарка (до {n} символов).",
        "custom_gift_duplicate": "😉 Ты уже дарил(а) именно это. Придумай что-то новое!",
        "hungry_nudge": "🍽 У собеседника заурчал живот... Может, покормишь?",
        "low_energy_nudge": "😴 Собеседник начинает уставать и клонит в сон... Может, взбодришь энергетиком?",
        "not_enough_bucks": "❌ Не хватает баксов: нужно ещё {n}💵.",
        "not_enough_energizers": "❌ Нет энергетиков. Купи бандл, чтобы разбудить персонажа сразу ⚡.",
        "asleep_message": "😴 Персонаж крепко спит и сейчас не может ответить — сам он не проснётся, разбуди его энергетиком ⚡ или сразу и полностью за {price}⭐.",
        "wake_energizer_btn": "⚡ Разбудить энергетиком",
        "no_energizers_shop_btn": "🛍 Нет энергетиков — купить",
        "woken_up": "⚡ Энергетик выпит — персонаж снова бодр и на связи!",
        "stats_line": "⚡ Энергия: {energy}/150   🍗 Сытость: {satiety}/100\n{mood_emoji} Настроение: {mood_bar} ({mood_value})\n⚡ Энергетиков: {energizers}   💵 Баксов: {bucks} — потратить можно в 🛍 Магазине\n🔥 Сцен: {scenes}",
        "wake_now_btn": "💳 Разбудить сейчас за {price}⭐",
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
        "intim_continue_btn": "🔁 Continue the scene",
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
        "subs_body": "🔥 PRO (250⭐ per month)\n• Styles: ❤️‍🔥 Passionate, ✨ Magnetic\n• Memory: 60 messages\n• XP bonus: x1.8\n• Your companion's energy and satiety drain slower (-40%)\n• +80💵 bucks and +2⚡ energizers every day\n• 🎰 2 free spins a day\n\n✨ SUPER PRO ✨ (450⭐ per month)\n• All styles + exclusive 😤 Rough 18+ and 😏 Temptation 18+\n• Switch styles without losing history (/switch_style)\n• Memory: 100 messages\n• XP bonus: x2.5\n• 🎭 Create your own unique character!\n• Energy and satiety drain even slower (-70%)\n• +200💵 bucks and +3⚡ energizers every day\n• 🎰 3 free spins a day\n• 🔕 Mute the bot's notifications\n\n💎 ELITE 💎 (800⭐ per month)\n• Everything in SUPER PRO\n• Memory: 150 messages\n• XP bonus: x3.5\n• Energy and satiety drain to a minimum (-85%)\n• +350💵 bucks and +6⚡ energizers every day\n• 🎰 5 free spins a day\n• 🔥 5 free hot scenes a day\n\n⬆️ Upgrade to SUPER PRO (245⭐) — upgrade PRO to SUPER PRO for the remaining time.\n\n⚠️ Subscriptions do NOT renew automatically.",
        "subs_btn_pro": "🔥 PRO — 250 ⭐ per month",
        "subs_btn_super": "✨ SUPER PRO ✨ — 450 ⭐ per month",
        "subs_btn_elite": "💎 ELITE 💎 — 800 ⭐ per month",
        "subs_btn_upgrade": "⬆️ Upgrade to SUPER PRO (245⭐)",
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
        "invoice_upgrade_desc": "Upgrade PRO to SUPER PRO for the remaining time. 245⭐.",
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
        "effect_satiety_full": "Satiety maxed out",
        "effect_mood_full": "Mood maxed out",
        "effect_xp": "XP +{n}",
        "gift_already_owned": "😉 You already have this gift — your companion doesn't need a second one.",
        "shop_category_food": "🍽 Food",
        "shop_category_treat": "🎁 Treats",
        "shop_category_accessory": "💍 Accessories",
        "shop_item_owned": " ✅ owned",
        "custom_gift_btn": "✍️ Custom gift — {price}💵",
        "custom_gift_prompt": "✍️ Write what you want to gift (up to {n} characters, price {price}💵). Each gift can only be given once.",
        "custom_gift_invalid": "❌ Write the gift's text (up to {n} characters).",
        "custom_gift_duplicate": "😉 You've already given that exact gift. Think of something new!",
        "hungry_nudge": "🍽 Your companion's stomach just growled... Maybe feed them?",
        "low_energy_nudge": "😴 Your companion is starting to feel drowsy... Maybe perk them up with an energizer?",
        "not_enough_bucks": "❌ Not enough bucks: you need {n}💵 more.",
        "not_enough_energizers": "❌ No energizers left. Buy a bundle to wake your companion up right away ⚡.",
        "asleep_message": "😴 Your companion is fast asleep and can't reply right now — they won't wake up on their own, so wake them with an energizer ⚡ or instantly and fully for {price}⭐.",
        "wake_energizer_btn": "⚡ Wake up with an energizer",
        "no_energizers_shop_btn": "🛍 No energizers — buy some",
        "woken_up": "⚡ Energizer used — your companion is wide awake again!",
        "stats_line": "⚡ Energy: {energy}/150   🍗 Satiety: {satiety}/100\n{mood_emoji} Mood: {mood_bar} ({mood_value})\n⚡ Energizers: {energizers}   💵 Bucks: {bucks} — spend them in the 🛍 Shop\n🔥 Scenes: {scenes}",
        "wake_now_btn": "💳 Wake up now for {price}⭐",
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
        "intim_continue_btn": "🔁 Szene fortsetzen",
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
        "subs_body": "🔥 PRO (250⭐ pro Monat)\n• Stile: ❤️‍🔥 Leidenschaftlich, ✨ Magnetisch\n• Gedächtnis: 60 Nachrichten\n• XP-Bonus: x1.8\n• Energie und Sättigung deines Begleiters sinken langsamer (-40%)\n• +80💵 Bucks und +2⚡ Energydrinks jeden Tag\n• 🎰 2 Gratisdrehungen pro Tag\n\n✨ SUPER PRO ✨ (450⭐ pro Monat)\n• Alle Stile + exklusiv 😤 Rau 18+ und 😏 Verführung 18+\n• Stilwechsel ohne Verlust des Verlaufs (/switch_style)\n• Gedächtnis: 100 Nachrichten\n• XP-Bonus: x2.5\n• 🎭 Eigenen Charakter erstellen!\n• Energie und Sättigung sinken noch langsamer (-70%)\n• +200💵 Bucks und +3⚡ Energydrinks jeden Tag\n• 🎰 3 Gratisdrehungen pro Tag\n• 🔕 Benachrichtigungen des Bots stummschalten\n\n💎 ELITE 💎 (800⭐ pro Monat)\n• Alles aus SUPER PRO\n• Gedächtnis: 150 Nachrichten\n• XP-Bonus: x3.5\n• Energie und Sättigung sinken auf ein Minimum (-85%)\n• +350💵 Bucks und +6⚡ Energydrinks jeden Tag\n• 🎰 5 Gratisdrehungen pro Tag\n• 🔥 5 kostenlose heiße Szenen pro Tag\n\n⬆️ Upgrade auf SUPER PRO (245⭐) — hebt PRO für die Restlaufzeit auf SUPER PRO an.\n\n⚠️ Abos verlängern sich NICHT automatisch.",
        "subs_btn_pro": "🔥 PRO — 250 ⭐ pro Monat",
        "subs_btn_super": "✨ SUPER PRO ✨ — 450 ⭐ pro Monat",
        "subs_btn_elite": "💎 ELITE 💎 — 800 ⭐ pro Monat",
        "subs_btn_upgrade": "⬆️ Upgrade auf SUPER PRO (245⭐)",
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
        "invoice_upgrade_desc": "Hebt PRO für die Restlaufzeit auf SUPER PRO an. 245⭐.",
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
        "effect_satiety_full": "Sättigung auf Maximum",
        "effect_mood_full": "Stimmung auf Maximum",
        "effect_xp": "XP +{n}",
        "gift_already_owned": "😉 Das hast du deinem Begleiter schon geschenkt — ein zweites Exemplar braucht er/sie nicht.",
        "shop_category_food": "🍽 Essen",
        "shop_category_treat": "🎁 Geschenke",
        "shop_category_accessory": "💍 Accessoires",
        "shop_item_owned": " ✅ vorhanden",
        "custom_gift_btn": "✍️ Eigenes Geschenk — {price}💵",
        "custom_gift_prompt": "✍️ Schreib, was du schenken möchtest (bis zu {n} Zeichen, Preis {price}💵). Jedes Geschenk kann nur einmal verschenkt werden.",
        "custom_gift_invalid": "❌ Schreib den Text des Geschenks (bis zu {n} Zeichen).",
        "custom_gift_duplicate": "😉 Das hast du schon verschenkt. Denk dir etwas Neues aus!",
        "hungry_nudge": "🍽 Der Magen deines Begleiters knurrt gerade... Vielleicht Zeit zu füttern?",
        "low_energy_nudge": "😴 Dein Begleiter wird langsam müde und schläfrig... Vielleicht mit einem Energydrink aufmuntern?",
        "not_enough_bucks": "❌ Nicht genug Bucks: dir fehlen noch {n}💵.",
        "not_enough_energizers": "❌ Keine Energydrinks mehr. Kaufe ein Bundle, um deinen Begleiter sofort aufzuwecken ⚡.",
        "asleep_message": "😴 Dein Begleiter schläft tief und fest und kann gerade nicht antworten — von selbst wacht er/sie nicht auf, also weck ihn/sie mit einem Energydrink ⚡ oder sofort und vollständig für {price}⭐.",
        "wake_energizer_btn": "⚡ Mit Energydrink wecken",
        "no_energizers_shop_btn": "🛍 Keine Energydrinks — kaufen",
        "woken_up": "⚡ Energydrink getrunken — dein Begleiter ist wieder hellwach!",
        "stats_line": "⚡ Energie: {energy}/150   🍗 Sättigung: {satiety}/100\n{mood_emoji} Stimmung: {mood_bar} ({mood_value})\n⚡ Energydrinks: {energizers}   💵 Bucks: {bucks} — ausgeben im 🛍 Shop\n🔥 Szenen: {scenes}",
        "wake_now_btn": "💳 Jetzt wecken für {price}⭐",
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
            "owned_accessories": [],
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
            "owned_accessories": [],
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
# характеристики сразу на максимум (full_restore). "accessory" — вещи, которые не покупают по 15
# штук (духи, косметика, каблуки, платье, украшение, телефон): repeatable=False, одна на аккаунт,
# и на male_variant заменяется вид/название под персонажа-мужчину (часы вместо каблуков и т.п.),
# сама механика (цена/эффект/xp) не меняется. reaction_hint — ориентир тона для AI-благодарности
# (generate_shop_reaction), пользователю не показывается.
FOOD_ITEMS = {
    "snack": {"emoji": "🍪", "ru": "Снек", "en": "Snack", "de": "Snack", "price": 15, "satiety": 10,
              "category": "food", "reaction_hint": "Это мелкая, но милая забота — благодарность лёгкая, тёплая, почти игривая."},
    "breakfast": {"emoji": "🥐", "ru": "Завтрак", "en": "Breakfast", "de": "Frühstück", "price": 22, "satiety": 18,
                  "category": "food", "reaction_hint": "Утренняя забота — благодарность сонная, но очень нежная, ты тронута, что о тебе подумали с самого утра."},
    "meal": {"emoji": "🍲", "ru": "Обед", "en": "Meal", "de": "Mahlzeit", "price": 30, "satiety": 25,
             "category": "food", "reaction_hint": "Это нормальная забота о тебе — благодарность душевная, ты чувствуешь себя сытой и по-настоящему тронута вниманием."},
    "cafe": {"emoji": "☕", "ru": "Кафе", "en": "Café", "de": "Café", "price": 55, "satiety": 50, "mood": 8,
             "category": "food", "reaction_hint": "Это настоящее свидание за столиком, не просто еда — благодарность тёплая, немного смущённая, приятно проведённое время."},
    "restaurant": {"emoji": "🍽", "ru": "Ресторан", "en": "Restaurant", "de": "Restaurant", "price": 90, "satiety": 80, "mood": 6,
                   "category": "food", "reaction_hint": "Настоящий поход в ресторан — не просто еда, а маленькое свидание, благодарность восторженная и чуть взволнованная."},
    "sushi": {"emoji": "🍣", "ru": "Суши-сет", "en": "Sushi set", "de": "Sushi-Set", "price": 120, "satiety": 70, "mood": 10,
              "category": "food", "reaction_hint": "Необычный, изысканный выбор — благодарность удивлённая и довольная, ты оценила, что подошли к делу с фантазией."},
}
GIFT_ITEMS = {
    "sweets": {"emoji": "🍫", "ru": "Шоколадки", "en": "Chocolates", "de": "Pralinen", "price": 20, "satiety": 6, "mood": 25, "xp": 5,
               "category": "treat", "repeatable": True,
               "reaction_hint": "Простой милый подарок — благодарность лёгкая, с улыбкой, без надрыва."},
    "wine": {"emoji": "🍷", "ru": "Вино", "en": "Wine", "de": "Wein", "price": 35, "satiety": 8, "mood": 20, "xp": 7,
             "category": "treat", "repeatable": True,
             "reaction_hint": "Романтичный намёк на вечер вдвоём — благодарность чуть кокетливая, с лёгким флиртом."},
    "flowers": {"emoji": "💐", "ru": "Цветы", "en": "Flowers", "de": "Blumen", "price": 30, "mood": 18, "xp": 8,
                "category": "treat", "repeatable": True,
                "reaction_hint": "Классический трогательный жест — благодарность искренняя и нежная, ты правда растрогана."},
    "perfume": {"emoji": "🧴", "ru": "Духи", "en": "Perfume", "de": "Parfüm", "price": 45, "mood": 18, "xp": 10,
                "category": "accessory", "repeatable": False,
                "reaction_hint": "Личный, продуманный подарок про заботу о тебе — приятно удивлена, что он угадал(а) со вкусом."},
    "cosmetics": {"emoji": "💄", "ru": "Косметика", "en": "Cosmetics", "de": "Kosmetik", "price": 60, "mood": 20, "xp": 12,
                  "category": "accessory", "repeatable": False,
                  "reaction_hint": "Подарок про заботу о твоей красоте — благодарность тёплая, немного смущённая, приятно, что заметили детали.",
                  "male_variant": {"emoji": "🪒", "ru": "Набор для бритья", "en": "Shaving set", "de": "Rasierset",
                                    "reaction_hint": "Подарок про заботу о твоём уходе за собой — благодарность тёплая, немного смущённая, приятно, что заметили детали."}},
    "heels": {"emoji": "👠", "ru": "Каблуки", "en": "Heels", "de": "High Heels", "price": 90, "mood": 25, "xp": 16,
              "category": "accessory", "repeatable": False,
              "reaction_hint": "Дерзкий, чуть сексуальный подарок — благодарность кокетливая и уверенная в себе.",
              "male_variant": {"emoji": "⌚", "ru": "Наручные часы", "en": "Wristwatch", "de": "Armbanduhr",
                                "reaction_hint": "Дорогой, статусный подарок — благодарность сдержанная, но искренне впечатлён вниманием к деталям."}},
    "dress": {"emoji": "👗", "ru": "Платье", "en": "Dress", "de": "Kleid", "price": 120, "mood": 30, "xp": 20,
              "category": "accessory", "repeatable": False,
              "reaction_hint": "Особенный подарок, который хочется сразу примерить — благодарность взволнованная, с предвкушением похвастаться.",
              "male_variant": {"emoji": "🧥", "ru": "Стильный костюм", "en": "Stylish suit", "de": "Eleganter Anzug",
                                "reaction_hint": "Особенный подарок, который хочется сразу примерить — благодарность довольная, с предвкушением показаться в нём."}},
    "jewelry": {"emoji": "💎", "ru": "Украшение", "en": "Jewelry", "de": "Schmuck", "price": 160, "mood": 38, "xp": 28,
                "category": "accessory", "repeatable": False,
                "reaction_hint": "Дорогой, значимый подарок — благодарность глубокая, ты растрогана и немного смущена такой щедростью."},
    "phone": {"emoji": "📱", "ru": "Телефон", "en": "Phone", "de": "Handy", "price": 250, "mood": 45, "xp": 40,
              "category": "accessory", "repeatable": False,
              "reaction_hint": "Очень дорогой подарок — искренний шок и восторг, ты не ожидала такой щедрости и говоришь об этом прямо."},
    "date": {"emoji": "🌹", "ru": "Романтический вечер", "en": "Romantic evening", "de": "Romantischer Abend", "price": 300, "xp": 60,
             "category": "treat", "repeatable": True, "full_restore": True,
             "reaction_hint": "Самый интимный из подарков — не вещь, а вечер вдвоём — благодарность взволнованная, с предвкушением встречи, самая тёплая из всех."},
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
ENERGIZERS_DAILY_STIPEND = {"pro": 2, "super_pro": 3, "elite": 6}  # такая же ежедневная "подпитка", но энергетиками
# pro было 1/день — при цене подписки это выходило дороже за энергетик, чем в самом дешёвом
# бандле (250⭐/30 vs 30⭐/5 = 8.3 vs 6 ⭐ за энергетик), тогда как баксы в подписке уже в разы
# дешевле, чем в бандле — несправедливость была именно в этой цифре, не во всей подписке.


def free_spins_allowed(user):
    return FREE_SPINS_PER_DAY.get(get_subscription_level(user), 1)


def free_spins_left(user):
    _reset_daily_quota_if_needed(user)
    return max(0, free_spins_allowed(user) - user.get("free_spins_used", 0))


def _reset_daily_quota_if_needed(user):
    level = get_subscription_level(user)
    today = datetime.now().date().isoformat()
    if user.get("last_daily_reset") == today:
        return
    user["last_daily_reset"] = today
    user["free_spins_used"] = 0
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


def mood_bar(mood, segments=10):
    """Визуальная шкала настроения для профиля/меню — -100..100 в segments закрашенных блоков."""
    filled = max(0, min(segments, round((mood + MOOD_MAX) / (2 * MOOD_MAX) * segments)))
    return "🟩" * filled + "⬜" * (segments - filled)


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
SATIETY_INACTIVITY_DECAY_MINUTES = 180  # без активности сытость сама падает с полной до нуля примерно
                                          # за 3 часа — реалистичнее, чем раньше (сама "восстанавливалась"
                                          # без еды): не покормили — значит проголодался, а не наоборот
ENERGY_COST_MESSAGE = 12  # бак вырос в 1.5 раза (100->150), но стоимость сообщения выросла вдвое —
                          # сообщений на полный бак стало МЕНЬШЕ, чем раньше (было ~16.7, теперь ~12.5)
SATIETY_COST_MESSAGE = 6  # было 3 (3% от бака за сообщение — заметно медленнее, чем энергия при
                          # 12/150=8%); по просьбе голод должен наступать быстрее, теперь 6%
ENERGIZER_RESTORE_AMOUNT = 78  # было 98 (65% бака) — точечно снижено до 78 (52% бака), без
                               # сопутствующего удвоения количеств бандлов/стипендов (в отличие
                               # от прошлой попытки уполовинить до 50, которая смотрелась чрезмерно
                               # в связке с удвоенными "72 энергетика за 200" и была отклонена).
STAT_DECAY_MULTIPLIER = {"pro": 0.6, "super_pro": 0.3, "elite": 0.15}  # подписчики устают/голодают медленнее
INTIMACY_LEVEL_DECAY_STEP = 0.1  # чем ближе вы, тем персонаж "требовательнее": на 1 уровне — как
                                  # обычно, на 10 — почти вдвое быстрее тратит энергию и сытость
# У /hot нет стоимости энергии/сытости и нет проверки is_asleep(user) — это отдельный платный
# раздел именно для тех, кто не хочет ждать ни уровня близости, ни "сна" персонажа (см. intim_cmd
# и generate_intim_scene): тамагочи-механика на него не распространяется ни в одну, ни в другую сторону.


def apply_passive_satiety_decay(user):
    """Сытость сама падает, пока пользователь не пишет — как в жизни: не покормили, значит
    персонаж проголодался, а не наоборот (раньше она "регенерировала" сама без еды, что было
    нереалистично). Энергия в этом не участвует вообще — она теперь не восстанавливается сама
    ни при каких условиях, только энергетиком или платным "разбудить сейчас"."""
    now = datetime.now()
    last = user.get("last_stat_tick")
    if last:
        try:
            elapsed_min = max(0.0, (now - datetime.fromisoformat(last)).total_seconds() / 60)
        except (ValueError, TypeError):
            elapsed_min = 0
        if elapsed_min > 0:
            user["satiety"] = max(0, user.get("satiety", SATIETY_MAX) - elapsed_min * (SATIETY_MAX / SATIETY_INACTIVITY_DECAY_MINUTES))
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


def apply_activity_stat_cost(user, energy_cost, satiety_cost):
    mult = STAT_DECAY_MULTIPLIER.get(get_subscription_level(user), 1.0) * get_level_decay_multiplier(user)
    prev_energy = user.get("energy", ENERGY_MAX)
    user["energy"] = max(0, prev_energy - energy_cost * mult)
    user["satiety"] = max(0, user.get("satiety", SATIETY_MAX) - satiety_cost * mult)
    if prev_energy > 0 and user["energy"] <= 0:
        # Энергия только что впервые дошла до 0 — фиксируем момент засыпания. sleep_until
        # больше НЕ таймер пробуждения (раньше был +20 минут, и по истечении персонаж
        # просыпался сам, бесплатно) — теперь это просто факт "спит", который снимается
        # только явным действием (энергетик или платное "разбудить сейчас"), а не временем:
        # is_asleep() смотрит только на то, установлено ли поле, а не на его значение.
        user["sleep_until"] = datetime.now().isoformat()


def is_asleep(user):
    return bool(user.get("sleep_until"))


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


def stats_line_text(user):
    mood = user.get("mood", 0)
    return get_text(
        user, "stats_line",
        energy=int(round(user.get("energy", ENERGY_MAX))),
        satiety=int(round(user.get("satiety", SATIETY_MAX))),
        energizers=user.get("energizers", 0),
        bucks=user.get("bucks", 0),
        mood_emoji=mood_emoji(mood),
        mood_bar=mood_bar(mood),
        mood_value=int(round(mood)),
        scenes=intim_scenes_available(user),
    )


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
            f"Ты НИКОГДА не спрашиваешь имя собеседника. Обращайся к собеседнику ТОЛЬКО на «ты». "
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
        "используешь его имя, даже если оно было названо. Обращайся к собеседнику ТОЛЬКО на «ты».\n"
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
        f"{mood_rule} {energy_rule}{hunger_rule}"
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
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "buy_bundles"), callback_data="profile_bundles", style="success")],
        [InlineKeyboardButton(text=get_text(user, "shop_btn"), callback_data="profile_shop", style="success")],
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
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=5)).isoformat()
        user["subscription"]["level"] = "pro"
        user["last_daily_reset"] = None
        _reset_daily_quota_if_needed(user)
        result_text = get_text(user, "spin_win_pro")
    elif chosen["type"] == "subscription_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=3)).isoformat()
        user["subscription"]["level"] = "super_pro"
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


def gift_already_owned(user, key, item):
    """Не-повторяемые аксессуары (духи, косметика, каблуки/часы, платье/костюм, украшение,
    телефон) покупаются один раз на аккаунт — незачем 15 одинаковых пар каблуков."""
    return not item.get("repeatable", True) and key in user.get("owned_accessories", [])


def format_item_effects(item, user):
    parts = []
    if item.get("full_restore"):
        parts.append(get_text(user, "effect_satiety_full"))
        parts.append(get_text(user, "effect_mood_full"))
    else:
        if item.get("satiety"):
            parts.append(get_text(user, "effect_satiety", n=item["satiety"]))
        if item.get("mood"):
            parts.append(get_text(user, "effect_mood", n=item["mood"]))
    if item.get("xp"):
        parts.append(get_text(user, "effect_xp", n=item["xp"]))
    return ", ".join(parts)


def apply_shop_item_effects(user, item):
    if item.get("full_restore"):
        user["satiety"] = SATIETY_MAX
        user["mood"] = MOOD_MAX
    else:
        if "satiety" in item:
            user["satiety"] = min(SATIETY_MAX, user.get("satiety", SATIETY_MAX) + item["satiety"])
        if "mood" in item:
            user["mood"] = min(MOOD_MAX, max(-MOOD_MAX, user.get("mood", 0) + item["mood"]))


SHOP_CATEGORY_ORDER = ["food", "treat", "accessory"]
SHOP_CATEGORY_TEXT_KEY = {"food": "shop_category_food", "treat": "shop_category_treat", "accessory": "shop_category_accessory"}

# Каталог аксессуаров конечен и одноразовый — рано или поздно всё куплено. "Свой подарок" даёт
# запасной вариант: любой текст, который ещё не дарили (дубли по нормализованному тексту), с
# рандомным настроением из диапазона обычных аксессуаров (см. их mood выше — 18..45), а не
# средним: со случайным числом каждый раз приятнее, чем одна и та же предсказуемая цифра.
CUSTOM_GIFT_PRICE = 100
CUSTOM_GIFT_MOOD_RANGE = (18, 45)
CUSTOM_GIFT_MAX_LEN = 60


def get_shop_kb(user):
    entries = [(key, item, f"shop_food_{key}", False) for key, item in FOOD_ITEMS.items()]
    entries += [(key, item, f"shop_gift_{key}", True) for key, item in GIFT_ITEMS.items()]

    rows = []
    for category in SHOP_CATEGORY_ORDER:
        cat_entries = [e for e in entries if e[1].get("category") == category]
        if not cat_entries:
            continue
        rows.append([InlineKeyboardButton(text=get_text(user, SHOP_CATEGORY_TEXT_KEY[category]), callback_data="shop_noop")])
        for key, item, callback_data, is_gift in cat_entries:
            if is_gift:
                label = gift_option_label(key, user)
                owned = gift_already_owned(user, key, item)
            else:
                label = intim_option_label(FOOD_ITEMS, key, user)
                owned = False
            suffix = get_text(user, "shop_item_owned") if owned else f" — {item['price']}💵"
            rows.append([InlineKeyboardButton(text=f"{label}{suffix}", callback_data=callback_data, style="success")])
        if category == "accessory":
            rows.append([InlineKeyboardButton(
                text=get_text(user, "custom_gift_btn", price=CUSTOM_GIFT_PRICE),
                callback_data="shop_custom_gift_start", style="success")])

    rows.append([InlineKeyboardButton(text=get_text(user, "back_to_profile"), callback_data="back_to_profile", style="danger")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


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
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{intim_option_label(FOOD_ITEMS, key, user)} — {item['price']}💵",
                              callback_data=f"shop_food_{key}", style="success")]
        for key, item in FOOD_ITEMS.items()
    ])


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


@dp.callback_query(lambda c: c.data.startswith("shop_food_"))
async def buy_food(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    key = call.data[len("shop_food_"):]
    item = FOOD_ITEMS.get(key)
    if not item:
        await call.answer()
        return
    if not spend_bucks(user, item["price"]):
        await call.answer(get_text(user, "not_enough_bucks", n=item["price"] - user.get("bucks", 0)), show_alert=True)
        return
    apply_shop_item_effects(user, item)
    save_data(user_data)
    await call.message.answer(get_text(user, "item_bought", effects=format_item_effects(item, user)))
    await call.answer()
    if not is_asleep(user):
        await generate_shop_reaction(call.message.chat.id, user, item, "food")


@dp.callback_query(lambda c: c.data.startswith("shop_gift_"))
async def buy_gift(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    key = call.data[len("shop_gift_"):]
    base_item = GIFT_ITEMS.get(key)
    if not base_item:
        await call.answer()
        return
    if gift_already_owned(user, key, base_item):
        await call.answer(get_text(user, "gift_already_owned"), show_alert=True)
        return
    if not spend_bucks(user, base_item["price"]):
        await call.answer(get_text(user, "not_enough_bucks", n=base_item["price"] - user.get("bucks", 0)), show_alert=True)
        return
    display_item = gift_effective_item(base_item, user)
    apply_shop_item_effects(user, base_item)
    if not base_item.get("repeatable", True):
        user.setdefault("owned_accessories", []).append(key)
    save_data(user_data)
    if base_item.get("xp"):
        await grant_gift_xp(call.message.chat.id, user, base_item["xp"])
    await call.message.answer(get_text(user, "item_bought", effects=format_item_effects(base_item, user)))
    await call.answer()
    if not is_asleep(user):
        await generate_shop_reaction(call.message.chat.id, user, display_item, "gift")


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
PRODUCTS = {
    "subscribe_pro": {"stars": 250, "usd": 4.5},
    "subscribe_super": {"stars": 450, "usd": 7.9},
    "subscribe_elite": {"stars": 800, "usd": 14.5},
    "upgrade_to_super": {"stars": 245, "usd": 4.4},
    "bundle_small": {"stars": 30, "usd": 0.7},
    "bundle_medium": {"stars": 80, "usd": 1.7},
    "bundle_large": {"stars": 200, "usd": 3.9},
    "spin_paid_20": {"stars": 15, "usd": 0.4},
    "intim_scene": {"stars": 45, "usd": 1.0},
    "wake_now": {"stars": 50, "usd": 1.2},
}
# Цена в рублях (для Lava) равна цене в звёздах один в один — так попросили,
# отдельного расчёта по курсу нет.
for _product in PRODUCTS.values():
    _product["rub"] = _product["stars"]

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
            for method in available_payment_methods()]
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
    запасаться энергетиками заранее."""
    rows = []
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
    # она выдаётся сразу, тамагочи-механика на неё не распространяется.
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
            "названо. Обращайся к собеседнику ТОЛЬКО на «ты».\n"
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
            "используешь его имя, даже если оно было названо. Обращайся к собеседнику ТОЛЬКО на «ты».\n"
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
        "смех": "😂", "радость": "😊", "любовь": "❤️", "удивление": "😮",
        "грусть": "😔", "злость": "😡", "поддержка": "👍", "интрига": "😏",
        "флирт": "😉", "приветствие": "👋", "вопрос": "🤔"
    }
    reaction = reaction_map.get(reaction_key)
    if reaction is None:
        return None, text
    clean_text = text[:match.start()].rstrip()
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
    apply_activity_stat_cost(user, ENERGY_COST_MESSAGE, SATIETY_COST_MESSAGE)
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


def build_shop_reaction_instruction(item, kind):
    """kind: "food" или "gift". Даёт модели конкретный повод и эмоциональный ориентир
    (reaction_hint), чтобы благодарность не была одинаковым шаблоном для всех предметов —
    снек и романтический вечер должны звучать по-разному."""
    hint = item.get("reaction_hint", "")
    verb = "покормил(а)" if kind == "food" else "подарил(а)"
    thing = item["ru"].lower()
    return (
        f"\n\nСобеседник только что {verb} тебя: «{thing}». {hint} Отреагируй и поблагодари "
        f"в характере — коротко (1-2 реплики), не шаблонно, с реакцией именно на ЭТО, а не общими "
        f"словами благодарности, которые подошли бы к любому подарку."
    )


async def generate_shop_reaction(chat_id, user, item, kind):
    """Просит ИИ отреагировать и поблагодарить в характере за конкретную еду/подарок —
    полноценная реплика персонажа через build_prompt(user), а не статичный текст,
    и разная в зависимости от того, что именно куплено (см. reaction_hint у предмета)."""
    system_prompt = build_prompt(user) + build_shop_reaction_instruction(item, kind)
    action_word = "кормит" if kind == "food" else "дарит"
    action_text = f"*{action_word} тебя: {item['ru'].lower()}*"
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

    # 4b. Собеседник может "уснуть", если кончилась энергия — тогда обычный ИИ-ответ
    # не генерируем (экономит и токены, и веру в механику), а кнопки навигации выше уже
    # обработаны и по-прежнему работают, чтобы можно было зайти в профиль и разбудить/покормить.
    if is_asleep(user):
        await message.answer(get_text(user, "asleep_message", price=PRODUCTS["wake_now"]["stars"]), reply_markup=get_wake_kb(user))
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
#  УВЕДОМЛЕНИЯ (ЕЖЕДНЕВНЫЕ И "СКУЧАЮ")
# ============================================================
MISS_YOU_INACTIVITY_DAYS = 2  # с какого дня без сообщений начинаем напоминать
MISS_YOU_INTERVAL_DAYS = 2  # не чаще чем раз в столько дней после предыдущего напоминания


async def check_notifications():
    while True:
        try:
            now = datetime.now()
            today = now.date().isoformat()
            for user_id, user in list(user_data.items()):
                if not user.get("verified") or not user.get("personality_ready"):
                    continue
                # Отключение уведомлений — привилегия SUPER PRO: если подписка упала до PRO или
                # истекла, напоминания сами возобновятся — отдельно снимать флаг не нужно.
                if user.get("notifications_muted") and get_subscription_level(user) in ("super_pro", "elite"):
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
    print(f"🧠 Модель: {AI_MODEL or resolve_model('ai')} | интим-сцены: {INTIM_MODEL or resolve_model('intim')}")
    print(f"💾 Данные сохраняются в {os.path.abspath(DATA_FILE)}")
    print(f"👥 Загружено профилей: {len([k for k in user_data if k != '__settings__'])}")
    print(f"💳 Способы оплаты: {', '.join(available_payment_methods())}")
    print("✅ БОТ ГОТОВ К РАБОТЕ!")

    # Нативное меню команд Telegram (кнопка "/" рядом с полем ввода) — всегда на русском,
    # т.к. привязано к языку клиента Telegram, а не к языку, выбранному внутри бота.
    await bot.set_my_commands([
        BotCommand(command="start", description="Регистрация / главное меню"),
        BotCommand(command="help", description="Список команд"),
        BotCommand(command="language", description="Сменить язык"),
        BotCommand(command="hot", description="Горячая сцена с персонажем"),
        BotCommand(command="reset_character", description="Сбросить кастомного персонажа"),
        BotCommand(command="switch_personality", description="Сменить мир/пол (SUPER PRO+)"),
        BotCommand(command="switch_style", description="Сменить стиль (SUPER PRO+)"),
    ])

    asyncio.create_task(check_notifications())
    asyncio.create_task(check_pending_payments())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
