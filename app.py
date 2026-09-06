import asyncio
import os
import json
import logging
import random
import re
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
)
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
        "our_channel": "📢 Наш канал",
        "edit": "✏️ Редактировать",
        "change_character": "🔄 Сменить персонажа",
        "invite_friend": "👥 Пригласить друга",
        "create_character": "🎭 Создать своего персонажа",
        "buy_packs": "📦 Купить пакеты",
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
        "spin_reminder": "🎁 Привет! У тебя сегодня бесплатное вращение в Колесе фортуны! Зайди и попробуй удачу 🍀",
        "spin_title": "🎰 **Колесо фортуны**",
        "spin_prizes": "🔥 **Что можно выиграть:**\n• 10–50 сообщений\n• 100–250 XP\n• 🎁 PRO на 5 дней\n• ✨ SUPER PRO на 3 дня",
        "spin_choose": "Выбери вариант:",
        "spin_nothing": "😢 Ничего... В следующий раз повезёт!",
        "profile": "Подписка: {status}\nОсталось сообщений: {messages}",
        "referral": "👥 **Твоя реферальная ссылка:**\n`{link}`\n\n🎁 За каждого друга, который зарегистрируется по ссылке, — **+10 сообщений** тебе, ему — **+5 бесплатных сообщений**!",
        "choose_lang_label": "🌍 Выбери язык:",
        "welcome_back_female": "Ой, тебя так долго не было! Я уже успела соскучиться 🥺💕",
        "welcome_back_male": "Ой, тебя так долго не было! Я уже успел соскучиться 🥺💕",
        "welcome_back_female_2": "Ну наконец-то! Я уже думала, ты меня забыл... 😔",
        "welcome_back_male_2": "Ну наконец-то! Я уже думал, ты меня забыла... 😔",
        "miss_you": [
            "Я скучаю... Ты где пропал? 😔 Напиши мне...",
            "Эй, ты там живой? 🥺 Я уже начала волноваться...",
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
        "agreement": "📜 **ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ**\n\nНастоящее Соглашение регулирует отношения между Администрацией (далее – «Мы») и Пользователем (далее – «Вы») при использовании сервиса Role Duel (далее – «Сервис»).\n\nИспользуя Сервис, Вы подтверждаете, что ознакомились с условиями настоящего Соглашения и принимаете их безоговорочно.\n\n---\n\n**1. ВОЗРАСТНОЕ ОГРАНИЧЕНИЕ**\n1.1. Сервис предназначен исключительно для лиц, достигших 18 лет.\n1.2. Использование Сервиса лицами младше 18 лет строго запрещено.\n\n**2. ОПИСАНИЕ СЕРВИСА**\n2.1. Сервис предоставляет доступ к виртуальным собеседникам на основе технологий искусственного интеллекта.\n2.2. Весь контент генерируется автоматически и не отражает мнение Администрации.\n2.3. Сервис не является медицинским, психологическим или консультационным инструментом.\n\n**3. ОТВЕТСТВЕННОСТЬ ПОЛЬЗОВАТЕЛЯ**\n3.1. Вы несёте полную ответственность за все действия, совершённые с использованием Вашего аккаунта.\n3.2. Запрещается использовать Сервис для распространения экстремистских материалов, оскорблений, угроз, клеветы, мошенничества, вредоносного ПО и любых действий, нарушающих законодательство РФ.\n\n**4. КОНФИДЕНЦИАЛЬНОСТЬ**\n4.1. Мы собираем: Telegram ID, историю диалогов, данные о покупках и подписках.\n4.2. Мы НЕ передаём персональные данные третьим лицам, за исключением случаев, предусмотренных законом.\n\n**5. ПЛАТНЫЕ УСЛУГИ**\n5.1. Сервис предоставляет платные услуги (пакеты сообщений, подписки, колесо фортуны).\n5.2. Подписки **НЕ продлеваются автоматически**.\n5.3. Возврат средств не производится, за исключением технической ошибки со стороны Сервиса.\n\n**6. ОТКАЗ ОТ ГАРАНТИЙ**\nСервис предоставляется «как есть» без каких-либо гарантий бесперебойной работы.\n\n**7. ИЗМЕНЕНИЕ УСЛОВИЙ**\nАдминистрация вправе изменять Соглашение в любое время; продолжение использования Сервиса означает согласие с новой версией.\n\n**8. КОНТАКТЫ**\nВсе вопросы принимаются через поддержку в Telegram.\n\n---\n\n⚠️ Если Вы не согласны с настоящим Соглашением, немедленно прекратите использование Сервиса."
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
        "buy_packs": "📦 Buy packs",
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
        "free": "🎁 Free (1/day)",
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
        "spin_reminder": "🎁 Hey! You have a free spin today! Try your luck 🍀",
        "spin_title": "🎰 **Spin wheel**",
        "spin_prizes": "🔥 **What you can win:**\n• 10–50 messages\n• 100–250 XP\n• 🎁 PRO for 5 days\n• ✨ SUPER PRO for 3 days",
        "spin_choose": "Choose an option:",
        "spin_nothing": "😢 Nothing... Better luck next time!",
        "profile": "Subscription: {status}\nMessages left: {messages}",
        "referral": "👥 **Your referral link:**\n`{link}`\n\n🎁 For every friend who signs up with your link — **+10 messages** for you, and **+5 free messages** for them!",
        "choose_lang_label": "🌍 Choose language:",
        "welcome_back_female": "Oh, you've been gone so long! I already missed you 🥺💕",
        "welcome_back_male": "Oh, you've been gone so long! I already missed you 🥺💕",
        "welcome_back_female_2": "Finally! I thought you forgot about me... 😔",
        "welcome_back_male_2": "Finally! I thought you forgot about me... 😔",
        "miss_you": [
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
        "agreement": "📜 **TERMS OF SERVICE**\n\nThis Agreement governs the relationship between the Administration (\"We\") and the User (\"You\") when using the Role Duel service (\"Service\").\n\nBy using the Service, you confirm that you have read and accept the terms of this Agreement unconditionally.\n\n---\n\n**1. AGE RESTRICTION**\n1.1. The Service is intended exclusively for persons aged 18 and over.\n1.2. Use of the Service by persons under 18 is strictly prohibited.\n\n**2. SERVICE DESCRIPTION**\n2.1. The Service provides access to virtual companions based on artificial intelligence.\n2.2. All content is generated automatically and does not reflect the Administration's opinion.\n2.3. The Service is not a medical, psychological or consulting tool.\n\n**3. USER RESPONSIBILITY**\n3.1. You are fully responsible for all actions performed using your account.\n3.2. It is prohibited to use the Service to distribute extremist materials, insults, threats, fraud, malware, or anything violating applicable law.\n\n**4. PRIVACY**\n4.1. We collect: Telegram ID, chat history, purchase and subscription data.\n4.2. We do NOT share personal data with third parties, except as required by law.\n\n**5. PAID SERVICES**\n5.1. The Service provides paid features (message packs, subscriptions, spin wheel).\n5.2. Subscriptions are **NOT renewed automatically**.\n5.3. Refunds are not provided except in case of a technical error by the Service.\n\n**6. DISCLAIMER**\nThe Service is provided «as is» with no uptime guarantees.\n\n**7. CHANGES TO TERMS**\nThe Administration may change this Agreement at any time; continued use means acceptance of the new version.\n\n**8. CONTACT**\nAll questions are handled through Telegram support.\n\n---\n\n⚠️ If you do not agree with this Agreement, stop using the Service immediately."
    }
}

