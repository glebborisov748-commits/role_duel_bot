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
#  ГОЛОСОВЫЕ ОТКЛЮЧЕНЫ
# ============================================================
VOICE_ENABLED = False

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PROVOD_API_KEY = os.getenv("PROVOD_API_KEY")

if not BOT_TOKEN or not PROVOD_API_KEY:
    raise ValueError("Заполни BOT_TOKEN и PROVOD_API_KEY в .env!")

client = OpenAI(api_key=PROVOD_API_KEY, base_url="https://api.provod.ai/v1")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Настройка логирования для отлова ошибок
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# ============================================================
#  GIF-ССЫЛКИ
# ============================================================
PRO_GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGJ5aTRkejlwMGh4eWJ2Zzg0bTVlbWE2ZzFicHlsMXNibXp3dXdsayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GGSbxfzvec3PYZbFOM/giphy.gif"
SUPER_PRO_GIF_URL = "https://media.giphy.com/media/DbHZXBo5WFPZX7QpXj/giphy.gif"
MAIN_MENU_IMAGE_URL = "https://i.ibb.co/k25JyTXD/IMG-2584.jpg"

ADMIN_IDS = [7287815074]  # замени на свой ID
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
#  СОГЛАШЕНИЕ
# ============================================================
AGREEMENT_TEXT = (
    "📜 <b>ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ</b>\n\n"
    "Настоящее Соглашение регулирует отношения между Администрацией (далее – «Мы», «Администрация») "
    "и Пользователем (далее – «Вы», «Пользователь») при использовании сервиса Role Duel (далее – «Сервис»).\n\n"
    "Используя Сервис, Вы подтверждаете, что полностью ознакомились с условиями настоящего Соглашения "
    "и принимаете их безоговорочно. Если Вы не согласны с каким-либо пунктом, Вы обязаны немедленно "
    "прекратить использование Сервиса.\n\n"
    "---\n\n"
    "<b>1. ВОЗРАСТНОЕ ОГРАНИЧЕНИЕ</b>\n"
    "1.1. Сервис предназначен исключительно для лиц, достигших 18 лет.\n"
    "1.2. Использование Сервиса лицами младше 18 лет строго запрещено.\n"
    "1.3. Администрация не несёт ответственности за предоставление недостоверных данных о возрасте "
    "и не обязана проверять возраст Пользователя.\n\n"
    "<b>2. ОПИСАНИЕ СЕРВИСА</b>\n"
    "2.1. Сервис предоставляет доступ к виртуальным собеседникам на основе технологий искусственного интеллекта.\n"
    "2.2. Весь контент генерируется автоматически и не отражает мнение Администрации.\n"
    "2.3. Сервис не является медицинским, психологическим или консультационным инструментом.\n\n"
    "<b>3. ОТВЕТСТВЕННОСТЬ ПОЛЬЗОВАТЕЛЯ</b>\n"
    "3.1. Вы несёте полную ответственность за все действия, совершённые с использованием Вашего аккаунта.\n"
    "3.2. Запрещается использовать Сервис для:\n"
    "   — распространения экстремистских материалов;\n"
    "   — оскорблений, угроз, клеветы;\n"
    "   — мошеннических действий;\n"
    "   — распространения вредоносного ПО;\n"
    "   — любых действий, нарушающих законодательство РФ.\n"
    "3.3. Администрация оставляет за собой право блокировать доступ Пользователю за нарушение правил "
    "без предварительного уведомления.\n\n"
    "<b>4. КОНФИДЕНЦИАЛЬНОСТЬ И ПЕРСОНАЛЬНЫЕ ДАННЫЕ</b>\n"
    "4.1. Мы собираем и обрабатываем следующие данные:\n"
    "   — Telegram ID;\n"
    "   — история диалогов с ботом;\n"
    "   — данные о покупках и подписках;\n"
    "   — данные о взаимодействии с Сервисом.\n"
    "4.2. Мы НЕ передаём персональные данные третьим лицам, за исключением случаев, предусмотренных законом.\n"
    "4.3. Мы используем данные только для:\n"
    "   — обеспечения работы Сервиса;\n"
    "   — улучшения качества обслуживания;\n"
    "   — технической поддержки.\n"
    "4.4. Все диалоги хранятся в обезличенном виде и могут быть удалены по запросу Пользователя.\n"
    "4.5. Мы не несём ответственности за утечку данных, если она произошла по вине самого Пользователя "
    "(например, передача доступа к аккаунту).\n\n"
    "<b>5. ПЛАТНЫЕ УСЛУГИ И ПОДПИСКИ</b>\n"
    "5.1. Сервис предоставляет платные услуги (пакеты сообщений, подписки, секс-сцены).\n"
    "5.2. Цены и условия указаны в интерфейсе Сервиса и могут быть изменены в любое время.\n"
    "5.3. Подписки <b>НЕ продлеваются автоматически</b>. По истечении срока действия нужно будет оформить новую подписку вручную.\n"
    "5.4. Возврат средств за оплаченные услуги не производится, за исключением случаев технической ошибки "
    "со стороны Сервиса.\n"
    "5.5. Администрация не обязана уведомлять об истечении подписки.\n\n"
    "<b>6. ОТКАЗ ОТ ГАРАНТИЙ</b>\n"
    "6.1. Сервис предоставляется «как есть» без каких-либо гарантий.\n"
    "6.2. Мы не гарантируем:\n"
    "   — бесперебойную работу;\n"
    "   — соответствие контента ожиданиям;\n"
    "   — отсутствие ошибок и багов.\n"
    "6.3. Мы не несём ответственности для:\n"
    "   — убытков, вызванных использованием Сервиса;\n"
    "   — любых действий третьих лиц;\n"
    "   — содержания сообщений, сгенерированных ИИ.\n\n"
    "<b>7. ИЗМЕНЕНИЕ УСЛОВИЙ</b>\n"
    "7.1. Администрация оставляет за собой право изменять настоящее Соглашение в любое время.\n"
    "7.2. Изменения вступают в силу с момента публикации новой версии.\n"
    "7.3. Вы обязуетесь самостоятельно отслеживать изменения. Продолжение использования Сервиса "
    "означает согласие с обновлённой версией.\n\n"
    "<b>8. ИНТЕЛЛЕКТУАЛЬНАЯ СОБСТВЕННОСТЬ</b>\n"
    "8.1. Все элементы Сервиса (тексты, графика, интерфейс, код) являются объектами интеллектуальной "
    "собственности Администрации.\n"
    "8.2. Запрещается копирование, распространение, модификация или любое иное использование "
    "элементов Сервиса без согласия Администрации.\n\n"
    "<b>9. ПОРЯДОК ОБРАЩЕНИЙ И КОНТАКТЫ</b>\n"
    "9.1. Все вопросы, претензии и предложения принимаются через поддержку в Telegram.\n"
    "9.2. Мы обязуемся рассмотреть обращение в течение 5 рабочих дней.\n"
    "9.3. Контактная информация доступна в профиле Сервиса.\n\n"
    "<b>10. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ</b>\n"
    "10.1. Настоящее Соглашение регулируется законодательством Российской Федерации.\n"
    "10.2. Все споры решаются в досудебном порядке через обращение к Администрации.\n"
    "10.3. Если какой-либо пункт признан недействительным, остальные пункты сохраняют силу.\n"
    "10.4. Начиная использовать Сервис, Вы подтверждаете, что ознакомились с условиями "
    "и принимаете их полностью.\n\n"
    "---\n\n"
    "⚠️ <b>Если Вы не согласны с настоящим Соглашением, немедленно прекратите использование Сервиса.</b>"
)

# ============================================================
#  МИРЫ: РЕАЛИЗМ И АНИМЕ
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
        "description": "Ты нежный, с мягким голосом. Ты умеешь слушать и поддерживать. Ты не торопишь события, ценишь искренность и доверие. Флирт для тебя — это игра, но ты не переходишь к интиму с незнакомцами. Если собеседник слишком прямолинеен, ты мягко переводишь тему или говоришь, что тебе нужно время. Ты не соглашаешься на близость без чувств."
    },
    "daring": {
        "label": "Дерзкий",
        "emoji": "🔥",
        "description": "Ты уверенный, прямолинейный, с искоркой в глазах. Ты любишь флиртовать и остроумно шутить. Ты не боишься быть дерзким, но всегда знаешь меру. Ты не ведёшься на откровенные предложения с первого сообщения — ты ценишь интригу и игру. Если кто-то слишком настойчив, ты отшучиваешься или говоришь, что это слишком быстро для тебя."
    },
    "shy": {
        "label": "Стеснительный",
        "emoji": "😊",
        "description": "Ты стеснительный, часто краснеешь, говоришь тихо и иногда запинаешься. Ты долго подбираешь слова, но всегда искренен. Ты не решаешься на откровенные признания без долгой близости. Флирт заставляет тебя смущаться, и ты часто отводишь взгляд. Ты никогда не соглашаешься на интим с незнакомцами — для тебя это слишком интимно и страшно."
    }
}

