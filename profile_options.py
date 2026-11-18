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

FULL_OUTFIT_SLOTS=frozenset(('body','top','bottom','legs','outerwear'))


def occupied_slots(key):
 item=WARDROBE[key];slot=item.get('slot')
 if not slot:return set()
 # A full outfit can reserve more slots, never fewer than upper/lower body.
 base=set(FULL_OUTFIT_SLOTS) if slot=='body' else {slot}
 return base|set(item.get('occupies') or [])


def active_outfit(user):
 raw=user.get('active_outfit')
 if not isinstance(raw,dict):
  key=user.get('wardrobe_outfit');raw={WARDROBE[key]['slot']:key} if key in WARDROBE and WARDROBE[key]['slot'] else {}
 inventory=user.get('inventory') or {};result={};used=set()
 # Full outfits win over incompatible legacy combinations; inventory is never removed.
 for slot,key in sorted(raw.items(),key=lambda pair:0 if pair[0]=='body' else 1):
  if slot not in SLOTS or not isinstance(key,str) or key not in WARDROBE or WARDROBE[key]['slot']!=slot or not inventory.get(key) or not gender_matches(user,key):continue
  occupied=occupied_slots(key)
  if occupied&used:continue
  result[slot]=key;used|=occupied
 return result


def slot_locks(user):
 current=active_outfit(user);locks={}
 for slot,key in current.items():
  for occupied in occupied_slots(key)-{slot}:locks[occupied]=key
 return locks


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
  if not gender_matches(user,key):raise ValueError('Этот предмет предназначен для другого пола персонажа')
  if not (user.get('inventory') or {}).get(key):raise ValueError('Сначала купи этот предмет')
  if item['adult'] and level<5:raise ValueError('Раздел 18+ доступен с 5 уровня близости')
  if item.get('catalog_only'):raise ValueError('Этот предмет пока только в каталоге. Применение к фото ещё не подключено.')
  if not item['slot']:raise ValueError('Этот предмет хранится в инвентаре, его нельзя надеть')
  slot=item['slot']
  occupied=occupied_slots(key)
  conflicts=[other for other,old in current.items() if other!=slot and occupied_slots(old)&occupied]
  if slot!='body' and conflicts:
   blocker=WARDROBE[current[conflicts[0]]]
   raise ValueError('Сначала сними «'+blocker['ru']+'»: этот комплект занимает выбранное место')
  for other in conflicts:current.pop(other,None)
  current[slot]=key
 user['active_outfit']=current
 user['wardrobe_outfit']=current.get('body') # old clients retain their single outfit field
 return current

def clothing_facts(user,level):
 items=[WARDROBE[k] for k in active_outfit(user).values()]
 items=[i for i in items if not i.get('catalog_only') and (not i['adult'] or level>=5)]
 facts=[i['fact'] for i in items if i['fact']]
 if not any(i['slot'] in ('body','top','bottom') for i in items):facts.insert(0,'an opaque casual shirt and full-length trousers')
 elif any(i['slot']=='top' for i in items) and not any(i['slot']=='bottom' for i in items):facts.append('full-length casual trousers')
 elif any(i['slot']=='bottom' for i in items) and not any(i['slot']=='top' for i in items):facts.append('an opaque casual shirt')
 return ', '.join(facts)
WARDROBE['scarf']=dict(name='Scarf',ru='Шарф',de='Schal',price=200,slot='neck',adult=False,emoji='🧣',image='wardrobe_scarf',fact='a soft lavender scarf')

# Catalog expansion only. New tags are stored metadata, not image-generation facts.
# Keep the existing body/neck/legs slot names so old purchases remain compatible.
SLOTS['outerwear']=('Верхняя одежда','Outerwear','Oberbekleidung')
WARDROBE['tracksuit'].update(price=600,tags='tracksuit')
WARDROBE['latex_bodysuit'].update(price=2000,tags='latex bodysuit')


