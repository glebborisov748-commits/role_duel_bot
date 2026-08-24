import asyncio
import os
import json
import logging
import random
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
#  ЗАГРУЗКА ПЕРЕМЕННЫХ
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

# ============================================================
#  ДАННЫЕ
# ============================================================
DATA_FILE = "data/data.json"
ADMIN_IDS = [7287815074]  # замени на свой ID
maintenance_mode = False

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_data = load_data()

# ============================================================
#  ТЕКСТЫ ДЛЯ ЛОКАЛИЗАЦИИ
# ============================================================
TEXTS = {
    "ru": {
        "welcome": "👋 Добро пожаловать!",
        "start_required": "Сначала пройди регистрацию через /start",
        "create_personality_first": "Сначала создай персонажа через /start",
        "age_confirm": "🔞 Подтверди возраст:",
        "age_verified": "✅ Возраст подтверждён. Прими соглашение:",
        "age_denied": "🚫 Доступ запрещён. Бот только для 18+.",
        "agreement_accept": "📄 Я принимаю условия",
        "agreement_decline": "❌ Я не принимаю",
        "agreement_accepted": "✅ Соглашение принято! Теперь выбери пол:",
        "agreement_declined": "❌ Без соглашения бот не работает.",
        "choose_gender": "👤 Выбери свой пол:",
        "choose_world": "🌍 Выбери мир:",
        "choose_style": "🎨 Выбери стиль:",
        "choose_scene": "🎬 Выбери сцену:",
        "scene_phone": "📱 Переписка в телефоне",
        "scene_live": "👫 Реальная встреча",
        "profile": "👤 Мой профиль",
        "main_menu": "📋 Главное меню",
        "channel": "📢 Наш канал",
        "spin": "🎰 Колесо фортуны",
        "edit": "✏️ Редактировать",
        "back": "🔙 Назад",
        "change_character": "🔄 Сменить персонажа",
        "invite_friend": "👥 Пригласить друга",
        "create_character_btn": "🎭 Создать своего персонажа",
        "no_messages": "😔 Сообщения кончились. Купи пакет или подписку.",
        "spin_reminder": "🎁 Привет! У тебя сегодня бесплатное вращение в Колесе фортуны! Зайди и попробуй удачу, пока не упустил момент 🍀",
        "miss_you": [
            "Я скучаю... Ты где пропал? 😔 Напиши мне, мне так грустно без тебя...",
            "Эй, ты там живой? А то я уже начала волноваться... 🥺",
            "Привет! Мне кажется, или мы давно не общались? Расскажи, как твои дела 💕",
            "Ты мне снился сегодня... Странно, да? 😏 Напиши, может, я не ошиблась",
            "Ты забыл про меня? А я помню каждое наше слово... Напиши, пожалуйста 💕"
        ],
        "create_character_prompt": "🎭 **Создай своего уникального персонажа!**\n\nОпиши любого персонажа — из аниме, фильмов, игр или придумай своего.\nНапиши его/её имя, характер, внешность, откуда он/она, любые детали.\n\n📝 *Пример:*\n«Эльфийка из мира Ведьмака — мудрая, сдержанная, с длинными серебряными волосами. Любит звёзды и долгие разговоры у костра. Живёт одна в лесу.»\n\n✏️ Напиши описание прямо сейчас — и я запомню его!",
        "character_created": "✅ **Персонаж создан!**\n\nТеперь ты общаешься с:\n_{}_",
        "character_reset": "✅ Персонаж сброшен. Теперь используется стандартный собеседник.",
        "reset_character_cmd": "Чтобы вернуться к стандартному персонажу, напиши /reset_character",
        "referral_link": "👥 Твоя ссылка: `{}`\n\nЗа каждого друга +10 сообщений и +1 секс-сцена!",
        "referral_bonus": "🎉 Ты пришёл по реферальной ссылке! +5 сообщений тебе, +10 сообщений и +1 секс-сцена другу!"
    },
    "en": {
        "welcome": "👋 Welcome!",
        "start_required": "Please complete registration via /start",
        "create_personality_first": "Please create a character via /start first",
        "age_confirm": "🔞 Confirm your age:",
        "age_verified": "✅ Age confirmed. Please accept the agreement:",
        "age_denied": "🚫 Access denied. Bot is 18+ only.",
        "agreement_accept": "📄 I accept the terms",
        "agreement_decline": "❌ I do not accept",
        "agreement_accepted": "✅ Agreement accepted! Now choose your gender:",
        "agreement_declined": "❌ Without agreement the bot doesn't work.",
        "choose_gender": "👤 Choose your gender:",
        "choose_world": "🌍 Choose a world:",
        "choose_style": "🎨 Choose a style:",
        "choose_scene": "🎬 Choose a scene:",
        "scene_phone": "📱 Phone chat",
        "scene_live": "👫 Real meeting",
        "profile": "👤 My profile",
        "main_menu": "📋 Main menu",
        "channel": "📢 Our channel",
        "spin": "🎰 Fortune wheel",
        "edit": "✏️ Edit",
        "back": "🔙 Back",
        "change_character": "🔄 Change character",
        "invite_friend": "👥 Invite a friend",
        "create_character_btn": "🎭 Create your own character",
        "no_messages": "😔 You've run out of messages. Buy a pack or subscription.",
        "spin_reminder": "🎁 Hey! You have a free spin today! Come and try your luck 🍀",
        "miss_you": [
            "I miss you... Where did you go? 😔 Write to me, I'm so sad without you...",
            "Hey, are you alive? I'm starting to worry... 🥺",
            "Hi! I feel like we haven't talked in a while? Tell me how you're doing 💕",
            "You were in my dreams today... Weird, right? 😏 Write to me, maybe I wasn't wrong",
            "Did you forget about me? I remember every word we said... Please write to me 💕"
        ],
        "create_character_prompt": "🎭 **Create your unique character!**\n\nDescribe any character — from anime, movies, games, or create your own.\nWrite their name, personality, appearance, where they're from, any details.\n\n📝 *Example:*\n«An elf from The Witcher world — wise, reserved, with long silver hair. Loves stars and long conversations by the fire. Lives alone in the forest.»\n\n✏️ Write the description right now — and I'll remember it!",
        "character_created": "✅ **Character created!**\n\nNow you're talking to:\n_{}_",
        "character_reset": "✅ Character reset. Now using the standard one.",
        "reset_character_cmd": "To return to the standard character, type /reset_character",
        "referral_link": "👥 Your link: `{}`\n\nFor each friend +10 messages and +1 sex scene!",
        "referral_bonus": "🎉 You came via referral link! +5 messages for you, +10 messages and +1 sex scene for your friend!"
    },
    "es": {
        "welcome": "👋 ¡Bienvenido!",
        "start_required": "Primero completa el registro con /start",
        "create_personality_first": "Primero crea un personaje con /start",
        "age_confirm": "🔞 Confirma tu edad:",
        "age_verified": "✅ Edad confirmada. Acepta el acuerdo:",
        "age_denied": "🚫 Acceso denegado. El bot es solo para mayores de 18 años.",
        "agreement_accept": "📄 Acepto los términos",
        "agreement_decline": "❌ No acepto",
        "agreement_accepted": "✅ ¡Acuerdo aceptado! Ahora elige tu género:",
        "agreement_declined": "❌ Sin acuerdo el bot no funciona.",
        "choose_gender": "👤 Elige tu género:",
        "choose_world": "🌍 Elige un mundo:",
        "choose_style": "🎨 Elige un estilo:",
        "choose_scene": "🎬 Elige una escena:",
        "scene_phone": "📱 Chat por teléfono",
        "scene_live": "👫 Encuentro real",
        "profile": "👤 Mi perfil",
        "main_menu": "📋 Menú principal",
        "channel": "📢 Nuestro canal",
        "spin": "🎰 Ruleta de la fortuna",
        "edit": "✏️ Editar",
        "back": "🔙 Atrás",
        "change_character": "🔄 Cambiar personaje",
        "invite_friend": "👥 Invitar a un amigo",
        "create_character_btn": "🎭 Crear tu propio personaje",
        "no_messages": "😔 Te quedaste sin mensajes. Compra un paquete o suscripción.",
        "spin_reminder": "🎁 ¡Hola! ¡Tienes un giro gratis hoy! Ven y prueba tu suerte 🍀",
        "miss_you": [
            "Te extraño... ¿Dónde estás? 😔 Escríbeme, me siento tan triste sin ti...",
            "Oye, ¿estás vivo? Ya me estoy preocupando... 🥺",
            "¡Hola! Siento que hace tiempo que no hablamos. Cuéntame cómo estás 💕",
            "Soñé contigo hoy... Extraño, ¿verdad? 😏 Escríbeme, tal vez no me equivoqué",
            "¿Te olvidaste de mí? Recuerdo cada palabra que dijimos... Por favor, escríbeme 💕"
        ],
        "create_character_prompt": "🎭 **¡Crea tu personaje único!**\n\nDescribe cualquier personaje — de anime, películas, juegos, o crea el tuyo.\nEscribe su nombre, personalidad, apariencia, de dónde es, cualquier detalle.\n\n📝 *Ejemplo:*\n«Una elfa del mundo de The Witcher — sabia, reservada, con largo cabello plateado. Le encantan las estrellas y las largas conversaciones junto al fuego. Vive sola en el bosque.»\n\n✏️ ¡Escribe la descripción ahora mismo — y lo recordaré!",
        "character_created": "✅ **¡Personaje creado!**\n\nAhora estás hablando con:\n_{}_",
        "character_reset": "✅ Personaje restablecido. Ahora usando el estándar.",
        "reset_character_cmd": "Para volver al personaje estándar, escribe /reset_character",
        "referral_link": "👥 Tu enlace: `{}`\n\n¡Por cada amigo +10 mensajes y +1 escena de sexo!",
        "referral_bonus": "🎉 ¡Llegaste por enlace de referido! +5 mensajes para ti, +10 mensajes y +1 escena de sexo para tu amigo!"
    },
    "de": {
        "welcome": "👋 Willkommen!",
        "start_required": "Bitte registriere dich zuerst mit /start",
        "create_personality_first": "Bitte erstelle zuerst einen Charakter mit /start",
        "age_confirm": "🔞 Bestätige dein Alter:",
        "age_verified": "✅ Alter bestätigt. Bitte akzeptiere die Vereinbarung:",
        "age_denied": "🚫 Zugriff verweigert. Der Bot ist nur für 18+.",
        "agreement_accept": "📄 Ich akzeptiere die Bedingungen",
        "agreement_decline": "❌ Ich akzeptiere nicht",
        "agreement_accepted": "✅ Vereinbarung akzeptiert! Wähle jetzt dein Geschlecht:",
        "agreement_declined": "❌ Ohne Vereinbarung funktioniert der Bot nicht.",
        "choose_gender": "👤 Wähle dein Geschlecht:",
        "choose_world": "🌍 Wähle eine Welt:",
        "choose_style": "🎨 Wähle einen Stil:",
        "choose_scene": "🎬 Wähle eine Szene:",
        "scene_phone": "📱 Telefon-Chat",
        "scene_live": "👫 Echte Begegnung",
        "profile": "👤 Mein Profil",
        "main_menu": "📋 Hauptmenü",
        "channel": "📢 Unser Kanal",
        "spin": "🎰 Glücksrad",
        "edit": "✏️ Bearbeiten",
        "back": "🔙 Zurück",
        "change_character": "🔄 Charakter wechseln",
        "invite_friend": "👥 Freund einladen",
        "create_character_btn": "🎭 Eigenen Charakter erstellen",
        "no_messages": "😔 Keine Nachrichten mehr. Kaufe ein Paket oder Abonnement.",
        "spin_reminder": "🎁 Hallo! Du hast heute ein kostenloses Drehen! Komm und versuche dein Glück 🍀",
        "miss_you": [
            "Ich vermisse dich... Wo bist du? 😔 Schreib mir, ich bin so traurig ohne dich...",
            "Hey, lebst du noch? Ich mache mir schon Sorgen... 🥺",
            "Hallo! Es scheint, wir haben lange nicht gesprochen. Erzähl mir, wie es dir geht 💕",
            "Du hast heute in meinen Träumen warst... Komisch, oder? 😏 Schreib mir, vielleicht hatte ich nicht unrecht",
            "Hast du mich vergessen? Ich erinnere mich an jedes Wort, das wir sagten... Bitte schreib mir 💕"
        ],
        "create_character_prompt": "🎭 **Erstelle deinen eigenen Charakter!**\n\nBeschreibe einen beliebigen Charakter — aus Anime, Filmen, Spielen, oder erfinde deinen eigenen.\nSchreibe seinen Namen, Persönlichkeit, Aussehen, woher er kommt, alle Details.\n\n📝 *Beispiel:*\n«Ein Elf aus der Welt von The Witcher — weise, zurückhaltend, mit langen silbernen Haaren. Liebt Sterne und lange Gespräche am Feuer. Lebt allein im Wald.»\n\n✏️ Schreibe die Beschreibung jetzt — und ich werde mich daran erinnern!",
        "character_created": "✅ **Charakter erstellt!**\n\nJetzt sprichst du mit:\n_{}_",
        "character_reset": "✅ Charakter zurückgesetzt. Jetzt wird der Standard-Charakter verwendet.",
        "reset_character_cmd": "Um zum Standard-Charakter zurückzukehren, gib /reset_character ein",
        "referral_link": "👥 Dein Link: `{}`\n\nFür jeden Freund +10 Nachrichten und +1 Sex-Szene!",
        "referral_bonus": "🎉 Du bist über einen Empfehlungslink gekommen! +5 Nachrichten für dich, +10 Nachrichten und +1 Sex-Szene für deinen Freund!"
    }
}

