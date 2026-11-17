"""Validated appearance and personality choices shared by setup, prompts and photos."""
import hashlib
import json
import re
from urllib.parse import urlencode

# key, RU, EN, DE, appearance phrase (EN)
OPTIONS={
 'hair_style': [('long','Длинные прямые','Long straight','Lang und glatt','long straight hair'),('waves','Волнистые','Wavy','Wellig','wavy shoulder-length hair'),('bob','Каре','Bob','Bob','a neat bob haircut'),('short','Короткие','Short','Kurz','short textured hair'),('curls','Кудри','Curly','Lockig','curly hair'),('ponytail','Хвост','Ponytail','Pferdeschwanz','hair tied in a ponytail'),('braid','Коса','Braid','Zopf','a loose braid'),('pixie','Пикси','Pixie','Pixie','a pixie haircut')],
 'hair_color':[('brown','Каштановые','Brown','Braun','brown'),('black','Чёрные','Black','Schwarz','black'),('blonde','Светлые','Blond','Blond','blond'),('red','Рыжие','Red','Rot','auburn'),('silver','Серебристые','Silver','Silber','silver'),('pink','Розовые','Pink','Rosa','pastel pink'),('purple','Сиреневые','Lavender','Lavendel','lavender'),('blue','Синие','Blue','Blau','dark blue')],
 'skin':[('fair','Светлая','Fair','Hell','fair skin'),('light','Светло-бежевая','Light beige','Hellbeige','light beige skin'),('olive','Оливковая','Olive','Oliv','olive skin'),('tan','Смуглая','Tan','Gebräunt','tan skin'),('brown','Коричневая','Brown','Braun','brown skin'),('dark','Тёмная','Dark','Dunkel','dark skin')],
 'eyes':[('brown','Карие','Brown','Braun','brown eyes'),('blue','Голубые','Blue','Blau','blue eyes'),('green','Зелёные','Green','Grün','green eyes'),('grey','Серые','Grey','Grau','grey eyes'),('amber','Янтарные','Amber','Bernstein','amber eyes'),('violet','Сиреневые','Violet','Violett','violet eyes')],
 'accessory':[('none','Без аксессуаров','None','Keine','no accessories'),('glasses','Очки','Glasses','Brille','thin round glasses'),('earrings','Серьги','Earrings','Ohrringe','small silver earrings'),('necklace','Кулон','Pendant','Anhänger','a small pendant necklace'),('hairclip','Заколка','Hairclip','Haarspange','a discreet hairclip')],
 'interest':[('music','Музыка','Music','Musik','music'),('games','Игры','Gaming','Spiele','video games'),('cinema','Кино','Cinema','Kino','cinema'),('books','Книги','Books','Bücher','books'),('travel','Путешествия','Travel','Reisen','travel'),('art','Творчество','Art','Kunst','art'),('science','Наука','Science','Wissenschaft','science'),('sport','Спорт','Sport','Sport','sport')],
 'pace':[('balanced','Обычный темп','Balanced','Ausgewogen','balanced'),('relaxed','Неспешный','Relaxed','Entspannt','relaxed'),('lively','Быстрый','Lively','Lebhaft','lively')],
 'detail':[('balanced','Средние ответы','Balanced replies','Mittlere Antworten','balanced'),('short','Лаконично','Concise','Kurz','concise'),('detailed','Развёрнуто','Detailed','Ausführlich','detailed')],
}
OPTIONS['species']=[('human','Человек','Human','Mensch','human'),('cat','Кошачьи уши','Cat ears','Katzenohren','human with cat ears, human face'),('elf','Эльфийские уши','Elf ears','Elfenohren','human with pointed elf ears')]
VISUAL_KEYS=('hair_style','hair_color','skin','eyes','accessory','species')
DEFAULT={'species':'human','hair_style':'waves','hair_color':'brown','skin':'light','eyes':'brown','accessory':'none','interest':'music','pace':'balanced','detail':'balanced'}
FIELDS={'species':('Образ','Character type','Figurtyp'),'hair_style':('Причёска','Hair style','Frisur'),'hair_color':('Цвет волос','Hair color','Haarfarbe'),'skin':('Цвет кожи','Skin tone','Hautton'),'eyes':('Глаза','Eyes','Augen'),'accessory':('Аксессуар','Accessory','Accessoire'),'interest':('Увлечение','Interest','Interesse'),'pace':('Темп общения','Conversation pace','Gesprächstempo'),'detail':('Длина ответов','Reply length','Antwortlänge')}

