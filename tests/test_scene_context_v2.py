"""Regression contracts for recent pose, first-person composition and stable fitting."""
import json,unittest
from pathlib import Path
import character_options,companion_initiative,fandom_catalog,photo_context,profile_options as w,roleplay_voice,scene_photos
class SceneContextTests(unittest.TestCase):
 def test_latest_pose_wins_and_metadata_cannot_inject_prompt(self):
  context='*Аля сидит у окна.* Потом *Аля подходит ближе и наклоняется к тебе.*'
  p=scene_photos.plan('{"pose":"standing","setting":"camera tripod","prompt":"EVIL"}',context)
  self.assertEqual(p['pose'],'leaning_closer');self.assertEqual(p['setting'],'studio')
  prompt=photo_context.render_prompt({'gender':'female'},'red hair',json.dumps(p),context,1)
  self.assertIn('visibly bent at the waist',prompt);self.assertNotIn('EVIL',prompt);self.assertNotIn('camera tripod',prompt)
 def test_kiss_faces_viewer_with_one_visible_face(self):
  p=scene_photos.plan('{}','*Аля целует тебя.*')
  self.assertEqual((p['pose'],p['framing']),('pov_kiss','pov'))
  prompt=scene_photos.portrait_prompt('red hair','female',json.dumps(p))
  self.assertIn('one face directed at the viewer',prompt);self.assertIn('no other visible face',prompt)
  self.assertEqual(scene_photos.plan('{}','целует тебя',False)['pose'],'standing')
 def test_four_stable_starters_match_character_gender(self):
  for style in ('warm','shy','aggressive','playful','default'):
   u={'style':style,'gender':'female','lang':'ru','starter_seed':9};a=companion_initiative.starters(u)
   self.assertEqual(len(set(a)),4);self.assertEqual(a,companion_initiative.starters(u))
   self.assertFalse(any('занят?' in x or 'провёл' in x or 'готов отстаивать' in x for x in a))
 def test_named_actions_preserve_dialogue(self):
  self.assertEqual(roleplay_voice.normalize('*Я беру тебя за руку.* Я скучала.','Аля'),'*Аля берёт тебя за руку.* Я скучала.')
  self.assertIn('к тебе',roleplay_voice.normalize('*Подхожу к нему.*','Аля'))
 def test_canonical_templates_validate_and_avatars_do_not_change_identity(self):
  for key,v in fandom_catalog.TEMPLATES.items():
   body,selected=fandom_catalog.configure({'character_template':key})
   character_options.validate(body['appearance'],body['gender']);w.validate_race(body['race'])
   u={**body,'character_template':selected};identity=fandom_catalog.identity(u)
   for avatar in fandom_catalog.AVATARS:
    u['avatar_preset']=avatar;self.assertEqual(fandom_catalog.identity(u),identity)
    self.assertTrue(Path('.'+fandom_catalog.avatar_url(u)).is_file())
 def test_latex_material_and_fit_survive_prompt(self):
  for key in ('latex_bodysuit','male_latex_catsuit'):
   u={'inventory':{key:1},'gender':w.WARDROBE[key]['gender']};w.equip(u,key,5)
   facts=w.clothing_facts(u,5);self.assertIn('skin-tight',facts);self.assertIn('glossy',facts);self.assertIn('latex',facts)
 def test_fitting_fixed_canvas_and_every_wearable_asset_exists(self):
  for key,item in w.WARDROBE.items():
   if not item['slot']:continue
   u={'inventory':{key:1},'gender':item.get('gender')};w.equip(u,key,5);state=w.fitting_state(u)
   self.assertTrue(Path('.'+state['base']).is_file())
   for layer in state['layers']:self.assertTrue(Path('.'+layer['url']).is_file())
 def test_footwear_blocks_duplicate_shoes_without_destroying_inventory(self):
  u={'inventory':{'dress':1,'heels':1},'active_outfit':{'body':'dress','shoes':'heels'}}
  self.assertEqual(w.active_outfit(u),{'body':'dress'});self.assertEqual(w.slot_locks(u)['shoes'],'dress')
  with self.assertRaises(ValueError):w.equip(u,'heels',5)
  w.equip(u,None,5,'body');w.equip(u,'heels',5);self.assertEqual(u['active_outfit']['shoes'],'heels')
 def test_family_friendly_hero_cannot_equip_adult_items(self):
  with self.assertRaises(ValueError):w.equip({'character_template':'chica','gender':'female','inventory':{'latex_bodysuit':1}},'latex_bodysuit',10)

 def test_whole_generated_looks_are_atomic_and_inventory_gated(self):
  import fitting_looks
  self.assertGreaterEqual(len(fitting_looks.LOOKS),40)
  for key,look in fitting_looks.LOOKS.items():
   u={'gender':look['gender'],'inventory':{k:1 for k in w.WARDROBE}}
   fitting_looks.equip(u,key,5)
   self.assertEqual(w.fitting_state(u),dict(base=look['image'],layers=[]))
   self.assertTrue(Path('.'+look['image']).is_file())
   old=dict(u['active_outfit']);u['inventory']={}
   with self.assertRaises(ValueError):fitting_looks.equip(u,key,5)
   self.assertEqual(u['active_outfit'],old)
