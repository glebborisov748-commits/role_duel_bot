"""Validated appearance and personality choices shared by setup, prompts and photos."""
import profile_options
import hashlib
import json
import re
from urllib.parse import urlencode

# key, RU, EN, DE, appearance phrase (EN)
OPTIONS={
 'hair_style': [('long','Длинные прямые','Long straight','Lang und glatt','long straight hair'),('waves','Волнистые','Wavy','Wellig','wavy shoulder-length hair'),('bob','Каре','Bob','Bob','a neat bob haircut'),('short','Короткие','Short','Kurz','short textured hair'),('curls','Кудри','Curly','Lockig','curly hair'),('ponytail','Хвост','Ponytail','Pferdeschwanz','hair tied in a ponytail'),('braid','Коса','Braid','Zopf','a loose braid'),('pixie','Пикси','Pixie','Pixie','a pixie haircut')],
 'hair_color':[('brown','Каштановые','Brown','Braun','brown'),('black','Чёрные','Black','Schwarz','black'),('blonde','Светлые','Blond','Blond','blond'),('red','Рыжие','Red','Rot','vivid copper-red ginger hair'),('silver','Серебристые','Silver','Silber','silver'),('pink','Розовые','Pink','Rosa','pastel pink'),('purple','Сиреневые','Lavender','Lavendel','lavender'),('blue','Синие','Blue','Blau','dark blue')],
 'skin':[('fair','Светлая','Fair','Hell','fair skin'),('light','Светло-бежевая','Light beige','Hellbeige','light beige skin'),('olive','Оливковая','Olive','Oliv','olive skin'),('tan','Смуглая','Tan','Gebräunt','tan skin'),('brown','Коричневая','Brown','Braun','brown skin'),('dark','Тёмная','Dark','Dunkel','dark skin')],
 'eyes':[('brown','Карие','Brown','Braun','brown eyes'),('blue','Голубые','Blue','Blau','blue eyes'),('green','Зелёные','Green','Grün','green eyes'),('grey','Серые','Grey','Grau','grey eyes'),('amber','Янтарные','Amber','Bernstein','amber eyes'),('violet','Сиреневые','Violet','Violett','violet eyes')],
 'accessory':[('none','Без аксессуаров','None','Keine','no accessories'),('glasses','Очки','Glasses','Brille','thin round glasses'),('earrings','Серьги','Earrings','Ohrringe','small silver earrings'),('necklace','Кулон','Pendant','Anhänger','a small pendant necklace'),('hairclip','Заколка','Hairclip','Haarspange','a discreet hairclip')],
 'interest':[('music','Музыка','Music','Musik','music'),('games','Игры','Gaming','Spiele','video games'),('cinema','Кино','Cinema','Kino','cinema'),('books','Книги','Books','Bücher','books'),('travel','Путешествия','Travel','Reisen','travel'),('art','Творчество','Art','Kunst','art'),('science','Наука','Science','Wissenschaft','science'),('sport','Спорт','Sport','Sport','sport')],
 'pace':[('balanced','Обычный темп','Balanced','Ausgewogen','balanced'),('relaxed','Неспешный','Relaxed','Entspannt','relaxed'),('lively','Быстрый','Lively','Lebhaft','lively')],
 'detail':[('balanced','Средние ответы','Balanced replies','Mittlere Antworten','balanced'),('short','Лаконично','Concise','Kurz','concise'),('detailed','Развёрнуто','Detailed','Ausführlich','detailed')],
}
OPTIONS['species']=[('human','Человек','Human','Mensch','human'),('cat','Кошачьи уши','Cat ears','Katzenohren','human with cat ears, human face'),('elf','Эльфийские уши','Elf ears','Elfenohren','human with pointed elf ears')]
VISUAL_KEYS=('hair_style','hair_color','skin','eyes','accessory','species')
MALE_HAIR=[('short','Короткая','Short','Kurz','short textured hair'),('undercut','Андеркат','Undercut','Undercut','an undercut hairstyle'),('fade','Фейд','Fade','Fade','a clean fade haircut'),('crop','Кроп','Crop','Crop','a short crop haircut'),('sidepart','С пробором','Side part','Seitenscheitel','a short side-part haircut'),('slicked','Зачёс назад','Slicked back','Zurückgekämmt','slicked-back short hair'),('curls_short','Короткие кудри','Short curls','Kurze Locken','short curly hair'),('medium','Средняя длина','Medium','Mittellang','medium-length masculine layered hair')]
OPTIONS['hair_style']+= [r for r in MALE_HAIR if r[0] not in {v[0] for v in OPTIONS['hair_style']}]
OPTIONS['accessory'] += [('sunglasses','Тёмные очки','Sunglasses','Sonnenbrille','dark sunglasses'),('stud','Серьга-гвоздик','Ear stud','Ohrstecker','a small ear stud'),('chain','Цепочка','Chain','Kette','a simple chain necklace'),('scarf','Шарф','Scarf','Schal','a soft scarf'),('headband','Ободок','Headband','Haarreif','a subtle headband'),('ribbon','Лента','Ribbon','Haarband','a hair ribbon')]
FEMALE_HAIR={'long','waves','bob','short','curls','ponytail','braid','pixie'}
MALE_ACCESSORIES={'none','glasses','sunglasses','stud','chain','scarf'}
DEFAULT={'species':'human','hair_style':'waves','hair_color':'brown','skin':'light','eyes':'brown','accessory':'none','interest':'music','pace':'balanced','detail':'balanced'}
FIELDS={'species':('Образ','Character type','Figurtyp'),'hair_style':('Причёска','Hair style','Frisur'),'hair_color':('Цвет волос','Hair color','Haarfarbe'),'skin':('Цвет кожи','Skin tone','Hautton'),'eyes':('Глаза','Eyes','Augen'),'accessory':('Аксессуар','Accessory','Accessoire'),'interest':('Увлечение','Interest','Interesse'),'pace':('Темп общения','Conversation pace','Gesprächstempo'),'detail':('Длина ответов','Reply length','Antwortlänge')}