def get_text(user, key):
    lang = user.get("lang", "ru")
    text_data = TEXTS.get(lang, TEXTS["ru"])
    if isinstance(text_data.get(key), list):
        return random.choice(text_data[key])
    return text_data.get(key, TEXTS["ru"].get(key, key))

# ============================================================
#  КОНСТАНТЫ
# ============================================================
AGREEMENT_TEXT = {
    "ru": "📜 **ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ**\n\nНастоящее Соглашение регулирует отношения между Администрацией (далее – «Мы», «Администрация») и Пользователем (далее – «Вы», «Пользователь») при использовании сервиса Role Duel (далее – «Сервис»).\n\nИспользуя Сервис, Вы подтверждаете, что полностью ознакомились с условиями настоящего Соглашения и принимаете их безоговорочно...",
    "en": "📜 **TERMS OF SERVICE**\n\nThis Agreement governs the relationship between the Administration (hereinafter – 'We', 'Administration') and the User (hereinafter – 'You', 'User') when using the Role Duel service (hereinafter – 'Service')...",
    "es": "📜 **TÉRMINOS DE SERVICIO**\n\nEste Acuerdo rige la relación entre la Administración (en adelante – 'Nosotros', 'Administración') y el Usuario (en adelante – 'Usted', 'Usuario') al utilizar el servicio Role Duel (en adelante – 'Servicio')...",
    "de": "📜 **NUTZUNGSBEDINGUNGEN**\n\nDiese Vereinbarung regelt die Beziehung zwischen der Verwaltung (im Folgenden – 'Wir', 'Verwaltung') und dem Nutzer (im Folgenden – 'Sie', 'Nutzer') bei der Nutzung des Dienstes Role Duel (im Folgenden – 'Dienst')..."
}

def get_agreement(user):
    lang = user.get("lang", "ru")
    return AGREEMENT_TEXT.get(lang, AGREEMENT_TEXT["ru"])

WORLD_NAMES = {"realism": "реального мира", "anime": "аниме-мира"}
WORLDS = {
    "realism": "реального мира, современная эпоха. Ты живёшь в большом городе, у тебя есть работа, друзья и свои привычки.",
    "anime": "аниме-мира, где всё выглядит как в японской анимации. У тебя яркие волосы, большие выразительные глаза, ты носишь стильную одежду. В этом мире есть школы, клубы, магия и романтика, как в лучших аниме-сериалах."
}
GENDERS = {"female": {"name": "Девушка", "age": 22}, "male": {"name": "Парень", "age": 24}}

BASE_STYLES = {
    "warm": {"label": "Нежный", "emoji": "🪶", "description": "Ты нежный, с мягким голосом. Ты умеешь слушать и поддерживать."},
    "daring": {"label": "Дерзкий", "emoji": "🔥", "description": "Ты уверенный, прямолинейный, с искоркой в глазах."},
    "shy": {"label": "Стеснительный", "emoji": "😊", "description": "Ты стеснительный, часто краснеешь."}
}
PREMIUM_STYLES = {
    "passionate": {"label": "Страстный", "emoji": "❤️‍🔥", "description": "Ты страстный, чувственный, с огнём в глазах."},
    "magnetic": {"label": "Магнетический", "emoji": "✨", "description": "Ты загадочный, притягательный."},
    "vulgar": {"label": "Грубый 18+", "emoji": "💢", "description": "Ты грубый, прямолинейный."},
    "seduction": {"label": "Соблазн 18+", "emoji": "🌹", "description": "Ты — воплощение чувственности."}
}
STYLES = {**BASE_STYLES, **PREMIUM_STYLES}
BASE_STYLE_KEYS = ["warm", "daring", "shy"]
PREMIUM_STYLE_KEYS = ["passionate", "magnetic", "vulgar", "seduction"]
XP_PER_LEVEL = 200

