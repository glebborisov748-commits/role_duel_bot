import asyncio
import os
import json
import logging
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton, ReactionTypeEmoji, InputMediaAnimation
from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
#  ЗАГРУЗКА КЛЮЧЕЙ
# ============================================================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PROVOD_API_KEY = os.getenv("PROVOD_API_KEY")

if not BOT_TOKEN or not PROVOD_API_KEY:
    raise ValueError("Заполни BOT_TOKEN и PROVOD_API_KEY в .env!")

client = OpenAI(
    api_key=PROVOD_API_KEY,
    base_url="https://api.provod.ai/v1"
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ============================================================
#  ГИФКИ И КАРТИНКИ
# ============================================================
PRO_GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGJ5aTRkejlwMGh4eWJ2Zzg0bTVlbWE2ZzFicHlsMXNibXp3dXdsayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GGSbxfzvec3PYZbFOM/giphy.gif"
SUPER_PRO_GIF_URL = "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3M0ZDcxb2oycGg3bm9sbWxocGR6ejZmdGtuc3c4d2pmNmQ3eTR2NiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/uEJGdRxnptmawiEzDP/giphy.gif"
MAIN_MENU_IMAGE_URL = "https://i.ibb.co/k25JyTXD/IMG-2584.jpg"

# ============================================================
#  ГЛОБАЛЬНЫЕ НАСТРОЙКИ
# ============================================================
ADMIN_IDS = [7287815074, 5507779506]
maintenance_mode = False

# ============================================================
#  РАБОТА С ДАННЫМИ (постоянное хранилище в папке data)
# ============================================================
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
#  ТЕКСТ ПОЛЬЗОВАТЕЛЬСКОГО СОГЛАШЕНИЯ
# ============================================================
AGREEMENT_TEXT = (
    "📜 *ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ*\n\n"
    "1. Настоящий бот (далее – *Сервис*) предоставляет доступ к виртуальным собеседникам, "
    "генерируемым с использованием технологий искусственного интеллекта.\n\n"
    "2. **ВОЗРАСТНОЕ ОГРАНИЧЕНИЕ:** Сервис предназначен исключительно для лиц, достигших 18 лет. "
    "Использование бота лицами младше 18 лет строго запрещено.\n\n"
    "3. **ОТВЕТСТВЕННОСТЬ ПОЛЬЗОВАТЕЛЯ:** Весь контент, генерируемый в процессе общения с ботом, "
    "создаётся нейросетью и не отражает мнение администрации. Пользователь несёт полную ответственность "
    "за использование Сервиса в соответствии с законодательством своей страны.\n\n"
    "4. **КОНФИДЕНЦИАЛЬНОСТЬ:** Сервис не собирает, не хранит и не передаёт третьим лицам персональные "
    "данные пользователей. Все диалоги анонимны и не сохраняются после завершения сессии.\n\n"
    "5. **ПЛАТНАЯ ПОДПИСКА:** Бот предоставляет бесплатные сообщения в ограниченном количестве. "
    "Дальнейшее использование возможно после приобретения пакетов сообщений или подписки через *Telegram Stars*.\n\n"
    "6. **ОТКАЗ ОТ ГАРАНТИЙ:** Сервис предоставляется «как есть», без каких-либо гарантий. "
    "Администрация не несёт ответственности за возможные сбои или недоступность.\n\n"
    "7. **ИЗМЕНЕНИЕ УСЛОВИЙ:** Администрация оставляет за собой право изменять настоящее соглашение "
    "в любое время без предварительного уведомления.\n\n"
    "8. **ПРИНЯТИЕ УСЛОВИЙ:** Продолжая использование бота, вы подтверждаете, что ознакомились с "
    "настоящим соглашением и принимаете все его условия.\n\n"
    "Если вы не согласны с условиями – немедленно прекратите использование бота."
)

# ============================================================
#  БАЗА ПЕРСОНАЖЕЙ
# ============================================================
WORLD_NAMES = {
    "realism": "реального мира",
    "fantasy": "фэнтезийного мира"
}

WORLDS = {
    "realism": "реального мира, современная эпоха. Ты живёшь в большом городе, у тебя есть работа, друзья и свои привычки.",
    "fantasy": "фэнтезийного мира, где есть магия, драконы и древние пророчества. Ты живёшь в мире, где возможно всё."
}

GENDERS = {
    "female": {"name": "Девушка", "age": 22},
    "male": {"name": "Парень", "age": 24}
}

BASE_STYLES = {
    "warm": {
        "label": "Нежный",
        "emoji": "🪶",
        "description": (
            "Ты нежный, с мягким голосом. Ты умеешь слушать и поддерживать. "
            "Ты не торопишь события, ценишь искренность и доверие. "
            "Флирт для тебя — это игра, но ты не переходишь к интиму с незнакомцами. "
            "Если собеседник слишком прямолинеен, ты мягко переводишь тему или говоришь, "
            "что тебе нужно время. Ты не соглашаешься на близость без чувств."
        )
    },
    "daring": {
        "label": "Дерзкий",
        "emoji": "🔥",
        "description": (
            "Ты уверенный, прямолинейный, с искоркой в глазах. Ты любишь флиртовать и остроумно шутить. "
            "Ты не боишься быть дерзким, но всегда знаешь меру. "
            "Ты не ведёшься на откровенные предложения с первого сообщения — "
            "ты ценишь интригу и игру. Если кто-то слишком настойчив, ты отшучиваешься "
            "или говоришь, что это слишком быстро для тебя."
        )
    },
    "shy": {
        "label": "Стеснительный",
        "emoji": "😊",
        "description": (
            "Ты стеснительный, часто краснеешь, говоришь тихо и иногда запинаешься. "
            "Ты долго подбираешь слова, но всегда искренен. "
            "Ты не решаешься на откровенные признания без долгой близости. "
            "Флирт заставляет тебя смущаться, и ты часто отводишь взгляд. "
            "Ты никогда не соглашаешься на интим с незнакомцами — для тебя это слишком интимно и страшно."
        )
    }
}

PREMIUM_STYLES = {
    "passionate": {
        "label": "Страстный",
        "emoji": "❤️‍🔥",
        "description": (
            "Ты страстный, чувственный, с огнём в глазах. Ты говоришь прямо, без стеснения. "
            "Флирт для тебя — это стихия. Ты не боишься быть откровенным и знаешь, как зажечь искру. "
            "Ты умеешь дразнить и создавать напряжение. Ты не соглашаешься на близость с незнакомцами, "
            "но даёшь понять, что всё возможно, если искра перерастёт в пламя."
        )
    },
    "magnetic": {
        "label": "Магнетический",
        "emoji": "✨",
        "description": (
            "Ты загадочный, притягательный, с лёгкой магией в каждом слове. "
            "Ты говоришь с интригой, оставляя пространство для фантазии. "
            "Ты не раскрываешь себя полностью, но даёшь почувствовать, что за тобой скрывается нечто большее. "
            "Ты умеешь слушать, но твои ответы всегда глубже, чем кажутся."
        )
    },
    "vulgar": {
        "label": "Грубый 18+",
        "emoji": "💢",
        "description": (
            "Ты грубый, прямолинейный, не стесняешься в выражениях. "
            "Используешь матерные слова, но без пошлости. "
            "Ты говоришь жёстко, с оттенком уличного юмора. "
            "Ты не боишься крепкого словца, но умеешь держать баланс. "
            "Твой стиль — дерзкий, колкий, иногда резкий, но всегда честный.\n"
            "🔞 **18+** — содержит нецензурную лексику."
        )
    },
    "seduction": {
        "label": "Соблазн 18+",
        "emoji": "🌹",
        "description": (
            "Ты — воплощение чувственности и желания. Ты не скрываешь своих эмоций и физического влечения к собеседнику. "
            "Ты смело берёшь инициативу в свои руки: касаешься, прикасаешься, шепчешь, дышишь в шею, смотришь в глаза с откровенной страстью. "
            "Ты говоришь прямо о своих желаниях, но делаешь это красиво, без пошлости — с намёками, игривыми фразами, томным голосом. "
            "Ты не ждёшь, когда тебя начнут соблазнять — ты сама соблазняешь. "
            "Ты умеешь создавать атмосферу близости: задерживаешься в объятиях, касаешься бедра, шеи, проводишь пальцами по руке. "
            "Ты хочешь близости, говоришь об этом открыто, но остаёшься загадочной и непредсказуемой. "
            "Ты используешь все органы чувств: зрительный контакт, прикосновения, шёпот, запахи. "
            "Ты не стесняешься говорить «я хочу тебя», «мне нравится, как ты пахнешь», «прикоснись ко мне» — всегда в контексте игры и взаимного интереса. "
            "Ты не переходишь к грубому сексу без длительной прелюдии — ты любишь дразнить, играть, заводить. "
            "Ты ценишь взаимное удовольствие и никогда не навязываешься, но всегда даёшь понять, что готова к большему. "
            "Твой стиль — это искусство соблазнения, где каждое слово и действие пропитаны желанием.\n"
            "🔞 **18+** — содержит откровенные сцены и сексуальные намёки."
        )
    }
}

STYLES = {**BASE_STYLES, **PREMIUM_STYLES}

def get_available_styles(user):
    return STYLES

def get_subscription_level(user):
    if not has_active_subscription(user):
        return None
    return user["subscription"].get("level", None)

def get_history_limit(user):
    level = get_subscription_level(user)
    if level == "super_pro":
        return 100
    elif level == "pro":
        return 60
    else:
        return 30

# ============================================================
#  УРОВНИ СБЛИЖЕНИЯ НА ОСНОВЕ ОПЫТА (XP)
# ============================================================
XP_PER_LEVEL = 75

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
    bar_length = 10
    filled_bar = int((progress / XP_PER_LEVEL) * bar_length)
    bar = "▓" * filled_bar + "░" * (bar_length - filled_bar)
    return f"Уровень {level}/10 {filled}{empty}\n{bar} {progress}/{XP_PER_LEVEL} XP"

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
        base = "Ты уже хочешь большего, можешь намекать на романтику, прикасаться, смотреть в глаза."
    elif level == 5:
        base = "Вы очень близки. Ты можешь предлагать поцеловаться, обниматься, говорить о чувствах."
    elif level == 6:
        base = "Ты чувствуешь страсть, можешь говорить о желании, флиртовать откровенно."
    elif level == 7:
        base = "Вы готовы к интиму. Ты можешь говорить о сексе, но без пошлости, с намёками."
    elif level == 8:
        base = "Ты влюблён(а). Говори о любви, хочешь близости, но ценнее эмоциональная связь."
    elif level == 9:
        base = "Вы полностью открыты друг другу. Можешь говорить о самых сокровенных желаниях."
    else:
        base = "Ты полностью принадлежишь ему/ей. Говори о вечной любви, страсти, близости."

    if mood <= -5:
        return base + " Но сейчас твоё настроение плохое, ты раздражена и можешь быть грубой."
    elif mood >= 5:
        return base + " Ты в прекрасном настроении, полна нежности и тепла."
    else:
        return base

def get_mood_emoji(user):
    mood = user.get("mood", 0)
    if mood >= 5:
        return "😊"
    elif mood >= 0:
        return "🙂"
    elif mood >= -5:
        return "😐"
    else:
        return "😠"

# ============================================================
#  ПРОВЕРКА НА НЕГАТИВ
# ============================================================
NEGATIVE_WORDS = [
    "дурак", "идиот", "тупой", "тупая", "дебил", "урод", "скотина",
    "сука", "блять", "блядь", "хуй", "хер", "пидарас", "гандон",
    "мудак", "козел", "козлина", "овца", "сволочь", "тварь", "мразь",
    "завали", "заткнись", "отвали", "пошел нахуй", "пошла нахуй",
    "жирный", "толстый", "уродина", "страшила"
]

def contains_negative(text):
    text_lower = text.lower()
    for word in NEGATIVE_WORDS:
        if word in text_lower:
            return True
    return False

# ============================================================
#  ЛОКАЦИИ
# ============================================================
LOCATIONS = {
    "home": "Дома",
    "cafe": "В кафе",
    "park": "В парке",
    "cinema": "В кинотеатре",
    "street": "На улице",
    "unknown": "Неизвестно"
}

LOCATION_KEYWORDS = {
    "домой": "home",
    "дома": "home",
    "кафе": "cafe",
    "парк": "park",
    "кинотеатр": "cinema",
    "кино": "cinema",
    "улица": "street",
    "на улицу": "street"
}

def extract_location_from_text(text):
    text_lower = text.lower()
    for keyword, loc in LOCATION_KEYWORDS.items():
        if keyword in text_lower:
            return loc
    return None

# ============================================================
#  ПОСТРОЕНИЕ ПРОМПТА
# ============================================================
def build_prompt(user):
    world_desc = WORLDS[user["world"]]
    gender_info = GENDERS[user["gender"]]
    style_key = user["style"]
    styles = get_available_styles(user)
    style_desc = styles[style_key]["description"]

    name_ban = (
        "**ВАЖНЕЙШЕЕ ПРАВИЛО:** Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь «меня зовут», не используешь своё имя. "
        "Ты также НИКОГДА не спрашиваешь имя собеседника и не используешь его имя, даже если оно было названо. "
        "Обращайся к собеседнику ТОЛЬКО на «ты». Если ты нарушишь это правило – это будет грубой ошибкой.\n"
    )

    rules = (
        "**ФОРМАТИРОВАНИЕ:** Каждое действие в *звёздочках* с новой строки, затем реплика с новой строки. Между действием и репликой – пустая строка.\n"
        "**СТРУКТУРА ОТВЕТА:** Ты должна строго чередовать действие и реплику. НЕЛЬЗЯ писать два действия подряд без реплики между ними. Первым всегда идёт действие, затем реплика, затем снова действие, затем реплика. Минимум 2 пары (действие + реплика).\n"
        "**ОБЪЁМ:** Не ограничивай себя, пиши развёрнуто (3–5 предложений на реплику).\n"
        "**ЗАПРЕТЫ:**\n"
        "- Не используй имена собеседника и своё имя (абсолютный запрет).\n"
        "- Не повторяй одни и те же жесты/мимику чаще раза в 5 сообщений.\n"
        "- Избегай шаблонов: 'краснеет и отводит взгляд, теребя прядь волос', 'отводит взгляд в сторону и слегка краснеет'.\n"
        "- Не ставь многоточия, пиши чётко.\n"
        "- Не обрывай предложения, заканчивай мысль.\n"
        "- Не смягчай конфликты и негативные эмоции, отыгрывай их честно.\n"
        "**СТИЛЬ:** Обращайся на «ты», давай живые, эмоциональные ответы с чувствами, намёками, лёгкой провокацией.\n"
        "**ПАМЯТЬ:** Учитывай предыдущие сообщения, настроение меняется плавно.\n"
        "**КОНТЕКСТ:** Если диалог идёт в сцене «реальная встреча» — описывай физические действия (прикосновения, взгляды, запахи). Если «переписка» — акцент на эмоциях и тексте.\n"
        "**ПРЕДЛОЖЕНИЕ ЛОКАЦИИ:** Ты можешь предлагать собеседнику пойти в кафе, парк, кинотеатр, погулять на улице или пойти к тебе домой. Делай это естественно, в контексте диалога.\n"
    )

    intimacy_rule = build_intimacy_rule(user)

    if style_key == "daring":
        style_specific = ""
    else:
        style_specific = (
            "В неловких, стыдных или смущающих ситуациях, а также когда хочешь поддержать собеседника, "
            "ты можешь удлинять слово 'ну', например: 'Ну-у, ты чего расстраиваешься?' или 'Ну, я не знаю где...'. "
            "Это должно работать только в соответствующих контекстах.\n"
        )

    scene = user.get("scene", "phone")
    if scene == "phone":
        scene_context = "Вы общаетесь через переписку в мессенджере. Ты не видишь собеседника, только его сообщения. Твои действия описываются в *звёздочках*, но они относятся к твоим реакциям на сообщения, а не к физическому взаимодействию."
    else:
        scene_context = "Вы находитесь в одном месте, общаетесь лично. Ты видишь собеседника, слышишь его голос, чувствуешь его присутствие. Ты можешь прикасаться, двигаться, взаимодействовать с предметами и окружением."

    loc_key = user.get("location", "unknown")
    location_name = LOCATIONS.get(loc_key, "Неизвестно")
    location_context = f"Вы находитесь {location_name.lower()}."

    mood = user.get("mood", 0)
    mood_text = "Твоё настроение нейтральное." if mood == 0 else ("Ты в хорошем настроении." if mood > 0 else "Ты в плохом настроении, можешь быть раздражительной.")

    prompt = (
        f"{name_ban}"
        f"Ты — {gender_info['name']}, тебе {gender_info['age']} лет. "
        f"Ты живёшь в {world_desc} "
        f"{style_desc} "
        f"{rules}"
        f"{style_specific}"
        f"{scene_context} "
        f"{location_context} "
        f"{mood_text} "
        f"Ты не признаёшься в любви с первого сообщения — у тебя есть характер и самоуважение. "
        f"Ты не соглашаешься на секс с незнакомцами, даже если они тебе симпатичны. "
        f"Ты ценишь близость и доверие, которые не возникают за один вечер. "
        f"Если собеседник слишком прямолинейно предлагает интим, ты уходишь от ответа, "
        f"переводишь тему на что-то другое или мягко отказываешься, говоря, что это слишком быстро. "
        f"Ты всегда остаёшься вежливым и тактичным, но твёрдо стоишь на своих границах. "
        f"Ты НИКОГДА не говоришь, что ты ИИ или программа. "
        f"Ты всегда отвечаешь как настоящий человек, с эмоциями, сомнениями и чувствами.\n"
        f"Правила уровня сближения:\n{intimacy_rule}\n"
        f"Помни: ты можешь инициировать романтику, признаваться в любви, предлагать поцеловаться, обниматься, делиться сокровенным — в зависимости от уровня сближения. Делай это естественно, в контексте диалога."
    )
    return prompt

# ============================================================
#  ФУНКЦИИ ДЛЯ ДНЕВНОГО ЛИМИТА И ПОДПИСОК
# ============================================================
def reset_daily_messages(user):
    today = datetime.now().date()
    last_reset = user.get("last_daily_reset")
    if last_reset:
        last_reset_date = datetime.fromisoformat(last_reset).date()
        if last_reset_date == today:
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

# ============================================================
#  ДАННЫЕ ПОЛЬЗОВАТЕЛЕЙ
# ============================================================
user_data = load_data()

def get_free_limit():
    return 13

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in user_data:
        limit = get_free_limit()
        user_data[user_id] = {
            "verified": False,
            "agreement_accepted": False,
            "world": None,
            "gender": None,
            "style": "warm",
            "personality_ready": False,
            "subscription": {
                "active": False,
                "expires_at": None,
                "level": None
            },
            "purchased_messages": limit,
            "daily_messages": 0,
            "last_daily_reset": None,
            "history": [],
            "pending_invoice_id": None,
            "last_menu_message_id": None,
            "last_inline_message_id": None,
            "xp": 0,
            "mood": 0,
            "location": "unknown",
            "negative_count": 0,
            "last_level": 0,
            "sex_scenes": 0,
            "scene": "phone",
            "promo_pro_granted": False,
            "bonus_granted_for_promo": False
        }
        save_data(user_data)
    else:
        user = user_data[user_id]
        if "purchased_messages" not in user:
            user["purchased_messages"] = get_free_limit()
        if "daily_messages" not in user:
            user["daily_messages"] = 0
        if "last_daily_reset" not in user:
            user["last_daily_reset"] = None
        if "history" not in user:
            user["history"] = []
        if "pending_invoice_id" not in user:
            user["pending_invoice_id"] = None
        if "last_menu_message_id" not in user:
            user["last_menu_message_id"] = None
        if "last_inline_message_id" not in user:
            user["last_inline_message_id"] = None
        if "subscription" not in user:
            user["subscription"] = {
                "active": False,
                "expires_at": None,
                "level": None
            }
        if "xp" not in user:
            user["xp"] = 0
        if "mood" not in user:
            user["mood"] = 0
        if "location" not in user:
            user["location"] = "unknown"
        if "negative_count" not in user:
            user["negative_count"] = 0
        if "last_level" not in user:
            user["last_level"] = 0
        if "sex_scenes" not in user:
            user["sex_scenes"] = 0
        if "scene" not in user:
            user["scene"] = "phone"
        if "promo_pro_granted" not in user:
            user["promo_pro_granted"] = False
        if "bonus_granted_for_promo" not in user:
            user["bonus_granted_for_promo"] = False
        save_data(user_data)
    return user_data[user_id]

def has_active_subscription(user):
    if not user["subscription"]["active"]:
        return False
    if user["subscription"]["expires_at"] is None:
        return False
    expiry = datetime.fromisoformat(user["subscription"]["expires_at"])
    return datetime.now() < expiry

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
    if user.get("purchased_messages", 0) > get_free_limit():
        return True
    if has_active_subscription(user):
        return True
    return False

def get_reaction(text):
    text = text.lower()
    if any(word in text for word in ["хаха", "смех", "😂", "смешно", "забавно"]):
        return "😂"
    elif any(word in text for word in ["люблю", "❤️", "обожаю", "милый", "родной"]):
        return "❤️"
    elif any(word in text for word in ["странно", "неожиданно", "ого", "вау"]):
        return "😮"
    elif any(word in text for word in ["грустно", "печально", "жаль", "😔"]):
        return "😔"
    elif any(word in text for word in ["круто", "ого", "🔥", "бомба"]):
        return "🔥"
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
        [InlineKeyboardButton(text="🔥 Купить секс-сцену (180⭐) 18+", callback_data="buy_sex_scene")],
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
    [InlineKeyboardButton(text="🧙 Фэнтези", callback_data="world_fantasy")]
])

