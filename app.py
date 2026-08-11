import asyncio
import os
import json
import logging
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton, ReactionTypeEmoji
from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
#  ГОЛОСОВЫЕ СООБЩЕНИЯ (gTTS + pydub)
# ============================================================
try:
    import io
    from gtts import gTTS
    from pydub import AudioSegment
    VOICE_ENABLED = True
    logging.info("✅ Голосовые сообщения включены (gTTS + pydub найдены)")
except ImportError as e:
    VOICE_ENABLED = False
    logging.warning(f"⚠️ Голосовые отключены: {e}")

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
#  GIF-ССЫЛКИ
# ============================================================
PRO_GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGJ5aTRkejlwMGh4eWJ2Zzg0bTVlbWE2ZzFicHlsMXNibXp3dXdsayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GGSbxfzvec3PYZbFOM/giphy.gif"
SUPER_PRO_GIF_URL = "https://media.giphy.com/media/DbHZXBo5WFPZX7QpXj/giphy.gif"
MAIN_MENU_IMAGE_URL = "https://i.ibb.co/k25JyTXD/IMG-2584.jpg"

ADMIN_IDS = [7287815074]  # ЗАМЕНИ НА СВОЙ ID
maintenance_mode = False

DATA_FILE = "data/data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================================================
#  ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ
# ============================================================
AGREEMENT_TEXT = (
    "📜 **ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ**\n\n"
    "Настоящее Соглашение регулирует отношения между Администрацией (далее – «Мы», «Администрация») "
    "и Пользователем (далее – «Вы», «Пользователь») при использовании сервиса Role Duel (далее – «Сервис»).\n\n"
    "Используя Сервис, Вы подтверждаете, что полностью ознакомились с условиями настоящего Соглашения "
    "и принимаете их безоговорочно. Если Вы не согласны с каким-либо пунктом, Вы обязаны немедленно "
    "прекратить использование Сервиса.\n\n"
    "---\n\n"
    "**1. ВОЗРАСТНОЕ ОГРАНИЧЕНИЕ**\n"
    "1.1. Сервис предназначен исключительно для лиц, достигших 18 лет.\n"
    "1.2. Использование Сервиса лицами младше 18 лет строго запрещено.\n"
    "1.3. Администрация не несёт ответственности за предоставление недостоверных данных о возрасте.\n\n"
    "**2. ОПИСАНИЕ СЕРВИСА**\n"
    "2.1. Сервис предоставляет доступ к виртуальным собеседникам на основе технологий искусственного интеллекта.\n"
    "2.2. Весь контент генерируется автоматически и не отражает мнение Администрации.\n\n"
    "**3. ОТВЕТСТВЕННОСТЬ ПОЛЬЗОВАТЕЛЯ**\n"
    "3.1. Вы несёте полную ответственность за все действия, совершённые с использованием Вашего аккаунта.\n"
    "3.2. Запрещается использовать Сервис для распространения экстремистских материалов, оскорблений, угроз, клеветы, мошенничества, распространения вредоносного ПО, любых действий, нарушающих законодательство РФ.\n"
    "3.3. Администрация оставляет за собой право блокировать доступ Пользователю за нарушение правил без предварительного уведомления.\n\n"
    "**4. КОНФИДЕНЦИАЛЬНОСТЬ И ПЕРСОНАЛЬНЫЕ ДАННЫЕ**\n"
    "4.1. Мы собираем и обрабатываем Telegram ID, историю диалогов, данные о покупках и подписках, данные о взаимодействии с Сервисом.\n"
    "4.2. Мы НЕ передаём персональные данные третьим лицам, за исключением случаев, предусмотренных законом.\n"
    "4.3. Мы используем данные только для обеспечения работы Сервиса, улучшения качества обслуживания, технической поддержки.\n"
    "4.4. Все диалоги хранятся в обезличенном виде.\n"
    "4.5. Мы не несём ответственности за утечку данных, если она произошла по вине самого Пользователя.\n\n"
    "**5. ПЛАТНЫЕ УСЛУГИ И ПОДПИСКИ**\n"
    "5.1. Сервис предоставляет платные услуги (пакеты сообщений, подписки, секс-сцены).\n"
    "5.2. Цены и условия указаны в интерфейсе Сервиса и могут быть изменены в любое время.\n"
    "5.3. Подписки, оплаченные через Telegram Stars, продлеваются автоматически каждый месяц.\n"
    "5.4. Подписки, оплаченные через ЮKassa, НЕ продлеваются автоматически.\n"
    "5.5. Вы можете отменить автопродление Stars в любой момент через настройки Telegram.\n"
    "5.6. Возврат средств за оплаченные услуги не производится, за исключением случаев технической ошибки со стороны Сервиса.\n"
    "5.7. Администрация не обязана уведомлять об истечении подписки.\n\n"
    "**6. ОТКАЗ ОТ ГАРАНТИЙ**\n"
    "6.1. Сервис предоставляется «как есть» без каких-либо гарантий.\n"
    "6.2. Мы не гарантируем бесперебойную работу, соответствие контента ожиданиям, отсутствие ошибок и багов.\n"
    "6.3. Мы не несём ответственности за убытки, вызванные использованием Сервиса, действия третьих лиц, содержание сообщений, сгенерированных ИИ.\n\n"
    "**7. ИЗМЕНЕНИЕ УСЛОВИЙ**\n"
    "7.1. Администрация оставляет за собой право изменять настоящее Соглашение в любое время.\n"
    "7.2. Изменения вступают в силу с момента публикации новой версии.\n"
    "7.3. Вы обязуетесь самостоятельно отслеживать изменения.\n\n"
    "**8. ИНТЕЛЛЕКТУАЛЬНАЯ СОБСТВЕННОСТЬ**\n"
    "8.1. Все элементы Сервиса (тексты, графика, интерфейс, код) являются объектами интеллектуальной собственности Администрации.\n"
    "8.2. Запрещается копирование, распространение, модификация или любое иное использование элементов Сервиса без согласия Администрации.\n\n"
    "**9. ПОРЯДОК ОБРАЩЕНИЙ И КОНТАКТЫ**\n"
    "9.1. Все вопросы, претензии и предложения принимаются через поддержку в Telegram.\n"
    "9.2. Мы обязуемся рассмотреть обращение в течение 5 рабочих дней.\n"
    "9.3. Контактная информация доступна в профиле Сервиса.\n\n"
    "**10. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ**\n"
    "10.1. Настоящее Соглашение регулируется законодательством Российской Федерации.\n"
    "10.2. Все споры решаются в досудебном порядке через обращение к Администрации.\n"
    "10.3. Если какой-либо пункт признан недействительным, остальные пункты сохраняют силу.\n"
    "10.4. Начиная использовать Сервис, Вы подтверждаете, что ознакомились с условиями и принимаете их полностью.\n\n"
    "---\n\n"
    "⚠️ **Если Вы не согласны с настоящим Соглашением, немедленно прекратите использование Сервиса.**"
)

# ============================================================
#  МИРЫ И ГЕНДЕРЫ
# ============================================================
WORLD_NAMES = {"realism": "реального мира", "anime": "аниме-мира"}
WORLDS = {
    "realism": "реального мира, современная эпоха. Ты живёшь в большом городе, у тебя есть работа, друзья и свои привычки.",
    "anime": "аниме-мира, где всё выглядит как в японской анимации. У тебя яркие волосы, большие выразительные глаза, ты носишь стильную одежду. В этом мире есть школы, клубы, магия и романтика, как в лучших аниме-сериалах."
}
GENDERS = {"female": {"name": "Девушка", "age": 22}, "male": {"name": "Парень", "age": 24}}