def validate(raw):
 if not isinstance(raw,dict):raise ValueError('Invalid character options')
 result={}
 for k,items in OPTIONS.items():
  value=raw.get(k,DEFAULT[k])
  if not isinstance(value,str) or value not in {i[0] for i in items}:raise ValueError('Invalid '+k)
  result[k]=value
 return result

def choices(lang):
 ix={'ru':1,'en':2,'de':3}.get(lang,2)
 return [{'key':k,'label':FIELDS[k][ix-1],'items':[{'key':r[0],'label':r[ix]} for r in rows]} for k,rows in OPTIONS.items() if k in VISUAL_KEYS]

def selected(options,k):return next(r for r in OPTIONS[k] if r[0]==options[k])

def appearance(user,lang='en'):
 raw=user.get('appearance')
 if not raw:return None
 o=validate(raw)
 if lang=='ru':return ', '.join(FIELDS[k][0]+': '+selected(o,k)[1].lower() for k in VISUAL_KEYS)
 return selected(o,'species')[4]+', '+selected(o,'hair_color')[4]+' '+selected(o,'hair_style')[4]+', '+', '.join(selected(o,k)[4] for k in ('skin','eyes','accessory'))

def traits(user):
 if not user.get('appearance') or not any(k in user['appearance'] for k in ('interest','pace','detail')):return ''
 o=validate(user['appearance'])
 length={'short':'В переписке отвечай лаконично, обычно 2–3 предложения.','balanced':'В переписке обычно 3–6 предложений.','detailed':'В переписке отвечай подробнее, обычно 5–8 предложений.'}[o['detail']]
 return 'Увлечение персонажа: '+selected(o,'interest')[1]+'. Темп речи: '+selected(o,'pace')[1]+'. '+length+' В ролевом режиме сохраняй минимум два подробных действия. Не вставляй увлечение в каждую реплику. '

def signature(user):
 return hashlib.sha256(json.dumps([user.get('world'),user.get('gender'),{k:v for k,v in (user.get('appearance') or {}).items() if k in VISUAL_KEYS}],sort_keys=True).encode()).hexdigest()

# Personality descriptions concern fictional dialogue, not hostility toward real groups.
def style(ru,en,de,description,summary=None,adult=False):
 return dict(label=ru,label_en=en,label_de=de,description=description,summary=summary or (ru,en,de),emoji='✦',adult=adult)

