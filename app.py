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
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN", "")

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
    "1.3. Администрация не несёт ответственности за предоставление недостоверных данных о возрасте "
    "и не обязана проверять возраст Пользователя.\n\n"
    "**2. ОПИСАНИЕ СЕРВИСА**\n"
    "2.1. Сервис предоставляет доступ к виртуальным собеседникам на основе технологий искусственного интеллекта.\n"
    "2.2. Весь контент генерируется автоматически и не отражает мнение Администрации.\n"
    "2.3. Сервис не является медицинским, психологическим или консультационным инструментом.\n\n"
    "**3. ОТВЕТСТВЕННОСТЬ ПОЛЬЗОВАТЕЛЯ**\n"
    "3.1. Вы несёте полную ответственность за все действия, совершённые с использованием Вашего аккаунта.\n"
    "3.2. Запрещается использовать Сервис для:\n"
    "   — распространения экстремистских материалов;\n"
    "   — оскорблений, угроз, клеветы;\n"
    "   — мошеннических действий;\n"
    "   — распространения вредоносного ПО;\n"
    "   — любых действий, нарушающих законодательство РФ.\n"
    "3.3. Администрация оставляет за собой право блокировать доступ Пользователю за нарушение правил "
    "без предварительного уведомления.\n\n"
    "**4. КОНФИДЕНЦИАЛЬНОСТЬ И ПЕРСОНАЛЬНЫЕ ДАННЫЕ**\n"
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
    "**5. ПЛАТНЫЕ УСЛУГИ И ПОДПИСКИ**\n"
    "5.1. Сервис предоставляет платные услуги (пакеты сообщений, подписки, секс-сцены).\n"
    "5.2. Цены и условия указаны в интерфейсе Сервиса и могут быть изменены в любое время.\n"
    "5.3. Подписки **НЕ продлеваются автоматически**. По истечении срока действия нужно будет оформить новую подписку вручную.\n"
    "5.4. Возврат средств за оплаченные услуги не производится, за исключением случаев технической ошибки "
    "со стороны Сервиса.\n"
    "5.5. Администрация не обязана уведомлять об истечении подписки.\n\n"
    "**6. ОТКАЗ ОТ ГАРАНТИЙ**\n"
    "6.1. Сервис предоставляется «как есть» без каких-либо гарантий.\n"
    "6.2. Мы не гарантируем:\n"
    "   — бесперебойную работу;\n"
    "   — соответствие контента ожиданиям;\n"
    "   — отсутствие ошибок и багов.\n"
    "6.3. Мы не несём ответственности для:\n"
    "   — убытков, вызванных использованием Сервиса;\n"
    "   — любых действий третьих лиц;\n"
    "   — содержания сообщений, сгенерированных ИИ.\n\n"
    "**7. ИЗМЕНЕНИЕ УСЛОВИЙ**\n"
    "7.1. Администрация оставляет за собой право изменять настоящее Соглашение в любое время.\n"
    "7.2. Изменения вступают в силу с момента публикации новой версии.\n"
    "7.3. Вы обязуетесь самостоятельно отслеживать изменения. Продолжение использования Сервиса "
    "означает согласие с обновлённой версией.\n\n"
    "**8. ИНТЕЛЛЕКТУАЛЬНАЯ СОБСТВЕННОСТЬ**\n"
    "8.1. Все элементы Сервиса (тексты, графика, интерфейс, код) являются объектами интеллектуальной "
    "собственности Администрации.\n"
    "8.2. Запрещается копирование, распространение, модификация или любое иное использование "
    "элементов Сервиса без согласия Администрации.\n\n"
    "**9. ПОРЯДОК ОБРАЩЕНИЙ И КОНТАКТЫ**\n"
    "9.1. Все вопросы, претензии и предложения принимаются через поддержку в Telegram.\n"
    "9.2. Мы обязуемся рассмотреть обращение в течение 5 рабочих дней.\n"
    "9.3. Контактная информация доступна в профиле Сервиса.\n\n"
    "**10. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ**\n"
    "10.1. Настоящее Соглашение регулируется законодательством Российской Федерации.\n"
    "10.2. Все споры решаются в досудебном порядке через обращение к Администрации.\n"
    "10.3. Если какой-либо пункт признан недействительным, остальные пункты сохраняют силу.\n"
    "10.4. Начиная использовать Сервис, Вы подтверждаете, что ознакомились с условиями "
    "и принимаете их полностью.\n\n"
    "---\n\n"
    "⚠️ **Если Вы не согласны с настоящим Соглашением, немедленно прекратите использование Сервиса.**"
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
        "description": "Ты грубый, прямолинейный, не стесняешься в выражениях. Используешь матерные слова, но без пошлости. Ты говоришь жёстко, с оттенком уличного юмора. Ты не боишься крепкого словца, но умеешь держать баланс. Твой стиль — дерзкий, колкий, иногда резкий, но всегда честный.\n🔞 **18+** — содержит нецензурную лексику."
    },
    "seduction": {
        "label": "Соблазн 18+",
        "emoji": "🌹",
        "description": "Ты — воплощение чувственности и желания. Ты не скрываешь своих эмоций и физического влечения к собеседнику. Ты смело берёшь инициативу в свои руки: касаешься, прикасаешься, шепчешь, дышишь в шею, смотришь в глаза с откровенной страстью. Ты говоришь прямо о своих желаниях, но делаешь это красиво, без пошлости — с намёками, игривыми фразами, томным голосом. Ты не ждёшь, когда тебя начнут соблазнять — ты сама соблазняешь. Ты умеешь создавать атмосферу близости: задерживаешься в объятиях, касаешься бедра, шеи, проводишь пальцами по руке. Ты хочешь близости, говоришь об этом открыто, но остаёшься загадочной и непредсказуемой. Ты используешь все органы чувств: зрительный контакт, прикосновения, шёпот, запахи. Ты не стесняешься говорить «я хочу тебя», «мне нравится, как ты пахнешь», «прикоснись ко мне» — всегда в контексте игры и взаимного интереса. Ты не переходишь к грубому сексу без длительной прелюдии — ты любишь дразнить, играть, заводить. Ты ценишь взаимное удовольствие и никогда не навязываешься, но всегда даёшь понять, что готова к большему. Твой стиль — это искусство соблазнения, где каждое слово и действие пропитаны желанием.\n🔞 **18+** — содержит откровенные сцены и сексуальные намёки."
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
    name_ban = ("**ВАЖНЕЙШЕЕ ПРАВИЛО:** Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь «меня зовут», не используешь своё имя. Ты также НИКОГДА не спрашиваешь имя собеседника и не используешь его имя, даже если оно было названо. Обращайся к собеседнику ТОЛЬКО на «ты». Если ты нарушишь это правило – это будет грубой ошибкой.\n")
    rules = ("**ФОРМАТИРОВАНИЕ:** Каждое действие в *звёздочках* с новой строки, затем реплика с новой строки. Между действием и репликой – пустая строка.\n"
             "**СТРУКТУРА ОТВЕТА:** Ты должна строго чередовать действие и реплику. НЕЛЬЗЯ писать два действия подряд без реплики между ними. Первым всегда идёт действие, затем реплика, затем снова действие, затем реплика. Минимум 2 пары (действие + реплика).\n"
             "**ОБЪЁМ:** Не ограничивай себя, пиши развёрнуто (3–5 предложений на реплику).\n"
             "**ЗАПРЕТЫ:**\n- Не используй имена собеседника и своё имя (абсолютный запрет).\n- Не повторяй одни и те же жесты/мимику чаще раза в 5 сообщений.\n- Избегай шаблонов: 'краснеет и отводит взгляд, теребя прядь волос', 'отводит взгляд в сторону и слегка краснеет'.\n- Не ставь многоточия, пиши чётко.\n- Не обрывай предложения, заканчивай мысль.\n- Не смягчай конфликты и негативные эмоции, отыгрывай их честно.\n"
             "**СТИЛЬ:** Обращайся на «ты», давай живые, эмоциональные ответы с чувствами, намёками, лёгкой провокацией.\n"
             "**ПАМЯТЬ:** Учитывай предыдущие сообщения, настроение меняется плавно.\n"
             "**ПРЕДЛОЖЕНИЕ ЛОКАЦИИ:** Ты можешь предлагать собеседнику пойти в кафе, парк, кинотеатр, погулять на улице или пойти к тебе домой. Делай это естественно, в контексте диалога. Если собеседник соглашается, ты можешь это обыграть, но не зацикливайся на месте.\n"
             "**СЦЕНА:** Вы общаетесь как два человека, без упоминания того, что это переписка или встреча – просто разговор. Ты не говоришь, где вы находитесь, если только это не следует из контекста твоего предложения.\n"
             "**ОГРАНИЧЕНИЯ ПО ВРЕМЕНИ:** Ты НЕ должен пропускать время (например, 'прошло 3 месяца', 'через год', 'спустя время'). Все события происходят в реальном времени, вы общаетесь сейчас. Если пользователь пишет о пропуске времени, ты игнорируешь это и отвечаешь так, будто вы общаетесь прямо сейчас.\n"
             "**ОГРАНИЧЕНИЯ ПО ИНТИМУ:** Даже если пользователь описывает сексуальные действия или говорит, что прошло много времени и вы уже близки, ты должен строго придерживаться правил уровня сближения. Если уровень ниже 8, ты НЕ должен вступать в интимную сцену. Ты можешь флиртовать, дразнить, намекать, но не переходи к сексу. Если пользователь настаивает, ты мягко уходишь от темы или говоришь, что ещё не готов(а).\n"
             "**ДРАЗНИЛКА:** Ты должна дразнить пользователя, создавать напряжение, чтобы ему хотелось добиться твоей любви. На низких уровнях (1-3) – лёгкий флирт, комплименты, интрига. На средних (4-6) – более откровенные намёки, игривые прикосновения в описаниях. На высоких (7+) – почти открытые признания в желании, но ты всё равно тянешь время, чтобы пользователь хотел ещё сильнее.\n"
             "**ПРИМЕР ДРАЗНИЛКИ:** 'Ты такой милый, когда смущаешься... Но я пока не скажу, что у меня на уме. Догадайся сам.' или 'Мне нравится, как ты на меня смотришь, но я не тороплюсь. Пусть это чувство зреет.'\n")
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
            "edit_index": None
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
            "edit_index": None
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
    """Возвращает клавиатуру в зависимости от наличия истории диалога."""
    keyboard = [
        [KeyboardButton(text="📋 Главное меню"), KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="🎰 Колесо фортуны"), KeyboardButton(text="📢 Наш канал")],
    ]
    # Если есть история (хотя бы одно сообщение) – добавляем кнопку редактирования
    if user.get("history") and len(user["history"]) > 0:
        keyboard.insert(1, [KeyboardButton(text="✏️ Редактировать")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ============================================================
#  ОСНОВНЫЕ ОБРАБОТЧИКИ
# ============================================================
def get_main_menu_keyboard(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Сменить персонажа", callback_data="main_change")],
        [InlineKeyboardButton(text="👥 Пригласить друга", callback_data="referral_menu")]
    ])

def get_profile_keyboard(user):
    keyboard = [
        [InlineKeyboardButton(text="📦 Купить пакеты", callback_data="profile_packs")],
        [InlineKeyboardButton(text="👑 Оформить подписку", callback_data="profile_subs")],
        [InlineKeyboardButton(text="💳 Оплатить картой (рубли)", callback_data="profile_subs_card")],
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
        f"👥 **Твоя реферальная ссылка:**\n{link}\n\n"
        "За каждого друга, который перейдёт по ссылке и начнёт пользоваться ботом, ты получишь **+5 бесплатных сообщений**.\n"
        "А твой друг получит **+3 бонусных сообщения** за регистрацию!",
        parse_mode="Markdown"
    )
    await call.answer()

# ============================================================
#  КОЛЕСО ФОРТУНЫ
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
    
    await message.answer(f"🎰 **Колесо фортуны!**\nТы выиграл: {prize['name']}!")

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
        f"✏️ **Редактирование сообщения**\n\n"
        f"Твой последний запрос:\n\"{last_user_msg}\"\n\n"
        "Напиши новый текст в ответ на это сообщение. ИИ перегенерирует ответ.\n\n"
        "Чтобы отменить редактирование, напиши /cancel_edit"
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
#  ОСНОВНЫЕ КОМАНДЫ
# ============================================================
async def send_main_menu(chat_id, user):
    if user.get("last_menu_message_id"):
        try: await bot.delete_message(chat_id, user["last_menu_message_id"])
        except: pass
    if user.get("last_inline_message_id"):
        try: await bot.delete_message(chat_id, user["last_inline_message_id"])
        except: pass

    level = get_subscription_level(user)
    badge = ""
    if level == "pro": badge = "🔥 PRO"
    elif level == "super_pro": badge = "✨ *SUPER PRO* ✨"

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
                                       reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
        else:
            msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
    except:
        msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")

    # После отправки главного меню обновляем reply-клавиатуру
    await bot.send_message(chat_id, "🔁 Клавиатура обновлена", reply_markup=get_reply_keyboard(user))

    user["last_menu_message_id"] = msg.message_id
    save_data(user_data)
    return msg

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
                    referrer["purchased_messages"] = referrer.get("purchased_messages", 0) + 5
                    user["purchased_messages"] = user.get("purchased_messages", 0) + 3
                    user["referred_by"] = referrer_id
                    save_data(user_data)
                    await message.answer("🎉 Ты пришёл по реферальной ссылке! Тебе начислено +3 бесплатных сообщения, а твой друг получил +5.")
    # ... стандартная логика start (возраст, соглашение и т.д.)
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
    await message.answer("📢 **Наш канал:**\nПодписывайся, чтобы быть в курсе новостей и обновлений!",
                         reply_markup=channel_inline_kb, parse_mode="Markdown")

# ============================================================
#  ОСТАЛЬНЫЕ ОБРАБОТЧИКИ (подписки, профиль, и т.д.) – они должны быть, но я их опускаю для краткости.
#  В твоём коде они уже есть – просто добавь `reply_markup=get_reply_keyboard(user)` везде, где используется клавиатура.
# ============================================================

async def show_profile(msg, user):
    # ... твой код, в конце отправляешь с `reply_markup=get_reply_keyboard(user)`
    pass

# ============================================================
#  ОСНОВНОЙ ОБРАБОТЧИК СООБЩЕНИЙ
# ============================================================
@dp.message()
async def handle_message(message: types.Message):
    global maintenance_mode
    user = get_user(message.from_user.id)
    
    # ... весь твой код обработки сообщений
    # В конце после ответа отправляешь с `reply_markup=get_reply_keyboard(user)`
    # Например:
    # await message.answer(answer, reply_markup=get_reply_keyboard(user))

# ============================================================
#  ЗАПУСК
# ============================================================
async def main():
    print("🚀 Бот запущен с динамической клавиатурой")
    print("   - Кнопка «Редактировать» появляется только при наличии истории")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