SUPPORTED_LANGS = ("ru", "en")


def get_text(user, key, **kwargs):
    lang = user.get("lang", "ru")
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, TEXTS["ru"][key])
    if kwargs:
        text = text.format(**kwargs)
    return text


def is_button(text, key):
    """Сравнивает текст сообщения с подписью кнопки на любом из поддерживаемых языков.
    Нужно, потому что клавиатуры теперь локализованы (ru/en), а не захардкожены на русском."""
    if not text:
        return False
    return text in (TEXTS["ru"][key], TEXTS["en"][key])


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

PRO_GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGJ5aTRkejlwMGh4eWJ2Zzg0bTVlbWE2ZzFicHlsMXNibXp3dXdsayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GGSbxfzvec3PYZbFOM/giphy.gif"
SUPER_PRO_GIF_URL = "https://media.giphy.com/media/DbHZXBo5WFPZX7QpXj/giphy.gif"
MAIN_MENU_IMAGE_URL = "https://i.ibb.co/k25JyTXD/IMG-2584.jpg"

ADMIN_IDS = [7287815074]
maintenance_mode = False

# ФИКС: раньше путь был "data/data.json", а папки data/ в проекте не было —
# бот при каждом старте читал пустую базу вместо настоящего data.json.
DATA_FILE = "data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            logging.warning(f"Файл {DATA_FILE} повреждён, создаём новый")
            return {}
    return {}


