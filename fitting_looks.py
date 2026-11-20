"""Whole generated looks: clothes and accessories drawn together, no runtime image cost."""
# Rows correspond exactly to the exported 4x4 atlases.
FEMALE=[
 {'body':'dress','head':'cat_ears_headband','neck':'pendant'},
 {'body':'dress','head':'beret','neck':'scarf'},
 {'body':'dress','face':'sunglasses','neck':'pendant'},
 {'body':'dress','head':'beanie','neck':'pendant'},
 {'body':'latex_bodysuit','head':'cat_ears_headband','neck':'pendant'},
 {'body':'latex_bodysuit','head':'beret'},
 {'body':'tracksuit','head':'beanie','neck':'pendant'},
 {'body':'pajamas','neck':'pendant'},
 {'body':'maid_outfit','head':'cat_ears_headband'},
 {'body':'nurse_outfit','neck':'pendant'},
 {'body':'qipao','neck':'pendant'},
 {'body':'bunny_outfit'},
 {'top':'cotton_tshirt','bottom':'denim_jeans','shoes':'sneakers','head':'beanie','neck':'pendant'},
 {'top':'knit_sweater','bottom':'pleated_skirt','shoes':'ankle_boots','head':'beret','neck':'pendant'},
 {'top':'hoodie','bottom':'denim_jeans','shoes':'sneakers','head':'cat_ears_headband'},
 {'top':'linen_shirt','bottom':'chino_trousers','shoes':'sneakers','face':'sunglasses','neck':'pendant'},
]
MALE=[
 {'body':'business_suit','face':'sunglasses'},
 {'body':'business_suit'}, # tie already occupies neck; scarf shown as outer lapel detail
 {'body':'casual_outfit','head':'beanie'},
 {'body':'casual_outfit','face':'sunglasses','neck':'pendant'},
 {'outerwear':'leather_jacket','top':'cotton_tshirt','bottom':'trousers','shoes':'ankle_boots','neck':'pendant'},
 {'outerwear':'leather_jacket','top':'cotton_tshirt','bottom':'trousers','shoes':'ankle_boots','head':'beanie'},
 {'body':'tracksuit','head':'beanie'},
 {'body':'tracksuit','neck':'pendant','face':'sunglasses'},
 {'body':'stripper_outfit'},
 {'body':'police_male'},
 {'body':'male_wetlook_catsuit','shoes':'ankle_boots','neck':'pendant'},
 {'body':'male_bodycon_jumpsuit','shoes':'ankle_boots','face':'sunglasses'},
 {'body':'male_bdsm_outfit','shoes':'ankle_boots'},
 {'body':'male_mesh_outfit','shoes':'ankle_boots'},
 {'body':'male_fox_cosplay'},
 {'outerwear':'male_satin_robe','top':'shirt','bottom':'trousers'},
]
EXTRA=[
 {'body':'female_corset_skirt','shoes':'heels','neck':'pendant'},
 {'body':'female_harness_bodysuit','shoes':'ankle_boots','neck':'collar_leash'},
 {'body':'female_leather_outfit','shoes':'ankle_boots','face':'sunglasses'},
 {'body':'female_mesh_dress','shoes':'heels','neck':'pendant'},
 {'body':'female_wetlook_catsuit','shoes':'ankle_boots','neck':'pendant'},
 {'body':'female_bodycon_jumpsuit','shoes':'ankle_boots','neck':'pendant'},
 {'top':'shirt','bottom':'female_leather_miniskirt','legs':'female_ribbed_tights_black','shoes':'ankle_boots'},
 {'top':'shirt','bottom':'female_pleated_miniskirt','legs':'female_ribbed_tights_cream','shoes':'ankle_boots'},
 {'body':'female_neckline_dress','shoes':'heels','neck':'pendant'},
 {'body':'female_fox_cosplay'},
 {'outerwear':'female_satin_robe','top':'shirt','bottom':'trousers','neck':'pendant'},
 {'outerwear':'female_kimono_robe','top':'shirt','bottom':'trousers','neck':'pendant'},
 {'body':'female_stewardess'},
 {'body':'female_teacher','shoes':'heels','face':'round_glasses','neck':'pendant'},
 {'body':'female_angel','shoes':'heels'},
 {'body':'female_devil','shoes':'ankle_boots'},
]
LOOKS={}
for group,gender,rows in (('female','female',FEMALE),('male','male',MALE),('extra','female',EXTRA)):
 for i,slots in enumerate(rows):LOOKS[group+'_'+str(i)]=dict(gender=gender,slots=slots,image='/assets/complete_'+group+'_'+str(i)+'.webp')