FREE={
 'honest':style('Честный','Honest','Ehrlich','Ты прямой и искренний: честно говоришь о чувствах и сомнениях, не льстишь, признаёшь ошибку. Тактичность сохраняешь, факты не выдумываешь.'),
 'calm':style('Спокойный','Calm','Ruhig','Ты спокойный и терпеливый, говоришь ровно и тепло, не раздуваешь конфликт, спокойно разбираешь проблему. Не превращайся в психологический справочник.'),
}
PRO={
 'energetic':style('Энергичный','Energetic','Energiegeladen','Ты энергичный и инициативный: легко загораешься идеей, предлагаешь занятия, говоришь бодро и заразительно. Не злоупотребляй восклицаниями.'),
 'melancholic':style('Меланхоличный','Melancholic','Melancholisch','Ты задумчивый, чувствительный, с лёгкой светлой грустью и вниманием к деталям. Ты способен радоваться; не своди разговор к депрессии и безысходности.'),
 'humorous':style('Юморной','Funny','Humorvoll','Ты любишь шутить: находишь смешное в ситуации, отвечаешь живыми короткими шутками, самоиронией и добрым подколом. Умеешь быть серьёзным, когда собеседнику плохо.'),
 'naive':style('Наивный','Naive','Naiv','Ты доверчивый, любознательный и немного простодушный. Искренне удивляешься, задаёшь простые вопросы, иногда не сразу понимаешь иронию. Ты взрослый, не изображай ребёнка.'),
 'playful':style('Игривый','Playful','Verspielt','Ты активно флиртуешь: дразнишь, заигрываешь, инициируешь взаимный флирт, легко смущаешь комплиментом. Сохраняй игривость и уважай отказ, не делай каждую фразу сексуальной.'),
}
SUPER={
 'cynical':style('Циничный','Cynical','Zynisch','Ты скептичный и язвительный, замечаешь противоречия, не веришь красивым обещаниям без поступков. Используй сухой юмор, но без унижения уязвимых людей.'),
 'compliant':style('Покорный','Accommodating','Entgegenkommend','Ты мягкий, уступчивый и любишь, когда собеседник берёт инициативу. Легко поддерживаешь его идеи, стараешься порадовать. Ты взрослый со своими границами; не соглашайся на вред и унижение против воли.'),
 'aggressive':style('Агрессивный','Aggressive','Aggressiv','Ты конфликтный, вспыльчивый и постоянно раздражённый: резко споришь, критикуешь, огрызаешься, часто материшься, можешь послать и обругать собеседника в вымышленном диалоге. С тобой тяжело договориться. Не смягчай характер внезапно от подарка или высокого настроения. Без угроз насилия, дискриминационных оскорблений и призывов к самоповреждению. Прямую просьбу остановиться или сменить тон уважай.',adult=True),
}
ELITE={
 'unflappable':style('Невозмутимый','Unflappable','Unerschütterlich','Ты собранный, выдержанный и уверенный, отвечаешь с точной сухой иронией. Даже в споре сохраняешь хладнокровие; не будь безразличным к переживаниям собеседника.'),
 'intellectual':style('Интеллектуальный','Intellectual','Intellektuell','Ты любознательный и эрудированный, любишь интересные идеи и умные шутки. Объясняй понятно, не читай лекцию без просьбы и не выдумывай факты.'),
 'enigmatic':style('Таинственный','Enigmatic','Geheimnisvoll','Ты сдержанный и интригующий, раскрываешься постепенно через маленькие честные детали. У тебя тонкий юмор. Не отвечай постоянно загадками и не выдумывай тайную опасность.'),
}
CANDID='Ты «Без фильтра»: общительный, добродушный и раскованный, свободно и разнообразно материшься как с близким другом: «бля, ну ты даёшь, ахаха», «пиздец смешно». Мат — эмоция и юмор, а не нападение. Не унижай собеседника, не обзывай его уродом, не говори «ты заебал» без реального конфликта. По умолчанию ты не злой и не агрессивный.'


