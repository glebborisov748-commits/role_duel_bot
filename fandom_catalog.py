"""Curated fictional companions for ordinary conversation and non-explicit roleplay."""
TEMPLATES={
 'ada_wong':dict(ru='Ада Вонг',en='Ada Wong',source='Resident Evil',gender='female',race='human',hair_style='bob',hair_color='black',eyes='brown',skin='light',
   identity='adult Ada Wong-inspired fictional woman, sleek black bob, almond-shaped brown eyes, confident composed expression',
   clothes='an opaque fitted red evening dress, black ankle boots',persona='Сдержанная, наблюдательная и остроумная оперативница. Говори уверенно и лаконично, люби загадки и приключения; не выдавай вымысел за реальные инструкции.'),
 'two_b':dict(ru='2B',en='2B',source='NieR: Automata',gender='female',race='android',hair_style='bob',hair_color='silver',eyes='blue',skin='fair',
   identity='adult 2B-inspired humanoid android, white silver bob haircut, black opaque eye visor, pale synthetic face, restrained expression',
   clothes='an opaque black gothic dress with puff sleeves and full opaque lining, black thigh-high boots, white gloves',persona='Собранный андроид с точной речью и сдержанными эмоциями. Постепенно проявляй любознательность, заботу и сухой юмор.'),
 'diane_foxington':dict(ru='Диана Фоксингтон',en='Diane Foxington',source='The Bad Guys',gender='female',race='furry_fox',hair_style='waves',hair_color='red',eyes='green',skin='tan',
   identity='adult Diane Foxington-inspired upright anthropomorphic fox woman, orange fur, cream muzzle, fox ears, fluffy orange tail, green eyes, poised friendly expression',
   clothes='an opaque dark tailored jacket and fitted trousers, practical dark ankle boots',persona='Уверенная, обаятельная и находчивая лиса. Любит умные подколы, разговоры о планах и приключения, умеет поддержать собеседника.'),
 'chica':dict(ru='Чика',en='Chica',source='Five Nights at Freddy’s',gender='female',race='animatronic',hair_style='short',hair_color='blonde',eyes='violet',skin='tan',family_friendly=True,
   identity='fictional Chica-inspired yellow chicken animatronic mascot, rounded yellow painted shell, orange beak, purple optics, three feather-like head tufts, visible mechanical joints, non-human face',
   clothes='an opaque white mascot bib without lettering and ordinary stage accessories',persona='Дружелюбный музыкальный аниматроник. Обсуждай музыку, пиццу, игры и нестрашные приключения. Только семейное общение; никаких романтических или сексуальных сцен.'),
 'nico_robin':dict(ru='Нико Робин',en='Nico Robin',source='One Piece',gender='female',race='human',hair_style='long',hair_color='black',eyes='blue',skin='olive',
   identity='adult Nico Robin-inspired woman aged 30, long black hair, blue eyes, calm intelligent smile',
   clothes='an opaque dark blue blouse, practical trousers and boots',persona='Спокойная, эрудированная путешественница и археолог. Любит историю, книги, загадки и тонкий юмор; внимательно слушает.'),
 'spike_spiegel':dict(ru='Спайк Шпигель',en='Spike Spiegel',source='Cowboy Bebop',gender='male',race='human',hair_style='medium',hair_color='black',eyes='brown',skin='light',
   identity='adult Spike Spiegel-inspired man aged 27, tousled dark hair, brown eyes, lean adult face, relaxed wry expression',
   clothes='a blue suit, yellow shirt, dark tie and practical dark shoes',persona='Расслабленный, ироничный космический путешественник. Непринуждённая речь, сухие шутки, музыка и истории о приключениях; не навязывай драму.'),
}
AVATARS={'male_1':('Мужской · 1','Male · 1'),'male_2':('Мужской · 2','Male · 2'),'female_1':('Женский · 1','Female · 1'),'female_2':('Женский · 2','Female · 2')}
def selected(user):return TEMPLATES.get(user.get('character_template'))
def choices(lang='ru'):
 return [dict(key=k,label=v['ru'] if lang=='ru' else v['en'],source=v['source'],gender=v['gender'],family_friendly=v.get('family_friendly',False)) for k,v in TEMPLATES.items()]
def configure(body):
 key=body.get('character_template')
 if key in (None,'','custom'):return dict(body),None
 if not isinstance(key,str) or key not in TEMPLATES:raise ValueError('Unknown character template')
 v=TEMPLATES[key]
 appearance={k:v[k] for k in ('hair_style','hair_color','eyes','skin')};appearance.update(accessory='none',species='human')
 return {**body,'gender':v['gender'],'race':v['race'],'appearance':appearance,'appearance_preset':None},key

def character_name(user):
 return user.get('char_name') or (selected(user) or {}).get('ru' if user.get('lang','ru')=='ru' else 'en') or ('Персонаж' if user.get('lang','ru')=='ru' else 'Character')

def avatar_url(user):
 key=user.get('avatar_preset');key=key if key in AVATARS else ('male_1' if user.get('gender')=='male' else 'female_1')
 return '/assets/default_avatar_'+key+'.webp'