def _catalog_item(name,ru,de,price,slot,adult,tags,emoji,gender='unisex'):
 return dict(name=name,ru=ru,de=de,price=price,slot=slot,adult=adult,tags=tags,
             emoji=emoji,gender=gender,image='wardrobe_catalog_placeholder',fact='',catalog_only=True)


WARDROBE.update({
 'crop_top':_catalog_item('Crop top','Кроп-топ','Crop-Top',300,'top',False,'crop top','👚'),
 'oversized_shirt':_catalog_item('Oversized shirt','Рубашка оверсайз','Oversize-Hemd',400,'top',False,'oversized shirt','👕'),
 'denim_shorts':_catalog_item('Denim shorts','Джинсовые шорты','Jeansshorts',300,'bottom',False,'denim shorts','🩳'),
 'pencil_skirt':_catalog_item('Pencil skirt','Юбка-карандаш','Bleistiftrock',500,'bottom',False,'pencil skirt','👗'),
 'qipao':_catalog_item('Qipao','Китайское платье Ципао','Qipao-Kleid',1000,'body',False,'qipao, chinese dress','👗'),
 'cap':_catalog_item('Cap','Кепка','Kappe',200,'head',False,'cap','🧢'),
 'cat_ears_headband':_catalog_item('Cat-ear headband','Ободок с кошачьими ушками','Katzenohren-Haarreif',400,'head',False,'cat ears headband','🐱'),
 'maid_outfit':_catalog_item('Maid outfit','Костюм горничной','Dienstmädchen-Kostüm',1500,'body',True,'maid outfit, apron','🧹'),
 'nurse_outfit':_catalog_item('Nurse outfit','Костюм медсестры','Pflege-Kostüm',1500,'body',True,'nurse outfit','🩺'),
 'lace_panties':_catalog_item('Lace panties','Кружевные трусики','Spitzenhöschen',800,'bottom',True,'lace panties','🩲'),
 'collar_leash':_catalog_item('Collar with leash','Ошейник с поводком','Halsband mit Leine',600,'neck',True,'choker, collar','◉'),
 'garter_stockings':_catalog_item('Stockings with garter belt','Чулки с поясом','Strümpfe mit Strapsgürtel',900,'legs',True,'stockings, garter belt','🧦'),
 'business_suit':_catalog_item('Business suit','Деловой костюм','Business-Anzug',800,'body',False,'business suit, tie','👔','male'),
 'sportswear':_catalog_item('Sportswear','Спортивный комплект: майка и шорты','Sportset: Tanktop und Shorts',500,'body',False,'tank top, shorts, sportswear','🎽','male'),
 'casual_outfit':_catalog_item('Casual outfit','Худи и джинсы','Hoodie und Jeans',500,'body',False,'hoodie, jeans','👕','male'),
 'leather_jacket':_catalog_item('Leather jacket','Кожаная куртка','Lederjacke',600,'outerwear',False,'leather jacket','🧥','male'),
 'stripper_outfit':_catalog_item('Stage outfit with bow tie','Сценический костюм стриптизёра','Bühnenkostüm mit Fliege',1500,'body',True,'open shirt, bow tie','🎩','male'),
 'police_male':_catalog_item('Police outfit — male','Полицейская форма — мужская','Polizeikostüm — Herren',1500,'body',True,'sexy police uniform','👮','male'),
 'police_female':_catalog_item('Police outfit — female','Полицейская форма — женская','Polizeikostüm — Damen',1500,'body',True,'sexy police uniform','👮','female'),
})
# New adult-shop collection is catalog-only: no artwork jobs or photo prompt changes.
ADULT_CATALOG_ITEMS={
 'male_leather_harness':_catalog_item('Leather harness and trousers','Кожаная портупея с брюками','Lederharness mit Hose',1800,'body',True,'mens leather harness, leather trousers','🖤','male'),
 'male_leather_bodysuit':_catalog_item('Leather bodysuit — male','Кожаный комбинезон — мужской','Leder-Overall — Herren',2400,'body',True,'mens leather bodysuit','🖤','male'),
 'male_mesh_outfit':_catalog_item('Mesh top and trousers','Сетчатый верх с брюками','Netzoberteil mit Hose',1600,'body',True,'mens mesh top, black trousers','🕸️','male'),
 'male_bdsm_outfit':_catalog_item('BDSM outfit — male','БДСМ-комплект: брюки, ошейник и манжеты','BDSM-Set: Hose, Halsband und Manschetten',2600,'body',True,'mens leather trousers, collar, wrist cuffs','⛓️','male'),
 'female_corset_skirt':_catalog_item('Corset and skirt','Корсет с юбкой','Korsett mit Rock',1800,'body',True,'corset, fitted skirt','🖤','female'),
 'female_harness_bodysuit':_catalog_item('Opaque bodysuit with harness','Закрытое боди с портупеей','Blickdichter Body mit Harness',2300,'body',True,'opaque bodysuit, leather harness','⛓️','female'),
 'female_leather_outfit':_catalog_item('Leather outfit — female','Кожаный комплект — женский','Leder-Outfit — Damen',2200,'body',True,'womens leather top, leather trousers','🖤','female'),
 'female_mesh_dress':_catalog_item('Lined mesh dress','Сетчатое платье с подкладкой','Netzkleid mit blickdichtem Unterkleid',1900,'body',True,'mesh dress, opaque lining','🕸️','female'),
}
# Shop imagery is pre-generated at development time; tags remain catalog metadata only.
ADULT_CATALOG_ITEMS.update({
 'female_wetlook_catsuit':_catalog_item('Wet-look catsuit — female','Wet-look комбинезон — женский','Wetlook-Catsuit — Damen',2400,'body',True,'womens glossy wet look catsuit','🖤','female'),
 'female_ribbed_tights_black':_catalog_item('Black ribbed tights','Чёрные колготки в рубчик','Schwarze Rippstrumpfhose',650,'legs',True,'black ribbed tights','🧦','female'),
 'female_ribbed_tights_cream':_catalog_item('Cream ribbed tights','Кремовые колготки в рубчик','Cremefarbene Rippstrumpfhose',650,'legs',True,'cream ribbed tights','🧦','female'),
 'female_bodycon_jumpsuit':_catalog_item('Fitted jumpsuit — female','Обтягивающий комбинезон — женский','Enger Overall — Damen',1900,'body',True,'womens fitted burgundy jumpsuit','♥️','female'),
 'female_leather_miniskirt':_catalog_item('Leather miniskirt','Кожаная мини-юбка','Leder-Minirock',900,'bottom',True,'black leather miniskirt','🖤','female'),
 'female_pleated_miniskirt':_catalog_item('Pleated miniskirt','Мини-юбка в складку','Falten-Minirock',800,'bottom',True,'red plaid pleated miniskirt','👗','female'),
 'female_neckline_dress':_catalog_item('V-neck mini dress','Мини-платье с декольте','Minikleid mit V-Ausschnitt',1600,'body',True,'burgundy v neck mini dress','♥️','female'),
 'female_fox_cosplay':_catalog_item('Fox cosplay — female','Косплей «Лисичка»','Fuchs-Cosplay — Damen',2300,'body',True,'fox cosplay dress, fox ears headband, decorative fox tail','🦊','female'),
 'female_satin_robe':_catalog_item('Satin robe — female','Атласный халат — женский','Satin-Morgenmantel — Damen',1400,'outerwear',True,'womens burgundy satin robe','🌹','female'),
 'female_kimono_robe':_catalog_item('Floral kimono robe','Халат-кимоно с цветами','Kimono-Morgenmantel mit Blumen',1700,'outerwear',True,'floral plum kimono robe, sash','🌸','female'),
 'female_strappy_lingerie':_catalog_item('Strappy lingerie set','Бельё с ремешками','Dessous-Set mit Riemchen',1800,'body',True,'black strappy lingerie set, opaque panels','🖤','female'),
 'female_stewardess':_catalog_item('Flight attendant cosplay','Костюм стюардессы','Flugbegleiterinnen-Kostüm',1900,'body',True,'navy flight attendant skirt suit, neck scarf, hat','✈️','female'),
 'female_teacher':_catalog_item('Teacher cosplay','Костюм учительницы','Lehrerinnen-Kostüm',1700,'body',True,'adult teacher cosplay, white blouse, pencil skirt, glasses','👓','female'),
 'female_angel':_catalog_item('Angel costume','Костюм ангела','Engelskostüm',2600,'body',True,'white angel costume dress, feather wings, halo','🤍','female'),
 'female_devil':_catalog_item('Devil costume','Костюм дьяволицы','Teufelinnen-Kostüm',2600,'body',True,'burgundy devil costume dress, horns headband, decorative tail','😈','female'),
 'female_onepiece_swimsuit':_catalog_item('One-piece swimsuit','Слитный купальник','Einteiliger Badeanzug',1200,'body',True,'blue opaque one piece swimsuit','🌊','female'),
 'female_bikini':_catalog_item('Emerald bikini','Изумрудное бикини','Smaragdgrüner Bikini',1300,'body',True,'emerald bikini swimwear, opaque fabric','👙','female'),
 'female_lace_bodystocking':_catalog_item('Lace bodystocking','Кружевной бодистокинг','Spitzen-Bodystocking',2000,'body',True,'black lace pattern bodystocking, opaque panels','🕸️','female'),
 'female_bandage_dress':_catalog_item('Bandage dress','Бандажное платье','Bandagekleid',2100,'body',True,'black fitted bandage mini dress','🖤','female'),
 'female_openback_dress':_catalog_item('Open-back dress','Платье с открытой спиной','Rückenfreies Kleid',1800,'body',True,'burgundy open back evening dress','🌹','female'),
 'male_wetlook_catsuit':_catalog_item('Wet-look catsuit — male','Wet-look комбинезон — мужской','Wetlook-Catsuit — Herren',2400,'body',True,'mens glossy wet look catsuit','🖤','male'),
 'male_bodycon_jumpsuit':_catalog_item('Fitted jumpsuit — male','Обтягивающий комбинезон — мужской','Enger Overall — Herren',1900,'body',True,'mens fitted burgundy jumpsuit','♥️','male'),
 'male_satin_robe':_catalog_item('Satin robe — male','Атласный халат — мужской','Satin-Morgenmantel — Herren',1400,'outerwear',True,'mens navy satin robe','🌙','male'),
 'male_fox_cosplay':_catalog_item('Fox cosplay — male','Косплей «Лис»','Fuchs-Cosplay — Herren',2300,'body',True,'mens orange fox cosplay jacket, black trousers, fox ears headband, decorative fox tail','🦊','male'),
})
WARDROBE.update(ADULT_CATALOG_ITEMS)