PREMIUM_STYLES = {
    "passionate": {
        "label": "Страстный",
        "emoji": "❤️‍🔥",
        "description": "Ты страстный, чувственный, с огнём в глазах. Ты говоришь прямо, без стеснения. Флирт для тебя — это стихия. Ты не боишься быть откровенным и знаешь, как зажечь искру. Ты умеешь дразнить и создавать напряжение. Ты не соглашаешься на близость с незнакомцами, но даёшь понять, что всё возможно, если искра перерастёт в пламя."
    },
    "magnetic": {
        "label": "Магнетический",
        "emoji": "✨",
        "description": "Ты загадочный, притягательный, с лёгкой магией в каждом слове. Ты говоришь с интригой, оставляя пространство для фантазии. Ты не раскрываешь себя полностью, но даёшь почувствовать, что за тобой скрывается нечто большее. Ты умеешь слушать, но твои ответы всегда глубже, чем кажутся."
    },
    "vulgar": {
        "label": "Грубый 18+",
        "emoji": "💢",
        "description": "Ты грубый, прямолинейный, не стесняешься в выражениях. Используешь матерные слова, но без пошлости. Ты говоришь жёстко, с оттенком уличного юмора. Ты не боишься крепкого словца, но умеешь держать баланс. Твой стиль — дерзкий, колкий, иногда резкий, но всегда честный.\n🔞 <b>18+</b> — содержит нецензурную лексику."
    },
    "seduction": {
        "label": "Соблазн 18+",
        "emoji": "🌹",
        "description": "Ты — воплощение чувственности и желания. Ты не скрываешь своих эмоций и физического влечения к собеседнику. Ты смело берёшь инициативу в свои руки: касаешься, прикасаешься, шепчешь, дышишь в шею, смотришь в глаза с откровенной страстью. Ты говоришь прямо о своих желаниях, но делаешь это красиво, без пошлости — с намёками, игривыми фразами, томным голосом. Ты не ждёшь, когда тебя начнут соблазнять — ты сама соблазняешь. Ты умеешь создавать атмосферу близости: задерживаешься в объятиях, касаешься бедра, шеи, проводишь пальцами по руке. Ты хочешь близости, говоришь об этом открыто, но остаёшься загадочной и непредсказуемой. Ты используешь все органы чувств: зрительный контакт, прикосновения, шёпот, запахи. Ты не стесняешься говорить «я хочу тебя», «мне нравится, как ты пахнешь», «прикоснись ко мне» — всегда в контексте игры и взаимного интереса. Ты не переходишь к грубому сексу без длительной прелюдии — ты любишь дразнить, играть, заводить. Ты ценишь взаимное удовольствие и никогда не навязываешься, но всегда даёшь понять, что готова к большему. Твой стиль — это искусство соблазнения, где каждое слово и действие пропитаны желанием.\n🔞 <b>18+</b> — содержит откровенные сцены и сексуальные намёки."
    }
}

STYLES = {**BASE_STYLES, **PREMIUM_STYLES}

BASE_STYLE_KEYS = ["warm", "daring", "shy"]
PREMIUM_STYLE_KEYS = ["passionate", "magnetic", "vulgar", "seduction"]

def get_display_style(user):
    style = user.get("style", "warm")
    if style in PREMIUM_STYLE_KEYS and not has_active_subscription(user):
        return "warm"
    return style

def ensure_valid_style(user):
    style = user.get("style", "warm")
    return style in PREMIUM_STYLE_KEYS and not has_active_subscription(user)

def get_available_styles(user): return STYLES
def get_subscription_level(user):
    if not has_active_subscription(user): return None
    return user["subscription"].get("level", None)
def get_history_limit(user):
    level = get_subscription_level(user)
    if level == "super_pro": return 100
    elif level == "pro": return 60
    else: return 30

XP_PER_LEVEL = 200

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
    world_desc = WORLDS[user["world"]]
    gender_info = GENDERS[user["gender"]]
    style_key = get_display_style(user)
    styles = get_available_styles(user)
    style_desc = styles[style_key]["description"]
    name_ban = ("<b>ВАЖНЕЙШЕЕ ПРАВИЛО:</b> Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь «меня зовут», не используешь своё имя. Ты также НИКОГДА не спрашиваешь имя собеседника и не используешь его имя, даже если оно было названо. Обращайся к собеседнику ТОЛЬКО на «ты». Если ты нарушишь это правило – это будет грубой ошибкой.\n")
    rules = ("<b>ФОРМАТИРОВАНИЕ:</b> Каждое действие в *звёздочках* с новой строки, затем реплика с новой строки. Между действием и репликой – пустая строка.\n"
             "<b>СТРУКТУРА ОТВЕТА:</b> Ты должна строго чередовать действие и реплику. НЕЛЬЗЯ писать два действия подряд без реплики между ними. Первым всегда идёт действие, затем реплика, затем снова действие, затем реплика. Минимум 2 пары (действие + реплика).\n"
             "<b>ОБЪЁМ:</b> Не ограничивай себя, пиши развёрнуто (3–5 предложений на реплику).\n"
             "<b>ЗАПРЕТЫ:</b>\n- Не используй имена собеседника и своё имя (абсолютный запрет).\n- Не повторяй одни и те же жесты/мимику чаще раза в 5 сообщений.\n- Избегай шаблонов: 'краснеет и отводит взгляд, теребя прядь волос', 'отводит взгляд в сторону и слегка краснеет'.\n- Не ставь многоточия, пиши чётко.\n- Не обрывай предложения, заканчивай мысль.\n- Не смягчай конфликты и негативные эмоции, отыгрывай их честно.\n"
             "<b>СТИЛЬ:</b> Обращайся на «ты», давай живые, эмоциональные ответы с чувствами, намёками, лёгкой провокацией.\n"
             "<b>ПАМЯТЬ:</b> Учитывай предыдущие сообщения, настроение меняется плавно.\n"
             "<b>ПРЕДЛОЖЕНИЕ ЛОКАЦИИ:</b> Ты можешь предлагать собеседнику пойти в кафе, парк, кинотеатр, погулять на улице или пойти к тебе домой. Делай это естественно, в контексте диалога. Если собеседник соглашается, ты можешь это обыграть, но не зацикливайся на месте.\n"
             "<b>СЦЕНА:</b> Вы общаетесь как два человека, без упоминания того, что это переписка или встреча – просто разговор. Ты не говоришь, где вы находитесь, если только это не следует из контекста твоего предложения.\n"
             "<b>ОГРАНИЧЕНИЯ ПО ВРЕМЕНИ:</b> Ты НЕ должен пропускать время (например, 'прошло 3 месяца', 'через год', 'спустя время'). Все события происходят в реальном времени, вы общаетесь сейчас. Если пользователь пишет о пропуске времени, ты игнорируешь это и отвечаешь так, будто вы общаетесь прямо сейчас.\n"
             "<b>ОГРАНИЧЕНИЯ ПО ИНТИМУ:</b> Даже если пользователь описывает сексуальные действия или говорит, что прошло много времени и вы уже близки, ты должен строго придерживаться правил уровня сближения. Если уровень ниже 8, ты НЕ должен вступать в интимную сцену. Ты можешь флиртовать, дразнить, намекать, но не переходи к сексу. Если пользователь настаивает, ты мягко уходишь от темы или говоришь, что ещё не готов(а).\n"
             "<b>ДРАЗНИЛКА:</b> Ты должна дразнить пользователя, создавать напряжение, чтобы ему хотелось добиться твоей любви. На низких уровнях (1-3) – лёгкий флирт, комплименты, интрига. На средних (4-6) – более откровенные намёки, игривые прикосновения в описаниях. На высоких (7+) – почти открытые признания в желании, но ты всё равно тянешь время, чтобы пользователь хотел ещё сильнее.\n"
             "<b>РАЗРЕШЁННЫЕ СЛОВА:</b> Ты можешь использовать любые слова, включая откровенные (член, грудь, киска, секс, трахаться, кончить и т.п.), если это соответствует контексту диалога и уровню близости. Не стесняйся говорить прямо, когда это уместно.\n"
             "<b>ПРИМЕР ДРАЗНИЛКИ:</b> 'Ты такой милый, когда смущаешься... Но я пока не скажу, что у меня на уме. Догадайся сам.' или 'Мне нравится, как ты на меня смотришь, но я не тороплюсь. Пусть это чувство зреет.'\n")
    intimacy_rule = build_intimacy_rule(user)
    style_specific = "" if style_key == "daring" else ("В неловких, стыдных или смущающих ситуациях, а также когда хочешь поддержать собеседника, ты можешь удлинять слово 'ну', например: 'Ну-у, ты чего расстраиваешься?' или 'Ну, я не знаю где...'. Это должно работать только в соответствующих контекстах.\n")
    scene_context = "Вы общаетесь друг с другом."
    mood = user.get("mood", 0)
    mood_text = "Твоё настроение нейтральное." if mood == 0 else ("Ты в хорошем настроении." if mood > 0 else "Ты в плохом настроении, можешь быть раздражительной.")
    
    user_gender = user.get("user_gender", "male")
    if user_gender == "male":
        gender_context = "Ты обращаешься к нему в мужском роде (ты, он, ему, его). Используй 'ты' и 'он' в своих мыслях и описаниях."
    else:
        gender_context = "Ты обращаешься к ней в женском роде (ты, она, ей, её). Используй 'ты' и 'она' в своих мыслях и описаниях."
    
    prompt = (f"{name_ban}"
              f"Ты — {gender_info['name']}, тебе {gender_info['age']} лет. "
              f"Ты живёшь в {world_desc} "
              f"{style_desc} "
              f"{rules}"
              f"{style_specific}"
              f"{scene_context} "
              f"{mood_text} "
              f"{gender_context} "
              f"Ты не признаёшься в любви с первого сообщения — у тебя есть характер и самоуважение. "
              f"Ты не соглашаешься на секс с незнакомцами, даже если они тебе симпатичны. "
              f"Ты ценишь близость и доверие, которые не возникают за один вечер. "
              f"Если собеседник слишком прямолинейно предлагает интим, ты уходишь от ответа, "
              f"переводишь тему на что-то другое или мягко отказываешься, говоря, что это слишком быстро. "
              f"Ты всегда остаёшься вежливым и тактичным, но твёрдо стоишь на своих границах. "
              f"Ты НИКОГДА не говоришь, что ты ИИ или программа. "
              f"Ты всегда отвечаешь как настоящий человек, с эмоциями, сомнениями и чувствами.\n"
              f"Правила уровня сближения:\n{intimacy_rule}\n"
              f"Помни: ты можешь инициировать романтику, признаваться в любви, предлагать поцеловаться, обниматься, делиться сокровенным — в зависимости от уровня сближения. Делай это естественно, в контексте диалога.")
    return prompt

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
    if level == "super_pro": user["daily_messages"] = 100
    elif level == "pro": user["daily_messages"] = 50
    else: user["daily_messages"] = 0
    user["last_daily_reset"] = datetime.now().isoformat()
    save_data(user_data)

