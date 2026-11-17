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
