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
def identity(user):
 v=selected(user)
 return ('Exactly one '+v['identity']+'. One coherent person, not a costume display or character sheet. ') if v else None

def prompt_rule(user):
 v=selected(user)
 if not v:return ''
 return ('Ты — самостоятельная вымышленная интерпретация '+v['ru']+' из '+v['source']+'. '+v['persona']+
         ' Узнаваемый образ: '+v['identity']+'. Это обычное общение и неоткровенные приключения. Не создавай сексуальные сцены и не заявляй, что это официальный персонаж или сервис. ')
def family_friendly(user):return bool((selected(user) or {}).get('family_friendly'))
def avatar_url(user):
 key=user.get('avatar_preset');key=key if key in AVATARS else ('male_1' if user.get('gender')=='male' else 'female_1')
 return '/assets/default_avatar_'+key+'.webp'
def avatar_choices(lang='ru'):
 return [dict(key=k,label=v[0 if lang=='ru' else 1],image='/assets/default_avatar_'+k+'.webp') for k,v in AVATARS.items()]