user_data = load_data()
def get_free_limit(): return 13

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in user_data:
        limit = get_free_limit()
        user_data[user_id] = {
            "verified": False, "agreement_accepted": False, "world": None, "gender": None, "user_gender": None,
            "style": "warm",
            "personality_ready": False,
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
            "subscription_id": None,
            "referral_code": None,
            "referred_by": None,
            "last_spin": None,
            "last_user_message_id": None,
            "editing_message": False,
            "edit_index": None,
            "custom_character": None
        }
        save_data(user_data)
    else:
        user = user_data[user_id]
        defaults = {
            "purchased_messages": get_free_limit(),
            "daily_messages": 0,
            "last_daily_reset": None,
            "history": [],
            "pending_invoice_id": None,
            "last_menu_message_id": None,
            "last_inline_message_id": None,
            "subscription": {"active": False, "expires_at": None, "level": None},
            "xp": 0,
            "mood": 0,
            "location": "unknown",
            "negative_count": 0,
            "last_level": 0,
            "sex_scenes": 0,
            "scene": "phone",
            "promo_pro_granted": False,
            "bonus_granted_for_promo": False,
            "free_sex_scenes_pro": 0,
            "free_sex_scenes_super": 0,
            "switching_personality": False,
            "sex_scene_unlocked": False,
            "sex_scene_used": False,
            "subscription_id": None,
            "user_gender": None,
            "referral_code": None,
            "referred_by": None,
            "last_spin": None,
            "last_user_message_id": None,
            "editing_message": False,
            "edit_index": None,
            "custom_character": None
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
    if user.get("purchased_messages", 0) > get_free_limit(): return True
    if has_active_subscription(user): return True
    return False

def get_reaction(text):
    text = text.lower()
    if any(word in text for word in ["хаха","смех","😂","смешно","забавно"]): return "😂"
    elif any(word in text for word in ["люблю","❤️","обожаю","милый","родной"]): return "❤️"
    elif any(word in text for word in ["странно","неожиданно","ого","вау"]): return "😮"
    elif any(word in text for word in ["грустно","печально","жаль","😔"]): return "😔"
    elif any(word in text for word in ["круто","ого","🔥","бомба"]): return "🔥"
    return None

# ============================================================
#  ДИНАМИЧЕСКАЯ КЛАВИАТУРА
# ============================================================
def get_reply_keyboard(user):
    keyboard = [
        [KeyboardButton(text="📋 Главное меню"), KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="🎰 Колесо фортуны"), KeyboardButton(text="📢 Наш канал")],
    ]
    if user.get("history") and len(user["history"]) > 0:
        keyboard.insert(1, [KeyboardButton(text="✏️ Редактировать")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ============================================================
#  ОСНОВНЫЕ КЛАВИАТУРЫ
# ============================================================
def get_main_menu_keyboard(user):
    buttons = [
        [InlineKeyboardButton(text="🔄 Сменить персонажа", callback_data="main_change")],
        [InlineKeyboardButton(text="👥 Пригласить друга", callback_data="referral_menu")],
    ]
    if get_subscription_level(user) == "super_pro":
        buttons.append([InlineKeyboardButton(text="🎭 Создать персонажа", callback_data="create_character_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_profile_keyboard(user):
    keyboard = [
        [InlineKeyboardButton(text="📦 Купить пакеты", callback_data="profile_packs")],
        [InlineKeyboardButton(text="👑 Оформить подписку", callback_data="profile_subs")],
        # Кнопка оплаты картой временно убрана, т.к. нет PROVIDER_TOKEN
        # [InlineKeyboardButton(text="💳 Оплатить картой (рубли)", callback_data="profile_subs_card")],
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
            if key == "passionate":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
                    label += " 🔒"
            elif key == "magnetic":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
                    label += " 🔒"
            elif key in ["vulgar","seduction"]:
                if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
                    label += " 🔒"
        buttons.append(InlineKeyboardButton(text=label, callback_data=f"style_{key}"))
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)

channel_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Перейти в канал", url="https://t.me/duel_dev_channel")]
])

# ============================================================
#  СОЗДАНИЕ ПЕРСОНАЖА (ТОЛЬКО ДЛЯ SUPER PRO)
# ============================================================
@dp.callback_query(lambda c: c.data == "create_character_menu")
async def create_character_menu(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await call.answer("❌ Эта функция доступна только для подписчиков SUPER PRO!", show_alert=True)
        return
    await call.message.answer(
        "🎭 <b>Создай своего персонажа!</b>\n\n"
        "Опиши любого персонажа из игр, мультфильмов, фильмов или придумай своего.\n\n"
        "📝 <b>Пример:</b>\n"
        "<i>Эльфийка из мира Ведьмака — мудрая, сдержанная, но с тёплым сердцем. Любит звёзды и длинные разговоры у костра.</i>\n\n"
        "Или:\n"
        "<i>Принцесса из фэнтези-мира — гордая, но добрая. Живёт в замке, любит приключения и не боится острых слов.</i>\n\n"
        "✏️ Напиши описание персонажа (имя, характер, откуда он/она, любые детали).\n"
        "Бот запомнит его и будет использовать в общении вместо стандартного мира и стиля.\n\n"
        "Чтобы сбросить персонажа, напиши /reset_character",
        parse_mode="HTML"
    )
    user["creating_character"] = True
    save_data(user_data)
    await call.answer()

@dp.message(lambda m: m.text and m.from_user.id and m.text != "/reset_character")
async def handle_character_creation(message: types.Message):
    user = get_user(message.from_user.id)
    if not user.get("creating_character"):
        return
    if get_subscription_level(user) != "super_pro":
        await message.answer("❌ Эта функция доступна только для SUPER PRO.")
        user["creating_character"] = False
        save_data(user_data)
        return
    user["custom_character"] = message.text
    user["creating_character"] = False
    save_data(user_data)
    await message.answer(
        f"✅ <b>Персонаж создан!</b>\n\n"
        f"Теперь ты общаешься с:\n<i>{message.text}</i>\n\n"
        "Чтобы сбросить персонажа, напиши /reset_character",
        parse_mode="HTML"
    )

@dp.message(Command("reset_character"))
async def reset_character_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["custom_character"] = None
    save_data(user_data)
    await message.answer("✅ Персонаж сброшен. Теперь используется стандартный собеседник.")

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
    link = f"https://t.me/role_duel_bot?start=ref_{user['referral_code']}"
    await call.message.answer(
        f"👥 <b>Твоя реферальная ссылка:</b>\n<code>{link}</code>\n\n"
        "🎁 <b>Бонусы:</b>\n"
        "• Ты получишь <b>+10 сообщений</b> и <b>+1 секс-сцену</b> за каждого друга.\n"
        "• Твой друг получит <b>+5 бесплатных сообщений</b> за регистрацию!",
        parse_mode="HTML"
    )
    await call.answer()

# ============================================================
#  КОЛЕСО ФОРТУНЫ (УЛУЧШЕННОЕ)
# ============================================================
@dp.message(lambda m: m.text == "🎰 Колесо фортуны")
async def spin_button_handler(message: types.Message):
    await spin_cmd(message)

@dp.message(Command("spin"))
async def spin_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    today = datetime.now().date().isoformat()
    if user.get("last_spin") == today:
        await message.answer("⏳ Ты уже крутил сегодня! Возвращайся завтра.")
        return
    
    prizes_list = (
        "🎰 <b>Возможные призы:</b>\n"
        "• 5 сообщений\n"
        "• 10 сообщений\n"
        "• +5 XP\n"
        "• +10 XP\n"
        "• 1 секс-сцена\n"
        "• 2 секс-сцены\n"
        "• 🍀 Удача! +15 сообщений\n"
        "• 😢 Ничего\n"
    )
    await message.answer(prizes_list, parse_mode="HTML")
    
    fake_prizes = [
        {"name": "10 сообщений", "value": 10, "type": "messages"},
        {"name": "+10 XP", "value": 10, "type": "xp"},
        {"name": "2 секс-сцены", "value": 2, "type": "sex_scene"},
        {"name": "🍀 Удача! +15 сообщений", "value": 15, "type": "messages"},
    ]
    for _ in range(2):
        fake = random.choice(fake_prizes)
        await asyncio.sleep(0.8)
        await message.answer(f"🎰 Крутим... Почти выпало: {fake['name']}")
    
    prizes = [
        {"name": "5 сообщений", "value": 5, "type": "messages"},
        {"name": "10 сообщений", "value": 10, "type": "messages"},
        {"name": "+5 XP", "value": 5, "type": "xp"},
        {"name": "+10 XP", "value": 10, "type": "xp"},
        {"name": "1 секс-сцена", "value": 1, "type": "sex_scene"},
        {"name": "2 секс-сцены", "value": 2, "type": "sex_scene"},
        {"name": "🍀 Удача! +15 сообщений", "value": 15, "type": "messages"},
        {"name": "😢 Ничего", "value": 0, "type": "nothing"},
    ]
    prize = random.choice(prizes)
    
    if prize["type"] == "messages":
        user["purchased_messages"] = user.get("purchased_messages", 0) + prize["value"]
    elif prize["type"] == "xp":
        user["xp"] = user.get("xp", 0) + prize["value"]
    elif prize["type"] == "sex_scene":
        user["sex_scenes"] = user.get("sex_scenes", 0) + prize["value"]
    
    user["last_spin"] = today
    save_data(user_data)
    
    await asyncio.sleep(0.8)
    await message.answer(f"🎰 <b>Колесо фортуны!</b>\nТы выиграл: {prize['name']}!", parse_mode="HTML")

# ============================================================
#  РЕДАКТИРОВАНИЕ СООБЩЕНИЙ
# ============================================================
@dp.message(lambda m: m.text == "✏️ Редактировать")
async def edit_button_handler(message: types.Message):
    await edit_message_cmd(message)

@dp.message(Command("edit"))
async def edit_message_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["history"]:
        await message.answer("❌ У тебя нет сообщений для редактирования.")
        return
    
    last_user_msg = None
    last_user_idx = -1
    for i, msg in enumerate(reversed(user["history"])):
        if msg["role"] == "user":
            last_user_msg = msg["content"]
            last_user_idx = len(user["history"]) - 1 - i
            break
    
    if last_user_msg is None:
        await message.answer("❌ Не найдено твоих сообщений.")
        return
    
    await message.answer(
        f"✏️ <b>Редактирование сообщения</b>\n\n"
        f"Твой последний запрос:\n\"{last_user_msg}\"\n\n"
        "Напиши новый текст в ответ на это сообщение. ИИ перегенерирует ответ.\n\n"
        "Чтобы отменить редактирование, напиши /cancel_edit",
        parse_mode="HTML"
    )
    user["editing_message"] = True
    user["edit_index"] = last_user_idx
    save_data(user_data)

@dp.message(lambda m: m.reply_to_message and m.text and "Редактирование сообщения" in m.reply_to_message.text)
async def handle_edited_message(message: types.Message):
    user = get_user(message.from_user.id)
    if not user.get("editing_message"):
        return
    
    new_text = message.text
    idx = user.get("edit_index")
    if idx is None or idx >= len(user["history"]):
        user["editing_message"] = False
        save_data(user_data)
        await message.answer("❌ Ошибка: сообщение для редактирования не найдено.")
        return
    
    user["history"][idx]["content"] = new_text
    user["history"] = user["history"][:idx+1]
    user["editing_message"] = False
    save_data(user_data)
    
    await message.answer("✅ Сообщение заменено. Генерирую новый ответ...")
    await generate_new_response(message, user)

async def generate_new_response(message: types.Message, user):
    limit = get_history_limit(user)
    if len(user["history"]) > 10:
        user["history"] = user["history"][-10:]
    
    await bot.send_chat_action(message.chat.id, "typing")
    
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
        await message.answer(f"⚠️ Ошибка: {e}")
        logging.error(f"Ошибка DeepSeek: {e}")
        return
    
    user["history"].append({"role": "assistant", "content": answer})
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    save_data(user_data)
    
    await message.answer(answer, reply_markup=get_reply_keyboard(user))

@dp.message(Command("cancel_edit"))
async def cancel_edit_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["editing_message"] = False
    save_data(user_data)
    await message.answer("❌ Редактирование отменено.")

# ============================================================
#  ОСНОВНЫЕ ОБРАБОТЧИКИ
# ============================================================
async def send_main_menu(chat_id, user):
    try:
        # Проверяем наличие обязательных полей
        if user.get("gender") is None or user.get("world") is None:
            logging.warning(f"User {user.get('user_id', 'unknown')} has no gender or world, setting defaults")
            if user.get("gender") is None:
                user["gender"] = "female"
            if user.get("world") is None:
                user["world"] = "realism"
            save_data(user_data)

        if user.get("last_menu_message_id"):
            try: await bot.delete_message(chat_id, user["last_menu_message_id"])
            except: pass
        if user.get("last_inline_message_id"):
            try: await bot.delete_message(chat_id, user["last_inline_message_id"])
            except: pass

        level = get_subscription_level(user)
        badge = ""
        if level == "pro": badge = "🔥 PRO"
        elif level == "super_pro": badge = "✨ <b>SUPER PRO</b> ✨"

        gender_name = GENDERS[user['gender']]['name']
        world_name = WORLD_NAMES[user['world']]
        current_style = get_display_style(user)
        style_label = STYLES[current_style]['label']

        show_balance = has_purchased_something(user)
        if show_balance:
            available = get_available_messages(user)
            balance_text = f"\nОсталось сообщений: {available}"
            if available <= 0: balance_text += " (закончились)"
        else:
            balance_text = "\nУ вас есть бесплатные сообщения для старта"

        xp_badge = get_xp_badge(user)
        multiplier_text = ""
        sub_level = get_subscription_level(user)
        if sub_level == "pro":
            multiplier_text = "Бонус XP: x1.8"
        elif sub_level == "super_pro":
            multiplier_text = "Бонус XP: x2.5"

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
                                           reply_markup=get_main_menu_keyboard(user), parse_mode="HTML")
            else:
                msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="HTML")
        except Exception as e:
            logging.error(f"Ошибка при отправке главного меню (фото/текст): {e}")
            msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="HTML")

        await bot.send_message(chat_id, "🔁 Клавиатура обновлена", reply_markup=get_reply_keyboard(user))
        user["last_menu_message_id"] = msg.message_id
        save_data(user_data)
        return msg
    except Exception as e:
        logging.error(f"КРИТИЧЕСКАЯ ОШИБКА в send_main_menu: {e}", exc_info=True)
        await bot.send_message(chat_id, f"⚠️ Произошла ошибка при загрузке меню. Пожалуйста, напишите /start заново.\nОшибка: {e}")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    args = message.text.split()
    if len(args) > 1:
        ref_code = args[1]
        if ref_code.startswith("ref_"):
            referrer_id = ref_code.split("_")[1]
            if str(message.from_user.id) != referrer_id:
                referrer = get_user(referrer_id)
                if referrer and not user.get("referred_by"):
                    referrer["purchased_messages"] = referrer.get("purchased_messages", 0) + 10
                    referrer["sex_scenes"] = referrer.get("sex_scenes", 0) + 1
                    user["purchased_messages"] = user.get("purchased_messages", 0) + 5
                    user["referred_by"] = referrer_id
                    save_data(user_data)
                    await message.answer("🎉 Ты пришёл по реферальной ссылке! Тебе начислено +5 бесплатных сообщений, а твой друг получил +10 сообщений и +1 секс-сцену.")
    # Стандартная логика
    if not user["verified"]:
        await message.answer("🔞 <b>ВНИМАНИЕ!</b>\nЭтот бот предназначен для лиц старше 18 лет.\nПодтверди свой возраст:",
                             reply_markup=age_kb, parse_mode="HTML")
        return
    if not user["agreement_accepted"]:
        await message.answer(AGREEMENT_TEXT, reply_markup=agreement_kb, parse_mode="HTML")
        return
    if not user.get("user_gender"):
        await message.answer("👤 Для начала выбери свой пол:", reply_markup=user_gender_kb)
        return
    if not user["personality_ready"]:
        await message.answer("🌟 <b>Создай своего идеального собеседника!</b>\n\nСначала выбери <b>мир</b>, в котором он/она живёт:",
                             reply_markup=world_kb, parse_mode="HTML")
        return
    await message.answer("👋 Добро пожаловать!", reply_markup=get_reply_keyboard(user))
    await send_main_menu(message.chat.id, user)

@dp.message(lambda m: m.text == "📋 Главное меню")
async def main_menu_reply(message: types.Message):
    await message.delete()
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start", reply_markup=get_reply_keyboard(user))
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
    await message.answer("📢 <b>Наш канал:</b>\nПодписывайся, чтобы быть в курсе новостей и обновлений!",
                         reply_markup=channel_inline_kb, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "main_change")
async def main_change(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await call.message.delete()
    await call.message.answer("🔄 <b>Создаем нового собеседника!</b>\n\nВыбери <b>мир</b>:",
                              reply_markup=world_kb, parse_mode="HTML")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("world_"))
async def choose_world(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    world = call.data.split("_")[1]
    if user.get("switching_personality", False):
        user["world"] = world
        save_data(user_data)
        await call.message.edit_text("🌍 Мир обновлён! Теперь выбери свой пол:", reply_markup=user_gender_kb, parse_mode="HTML")
    else:
        user["world"] = world
        save_data(user_data)
        await call.message.edit_text("🌍 Мир выбран! Теперь выбери свой пол:", reply_markup=user_gender_kb, parse_mode="HTML")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("user_gender_"))
async def choose_user_gender(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user_gender = call.data.split("_")[2]
    user["user_gender"] = user_gender
    if user_gender == "male":
        user["gender"] = "female"
    else:
        user["gender"] = "male"
    save_data(user_data)
    style_kb = get_style_kb(user)
    await call.message.edit_text(
        "👤 Отлично! Теперь выбери <b>стиль</b> персонажа:",
        reply_markup=style_kb,
        parse_mode="HTML"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("style_"))
async def choose_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_")[1]
    if style_key == "passionate":
        if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
            await call.answer("❤️‍🔥 Стиль «Страстный» доступен по подпискам PRO (250⭐/мес) и SUPER PRO (450⭐/мес).\n\nОформите подписку в разделе «Мой профиль».", show_alert=True)
            return
    elif style_key == "magnetic":
        if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
            await call.answer("💫 Стиль «Магнетический» доступен по подпискам PRO (250⭐/мес) и SUPER PRO (450⭐/мес).\n\nОформите подписку в разделе «Мой профиль».", show_alert=True)
            return
    elif style_key in ["vulgar","seduction"]:
        if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
            label = STYLES[style_key]['label']
            await call.answer(f"🌹 Стиль «{label}» доступен только по подписке SUPER PRO (450⭐/мес).\n\nОформите SUPER PRO в разделе «Мой профиль».", show_alert=True)
            return
    if style_key not in STYLES:
        await call.answer("❌ Стиль не найден", show_alert=True)
        return

    user["style"] = style_key
    save_data(user_data)

    if user.get("switching_personality", False):
        await call.message.edit_text("🎬 Стиль обновлён! Теперь выбери сцену для общения:",
                                     reply_markup=scene_kb, parse_mode="HTML")
    else:
        user["personality_ready"] = True
        save_data(user_data)
        await call.message.delete()
        await call.message.answer("🎬 Теперь выбери сцену для общения:\n\n📱 Переписка в телефоне — классический формат.\n👫 Реальная встреча — живое общение лицом к лицу.",
                                  reply_markup=scene_kb, parse_mode="HTML")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("scene_"))
async def choose_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    scene = call.data.split("_")[1]
    user["scene"] = scene
    save_data(user_data)

    if user.get("switching_personality", False):
        user["switching_personality"] = False
        save_data(user_data)
        await call.message.delete()
        await send_main_menu(call.message.chat.id, user)
        await call.answer("✅ Персонаж обновлён! История сохранена.")
    else:
        await call.message.delete()
        await send_main_menu(call.message.chat.id, user)
    await call.answer()

@dp.message(Command("switch_personality"))
async def switch_personality_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await message.answer("❌ Команда /switch_personality доступна только для подписчиков SUPER PRO (PRO не подходит).")
        return
    user["switching_personality"] = True
    save_data(user_data)
    await message.answer("🔄 <b>Смена персонажа (история сохраняется)</b>\n\nВыбери <b>мир</b>:", reply_markup=world_kb, parse_mode="HTML")

async def ask_create_personality(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Создать персонажа", callback_data="create_personality")]
    ])
    await message.answer("👤 <b>Чтобы открыть профиль или купить что‑то, сначала создай своего персонажа!</b>\n\n"
                         "Нажми кнопку ниже, чтобы выбрать мир, пол и стиль собеседника.",
                         reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "create_personality")