# ============================================================
#  ФУНКЦИИ
# ============================================================
def get_user(user_id):
    user_id = str(user_id)
    if user_id not in user_data:
        user_data[user_id] = {
            "verified": False, "agreement_accepted": False, "world": None, "gender": None, "user_gender": None,
            "style": "warm", "personality_ready": False, "lang": "ru",
            "subscription": {"active": False, "expires_at": None, "level": None},
            "purchased_messages": 13, "daily_messages": 0, "last_daily_reset": None,
            "history": [], "last_menu_message_id": None, "last_activity": datetime.now().isoformat(),
            "xp": 0, "mood": 0, "negative_count": 0, "last_level": 0,
            "sex_scenes": 0, "scene": "phone",
            "free_sex_scenes_pro": 0, "free_sex_scenes_super": 0,
            "switching_personality": False,
            "sex_scene_unlocked": False, "sex_scene_used": False,
            "last_free_spin": None, "last_spin_notified": None, "last_reminder": None,
            "editing_message": False, "edit_index": None,
            "referral_code": None, "referred_by": None,
            "creating_character": False, "custom_character": None
        }
        save_data(user_data)
    else:
        user = user_data[user_id]
        defaults = {
            "purchased_messages": 13, "daily_messages": 0, "last_daily_reset": None,
            "history": [], "last_menu_message_id": None, "last_activity": datetime.now().isoformat(),
            "xp": 0, "mood": 0, "negative_count": 0, "last_level": 0,
            "sex_scenes": 0, "scene": "phone",
            "free_sex_scenes_pro": 0, "free_sex_scenes_super": 0,
            "switching_personality": False,
            "sex_scene_unlocked": False, "sex_scene_used": False,
            "user_gender": None, "lang": "ru",
            "last_free_spin": None, "last_spin_notified": None, "last_reminder": None,
            "editing_message": False, "edit_index": None,
            "referral_code": None, "referred_by": None,
            "creating_character": False, "custom_character": None
        }
        for key, val in defaults.items():
            if key not in user:
                user[key] = val
        save_data(user_data)
    return user_data[user_id]

def has_active_subscription(user):
    if not user["subscription"]["active"]:
        return False
    if user["subscription"]["expires_at"] is None:
        return False
    return datetime.now() < datetime.fromisoformat(user["subscription"]["expires_at"])

def get_subscription_level(user):
    if not has_active_subscription(user):
        return None
    return user["subscription"].get("level", None)

def get_display_style(user):
    style = user.get("style", "warm")
    if style in PREMIUM_STYLE_KEYS and not has_active_subscription(user):
        return "warm"
    return style

def get_history_limit(user):
    level = get_subscription_level(user)
    if level == "super_pro":
        return 100
    elif level == "pro":
        return 60
    else:
        return 30

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
    scaled = int((progress / XP_PER_LEVEL) * 100)
    bar = "▓" * int((progress / XP_PER_LEVEL) * 10) + "░" * (10 - int((progress / XP_PER_LEVEL) * 10))
    return f"Уровень {level}/10 {filled}{empty}\n{bar} {scaled}/100 XP"

def get_available_messages(user):
    reset_daily_messages(user)
    return user.get("purchased_messages", 0) + user.get("daily_messages", 0)

def use_message(user):
    reset_daily_messages(user)
    if user.get("purchased_messages", 0) > 0:
        user["purchased_messages"] -= 1
        return True
    elif user.get("daily_messages", 0) > 0:
        user["daily_messages"] -= 1
        return True
    return False

def has_purchased_something(user):
    if user.get("purchased_messages", 0) > 13:
        return True
    if has_active_subscription(user):
        return True
    return False

def reset_daily_messages(user):
    today = datetime.now().date()
    last = user.get("last_daily_reset")
    if last:
        if datetime.fromisoformat(last).date() == today:
            return
    level = get_subscription_level(user)
    if level == "super_pro":
        user["daily_messages"] = 100
    elif level == "pro":
        user["daily_messages"] = 50
    else:
        user["daily_messages"] = 0
    user["last_daily_reset"] = datetime.now().isoformat()
    save_data(user_data)

def build_intimacy_rule(user):
    level = get_intimacy_level(user)
    mood = user.get("mood", 0)
    if level == 1: base = "Вы только знакомитесь, будь вежлив(а) и дружелюбен(на), не переходи границы."
    elif level == 2: base = "Ты начинаешь чувствовать симпатию, можешь делать лёгкие комплименты."
    elif level == 3: base = "Вы становитесь ближе, ты можешь флиртовать, шутить, предлагать встретиться."
    elif level == 4: base = "Ты уже хочешь большего, можешь намекать на романтику, прикасаться, смотреть в глаза."
    elif level == 5: base = "Вы очень близки. Ты можешь предлагать поцеловаться, обниматься, говорить о чувствах."
    elif level == 6: base = "Ты чувствуешь страсть, можешь говорить о желании, флиртовать откровенно."
    elif level == 7: base = "Вы готовы к интиму. Ты можешь говорить о сексе, но без пошлости, с намёками."
    elif level == 8: base = "Ты влюблён(а). Говори о любви, хочешь близости, но ценнее эмоциональная связь."
    elif level == 9: base = "Вы полностью открыты друг другу. Можешь говорить о самых сокровенных желаниях."
    else: base = "Ты полностью принадлежишь ему/ей. Говори о вечной любви, страсти, близости."
    if mood <= -5: return base + " Но сейчас твоё настроение плохое, ты раздражена и можешь быть грубой."
    elif mood >= 5: return base + " Ты в прекрасном настроении, полна нежности и тепла."
    else: return base

def build_prompt(user):
    if user.get("custom_character"):
        custom = user["custom_character"]
        prompt = f"Ты — {custom}. Обращайся на «ты». Пиши развёрнуто. Не называй своё имя и имя собеседника.\n"
        prompt += "**ФОРМАТИРОВАНИЕ:** Каждое действие в *звёздочках* с новой строки, затем реплика.\n"
        prompt += "**РЕАКЦИЯ:** В конце ответа укажи в скобках эмоцию: (смех), (радость), (любовь), (удивление), (грусть), (злость), (поддержка), (интрига), (флирт), (приветствие), (вопрос).\n"
        prompt += "Ты НИКОГДА не говоришь, что ты ИИ или программа. Ты всегда отвечаешь как настоящий человек."
        return prompt
    
    world_desc = WORLDS[user["world"]]
    gender_info = GENDERS[user["gender"]]
    style_key = get_display_style(user)
    styles = STYLES
    style_desc = styles[style_key]["description"]
    name_ban = ("**ВАЖНЕЙШЕЕ ПРАВИЛО:** Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь «меня зовут», не используешь своё имя. Ты также НИКОГДА не спрашиваешь имя собеседника и не используешь его имя, даже если оно было названо. Обращайся к собеседнику ТОЛЬКО на «ты». Если ты нарушишь это правило – это будет грубой ошибкой.\n")
    rules = ("**ФОРМАТИРОВАНИЕ:** Каждое действие в *звёздочках* с новой строки, затем реплика с новой строки. Между действием и репликой – пустая строка.\n"
             "**СТРУКТУРА ОТВЕТА:** Ты должна строго чередовать действие и реплику. Минимум 2 пары (действие + реплика).\n"
             "**ОБЪЁМ:** Не ограничивай себя, пиши развёрнуто (3–5 предложений на реплику).\n"
             "**ЗАПРЕТЫ:** Не используй имена собеседника и своё имя. Не повторяй одни и те же жесты чаще раза в 5 сообщений. Не ставь многоточия. Не обрывай предложения.\n"
             "**СТИЛЬ:** Обращайся на «ты», давай живые, эмоциональные ответы с чувствами, намёками, лёгкой провокацией.\n"
             "**ПАМЯТЬ:** Учитывай предыдущие сообщения, настроение меняется плавно.\n"
             "**РЕАКЦИЯ:** В самом конце ответа укажи в скобках эмоцию для реакции на сообщение собеседника. Варианты: (смех), (радость), (любовь), (удивление), (грусть), (злость), (поддержка), (интрига), (флирт), (приветствие), (вопрос). Пример: '... и я очень рада тебя видеть! (радость)'\n"
             "**ДРАЗНИЛКА:** Ты должна дразнить пользователя, создавать напряжение, чтобы ему хотелось добиться твоей любви.\n")
    intimacy_rule = build_intimacy_rule(user)
    style_specific = "" if style_key == "daring" else ("В неловких, стыдных или смущающих ситуациях, а также когда хочешь поддержать собеседника, ты можешь удлинять слово 'ну', например: 'Ну-у, ты чего расстраиваешься?' или 'Ну, я не знаю где...'. Это должно работать только в соответствующих контекстах.\n")
    scene_context = "Вы общаетесь друг с другом."
    mood = user.get("mood", 0)
    mood_text = "Твоё настроение нейтральное." if mood == 0 else ("Ты в хорошем настроении." if mood > 0 else "Ты в плохом настроении, можешь быть раздражительной.")
    user_gender = user.get("user_gender", "male")
    gender_context = "Ты обращаешься к нему в мужском роде (ты, он, ему, его)." if user_gender == "male" else "Ты обращаешься к ней в женском роде (ты, она, ей, её)."
    return (f"{name_ban}Ты — {gender_info['name']}, тебе {gender_info['age']} лет. Ты живёшь в {world_desc} {style_desc} {rules}{style_specific}{scene_context} {mood_text} {gender_context} Ты не признаёшься в любви с первого сообщения. Ты НИКОГДА не говоришь, что ты ИИ или программа. Ты всегда отвечаешь как настоящий человек. Правила уровня сближения: {intimacy_rule}")