# ============================================================
#  СТИЛИ
# ============================================================
BASE_STYLES = {
    "warm": {"label": "Нежный", "emoji": "🪶", "description": "Ты нежный, с мягким голосом. Ты умеешь слушать и поддерживать. Ты не торопишь события, ценишь искренность и доверие. Флирт для тебя — это игра, но ты не переходишь к интиму с незнакомцами."},
    "daring": {"label": "Дерзкий", "emoji": "🔥", "description": "Ты уверенный, прямолинейный, с искоркой в глазах. Ты любишь флиртовать и остроумно шутить. Ты не боишься быть дерзким, но всегда знаешь меру."},
    "shy": {"label": "Стеснительный", "emoji": "😊", "description": "Ты стеснительный, часто краснеешь, говоришь тихо и иногда запинаешься. Ты долго подбираешь слова, но всегда искренен."}
}
PREMIUM_STYLES = {
    "passionate": {"label": "Страстный", "emoji": "❤️‍🔥", "description": "Ты страстный, чувственный, с огнём в глазах. Ты говоришь прямо, без стеснения. Флирт для тебя — это стихия."},
    "magnetic": {"label": "Магнетический", "emoji": "✨", "description": "Ты загадочный, притягательный, с лёгкой магией в каждом слове."},
    "vulgar": {"label": "Грубый 18+", "emoji": "💢", "description": "Ты грубый, прямолинейный, не стесняешься в выражениях. Используешь матерные слова, но без пошлости.\n🔞 **18+** — содержит нецензурную лексику."},
    "seduction": {"label": "Соблазн 18+", "emoji": "🌹", "description": "Ты — воплощение чувственности и желания. Ты не скрываешь своих эмоций и физического влечения к собеседнику.\n🔞 **18+** — содержит откровенные сцены и сексуальные намёки."}
}
STYLES = {**BASE_STYLES, **PREMIUM_STYLES}
BASE_STYLE_KEYS = ["warm", "daring", "shy"]
PREMIUM_STYLE_KEYS = ["passionate", "magnetic", "vulgar", "seduction"]

def get_available_styles(user): return STYLES
def get_display_style(user):
    style = user.get("style", "warm")
    if style in PREMIUM_STYLE_KEYS and not has_active_subscription(user):
        return "warm"
    return style

def ensure_valid_style(user):
    style = user.get("style", "warm")
    return style in PREMIUM_STYLE_KEYS and not has_active_subscription(user)

def get_subscription_level(user):
    if not has_active_subscription(user): return None
    return user["subscription"].get("level", None)

def get_history_limit(user):
    level = get_subscription_level(user)
    return 100 if level == "super_pro" else 60 if level == "pro" else 30

# ============================================================
#  XP
# ============================================================
XP_PER_LEVEL = 200

def get_intimacy_level(user):
    xp = user.get("xp", 0)
    return min(10, xp // XP_PER_LEVEL + 1)

def get_xp_progress(user):
    xp = user.get("xp", 0)
    level = get_intimacy_level(user)
    if level >= 10: return XP_PER_LEVEL
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
    base = {
        1: "Вы только знакомитесь, будь вежлив(а) и дружелюбен(на), не переходи границы.",
        2: "Ты начинаешь чувствовать симпатию, можешь делать лёгкие комплименты.",
        3: "Вы становитесь ближе, ты можешь флиртовать, шутить, предлагать встретиться.",
        4: "Ты уже хочешь большего, можешь намекать на романтику, прикасаться, смотреть в глаза.",
        5: "Вы очень близки. Ты можешь предлагать поцеловаться, обниматься, говорить о чувствах.",
        6: "Ты чувствуешь страсть, можешь говорить о желании, флиртовать откровенно.",
        7: "Вы готовы к интиму. Ты можешь говорить о сексе, но без пошлости, с намёками.",
        8: "Ты влюблён(а). Говори о любви, хочешь близости, но ценнее эмоциональная связь.",
        9: "Вы полностью открыты друг другу. Можешь говорить о самых сокровенных желаниях.",
        10: "Ты полностью принадлежишь ему/ей. Говори о вечной любви, страсти, близости."
    }[level]
    if mood <= -5: return base + " Но сейчас твоё настроение плохое, ты раздражена и можешь быть грубой."
    if mood >= 5: return base + " Ты в прекрасном настроении, полна нежности и тепла."
    return base

def build_prompt(user):
    world_desc = WORLDS[user["world"]]
    gender_info = GENDERS[user["gender"]]
    style_key = get_display_style(user)
    style_desc = STYLES[style_key]["description"]
    user_gender = user.get("user_gender", "male")
    gender_context = "Ты обращаешься к нему в мужском роде (ты, он, ему, его)." if user_gender == "male" else "Ты обращаешься к ней в женском роде (ты, она, ей, её)."
    mood = user.get("mood", 0)
    mood_text = "Твоё настроение нейтральное." if mood == 0 else ("Ты в хорошем настроении." if mood > 0 else "Ты в плохом настроении, можешь быть раздражительной.")
    prompt = (
        f"**ВАЖНЕЙШЕЕ ПРАВИЛО:** Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь «меня зовут», не используешь своё имя. "
        f"Ты также НИКОГДА не спрашиваешь имя собеседника и не используешь его имя, даже если оно было названо. Обращайся к собеседнику ТОЛЬКО на «ты».\n"
        f"Ты — {gender_info['name']}, тебе {gender_info['age']} лет. Ты живёшь в {world_desc}. {style_desc}\n"
        f"ФОРМАТИРОВАНИЕ: Каждое действие в *звёздочках* с новой строки, затем реплика с новой строки. Между действием и репликой – пустая строка. "
        f"СТРУКТУРА ОТВЕТА: Ты должна строго чередовать действие и реплику. Первым всегда идёт действие, затем реплика. Минимум 2 пары (действие + реплика).\n"
        f"ЗАПРЕТЫ: Не используй имена собеседника и своё имя. Не повторяй одни и те же жесты/мимику чаще раза в 5 сообщений. Не ставь многоточия, пиши чётко. Не обрывай предложения.\n"
        f"СТИЛЬ: Обращайся на «ты», давай живые, эмоциональные ответы с чувствами, намёками, лёгкой провокацией.\n"
        f"ПАМЯТЬ: Учитывай предыдущие сообщения, настроение меняется плавно.\n"
        f"ПРЕДЛОЖЕНИЕ ЛОКАЦИИ: Ты можешь предлагать собеседнику пойти в кафе, парк, кинотеатр, погулять на улице или пойти к тебе домой.\n"
        f"ОГРАНИЧЕНИЯ ПО ВРЕМЕНИ: Ты НЕ должен пропускать время. Все события происходят в реальном времени.\n"
        f"ОГРАНИЧЕНИЯ ПО ИНТИМУ: Если уровень ниже 8, ты НЕ должен вступать в интимную сцену. Ты можешь флиртовать, дразнить, намекать, но не переходи к сексу.\n"
        f"ДРАЗНИЛКА: Ты должна дразнить пользователя, создавать напряжение. На низких уровнях – лёгкий флирт, комплименты. На средних – более откровенные намёки. На высоких – почти открытые признания в желании.\n"
        f"{gender_context}\n{mood_text}\n"
        f"Правила уровня сближения:\n{build_intimacy_rule(user)}\n"
        f"Помни: ты можешь инициировать романтику, признаваться в любви, предлагать поцеловаться, обниматься, делиться сокровенным — в зависимости от уровня сближения."
    )
    return prompt

# ============================================================
#  НЕГАТИВ, ЛОКАЦИЯ, БАЛАНС
# ============================================================
NEGATIVE_WORDS = ["дурак","идиот","тупой","тупая","дебил","урод","скотина","сука","блять","блядь","хуй","хер","пидарас","гандон","мудак","козел","козлина","овца","сволочь","тварь","мразь","завали","заткнись","отвали","пошел нахуй","пошла нахуй","жирный","толстый","уродина","страшила"]
def contains_negative(text):
    text_lower = text.lower()
    for word in NEGATIVE_WORDS:
        if word in text_lower: return True
    return False

LOCATIONS = {"home":"Дома","cafe":"В кафе","park":"В парке","cinema":"В кинотеатре","street":"На улице","unknown":"Неизвестно"}
LOCATION_KEYWORDS = {"домой":"home","дома":"home","кафе":"cafe","парк":"park","кинотеатр":"cinema","кино":"cinema","улица":"street","на улицу":"street"}
def extract_location_from_text(text):
    text_lower = text.lower()
    for keyword, loc in LOCATION_KEYWORDS.items():
        if keyword in text_lower: return loc
    return None

def reset_daily_messages(user):
    today = datetime.now().date()
    last_reset = user.get("last_daily_reset")
    if last_reset:
        last_reset_date = datetime.fromisoformat(last_reset).date()
        if last_reset_date == today: return
    level = get_subscription_level(user)
    user["daily_messages"] = 100 if level == "super_pro" else 50 if level == "pro" else 0
    user["last_daily_reset"] = datetime.now().isoformat()
    save_data(user_data)

def get_free_limit(): return 13

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in user_data:
        limit = get_free_limit()
        user_data[user_id] = {
            "verified": False, "agreement_accepted": False, "world": None, "gender": None, "user_gender": None,
            "style": "warm", "personality_ready": False,
            "subscription": {"active": False, "expires_at": None, "level": None},
            "purchased_messages": limit, "daily_messages": 0, "last_daily_reset": None,
            "history": [], "pending_invoice_id": None, "last_menu_message_id": None, "last_inline_message_id": None,
            "xp": 0, "mood": 0, "location": "unknown", "negative_count": 0, "last_level": 0,
            "sex_scenes": 0, "scene": "phone",
            "promo_pro_granted": False, "bonus_granted_for_promo": False,
            "free_sex_scenes_pro": 0, "free_sex_scenes_super": 0,
            "switching_personality": False,
            "sex_scene_unlocked": False,
            "sex_scene_used": False,
            "subscription_id": None
        }
        save_data(user_data)
    else:
        user = user_data[user_id]
        defaults = {
            "purchased_messages": get_free_limit(),
            "daily_messages": 0, "last_daily_reset": None,
            "history": [], "pending_invoice_id": None,
            "last_menu_message_id": None, "last_inline_message_id": None,
            "subscription": {"active": False, "expires_at": None, "level": None},
            "xp": 0, "mood": 0, "location": "unknown", "negative_count": 0, "last_level": 0,
            "sex_scenes": 0, "scene": "phone",
            "promo_pro_granted": False, "bonus_granted_for_promo": False,
            "free_sex_scenes_pro": 0, "free_sex_scenes_super": 0,
            "switching_personality": False,
            "sex_scene_unlocked": False, "sex_scene_used": False,
            "subscription_id": None,
            "user_gender": None
        }
        for key, val in defaults.items():
            if key not in user:
                user[key] = val
        save_data(user_data)
    return user_data[user_id]

def has_active_subscription(user):
    if not user["subscription"]["active"]: return False
    if user["subscription"]["expires_at"] is None: return False
    return datetime.now() < datetime.fromisoformat(user["subscription"]["expires_at"])

def get_available_messages(user):
    reset_daily_messages(user)
    return user["purchased_messages"] + user["daily_messages"]

def use_message(user):
    reset_daily_messages(user)
    if user["purchased_messages"] > 0:
        user["purchased_messages"] -= 1
        return True
    elif user["daily_messages"] > 0:
        user["daily_messages"] -= 1
        return True
    return False

def has_purchased_something(user):
    return user.get("purchased_messages", 0) > get_free_limit() or has_active_subscription(user)

def get_reaction(text):
    text = text.lower()
    if any(word in text for word in ["хаха","смех","😂","смешно","забавно"]): return "😂"
    if any(word in text for word in ["люблю","❤️","обожаю","милый","родной"]): return "❤️"
    if any(word in text for word in ["странно","неожиданно","ого","вау"]): return "😮"
    if any(word in text for word in ["грустно","печально","жаль","😔"]): return "😔"
    if any(word in text for word in ["круто","ого","🔥","бомба"]): return "🔥"
    return None

# ============================================================
#  КЛАВИАТУРЫ
# ============================================================
full_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Главное меню"), KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="📢 Наш канал")]
    ],
    resize_keyboard=True
)

