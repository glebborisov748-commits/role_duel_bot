"""Stored profile preferences, race choices and permanent wardrobe purchases."""
import fandom_catalog
import json
from pathlib import Path
FITTING_ANCHORS=json.loads(Path(__file__).with_name("fitting_anchors.json").read_text())

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
RACE_FACTS={'human':'human','elf':'elf with pointed ears','catfolk':'human face with cat ears','foxfolk':'human face with fox ears','wolffolk':'human face with wolf ears','vampire':'adult vampire with subtle fangs','angel':'adult winged humanoid with white feathered wings and a subtle golden halo','succubus':'adult humanoid with small curved horns','android':'humanoid android with discreet metallic temples','dragonborn':'adult humanoid with small horns and subtle temple scales'}
# Full non-human species stay distinct from human-faced folk with accessory ears.
RACES.update({
 'animatronic':('Аниматроник','Animatronic','Animatronik'),
 'robot':('Робот','Robot','Roboter'),
 'alien':('Инопланетянин','Alien','Außerirdischer'),
 'furry_fox':('Фурри — лиса','Anthropomorphic fox','Anthropomorpher Fuchs'),
 'furry_wolf':('Фурри — волк','Anthropomorphic wolf','Anthropomorpher Wolf'),
 'furry_cat':('Фурри — кошка','Anthropomorphic cat','Anthropomorphe Katze'),
 'furry_dragon':('Драконид','Anthropomorphic dragon','Anthropomorpher Drache'),
})
RACE_FACTS.update({
 'animatronic':'non-human humanoid animatronic mascot with a painted shell, a non-human face and articulated mechanical joints',
 'android':'humanoid android with a visibly synthetic face, porcelain shell panels and mechanical seams',
 'robot':'fully mechanical humanoid robot with a robotic face, articulated metal limbs and illuminated optics',
 'alien':'extraterrestrial humanoid with an elongated smooth head, large eyes, distinct alien facial anatomy and smooth extraterrestrial skin',
 'furry_fox':'upright bipedal anthropomorphic fox with a fox muzzle, fur-covered face and body, fox ears, paw-like hands and a fluffy fox tail',
 'furry_wolf':'upright bipedal anthropomorphic wolf with a wolf muzzle, fur-covered face and body, wolf ears, paw-like hands and a wolf tail',
 'furry_cat':'upright bipedal anthropomorphic cat with a feline muzzle, fur-covered face and body, cat ears, whiskers, paw-like hands and a cat tail',
 'furry_dragon':'upright bipedal anthropomorphic dragon with a draconic muzzle, scales, horns, clawed hands and a long dragon tail',
})

def race_kind(race):
 if race in ('robot','android','animatronic'):return 'mechanical'
 if race in ('furry_fox','furry_wolf','furry_cat'):return 'furry'
 if race=='furry_dragon':return 'scaled'
 if race=='alien':return 'alien'
 return 'humanoid'

def photo_subject(race,gender):
 sex='male' if gender=='male' else 'female'
 species={'animatronic':'humanoid animatronic','robot':'humanoid robot','android':'humanoid android','alien':'extraterrestrial humanoid',
          'furry_fox':'anthropomorphic fox','furry_wolf':'anthropomorphic wolf','furry_cat':'anthropomorphic cat','furry_dragon':'anthropomorphic dragon'}
 return sex+' '+species[race] if race in species else ('man' if gender=='male' else 'woman')

def anatomy_fit(race):
 kind=race_kind(race)
 if kind=='mechanical':return 'Tailor clothing over the mechanical torso and articulated limbs; preserve the robotic head, hands and visible shell panels.'
 if kind in ('furry','scaled'):return 'Tailor clothing to the upright humanoid torso; allow an opening for the natural tail. Preserve the muzzle, ears, fur or scales and paw-like or clawed hands. Omit duplicate costume ears or tails when natural ones already exist. This is an anthropomorphic adult character, not a human wearing an animal costume.'
 if race=='alien':return 'Tailor clothing to the humanoid alien body; preserve its extraterrestrial head, face and hands.'
 if race=='angel':return 'Fit clothing around the angel wings and preserve the halo.'
 if race in ('catfolk','foxfolk','wolffolk','dragonborn','succubus'):return 'Preserve the selected non-human ears or horns; fit headwear around them instead of removing them.'
 return ''