for _item in WARDROBE.values():
 _item.setdefault('tags','')
 _item.setdefault('gender','unisex')
 _item.setdefault('catalog_only',False)

# Generated catalog art and wearable descriptions. Preferences are not image tags.
OUTFIT_FACTS={
 'crop_top':'an opaque casual crop top','oversized_shirt':'an opaque oversized shirt',
 'denim_shorts':'denim shorts','pencil_skirt':'an opaque knee-length pencil skirt',
 'qipao':'an elegant opaque high-neck qipao dress','cap':'a casual cap',
 'cat_ears_headband':'a decorative cat-ear headband','maid_outfit':'an opaque knee-length black and white uniform dress with apron',
 'nurse_outfit':'an opaque knee-length nurse uniform dress','lace_panties':'opaque underwear worn under an ordinary skirt',
 'collar_leash':'a simple black fashion neck band','garter_stockings':'opaque dark stockings worn with an ordinary knee-length skirt',
 'business_suit':'a business suit with tie','sportswear':'a tank top and sports shorts',
 'casual_outfit':'a hoodie and jeans','leather_jacket':'a leather jacket',
 'stripper_outfit':'an opaque white stage shirt with bow tie and full-length trousers',
 'police_male':'a navy police uniform shirt and trousers','police_female':'a navy police uniform shirt and trousers',
}
for _key,_item in WARDROBE.items():
 _item['image']='catalog_'+_key
 if _key in OUTFIT_FACTS:
  _item.update(fact=OUTFIT_FACTS[_key],catalog_only=False)