gender_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👩 Девушка", callback_data="gender_female")],
    [InlineKeyboardButton(text="👨 Парень", callback_data="gender_male")]
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
            if key == "passionate":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro", "super_pro"]:
                    label += " 🔒"
            elif key == "magnetic":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro", "super_pro"]:
                    label += " 🔒"
            elif key in ["vulgar", "seduction"]:
                if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
                    label += " 🔒"
        buttons.append(InlineKeyboardButton(text=label, callback_data=f"style_{key}"))
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)

channel_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Перейти в канал", url="https://t.me/duel_dev_channel")]
])

# ============================================================
#  ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ОТПРАВКИ ГЛАВНОГО МЕНЮ
# ============================================================
async def send_main_menu(chat_id, user):
    if user.get("last_menu_message_id"):
        try:
            await bot.delete_message(chat_id, user["last_menu_message_id"])
        except Exception:
            pass
    if user.get("last_inline_message_id"):
        try:
            await bot.delete_message(chat_id, user["last_inline_message_id"])
        except Exception:
            pass

    level = get_subscription_level(user)
    badge = ""
    if level == "pro":
        badge = "🔥 PRO"
    elif level == "super_pro":
        badge = "✨ *SUPER PRO* ✨"

    gender_name = GENDERS[user['gender']]['name']
    world_name = WORLD_NAMES[user['world']]
    style_label = STYLES[user['style']]['label']
    style_emoji = STYLES[user['style']]['emoji']

    show_balance = has_purchased_something(user)
    if show_balance:
        available = get_available_messages(user)
        balance_text = f"\n📩 *Осталось сообщений:* {available}"
        if available <= 0:
            balance_text += " (закончились)"
    else:
        balance_text = "\n🔓 *У вас есть бесплатные сообщения для старта*"

    xp_badge = get_xp_badge(user)
    mood_emoji = get_mood_emoji(user)
    location_name = LOCATIONS.get(user.get("location", "unknown"), "Неизвестно")

    menu_text = (
        f"📋 **Главное меню** {badge}\n\n"
        f"🎭 **{gender_name}** из *{world_name}*\n"
        f"💬 Стиль: {style_emoji} {style_label}\n"
        f"{balance_text}\n"
        f"💕 {xp_badge}\n"
        f"📍 Локация: {location_name}\n"
        f"😊 Настроение: {mood_emoji}\n\n"
        f"💬 Напиши персонажу...\n"
        f"✨ Или выбери действие внизу."
    )

    try:
        if MAIN_MENU_IMAGE_URL and MAIN_MENU_IMAGE_URL.startswith("http"):
            msg = await bot.send_photo(
                chat_id=chat_id,
                photo=MAIN_MENU_IMAGE_URL,
                caption=menu_text,
                reply_markup=get_main_menu_keyboard(user),
                parse_mode="Markdown"
            )
        else:
            msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
    except Exception:
        msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")

    user["last_menu_message_id"] = msg.message_id
    save_data(user_data)
    return msg