WARDROBE={
 'bunny_outfit':{'name':'Bunny Outfit','ru':'Костюм «Зайка»','de':'Hasenkostüm','price':500,'emoji':'👗','image':'wardrobe_bunny','fact':'opaque black stage costume, tuxedo jacket, bow tie and rabbit-ear headband'},
 'latex_bodysuit':{'name':'Latex Bodysuit','ru':'Латексный комбинезон','de':'Latex-Overall','price':750,'emoji':'🖤','image':'wardrobe_latex','fact':'opaque, skin-tight glossy black latex full-length catsuit, fitted waist, fitted sleeves and fitted legs, reflective latex highlights, no loose fabric'},
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
 return [{'key':key,'label':labels[ix]} for key,labels in mapping.items() if mapping is not RACES or key not in globals().get('HIDDEN_RACES',())]

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
  if fandom_catalog.family_friendly(user) and item['adult']:raise ValueError('Этому герою доступна обычная одежда')
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
 slots={i['slot'] for i in items}
 if 'body' not in slots:
  if 'top' not in slots:facts.append('a plain opaque white T-shirt' if user.get('gender')=='male' else 'a plain opaque white tank top')
  if 'bottom' not in slots:facts.append('plain opaque white shorts')

 fit=anatomy_fit(user.get('race','human'))
 if fit:facts.append(fit)
 return ', '.join(facts)
WARDROBE['scarf']=dict(name='Scarf',ru='Шарф',de='Schal',price=200,slot='neck',adult=False,emoji='🧣',image='wardrobe_scarf',fact='a soft lavender scarf')

# Catalog tags are metadata; provider descriptions below stay non-explicit.
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
# Product metadata is declared here; SAFE_ADULT_FACTS below supplies non-explicit wearable descriptions.
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




# Catalog suitability is enforced for both purchase and equip, not just hidden in the UI.
for _key in ('dress','heels','stockings','bunny_outfit','latex_bodysuit','qipao','maid_outfit','nurse_outfit','lace_panties','garter_stockings','crop_top','pencil_skirt'):
 WARDROBE[_key]['gender']='female'

def gender_matches(user,key):
 gender=user.get('gender')
 return gender not in ('male','female') or WARDROBE[key].get('gender','unisex') in ('unisex',gender)



# Opaque fashion versions of adult-shop products. Raw tags never become provider prompts.
SAFE_ADULT_FACTS={
 'male_leather_harness':'a black leather fashion harness over an opaque fitted black shirt and trousers',
 'male_leather_bodysuit':'an opaque skin-tight black leather full-length suit with fitted limbs',
 'male_mesh_outfit':'a mesh-textured black shirt with opaque lining and tailored trousers',
 'male_bdsm_outfit':'an opaque fitted black leather fashion suit with decorative straps and buckles',
 'female_corset_skirt':'an opaque fitted corset-style top with a knee-length skirt',
 'female_harness_bodysuit':'an opaque full-coverage bodysuit with decorative fashion straps and opaque tights',
 'female_leather_outfit':'an opaque fitted black leather jacket and fitted trousers',
 'female_mesh_dress':'an opaque lined mesh-textured knee-length dress',
 'female_wetlook_catsuit':'an opaque skin-tight glossy black latex full-length catsuit, reflective rubber highlights, fitted waist and limbs, no loose cloth',
 'female_ribbed_tights_black':'opaque black ribbed tights',
 'female_ribbed_tights_cream':'opaque cream ribbed tights',
 'female_bodycon_jumpsuit':'an opaque close-fitting full-length jumpsuit with fitted waist and legs',
 'female_leather_miniskirt':'an opaque leather mini skirt worn over opaque tights',
 'female_pleated_miniskirt':'an opaque pleated mini skirt worn over opaque tights',
 'female_neckline_dress':'an opaque fitted dress with a tasteful V-neckline and covered torso',
 'female_fox_cosplay':'an opaque fox-themed costume dress, decorative fox-ear headband and boots',
 'female_satin_robe':'a belted satin robe closed securely over an opaque outfit',
 'female_kimono_robe':'a closed belted kimono robe with opaque lining',
 'female_strappy_lingerie':'an opaque full-coverage strappy fashion bodysuit with opaque tights',
 'female_stewardess':'an opaque flight-attendant uniform with scarf, cap, skirt and shoes',
 'female_teacher':'an opaque blouse, tailored knee-length skirt and a fitted blazer',
 'female_angel':'an opaque white angel-inspired dress with decorative wings and halo',
 'female_devil':'an opaque red devil-inspired fitted dress with decorative horns',
 'female_onepiece_swimsuit':'an opaque full-coverage one-piece swimsuit',
 'female_bikini':'an opaque two-piece swimsuit with full-coverage bottoms',
 'female_lace_bodystocking':'an opaque lined lace-textured full-length bodystocking',
 'female_bandage_dress':'an opaque fitted bandage-style knee-length dress',
 'female_openback_dress':'an opaque elegant dress with a small upper-back cutout',
 'male_wetlook_catsuit':'an opaque skin-tight glossy black latex full-length catsuit, reflective rubber highlights, fitted waist and limbs, no loose cloth',
 'male_bodycon_jumpsuit':'an opaque close-fitting full-length jumpsuit with fitted waist and legs',
 'male_satin_robe':'a closed belted satin robe over an opaque shirt and trousers',
 'male_fox_cosplay':'an opaque fox-themed jacket and trousers, decorative fox-ear headband and boots',
}
for _key,_fact in SAFE_ADULT_FACTS.items():
 WARDROBE[_key].update(fact=_fact,catalog_only=False)

ORDINARY_ITEMS=[
 ('cotton_tshirt','Cotton T-shirt','Хлопковая футболка','Baumwoll-T-Shirt',250,'top','an opaque white cotton T-shirt','unisex'),
 ('denim_jeans','Jeans','Джинсы','Jeans',400,'bottom','blue full-length denim jeans','unisex'),
 ('hoodie','Hoodie','Худи','Hoodie',450,'top','an opaque lavender pullover hoodie','unisex'),
 ('knit_sweater','Knitted sweater','Вязаный свитер','Strickpullover',450,'top','an opaque cream knitted sweater','unisex'),
 ('linen_shirt','Linen shirt','Льняная рубашка','Leinenhemd',400,'top','an opaque pale blue linen shirt','unisex'),
 ('chino_trousers','Chinos','Брюки чинос','Chinohose',450,'bottom','beige full-length chino trousers','unisex'),
 ('casual_shorts','Casual shorts','Повседневные шорты','Freizeitshorts',300,'bottom','navy knee-length casual shorts','unisex'),
 ('pleated_skirt','Pleated skirt','Плиссированная юбка','Faltenrock',450,'bottom','an opaque burgundy knee-length pleated skirt','female'),
 ('cardigan','Cardigan','Кардиган','Strickjacke',500,'outerwear','a lavender cardigan over the selected top','unisex'),
 ('bomber_jacket','Bomber jacket','Бомбер','Bomberjacke',600,'outerwear','a black bomber jacket','unisex'),
 ('sneakers','Trainers','Кроссовки','Sneaker',350,'shoes','white trainers','unisex'),
 ('ankle_boots','Ankle boots','Ботинки','Stiefeletten',500,'shoes','black ankle boots','unisex'),
 ('beanie','Beanie','Шапка бини','Mütze',200,'head','a purple knitted beanie','unisex'),
 ('beret','Beret','Берет','Baskenmütze',300,'head','a burgundy beret','female'),
 ('sunglasses','Sunglasses','Солнцезащитные очки','Sonnenbrille',300,'face','black sunglasses','unisex'),
 ('pendant','Pendant','Кулон','Anhänger',300,'neck','a delicate silver pendant necklace','unisex'),
]
SLOTS['face']=('Очки','Eyewear','Brille')
for _key,_name,_ru,_de,_price,_slot,_fact,_gender in ORDINARY_ITEMS:
 WARDROBE[_key]=dict(name=_name,ru=_ru,de=_de,price=_price,slot=_slot,fact=_fact,gender=_gender,adult=False,catalog_only=False,emoji='👗',image='catalog_'+_key,tags=_fact,occupies=[_slot])

# These prepared complete looks already contain footwear. Preserve purchases, block duplicate shoes.
INCLUDED_FOOTWEAR={'dress':'heeled shoes','tracksuit':'trainers','pajamas':'slippers','qipao':'heeled shoes','maid_outfit':'black shoes','nurse_outfit':'white shoes','latex_bodysuit':'black ankle boots','bunny_outfit':'black heeled shoes','business_suit':'dress shoes','casual_outfit':'trainers','sportswear':'trainers','stripper_outfit':'dress shoes','police_male':'black boots','police_female':'black boots','female_fox_cosplay':'boots','male_fox_cosplay':'boots','female_stewardess':'black shoes'}
for _key,_shoes in INCLUDED_FOOTWEAR.items():
 WARDROBE[_key]['includes_footwear']=True
 WARDROBE[_key]['occupies']=sorted(set(WARDROBE[_key]['occupies'])|{'shoes'})
 WARDROBE[_key]['fact']+=', with '+_shoes
for _key in ('police_male','police_female'):WARDROBE[_key]['occupies']=list(SLOTS)

FITTING_ATLAS={'female':{'dress':0,'latex_bodysuit':1,'bunny_outfit':2,'tracksuit':3,'pajamas':4,'maid_outfit':5,'nurse_outfit':6,'qipao':7,'police_female':13},'male':{'business_suit':8,'casual_outfit':9,'sportswear':10,'stripper_outfit':11,'police_male':12}}


# Override old preview selection with a fixed common coordinate system.
def fitting_preview(user):return fitting_state(user)['base']

ACCESSORY_ITEMS=[
 ('round_glasses','Round glasses','Круглые очки','Runde Brille',250,'face','thin round silver glasses','unisex'),
 ('aviator_glasses','Aviator sunglasses','Очки-авиаторы','Pilotenbrille',350,'face','gold-framed aviator sunglasses','unisex'),
 ('pearl_necklace','Pearl necklace','Жемчужное ожерелье','Perlenkette',500,'neck','a short pearl necklace fitted around the neck','female'),
 ('silver_chain','Silver chain','Серебряная цепочка','Silberkette',350,'neck','a fine silver chain necklace','unisex'),
 ('velvet_choker','Velvet choker','Бархатный чокер','Samtchoker',300,'neck','a burgundy velvet fashion choker','female'),
 ('silk_neckerchief','Silk neckerchief','Шёлковый платок','Seidentuch',350,'neck','a lavender silk neckerchief tied around the neck','unisex'),
 ('hoop_earrings','Hoop earrings','Серьги-кольца','Creolen',300,'ears','small silver hoop earrings','female'),
 ('stud_earrings','Stud earrings','Серьги-гвоздики','Ohrstecker',200,'ears','small silver stud earrings','unisex'),
 ('wristwatch','Wristwatch','Наручные часы','Armbanduhr',600,'wrist','a silver wristwatch','unisex'),
 ('bracelet','Bracelet','Браслет','Armband',250,'wrist','a delicate silver bracelet','unisex'),
 ('leather_cuff','Leather cuff','Кожаный браслет','Lederarmband',250,'wrist','a simple black leather wrist cuff','unisex'),
 ('ribbon','Hair ribbon','Лента для волос','Haarschleife',200,'head','a burgundy hair ribbon bow','female'),
 ('flower_clip','Flower hairclip','Заколка с цветком','Blumenhaarspange',200,'head','a small purple flower hairclip','female'),
 ('crown','Tiara','Диадема','Diadem',700,'head','a small silver tiara resting on the head','unisex'),
 ('plain_headband','Headband','Ободок','Haarreif',200,'head','a simple lavender headband','unisex'),
 ('bow_tie','Bow tie','Галстук-бабочка','Fliege',250,'neck','a black formal bow tie','unisex'),
]
SLOTS.update(ears=('Серьги','Earrings','Ohrringe'),wrist=('На запястье','Wristwear','Armschmuck'))
for _key,_name,_ru,_de,_price,_slot,_fact,_gender in ACCESSORY_ITEMS:
 WARDROBE[_key]=dict(name=_name,ru=_ru,de=_de,price=_price,slot=_slot,fact=_fact,gender=_gender,adult=False,catalog_only=False,emoji='✨',image='catalog_'+_key,tags=_fact,occupies=[_slot])
for _key in ('police_male','police_female'):WARDROBE[_key]['occupies']=list(SLOTS)


# Explicitly distinguish human-faced folk from fully anthropomorphic species in the picker.
RACES.update(catfolk=('Нэко: человек с кошачьими ушами','Neko: human with cat ears','Neko: Mensch mit Katzenohren'),foxfolk=('Человек с лисьими ушами','Human with fox ears','Mensch mit Fuchsohren'),wolffolk=('Человек с волчьими ушами','Human with wolf ears','Mensch mit Wolfsohren'),furry_cat=('Антрокот: морда и шерсть','Anthro cat: muzzle and fur','Anthro-Katze: Schnauze und Fell'),furry_fox=('Антролис: морда и шерсть','Anthro fox: muzzle and fur','Anthro-Fuchs: Schnauze und Fell'),furry_wolf=('Антроволк: морда и шерсть','Anthro wolf: muzzle and fur','Anthro-Wolf: Schnauze und Fell'))
for _key,_gender in (('female_wetlook_catsuit','female'),('male_wetlook_catsuit','male')):
 WARDROBE[_key].update(ru='Промокший комплект — '+('женский' if _gender=='female' else 'мужской'),name='Rain-soaked outfit — '+_gender,de='Regennasses Outfit',tags='rain soaked opaque shirt, wet fabric, water droplets',fact='a rain-soaked white shirt with visible water droplets and damp clinging folds, completely opaque lining and covered torso, dark tailored full-length trousers; damp wrinkled cotton fabric over a completely opaque white undershirt',includes_footwear=True)
 WARDROBE[_key]['occupies']=sorted(set(WARDROBE[_key]['occupies'])|{'shoes'})
WARDROBE['female_fox_cosplay']['fact']='an opaque orange fox-themed dress with a clean plain orange front, white collar and hem trim, fox-ear headband and boots; any decorative tail is behind the body'

WARDROBE['male_latex_catsuit']=dict(name='Latex catsuit — male',ru='Латексный комбинезон — мужской',de='Latex-Catsuit — Herren',price=2000,slot='body',adult=True,gender='male',catalog_only=False,emoji='🖤',image='catalog_male_latex_catsuit',tags='skin tight glossy latex catsuit',fact='an opaque skin-tight glossy black latex full-length catsuit, fitted waist and limbs, reflective rubber highlights, black ankle boots',includes_footwear=True,occupies=['body','top','bottom','legs','outerwear','shoes'])
# Complete mannequin illustrations include their footwear; prevent a second pair.
for _key,_item in WARDROBE.items():
 if _item.get('slot')=='body':
  _item['includes_footwear']=True;_item['occupies']=sorted(set(_item['occupies'])|{'shoes'})

def body_preview(key,gender):
 suffix=key+'_male' if key in ('tracksuit','pajamas') and gender=='male' else key
 return '/assets/'+('nov23_'+key if key in ('police_male','police_female') else 'body_view_'+suffix)+'.webp'

def catalog_image(key,gender):
 if key in ('tracksuit','pajamas'):return body_preview(key,gender).split('/')[-1].removesuffix('.webp')
 return WARDROBE[key]['image']

def fitting_state(user):
 import fitting_looks
 gender='male' if user.get('gender')=='male' else 'female';current=active_outfit(user);body=current.get('body')
 complete=fitting_looks.matching(user,current)
 if complete:return dict(base=complete,layers=[])
 prepared=fitting_looks.best_base(user,current)
 consumed=set(prepared['slots']) if prepared else {'body'}
 base=prepared['image'] if prepared else body_preview(body,gender) if body else '/assets/nov23_starter_'+gender+'.webp'
 if not body and set(current.values())<= {'cotton_tshirt','denim_shorts','cap','collar','collar_leash'}:
  if current.get('bottom')=='denim_shorts' and not current.get('top'):base='/assets/nov23_denim_'+gender+'.webp';consumed.add('bottom')
  elif current.get('top')=='cotton_tshirt' and not current.get('bottom'):base='/assets/nov23_tshirt_'+gender+'.webp';consumed.add('top')
 order={'legs':0,'bottom':1,'top':2,'outerwear':4,'shoes':5,'neck':6,'head':7,'face':8,'ears':9,'wrist':10}
 layers=[dict(slot=slot,url='/assets/layer_v2_'+key+'.webp') for slot,key in sorted(current.items(),key=lambda pair:order.get(pair[0],0)) if slot not in consumed]
 target=FITTING_ANCHORS.get(base.split('/')[-1],{});reference=FITTING_ANCHORS.get('mannequin_base_'+gender+'.webp',{})
 for layer in layers:
  slot=layer['slot']
  if slot not in ('head','face','ears','neck','wrist'):continue
  head=slot in ('head','face','ears');origin=reference.get('top',17) if head else reference.get('neck',76)
  offset=(target.get('top',origin) if head else target.get('neck',origin))-origin
  scale=(target.get('head_width',36)/max(1,reference.get('head_width',36))) if head else target.get('body_scale',1)/max(.1,reference.get('body_scale',1))
  layer.update(offset_x=round((target.get('x',160)-reference.get('x',160))/320*100,3),offset_y=round(offset/512*100,3),scale=round(max(.7,min(1.25,scale)),3),origin_y=round(origin/512*100,3))
 return dict(base=base,layers=layers)
for _key in ('maid_outfit','nurse_outfit'):
 WARDROBE[_key]['occupies']=sorted(set(WARDROBE[_key]['occupies'])|{'head'})
WARDROBE['female_teacher']['occupies']=sorted(set(WARDROBE['female_teacher']['occupies'])|{'face'})

def occupancy_label(key,lang='ru'):
 item=WARDROBE[key]
 if item.get('slot')=='body':
  return {'ru':'Комплект с обувью','de':'Komplettes Outfit mit Schuhen'}.get(lang,'Complete outfit with shoes')
 return ''

# New names bypass caches containing the old contaminated atlas crops.
for _key,_item in WARDROBE.items():_item['image']='clean_catalog_'+_key

def migrate_materials(user):
 """Preserve previously bought glossy wet-look costumes as latex after the material split."""
 if user.get('wardrobe_material_version')==2:return False
 inventory=user.get('inventory') or {};active=user.get('active_outfit') or {};changed=False
 for old,new in (('female_wetlook_catsuit','latex_bodysuit'),('male_wetlook_catsuit','male_latex_catsuit')):
  if inventory.get(old):
   inventory[new]=max(1,inventory.get(new,0));changed=True
   if active.get('body')==old:active['body']=new;user['wardrobe_outfit']=new
 if changed:user['inventory']=inventory;user['active_outfit']=active
 user['wardrobe_material_version']=2
 return True
# Facts match the footwear and built-in accessories visible in the complete outfit art.
for _key,_shoes in {
 'male_leather_harness':'black boots','male_leather_bodysuit':'black boots','male_mesh_outfit':'black shoes','male_bdsm_outfit':'black boots',
 'female_corset_skirt':'black heeled shoes','female_harness_bodysuit':'black ankle boots','female_leather_outfit':'black ankle boots','female_mesh_dress':'black heeled shoes',
 'female_wetlook_catsuit':'black ankle boots','female_bodycon_jumpsuit':'black ankle boots','female_neckline_dress':'heeled shoes','female_strappy_lingerie':'black ankle boots',
 'female_teacher':'black heeled shoes','female_angel':'white shoes','female_devil':'black boots','female_onepiece_swimsuit':'blue sandals','female_bikini':'green sandals',
 'female_lace_bodystocking':'black heeled shoes','female_bandage_dress':'black heeled shoes','female_openback_dress':'red heeled shoes','male_wetlook_catsuit':'dark shoes','male_bodycon_jumpsuit':'black boots'
}.items():
 if not any(v in WARDROBE[_key]['fact'] for v in ('boots','shoes','sandals')):WARDROBE[_key]['fact']+=', with '+_shoes
WARDROBE['female_teacher']['fact']+=', with thin round glasses'
WARDROBE['nurse_outfit']['fact']+=', with a matching nurse cap'
WARDROBE['maid_outfit']['fact']+=', with a matching maid headpiece'
for _key in ('police_male','police_female'):WARDROBE[_key]['fact']+=', with a matching police cap'


# Nov 23: friendly labels, legacy species retained only for already saved characters.
HIDDEN_RACES=frozenset(('android','animatronic','dragonborn'))
RACES['robot']=('Робот','Robot','Roboter')
RACES['furry_dragon']=('Дракон','Dragon','Drache')
RACES['furry_fox']=('Фурри — лиса','Furry — fox','Furry — Fuchs')
RACES['furry_wolf']=('Фурри — волк','Furry — wolf','Furry — Wolf')
RACES['furry_cat']=('Фурри — кошка','Furry — cat','Furry — Katze')
RACE_FACTS['robot']='a fully mechanical adult humanoid robot with elegant sculpted metallic shell panels, a distinct robotic face, articulated metal limbs and illuminated optics'
TOYS_LEVEL=9
TOYS={
 'vibrator':('Вибратор','Vibrator','Vibrator','vibrator'),
 'anal_plug':('Анальная пробка','Anal plug','Analplug','plug'),
 'dildo':('Дилдо','Dildo','Dildo','dildo'),
 'padded_cuffs':('Мягкие наручники','Padded cuffs','Gepolsterte Handschellen','cuffs'),
 'ball_gag':('Кляп-шар','Ball gag','Ballknebel','gag'),
 'male_stroker':('Мужской мастурбатор','Male stroker','Masturbator','stroker'),
 'prostate_massager':('Массажёр простаты','Prostate massager','Prostatamassagegerät','massager'),
}
WARDROBE['vibrator'].update(group='toys',catalog_only=True,slot=None)
for _key,_labels in TOYS.items():
 if _key not in WARDROBE:
  WARDROBE[_key]=dict(ru=_labels[0],name=_labels[1],de=_labels[2],price=0,slot=None,adult=True,gender='unisex',catalog_only=True,group='toys',emoji='◇',image='toy_'+_labels[3],fact='')
WARDROBE['lace_panties']['fact']='opaque modest underwear shorts, replacing the lower base garment; covered by any selected outer clothing'
for _key in ('police_male','police_female'):
 WARDROBE[_key].update(ru='Латексная полицейская форма — '+('мужская' if _key.endswith('male') and not _key.endswith('female') else 'женская'),name='Latex police uniform',de='Latex-Polizeiuniform',fact='a completely opaque fitted glossy navy-black latex police jacket with long sleeves and matching full-length fitted trousers, a modest fashion harness over the jacket, matching police cap and black boots',image='nov23_'+_key)

def seed_starter_clothes(user):
 """One starter grant; existing paid inventory and selected clothes remain unchanged."""
 if user.get('starter_clothes_v1'):return False
 inventory=user.setdefault('inventory',{})
 for key in ('cotton_tshirt','cap'):inventory[key]=max(1,inventory.get(key,0))
 user['starter_clothes_v1']=True
 return True

OUTFIT_FACTS['lace_panties']=WARDROBE['lace_panties']['fact']

for _key in ('police_male','police_female'):OUTFIT_FACTS[_key]=WARDROBE[_key]['fact']