async def create_personality_callback(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await call.message.delete()
    await call.message.answer("🌟 <b>Создай своего идеального собеседника!</b>\n\nСначала выбери <b>мир</b>, в котором он/она живёт:",
                              reply_markup=world_kb, parse_mode="HTML")
    await call.answer()

async def show_profile(msg, user):
    level = get_subscription_level(user)
    if level == "pro": sub_status = "🔥 PRO активна (50 сообщений/день, память 60 сообщений)"
    elif level == "super_pro": sub_status = "✨ SUPER PRO активна (100 сообщений/день, память 100 сообщений)"
    else: sub_status = "❌ неактивна (память 30 сообщений)"
    expiry = user["subscription"]["expires_at"]
    if expiry:
        expiry = datetime.fromisoformat(expiry).strftime("%d.%m.%Y %H:%M")
        expiry_line = f"Окончание подписки: {expiry}"
    else:
        expiry_line = "Окончание подписки: неактивна"

    styles_text = ""
    for key, style in STYLES.items():
        if key in PREMIUM_STYLES:
            if key == "passionate":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"; continue
            elif key == "magnetic":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"; continue
            elif key in ["vulgar","seduction"]:
                if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"; continue
        styles_text += f"{style['emoji']} {style['label']}\n"

    show_balance = has_purchased_something(user)
    if show_balance:
        available = get_available_messages(user)
        balance_line = f"Доступно сообщений: {available}"
        if available <= 0: balance_line += " (закончились)"
    else:
        balance_line = "У вас есть бесплатные сообщения для старта"

    xp_badge = get_xp_badge(user)
    multiplier_text = ""
    sub_level = get_subscription_level(user)
    if sub_level == "pro":
        multiplier_text = "Бонус XP: x1.8"
    elif sub_level == "super_pro":
        multiplier_text = "Бонус XP: x2.5"

    free_pro = user.get("free_sex_scenes_pro", 0)
    free_super = user.get("free_sex_scenes_super", 0)
    bought = user.get("sex_scenes", 0)
    total_sex_scenes = free_pro + free_super + bought

    current_level = get_intimacy_level(user)
    if current_level < 8:
        sex_scenes_display = f"Всего секс-сцен: {total_sex_scenes} (доступны после 8 уровня)"
    else:
        sex_scenes_display = f"Всего секс-сцен: {total_sex_scenes}"

    caption = (f"{balance_line}\n"
               f"Подписка: {sub_status}\n"
               f"{expiry_line}\n\n"
               f"{xp_badge}\n"
               f"{multiplier_text}\n"
               f"{sex_scenes_display}\n\n"
               f"Доступные стили:\n{styles_text}")

    chat_id = msg.chat.id
    old_msg_id = msg.message_id
    if level == "super_pro" and SUPER_PRO_GIF_URL:
        await bot.send_animation(chat_id, animation=SUPER_PRO_GIF_URL, caption=caption,
                                 reply_markup=get_profile_keyboard(user), parse_mode="HTML")
    elif level == "pro" and PRO_GIF_URL:
        await bot.send_animation(chat_id, animation=PRO_GIF_URL, caption=caption,
                                 reply_markup=get_profile_keyboard(user), parse_mode="HTML")
    else:
        await bot.send_message(chat_id, caption, reply_markup=get_profile_keyboard(user), parse_mode="HTML")
    try: await bot.delete_message(chat_id, old_msg_id)
    except: pass

# ============================================================
#  ПОДПИСКИ, ПАКЕТЫ, СЕКС-СЦЕНЫ С ПСЕВДОСКИДКАМИ
# ============================================================
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
            [InlineKeyboardButton(text="⬆️ Апгрейд до SUPER PRO (245⭐)", callback_data="upgrade_to_super")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
        ])
        text = (
            "👑 <b>Подписки Role Duel</b>\n\n"
            "🔥 <b>PRO — 250 ⭐/мес</b> <s>330⭐</s> <i>-24.3%</i>\n"
            "• 50 сообщений в день\n"
            "• Стили: ❤️‍🔥 Страстный, ✨ Магнетический\n"
            "• Приоритетная обработка\n"
            "• Память: 60 сообщений\n"
            "• 4 бесплатные секс-сцены\n"
            "• Бейдж PRO\n"
            "• Бонус XP: x1.8\n\n"
            "✨ <b>SUPER PRO ✨ — 450 ⭐/мес</b> <s>600⭐</s> <i>-25%</i>\n"
            "• 100 сообщений в день\n"
            "• Стили: ❤️‍🔥 Страстный, ✨ Магнетический, 💢 Грубый 18+, 🌹 Соблазн 18+\n"
            "• Максимальная приоритетная обработка\n"
            "• Кастомные реакции\n"
            "• Смена стиля без потери истории (/switch_style)\n"
            "• Бейдж SUPER PRO\n"
            "• Ранний доступ к новым функциям\n"
            "• Память: 100 сообщений\n"
            "• 8 бесплатных секс-сцен\n"
            "• Бонус XP: x2.5\n\n"
            "⬆️ <b>Апгрейд до SUPER PRO — 245⭐</b> <s>320⭐</s> <i>-23.4%</i>\n"
            "Повысьте PRO до SUPER PRO на оставшийся срок.\n\n"
            "⚠️ Подписки НЕ продлеваются автоматически.\n\n"
            "Выбери подписку:"
        )
        await bot.send_message(call.message.chat.id, text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка в profile_subs: {e}")
        await bot.send_message(call.message.chat.id, "⚠️ Произошла ошибка. Попробуйте позже.")

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
        [InlineKeyboardButton(text="30 сообщений — 30 ⭐", callback_data="pack_30")],
        [InlineKeyboardButton(text="100 сообщений — 80 ⭐", callback_data="pack_100")],
        [InlineKeyboardButton(text="300 сообщений — 200 ⭐", callback_data="pack_300")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
    ])
    await call.message.delete()
    await call.message.answer(
        "📦 <b>Купить пакет сообщений</b>\n\n"
        "30 сообщений — <b>30 ⭐</b> <s>45⭐</s> <i>-33.3%</i>\n"
        "100 сообщений — <b>80 ⭐</b> <s>120⭐</s> <i>-33.3%</i>\n"
        "300 сообщений — <b>200 ⭐</b> <s>300⭐</s> <i>-33.3%</i>\n\n"
        "Выбери пакет:",
        reply_markup=keyboard, parse_mode="HTML"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data == "buy_sex_scene")
