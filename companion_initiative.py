"""Starter variety and opt-out-aware, once-per-conversation re-engagement."""
import hashlib,random,re
from datetime import datetime
STARTERS={
 'warm':['Привет! Что сегодня тебя порадовало?','Как бы ты провёл идеальный спокойный вечер?','Хочется немного поболтать. Как ты?','Расскажешь о маленькой радости за сегодня?'],
 'shy':['Привет… можно немного с тобой поболтать?','Я пока не знаю, с чего начать. Как прошёл твой день?','Какую музыку ты сейчас слушаешь?','Давай начнём с чего-нибудь простого: чай или кофе?'],
 'aggressive':['Ну что, познакомимся без скучных анкет?','Какой спор ты готов отстаивать до последнего?','Есть тема поинтереснее обычного «как дела»?','Что тебя сегодня больше всего взбесило?'],
 'playful':['С чего начнём: вопрос или маленький спор?','Угадай, какой у меня сегодня настрой.','Расскажешь о себе то, чего не угадать с первого взгляда?','Давай обменяемся неожиданными фактами?'],
 'default':['Привет! Чем сейчас занят?','Что тебе в последнее время интересно?','Какое место тебе хочется посетить?','Какой фильм стоит посмотреть вместе?','Что у тебя сегодня случилось необычного?','Какую песню поставим первой?']}
def starters(user):
 if user.get('lang','ru')!='ru':return ['Hey! How has your day been?','What have you been into lately?','What song should we play first?','What would make today better?'] if user.get('lang')!='de' else ['Hey! Wie war dein Tag?','Was interessiert dich gerade?','Welches Lied hören wir zuerst?','Was würde deinen Tag schöner machen?']
 key=user.setdefault('starter_seed',random.getrandbits(64));rng=random.Random(str(key)+str(user.get('style'))+str(user.get('gender')))
 pool=STARTERS.get(user.get('style'),STARTERS['default']);items=rng.sample(pool,min(4,len(pool)))
 if len(items)<4:items+=rng.sample([x for x in STARTERS['default'] if x not in items],4-len(items))
 if user.get('gender')=='female':items=[x.replace('занят?','занята?').replace('провёл','провела').replace('готов отстаивать','готова отстаивать') for x in items]
 return items
def signature(user):
 messages=[m for m in user.get('history',[]) if m.get('role')=='user']
 return hashlib.sha256(str(messages).encode()).hexdigest() if messages else None

def due(user,local_time):
 sub=user.get('subscription') or {}
 try:elite=sub.get('active') and sub.get('level')=='elite' and datetime.fromisoformat(sub.get('expires_at',''))>datetime.now()
 except (TypeError,ValueError):elite=False
 if (elite and user.get('initiative_enabled') is False) or user.get('dead') or user.get('sleep_until') or user.get('app_pending') or user.get('hot_pending'):return False
 if not 9<=local_time.hour<22:return False
 sig=signature(user)
 if not sig or user.get('initiative_signature')==sig:return False
 try:idle=(datetime.now()-datetime.fromisoformat(user['last_activity'])).total_seconds()
 except (KeyError,ValueError,TypeError):return False
 return 6*3600<=idle<=7*86400

def instruction(user,level,style):
 return (f'Write one brief non-explicit follow-up message from an adult fictional companion. Character gender: {user.get("gender")}. '
 f'Personality: {style}. Relationship level: {level}/10. Language: {user.get("lang","ru")}. '
 'Continue the latest conversation naturally. At low levels be reserved; at high levels established affectionate names are allowed. '
 'For a shy character be hesitant; for an aggressive character allow a short sharp tease and mild swearing. '
 'Respect any stated sleep, work or absence plans; if they asked for space or said when they will return, output exactly SKIP. '
 'No guilt, demands, threats, crisis claims or purchases. Do not invent shared memories. Return only the message, at most 220 characters.')