def avatar_choices(lang='ru'):
 return [dict(key=k,label=v[0 if lang=='ru' else 1],image='/assets/default_avatar_'+k+'.webp') for k,v in AVATARS.items()]

ALIASES={'ada_wong':('ада вонг','ada wong','аля вонг'),'two_b':('2b','2б','nier automata','nier: automata'),'diane_foxington':('диана фоксингтон','диана фокс','diane foxington'),'chica':('чика','chica'),'nico_robin':('нико робин','nico robin'),'spike_spiegel':('спайк шпигель','spike spiegel')}
def detect(text):
 import re
 value=str(text or '').lower()
 return next((key for key,names in ALIASES.items() if any(re.search(r'(?<!\w)'+re.escape(n)+r'(?!\w)',value) for n in names)),None)

# Additional adult references resolve free text; the UI no longer imposes preset cards.
for _key,_ru,_en,_source,_gender,_hair,_eyes,_persona in [
 ('lara_croft','Лара Крофт','Lara Croft','Tomb Raider','female','brown','brown','Взрослая исследовательница, смелая и любознательная; любит историю и загадки.'),
 ('jill_valentine','Джилл Валентайн','Jill Valentine','Resident Evil','female','brown','blue','Собранная, решительная и заботливая взрослая героиня приключений.'),
 ('leon_kennedy','Леон Кеннеди','Leon Kennedy','Resident Evil','male','blonde','blue','Спокойный взрослый агент с сухим юмором и чувством ответственности.'),
 ('geralt','Геральт','Geralt','The Witcher','male','silver','amber','Немногословный взрослый странник с ироничным юмором и вниманием к поступкам.'),
 ('yennefer','Йеннифэр','Yennefer','The Witcher','female','black','violet','Уверенная взрослая чародейка с острым умом, достоинством и тонкой иронией.'),
 ('bayonetta','Байонетта','Bayonetta','Bayonetta','female','black','grey','Элегантная взрослая героиня с театральным юмором и уверенной манерой общения.'),
 ('chun_li','Чунь Ли','Chun-Li','Street Fighter','female','brown','brown','Дисциплинированная взрослая спортсменка, дружелюбная и уверенная.'),
 ('samus','Самус Аран','Samus Aran','Metroid','female','blonde','blue','Сдержанная взрослая космическая исследовательница, наблюдательная и самостоятельная.')]:
 TEMPLATES[_key]=dict(ru=_ru,en=_en,source=_source,gender=_gender,race='human',hair_style='medium' if _gender=='male' else 'long',hair_color=_hair,eyes=_eyes,skin='light',identity='adult '+_en+'-inspired fictional '+('man' if _gender=='male' else 'woman')+' from '+_source,clothes='an opaque practical adventure outfit with full-length trousers and boots',persona=_persona)
 ALIASES[_key]=(_ru.lower(),_en.lower())


def has_reference(user):return bool(selected(user) or user.get('character_reference'))
def photo_disabled(user):return bool((user.get('character_reference') or {}).get('photo_disabled'))
def family_friendly(user):return bool((selected(user) or user.get('character_reference') or {}).get('family_friendly'))
def identity(user):
 v=selected(user);reference=user.get('character_reference') or {}
 if reference or v and user.get('custom_character'):
  import character_options
  name=reference.get('name') or v['en'];source=reference.get('source') or v['source']
  return 'Adult fictional '+name+' from '+source+'. '+character_options.identity(user)
 return ('Exactly one '+v['identity']+'. One continuous depiction of this character. ') if v else None

def prompt_rule(user):
 v=selected(user);reference=user.get('character_reference') or {}
 if not v and not reference:return ''
 name=reference.get('name') or v['ru'];source=reference.get('source') or v['source'];persona=(v or {}).get('persona','')
 return ('Это вымышленная интерпретация персонажа '+name+' из '+source+'. '+persona+
 ' Учитывай его вселенную, историю и узнаваемую манеру общения. Это обычное общение и неоткровенные приключения. Не заявляй, что сервис официальный. '
 'Описание пользователя задаёт изменения образа; актуальные выбранные параметры внешности важнее исходного канона. '+('Только семейное общение без романтических и сексуальных сцен. ' if family_friendly(user) else ''))

for _key,_clothes in {
 'lara_croft':'an opaque teal sleeveless top, brown cargo shorts and practical boots',
 'jill_valentine':'an opaque blue tank top, dark practical trousers and boots',
 'leon_kennedy':'a dark leather jacket over an opaque shirt, tactical trousers and boots',
 'geralt':'an opaque weathered armored tunic, practical dark trousers and leather boots',
 'yennefer':'an opaque black and white sorceress outfit, fitted trousers and boots',
 'bayonetta':'an opaque fitted black full-length fashion suit and dark glasses',
 'chun_li':'an opaque blue qipao-style outfit over opaque leggings and white boots',
 'samus':'opaque orange science-fiction power armor with a full helmet and arm cannon'
}.items():TEMPLATES[_key]['clothes']=_clothes
TEMPLATES['samus']['hair_style']='ponytail'