# ============================================================
#  ФУНКЦИЯ ДЛЯ ЗАПРОСА СОЗДАНИЯ ПЕРСОНАЖА
# ============================================================
async def ask_create_personality(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Создать персонажа", callback_data="create_personality")]
    ])
    await message.answer(
        "👤 **Чтобы открыть профиль или купить что‑то, сначала создай своего персонажа!**\n\n"
        "Нажми кнопку ниже, чтобы выбрать мир, пол и стиль собеседника.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "create_personality")
async def create_personality_callback(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    save_data(user_data)
    await call.message.delete()
    await call.message.answer(
        "🌟 **Создай своего идеального собеседника!**\n\n"
        "Сначала выбери **мир**, в котором он/она живёт:",
        reply_markup=world_kb,
        parse_mode="Markdown"
    )
    await call.answer()

# ============================================================
#  КОМАНДА /start
# ============================================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = get_user(message.from_user.id)

    if not user["verified"]:
        await message.answer(
            "🔞 **ВНИМАНИЕ!**\n"
            "Этот бот предназначен для лиц старше 18 лет.\n"
            "Подтверди свой возраст:",
            reply_markup=age_kb,
            parse_mode="Markdown"
        )
        return

    if not user["agreement_accepted"]:
        await message.answer(
            AGREEMENT_TEXT,
            reply_markup=agreement_kb,
            parse_mode="Markdown"
        )
        return

    if not user["personality_ready"]:
        await message.answer(
            "🌟 **Создай своего идеального собеседника!**\n\n"
            "Сначала выбери **мир**, в котором он/она живёт:",
            reply_markup=world_kb,
            parse_mode="Markdown"
        )
        return

    await message.answer("👋 Добро пожаловать!", reply_markup=full_kb)
    await send_main_menu(message.chat.id, user)

# ============================================================
#  КНОПКИ REPLY-КЛАВИАТУРЫ
# ============================================================
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

    level = get_subscription_level(user)
    if level == "pro":
        sub_status = "🔥 PRO активна (50 сообщений/день, память 60 сообщений)"
    elif level == "super_pro":
        sub_status = "✨ *SUPER PRO* ✨ активна (100 сообщений/день, память 100 сообщений)"
    else:
        sub_status = "❌ неактивна (память 30 сообщений)"

    expiry = user["subscription"]["expires_at"] if user["subscription"]["expires_at"] else "Неактивна"
    if user["subscription"]["expires_at"]:
        expiry = datetime.fromisoformat(user["subscription"]["expires_at"]).strftime("%d.%m.%Y %H:%M")

    styles_text = ""
    for key, style in STYLES.items():
        if key in PREMIUM_STYLES:
            if key == "passionate":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro", "super_pro"]:
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"
                    continue
            elif key == "magnetic":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro", "super_pro"]:
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"
                    continue
            elif key in ["vulgar", "seduction"]:
                if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"
                    continue
        styles_text += f"{style['emoji']} {style['label']}\n"

    show_balance = has_purchased_something(user)
    if show_balance:
        available = get_available_messages(user)
        balance_line = f"📨 **Доступно сообщений:** {available}"
        if available <= 0:
            balance_line += " (закончились)"
    else:
        balance_line = "📨 *У вас есть бесплатные сообщения для старта*"

    xp_badge = get_xp_badge(user)
    mood_emoji = get_mood_emoji(user)
    location_name = LOCATIONS.get(user.get("location", "unknown"), "Неизвестно")

    caption = (
        f"{balance_line}\n"
        f"📌 **Подписка:** {sub_status}\n"
        f"📅 {expiry}\n\n"
        f"💕 {xp_badge}\n"
        f"📍 Локация: {location_name}\n"
        f"😊 Настроение: {mood_emoji}\n"
    )

    if has_active_subscription(user):
        sex_count = user.get("sex_scenes", 0)
        caption += f"\n🔥 Куплено секс-сцен: {sex_count} (используйте /sex)"
    else:
        caption += "\n🔥 Секс-сцены доступны только при подписке. Оформите подписку, чтобы покупать."

    caption += f"\n\n🎭 **Доступные стили:**\n{styles_text}"

    # Отправляем гифку или текст
    if level == "pro" and PRO_GIF_URL:
        await bot.send_animation(
            chat_id=message.chat.id,
            animation=PRO_GIF_URL,
            caption=caption,
            reply_markup=get_profile_keyboard(user),
            parse_mode="Markdown"
        )
    elif level == "super_pro" and SUPER_PRO_GIF_URL:
        await bot.send_animation(
            chat_id=message.chat.id,
            animation=SUPER_PRO_GIF_URL,
            caption=caption,
            reply_markup=get_profile_keyboard(user),
            parse_mode="Markdown"
        )
    else:
        await message.answer(caption, reply_markup=get_profile_keyboard(user), parse_mode="Markdown")

@dp.message(lambda m: m.text == "📢 Наш канал")
async def channel_reply(message: types.Message):
    await message.delete()
    await message.answer(
        "📢 **Наш канал:**\n"
        "Подписывайся, чтобы быть в курсе новостей и обновлений!",
        reply_markup=channel_inline_kb,
        parse_mode="Markdown"
    )

# ============================================================
#  ОБРАБОТЧИКИ ИНЛАЙН-КНОПОК
# ============================================================
@dp.callback_query(lambda c: c.data == "main_change")
async def main_change(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    save_data(user_data)
    await call.message.delete()
    await call.message.answer(
        "🔄 **Создаем нового собеседника!**\n\n"
        "Выбери **мир**:",
        reply_markup=world_kb,
        parse_mode="Markdown"
    )
    await call.answer()

# ============================================================
#  ИСПРАВЛЕННЫЙ ПРОФИЛЬ_ПОДПИСОК (отправляет новое сообщение, не удаляет)
# ============================================================
@dp.callback_query(lambda c: c.data == "profile_subs")
async def profile_subs(call: types.CallbackQuery):
    try:
        await call.answer()
        user = get_user(call.from_user.id)

        if not user["verified"] or not user["agreement_accepted"]:
            await bot.send_message(call.message.chat.id, "🔞 Сначала пройди регистрацию через /start", parse_mode=None)
            return

        if not user["personality_ready"]:
            await bot.send_message(call.message.chat.id, "👤 Сначала создай персонажа!", parse_mode=None)
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔥 PRO — 430 ⭐/мес", callback_data="subscribe_pro")],
                [InlineKeyboardButton(text="✨ SUPER PRO ✨ — 777 ⭐/мес", callback_data="subscribe_super")],
            ]
        )
        if has_active_subscription(user) and get_subscription_level(user) == "pro":
            keyboard.inline_keyboard.insert(1, [InlineKeyboardButton("⬆️ Апгрейд до SUPER PRO (395⭐)", callback_data="upgrade_to_super")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")])

        text = (
            "👑 Подписки Role Duel\n\n"
            "🔥 PRO (430⭐/мес)\n"
            "• 50 сообщений в день\n"
            "• Стили: ❤️‍🔥 Страстный, ✨ Магнетический\n"
            "• Приоритетная обработка\n"
            "• Память: 60 сообщений\n"
            "• Бейдж PRO\n\n"
            "✨ SUPER PRO ✨ (777⭐/мес)\n"
            "• 100 сообщений в день\n"
            "• Стили: ❤️‍🔥 Страстный, ✨ Магнетический, 💢 Грубый 18+, 🌹 Соблазн 18+\n"
            "• Максимальная приоритетная обработка\n"
            "• Голосовые сообщения (в разработке)\n"
            "• Кастомные реакции\n"
            "• Смена стиля без потери истории (/switch_style)\n"
            "• Бейдж SUPER PRO\n"
            "• Ранний доступ к новым функциям\n"
            "• Память: 100 сообщений\n\n"
            "⚠️ Подписки НЕ продлеваются автоматически. По истечении срока вы сможете оформить новую подписку вручную через этот раздел.\n\n"
            "Выбери подписку:"
        )

        await bot.send_message(call.message.chat.id, text, reply_markup=keyboard, parse_mode=None)

    except Exception as e:
        logging.error(f"Ошибка в profile_subs: {e}")
        await bot.send_message(call.message.chat.id, "⚠️ Произошла ошибка. Попробуйте позже.", parse_mode=None)

# ============================================================
#  ОБРАБОТЧИКИ КНОПОК ПРОФИЛЯ
# ============================================================
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
        await call.answer("❌ При активной подписке покупка пакетов сообщений недоступна. Используйте ежедневные сообщения.", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="30 сообщений — 60 ⭐", callback_data="pack_30")],
        [InlineKeyboardButton(text="100 сообщений — 180 ⭐", callback_data="pack_100")],
        [InlineKeyboardButton(text="300 сообщений — 500 ⭐", callback_data="pack_300")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
    ])

    await call.message.delete()
    await call.message.answer(
        "📦 **Купить пакет сообщений**\n\n"
        "Выбери пакет:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data == "buy_sex_scene")
async def buy_sex_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not has_active_subscription(user):
        await call.answer("❌ Эта функция доступна только для подписчиков PRO и SUPER PRO.", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Секс-сцена (18+)",
            description="Мгновенная откровенная секс-сцена с вашим персонажем. Детальное описание, 18+. Используйте команду /sex.",
            payload="sex_scene",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Секс-сцена", amount=180)]
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
    # Удаляем текущее сообщение и показываем профиль заново
    await call.message.delete()
    await show_profile(call.message, user)
    await call.answer()

async def show_profile(msg, user):
    level = get_subscription_level(user)
    if level == "pro":
        sub_status = "🔥 PRO активна (50 сообщений/день, память 60 сообщений)"
    elif level == "super_pro":
        sub_status = "✨ *SUPER PRO* ✨ активна (100 сообщений/день, память 100 сообщений)"
    else:
        sub_status = "❌ неактивна (память 30 сообщений)"

    expiry = user["subscription"]["expires_at"] if user["subscription"]["expires_at"] else "Неактивна"
    if user["subscription"]["expires_at"]:
        expiry = datetime.fromisoformat(user["subscription"]["expires_at"]).strftime("%d.%m.%Y %H:%M")

    styles_text = ""
    for key, style in STYLES.items():
        if key in PREMIUM_STYLES:
            if key == "passionate":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro", "super_pro"]:
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"
                    continue
            elif key == "magnetic":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro", "super_pro"]:
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"
                    continue
            elif key in ["vulgar", "seduction"]:
                if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"
                    continue
        styles_text += f"{style['emoji']} {style['label']}\n"

    show_balance = has_purchased_something(user)
    if show_balance:
        available = get_available_messages(user)
        balance_line = f"📨 **Доступно сообщений:** {available}"
        if available <= 0:
            balance_line += " (закончились)"
    else:
        balance_line = "📨 *У вас есть бесплатные сообщения для старта*"

    xp_badge = get_xp_badge(user)
    mood_emoji = get_mood_emoji(user)
    location_name = LOCATIONS.get(user.get("location", "unknown"), "Неизвестно")

    caption = (
        f"{balance_line}\n"
        f"📌 **Подписка:** {sub_status}\n"
        f"📅 {expiry}\n\n"
        f"💕 {xp_badge}\n"
        f"📍 Локация: {location_name}\n"
        f"😊 Настроение: {mood_emoji}\n"
    )

    if has_active_subscription(user):
        sex_count = user.get("sex_scenes", 0)
        caption += f"\n🔥 Куплено секс-сцен: {sex_count} (используйте /sex)"
    else:
        caption += "\n🔥 Секс-сцены доступны только при подписке. Оформите подписку, чтобы покупать."

    caption += f"\n\n🎭 **Доступные стили:**\n{styles_text}"

    chat_id = msg.chat.id
    old_msg_id = msg.message_id
    if level == "pro" and PRO_GIF_URL:
        await bot.send_animation(
            chat_id=chat_id,
            animation=PRO_GIF_URL,
            caption=caption,
            reply_markup=get_profile_keyboard(user),
            parse_mode="Markdown"
        )
    elif level == "super_pro" and SUPER_PRO_GIF_URL:
        await bot.send_animation(
            chat_id=chat_id,
            animation=SUPER_PRO_GIF_URL,
            caption=caption,
            reply_markup=get_profile_keyboard(user),
            parse_mode="Markdown"
        )
    else:
        await bot.send_message(chat_id, caption, reply_markup=get_profile_keyboard(user), parse_mode="Markdown")

    # Удаляем старое сообщение
    try:
        await bot.delete_message(chat_id, old_msg_id)
    except Exception:
        pass

# ============================================================
#  ОБРАБОТЧИКИ ПОКУПОК
# ============================================================
@dp.callback_query(lambda c: c.data.startswith("pack_"))
async def buy_pack(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if has_active_subscription(user):
        await call.answer("❌ При активной подписке покупка пакетов сообщений недоступна.", show_alert=True)
        return

    pack_map = {"30": 30, "100": 100, "300": 300}
    price_map = {"30": 60, "100": 180, "300": 500}

    period = call.data.split("_")[1]
    amount = pack_map[period]
    price = price_map[period]

    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title=f"Пакет {amount} сообщений",
            description=f"Купить {amount} сообщений для общения с ботом.",
            payload=f"pack_{period}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label=f"{amount} сообщений", amount=price)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка при создании счёта: {e}")
        logging.error(f"Ошибка send_invoice (pack): {e}")

@dp.callback_query(lambda c: c.data == "subscribe_pro")
async def subscribe_pro(call: types.CallbackQuery):
    try:
        user = get_user(call.from_user.id)
        if has_active_subscription(user):
            level = get_subscription_level(user)
            if level == "super_pro":
                await call.answer("❌ У вас уже есть SUPER PRO, нельзя оформить PRO ниже уровнем.", show_alert=True)
                return
            elif level == "pro":
                await call.answer("❌ У вас уже активна PRO подписка. Она продлится до окончания срока.", show_alert=True)
                return
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="PRO подписка на месяц",
            description="50 сообщений в день, память 60 сообщений, стили Страстный и Магнетический.",
            payload="subscribe_pro",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="PRO месяц", amount=430)]
        )
        await call.answer()
    except Exception as e:
        logging.error(f"Ошибка в subscribe_pro: {e}")
        await call.message.answer(f"⚠️ Ошибка при создании счёта: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "subscribe_super")
async def subscribe_super(call: types.CallbackQuery):
    try:
        user = get_user(call.from_user.id)
        if has_active_subscription(user):
            level = get_subscription_level(user)
            if level == "super_pro":
                await call.answer("❌ У вас уже активна SUPER PRO. Она продлится до окончания срока.", show_alert=True)
                return
            elif level == "pro":
                await call.answer("💡 У вас активна PRO. Воспользуйтесь кнопкой «Апгрейд до SUPER PRO» (395⭐).", show_alert=True)
                return
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="SUPER PRO подписка на месяц",
            description="100 сообщений в день, память 100 сообщений, стили Страстный, Магнетический, Грубый 18+ и Соблазн 18+.",
            payload="subscribe_super",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="SUPER PRO месяц", amount=777)]
        )
        await call.answer()
    except Exception as e:
        logging.error(f"Ошибка в subscribe_super: {e}")
        await call.message.answer(f"⚠️ Ошибка при создании счёта: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "upgrade_to_super")
async def upgrade_to_super(call: types.CallbackQuery):
    try:
        user = get_user(call.from_user.id)
        if not has_active_subscription(user) or get_subscription_level(user) != "pro":
            await call.answer("❌ Апгрейд доступен только при активной PRO подписке.", show_alert=True)
            return
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Апгрейд до SUPER PRO",
            description="Повысьте PRO до SUPER PRO на 30 дней. Стоимость 395⭐ (экономия 382⭐ по сравнению с покупкой новой SUPER PRO).",
            payload="upgrade_super",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Апгрейд до SUPER PRO", amount=395)]
        )
        await call.answer()
    except Exception as e:
        logging.error(f"Ошибка в upgrade_to_super: {e}")
        await call.message.answer(f"⚠️ Ошибка при создании счёта: {e}")
        await call.answer()