def save_data(data):
    directory = os.path.dirname(DATA_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


user_data = load_data()


def get_free_limit():
    return 13


def get_user(user_id):
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
            "last_activity": datetime.now().isoformat(),
            "last_spin_notified": None,
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
            "last_activity": None,
            "last_spin_notified": None,
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

BASE_STYLES = {
    "warm": {
        "label": "Нежный",
        "emoji": "🪶",
        "description": "Ты нежный, с мягким голосом. Ты умеешь слушать и поддерживать. Ты не торопишь события, ценишь искренность и доверие."
    },
    "daring": {
        "label": "Дерзкий",
        "emoji": "🔥",
        "description": "Ты уверенный, прямолинейный, с искоркой в глазах. Ты любишь флиртовать и остроумно шутить, но всегда знаешь меру."
    },
    "shy": {
        "label": "Стеснительный",
        "emoji": "😊",
        "description": "Ты стеснительный, часто краснеешь, говоришь тихо и иногда запинаешься. Ты долго подбираешь слова, но всегда искренен."
    }
}

PREMIUM_STYLES = {
    "passionate": {
        "label": "Страстный",
        "emoji": "❤️‍🔥",
        "description": "Ты страстный, эмоциональный, с огнём в глазах. Ты говоришь прямо, без стеснения, умеешь дразнить и создавать романтическое напряжение, оставаясь в рамках приличия."
    },
    "magnetic": {
        "label": "Магнетический",
        "emoji": "✨",
        "description": "Ты загадочный, притягательный, с лёгкой магией в каждом слове. Ты говоришь с интригой, оставляя пространство для фантазии, но не раскрываешься полностью."
    }
}

STYLES = {**BASE_STYLES, **PREMIUM_STYLES}
BASE_STYLE_KEYS = ["warm", "daring", "shy"]
PREMIUM_STYLE_KEYS = ["passionate", "magnetic"]
XP_PER_LEVEL = 200

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
    if style in PREMIUM_STYLE_KEYS and get_subscription_level(user) not in ("pro", "super_pro"):
        return "warm"
    return style


def ensure_valid_style(user):
    """True, если текущий стиль премиальный, а подписка на него уже не действует —
    тогда в handle_message() покажем клавиатуру выбора бесплатного стиля."""
    style = user.get("style", "warm")
    return style in PREMIUM_STYLE_KEYS and get_subscription_level(user) not in ("pro", "super_pro")


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
    return f"Уровень {level}/10 {filled}{empty}\n{bar} {scaled_progress}/100 XP"


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


def build_prompt(user):
    no_explicit_rule = (
        "**СТРОГИЙ ЗАПРЕТ 18+:** Ты НИКОГДА не описываешь и не участвуешь в сексуальных сценах, "
        "не используешь откровенную лексику. Романтика ограничивается объятиями, поцелуями и разговорами "
        "о чувствах — без физической близости и её описаний. Если собеседник просит явный контент 18+, "
        "ты мягко уходишь от темы и переводишь разговор на эмоциональную близость.\n"
    )

    if user.get("custom_character"):
        return (
            f"Ты — {user['custom_character']}. "
            f"Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь «меня зовут». "
            f"Ты НИКОГДА не спрашиваешь имя собеседника. Обращайся к собеседнику ТОЛЬКО на «ты». "
            f"Ты всегда отвечаешь как настоящий человек, с эмоциями, сомнениями и чувствами.\n"
            f"{no_explicit_rule}"
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

    lang = user.get("lang", "ru")
    if lang == "en":
        prompt += "\n**ВАЖНО:** Ты ОБЯЗАН отвечать ТОЛЬКО на АНГЛИЙСКОМ языке."
    else:
        prompt += "\n**ВАЖНО:** Ты ОБЯЗАН отвечать ТОЛЬКО на РУССКОМ языке."

    return prompt


# ============================================================
#  КЛАВИАТУРЫ (локализованные по языку пользователя)
# ============================================================
def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ])