LOOKS.pop('male_1') # scarf would conflict with the suit's built-in tie

def matching(user,current):
 # Only use complete art when every depicted selection actually matches the equipped items.
 for key,look in LOOKS.items():
  if user.get('gender','female')==look['gender'] and current==look['slots']:return look['image']
 return None

def choices(user,lang='ru',level=0):
 import profile_options as w
 result=[]
 for key,look in LOOKS.items():
  if look['gender']!=user.get('gender','female'):continue
  values=[w.WARDROBE[k] for k in look['slots'].values()]
  if any(i['adult'] for i in values) and (level<5 or __import__('fandom_catalog').family_friendly(user)):continue
  label=' + '.join(i.get(lang,i['name']) for i in values)
  result.append(dict(key=key,image=look['image'],label=label,owned=all((user.get('inventory') or {}).get(k) for k in look['slots'].values()),adult=any(i['adult'] for i in values)))
 return result

def equip(user,key,level):
 import profile_options as w
 if not isinstance(key,str) or key not in LOOKS:raise ValueError('Неизвестный комплект')
 look=LOOKS[key]
 if look['gender']!=user.get('gender','female'):raise ValueError('Комплект для другого пола персонажа')
 trial={**user,'active_outfit':{}}
 for slot,item in look['slots'].items():w.equip(trial,item,level,slot)
 user['active_outfit']=trial['active_outfit'];user['wardrobe_outfit']=trial.get('wardrobe_outfit')
 return user['active_outfit']

# Every full outfit has a whole-body illustration, even before adding accessories.
import profile_options as _wardrobe
for _look in LOOKS.values():
 if 'body' in _look['slots']:
  _look['slots'].pop('shoes',None)
  if len(_look['slots'])==1:_look['image']=_wardrobe.body_preview(_look['slots']['body'],_look['gender'])
for _key,_item in _wardrobe.WARDROBE.items():
 if _item.get('slot')!='body':continue
 for _gender in ('male','female'):
  if _item.get('gender','unisex') not in ('unisex',_gender):continue
  LOOKS['body_'+_gender+'_'+_key]=dict(gender=_gender,slots={'body':_key},image=_wardrobe.body_preview(_key,_gender))

# A prepared look must obey the same occupancy rules as manual selection.
for _key,_look in list(LOOKS.items()):
 _test={'gender':_look['gender'],'inventory':{item:1 for item in _look['slots'].values()}}
 try:
  for _slot,_item in _look['slots'].items():_wardrobe.equip(_test,_item,5,_slot)
 except ValueError:LOOKS.pop(_key);continue
 if '/complete_' in _look['image']:_look['image']=_look['image'].replace('/complete_','/complete_clean_')
# Old glossy ready combinations now belong to latex, not rain-soaked fabric.
for _key,_look in LOOKS.items():
 _body=_look['slots'].get('body')
 if not _key.startswith('body_') and _body in ('female_wetlook_catsuit','male_wetlook_catsuit'):
  _look['slots']['body']='latex_bodysuit' if _body.startswith('female') else 'male_latex_catsuit'
for _key,_gender,_slots in (
 ('mix_tshirt','female',{'top':'cotton_tshirt','bottom':'denim_jeans','shoes':'sneakers'}),
 ('mix_hoodie','female',{'top':'hoodie','bottom':'denim_jeans','shoes':'sneakers'}),
 ('mix_linen','male',{'top':'linen_shirt','bottom':'chino_trousers','shoes':'sneakers'}),
 ('mix_bomber','male',{'outerwear':'bomber_jacket','top':'cotton_tshirt','bottom':'denim_jeans','shoes':'sneakers'})
):LOOKS[_key]=dict(gender=_gender,slots=_slots,image='/assets/body_view_'+_key+'.webp')

def best_base(user,current):
 """Reuse a coherent clothing render when only extra accessories differ."""
 main={'body','top','bottom','legs','outerwear','shoes'};selected_main={k:v for k,v in current.items() if k in main};candidates=[]
 for look in LOOKS.values():
  if look['gender']!=user.get('gender','female'):continue
  if {k:v for k,v in look['slots'].items() if k in main}!=selected_main:continue
  if not all(current.get(k)==v for k,v in look['slots'].items()):continue
  candidates.append(look)
 return max(candidates,key=lambda v:len(v['slots'])) if candidates else None