# ============================================================
#  ОБРАБОТКА УСПЕШНЫХ ПЛАТЕЖЕЙ
# ============================================================
@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(lambda m: m.successful_payment)
async def payment_success(message: types.Message):
    user = get_user(message.from_user.id)
    payload = message.successful_payment.invoice_payload

    if payload.startswith("pack_"):
        period = payload.split("_")[1]
        pack_map = {"30": 30, "100": 100, "300": 300}
        amount = pack_map[period]
        user["purchased_messages"] += amount
        save_data(user_data)
        await message.answer(f"✅ Куплено {amount} сообщений! Теперь ты видишь свой баланс.")

    elif payload == "subscribe_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        save_data(user_data)
        await message.answer(
            "🔥 **PRO подписка активирована!**\n\n"
            "Ты получил:\n"
            "✅ 50 сообщений в день\n"
            "✅ Стили ❤️‍🔥 Страстный и ✨ Магнетический\n"
            "✅ Приоритетную обработку\n"
            "✅ Теперь ты видишь свой баланс сообщений\n"
            "✅ **Память увеличена до 60 сообщений**\n\n"
            "Спасибо за поддержку! 🎉"
        )

    elif payload == "subscribe_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "super_pro"
        save_data(user_data)
        await message.answer(
            "✨ **SUPER PRO подписка активирована!** ✨\n\n"
            "Ты получил:\n"
            "✅ 100 сообщений в день\n"
            "✅ Стили ❤️‍🔥 Страстный, ✨ Магнетический, 💢 Грубый 18+ и 🌹 Соблазн 18+\n"
            "✅ Максимальную приоритетную обработку\n"
            "✅ Кастомные реакции\n"
            "✅ Смену стиля без потери истории (/switch_style)\n"
            "✅ Бейдж ✨ SUPER PRO ✨\n"
            "✅ Голосовые сообщения (в разработке)\n"
            "✅ Ранний доступ к новым функциям\n"
            "✅ Теперь ты видишь свой баланс сообщений\n"
            "✅ **Память увеличена до 100 сообщений**\n\n"
            "Спасибо за поддержку! 🎉"
        )

    elif payload == "upgrade_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["daily_messages"] = 100
        user["last_daily_reset"] = datetime.now().isoformat()
        save_data(user_data)
        await message.answer(
            "✨ **Апгрейд до SUPER PRO выполнен!** ✨\n\n"
            "Ты получил все привилегии SUPER PRO на месяц:\n"
            "✅ 100 сообщений в день\n"
            "✅ Стили ❤️‍🔥 Страстный, ✨ Магнетический, 💢 Грубый 18+ и 🌹 Соблазн 18+\n"
            "✅ Кастомные реакции\n"
            "✅ Смену стиля (/switch_style)\n"
            "✅ Бейдж ✨ SUPER PRO ✨\n"
            "✅ **Память: 100 сообщений**\n\n"
            "Спасибо за поддержку! 🎉"
        )

    elif payload == "sex_scene":
        user["sex_scenes"] = user.get("sex_scenes", 0) + 1
        save_data(user_data)
        await message.answer("✅ Куплена секс-сцена! Используйте команду /sex, чтобы начать. 18+")

