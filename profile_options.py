"""Stored profile preferences, race choices and permanent wardrobe purchases."""
PREFERENCES={
 'foot_focus':('Акцент на стопах','Foot focus','Fokus auf Füße'),
 'bdsm_theme':('Тема BDSM','BDSM theme','BDSM-Thema'),
 'latex_style':('Латекс','Latex style','Latex-Stil'),
 'toys':('Игрушки','Toys','Spielzeuge'),
 'domination':('Доминирование','Domination','Dominanz'),
}
RACES={
 'human':('Человек','Human','Mensch'),
 'elf':('Эльф','Elf','Elf'),
 'succubus':('Суккуб','Succubus','Sukkubus'),
 'android':('Андроид','Android','Android'),
}
WARDROBE={
 'bunny_outfit':{'name':'Bunny Outfit','price':500,'emoji':'👗'},
 'latex_bodysuit':{'name':'Latex Bodysuit','price':750,'emoji':'🖤'},
 'stockings':{'name':'Stockings','price':200,'emoji':'🧦'},
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