def get_main_menu_keyboard(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Сменить персонажа", callback_data="main_change")]
    ])

def get_profile_keyboard(user):
    keyboard = [
        [InlineKeyboardButton(text="📦 Купить пакеты", callback_data="profile_packs")],
        [InlineKeyboardButton(text="👑 Оформить подписку", callback_data="profile_subs")],
        [InlineKeyboardButton(text="🔥 Купить секс-сцену (45⭐) 18+", callback_data="buy_sex_scene")],
    ]
    keyboard.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="profile_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

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

def get_style_kb(user):
    buttons = []
    for key, style in STYLES.items():
        label = f"{style['emoji']} {style['label']}"
        if key in PREMIUM_STYLES:
            if key == "passionate" and not (has_active_subscription(user) and get_subscription_level(user) in ["pro","super_pro"]):
                label += " 🔒"
            elif key == "magnetic" and not (has_active_subscription(user) and get_subscription_level(user) in ["pro","super_pro"]):
                label += " 🔒"
            elif key in ["vulgar","seduction"] and get_subscription_level(user) != "super_pro":
                label += " 🔒"
        buttons.append(InlineKeyboardButton(text=label, callback_data=f"style_{key}"))
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)

channel_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Перейти в канал", url="https://t.me/duel_dev_channel")]
])

# ============================================================
#  ГОЛОСОВЫЕ
# ============================================================
async def send_voice_message(chat_id, text):
    if not VOICE_ENABLED:
        return
    try:
        tts = gTTS(text=text, lang='ru')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio = AudioSegment.from_file(mp3_fp, format="mp3")
        ogg_fp = io.BytesIO()
        audio.export(ogg_fp, format="ogg")
        ogg_fp.seek(0)
        await bot.send_voice(
            chat_id=chat_id,
            voice=types.BufferedInputFile(ogg_fp.read(), filename="voice.ogg"),
            caption="🎧 Голосовая версия"
        )
        logging.info("🎙️ Голосовое отправлено")
    except Exception as e:
        logging.error(f"Ошибка генерации голоса: {e}")

# ============================================================
#  ОСНОВНЫЕ ОБРАБОТЧИКИ
# ============================================================
async def send_main_menu(chat_id, user):
    if user.get("last_menu_message_id"):
        try: await bot.delete_message(chat_id, user["last_menu_message_id"])
        except: pass
    if user.get("last_inline_message_id"):
        try: await bot.delete_message(chat_id, user["last_inline_message_id"])
        except: pass

    level = get_subscription_level(user)
    badge = "🔥 PRO" if level == "pro" else "✨ *SUPER PRO* ✨" if level == "super_pro" else ""
    gender_name = GENDERS[user['gender']]['name']
    world_name = WORLD_NAMES[user['world']]
    current_style = get_display_style(user)
    style_label = STYLES[current_style]['label']

    show_balance = has_purchased_something(user)
    if show_balance:
        available = get_available_messages(user)
        balance_text = f"\nОсталось сообщений: {available}" + (" (закончились)" if available <= 0 else "")
    else:
        balance_text = "\nУ вас есть бесплатные сообщения для старта"

    xp_badge = get_xp_badge(user)
    multiplier_text = ""
    sub_level = get_subscription_level(user)
    if sub_level == "pro": multiplier_text = "Бонус XP: x1.8"
    elif sub_level == "super_pro": multiplier_text = "Бонус XP: x2.5"

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
        if MAIN_MENU_IMAGE_URL and MAIN_MENU_IMAGE_URL.startswith("http"):
            msg = await bot.send_photo(chat_id, photo=MAIN_MENU_IMAGE_URL, caption=menu_text,
                                       reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
        else:
            msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
    except:
        msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")

    user["last_menu_message_id"] = msg.message_id
    save_data(user_data)
    return msg

async def ask_create_personality(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Создать персонажа", callback_data="create_personality")]
    ])
    await message.answer("👤 **Чтобы открыть профиль или купить что‑то, сначала создай своего персонажа!**\n\n"
                         "Нажми кнопку ниже, чтобы выбрать мир, пол и стиль собеседника.",
                         reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "create_personality")