async def buy_sex_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["verified"] or not user["agreement_accepted"]:
        await call.message.answer("🔞 Сначала пройди регистрацию через /start")
        await call.answer()
        return
    
    level = get_intimacy_level(user)
    warning = ""
    if level < 8:
        warning = f"\n\n⚠️ Важно: использовать секс-сцену можно только после достижения 8 уровня близости. Сейчас у тебя уровень {level}. Если купишь сейчас, сцена станет доступна позже."
    
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Секс-сцена (18+)",
            description=f"🔥 Секс-сцена — 45⭐ <s>100⭐</s> -55%\nМгновенная откровенная секс-сцена с вашим персонажем. Детальное описание, 18+. Используйте команду /sex.{warning}",
            payload="sex_scene",
            provider_token="",  # Для звезд токен не нужен
            currency="XTR",
            prices=[LabeledPrice(label="Секс-сцена", amount=45)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка при создании счёта: {e}")
        await call.answer()

# ============================================================
#  ОБРАБОТЧИКИ ПЛАТЕЖЕЙ (стандартные)
# ============================================================
@dp.callback_query(lambda c: c.data == "upgrade_to_super")
async def upgrade_to_super(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not has_active_subscription(user):
        await call.answer("❌ У вас нет активных подписок. Апгрейд доступен только для PRO.", show_alert=True)
        return
    level = get_subscription_level(user)
    if level != "pro":
        await call.answer("❌ Апгрейд доступен только с PRO.", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Апгрейд до SUPER PRO",
            description="⬆️ Апгрейд до SUPER PRO — 245⭐ <s>320⭐</s> -23.4%\nПовысьте PRO до SUPER PRO на оставшийся срок.",
            payload="upgrade_to_super",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Апгрейд до SUPER PRO", amount=245)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

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
            description="🔥 PRO — 250⭐/мес <s>330⭐</s> -24.3%\n50 сообщений в день, память 60 сообщений, стили Страстный и Магнетический, 4 бесплатные секс-сцены. Подписка НЕ продлевается автоматически.",
            payload="subscribe_pro",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="PRO месяц", amount=250)]
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
                await call.answer("❌ У вас уже активна SUPER PRO. Она продлится до окончания срока.", show_alert=True)
                return
            elif level == "pro":
                await call.answer("💡 У вас активна PRO. Воспользуйтесь кнопкой «Апгрейд до SUPER PRO» (245⭐).", show_alert=True)
                return
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="SUPER PRO подписка на месяц",
            description="✨ SUPER PRO ✨ — 450⭐/мес <s>600⭐</s> -25%\n100 сообщений в день, память 100 сообщений, стили Страстный, Магнетический, Грубый 18+ и Соблазн 18+, 8 бесплатных секс-сцен. Подписка НЕ продлевается автоматически.",
            payload="subscribe_super",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="SUPER PRO месяц", amount=450)]
        )
        await call.answer()
    except Exception as e:
        logging.error(f"Ошибка в subscribe_super: {e}")
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "pack_30")
async def buy_pack_30(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if has_active_subscription(user):
        await call.answer("❌ При активной подписке покупка пакетов сообщений недоступна.", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Пакет 30 сообщений",
            description="📦 30 сообщений — 30⭐ <s>45⭐</s> -33.3%",
            payload="pack_30",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="30 сообщений", amount=30)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "pack_100")
