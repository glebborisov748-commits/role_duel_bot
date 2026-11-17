"""Stored profile preferences, race choices and permanent wardrobe purchases."""
PREFERENCES={
 'foot_focus':('Акцент на стопах','Foot focus','Fokus auf Füße'),
 'bdsm_theme':('Тема BDSM','BDSM theme','BDSM-Thema'),
 'latex_style':('Латекс','Latex style','Latex-Stil'),
 'toys':('Игрушки','Toys','Spielzeuge'),
 'domination':('Доминирование','Domination','Dominanz'),
}
RACES={
 'human':('Человек','Human','Mensch'), 'elf':('Эльф','Elf','Elf'),
 'catfolk':('Кошачий народ','Catfolk','Katzenmensch'), 'foxfolk':('Лисий народ','Foxfolk','Fuchsmensch'),
 'wolffolk':('Волчий народ','Wolffolk','Wolfsmensch'), 'vampire':('Вампир','Vampire','Vampir'),
 'angel':('Ангел','Angel','Engel'), 'succubus':('Демон','Demon','Dämon'),
 'android':('Андроид','Android','Android'), 'dragonborn':('Драконий народ','Dragonfolk','Drachenmensch'),
}
RACE_FACTS={'human':'human','elf':'elf with pointed ears','catfolk':'human face with cat ears','foxfolk':'human face with fox ears','wolffolk':'human face with wolf ears','vampire':'adult vampire with subtle fangs','angel':'adult human with a subtle golden halo','succubus':'adult humanoid with small curved horns','android':'humanoid android with discreet metallic temples','dragonborn':'adult humanoid with small horns and subtle temple scales'}
WARDROBE={
 'bunny_outfit':{'name':'Bunny Outfit','ru':'Костюм «Зайка»','de':'Hasenkostüm','price':500,'emoji':'👗','image':'wardrobe_bunny','fact':'opaque black stage costume, tuxedo jacket, bow tie and rabbit-ear headband'},
 'latex_bodysuit':{'name':'Latex Bodysuit','ru':'Латексный комбинезон','de':'Latex-Overall','price':750,'emoji':'🖤','image':'wardrobe_latex','fact':'opaque full-length high-neck long-sleeved charcoal fashion jumpsuit'},
 'stockings':{'name':'Stockings','ru':'Чулки','de':'Strümpfe','price':200,'emoji':'🧦','image':'wardrobe_stockings','fact':'opaque dark fashion stockings with a modest skirt and top'},
 'dress':{'name':'Evening dress','ru':'Вечернее платье','de':'Abendkleid','price':1200,'emoji':'👗','image':'gift_dress','fact':'elegant opaque evening dress'},
 'heels':{'name':'Heeled shoes','ru':'Туфли на каблуке','de':'Pumps','price':900,'emoji':'👠','image':'gift_heels','fact':'elegant heeled shoes with a modest everyday outfit'},
}

def defaults():return dict.fromkeys(PREFERENCES,False)

def preferences(user):
 raw=user.get('preferences') or {}
 return {k:raw.get(k) is True for k in PREFERENCES} if isinstance(raw,dict) else defaults()

def validate_preferences(raw,current=None):
 if not isinstance(raw,dict) or set(raw)-PREFERENCES.keys() or any(type(v) is not bool for v in raw.values()):raise ValueError('Invalid preferences')
 return {**(current or defaults()),**raw}

def validate_race(value):
 if not isinstance(value,str) or value not in RACES:raise ValueError('Invalid race')
 return value

def choices(mapping,lang):
 ix={'ru':0,'en':1,'de':2}.get(lang,1)
 return [{'key':key,'label':labels[ix]} for key,labels in mapping.items()]

def state(user):
 lang=user.get('lang','ru')
 return {'preferences':preferences(user),'preference_options':choices(PREFERENCES,lang),'race':user.get('race','human'),'races':choices(RACES,lang),'inventory':dict(user.get('inventory') or {})}