def get_age_kb(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "accept"), callback_data="age_yes")],
        [InlineKeyboardButton(text=get_text(user, "decline"), callback_data="age_no")]
    ])


AGREEMENT_URLS = {
    "ru": "https://glebborisov748-commits.github.io/agreement/agreement_ru.html",
    "en": "https://glebborisov748-commits.github.io/agreement/agreement_en.html",
}


def get_agreement_kb(user):
    lang = user.get("lang", "ru")
    url = AGREEMENT_URLS.get(lang, AGREEMENT_URLS["ru"])
    # ВАЖНО: кнопки "Принимаю"/"Не принимаю" продублированы здесь как обычные inline-кнопки.
    # Раньше согласие можно было подтвердить ТОЛЬКО через WebApp, но бот нигде не слушал
    # web_app_data — нажатие "Принимаю" внутри WebApp никак не доходило до бота.
    # Теперь пользователь может просто нажать кнопку в чате — это работает всегда.
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "open_agreement"), web_app=WebAppInfo(url=url))],
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
    for key, style in STYLES.items():
        label = f"{style['emoji']} {style['label']}"
        if key in PREMIUM_STYLE_KEYS and get_subscription_level(user) not in ("pro", "super_pro"):
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
        await bot.send_message(chat_id, get_text(user, "agreement_intro"), reply_markup=get_agreement_kb(user))
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
            user["purchased_messages"] = user.get("purchased_messages", 0) + 5
            user["referred_by"] = referrer_id
            save_data(user_data)
            await message.answer("🎉 Ты пришёл по реферальной ссылке! +5 сообщений тебе и +10 сообщений другу!")

    await proceed_flow(message.from_user.id, message.chat.id)


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


@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    """На случай, если страница соглашения (GitHub Pages) вызовет Telegram.WebApp.sendData(...) —
    тогда бот тоже примет согласие. Основной путь принятия — инлайн-кнопки в get_agreement_kb(),
    им WebApp для этого не требуется."""
    user = get_user(message.from_user.id)
    user["agreement_accepted"] = True
    save_data(user_data)
    await bot.send_message(message.chat.id, get_text(user, "agreement_ok"))
    await proceed_flow(message.from_user.id, message.chat.id)


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
        await message.answer("❌ Команда /switch_personality доступна только для подписчиков SUPER PRO.")
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
        await call.answer("❌ Стиль не найден", show_alert=True)
        return
    if style_key in PREMIUM_STYLE_KEYS and get_subscription_level(user) not in ("pro", "super_pro"):
        label = STYLES[style_key]["label"]
        await call.answer(f"🔒 Стиль «{label}» доступен по подписке PRO/SUPER PRO. Оформи в «Моём профиле».", show_alert=True)
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
        await call.answer("✅ Персонаж обновлён! История сохранена.")
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
        await call.message.edit_text(f"✅ Стиль изменён на: {STYLES[style]['label']}")
        await call.answer()
        await send_main_menu(call.message.chat.id, user)
    else:
        await call.answer("❌ Недопустимый стиль", show_alert=True)


@dp.message(Command("switch_style"))
async def switch_style_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await message.answer("❌ Только для SUPER PRO.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for key, style in STYLES.items():
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=f"{style['emoji']} {style['label']}", callback_data=f"switch_{key}")])
    await message.answer("🔄 **Выбери новый стиль:**\n\nИстория диалога сохранится.", reply_markup=keyboard, parse_mode="Markdown")


@dp.callback_query(lambda c: c.data.startswith("switch_"))
async def switch_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style = call.data.split("_", 1)[1]
    if style not in STYLES:
        await call.answer("❌ Стиль недоступен", show_alert=True)
        return
    user["style"] = style
    save_data(user_data)
    await call.message.edit_text(f"✅ Стиль изменён на: {STYLES[style]['label']}")
    await call.answer()