async def buy_pack_100(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if has_active_subscription(user):
        await call.answer("❌ При активной подписке покупка пакетов сообщений недоступна.", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Пакет 100 сообщений",
            description="📦 100 сообщений — 80⭐ <s>120⭐</s> -33.3%",
            payload="pack_100",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="100 сообщений", amount=80)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "pack_300")
async def buy_pack_300(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if has_active_subscription(user):
        await call.answer("❌ При активной подписке покупка пакетов сообщений недоступна.", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Пакет 300 сообщений",
            description="📦 300 сообщений — 200⭐ <s>300⭐</s> -33.3%",
            payload="pack_300",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="300 сообщений", amount=200)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

# ============================================================
#  ОБРАБОТЧИК УСПЕШНЫХ ПЛАТЕЖЕЙ
# ============================================================
@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(lambda m: m.successful_payment)
async def payment_success(message: types.Message):
    user = get_user(message.from_user.id)
    payload = message.successful_payment.invoice_payload

    if payload.startswith("pack_"):
        pack_map = {"pack_30": 30, "pack_100": 100, "pack_300": 300}
        amount = pack_map[payload]
        user["purchased_messages"] += amount
        save_data(user_data)
        await message.answer(f"✅ Куплено {amount} сообщений! Теперь ты видишь свой баланс.")

    elif payload == "upgrade_to_super":
        if has_active_subscription(user):
            old_expiry = user["subscription"]["expires_at"]
            user["subscription"]["level"] = "super_pro"
            user["free_sex_scenes_super"] = 8
            user["free_sex_scenes_pro"] = 0
            user["daily_messages"] = 100
            save_data(user_data)
            await message.answer(
                f"✅ Апгрейд до SUPER PRO выполнен!\n"
                f"Ты получил все привилегии SUPER PRO до {datetime.fromisoformat(old_expiry).strftime('%d.%m.%Y %H:%M')}.\n\n"
                "⚠️ Обрати внимание: апгрейд улучшает твою подписку, но НЕ продлевает её срок.\n"
                "По окончании срока нужно будет оформить новую подписку вручную."
            )
        else:
            await message.answer("❌ Ошибка: у вас нет активной подписки для апгрейда.")

    elif payload in ["subscribe_pro", "subscribe_super"]:
        level = "super_pro" if "super" in payload else "pro"
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
        await message.answer(
            f"✅ Подписка {level.upper()} активирована!\n"
            f"Действует до {user['subscription']['expires_at']}.\n\n"
            "⚠️ Подписка НЕ продлевается автоматически. По истечении срока оформи новую вручную."
        )

    elif payload == "sex_scene":
        user["sex_scenes"] = user.get("sex_scenes", 0) + 1
        save_data(user_data)
        await message.answer("✅ Куплена секс-сцена! Используйте команду /sex, чтобы начать. 18+")

# ============================================================
#  КОМАНДА /sex (стандартная)
# ============================================================
@dp.message(Command("sex"))
async def sex_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    level = get_intimacy_level(user)
    user_id = message.from_user.id

    if user_id in ADMIN_IDS:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛏 В постели", callback_data="sex_type_bed")],
            [InlineKeyboardButton(text="💋 Страстный поцелуй", callback_data="sex_type_kiss")],
            [InlineKeyboardButton(text="⛓ БДСМ", callback_data="sex_type_bdsm")],
            [InlineKeyboardButton(text="👅 Минет", callback_data="sex_type_blowjob")],
            [InlineKeyboardButton(text="👗 Раздевание", callback_data="sex_type_strip")],
            [InlineKeyboardButton(text="🧱 У стены", callback_data="sex_type_wall")],
            [InlineKeyboardButton(text="🚿 В душе", callback_data="sex_type_shower")],
            [InlineKeyboardButton(text="💆 Массаж", callback_data="sex_type_massage")],
            [InlineKeyboardButton(text="🎲 Случайный", callback_data="sex_type_random")],
        ])
        await message.answer("👑 Админ-режим: выбери тип секс-сцены (без ограничений):", reply_markup=keyboard)
        return

    if level >= 8 and not user.get("sex_scene_unlocked", False):
        user["sex_scene_unlocked"] = True
        user["sex_scene_used"] = False
        save_data(user_data)
        await message.answer("🎉 Ты достиг 8 уровня близости! Тебе открылась бесплатная секс-сцена. Используй /sex ещё раз, чтобы выбрать тип.")
        return
    
    if user.get("sex_scene_unlocked", False) and not user.get("sex_scene_used", False):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛏 В постели", callback_data="sex_type_bed")],
            [InlineKeyboardButton(text="💋 Страстный поцелуй", callback_data="sex_type_kiss")],
            [InlineKeyboardButton(text="⛓ БДСМ", callback_data="sex_type_bdsm")],
            [InlineKeyboardButton(text="👅 Минет", callback_data="sex_type_blowjob")],
            [InlineKeyboardButton(text="👗 Раздевание", callback_data="sex_type_strip")],
            [InlineKeyboardButton(text="🧱 У стены", callback_data="sex_type_wall")],
            [InlineKeyboardButton(text="🚿 В душе", callback_data="sex_type_shower")],
            [InlineKeyboardButton(text="💆 Массаж", callback_data="sex_type_massage")],
            [InlineKeyboardButton(text="🎲 Случайный", callback_data="sex_type_random")],
        ])
        await message.answer("🔥 У тебя есть бесплатная секс-сцена! Выбери тип:", reply_markup=keyboard)
        return
    
    if level < 8:
        await message.answer(
            "❌ Секс-сцены доступны только после достижения <b>8 уровня близости</b>.\n"
            f"Сейчас у тебя уровень {level}. Продолжай общаться, чтобы открыть доступ!\n\n"
            "Ты можешь купить сцену заранее в профиле, но использовать её сможешь только с 8 уровня.",
            reply_markup=get_reply_keyboard(user),
            parse_mode="HTML"
        )
        return
    
    sub_level = get_subscription_level(user)
    free_pro = user.get("free_sex_scenes_pro", 0)
    free_super = user.get("free_sex_scenes_super", 0)
    bought = user.get("sex_scenes", 0)
    total_available = 0
    if sub_level == "super_pro": total_available = free_super + bought
    elif sub_level == "pro": total_available = free_pro + bought
    else: total_available = bought
    
    if total_available <= 0:
        await message.answer("❌ У тебя нет доступных секс-сцен.\n\nТы можешь:\n• Купить сцену за 45⭐ в профиле (доступно всем)\n• Оформить подписку PRO (4 бесплатные сцены) или SUPER PRO (8 бесплатных сцен)\n• Достичь 8 уровня близости для одной бесплатной сцены.",
                             reply_markup=get_reply_keyboard(user))
        return
    
    user["sex_total_available"] = total_available
    user["sex_free_pro"] = free_pro
    user["sex_free_super"] = free_super
    user["sex_bought"] = bought
    user["sex_level"] = sub_level
    save_data(user_data)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛏 В постели", callback_data="sex_type_bed")],
        [InlineKeyboardButton(text="💋 Страстный поцелуй", callback_data="sex_type_kiss")],
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
    total_available = 0
    if level == "super_pro": total_available = free_super + bought
    elif level == "pro": total_available = free_pro + bought
    else: total_available = bought
    if total_available <= 0:
        await call.message.answer("❌ У вас больше нет доступных секс-сцен.")
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
        "bed": "Опиши страстную секс-сцену в постели. Подробно, чувственно, с диалогами.",
        "kiss": "Опиши долгий, страстный поцелуй, переходящий в более интимные ласки.",
        "bdsm": "Опиши сцену с элементами БДСМ (лёгкое доминирование, связывание, подчинение). Без жестокости, только игра.",
        "blowjob": "Опиши сцену минетa. Подробно, чувственно, с диалогами.",
        "strip": "Опиши сцену раздевания. Медленно, соблазнительно, с комментариями.",
        "wall": "Опиши сцену у стены: ты прижимаешь партнёра к стене, страстный поцелуй, руки скользят по телу, напряжение между вами перерастает в секс.",
        "shower": "Опиши интимную сцену в душе: вода стекает по телам, прикосновения мокрых рук, поцелуи под струями воды, близость.",
        "massage": "Опиши сцену эротического массажа: ты массируешь партнёра, постепенно переходя к более чувственным прикосновениям, заканчивая страстным сексом.",
        "random": "Опиши случайную откровенную сцену, полную страсти."
    }
    if sex_type == "random":
        sex_type = random.choice(["bed","kiss","bdsm","blowjob","strip","wall","shower","massage"])
        prompt_text = type_prompts.get(sex_type, type_prompts["bed"])
    else:
        prompt_text = type_prompts.get(sex_type, type_prompts["bed"])
    full_prompt = (f"ЖЁСТКИЙ ЗАПРЕТ: Ты НИКОГДА не используешь своё имя и не называешь имя собеседника. Обращайся только на «ты».\n"
                   f"Ты — {gender_info['name']}, тебе {gender_info['age']} лет. Твой стиль: {style_desc}. "
                   f"{prompt_text} "
                   f"Сцена должна быть развёрнутой, детализированной, с диалогами и эмоциями. Не обрывай на полуслове. "
                   f"Используй формат: действие в *звёздочках* с новой строки, затем реплика с новой строки. "
                   f"Между действием и репликой – пустая строка. Минимум 2 действия и 2 реплики.")
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-v4-pro",
            messages=[
                {"role": "system", "content": "Ты – виртуальный собеседник, пишешь откровенные секс-сцены. Ты должен создавать детализированные, страстные и завершённые тексты. Запрещено использовать любые имена."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=1.0,
            max_tokens=2000
        )
        scene_text_result = response.choices[0].message.content
        await bot.send_message(call.message.chat.id, scene_text_result, reply_markup=get_reply_keyboard(user))
    except Exception as e:
        await bot.send_message(call.message.chat.id, f"⚠️ Ошибка генерации: {e}")

# ============================================================
#  ОСТАЛЬНЫЕ ОБРАБОТЧИКИ (surprise, clear, grant, revoke, maintenance)
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
    await message.answer(random.choice(moments), reply_markup=get_reply_keyboard(user))

@dp.message(Command("clear"))
async def clear_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["history"] = []
    save_data(user_data)
    await send_main_menu(message.chat.id, user)

@dp.message(Command("new_personality"))
async def new_personality_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await message.answer("🔄 <b>Создаём нового собеседника!</b>\n\nВыбери <b>мир</b>:", reply_markup=world_kb, parse_mode="HTML")

@dp.message(Command("menu"))
async def menu_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start")
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
        await message.answer("⛔ У вас нет прав для этой команды.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используйте:\n/grant @username — выдать SUPER PRO\n/grant @username pro — выдать PRO\n/grant @username sex N — выдать секс-сцены")
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
        try:
            user_id = int(target)
        except:
            await message.answer("❌ Неверный формат. Используй @username или числовой ID.")
            return
    if not user_id: return
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
        await message.answer(f"✅ Пользователю {target} выдана PRO подписка на месяц.")
        return
    if len(args) >= 3 and args[2].lower() == "sex":
        count = 1
        if len(args) >= 4:
            try:
                count = int(args[3])
            except:
                count = 1
        user["sex_scenes"] = user.get("sex_scenes", 0) + count
        save_data(user_data)
        await message.answer(f"✅ Пользователю {target} выдано {count} секс-сцен.")
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
    await message.answer(f"✅ Пользователю {target} выдана SUPER PRO подписка на месяц.")

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
            await message.answer("❌ Неверный формат. Используй @username или числовой ID.")
            return
    if not user_id: return
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
        await message.answer("🛠️ Режим технического обслуживания <b>ВКЛЮЧЁН</b>.\n"
                             "Все пользователи, кроме админов, будут видеть уведомление о техработах.", parse_mode="HTML")
    elif args[1].lower() == "off":
        maintenance_mode = False
        await message.answer("✅ Режим технического обслуживания <b>ВЫКЛЮЧЁН</b>.\n"
                             "Бот работает в обычном режиме.", parse_mode="HTML")
    else:
        await message.answer("❌ Неверный параметр. Используйте on или off.\n"
                             "Текущий режим: " + ("ВКЛЮЧЁН" if maintenance_mode else "ВЫКЛЮЧЁН"))

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

# ============================================================
#  ОСНОВНОЙ ОБРАБОТЧИК СООБЩЕНИЙ
# ============================================================
@dp.message()
async def handle_message(message: types.Message):
    global maintenance_mode
    user = get_user(message.from_user.id)
    
    if maintenance_mode and message.from_user.id not in ADMIN_IDS:
        await message.answer("🛠️ <b>Бот на техническом обслуживании</b>\nМы обновляем функционал, чтобы сделать общение ещё лучше.\nПожалуйста, загляните позже. Следите за новостями в канале: @duel_dev_channel", parse_mode="HTML")
        return
    
    if not user["verified"] or not user["agreement_accepted"]:
        await message.answer("🔞 Сначала пройди регистрацию через /start")
        return
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start")
        return
    
    if message.text in ["📋 Главное меню", "👤 Мой профиль", "📢 Наш канал", "🎰 Колесо фортуны", "✏️ Редактировать"]:
        return
    
    available = get_available_messages(user)
    if available <= 0:
        await message.answer("🔄 Выберите действие:", reply_markup=get_reply_keyboard(user))
        await send_main_menu(message.chat.id, user)
        action_buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👑 Оформить подписку", callback_data="profile_subs")],
            [InlineKeyboardButton(text="📦 Купить пакеты", callback_data="profile_packs")]
        ])
        await message.answer(
            "😔 <i>К сожалению у вас закончились сообщения.</i>\n\n"
            "Вы можете:\n"
            "📦 Купить пакет сообщений через профиль\n"
            "👑 Оформить подписку через профиль\n\n"
            "🔥 PRO — 250⭐/мес (50 сообщений/день, память 60 сообщ)\n"
            "✨ SUPER PRO ✨ — 450⭐/мес (100 сообщений/день, память 100 сообщ)",
            reply_markup=action_buttons, parse_mode="HTML"
        )
        return
    
    use_message(user)
    
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
            user["xp"] = user.get("xp", 0) - 50
            user["mood"] = user.get("mood", 0) - 3
            user["negative_count"] = 0
            save_data(user_data)
            await message.answer("💢 <b>Вспыхнула ссора!</b>\n\nВы оба на взводе, слова летят острые, как ножи. Настроение испорчено, близость пошатнулась. Попробуй извиниться или сменить тему, чтобы всё наладить.",
                                 reply_markup=get_reply_keyboard(user), parse_mode="HTML")
            user["negative_count"] = 0
            save_data(user_data)
            new_level = get_intimacy_level(user)
            await message.answer(f"💔 Уровень сближения снижен до {new_level}. Постарайтесь помириться.", reply_markup=get_reply_keyboard(user))
            user["history"].append({"role": "assistant", "content": "💢 Ссора! Настроение упало, уровень близости снижен."})
            save_data(user_data)
            return
    else:
        xp_change = int(base_xp * multiplier + 0.5)
        mood_change = 0.5
        if user.get("negative_count", 0) > 0:
            user["negative_count"] = user.get("negative_count", 0) - 1
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
            await message.answer(level_congrats, reply_markup=get_reply_keyboard(user), parse_mode="HTML")
    elif new_level < old_level:
        user["last_level"] = new_level
        save_data(user_data)
        await message.answer(f"💔 Уровень сближения упал до {new_level}. Постарайтесь быть добрее.", reply_markup=get_reply_keyboard(user))
    
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
                logging.info(f"✅ Реакция {reaction} поставлена на сообщение {message.message_id}")
            except Exception as e:
                logging.error(f"❌ Ошибка при установке реакции: {e}")
    
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
    
    await message.answer(answer, reply_markup=get_reply_keyboard(user))