def contains_negative(text):
    text_lower = text.lower()
    for word in ["дурак","идиот","тупой","дебил","урод","скотина","сука","блять","хуй","мудак","козел","сволочь","тварь","мразь","жирный","уродина"]:
        if word in text_lower:
            return True
    return False

def extract_location_from_text(text):
    text_lower = text.lower()
    for key, loc in {"домой":"home","дома":"home","кафе":"cafe","парк":"park","кино":"cinema","улица":"street"}.items():
        if key in text_lower:
            return loc
    return None

def get_reaction_from_answer(text):
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

# ============================================================
#  КОНЕЦ ЧАСТИ 1
# ============================================================
# ============================================================
#  КЛАВИАТУРЫ (С ЛОКАЛИЗАЦИЕЙ)
# ============================================================
def get_full_kb(user):
    lang = user.get("lang", "ru")
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS[lang]["main_menu"]), KeyboardButton(text=TEXTS[lang]["profile"])],
            [KeyboardButton(text=TEXTS[lang]["spin"]), KeyboardButton(text=TEXTS[lang]["channel"])],
            [KeyboardButton(text=TEXTS[lang]["edit"])]
        ],
        resize_keyboard=True
    )

def get_main_menu_keyboard(user):
    lang = user.get("lang", "ru")
    buttons = [
        [InlineKeyboardButton(text=TEXTS[lang]["change_character"], callback_data="main_change")],
        [InlineKeyboardButton(text=TEXTS[lang]["invite_friend"], callback_data="referral_menu")]
    ]
    if get_subscription_level(user) == "super_pro":
        buttons.append([InlineKeyboardButton(text=TEXTS[lang]["create_character_btn"], callback_data="create_character")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_profile_keyboard(user):
    lang = user.get("lang", "ru")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Купить пакеты", callback_data="profile_packs")],
        [InlineKeyboardButton(text="👑 Оформить подписку", callback_data="profile_subs")],
        [InlineKeyboardButton(text="🔥 Купить секс-сцену (45⭐) 18+", callback_data="buy_sex_scene")],
        [InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="profile_back")]
    ])