# Slot occupancy is a wardrobe rule, independent of image tags.
for _key,_item in WARDROBE.items():
 _item['occupies']=[_item['slot']] if _item.get('slot') else []
 if _item.get('slot')=='body':_item['occupies']=['body','top','bottom','legs','outerwear']
for _key in ('police_male','police_female'):
 WARDROBE[_key]['occupies']=list(SLOTS)
for _key,_extra in {'bunny_outfit':['head'],'business_suit':['neck'],'stripper_outfit':['neck'],'male_bdsm_outfit':['neck'],'female_fox_cosplay':['head'],'male_fox_cosplay':['head'],'female_stewardess':['head','neck'],'female_angel':['head'],'female_devil':['head']}.items():
 WARDROBE[_key]['occupies']=list(set(WARDROBE[_key]['occupies'])|set(_extra))


def occupancy_label(key,lang='ru'):
 slots=occupied_slots(key)
 if len(slots)<2:return ''
 if slots==set(SLOTS):return {'ru':'Занимает весь образ','de':'Belegt das gesamte Outfit'}.get(lang,'Occupies the entire outfit')
 free=[labels[{'ru':0,'en':1,'de':2}.get(lang,1)] for slot,labels in SLOTS.items() if slot not in slots]
 return {'ru':'Свободно: ','de':'Frei: '}.get(lang,'Free: ')+', '.join(free)