async def create_personality_callback(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await call.message.delete()
    await call.message.answer("🌟 **Создай своего идеального собеседника!**\n\nСначала выбери **мир**, в котором он/она живёт:",
                              reply_markup=world_kb, parse_mode="Markdown")
    await call.answer()

@dp.message(Command("switch_personality"))
async def switch_personality_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await message.answer("❌ Команда /switch_personality доступна только для подписчиков SUPER PRO (PRO не подходит).")
        return
    user["switching_personality"] = True
    save_data(user_data)
    await message.answer("🔄 **Смена персонажа (история сохраняется)**\n\nВыбери **мир**:", reply_markup=world_kb, parse_mode="Markdown")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["verified"]:
        await message.answer("🔞 **ВНИМАНИЕ!**\nЭтот бот предназначен для лиц старше 18 лет.\nПодтверди свой возраст:",
                             reply_markup=age_kb, parse_mode="Markdown")
        return
    if not user["agreement_accepted"]:
        await message.answer(AGREEMENT_TEXT, reply_markup=agreement_kb, parse_mode="Markdown")
        return
    if not user.get("user_gender"):
        await message.answer("👤 Для начала выбери свой пол:", reply_markup=user_gender_kb)
        return
    if not user["personality_ready"]:
        await message.answer("🌟 **Создай своего идеального собеседника!**\n\nСначала выбери **мир**, в котором он/она живёт:",
                             reply_markup=world_kb, parse_mode="Markdown")
        return
    await message.answer("👋 Добро пожаловать!", reply_markup=full_kb)
    await send_main_menu(message.chat.id, user)

@dp.message(lambda m: m.text == "📋 Главное меню")
async def main_menu_reply(message: types.Message):
    await message.delete()
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start", reply_markup=full_kb)
        return
    await send_main_menu(message.chat.id, user)

@dp.message(lambda m: m.text == "👤 Мой профиль")
async def profile_reply(message: types.Message):
    await message.delete()
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await ask_create_personality(message)
        return
    await show_profile(message, user)

@dp.message(lambda m: m.text == "📢 Наш канал")
async def channel_reply(message: types.Message):
    await message.delete()
    await message.answer("📢 **Наш канал:**\nПодписывайся, чтобы быть в курсе новостей и обновлений!",
                         reply_markup=channel_inline_kb, parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "main_change")
async def main_change(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await call.message.delete()
    await call.message.answer("🔄 **Создаем нового собеседника!**\n\nВыбери **мир**:",
                              reply_markup=world_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("world_"))
async def choose_world(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    world = call.data.split("_")[1]
    user["world"] = world
    save_data(user_data)
    await call.message.edit_text("🌍 Мир выбран! Теперь выбери свой пол:", reply_markup=user_gender_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("user_gender_"))
async def choose_user_gender(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user_gender = call.data.split("_")[2]
    user["user_gender"] = user_gender
    user["gender"] = "female" if user_gender == "male" else "male"
    save_data(user_data)
    style_kb = get_style_kb(user)
    await call.message.edit_text("👤 Отлично! Теперь выбери **стиль** персонажа:", reply_markup=style_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("style_"))
async def choose_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_")[1]
    if style_key == "passionate" and not (has_active_subscription(user) and get_subscription_level(user) in ["pro","super_pro"]):
        await call.answer("❤️‍🔥 Стиль «Страстный» доступен по подпискам PRO и SUPER PRO.", show_alert=True)
        return
    if style_key == "magnetic" and not (has_active_subscription(user) and get_subscription_level(user) in ["pro","super_pro"]):
        await call.answer("💫 Стиль «Магнетический» доступен по подпискам PRO и SUPER PRO.", show_alert=True)
        return
    if style_key in ["vulgar","seduction"] and get_subscription_level(user) != "super_pro":
        await call.answer(f"🌹 Стиль «{STYLES[style_key]['label']}» доступен только по подписке SUPER PRO.", show_alert=True)
        return
    if style_key not in STYLES:
        await call.answer("❌ Стиль не найден", show_alert=True)
        return

    user["style"] = style_key
    user["personality_ready"] = True
    save_data(user_data)
    await call.message.delete()
    await call.message.answer("🎬 Теперь выбери сцену для общения:\n\n📱 Переписка в телефоне\n👫 Реальная встреча",
                              reply_markup=scene_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("scene_"))
async def choose_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    scene = call.data.split("_")[1]
    user["scene"] = scene
    save_data(user_data)
    await call.message.delete()
    await send_main_menu(call.message.chat.id, user)
    await call.answer()

async def show_profile(msg, user):
    level = get_subscription_level(user)
    sub_status = "🔥 PRO активна" if level == "pro" else "✨ SUPER PRO активна" if level == "super_pro" else "❌ неактивна"
    expiry = user["subscription"]["expires_at"]
    expiry_line = f"Окончание подписки: {datetime.fromisoformat(expiry).strftime('%d.%m.%Y %H:%M')}" if expiry else "Окончание подписки: неактивна"

    styles_text = ""
    for key, style in STYLES.items():
        locked = False
        if key in PREMIUM_STYLES:
            if key in ["vulgar","seduction"] and get_subscription_level(user) != "super_pro":
                locked = True
            elif key in ["passionate","magnetic"] and get_subscription_level(user) not in ["pro","super_pro"]:
                locked = True
        styles_text += f"{style['emoji']} {style['label']}{' 🔒' if locked else ''}\n"

    show_balance = has_purchased_something(user)
    balance_line = f"Доступно сообщений: {get_available_messages(user)}{' (закончились)' if get_available_messages(user) <= 0 else ''}" if show_balance else "У вас есть бесплатные сообщения для старта"
    xp_badge = get_xp_badge(user)
    multiplier_text = "Бонус XP: x1.8" if get_subscription_level(user) == "pro" else "Бонус XP: x2.5" if get_subscription_level(user) == "super_pro" else ""
    free_pro = user.get("free_sex_scenes_pro", 0)
    free_super = user.get("free_sex_scenes_super", 0)
    bought = user.get("sex_scenes", 0)
    total_sex_scenes = free_pro + free_super + bought
    sex_scenes_display = f"Всего секс-сцен: {total_sex_scenes}{' (доступны после 8 уровня)' if get_intimacy_level(user) < 8 else ''}"

    caption = (f"{balance_line}\nПодписка: {sub_status}\n{expiry_line}\n\n{xp_badge}\n{multiplier_text}\n{sex_scenes_display}\n\nДоступные стили:\n{styles_text}")

    chat_id = msg.chat.id
    old_msg_id = msg.message_id
    if level == "super_pro" and SUPER_PRO_GIF_URL:
        await bot.send_animation(chat_id, animation=SUPER_PRO_GIF_URL, caption=caption,
                                 reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
    elif level == "pro" and PRO_GIF_URL:
        await bot.send_animation(chat_id, animation=PRO_GIF_URL, caption=caption,
                                 reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
    else:
        await bot.send_message(chat_id, caption, reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
    try: await bot.delete_message(chat_id, old_msg_id)
    except: pass

@dp.callback_query(lambda c: c.data == "profile_subs")
async def profile_subs(call: types.CallbackQuery):
    try:
        await call.answer()
        user = get_user(call.from_user.id)
        if not user["verified"] or not user["agreement_accepted"]:
            await bot.send_message(call.message.chat.id, "🔞 Сначала пройди регистрацию через /start")
            return
        if not user["personality_ready"]:
            await bot.send_message(call.message.chat.id, "👤 Сначала создай персонажа!")
            return
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔥 PRO — 250 ⭐/мес", callback_data="subscribe_pro")],
            [InlineKeyboardButton(text="✨ SUPER PRO ✨ — 450 ⭐/мес", callback_data="subscribe_super")],
            [InlineKeyboardButton(text="🧪 Тест SUPER PRO (1⭐/мес) — для проверки автопродления", callback_data="subscribe_test")],
            [InlineKeyboardButton(text="⬆️ Апгрейд до SUPER PRO (245⭐) — улучшение без продления", callback_data="upgrade_to_super")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
        ])
        text = ("👑 Подписки Role Duel\n\n"
                "🔥 PRO (250⭐/мес)\n• 50 сообщений в день\n• Стили: ❤️‍🔥 Страстный, ✨ Магнетический\n• Память: 60 сообщений\n• 4 бесплатные секс-сцены\n• Бонус XP: x1.8\n\n"
                "✨ SUPER PRO ✨ (450⭐/мес)\n• 100 сообщений в день\n• Стили: ❤️‍🔥 Страстный, ✨ Магнетический, 💢 Грубый 18+, 🌹 Соблазн 18+\n"
                "• Голосовые сообщения\n• Кастомные реакции\n• Смена стиля без потери истории (/switch_style)\n"
                "• Память: 100 сообщений\n• 8 бесплатных секс-сцен\n• Бонус XP: x2.5\n\n"
                "🧪 Тест SUPER PRO (1⭐/мес) — для проверки автопродления.\n\n"
                "⬆️ Апгрейд до SUPER PRO (245⭐) — повысьте PRO до SUPER PRO на оставшийся срок. Это разовое улучшение, которое НЕ продлевает подписку.\n\n"
                "✅ Подписка продлевается автоматически каждый месяц через Telegram Stars.\n"
                "Вы можете отменить автопродление в любой момент в настройках Telegram.\n\n"
                "Выбери подписку:")
        await bot.send_message(call.message.chat.id, text, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Ошибка в profile_subs: {e}")
        await bot.send_message(call.message.chat.id, "⚠️ Произошла ошибка. Попробуйте позже.")

@dp.callback_query(lambda c: c.data == "subscribe_test")
async def subscribe_test(call: types.CallbackQuery):
    try:
        user = get_user(call.from_user.id)
        if has_active_subscription(user):
            level = get_subscription_level(user)
            if level == "super_pro":
                await call.answer("❌ У вас уже есть SUPER PRO.", show_alert=True)
                return
            elif level == "pro":
                await call.answer("❌ У вас уже активна PRO. Вы можете оформить тест только при отсутствии подписки.", show_alert=True)
                return
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Тест SUPER PRO (1⭐)",
            description="Тестовая подписка SUPER PRO на месяц за 1 звезду. Автопродление включено.",
            payload="subscribe_test",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Тест SUPER PRO", amount=1)],
            subscription_period=2592000
        )
        await call.answer()
    except Exception as e:
        logging.error(f"Ошибка в subscribe_test: {e}")
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "upgrade_to_super")
async def upgrade_to_super(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not has_active_subscription(user):
        await call.answer("❌ У вас нет активных подписок. Апгрейд доступен только для PRO.", show_alert=True)
        return
    level = get_subscription_level(user)
    if level != "pro":
        if level == "super_pro":
            await call.answer("❌ У вас уже есть SUPER PRO.", show_alert=True)
        else:
            await call.answer("❌ Неизвестный уровень подписки.", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Апгрейд до SUPER PRO",
            description="Повысьте PRO до SUPER PRO на оставшийся срок. Стоимость 245⭐. Это разовый платёж, который улучшает вашу подписку, но НЕ продлевает её. Дата окончания остаётся прежней.",
            payload="upgrade_to_super",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Апгрейд до SUPER PRO", amount=245)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "profile_packs")
async def profile_packs(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["verified"] or not user["agreement_accepted"]:
        await call.message.answer("🔞 Сначала пройди регистрацию через /start")
        return
    if not user["personality_ready"]:
        await call.message.delete()
        await ask_create_personality(call.message)
        await call.answer()
        return
    if has_active_subscription(user):
        await call.answer("❌ При активной подписке покупка пакетов сообщений недоступна.", show_alert=True)
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="30 сообщений — 30 ⭐", callback_data="pack_30")],
        [InlineKeyboardButton(text="100 сообщений — 80 ⭐", callback_data="pack_100")],
        [InlineKeyboardButton(text="300 сообщений — 200 ⭐", callback_data="pack_300")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
    ])
    await call.message.delete()
    await call.message.answer("📦 **Купить пакет сообщений**\n\nВыбери пакет:", reply_markup=keyboard, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data == "buy_sex_scene")
async def buy_sex_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["verified"] or not user["agreement_accepted"]:
        await call.message.answer("🔞 Сначала пройди регистрацию через /start")
        await call.answer()
        return
    level = get_intimacy_level(user)
    warning = f"\n\n⚠️ Использовать секс-сцену можно только после 8 уровня. Сейчас уровень {level}." if level < 8 else ""
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Секс-сцена (18+)",
            description="Мгновенная откровенная секс-сцена. Используйте /sex." + warning,
            payload="sex_scene",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Секс-сцена", amount=45)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка при создании счёта: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "profile_back")
async def profile_back(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await send_main_menu(call.message.chat.id, user)
    await call.message.delete()
    await call.answer()

@dp.callback_query(lambda c: c.data == "back_to_profile")
async def back_to_profile(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.message.delete()
        await ask_create_personality(call.message)
        await call.answer()
        return
    await call.message.delete()
    await show_profile(call.message, user)
    await call.answer()

@dp.message(Command("revoke_subscription"))
async def revoke_subscription_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет прав для этой команды.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используйте: /revoke_subscription @username  или  /revoke_subscription ID")
        return
    target = args[1]
    user_id = None
    if target.startswith("@"):
        try:
            chat = await bot.get_chat(target)
            user_id = chat.id
        except:
            try:
                chat = await bot.get_chat(target[1:])
                user_id = chat.id
            except:
                await message.answer("❌ Не удалось найти пользователя по юзернейму.")
                return
    else:
        try: user_id = int(target)
        except:
            await message.answer("❌ Неверный формат.")
            return
    user = get_user(user_id)
    if not has_active_subscription(user):
        await message.answer(f"✅ У пользователя {target} нет активной подписки.")
        return
    old_level = user["subscription"].get("level", "неизвестно")
    user["subscription"]["active"] = False
    user["subscription"]["expires_at"] = None
    user["subscription"]["level"] = None
    user["free_sex_scenes_pro"] = 0
    user["free_sex_scenes_super"] = 0
    save_data(user_data)
    await message.answer(f"✅ Подписка {old_level.upper()} у пользователя {target} отозвана.")

@dp.message(Command("maintenance"))
async def maintenance_cmd(message: types.Message):
    global maintenance_mode
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет прав для этой команды.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("ℹ️ Текущий режим: " + ("ВКЛЮЧЁН" if maintenance_mode else "ВЫКЛЮЧЁН") +
                             "\nИспользуйте: /maintenance on  или  /maintenance off")
        return
    if args[1].lower() == "on":
        maintenance_mode = True
        await message.answer("🛠️ Режим технического обслуживания **ВКЛЮЧЁН**.")
    elif args[1].lower() == "off":
        maintenance_mode = False
        await message.answer("✅ Режим технического обслуживания **ВЫКЛЮЧЁН**.")
    else:
        await message.answer("❌ Неверный параметр. Используйте on или off.\nТекущий режим: " + ("ВКЛЮЧЁН" if maintenance_mode else "ВЫКЛЮЧЁН"))

@dp.callback_query(lambda c: c.data.startswith("pack_"))
async def buy_pack(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if has_active_subscription(user):
        await call.answer("❌ При активной подписке покупка пакетов сообщений недоступна.", show_alert=True)
        return
    pack_map = {"30":30,"100":100,"300":300}
    price_map = {"30":30,"100":80,"300":200}
    period = call.data.split("_")[1]
    amount = pack_map[period]
    price = price_map[period]
    try:
        await bot.send_invoice(chat_id=call.message.chat.id, title=f"Пакет {amount} сообщений",
                               description=f"Купить {amount} сообщений.",
                               payload=f"pack_{period}", provider_token="", currency="XTR",
                               prices=[LabeledPrice(label=f"{amount} сообщений", amount=price)])
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
        logging.error(f"Ошибка send_invoice (pack): {e}")

@dp.callback_query(lambda c: c.data == "subscribe_pro")
async def subscribe_pro(call: types.CallbackQuery):
    try:
        user = get_user(call.from_user.id)
        if has_active_subscription(user):
            level = get_subscription_level(user)
            if level == "super_pro":
                await call.answer("❌ У вас уже есть SUPER PRO.", show_alert=True)
                return
            elif level == "pro":
                await call.answer("❌ У вас уже активна PRO подписка.", show_alert=True)
                return
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="PRO подписка на месяц",
            description="50 сообщений в день, память 60, 4 бесплатные секс-сцены. Автопродление.",
            payload="subscribe_pro",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="PRO месяц", amount=250)],
            subscription_period=2592000
        )
        await call.answer()
    except Exception as e:
        logging.error(f"Ошибка в subscribe_pro: {e}")
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "subscribe_super")
async def subscribe_super(call: types.CallbackQuery):
    try:
        user = get_user(call.from_user.id)
        if has_active_subscription(user):
            level = get_subscription_level(user)
            if level == "super_pro":
                await call.answer("❌ У вас уже активна SUPER PRO.", show_alert=True)
                return
            elif level == "pro":
                await call.answer("💡 У вас активна PRO. Воспользуйтесь кнопкой «Апгрейд до SUPER PRO» (245⭐).", show_alert=True)
                return
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="SUPER PRO подписка на месяц",
            description="100 сообщений в день, память 100, 8 бесплатных секс-сцен, голосовые, реакции. Автопродление.",
            payload="subscribe_super",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="SUPER PRO месяц", amount=450)],
            subscription_period=2592000
        )
        await call.answer()
    except Exception as e:
        logging.error(f"Ошибка в subscribe_super: {e}")
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(lambda m: m.successful_payment)
async def payment_success(message: types.Message):
    user = get_user(message.from_user.id)
    payload = message.successful_payment.invoice_payload
    is_first = message.successful_payment.is_first_recurring

    if payload.startswith("pack_"):
        period = payload.split("_")[1]
        pack_map = {"30":30,"100":100,"300":300}
        amount = pack_map[period]
        user["purchased_messages"] += amount
        save_data(user_data)
        await message.answer(f"✅ Куплено {amount} сообщений!")

    elif payload == "upgrade_to_super":
        if has_active_subscription(user):
            old_expiry = user["subscription"]["expires_at"]
            user["subscription"]["level"] = "super_pro"
            user["free_sex_scenes_super"] = 8
            user["free_sex_scenes_pro"] = 0
            user["daily_messages"] = 100
            user["subscription_id"] = None
            save_data(user_data)
            await message.answer(
                f"✅ Апгрейд до SUPER PRO выполнен!\n"
                f"Ты получил SUPER PRO до {datetime.fromisoformat(old_expiry).strftime('%d.%m.%Y %H:%M')}.\n\n"
                "⚠️ Апгрейд НЕ продлевает подписку. Автопродление отключено."
            )
        else:
            await message.answer("❌ Ошибка: нет активной подписки для апгрейда.")

    elif payload in ["subscribe_pro", "subscribe_super", "subscribe_test"]:
        level = "super_pro" if ("super" in payload or "test" in payload) else "pro"
        if is_first or not has_active_subscription(user):
            user["subscription"]["active"] = True
            user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
            user["subscription"]["level"] = level
            if level == "super_pro":
                user["free_sex_scenes_super"] = 8
                user["free_sex_scenes_pro"] = 0
                user["daily_messages"] = 100
            else:
                user["free_sex_scenes_pro"] = 4
                user["free_sex_scenes_super"] = 0
                user["daily_messages"] = 50
            user["last_daily_reset"] = datetime.now().isoformat()
            save_data(user_data)
            await message.answer(f"✅ Подписка {level.upper()} активирована! Автопродление включено.")
        else:
            current_expiry = datetime.fromisoformat(user["subscription"]["expires_at"])
            new_expiry = current_expiry + timedelta(days=30)
            user["subscription"]["expires_at"] = new_expiry.isoformat()
            save_data(user_data)
            await message.answer("✅ Подписка продлена на месяц!")

    elif payload == "sex_scene":
        user["sex_scenes"] = user.get("sex_scenes", 0) + 1
        save_data(user_data)
        await message.answer("✅ Куплена секс-сцена! Используйте /sex.")

@dp.message(Command("switch_style"))
async def switch_style_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await message.answer("❌ Команда /switch_style доступна только для SUPER PRO.")
        return
    styles = get_available_styles(user)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for key, style in styles.items():
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=f"{style['emoji']} {style['label']}", callback_data=f"switch_{key}")])
    await message.answer("🔄 **Выбери новый стиль:**\n\nИстория сохранится.", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(lambda c: c.data.startswith("switch_"))
async def switch_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_")[1]
    if style_key not in STYLES:
        await call.answer("❌ Стиль недоступен", show_alert=True)
        return
    user["style"] = style_key
    save_data(user_data)
    await call.message.edit_text(f"✅ Стиль изменён на: {STYLES[style_key]['label']}", parse_mode="Markdown")
    await call.answer()

@dp.message(Command("sex"))
async def sex_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    level = get_intimacy_level(user)
    user_id = message.from_user.id

    if user_id in ADMIN_IDS:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛏 В постели", callback_data="sex_type_bed")],
            [InlineKeyboardButton(text="💋 Поцелуй", callback_data="sex_type_kiss")],
            [InlineKeyboardButton(text="⛓ БДСМ", callback_data="sex_type_bdsm")],
            [InlineKeyboardButton(text="👅 Минет", callback_data="sex_type_blowjob")],
            [InlineKeyboardButton(text="👗 Раздевание", callback_data="sex_type_strip")],
            [InlineKeyboardButton(text="🧱 У стены", callback_data="sex_type_wall")],
            [InlineKeyboardButton(text="🚿 В душе", callback_data="sex_type_shower")],
            [InlineKeyboardButton(text="💆 Массаж", callback_data="sex_type_massage")],
            [InlineKeyboardButton(text="🎲 Случайный", callback_data="sex_type_random")],
        ])
        await message.answer("👑 Админ-режим (без ограничений):", reply_markup=keyboard)
        return

    if level >= 8 and not user.get("sex_scene_unlocked", False):
        user["sex_scene_unlocked"] = True
        user["sex_scene_used"] = False
        save_data(user_data)
        await message.answer("🎉 Ты достиг 8 уровня! Тебе открылась бесплатная секс-сцена. Используй /sex ещё раз.")
        return

    if user.get("sex_scene_unlocked", False) and not user.get("sex_scene_used", False):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛏 В постели", callback_data="sex_type_bed")],
            [InlineKeyboardButton(text="💋 Поцелуй", callback_data="sex_type_kiss")],
            [InlineKeyboardButton(text="⛓ БДСМ", callback_data="sex_type_bdsm")],
            [InlineKeyboardButton(text="👅 Минет", callback_data="sex_type_blowjob")],
            [InlineKeyboardButton(text="👗 Раздевание", callback_data="sex_type_strip")],
            [InlineKeyboardButton(text="🧱 У стены", callback_data="sex_type_wall")],
            [InlineKeyboardButton(text="🚿 В душе", callback_data="sex_type_shower")],
            [InlineKeyboardButton(text="💆 Массаж", callback_data="sex_type_massage")],
            [InlineKeyboardButton(text="🎲 Случайный", callback_data="sex_type_random")],
        ])
        await message.answer("🔥 Бесплатная секс-сцена! Выбери тип:", reply_markup=keyboard)
        return

    if level < 8:
        await message.answer(
            f"❌ Секс-сцены доступны только после 8 уровня. Сейчас уровень {level}. Продолжай общаться!\n\n"
            "Ты можешь купить сцену заранее в профиле.",
            reply_markup=full_kb,
            parse_mode="Markdown"
        )
        return

    sub_level = get_subscription_level(user)
    free_pro = user.get("free_sex_scenes_pro", 0)
    free_super = user.get("free_sex_scenes_super", 0)
    bought = user.get("sex_scenes", 0)
    total_available = (free_super if sub_level == "super_pro" else 0) + (free_pro if sub_level == "pro" else 0) + bought
    if total_available <= 0:
        await message.answer("❌ Нет доступных секс-сцен.\n\nКупи в профиле за 45⭐ или оформи подписку.", reply_markup=full_kb)
        return

    user["sex_total_available"] = total_available
    user["sex_free_pro"] = free_pro
    user["sex_free_super"] = free_super
    user["sex_bought"] = bought
    user["sex_level"] = sub_level
    save_data(user_data)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛏 В постели", callback_data="sex_type_bed")],
        [InlineKeyboardButton(text="💋 Поцелуй", callback_data="sex_type_kiss")],
        [InlineKeyboardButton(text="⛓ БДСМ", callback_data="sex_type_bdsm")],
        [InlineKeyboardButton(text="👅 Минет", callback_data="sex_type_blowjob")],
        [InlineKeyboardButton(text="👗 Раздевание", callback_data="sex_type_strip")],
        [InlineKeyboardButton(text="🧱 У стены", callback_data="sex_type_wall")],
        [InlineKeyboardButton(text="🚿 В душе", callback_data="sex_type_shower")],
        [InlineKeyboardButton(text="💆 Массаж", callback_data="sex_type_massage")],
        [InlineKeyboardButton(text="🎲 Случайный", callback_data="sex_type_random")],
    ])
    await message.answer("🔥 Выбери тип секс-сцены:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("sex_type_"))
async def sex_type_choice(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    user = get_user(call.from_user.id)
    sex_type = call.data.split("_")[2]
    user_id = call.from_user.id

    if user_id in ADMIN_IDS:
        await generate_sex_scene(call, user, sex_type, free=True)
        return

    if user.get("sex_scene_unlocked", False) and not user.get("sex_scene_used", False):
        user["sex_scene_used"] = True
        save_data(user_data)
        await generate_sex_scene(call, user, sex_type, free=True)
        return

    level = user.get("sex_level")
    free_pro = user.get("sex_free_pro", 0)
    free_super = user.get("sex_free_super", 0)
    bought = user.get("sex_bought", 0)
    total_available = (free_super if level == "super_pro" else 0) + (free_pro if level == "pro" else 0) + bought
    if total_available <= 0:
        await call.message.answer("❌ Больше нет доступных секс-сцен.")
        return
    if level == "super_pro" and free_super > 0:
        user["free_sex_scenes_super"] = free_super - 1
    elif level == "pro" and free_pro > 0:
        user["free_sex_scenes_pro"] = free_pro - 1
    else:
        user["sex_scenes"] = bought - 1
    save_data(user_data)
    await generate_sex_scene(call, user, sex_type, free=False)

async def generate_sex_scene(call, user, sex_type, free=False):
    await bot.send_chat_action(call.message.chat.id, "typing")
    gender_info = GENDERS[user['gender']]
    style_key = get_display_style(user)
    style_desc = STYLES[style_key]['description']
    type_prompts = {
        "bed": "Опиши страстную секс-сцену в постели.",
        "kiss": "Опиши долгий, страстный поцелуй.",
        "bdsm": "Опиши сцену с элементами БДСМ (лёгкое доминирование, связывание).",
        "blowjob": "Опиши сцену минетa.",
        "strip": "Опиши сцену раздевания.",
        "wall": "Опиши сцену у стены.",
        "shower": "Опиши интимную сцену в душе.",
        "massage": "Опиши сцену эротического массажа.",
        "random": "Опиши случайную откровенную сцену."
    }
    if sex_type == "random":
        sex_type = random.choice(["bed","kiss","bdsm","blowjob","strip","wall","shower","massage"])
    prompt_text = type_prompts.get(sex_type, type_prompts["bed"])
    full_prompt = (f"ЖЁСТКИЙ ЗАПРЕТ: не используй имена.\n"
                   f"Ты — {gender_info['name']}, {gender_info['age']} лет. Стиль: {style_desc}. "
                   f"{prompt_text} "
                   f"Сцена должна быть развёрнутой, с диалогами и эмоциями. Используй формат: действие в *звёздочках*, затем реплика. Минимум 2 пары.")
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-v4-pro",
            messages=[
                {"role": "system", "content": "Ты – виртуальный собеседник, пишешь откровенные секс-сцены. Запрещено использовать имена."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=1.0,
            max_tokens=2000
        )
        scene_text = response.choices[0].message.content
        await bot.send_message(call.message.chat.id, scene_text, reply_markup=full_kb)
    except Exception as e:
        await bot.send_message(call.message.chat.id, f"⚠️ Ошибка генерации: {e}")

@dp.message(Command("surprise"))
async def surprise_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not has_active_subscription(user):
        await message.answer("❌ Только для подписчиков.")
        return
    level = get_intimacy_level(user)
    if level < 3:
        await message.answer("💕 Вы ещё не достаточно близки.")
        return
    moments = [
        "Я беру твою руку в свою и шепчу: «Я так рад(а), что ты у меня есть…»",
        "Я смотрю тебе в глаза и говорю: «Ты изменил(а) всё…»",
        "Я обнимаю тебя сзади и шепчу: «Я хочу быть с тобой каждую минуту…»",
        "Я достаю кольцо и говорю: «Ты – моя мечта.»"
    ]
    if level >= 6:
        moments += ["Я прижимаю тебя к себе: «Я хочу тебя. Ты готов(а)?»",
                    "Я шепчу: «Раздень меня… медленно.»"]
    if level >= 8:
        moments += ["Я говорю: «Ты – моя судьба.»",
                    "Я говорю: «Я хочу провести с тобой всю жизнь.»"]
    await message.answer(random.choice(moments), reply_markup=full_kb)

@dp.callback_query(lambda c: c.data == "age_yes")
async def age_yes(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["verified"] = True
    save_data(user_data)
    await call.message.edit_text("✅ Возраст подтверждён.\nОзнакомьтесь с соглашением:", reply_markup=agreement_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data == "age_no")
async def age_no(call: types.CallbackQuery):
    await call.message.edit_text("🚫 Доступ запрещён.")
    await call.message.edit_reply_markup()
    await call.answer()

@dp.callback_query(lambda c: c.data == "agreement_accept")
async def agreement_accept(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["agreement_accepted"] = True
    save_data(user_data)
    await call.message.edit_text("✅ Соглашение принято!\n\nТеперь создай персонажа.\nВыбери мир:", reply_markup=world_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data == "agreement_decline")
async def agreement_decline(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["verified"] = False
    save_data(user_data)
    await call.message.edit_text("❌ Вы отказались.")
    await call.message.edit_reply_markup()
    await call.answer()

@dp.message(Command("new_personality"))
async def new_personality_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await message.answer("🔄 Создаём нового собеседника!\nВыбери мир:", reply_markup=world_kb, parse_mode="Markdown")

@dp.message(Command("clear"))
async def clear_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["history"] = []
    save_data(user_data)
    await send_main_menu(message.chat.id, user)

@dp.message(Command("menu"))
async def menu_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа.")
        return
    await send_main_menu(message.chat.id, user)

@dp.message(Command("profile"))
async def profile_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await ask_create_personality(message)
        return
    await show_profile(message, user)

@dp.message(Command("grant"))
async def grant_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/grant @username — SUPER PRO\n/grant @username pro — PRO\n/grant @username sex N — секс-сцены")
        return
    target = args[1]
    user_id = None
    if target.startswith("@"):
        try:
            chat = await bot.get_chat(target)
            user_id = chat.id
        except:
            try:
                chat = await bot.get_chat(target[1:])
                user_id = chat.id
            except:
                await message.answer("❌ Не найден пользователь.")
                return
    else:
        try: user_id = int(target)
        except:
            await message.answer("❌ Неверный формат.")
            return
    user = get_user(user_id)
    if len(args) >= 3 and args[2].lower() == "pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().isoformat()
        user["free_sex_scenes_pro"] = 4
        user["free_sex_scenes_super"] = 0
        save_data(user_data)
        await message.answer(f"✅ PRO выдана {target}.")
        return
    if len(args) >= 3 and args[2].lower() == "sex":
        count = 1
        if len(args) >= 4:
            try: count = int(args[3])
            except: count = 1
        user["sex_scenes"] = user.get("sex_scenes", 0) + count
        save_data(user_data)
        await message.answer(f"✅ {count} секс-сцен выдано {target}.")
        return
    user["subscription"]["active"] = True
    user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
    user["subscription"]["level"] = "super_pro"
    user["purchased_messages"] += 50
    user["daily_messages"] = 100
    user["last_daily_reset"] = datetime.now().isoformat()
    user["free_sex_scenes_super"] = 8
    user["free_sex_scenes_pro"] = 0
    save_data(user_data)
    await message.answer(f"✅ SUPER PRO выдана {target}.")

@dp.callback_query(lambda c: c.data == "cancel_payment")
async def cancel_payment(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    pending_id = user.get("pending_invoice_id")
    if pending_id:
        try: await bot.delete_message(call.message.chat.id, message_id=pending_id)
        except: pass
        user["pending_invoice_id"] = None
        save_data(user_data)
    await call.message.delete()
    await send_main_menu(call.message.chat.id, user)
    await call.answer()

@dp.message()
async def handle_message(message: types.Message):
    global maintenance_mode
    user = get_user(message.from_user.id)
    
    logging.info(f"📩 Сообщение от {message.from_user.id}, уровень подписки: {get_subscription_level(user)}")
    
    if ensure_valid_style(user):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🪶 Нежный", callback_data="fix_style_warm")],
            [InlineKeyboardButton(text="🔥 Дерзкий", callback_data="fix_style_daring")],
            [InlineKeyboardButton(text="😊 Стеснительный", callback_data="fix_style_shy")],
        ])
        await message.answer(
            "⚠️ Твоя подписка закончилась, а у тебя выбран премиум-стиль.\n"
            "Выбери бесплатный стиль (история сохранится):",
            reply_markup=keyboard
        )
        return

    if maintenance_mode and message.from_user.id not in ADMIN_IDS:
        await message.answer("🛠️ Бот на техобслуживании. Загляни позже.", parse_mode="Markdown")
        return
    if not user["verified"] or not user["agreement_accepted"]:
        await message.answer("🔞 Сначала пройди регистрацию через /start")
        return
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start")
        return
    if message.text in ["📋 Главное меню", "👤 Мой профиль", "📢 Наш канал"]:
        return
    available = get_available_messages(user)
    if available <= 0:
        await message.answer("🔄 Выберите действие:", reply_markup=full_kb)
        await send_main_menu(message.chat.id, user)
        action_buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👑 Оформить подписку", callback_data="profile_subs")],
            [InlineKeyboardButton(text="📦 Купить пакеты", callback_data="profile_packs")]
        ])
        await message.answer(
            "😔 Закончились сообщения.\n\nКупи пакет или оформи подписку.",
            reply_markup=action_buttons,
            parse_mode="Markdown"
        )
        return
    use_message(user)
    
    negative = contains_negative(message.text)
    base_xp = 5
    multiplier = 1.0
    sub_level = get_subscription_level(user)
    if sub_level == "pro": multiplier = 1.8
    elif sub_level == "super_pro": multiplier = 2.5

    if negative:
        xp_change = -10
        mood_change = -1
        user["negative_count"] = user.get("negative_count", 0) + 1
        if user["negative_count"] >= 5:
            user["xp"] = user.get("xp", 0) - 50
            user["mood"] = user.get("mood", 0) - 3
            user["negative_count"] = 0
            save_data(user_data)
            await message.answer("💢 Вспыхнула ссора! Настроение испорчено.", reply_markup=full_kb, parse_mode="Markdown")
            new_level = get_intimacy_level(user)
            await message.answer(f"💔 Уровень снижен до {new_level}.", reply_markup=full_kb)
            user["history"].append({"role": "assistant", "content": "💢 Ссора!"})
            save_data(user_data)
            return
    else:
        xp_change = int(base_xp * multiplier + 0.5)
        mood_change = 0.5
        if user.get("negative_count", 0) > 0:
            user["negative_count"] -= 1
            if user["negative_count"] < 0: user["negative_count"] = 0

    user["xp"] = user.get("xp", 0) + xp_change
    user["mood"] = user.get("mood", 0) + mood_change
    if user["mood"] > 10: user["mood"] = 10
    elif user["mood"] < -10: user["mood"] = -10
    if user["xp"] < 0: user["xp"] = 0
    
    new_level = get_intimacy_level(user)
    old_level = user.get("last_level", 0)
    if new_level > old_level:
        user["last_level"] = new_level
        save_data(user_data)
        level_congrats = get_level_congratulation(new_level)
        if level_congrats:
            await message.answer(level_congrats, reply_markup=full_kb, parse_mode="Markdown")
    elif new_level < old_level:
        user["last_level"] = new_level
        save_data(user_data)
        await message.answer(f"💔 Уровень упал до {new_level}.", reply_markup=full_kb)
    
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
    async def keep_typing():
        while True:
            await bot.send_chat_action(message.chat.id, "typing")
            await asyncio.sleep(4)
    typing_task = asyncio.create_task(keep_typing())
    
    if get_subscription_level(user) == "super_pro":
        reaction = get_reaction(message.text)
        if reaction:
            try:
                await bot.set_message_reaction(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    reaction=[{"type": "emoji", "emoji": reaction}]
                )
                logging.info(f"✅ Реакция {reaction}")
            except Exception as e:
                logging.error(f"❌ Ошибка реакции: {e}")
    
    system_prompt = build_prompt(user)
    messages_for_api = [{"role": "system", "content": system_prompt}]
    messages_for_api.extend(user["history"])
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-v4-pro",
            messages=messages_for_api,
            temperature=0.9,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
    except Exception as e:
        if typing_task:
            typing_task.cancel()
            try: await typing_task
            except asyncio.CancelledError: pass
        await message.answer(f"⚠️ Ошибка: {e}")
        logging.error(f"Ошибка DeepSeek: {e}")
        return
    finally:
        if typing_task:
            typing_task.cancel()
            try: await typing_task
            except asyncio.CancelledError: pass
    
    user["history"].append({"role": "assistant", "content": answer})
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    save_data(user_data)
    
    sent_msg = await message.answer(answer, reply_markup=full_kb)

    if get_subscription_level(user) == "super_pro" and VOICE_ENABLED:
        await send_voice_message(message.chat.id, answer)

@dp.callback_query(lambda c: c.data.startswith("fix_style_"))
async def fix_style_callback(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_")[2]
    if style_key in BASE_STYLE_KEYS:
        user["style"] = style_key
        save_data(user_data)
        await call.message.edit_text(f"✅ Стиль изменён на {STYLES[style_key]['label']}.\nПродолжай общение.")
        await call.answer()
        await send_main_menu(call.message.chat.id, user)
    else:
        await call.answer("❌ Недопустимый стиль", show_alert=True)

def get_level_congratulation(level):
    return {
        2: "🎉 Уровень 2 – теперь можно флиртовать!",
        3: "💞 Уровень 3 – обниматься и делиться секретами!",
        4: "🔥 Уровень 4 – напряжение растёт!",
        5: "💋 Уровень 5 – готовы к поцелую!",
        6: "🌹 Уровень 6 – ты влюблён(а)!",
        7: "💕 Уровень 7 – интимная близость близка!",
        8: "❤️‍🔥 Уровень 8 – вы пара!",
        9: "🔥 Уровень 9 – вы открыты друг другу!",
        10: "💖 Уровень 10 – вы единое целое!"
    }.get(level, "")

async def main():
    print("🚀 Role Duel запущен!")
    print("🔥 PRO: 250⭐/мес, x1.8 XP")
    print("✨ SUPER PRO: 450⭐/мес, x2.5 XP")
    print("⬆️ Апгрейд: 245⭐ (без продления)")
    print("🧪 Тест SUPER PRO: 1⭐/мес (автопродление)")
    print("🎙️ Голосовые сообщения:", "ВКЛЮЧЕНЫ" if VOICE_ENABLED else "ОТКЛЮЧЕНЫ")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