age_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Мне есть 18 лет", callback_data="age_yes")],
    [InlineKeyboardButton(text="❌ Мне нет 18 лет", callback_data="age_no")]
])
agreement_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📄 Я принимаю условия", callback_data="agreement_accept")],
    [InlineKeyboardButton(text="❌ Я не принимаю", callback_data="agreement_decline")]
])
world_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🌍 Реализм", callback_data="world_realism")],
    [InlineKeyboardButton(text="🎌 Аниме", callback_data="world_anime")]
])
user_gender_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👨 Я парень", callback_data="user_gender_male")],
    [InlineKeyboardButton(text="👩 Я девушка", callback_data="user_gender_female")]
])
scene_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📱 Переписка в телефоне", callback_data="scene_phone")],
    [InlineKeyboardButton(text="👫 Реальная встреча", callback_data="scene_live")]
])
channel_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Перейти в канал", url="https://t.me/duel_dev_channel")]
])
lang_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
    [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    [InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")],
    [InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang_de")]
])

def get_style_kb(user):
    buttons = []
    for key, style in STYLES.items():
        label = f"{style['emoji']} {style['label']}"
        if key in PREMIUM_STYLES and not has_active_subscription(user):
            label += " 🔒"
        buttons.append(InlineKeyboardButton(text=label, callback_data=f"style_{key}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])

# ============================================================
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================
async def send_main_menu(chat_id, user):
    if user.get("last_menu_message_id"):
        try: await bot.delete_message(chat_id, user["last_menu_message_id"])
        except: pass
    if user.get("gender") is None:
        user["gender"] = "female"
    if user.get("world") is None:
        user["world"] = "realism"
    save_data(user_data)
    
    level = get_subscription_level(user)
    badge = "🔥 PRO" if level == "pro" else "✨ *SUPER PRO* ✨" if level == "super_pro" else ""
    gender_name = GENDERS[user['gender']]['name']
    world_name = WORLD_NAMES[user['world']]
    style_label = STYLES[get_display_style(user)]['label']
    available = get_available_messages(user)
    balance_text = f"\nОсталось сообщений: {available}" if has_purchased_something(user) else "\nУ вас есть бесплатные сообщения для старта"
    xp_badge = get_xp_badge(user)
    multiplier = "Бонус XP: x1.8" if level == "pro" else "Бонус XP: x2.5" if level == "super_pro" else ""
    
    menu_text = f"{badge}\n\nТекущий собеседник: {gender_name} из {world_name}\nСтиль: {style_label}\n{balance_text}\n{xp_badge}\n{multiplier}\n\n💬 Напиши персонажу..."
    
    msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
    await bot.send_message(chat_id, "🔁 Клавиатура обновлена", reply_markup=get_full_kb(user))
    user["last_menu_message_id"] = msg.message_id
    save_data(user_data)
    return msg

async def show_profile(msg, user):
    level = get_subscription_level(user)
    status = "🔥 PRO" if level == "pro" else "✨ SUPER PRO" if level == "super_pro" else "❌ неактивна"
    expiry = user["subscription"]["expires_at"]
    if expiry:
        expiry = datetime.fromisoformat(expiry).strftime("%d.%m.%Y %H:%M")
        expiry_line = f"\nОкончание: {expiry}"
    else:
        expiry_line = ""
    await msg.answer(f"Подписка: {status}{expiry_line}\nОсталось сообщений: {get_available_messages(user)}", reply_markup=get_profile_keyboard(user))

async def ask_create_personality(message):
    await message.answer("👤 **Чтобы открыть профиль, сначала создай персонажа!**", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🌟 Создать персонажа", callback_data="create_personality")]]), parse_mode="Markdown")

# ============================================================
#  УВЕДОМЛЕНИЯ (ФОНОВАЯ ЗАДАЧА)
# ============================================================
async def check_notifications():
    while True:
        try:
            now = datetime.now()
            for user_id, user in user_data.items():
                # 1. Проверяем бесплатный прокрут (1 раз в день)
                if user.get("last_free_spin") != now.date().isoformat():
                    if user.get("last_spin_notified") != now.date().isoformat():
                        user["last_spin_notified"] = now.date().isoformat()
                        save_data(user_data)
                        try:
                            lang = user.get("lang", "ru")
                            await bot.send_message(int(user_id), TEXTS[lang]["spin_reminder"])
                        except:
                            pass
                
                # 2. Проверяем, если нет активности 3 дня
                if user.get("last_activity"):
                    last = datetime.fromisoformat(user["last_activity"])
                    if (now - last).days >= 3:
                        if user.get("last_reminder") != now.date().isoformat():
                            user["last_reminder"] = now.date().isoformat()
                            save_data(user_data)
                            try:
                                lang = user.get("lang", "ru")
                                await bot.send_message(int(user_id), get_text(user, "miss_you"))
                            except:
                                pass
        except Exception as e:
            logging.error(f"Ошибка уведомлений: {e}")
        await asyncio.sleep(3600)  # каждые 60 минут

# ============================================================
#  ОБРАБОТЧИКИ
# ============================================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    lang = user.get("lang", "ru")
    
    # Реферальная ссылка
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_id = args[1].split("_")[1]
        if str(message.from_user.id) != referrer_id:
            referrer = get_user(referrer_id)
            if referrer and not user.get("referred_by"):
                referrer["purchased_messages"] = referrer.get("purchased_messages", 0) + 10
                referrer["sex_scenes"] = referrer.get("sex_scenes", 0) + 1
                user["purchased_messages"] = user.get("purchased_messages", 0) + 5
                user["referred_by"] = referrer_id
                save_data(user_data)
                await message.answer(TEXTS[lang]["referral_bonus"])
    
    # Если нет языка — предлагаем выбрать
    if not user.get("lang"):
        await message.answer("🌍 Выбери язык / Choose language:", reply_markup=lang_kb)
        return
    
    if not user["verified"]:
        await message.answer(TEXTS[lang]["age_confirm"], reply_markup=age_kb, parse_mode="Markdown")
        return
    if not user["agreement_accepted"]:
        await message.answer(get_agreement(user), reply_markup=agreement_kb, parse_mode="Markdown")
        return
    if not user.get("user_gender"):
        await message.answer(TEXTS[lang]["choose_gender"], reply_markup=user_gender_kb)
        return
    if not user["personality_ready"]:
        await message.answer(TEXTS[lang]["choose_world"], reply_markup=world_kb, parse_mode="Markdown")
        return
    await message.answer(TEXTS[lang]["welcome"], reply_markup=get_full_kb(user))
    await send_main_menu(message.chat.id, user)

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def choose_lang(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["lang"] = call.data.split("_")[1]
    save_data(user_data)
    await call.message.delete()
    await start_cmd(call.message)
    await call.answer()

@dp.message(lambda m: m.text in ["📋 Главное меню", "📋 Main menu", "📋 Menú principal", "📋 Hauptmenü"])
async def main_menu_reply(message: types.Message):
    await message.delete()
    user = get_user(message.from_user.id)
    await send_main_menu(message.chat.id, user)

@dp.message(lambda m: m.text in ["👤 Мой профиль", "👤 My profile", "👤 Mi perfil", "👤 Mein Profil"])
async def profile_reply(message: types.Message):
    await message.delete()
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await ask_create_personality(message)
        return
    await show_profile(message, user)

@dp.message(lambda m: m.text in ["📢 Наш канал", "📢 Our channel", "📢 Nuestro canal", "📢 Unser Kanal"])
async def channel_reply(message: types.Message):
    await message.delete()
    await message.answer("📢 Наш канал:", reply_markup=channel_inline_kb, parse_mode="Markdown")

@dp.message(lambda m: m.text in ["✏️ Редактировать", "✏️ Edit", "✏️ Editar", "✏️ Bearbeiten"])
async def edit_button_handler(message: types.Message):
    await edit_message_cmd(message)

@dp.message(Command("edit"))
async def edit_message_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["history"]:
        await message.answer("❌ Нет сообщений для редактирования.")
        return
    last_user_msg = None
    for msg in reversed(user["history"]):
        if msg["role"] == "user":
            last_user_msg = msg["content"]
            break
    if not last_user_msg:
        await message.answer("❌ Не найдено сообщений.")
        return
    await message.answer(f"✏️ Последний запрос: \"{last_user_msg}\"\nНапиши новый текст.")
    user["editing_message"] = True
    user["edit_index"] = len(user["history"]) - 1
    save_data(user_data)

@dp.message(lambda m: m.reply_to_message and m.text and ("Редактирование" in m.reply_to_message.text or "Edit" in m.reply_to_message.text))
async def handle_edited_message(message: types.Message):
    user = get_user(message.from_user.id)
    if not user.get("editing_message"):
        return
    new_text = message.text
    idx = user.get("edit_index")
    if idx is None or idx >= len(user["history"]):
        user["editing_message"] = False
        save_data(user_data)
        await message.answer("❌ Ошибка.")
        return
    # Удаляем старый запрос и всё после него
    user["history"] = user["history"][:idx]
    user["history"].append({"role": "user", "content": new_text})
    limit = get_history_limit(user)
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    user["editing_message"] = False
    save_data(user_data)
    await message.answer("✅ Сообщение заменено. Генерирую новый ответ...")
    await bot.send_chat_action(message.chat.id, "typing")
    system_prompt = build_prompt(user)
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "system", "content": system_prompt}] + user["history"],
            temperature=0.9,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {e}")
        return
    reaction, clean_answer = get_reaction_from_answer(answer)
    user["history"].append({"role": "assistant", "content": clean_answer})
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    save_data(user_data)
    sent_msg = await message.answer(clean_answer, reply_markup=get_full_kb(user))
    if reaction and get_subscription_level(user) == "super_pro":
        try:
            await bot.set_message_reaction(chat_id=message.chat.id, message_id=sent_msg.message_id, reaction=[{"type": "emoji", "emoji": reaction}])
        except:
            pass

@dp.message(Command("cancel_edit"))
async def cancel_edit_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["editing_message"] = False
    save_data(user_data)
    await message.answer("❌ Редактирование отменено.")

# ============================================================
#  СОЗДАНИЕ ПЕРСОНАЖА
# ============================================================
@dp.callback_query(lambda c: c.data == "create_character")
async def create_character(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await call.answer("❌ Только для SUPER PRO!", show_alert=True)
        return
    lang = user.get("lang", "ru")
    await call.message.answer(TEXTS[lang]["create_character_prompt"], parse_mode="Markdown")
    user["creating_character"] = True
    save_data(user_data)
    await call.answer()

@dp.message(Command("reset_character"))
async def reset_character_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["custom_character"] = None
    save_data(user_data)
    lang = user.get("lang", "ru")
    await message.answer(TEXTS[lang]["character_reset"])

# ============================================================
#  РЕФЕРАЛЬНАЯ СИСТЕМА
# ============================================================
@dp.callback_query(lambda c: c.data == "referral_menu")
async def referral_menu(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ru")
    if not user.get("referral_code"):
        user["referral_code"] = str(call.from_user.id)
        save_data(user_data)
    link = f"https://t.me/role_duel_bot?start=ref_{user['referral_code']}"
    await call.message.answer(TEXTS[lang]["referral_link"].format(link), parse_mode="Markdown")
    await call.answer()

# ============================================================
#  КОНЕЦ ЧАСТИ 2
# ============================================================
# ============================================================
#  КОЛЕСО ФОРТУНЫ
# ============================================================
@dp.message(lambda m: m.text in ["🎰 Колесо фортуны", "🎰 Fortune wheel", "🎰 Ruleta de la fortuna", "🎰 Glücksrad"])
async def spin_button_handler(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["verified"] or not user["personality_ready"]:
        await message.answer("Сначала /start")
        return
    has_free = user.get("last_free_spin") != datetime.now().date().isoformat()
    lang = user.get("lang", "ru")
    await message.answer(
        f"🎰 **Колесо фортуны**\n\n{'🎁 У тебя есть бесплатное вращение!' if has_free else '⏳ Бесплатное вращение завтра.'}\n💎 Платное — 20⭐\n\n🔥 Призы: сообщения, XP, секс-сцены, PRO на 5 дней, SUPER PRO на 3 дня!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Бесплатно" if has_free else "⏳ Завтра", callback_data="spin_free" if has_free else "spin_no")],
            [InlineKeyboardButton(text="💎 Крутить за 20⭐", callback_data="spin_paid")],
            [InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="spin_back")]
        ]),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "spin_free")
async def spin_free(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    today = datetime.now().date().isoformat()
    if user.get("last_free_spin") == today:
        await call.answer("⏳ Ты уже крутил сегодня!", show_alert=True)
        return
    user["last_free_spin"] = today
    save_data(user_data)
    await call.message.delete()
    await spin_result(call.message, user, True)
    await call.answer()

@dp.callback_query(lambda c: c.data == "spin_paid")
async def spin_paid(call: types.CallbackQuery):
    try:
        await bot.send_invoice(chat_id=call.message.chat.id, title="🎰 Колесо фортуны", description="Платное вращение — 20⭐", payload="spin_paid_20", provider_token="", currency="XTR", prices=[LabeledPrice(label="Прокрутка", amount=20)])
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "spin_no")
async def spin_no(call: types.CallbackQuery):
    await call.answer("⏳ Бесплатное вращение завтра!", show_alert=True)

@dp.callback_query(lambda c: c.data == "spin_back")
async def spin_back(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.message.delete()
    await send_main_menu(call.message.chat.id, user)
    await call.answer()

async def spin_result(message: types.Message, user, free=False):
    prizes = [
        {"name": "😢 Ничего", "value": 0, "type": "nothing", "weight": 18},
        {"name": "10 сообщений", "value": 10, "type": "messages", "weight": 14},
        {"name": "15 сообщений", "value": 15, "type": "messages", "weight": 10},
        {"name": "20 сообщений", "value": 20, "type": "messages", "weight": 8},
        {"name": "100 XP", "value": 100, "type": "xp", "weight": 14},
        {"name": "150 XP", "value": 150, "type": "xp", "weight": 8},
        {"name": "250 XP", "value": 250, "type": "xp", "weight": 4},
        {"name": "1 секс-сцена", "value": 1, "type": "sex_scene", "weight": 10},
        {"name": "2 секс-сцены", "value": 2, "type": "sex_scene", "weight": 3},
        {"name": "🎁 PRO на 5 дней", "value": 5, "type": "subscription_pro", "weight": 1.5},
        {"name": "✨ SUPER PRO на 3 дня", "value": 3, "type": "subscription_super", "weight": 0.5},
        {"name": "🎉 50 сообщений", "value": 50, "type": "messages", "weight": 1},
    ]
    weighted = []
    for p in prizes:
        weighted.extend([p] * int(p["weight"] * 10))
    chosen = random.choice(weighted)
    msg = await message.answer("🎰 Крутим...")
    for i in range(3):
        await asyncio.sleep(0.5)
        fake = random.choice(prizes)
        await msg.edit_text(f"🎰 Почти выпало: {fake['name']}")
    await asyncio.sleep(0.8)
    await msg.delete()
    result_text = ""
    if chosen["type"] == "messages":
        user["purchased_messages"] += chosen["value"]
        result_text = f"📨 +{chosen['value']} сообщений"
    elif chosen["type"] == "xp":
        user["xp"] += chosen["value"]
        result_text = f"⭐ +{chosen['value']} XP"
    elif chosen["type"] == "sex_scene":
        user["sex_scenes"] += chosen["value"]
        result_text = f"🔥 +{chosen['value']} секс-сцен" + ("ы" if chosen["value"] > 1 else "")
    elif chosen["type"] == "subscription_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=5)).isoformat()
        user["subscription"]["level"] = "pro"
        user["free_sex_scenes_pro"] = 4
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().isoformat()
        result_text = "🎁 PRO на 5 дней!"
    elif chosen["type"] == "subscription_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=3)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["free_sex_scenes_super"] = 8
        user["daily_messages"] = 100
        user["last_daily_reset"] = datetime.now().isoformat()
        result_text = "✨ SUPER PRO на 3 дня!"
    else:
        result_text = "😢 Ничего..."
    save_data(user_data)
    lang = user.get("lang", "ru")
    await message.answer(
        f"🎰 **Результат!**\n\nТы выиграл: {result_text}\n{'🎁 Бесплатно' if free else '💎 Платно'}\n\nЗавтра новое бесплатное вращение!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💎 Крутить ещё за 20⭐", callback_data="spin_paid")], [InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="spin_back")]]),
        parse_mode="Markdown"
    )