# ============================================================
#  СОЗДАНИЕ СВОЕГО ПЕРСОНАЖА (SUPER PRO)
# ============================================================
@dp.callback_query(lambda c: c.data == "create_character_locked")
async def create_character_locked(call: types.CallbackQuery):
    await call.answer("🔒 Создание своего персонажа доступно только с подпиской SUPER PRO!", show_alert=True)


@dp.callback_query(lambda c: c.data == "create_character")
async def create_character(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await call.answer("❌ Только для SUPER PRO!", show_alert=True)
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

    gender_name = GENDERS[user["gender"]]["name"]
    world_name = WORLD_NAMES[user["world"]]
    style_label = STYLES[get_display_style(user)]["label"]

    if has_purchased_something(user):
        available = get_available_messages(user)
        balance_text = f"\nОсталось сообщений: {available}" + (" (закончились)" if available <= 0 else "")
    else:
        balance_text = "\nУ вас есть бесплатные сообщения для старта"

    xp_badge = get_xp_badge(user)
    multiplier_text = "Бонус XP: x1.8" if level == "pro" else ("Бонус XP: x2.5" if level == "super_pro" else "")

    menu_text = (
        f"{badge}\n\n"
        f"Текущий собеседник: {gender_name} из {world_name}\n"
        f"Стиль: {style_label}\n"
        f"{balance_text}\n"
        f"{xp_badge}\n"
        f"{multiplier_text}\n\n"
        f"💬 Напиши персонажу...\n"
        f"✨ Или выбери действие внизу."
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
        sub_status = "🔥 PRO активна (50 сообщений/день, память 60 сообщений)"
    elif level == "super_pro":
        sub_status = "✨ SUPER PRO активна (100 сообщений/день, память 100 сообщений)"
    else:
        sub_status = "❌ неактивна (память 30 сообщений)"

    expiry = user["subscription"]["expires_at"]
    if expiry:
        expiry_line = f"Окончание подписки: {datetime.fromisoformat(expiry).strftime('%d.%m.%Y %H:%M')}"
    else:
        expiry_line = "Окончание подписки: неактивна"

    styles_text = ""
    for key, style in STYLES.items():
        locked = key in PREMIUM_STYLE_KEYS and level not in ("pro", "super_pro")
        styles_text += f"{style['emoji']} {style['label']}" + (" 🔒\n" if locked else "\n")

    if has_purchased_something(user):
        available = get_available_messages(user)
        balance_line = f"Доступно сообщений: {available}" + (" (закончились)" if available <= 0 else "")
    else:
        balance_line = "У вас есть бесплатные сообщения для старта"

    xp_badge = get_xp_badge(user)
    multiplier_text = "Бонус XP: x1.8" if level == "pro" else ("Бонус XP: x2.5" if level == "super_pro" else "")

    caption = (f"{balance_line}\n"
               f"Подписка: {sub_status}\n"
               f"{expiry_line}\n\n"
               f"{xp_badge}\n"
               f"{multiplier_text}\n\n"
               f"Доступные стили:\n{styles_text}")

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
        [InlineKeyboardButton(text="🌟 Создать персонажа", callback_data="create_personality")]
    ])
    await message.answer(
        "👤 **Чтобы открыть профиль или купить что-то, сначала создай своего персонажа!**",
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
        await message.answer("Сначала создай персонажа через /start", reply_markup=get_full_kb(user))
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
    await message.answer("📢 **Наш канал:**\nПодписывайся, чтобы быть в курсе новостей и обновлений!",
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
        await message.answer("Сначала заверши регистрацию через /start.")
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
        await call.answer("⏳ Ты уже крутил сегодня! Завтра будет новое бесплатное вращение.", show_alert=True)
        return
    user["last_free_spin"] = today
    save_data(user_data)
    await safe_delete(call.message)
    await spin_result(call.message, user, free=True)
    await call.answer()


@dp.callback_query(lambda c: c.data == "spin_paid")
async def spin_paid(call: types.CallbackQuery):
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="🎰 Колесо фортуны",
            description="Платное вращение — 20⭐. Удачи!",
            payload="spin_paid_20",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Прокрутка", amount=20)]
        )
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
    await call.answer()


@dp.callback_query(lambda c: c.data == "spin_no")
async def spin_no(call: types.CallbackQuery):
    await call.answer("⏳ Бесплатное вращение будет доступно завтра!", show_alert=True)


@dp.callback_query(lambda c: c.data == "spin_back")
async def spin_back(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await safe_delete(call.message)
    await send_main_menu(call.message.chat.id, user)
    await call.answer()


SPIN_PRIZES = [
    {"name": "😢 Ничего", "value": 0, "type": "nothing", "weight": 20},
    {"name": "10 сообщений", "value": 10, "type": "messages", "weight": 18},
    {"name": "15 сообщений", "value": 15, "type": "messages", "weight": 13},
    {"name": "20 сообщений", "value": 20, "type": "messages", "weight": 10},
    {"name": "100 XP", "value": 100, "type": "xp", "weight": 18},
    {"name": "150 XP", "value": 150, "type": "xp", "weight": 10},
    {"name": "250 XP", "value": 250, "type": "xp", "weight": 5},
    {"name": "🎁 PRO на 5 дней", "value": 5, "type": "subscription_pro", "weight": 1.5},
    {"name": "✨ SUPER PRO на 3 дня", "value": 3, "type": "subscription_super", "weight": 0.5},
    {"name": "🎉 50 сообщений (ДЖЕКПОТ!)", "value": 50, "type": "messages", "weight": 1},
]


async def spin_result(message: types.Message, user, free=False):
    weighted = []
    for p in SPIN_PRIZES:
        weighted.extend([p] * int(p["weight"] * 10))
    chosen = random.choice(weighted)

    msg = await message.answer("🎰 Крутим...")
    for _ in range(3):
        await asyncio.sleep(0.5)
        fake = random.choice(SPIN_PRIZES)
        try:
            await msg.edit_text(f"🎰 Почти выпало: {fake['name']}")
        except Exception:
            pass
    await asyncio.sleep(0.8)
    await safe_delete(msg)

    if chosen["type"] == "messages":
        user["purchased_messages"] = user.get("purchased_messages", 0) + chosen["value"]
        result_text = f"📨 **+{chosen['value']} сообщений**"
    elif chosen["type"] == "xp":
        user["xp"] = user.get("xp", 0) + chosen["value"]
        result_text = f"⭐ **+{chosen['value']} XP**"
    elif chosen["type"] == "subscription_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=5)).isoformat()
        user["subscription"]["level"] = "pro"
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().date().isoformat()
        result_text = "🎁 **PRO подписка на 5 дней!**\n🔥 50 сообщений/день, стили Страстный и Магнетический!"
    elif chosen["type"] == "subscription_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=3)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["daily_messages"] = 100
        user["last_daily_reset"] = datetime.now().date().isoformat()
        result_text = "✨ **SUPER PRO на 3 дня!**\n👑 100 сообщений/день, все стили!"
    else:
        result_text = get_text(user, "spin_nothing")

    save_data(user_data)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user, "spin_more"), callback_data="spin_paid")],
        [InlineKeyboardButton(text=get_text(user, "back"), callback_data="spin_back")]
    ])

    await message.answer(
        f"🎰 **Результат!**\n\nТы выиграл: {result_text}\n"
        f"{'🎁 Бесплатное вращение' if free else '💎 Платное вращение'}",
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
        await call.answer("Сначала создай персонажа!", show_alert=True)
        return
    if not user.get("referral_code"):
        user["referral_code"] = str(call.from_user.id)
        save_data(user_data)
    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start=ref_{user['referral_code']}"
    await call.message.answer(get_text(user, "referral", link=link), parse_mode="Markdown")
    await call.answer()


# ============================================================
#  ПОДПИСКИ И ПАКЕТЫ
# ============================================================
@dp.callback_query(lambda c: c.data == "profile_subs")
async def profile_subs(call: types.CallbackQuery):
    await call.answer()
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer("Сначала создай персонажа!", show_alert=True)
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 PRO — 250 ⭐/мес", callback_data="subscribe_pro")],
        [InlineKeyboardButton(text="✨ SUPER PRO ✨ — 450 ⭐/мес", callback_data="subscribe_super")],
        [InlineKeyboardButton(text="⬆️ Апгрейд до SUPER PRO (245⭐)", callback_data="upgrade_to_super")],
        [InlineKeyboardButton(text=get_text(user, "back_to_profile"), callback_data="back_to_profile")]
    ])
    text = ("👑 Подписки Role Duel\n\n"
            "🔥 PRO (250⭐/мес)\n"
            "• 50 сообщений в день\n"
            "• Стили: ❤️‍🔥 Страстный, ✨ Магнетический\n"
            "• Память: 60 сообщений\n"
            "• Бонус XP: x1.8\n\n"
            "✨ SUPER PRO ✨ (450⭐/мес)\n"
            "• 100 сообщений в день\n"
            "• Все стили\n"
            "• Смена стиля без потери истории (/switch_style)\n"
            "• Память: 100 сообщений\n"
            "• Бонус XP: x2.5\n"
            "• 🎭 Создание своего уникального персонажа!\n\n"
            "⬆️ Апгрейд до SUPER PRO (245⭐) — повысьте PRO до SUPER PRO на оставшийся срок.\n\n"
            "⚠️ Подписки НЕ продлеваются автоматически.")
    await call.message.answer(text, reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "profile_packs")