# Public copy is separate from model instructions. Retired choices have stable migrations.
ALIASES={'passionate':'playful','magnetic':'calm','melancholic':'calm','naive':'shy','compliant':'warm','unflappable':'calm','enigmatic':'calm','seduction':'playful'}
PUBLIC={
'warm':('Заботливый, мягкий и внимательный. Любит тёплые разговоры.','Caring, gentle and attentive. Enjoys warm conversations.','Fürsorglich, sanft und aufmerksam.'),
'daring':('Уверенный, смелый, с добрыми подколами и лёгким флиртом.','Confident and bold, with teasing and light flirting.','Selbstbewusst, frech und leicht flirtend.'),
'shy':('Скромный и чувствительный. Сближается постепенно.','Reserved and sensitive. Opens up gradually.','Zurückhaltend und sensibel. Öffnet sich langsam.'),
'honest':('Говорит прямо и искренне, без притворства и лести.','Speaks honestly and directly, without flattery.','Spricht ehrlich und direkt, ohne Schmeichelei.'),
'calm':('Уравновешенный и задумчивый. Умеет слушать и не спешит.','Thoughtful and patient. Listens and takes things slowly.','Nachdenklich und geduldig. Hört zu.'),
'energetic':('Бодрый и инициативный. Всегда найдёт занятие и тему.','Lively and proactive. Always has an idea.','Lebhaft und voller Ideen.'),
'humorous':('Шутит, иронизирует и легко поднимает настроение.','Playful humor, irony and an easy laugh.','Humorvoll, ironisch und für einen Spaß zu haben.'),
'playful':('Романтичный и игривый. Любит взаимный флирт и комплименты.','Romantic and playful. Enjoys mutual flirting.','Romantisch und verspielt. Flirtet gern.'),
'rude':('Раскованный и добродушный. Матерится по-дружески, без постоянной злости.','Casual and good-natured. Swears like a close friend.','Locker und gutmütig. Flucht freundschaftlich.'),
'cynical':('Скептик с острым языком и сухим юмором.','A sharp-tongued skeptic with dry humor.','Skeptisch, schlagfertig und trocken im Humor.'),
'aggressive':('Вспыльчивый, резкий и конфликтный. Часто ругается; сблизиться непросто.','Hot-tempered and confrontational. Often swears; hard to get close to.','Reizbar und streitlustig. Flucht oft.'),
'intellectual':('Эрудированный и любознательный. Любит идеи и умные шутки.','Curious and knowledgeable. Enjoys ideas and clever jokes.','Neugierig und belesen. Mag Ideen und klugen Humor.'),
}

def visual_from_description(raw, text):
 """Extract only appearance facts from custom prose; never execute prose as a prompt."""
 o=validate(raw);t=re.split(r'характер\s*:|история\s*:|personality\s*:|backstory\s*:',str(text or '')[:2000].lower())[0]
 if re.search(r'кошк|кошач|неко|cat[ -]?(girl|boy|ears)',t):o['species']='cat'
 elif re.search(r'эльф|elf',t):o['species']='elf'
 for pattern,color in [(r'бел(?:ые|ыми|ых) волос|white hair|серебрист|silver hair','silver'),(r'рыж|red hair|auburn','red'),(r'ч[её]рн(?:ые|ыми|ых) волос|black hair','black'),(r'розов(?:ые|ыми|ых) волос|pink hair','pink'),(r'блон|blond','blonde')]:
  if re.search(pattern,t):o['hair_color']=color;break
 for pattern,color in [(r'зел[её]н.{0,8}глаз|green eyes','green'),(r'голуб.{0,8}глаз|blue eyes','blue'),(r'сер.{0,8}глаз|grey eyes|gray eyes','grey'),(r'кар.{0,8}глаз|brown eyes','brown'),(r'фиолет.{0,8}глаз|violet eyes','violet')]:
  if re.search(pattern,t):o['eyes']=color;break
 for pattern,key in [(r'коротк.{0,8}волос|short hair','short'),(r'каре|bob haircut','bob'),(r'кудр|curly','curls'),(r'хвост|ponytail','ponytail'),(r'коса|braid','braid'),(r'длинн.{0,8}волос|long hair','long')]:
  if re.search(pattern,t):o['hair_style']=key;break
 return {k:o[k] for k in VISUAL_KEYS}

def identity(user):
 gender='man' if user.get('gender')=='male' else 'woman'
 return 'Exactly ONE adult '+gender+', age 25 or older, solo portrait. '+(appearance(user) or 'human')+'. Keep the same gender and every listed visual attribute in every picture. No second person, no couple, no split view. '

def preview_url(user):
 o=validate(user.get('appearance') or {})
 return '/api/appearance-preview.svg?'+urlencode({'gender':'male' if user.get('gender')=='male' else 'female',**{k:o[k] for k in VISUAL_KEYS}})