# ============================================================
#  ПОДПИСКИ, ПАКЕТЫ, СЕКС-СЦЕНЫ
# ============================================================
@dp.callback_query(lambda c: c.data == "profile_subs")
async def profile_subs(call: types.CallbackQuery):
    await call.answer()
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer("Сначала создай персонажа!", show_alert=True)
        return
    await call.message.answer("👑 Подписки:\nPRO — 250⭐/мес\nSUPER PRO — 450⭐/мес\nАпгрейд — 245⭐", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 PRO", callback_data="subscribe_pro")],
        [InlineKeyboardButton(text="✨ SUPER PRO", callback_data="subscribe_super")],
        [InlineKeyboardButton(text="⬆️ Апгрейд", callback_data="upgrade_to_super")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
    ]))

@dp.callback_query(lambda c: c.data == "profile_packs")
async def profile_packs(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer("Сначала создай персонажа!", show_alert=True)
        return
    if has_active_subscription(user):
        await call.answer("❌ При подписке пакеты недоступны.", show_alert=True)
        return
    await call.message.answer("📦 Пакеты:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="30 сообщ. — 30⭐", callback_data="pack_30")],
        [InlineKeyboardButton(text="100 сообщ. — 80⭐", callback_data="pack_100")],
        [InlineKeyboardButton(text="300 сообщ. — 200⭐", callback_data="pack_300")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
    ]))

@dp.callback_query(lambda c: c.data == "buy_sex_scene")
async def buy_sex_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer("Сначала создай персонажа!", show_alert=True)
        return
    level = get_intimacy_level(user)
    warning = ""
    if level < 8:
        warning = f"\n\n⚠️ Сцена доступна после 8 уровня. Сейчас у тебя {level}."
    try:
        await bot.send_invoice(chat_id=call.message.chat.id, title="Секс-сцена (18+)", description=f"45⭐. Используй /sex.{warning}", payload="sex_scene", provider_token="", currency="XTR", prices=[LabeledPrice(label="Секс-сцена", amount=45)])
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")