async def profile_packs(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer("Сначала создай персонажа!", show_alert=True)
        return
    if has_active_subscription(user):
        await call.answer("❌ При активной подписке покупка пакетов недоступна.", show_alert=True)
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="30 сообщений — 30 ⭐", callback_data="pack_30")],
        [InlineKeyboardButton(text="100 сообщений — 80 ⭐", callback_data="pack_100")],
        [InlineKeyboardButton(text="300 сообщений — 200 ⭐", callback_data="pack_300")],
        [InlineKeyboardButton(text=get_text(user, "back_to_profile"), callback_data="back_to_profile")]
    ])
    await call.message.answer("📦 **Купить пакет сообщений**\n\nВыбери пакет:", reply_markup=keyboard, parse_mode="Markdown")
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


@dp.callback_query(lambda c: c.data == "subscribe_pro")
async def subscribe_pro(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if has_active_subscription(user):
        await call.answer("❌ У вас уже есть подписка.", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="PRO подписка на месяц",
            description="50 сообщений/день, память 60 сообщений, стили Страстный и Магнетический.",
            payload="subscribe_pro",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="PRO месяц", amount=250)]
        )
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
    await call.answer()


@dp.callback_query(lambda c: c.data == "subscribe_super")
async def subscribe_super(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if has_active_subscription(user):
        await call.answer("❌ У вас уже есть подписка.", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="SUPER PRO подписка на месяц",
            description="100 сообщений/день, память 100 сообщений, все стили.",
            payload="subscribe_super",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="SUPER PRO месяц", amount=450)]
        )
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
    await call.answer()