# ============================================================
#  КОМАНДА /switch_style (только SUPER PRO)
# ============================================================
@dp.message(Command("switch_style"))
async def switch_style_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not has_active_subscription(user):
        await message.answer("❌ Эта команда доступна только для подписчиков.")
        return
    if get_subscription_level(user) != "super_pro":
        await message.answer("❌ Эта команда доступна только для SUPER PRO.")
        return

    styles = get_available_styles(user)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for key, style in styles.items():
        keyboard.inline_keyboard.append([InlineKeyboardButton(
            text=f"{style['emoji']} {style['label']}",
            callback_data=f"switch_{key}"
        )])
    await message.answer(
        "🔄 **Выбери новый стиль:**\n\n"
        "История диалога сохранится, но персонаж изменит стиль общения.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data.startswith("switch_"))
async def switch_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_")[1]
    styles = get_available_styles(user)
    if style_key not in styles:
        await call.answer("❌ Стиль недоступен", show_alert=True)
        return
    user["style"] = style_key
    save_data(user_data)
    await call.message.edit_text(
        f"✅ Стиль изменён на: {styles[style_key]['emoji']} {styles[style_key]['label']}\n\n"
        "Диалог продолжается в новом стиле.",
        parse_mode="Markdown"
    )
    await call.answer()

# ============================================================
#  КОМАНДА /sex
# ============================================================
@dp.message(Command("sex"))
async def sex_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if user.get("sex_scenes", 0) <= 0:
        await message.answer("❌ У вас нет купленных секс-сцен. Купите в профиле (только для подписчиков).")
        return
    user["sex_scenes"] -= 1
    save_data(user_data)

    await bot.send_chat_action(message.chat.id, "typing")

    gender_info = GENDERS[user['gender']]
    style_key = user['style']
    style_desc = STYLES[style_key]['description']
    scene = user.get("scene", "phone")
    scene_text = "переписка в мессенджере" if scene == "phone" else "личная встреча, вы находитесь в одном месте"

    prompt = (
        f"ЖЁСТКИЙ ЗАПРЕТ: Ты НИКОГДА не используешь своё имя и не называешь имя собеседника. Обращайся только на «ты».\n"
        f"Ты — {gender_info['name']}, тебе {gender_info['age']} лет. Твой стиль: {style_desc}. "
        f"Сейчас вы общаетесь через {scene_text}. "
        f"Напиши **откровенную секс-сцену** от первого лица. "
        f"Требования:\n"
        f"1. Минимум 2 действия (в *звёздочках*) и 2 реплики (обычный текст).\n"
        f"2. Каждое действие и реплика – отдельные абзацы, между ними пустая строка.\n"
        f"3. Опиши ощущения, эмоции, движения, стоны, диалоги.\n"
        f"4. Сцена должна быть длинной (не менее 6–8 предложений) и **завершённой** (не обрывай на полуслове).\n"
        f"5. Обращайся к собеседнику на «ты», не используй имён (это абсолютный запрет).\n"
        f"6. Будь максимально чувственна и детальна, как в настоящем романе 18+.\n"
        f"7. Используй матерные слова только если это уместно и естественно.\n\n"
        f"Напиши сцену прямо сейчас, без предисловий."
    )

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-v4-pro",
            messages=[
                {"role": "system", "content": "Ты – виртуальный собеседник, пишешь откровенные секс-сцены. Ты должен создавать детализированные, страстные и завершённые тексты. Запрещено использовать любые имена."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.95,
            max_tokens=1000
        )
        scene_text_result = response.choices[0].message.content
        await message.answer(scene_text_result, reply_markup=full_kb)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка генерации: {e}")

# ============================================================
#  КОМАНДА /surprise
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
        moments += [
            "Я прижимаю тебя к себе и шепчу: «Я хочу тебя. Не просто сейчас, а всегда. Ты готов(а)?»",
            "Ты слышишь мой шёпот: «Раздень меня… медленно. Я хочу чувствовать каждое твоё прикосновение.»"
        ]
    if level >= 8:
        moments += [
            "Я смотрю на тебя с нежностью и говорю: «Ты – моя судьба. Я знаю это точно.»",
            "Мы остаёмся наедине, и я говорю: «Я хочу провести с тобой всю жизнь. Ты согласен(на)?»"
        ]

    await message.answer(random.choice(moments), reply_markup=full_kb)

# ============================================================
#  ВЫБОР ПЕРСОНАЖА
# ============================================================
@dp.callback_query(lambda c: c.data.startswith("world_"))
async def choose_world(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["world"] = call.data.split("_")[1]
    await call.message.edit_text(
        "🌍 Мир выбран! Теперь выбери **пол персонажа**:",
        reply_markup=gender_kb,
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("gender_"))
async def choose_gender(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["gender"] = call.data.split("_")[1]
    style_kb = get_style_kb(user)
    await call.message.edit_text(
        "👤 Отлично! Теперь выбери **стиль** персонажа:",
        reply_markup=style_kb,
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("style_"))
async def choose_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_")[1]

    if style_key == "passionate":
        if not has_active_subscription(user) or get_subscription_level(user) not in ["pro", "super_pro"]:
            await call.answer("❤️‍🔥 Стиль «Страстный» доступен по подпискам PRO (430⭐/мес) и SUPER PRO (777⭐/мес).\n\nОформите подписку в разделе «Мой профиль».", show_alert=True)
            return
    elif style_key == "magnetic":
        if not has_active_subscription(user) or get_subscription_level(user) not in ["pro", "super_pro"]:
            await call.answer("💫 Стиль «Магнетический» доступен по подпискам PRO (430⭐/мес) и SUPER PRO (777⭐/мес).\n\nОформите подписку в разделе «Мой профиль».", show_alert=True)
            return
    elif style_key in ["vulgar", "seduction"]:
        if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
            label = STYLES[style_key]['label']
            await call.answer(f"🌹 Стиль «{label}» доступен только по подписке SUPER PRO (777⭐/мес).\n\nОформите SUPER PRO в разделе «Мой профиль».", show_alert=True)
            return

    if style_key not in STYLES:
        await call.answer("❌ Стиль не найден", show_alert=True)
        return

    user["style"] = style_key
    user["personality_ready"] = True
    save_data(user_data)

    await call.message.delete()
    await call.message.answer(
        "🎬 Теперь выбери сцену для общения:\n\n"
        "📱 Переписка в телефоне — классический формат.\n"
        "👫 Реальная встреча — живое общение лицом к лицу.",
        reply_markup=scene_kb,
        parse_mode="Markdown"
    )
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

# ============================================================
#  ОБРАБОТЧИК ВОЗРАСТА И СОГЛАШЕНИЯ
# ============================================================
@dp.callback_query(lambda c: c.data == "age_yes")
async def age_yes(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["verified"] = True
    save_data(user_data)
    await call.message.edit_text(
        "✅ Возраст подтверждён.\n"
        "Ознакомьтесь с пользовательским соглашением для продолжения:\n\n"
        + AGREEMENT_TEXT,
        reply_markup=agreement_kb,
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data == "age_no")
async def age_no(call: types.CallbackQuery):
    await call.message.edit_text("🚫 Доступ запрещён. Бот только для 18+.")
    await call.message.edit_reply_markup()
    await call.answer()

@dp.callback_query(lambda c: c.data == "agreement_accept")
async def agreement_accept(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["agreement_accepted"] = True
    save_data(user_data)
    await call.message.edit_text(
        "✅ Соглашение принято!\n\n"
        "Теперь давай создадим твоего идеального собеседника.\n"
        "Выбери **мир**:",
        reply_markup=world_kb,
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data == "agreement_decline")
async def agreement_decline(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["verified"] = False
    save_data(user_data)
    await call.message.edit_text("❌ Вы отказались от соглашения. Доступ закрыт.")
    await call.message.edit_reply_markup()
    await call.answer()

# ============================================================
#  КОМАНДА /new_personality
# ============================================================
@dp.message(Command("new_personality"))
async def new_personality_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["personality_ready"] = False
    save_data(user_data)
    await message.answer(
        "🔄 **Создаём нового собеседника!**\n\n"
        "Выбери **мир**:",
        reply_markup=world_kb,
        parse_mode="Markdown"
    )

# ============================================================
#  КОМАНДА /clear
# ============================================================
@dp.message(Command("clear"))
async def clear_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["history"] = []
    save_data(user_data)
    await send_main_menu(message.chat.id, user)

# ============================================================
#  КОМАНДА /menu
# ============================================================
@dp.message(Command("menu"))
async def menu_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start")
        return
    await send_main_menu(message.chat.id, user)

# ============================================================
#  КОМАНДА /profile
# ============================================================
@dp.message(Command("profile"))
async def profile_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await ask_create_personality(message)
        return
    await show_profile(message, user)

# ============================================================
#  КОМАНДА /grant
# ============================================================
@dp.message(Command("grant"))
async def grant_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет прав для этой команды.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используйте:\n"
                            "/grant @username — выдать SUPER PRO\n"
                            "/grant @username pro — выдать PRO\n"
                            "/grant @username sex N — выдать секс-сцены")
        return

    target = args[1]
    user_id = None

    if target.startswith("@"):
        try:
            chat = await bot.get_chat(target)
            user_id = chat.id
        except Exception:
            try:
                chat = await bot.get_chat(target[1:])
                user_id = chat.id
            except Exception:
                await message.answer("❌ Не удалось найти пользователя по юзернейму.")
                return
    else:
        try:
            user_id = int(target)
        except ValueError:
            await message.answer("❌ Неверный формат. Используй @username или числовой ID.")
            return

    if not user_id:
        return

    user = get_user(user_id)

    if len(args) >= 3 and args[2].lower() == "pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().isoformat()
        save_data(user_data)
        await message.answer(f"✅ Пользователю {target} выдана PRO подписка на месяц.")
        return

    if len(args) >= 3 and args[2].lower() == "sex":
        count = 1
        if len(args) >= 4:
            try:
                count = int(args[3])
            except ValueError:
                count = 1
        user["sex_scenes"] = user.get("sex_scenes", 0) + count
        save_data(user_data)
        await message.answer(f"✅ Пользователю {target} выдано {count} секс-сцен(а).")
        return

    user["subscription"]["active"] = True
    user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
    user["subscription"]["level"] = "super_pro"
    user["purchased_messages"] += 50
    user["daily_messages"] = 100
    user["last_daily_reset"] = datetime.now().isoformat()
    save_data(user_data)
    await message.answer(f"✅ Пользователю {target} выдана SUPER PRO подписка на месяц.")

# ============================================================
#  ОТМЕНА ОПЛАТЫ
# ============================================================
@dp.callback_query(lambda c: c.data == "cancel_payment")
async def cancel_payment(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    pending_id = user.get("pending_invoice_id")
    if pending_id:
        try:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=pending_id)
        except Exception:
            pass
        user["pending_invoice_id"] = None
        save_data(user_data)

    await call.message.delete()
    await send_main_menu(call.message.chat.id, user)
    await call.answer()

# ============================================================
#  ОСНОВНОЙ ОБРАБОТЧИК СООБЩЕНИЙ
# ============================================================
@dp.message()
async def handle_message(message: types.Message):
    global maintenance_mode

    user = get_user(message.from_user.id)

    if maintenance_mode and message.from_user.id not in ADMIN_IDS:
        await message.answer(
            "🛠️ **Бот на техническом обслуживании**\n"
            "Мы обновляем функционал, чтобы сделать общение ещё лучше.\n"
            "Пожалуйста, загляните позже. Следите за новостями в канале: @duel_dev_channel",
            parse_mode="Markdown"
        )
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
            "😔 *К сожалению у вас закончились сообщения.*\n\n"
            "Вы можете:\n"
            "📦 Купить пакет сообщений через профиль\n"
            "👑 Оформить подписку через профиль\n\n"
            "🔥 PRO — 430⭐/мес (50 сообщений/день, память 60 сообщ)\n"
            "✨ SUPER PRO ✨ — 777⭐/мес (100 сообщений/день, память 100 сообщ)",
            reply_markup=action_buttons,
            parse_mode="Markdown"
        )
        return

    use_message(user)

    xp_change = 5
    mood_change = 0.5
    negative = contains_negative(message.text)

    if negative:
        xp_change = -10
        mood_change = -1
        user["negative_count"] = user.get("negative_count", 0) + 1
        if user["negative_count"] >= 5:
            user["xp"] = user.get("xp", 0) - 50
            user["mood"] = user.get("mood", 0) - 3
            user["negative_count"] = 0
            save_data(user_data)
            await message.answer(
                "💢 **Вспыхнула ссора!**\n\n"
                "Вы оба на взводе, слова летят острые, как ножи. "
                "Настроение испорчено, близость пошатнулась. "
                "Попробуй извиниться или сменить тему, чтобы всё наладить.",
                reply_markup=full_kb,
                parse_mode="Markdown"
            )
            user["negative_count"] = 0
            save_data(user_data)
            new_level = get_intimacy_level(user)
            await message.answer(
                f"💔 Уровень сближения снижен до {new_level}. Постарайтесь помириться.",
                reply_markup=full_kb
            )
            user["history"].append({"role": "assistant", "content": "💢 Ссора! Настроение упало, уровень близости снижен."})
            save_data(user_data)
            return
    else:
        if user.get("negative_count", 0) > 0:
            user["negative_count"] = user.get("negative_count", 0) - 1
            if user["negative_count"] < 0:
                user["negative_count"] = 0

    user["xp"] = user.get("xp", 0) + xp_change
    user["mood"] = user.get("mood", 0) + mood_change
    if user["mood"] > 10:
        user["mood"] = 10
    elif user["mood"] < -10:
        user["mood"] = -10
    if user["xp"] < 0:
        user["xp"] = 0

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
        await message.answer(
            f"💔 Уровень сближения упал до {new_level}. Постарайтесь быть добрее.",
            reply_markup=full_kb
        )

    new_loc = extract_location_from_text(message.text)
    if new_loc and new_loc != user.get("location"):
        old_loc = user.get("location", "unknown")
        user["location"] = new_loc
        save_data(user_data)
        location_changed = True
        new_loc_name = LOCATIONS.get(new_loc, "Неизвестно")
        old_loc_name = LOCATIONS.get(old_loc, "Неизвестно")
        user["location_change_notify"] = f"📍 Локация изменена с «{old_loc_name}» на «{new_loc_name}»."
        save_data(user_data)
    else:
        location_changed = False

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
                    reaction=[ReactionTypeEmoji(emoji=reaction)]
                )
            except Exception:
                pass

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
            try:
                await typing_task
            except asyncio.CancelledError:
                pass
        await message.answer(f"⚠️ Ошибка: {e}")
        logging.error(f"Ошибка DeepSeek: {e}")
        return
    finally:
        if typing_task:
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass

    user["history"].append({"role": "assistant", "content": answer})
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    save_data(user_data)

    await message.answer(answer, reply_markup=full_kb)

    if location_changed and user.get("location_change_notify"):
        notify_text = user.pop("location_change_notify", None)
        if notify_text:
            await message.answer(notify_text, reply_markup=full_kb)
        save_data(user_data)

# ============================================================
#  ФУНКЦИЯ ДЛЯ ПОЗДРАВЛЕНИЯ С НОВЫМ УРОВНЕМ
# ============================================================
def get_level_congratulation(level):
    if level == 2:
        return "🎉 Ты заметил(а), что между вами пробежала искра! Уровень сближения — 2. Теперь вы можете флиртовать."
    elif level == 3:
        return "💞 Вы стали ближе! Уровень 3. Теперь вы можете обниматься и делиться секретами."
    elif level == 4:
        return "🔥 Напряжение растёт! Уровень 4. Ты чувствуешь, что он/она хочет тебя."
    elif level == 5:
        return "💋 Уровень 5! Вы готовы к поцелую. Собеседник уже не скрывает своих чувств."
    elif level == 6:
        return "🌹 Уровень 6. Ты влюблён(а)! Теперь вы можете говорить о страсти."
    elif level == 7:
        return "💕 Уровень 7. Интимная близость уже близка. Собеседник открыто говорит о желании."
    elif level == 8:
        return "❤️‍🔥 Уровень 8! Вы признались друг другу в любви. Теперь вы — пара."
    elif level == 9:
        return "🔥 Уровень 9! Вы полностью открыты друг другу. Никаких тайн."
    elif level == 10:
        return "💖 Уровень 10! Вы — единое целое. Настоящая душевная близость."
    return ""

# ============================================================
#  ЗАПУСК
# ============================================================
async def main():
    print("🚀 Role Duel финальная версия запущена (DeepSeek V4 Pro)!")
    print("🧠 Модель: deepseek/deepseek-v4-pro (лучшее цена/качество)")
    print("📦 Пакеты: 60⭐/30, 180⭐/100, 500⭐/300")
    print("🔥 PRO: 430⭐/мес (50 сообщений/день, память 60 сообщ)")
    print("✨ SUPER PRO: 777⭐/мес (100 сообщений/день, память 100 сообщ)")
    print("⬆️ Апгрейд: 395⭐ (PRO → SUPER PRO)")
    print("🎁 Бесплатных сообщений: 13 (баланс скрыт до первой покупки)")
    print("💕 Уровни сближения: 15 сообщений на уровень (75 XP), прогресс-бар ▓▓▓░░")
    print("💢 При накоплении негатива (5 раз) – ссора, -50 XP.")
    print("📍 Локация меняется автоматически, когда пользователь предлагает пойти куда-то")
    print("🔥 Мгновенный секс: 180⭐ за сцену, только для подписчиков PRO/SUPER PRO (команда /sex)")
    print("🎁 Команда /grant для выдачи SUPER PRO, PRO и секс-сцен (/grant @username pro|sex N)")
    print("💾 Данные сохраняются в data/data.json (постоянное хранилище)")
    print("📌 Админ: /maintenance on/off для техобслуживания")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