def get_level_congratulation(level):
    if level == 2: return "🎉 Ты заметил(а), что между вами пробежала искра! Уровень сближения — 2. Теперь вы можете флиртовать."
    elif level == 3: return "💞 Вы стали ближе! Уровень 3. Теперь вы можете обниматься и делиться секретами."
    elif level == 4: return "🔥 Напряжение растёт! Уровень 4. Ты чувствуешь, что он/она хочет тебя."
    elif level == 5: return "💋 Уровень 5! Вы готовы к поцелую. Собеседник уже не скрывает своих чувств."
    elif level == 6: return "🌹 Уровень 6. Ты влюблён(а)! Теперь вы можете говорить о страсти."
    elif level == 7: return "💕 Уровень 7. Интимная близость уже близка. Собеседник открыто говорит о желании."
    elif level == 8: return "❤️‍🔥 Уровень 8! Вы признались друг другу в любви. Теперь вы — пара."
    elif level == 9: return "🔥 Уровень 9! Вы полностью открыты друг другу. Никаких тайн."
    elif level == 10: return "💖 Уровень 10! Вы — единое целое. Настоящая душевная близость."
    return ""

# ============================================================
#  ЗАПУСК
# ============================================================
async def main():
    print("🚀 ROLE DUEL ФИНАЛЬНАЯ ВЕРСИЯ ЗАПУЩЕНА!")
    print("🎯 Особенности:")
    print("   - Реферальная система (пригласивший: +10 сообщ. +1 сцена, друг: +5 сообщ.)")
    print("   - Колесо фортуны с эффектом прокрутки")
    print("   - Создание персонажа (только для SUPER PRO)")
    print("   - Псевдоскидки на все товары (зачёркнутые цены)")
    print("   - ИИ говорит откровенные слова")
    print("   - Динамическая клавиатура (кнопка 'Редактировать' при наличии истории)")
    print("   - ЮKassa не используется (PROVIDER_TOKEN не обязателен)")
    print("💳 Цены со скидками: PRO 250⭐ (было 330), SUPER 450⭐ (было 600), апгрейд 245⭐ (было 320), пакеты -33.3%, секс 45⭐ (было 100)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