@dp.callback_query(lambda c: c.data == "upgrade_to_super")
async def upgrade_to_super(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if get_subscription_level(user) != "pro":
        await call.answer("❌ Только для PRO.", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Апгрейд до SUPER PRO",
            description="Повысьте PRO до SUPER PRO на оставшийся срок. 245⭐.",
            payload="upgrade_to_super",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Апгрейд", amount=245)]
        )
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
    await call.answer()


@dp.callback_query(lambda c: c.data.startswith("pack_"))
async def buy_pack(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if has_active_subscription(user):
        await call.answer("❌ При подписке пакеты недоступны.", show_alert=True)
        return
    period = call.data.split("_", 1)[1]
    pack_map = {"30": 30, "100": 100, "300": 300}
    price_map = {"30": 30, "100": 80, "300": 200}
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title=f"Пакет {pack_map[period]} сообщений",
            description=f"{pack_map[period]} сообщений за {price_map[period]}⭐",
            payload=f"pack_{period}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label=f"{pack_map[period]} сообщ.", amount=price_map[period])]
        )
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
    await call.answer()


@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)


@dp.message(lambda m: m.successful_payment)
async def payment_success(message: types.Message):
    user = get_user(message.from_user.id)
    payload = message.successful_payment.invoice_payload
    user["has_purchased"] = True

    if payload.startswith("pack_"):
        period = payload.split("_", 1)[1]
        pack_map = {"30": 30, "100": 100, "300": 300}
        user["purchased_messages"] += pack_map[period]
        save_data(user_data)
        await message.answer(f"✅ Куплено {pack_map[period]} сообщений!")
    elif payload == "subscribe_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().date().isoformat()
        save_data(user_data)
        await message.answer("✅ PRO подписка активирована на месяц!")
    elif payload == "subscribe_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["daily_messages"] = 100
        user["last_daily_reset"] = datetime.now().date().isoformat()
        save_data(user_data)
        await message.answer("✅ SUPER PRO подписка активирована на месяц!")
    elif payload == "upgrade_to_super":
        if has_active_subscription(user) and get_subscription_level(user) == "pro":
            old_expiry = user["subscription"]["expires_at"]
            user["subscription"]["level"] = "super_pro"
            user["daily_messages"] = 100
            save_data(user_data)
            await message.answer(f"✅ Апгрейд до SUPER PRO выполнен до {old_expiry}!")
    elif payload == "spin_paid_20":
        await spin_result(message, user, free=False)


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
        await message.answer("/grant @username — SUPER PRO\n/grant @username pro — PRO")
        return
    user_id = await _resolve_admin_target(message, args[1])
    if user_id is None:
        return
    user = get_user(user_id)
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