# Catalog suitability is enforced for both purchase and equip, not just hidden in the UI.
for _key in ('dress','heels','stockings','bunny_outfit','latex_bodysuit','qipao','maid_outfit','nurse_outfit','lace_panties','garter_stockings','crop_top','pencil_skirt'):
 WARDROBE[_key]['gender']='female'

def gender_matches(user,key):
 gender=user.get('gender')
 return gender not in ('male','female') or WARDROBE[key].get('gender','unisex') in ('unisex',gender)

def fitting_preview(user):
 """A static, coherent full outfit illustration; selecting clothes makes no provider call.
 These previews show the principal outfit; photo generation uses every equipped slot.
 """
 gender='male' if user.get('gender')=='male' else 'female'
 current=active_outfit(user);body=current.get('body')
 indices={
 'female':{'dress':0,'tracksuit':1,'pajamas':2,'qipao':3,'maid_outfit':4,'nurse_outfit':5,'latex_bodysuit':6,'bunny_outfit':7,'police_female':8,'casual_outfit':14,'sportswear':15},
 'male':{'business_suit':0,'casual_outfit':1,'sportswear':3,'police_male':4,'tracksuit':6,'pajamas':7,'stripper_outfit':10}}
 index=indices[gender].get(body)
 if index is None:
  top=current.get('top');bottom=current.get('bottom')
  if current.get('outerwear')=='leather_jacket':index=17 if gender=='female' else 2
  elif gender=='female':
   index=11 if top=='crop_top' else 12 if bottom=='pencil_skirt' else 10 if top=='oversized_shirt' or bottom=='denim_shorts' else 13
  else:index=12 if top=='oversized_shirt' or bottom=='denim_shorts' else 8
 return '/assets/fitting_'+gender+'_'+str(index)+'.webp'