# Purchases remain permanent. Equipping never starts a paid generation.
PREFERENCES.update({
 'hair_pulling':('Тянуть за волосы','Hair pulling','An den Haaren ziehen'),
 'biting':('Укусы','Biting','Beißen'),
 'breast_focus':('Акцент на груди','Breast focus','Fokus auf die Brust'),
})
WARDROBE['dress'].update(price=350,slot='body',adult=False,fact='an elegant opaque knee-length evening dress')
WARDROBE['heels'].update(price=300,slot='shoes',adult=False,fact='elegant heeled shoes')
WARDROBE['stockings'].update(slot='legs',adult=False,fact='opaque dark fashion stockings')
WARDROBE['bunny_outfit'].update(price=1800,slot='body',adult=True)
WARDROBE['latex_bodysuit'].update(price=2500,slot='body',adult=True)
WARDROBE.update({
 'tracksuit':dict(name='Tracksuit',ru='Спортивный костюм',de='Trainingsanzug',price=450,slot='body',adult=False,emoji='👟',image='wardrobe_tracksuit',fact='a comfortable opaque matching tracksuit'),
 'pajamas':dict(name='Pajamas',ru='Пижама',de='Schlafanzug',price=250,slot='body',adult=False,emoji='🌙',image='wardrobe_pajamas',fact='a soft opaque long-sleeve pajama set'),
 'collar':dict(name='Collar',ru='Ошейник',de='Halsband',price=1500,slot='neck',adult=True,emoji='◉',image='wardrobe_collar',fact='a simple black fashion neck band'),
 'vibrator':dict(name='Personal massager',ru='Вибратор',de='Vibrator',price=3000,slot=None,adult=True,emoji='◇',image='wardrobe_massager',fact=''),
})
SLOTS={'body':('Костюм / платье','Outfit / dress','Outfit / Kleid'),
       'top':('Верх','Top','Oberteil'),'bottom':('Низ','Bottom','Unterteil'),
       'head':('Головной убор','Headwear','Kopfbedeckung'),'legs':('Чулки','Stockings','Strümpfe'),
       'shoes':('Обувь','Shoes','Schuhe'),'neck':('На шею','Neckwear','Halsschmuck')}
WARDROBE.update({
 'shirt':dict(name='Shirt',ru='Рубашка',de='Hemd',price=200,slot='top',adult=False,emoji='👕',image='wardrobe_shirt',fact='an opaque casual shirt'),
 'trousers':dict(name='Trousers',ru='Брюки',de='Hose',price=250,slot='bottom',adult=False,emoji='👖',image='wardrobe_trousers',fact='casual full-length trousers'),
 'hat':dict(name='Hat',ru='Шляпа',de='Hut',price=200,slot='head',adult=False,emoji='🎩',image='wardrobe_hat',fact='a stylish casual hat'),
})

def active_outfit(user):
 raw=user.get('active_outfit')
 if not isinstance(raw,dict):
  key=user.get('wardrobe_outfit');raw={WARDROBE[key]['slot']:key} if key in WARDROBE and WARDROBE[key]['slot'] else {}
 inventory=user.get('inventory') or {}
 return {slot:key for slot,key in raw.items() if slot in SLOTS and isinstance(key,str) and key in WARDROBE and WARDROBE[key]['slot']==slot and inventory.get(key)}

def equip(user,key,level,slot=None):
 if slot is not None and (not isinstance(slot,str) or slot not in SLOTS):raise ValueError('Unknown slot')
 current=active_outfit(user)
 if key is None:
  if slot is None:current={}
  elif slot not in SLOTS:raise ValueError('Unknown slot')
  else:current.pop(slot,None)
 else:
  if not isinstance(key,str) or key not in WARDROBE:raise ValueError('Unknown item')
  item=WARDROBE[key]
  if not (user.get('inventory') or {}).get(key):raise ValueError('Сначала купи этот предмет')
  if item['adult'] and level<5:raise ValueError('Раздел 18+ доступен с 5 уровня близости')
  if not item['slot']:raise ValueError('Этот предмет хранится в инвентаре, его нельзя надеть')
  slot=item['slot']
  if slot=='body':current.pop('top',None);current.pop('bottom',None)
  if slot in ('top','bottom'):current.pop('body',None)
  current[slot]=key
 user['active_outfit']=current
 user['wardrobe_outfit']=current.get('body') # old clients retain their single outfit field
 return current

def clothing_facts(user,level):
 items=[WARDROBE[k] for k in active_outfit(user).values()]
 items=[i for i in items if not i['adult'] or level>=5]
 facts=[i['fact'] for i in items if i['fact']]
 if not any(i['slot'] in ('body','top','bottom') for i in items):facts.insert(0,'an opaque casual shirt and full-length trousers')
 elif any(i['slot']=='top' for i in items) and not any(i['slot']=='bottom' for i in items):facts.append('full-length casual trousers')
 elif any(i['slot']=='bottom' for i in items) and not any(i['slot']=='top' for i in items):facts.append('an opaque casual shirt')
 return ', '.join(facts)
WARDROBE['scarf']=dict(name='Scarf',ru='Шарф',de='Schal',price=200,slot='neck',adult=False,emoji='🧣',image='wardrobe_scarf',fact='a soft lavender scarf')