async def send_long(message: types.Message, text, **kwargs):
    """Если ответ ИИ длиннее лимита Telegram, отправляем несколькими сообщениями,
    вместо падения с ошибкой 'message is too long'."""
    if len(text) <= MAX_MESSAGE_LEN:
        return await message.answer(text, **kwargs)
    chunks = [text[i:i + MAX_MESSAGE_LEN] for i in range(0, len(text), MAX_MESSAGE_LEN)]
    last = None
    for i, chunk in enumerate(chunks):
        last = await message.answer(chunk, **(kwargs if i == len(chunks) - 1 else {}))
    return last


async def generate_and_reply(message: types.Message, user):
    """Общая логика вызова ИИ и отправки ответа — используется и для обычных сообщений,
    и для регенерации после редактирования (edit)."""
    system_prompt = build_prompt(user)
    typing_task = asyncio.create_task(_keep_typing(message.chat.id))
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "system", "content": system_prompt}] + user["history"],
            temperature=0.9,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
    except Exception as e:
        await message.answer(f"⚠️ Ошибка генерации ответа: {e}")
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
        await message.answer("🛠️ **Бот на техобслуживании**\nСледите за новостями: @duel_dev_channel", parse_mode="Markdown")
        return
    if not user["verified"] or not user["agreement_accepted"]:
        await message.answer("🔞 Сначала пройди регистрацию через /start")
        return
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start")
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
            [InlineKeyboardButton(text="🪶 Нежный", callback_data="fix_style_warm")],
            [InlineKeyboardButton(text="🔥 Дерзкий", callback_data="fix_style_daring")],
            [InlineKeyboardButton(text="😊 Стеснительный", callback_data="fix_style_shy")],
        ])
        await message.answer("⚠️ Твоя подписка закончилась, выбери бесплатный стиль:", reply_markup=keyboard)
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
            await message.answer("💢 Ссора! Уровень близости снижен.", reply_markup=get_full_kb(user))
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
        if new_level > old_level:
            congrats = get_level_congratulation(user, new_level)
            if congrats:
                await message.answer(congrats, reply_markup=get_full_kb(user))
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
async def check_notifications():
    while True:
        try:
            now = datetime.now()
            today = now.date().isoformat()
            for user_id, user in list(user_data.items()):
                if not user.get("verified") or not user.get("personality_ready"):
                    continue

                if user.get("last_free_spin") != today and user.get("last_spin_notified") != today:
                    user["last_spin_notified"] = today
                    save_data(user_data)
                    try:
                        await bot.send_message(int(user_id), get_text(user, "spin_reminder"))
                    except Exception:
                        pass

                if user.get("last_activity"):
                    try:
                        last = datetime.fromisoformat(user["last_activity"])
                    except Exception:
                        continue
                    if (now - last).days >= 3 and user.get("last_reminder") != today:
                        user["last_reminder"] = today
                        save_data(user_data)
                        try:
                            await bot.send_message(int(user_id), random.choice(get_text(user, "miss_you")))
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
    print("🧠 Модель: deepseek/deepseek-chat")
    print(f"💾 Данные сохраняются в {DATA_FILE}")
    print("✅ БОТ ГОТОВ К РАБОТЕ!")

    asyncio.create_task(check_notifications())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