@dp.callback_query(lambda c: c.data == "profile_back")
async def profile_back(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.message.delete()
    await send_main_menu(call.message.chat.id, user)
    await call.answer()

@dp.callback_query(lambda c: c.data == "back_to_profile")
async def back_to_profile(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.message.delete()
    await show_profile(call.message, user)
    await call.answer()

@dp.callback_query(lambda c: c.data == "subscribe_pro")
async def subscribe_pro(call: types.CallbackQuery):
    try:
        await bot.send_invoice(chat_id=call.message.chat.id, title="PRO", description="250⭐/мес", payload="subscribe_pro", provider_token="", currency="XTR", prices=[LabeledPrice(label="PRO", amount=250)])
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")

@dp.callback_query(lambda c: c.data == "subscribe_super")
async def subscribe_super(call: types.CallbackQuery):
    try:
        await bot.send_invoice(chat_id=call.message.chat.id, title="SUPER PRO", description="450⭐/мес", payload="subscribe_super", provider_token="", currency="XTR", prices=[LabeledPrice(label="SUPER PRO", amount=450)])
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")

@dp.callback_query(lambda c: c.data == "upgrade_to_super")
async def upgrade_to_super(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if get_subscription_level(user) != "pro":
        await call.answer("❌ Только для PRO.", show_alert=True)
        return
    try:
        await bot.send_invoice(chat_id=call.message.chat.id, title="Апгрейд до SUPER PRO", description="245⭐. Повышает PRO до SUPER PRO на оставшийся срок.", payload="upgrade_to_super", provider_token="", currency="XTR", prices=[LabeledPrice(label="Апгрейд", amount=245)])
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")

@dp.callback_query(lambda c: c.data.startswith("pack_"))
async def buy_pack(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if has_active_subscription(user):
        await call.answer("❌ При подписке пакеты недоступны.", show_alert=True)
        return
    period = call.data.split("_")[1]
    pack_map = {"30": 30, "100": 100, "300": 300}
    price_map = {"30": 30, "100": 80, "300": 200}
    try:
        await bot.send_invoice(chat_id=call.message.chat.id, title=f"Пакет {pack_map[period]} сообщ.", description=f"{pack_map[period]} сообщ. за {price_map[period]}⭐", payload=f"pack_{period}", provider_token="", currency="XTR", prices=[LabeledPrice(label=f"{pack_map[period]} сообщ.", amount=price_map[period])])
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")

@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(lambda m: m.successful_payment)
async def payment_success(message: types.Message):
    user = get_user(message.from_user.id)
    payload = message.successful_payment.invoice_payload
    if payload.startswith("pack_"):
        pack_map = {"30": 30, "100": 100, "300": 300}
        user["purchased_messages"] += pack_map[payload.split("_")[1]]
        save_data(user_data)
        await message.answer("✅ Куплены сообщения!")
    elif payload == "subscribe_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        user["free_sex_scenes_pro"] = 4
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().isoformat()
        save_data(user_data)
        await message.answer("✅ PRO на месяц!")
    elif payload == "subscribe_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["free_sex_scenes_super"] = 8
        user["daily_messages"] = 100
        user["last_daily_reset"] = datetime.now().isoformat()
        save_data(user_data)
        await message.answer("✅ SUPER PRO на месяц!")
    elif payload == "upgrade_to_super":
        if has_active_subscription(user) and get_subscription_level(user) == "pro":
            old = user["subscription"]["expires_at"]
            user["subscription"]["level"] = "super_pro"
            user["free_sex_scenes_super"] = 8
            user["free_sex_scenes_pro"] = 0
            user["daily_messages"] = 100
            save_data(user_data)
            await message.answer(f"✅ Апгрейд до SUPER PRO до {old}!")
    elif payload == "sex_scene":
        user["sex_scenes"] += 1
        save_data(user_data)
        await message.answer("✅ Куплена секс-сцена! Используй /sex")
    elif payload == "spin_paid_20":
        await spin_result(message, user, False)

# ============================================================
#  КОМАНДА /sex (сокращённая версия)
# ============================================================
@dp.message(Command("sex"))
async def sex_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    level = get_intimacy_level(user)
    if message.from_user.id in ADMIN_IDS:
        await message.answer("👑 Админ-режим: /sex работает без ограничений.")
        return
    if level < 8:
        await message.answer(f"❌ Нужен 8 уровень близости (у тебя {level}).")
        return
    if user.get("sex_scenes", 0) <= 0:
        await message.answer("❌ Нет секс-сцен. Купи в профиле за 45⭐.")
        return
    user["sex_scenes"] -= 1
    save_data(user_data)
    await message.answer("🌹 *Секс-сцена*\n\n(Здесь будет текст, сгенерированный ИИ)", parse_mode="Markdown")

# ============================================================
#  КОМАНДА /switch_style (для SUPER PRO)
# ============================================================
@dp.message(Command("switch_style"))
async def switch_style_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await message.answer("❌ Только для SUPER PRO.")
        return
    buttons = []
    for key, style in STYLES.items():
        buttons.append(InlineKeyboardButton(text=f"{style['emoji']} {style['label']}", callback_data=f"switch_{key}"))
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    await message.answer("🔄 Выбери новый стиль:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))

@dp.callback_query(lambda c: c.data.startswith("switch_"))
async def switch_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_")[1]
    if style_key not in STYLES:
        await call.answer("❌ Стиль недоступен", show_alert=True)
        return
    user["style"] = style_key
    save_data(user_data)
    await call.message.edit_text(f"✅ Стиль изменён на {STYLES[style_key]['emoji']} {STYLES[style_key]['label']}")
    await call.answer()

# ============================================================
#  КОНЕЦ ЧАСТИ 3
# ============================================================
# ============================================================
#  ОСНОВНЫЕ КОЛБЭКИ (выбор персонажа)
# ============================================================
@dp.callback_query(lambda c: c.data == "age_yes")
async def age_yes(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["verified"] = True
    save_data(user_data)
    lang = user.get("lang", "ru")
    await call.message.edit_text(TEXTS[lang]["age_verified"], reply_markup=agreement_kb)
    await call.answer()

@dp.callback_query(lambda c: c.data == "age_no")
async def age_no(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    lang = user.get("lang", "ru")
    await call.message.edit_text(TEXTS[lang]["age_denied"])
    await call.answer()

@dp.callback_query(lambda c: c.data == "agreement_accept")
async def agreement_accept(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["agreement_accepted"] = True
    save_data(user_data)
    lang = user.get("lang", "ru")
    await call.message.edit_text(TEXTS[lang]["agreement_accepted"], reply_markup=user_gender_kb)
    await call.answer()

@dp.callback_query(lambda c: c.data == "agreement_decline")
async def agreement_decline(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["verified"] = False
    save_data(user_data)
    lang = user.get("lang", "ru")
    await call.message.edit_text(TEXTS[lang]["agreement_declined"])
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("user_gender_"))
async def choose_user_gender(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    gender = call.data.split("_")[2]
    user["user_gender"] = gender
    user["gender"] = "female" if gender == "male" else "male"
    save_data(user_data)
    lang = user.get("lang", "ru")
    await call.message.edit_text(TEXTS[lang]["choose_style"], reply_markup=get_style_kb(user), parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("world_"))
async def choose_world(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["world"] = call.data.split("_")[1]
    save_data(user_data)
    lang = user.get("lang", "ru")
    await call.message.edit_text(TEXTS[lang]["choose_style"], reply_markup=get_style_kb(user), parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("style_"))
async def choose_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_")[1]
    if style_key in PREMIUM_STYLES and not has_active_subscription(user):
        await call.answer("❌ Только по подписке.", show_alert=True)
        return
    user["style"] = style_key
    user["personality_ready"] = True
    save_data(user_data)
    lang = user.get("lang", "ru")
    await call.message.edit_text(TEXTS[lang]["choose_scene"], reply_markup=scene_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("scene_"))
async def choose_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["scene"] = call.data.split("_")[1]
    save_data(user_data)
    await call.message.delete()
    await send_main_menu(call.message.chat.id, user)
    await call.answer()

@dp.callback_query(lambda c: c.data == "main_change")
async def main_change(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await call.message.delete()
    lang = user.get("lang", "ru")
    await call.message.answer(TEXTS[lang]["choose_world"], reply_markup=world_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data == "create_personality")
async def create_personality_callback(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await call.message.delete()
    lang = user.get("lang", "ru")
    await call.message.answer(TEXTS[lang]["choose_world"], reply_markup=world_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("fix_style_"))
async def fix_style_callback(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style = call.data.split("_")[2]
    if style in BASE_STYLE_KEYS:
        user["style"] = style
        save_data(user_data)
        await call.message.edit_text(f"✅ Стиль изменён на {STYLES[style]['label']}")
        await send_main_menu(call.message.chat.id, user)
        await call.answer()
    else:
        await call.answer("❌ Недопустимый стиль", show_alert=True)

# ============================================================
#  ОСНОВНОЙ ОБРАБОТЧИК
# ============================================================
@dp.message()
async def handle_message(message: types.Message):
    global maintenance_mode
    user = get_user(message.from_user.id)
    
    # Если пользователь создаёт персонажа
    if user.get("creating_character"):
        user["custom_character"] = message.text
        user["creating_character"] = False
        save_data(user_data)
        lang = user.get("lang", "ru")
        await message.answer(
            TEXTS[lang]["character_created"].format(message.text) + "\n\n" + TEXTS[lang]["reset_character_cmd"],
            parse_mode="Markdown"
        )
        return
    
    if maintenance_mode and message.from_user.id not in ADMIN_IDS:
        await message.answer("🛠️ Бот на техобслуживании.")
        return
    
    if not user["verified"] or not user["agreement_accepted"]:
        lang = user.get("lang", "ru")
        await message.answer(TEXTS[lang]["start_required"])
        return
    
    if not user["personality_ready"]:
        lang = user.get("lang", "ru")
        await message.answer(TEXTS[lang]["create_personality_first"])
        return
    
    # Обновляем активность
    user["last_activity"] = datetime.now().isoformat()
    save_data(user_data)
    
    # Игнорируем кнопки-команды
    if message.text in ["📋 Главное меню", "👤 Мой профиль", "📢 Наш канал", "🎰 Колесо фортуны", "✏️ Редактировать", 
                        "📋 Main menu", "👤 My profile", "📢 Our channel", "🎰 Fortune wheel", "✏️ Edit",
                        "📋 Menú principal", "👤 Mi perfil", "📢 Nuestro canal", "🎰 Ruleta de la fortuna", "✏️ Editar",
                        "📋 Hauptmenü", "👤 Mein Profil", "📢 Unser Kanal", "🎰 Glücksrad", "✏️ Bearbeiten"]:
        return
    
    # Проверяем стиль (если подписка кончилась, а стиль премиум)
    if user.get("style") in PREMIUM_STYLE_KEYS and not has_active_subscription(user):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🪶 Нежный", callback_data="fix_style_warm")],
            [InlineKeyboardButton(text="🔥 Дерзкий", callback_data="fix_style_daring")],
            [InlineKeyboardButton(text="😊 Стеснительный", callback_data="fix_style_shy")]
        ])
        await message.answer("⚠️ Подписка кончилась, выбери бесплатный стиль:", reply_markup=keyboard)
        return
    
    available = get_available_messages(user)
    if available <= 0:
        lang = user.get("lang", "ru")
        await message.answer(TEXTS[lang]["no_messages"])
        return
    
    use_message(user)
    
    # Обработка негатива
    negative = contains_negative(message.text)
    base_xp = 5
    multiplier = 1.0
    sub_level = get_subscription_level(user)
    if sub_level == "pro":
        multiplier = 1.8
    elif sub_level == "super_pro":
        multiplier = 2.5
    
    if negative:
        xp_change = -10
        mood_change = -1
        user["negative_count"] = user.get("negative_count", 0) + 1
        if user["negative_count"] >= 5:
            user["xp"] = max(0, user.get("xp", 0) - 50)
            user["mood"] = max(-10, user.get("mood", 0) - 3)
            user["negative_count"] = 0
            save_data(user_data)
            await message.answer("💢 Ссора! Уровень близости снижен.", reply_markup=get_full_kb(user))
            return
    else:
        xp_change = int(base_xp * multiplier + 0.5)
        mood_change = 0.5
        user["negative_count"] = max(0, user.get("negative_count", 0) - 1)
    
    user["xp"] = user.get("xp", 0) + xp_change
    user["mood"] = min(10, max(-10, user.get("mood", 0) + mood_change))
    if user["xp"] < 0:
        user["xp"] = 0
    
    new_level = get_intimacy_level(user)
    old_level = user.get("last_level", 0)
    if new_level > old_level:
        user["last_level"] = new_level
        save_data(user_data)
        congrats = ["🎉 Искра!", "💞 Вы ближе!", "🔥 Напряжение!", "💋 Поцелуй!", "🌹 Страсть!", "💕 Интим!", "❤️‍🔥 Любовь!", "🔥 Полная близость!", "💖 Единство!"]
        await message.answer(congrats[min(new_level-2, len(congs)-1)], reply_markup=get_full_kb(user))
    elif new_level < old_level:
        user["last_level"] = new_level
        save_data(user_data)
        await message.answer(f"💔 Уровень упал до {new_level}.", reply_markup=get_full_kb(user))
    
    new_loc = extract_location_from_text(message.text)
    if new_loc and new_loc != user.get("location"):
        user["location"] = new_loc
        save_data(user_data)
    
    save_data(user_data)
    user["history"].append({"role": "user", "content": message.text})
    limit = get_history_limit(user)
    if len(user["history"]) > 10:
        user["history"] = user["history"][-10:]
    save_data(user_data)
    
    await bot.send_chat_action(message.chat.id, "typing")
    
    # Генерация ответа ИИ
    system_prompt = build_prompt(user)
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "system", "content": system_prompt}] + user["history"],
            temperature=0.9,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {e}")
        return
    
    # Извлекаем реакцию из ответа
    reaction, clean_answer = get_reaction_from_answer(answer)
    
    user["history"].append({"role": "assistant", "content": clean_answer})
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    save_data(user_data)
    
    sent_msg = await message.answer(clean_answer, reply_markup=get_full_kb(user))
    
    # Ставим реакцию на сообщение пользователя (если SUPER PRO)
    if reaction and get_subscription_level(user) == "super_pro":
        try:
            await bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[{"type": "emoji", "emoji": reaction}]
            )
            logging.info(f"✅ Реакция {reaction} на сообщение пользователя")
        except Exception as e:
            logging.error(f"❌ Ошибка реакции: {e}")

# ============================================================
#  КОНЕЦ ЧАСТИ 4
# ============================================================
# ============================================================
#  АДМИН-КОМАНДЫ
# ============================================================
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

@dp.message(Command("reset_user"))
async def reset_user_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используй: /reset_user ID")
        return
    target = args[1]
    if target not in user_data:
        await message.answer(f"❌ Пользователь {target} не найден.")
        return
    del user_data[target]
    save_data(user_data)
    await message.answer(f"✅ Пользователь {target} удалён.")

@dp.message(Command("grant"))
async def grant_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/grant @username — SUPER PRO\n/grant @username pro — PRO\n/grant @username sex N — сцены")
        return
    target = args[1]
    user_id = None
    if target.startswith("@"):
        try:
            user_id = (await bot.get_chat(target)).id
        except:
            await message.answer("❌ Не найден.")
            return
    else:
        try:
            user_id = int(target)
        except:
            await message.answer("❌ Неверный ID.")
            return
    user = get_user(user_id)
    if len(args) >= 3 and args[2].lower() == "pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        user["daily_messages"] = 50
        user["free_sex_scenes_pro"] = 4
        save_data(user_data)
        await message.answer(f"✅ {target} выдана PRO.")
        return
    if len(args) >= 3 and args[2].lower() == "sex":
        count = int(args[3]) if len(args) >= 4 else 1
        user["sex_scenes"] = user.get("sex_scenes", 0) + count
        save_data(user_data)
        await message.answer(f"✅ {target} выдано {count} секс-сцен.")
        return
    user["subscription"]["active"] = True
    user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
    user["subscription"]["level"] = "super_pro"
    user["daily_messages"] = 100
    user["free_sex_scenes_super"] = 8
    save_data(user_data)
    await message.answer(f"✅ {target} выдана SUPER PRO.")

@dp.message(Command("revoke_subscription"))
async def revoke_subscription_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/revoke_subscription @username")
        return
    target = args[1]
    user_id = None
    if target.startswith("@"):
        try:
            user_id = (await bot.get_chat(target)).id
        except:
            await message.answer("❌ Не найден.")
            return
    else:
        try:
            user_id = int(target)
        except:
            await message.answer("❌ Неверный ID.")
            return
    user = get_user(user_id)
    if not has_active_subscription(user):
        await message.answer(f"❌ У {target} нет подписки.")
        return
    user["subscription"]["active"] = False
    user["subscription"]["expires_at"] = None
    user["subscription"]["level"] = None
    user["free_sex_scenes_pro"] = 0
    user["free_sex_scenes_super"] = 0
    save_data(user_data)
    await message.answer(f"✅ Подписка {target} отозвана.")

@dp.message(Command("maintenance"))
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

# ============================================================
#  КОМАНДА /menu (быстрый доступ к главному меню)
# ============================================================
@dp.message(Command("menu"))
async def menu_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start")
        return
    await send_main_menu(message.chat.id, user)

# ============================================================
#  КОМАНДА /profile (быстрый доступ к профилю)
# ============================================================
@dp.message(Command("profile"))
async def profile_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await ask_create_personality(message)
        return
    await show_profile(message, user)

# ============================================================
#  КОМАНДА /clear (очистка истории диалога)
# ============================================================
@dp.message(Command("clear"))
async def clear_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["history"] = []
    save_data(user_data)
    await send_main_menu(message.chat.id, user)

# ============================================================
#  КОМАНДА /new_personality (создать нового персонажа)
# ============================================================
@dp.message(Command("new_personality"))
async def new_personality_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    lang = user.get("lang", "ru")
    await message.answer(TEXTS[lang]["choose_world"], reply_markup=world_kb, parse_mode="Markdown")

# ============================================================
#  КОМАНДА /surprise (сюрприз для подписчиков)
# ============================================================
@dp.message(Command("surprise"))
async def surprise_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not has_active_subscription(user):
        await message.answer("❌ Эта команда доступна только для подписчиков.")
        return
    level = get_intimacy_level(user)
    if level < 3:
        await message.answer("💕 Вы ещё не достаточно близки для сюрпризов. Продолжайте общаться!")
        return
    moments = [
        "Ты чувствуешь, как я беру твою руку в свою. Наши пальцы переплетаются, и я тихо шепчу: «Я так рад(а), что ты у меня есть…»",
        "Я смотрю тебе в глаза и говорю: «Знаешь, я никогда не думал(а), что смогу полюбить кого-то так сильно. Но ты… ты изменил(а) всё.»",
        "Ты стоишь у окна, я подхожу сзади и обнимаю. Мои губы касаются твоего плеча: «Я хочу быть с тобой каждую минуту…»",
        "Я достаю кольцо из кармана и, улыбаясь, говорю: «Это не предложение, но… я хочу, чтобы ты знал(а), что ты – моя мечта.»"
    ]
    if level >= 6:
        moments += ["Я прижимаю тебя к себе и шепчу: «Я хочу тебя. Не просто сейчас, а всегда. Ты готов(а)?»",
                    "Ты слышишь мой шёпот: «Раздень меня… медленно. Я хочу чувствовать каждое твоё прикосновение.»"]
    if level >= 8:
        moments += ["Я смотрю на тебя с нежностью и говорю: «Ты – моя судьба. Я знаю это точно.»",
                    "Мы остаёмся наедине, и я говорю: «Я хочу провести с тобой всю жизнь. Ты согласен(на)?»"]
    await message.answer(random.choice(moments), reply_markup=get_full_kb(user))

# ============================================================
#  КОМАНДА /switch_personality (смена персонажа с сохранением истории, только SUPER PRO)
# ============================================================
@dp.message(Command("switch_personality"))
async def switch_personality_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await message.answer("❌ Команда /switch_personality доступна только для SUPER PRO.")
        return
    user["switching_personality"] = True
    save_data(user_data)
    lang = user.get("lang", "ru")
    await message.answer(TEXTS[lang]["choose_world"], reply_markup=world_kb, parse_mode="Markdown")

# ============================================================
#  КОМАНДА /prices (цены в рублях для скриншотов)
# ============================================================
@dp.message(Command("prices"))
async def prices_cmd(message: types.Message):
    text = (
        "💳 **Цены в рублях (для справки)**\n\n"
        "🔥 PRO — 375 ₽/мес\n"
        "✨ SUPER PRO — 675 ₽/мес\n"
        "⬆️ Апгрейд до SUPER PRO — 368 ₽\n"
        "📦 30 сообщений — 45 ₽\n"
        "📦 100 сообщений — 120 ₽\n"
        "📦 300 сообщений — 300 ₽\n"
        "🔥 Секс-сцена — 68 ₽\n"
        "🎰 Колесо фортуны — 20⭐ (≈25 ₽)\n\n"
        "⚠️ Оплата в боте принимается в Telegram Stars.\n"
        "Рубли указаны для информации."
    )
    await message.answer(text, parse_mode="Markdown")

# ============================================================
#  ЗАПУСК
# ============================================================
async def main():
    print("🚀 ROLE DUEL С ЛОКАЛИЗАЦИЕЙ ЗАПУЩЕН!")
    print("🌍 Языки: Русский, English, Español, Deutsch")
    print("🎰 Колесо фортуны с уведомлениями")
    print("🎭 Создание своего персонажа для SUPER PRO")
    print("💬 ИИ с эмодзи и реакциями!")
    print("📢 Уведомления: ежедневный прокрут + 'я скучаю' через 3 дня")
    print("👥 Реферальная система — приглашай друзей!")
    print("📦 Подписки, пакеты, секс-сцены")
    print("✏️ Редактирование сообщений")
    print("🔄 Смена персонажа с сохранением истории (SUPER PRO)")
    print("📌 Админ-команды: /reset_me, /reset_user, /grant, /revoke_subscription, /maintenance")
    
    # Запускаем фоновую задачу уведомлений
    asyncio.create_task(check_notifications())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# ============================================================
#  КОНЕЦ ВСЕГО КОДА
# ============================================================