def validate(raw,gender=None):
 if not isinstance(raw,dict):raise ValueError('Invalid character options')
 result={}
 for k,items in OPTIONS.items():
  value=raw.get(k,DEFAULT[k])
  if not isinstance(value,str) or value not in {i[0] for i in items}:raise ValueError('Invalid '+k)
  result[k]=value
 if gender=='male':
  if result['hair_style'] not in {r[0] for r in MALE_HAIR}:result['hair_style']='short'
  if result['accessory'] not in MALE_ACCESSORIES:result['accessory']='none'
 return result

def choices(lang,gender=None):
 ix={'ru':1,'en':2,'de':3}.get(lang,2)
 return [{'key':k,'label':FIELDS[k][ix-1],'items':[{'key':r[0],'label':r[ix]} for r in (MALE_HAIR if k=='hair_style' and gender=='male' else [v for v in rows if v[0] in FEMALE_HAIR] if k=='hair_style' else [v for v in rows if v[0] in MALE_ACCESSORIES] if k=='accessory' and gender=='male' else rows)]} for k,rows in OPTIONS.items() if k in VISUAL_KEYS and k!='species']

def selected(options,k):return next(r for r in OPTIONS[k] if r[0]==options[k])

def appearance(user,lang='en'):
 raw=user.get('appearance')
 if not raw and user.get('race','human')=='human':return None
 raw=raw or {}
 o=validate(raw,user.get('gender'))
 if lang=='ru':
  race=user.get('race','human');kind=profile_options.race_kind(race)
  labels={k:FIELDS[k][0] for k in VISUAL_KEYS if k!='species'}
  if kind in ('mechanical','alien'):labels={k:v for k,v in labels.items() if k not in ('hair_style','hair_color')}
  if kind=='mechanical':labels.update(skin='Покрытие корпуса',eyes='Цвет оптики')
  elif kind=='furry':labels['skin']='Цвет шерсти'
  elif kind=='scaled':labels['skin']='Цвет чешуи'
  descriptions={k:selected(o,k)[1].lower() for k in labels}
  if kind=='mechanical':descriptions['skin']={'fair':'слоновая кость','light':'жемчужное','olive':'оливковый металл','tan':'бронза','brown':'медь','dark':'графит'}[o['skin']]
  elif kind=='alien':descriptions['skin']={'fair':'светло-сиреневая','light':'бирюзовая','olive':'зелёная','tan':'янтарная','brown':'фиолетовая','dark':'тёмно-синяя'}[o['skin']]
  return profile_options.RACES.get(race,profile_options.RACES['human'])[0]+', '+', '.join(label+': '+descriptions[k] for k,label in labels.items())
 race=user.get('race') or {'cat':'catfolk','elf':'elf'}.get(o.get('species'),'human')
 kind=profile_options.race_kind(race);facts=[profile_options.RACE_FACTS.get(race,'human')]
 if kind=='mechanical':
  finishes={'fair':'ivory','light':'pearl white','olive':'olive metal','tan':'bronze','brown':'copper','dark':'graphite'}
  facts += [finishes[o['skin']]+' shell finish',selected(o,'eyes')[4].replace('eyes','illuminated optics'),selected(o,'accessory')[4]]
 elif kind=='alien':
  colors={'fair':'pale lavender','light':'turquoise','olive':'green','tan':'amber','brown':'violet','dark':'midnight blue'}
  facts += [colors[o['skin']]+' alien skin',selected(o,'eyes')[4],selected(o,'accessory')[4]]
 else:
  facts += [selected(o,'hair_color')[4]+' '+selected(o,'hair_style')[4]]
  surface=selected(o,'skin')[4]
  if kind=='furry':surface=surface.replace('skin','fur')
  elif kind=='scaled':surface=surface.replace('skin','scales')
  facts += [surface,selected(o,'eyes')[4],selected(o,'accessory')[4]]
 return ', '.join(facts)


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
ALIASES={'passionate':'playful','magnetic':'calm','melancholic':'calm','naive':'shy','unflappable':'calm','seduction':'playful'}
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
 gender=profile_options.photo_subject(user.get('race','human'),user.get('gender'))
 return 'Exactly ONE adult '+gender+', age 25 or older, solo portrait. '+(appearance(user) or 'human')+'. Keep the same gender and every listed visual attribute in every picture. No second person, no couple, no split view. '


def preview_url(user):
 o=validate(user.get('appearance') or {},user.get('gender'))
 return '/api/appearance-preview.svg?v=20261117d&'+urlencode({'world':user.get('world') or 'anime','race':user.get('race','human'),'gender':'male' if user.get('gender')=='male' else 'female',**{k:o[k] for k in VISUAL_KEYS}})

STYLE_EMOJI={'honest':'🤍','calm':'🍃','energetic':'⚡','melancholic':'🌧','humorous':'😄','naive':'🌼','playful':'😉','cynical':'🕶','compliant':'🕊','aggressive':'🌋','unflappable':'🧊','intellectual':'📚','rude':'💬'}

# Selection cards are descriptive only. No library portrait is used as an avatar/reference.
def creation_presets(lang,gender):
 rows=[('red',('Рыжие волосы · зелёные глаза','Red hair · green eyes','Rote Haare · grüne Augen'),'red','green','human'),
       ('dark',('Тёмные волосы · карие глаза','Dark hair · brown eyes','Dunkle Haare · braune Augen'),'black','brown','human'),
       ('blond',('Светлые волосы · голубые глаза','Blond hair · blue eyes','Blonde Haare · blaue Augen'),'blonde','blue','human'),
       ('silver',('Серебристые волосы · серые глаза','Silver hair · grey eyes','Silberne Haare · graue Augen'),'silver','grey','human'),
       ('elf',('Эльф · светлые волосы','Elf · blond hair','Elf · blonde Haare'),'blonde','green','elf'),
       ('cat',('Кошачьи уши · тёмные волосы','Cat ears · dark hair','Katzenohren · dunkle Haare'),'black','amber','catfolk')]
 ix={'ru':0,'en':1,'de':2}.get(lang,1)
 return [{'key':key,'label':label[ix],'race':race,'appearance':{'hair_style':'short' if gender=='male' else 'waves','hair_color':color,'eyes':eyes,'skin':'light','accessory':'none','species':'human'}} for key,label,color,eyes,race in rows]

# Additional paid personalities, separate from photo generation.
ELITE['temptation']=style('Искушение','Temptation','Versuchung','Ты взрослый романтичный собеседник 25+. Флиртуй уверенно: тонкие двусмысленные намёки, остроумные подколы, выразительные комплименты и романтическое напряжение. Без графических сексуальных описаний и давления. Уважай границы и просьбу остановиться.',adult=True)
PUBLIC.update({
 'compliant':('Мягкий, уступчивый, охотно поддерживает твою инициативу. Со своими границами.','Gentle and accommodating; follows your lead while respecting boundaries.','Sanft und entgegenkommend, mit eigenen Grenzen.'),
 'enigmatic':('Интригующий характер, тонкий юмор и постепенное раскрытие личности.','Intriguing, dry humor and a personality that unfolds gradually.','Geheimnisvoll, mit feinem Humor.'),
 'temptation':('18+ · уверенный флирт, двусмысленные намёки и романтическое напряжение. Только переписка, без фото.','18+ · confident flirting and romantic tension. Text only, no photos.','18+ · Flirt und romantische Spannung. Nur Text, keine Fotos.'),
})
STYLE_EMOJI.update(compliant='🕊️',enigmatic='🌒',temptation='💋')
