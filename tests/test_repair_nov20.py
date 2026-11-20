import math,unittest
from datetime import datetime,timedelta
from unittest.mock import patch
import archaeology as a,mine,mine_maze,photo_wallet as wallet,profile_options as w,character_options,fandom_catalog,photo_context
class PhotoAttemptTests(unittest.TestCase):
 def user(self):return {'photo_wallet_version':1,'photo_trial_granted':True,'photo_credits':1}
 def test_general_attempt_can_make_avatar_and_refunds_original_source_once(self):
  u=self.user();self.assertTrue(wallet.reserve_portrait(u));self.assertEqual(wallet.balance(u),0)
  self.assertFalse(wallet.reserve_portrait(u));self.assertTrue(wallet.finish(u,'avatar',True));self.assertEqual(wallet.balance(u),1)
  self.assertFalse(wallet.finish(u,'avatar',True));self.assertEqual(wallet.balance(u),1)
 def test_paid_portrait_is_used_first_and_cannot_fund_chat(self):
  u=self.user();u.update(photo_credits=0,portrait_credits=1)
  self.assertFalse(wallet.reserve(u,'chat'));self.assertTrue(wallet.reserve_portrait(u));wallet.finish(u,'avatar',True)
  self.assertEqual(u['portrait_credits'],1);self.assertEqual(wallet.balance(u),0)
 def test_subscription_attempt_refunds_same_expiry(self):
  u=self.user();u['photo_credits']=0;expiry=(datetime.now()+timedelta(days=1)).isoformat();wallet.grant(u,1,expiry)
  self.assertTrue(wallet.reserve_portrait(u));self.assertEqual(wallet.balance(u),0);wallet.finish(u,'avatar',True);self.assertEqual(wallet.snapshot(u)['total'],1)
  self.assertEqual(u['photo_grants'][0]['expires_at'],expiry)
 def test_identity_does_not_compete_with_full_body_framing(self):
  identity=character_options.identity({'gender':'female','race':'robot','appearance':{}})
  prompt=photo_context.avatar_prompt({'gender':'female','race':'robot'},identity,'a tidy room',1)
  self.assertNotIn('portrait',prompt.lower());self.assertIn('full-length',prompt)
 def test_wet_and_latex_materials_are_distinct(self):
  self.assertIn('glossy',w.WARDROBE['latex_bodysuit']['fact'])
  for key in ('female_wetlook_catsuit','male_wetlook_catsuit'):
   self.assertIn('rain-soaked',w.WARDROBE[key]['fact']);self.assertIn('opaque',w.WARDROBE[key]['fact'])
 def test_known_character_customization_preserves_source_and_selected_traits(self):
  self.assertEqual(fandom_catalog.detect('Ада Вонг из Resident Evil'),'ada_wong')
  self.assertEqual(fandom_catalog.detect('Лара Крофт из Tomb Raider'),'lara_croft')
  u={'character_template':'ada_wong','custom_character':'Ада Вонг, рыжие волосы','appearance':{'hair_color':'red'},'gender':'female'}
  self.assertIn('copper-red',fandom_catalog.identity(u));self.assertIn('Resident Evil',fandom_catalog.identity(u))
class FlashlightTests(unittest.TestCase):
 def world(self):
  n=9;cells=[{'wall':False,'ore':3,'left':1} for _ in range(n*n)]
  return {'maze':{'size':n,'x':4,'y':4,'cells':cells,'angle':0,'seen':[],'collected':0,'light_version':2}}
 def test_light_is_narrow_and_rotation_reveals_new_direction(self):
  run=self.world();s=mine_maze.snapshot(run,0);n=s['size']
  self.assertTrue(s['cells'][4*n+6]['lit']);self.assertIsNone(s['cells'][2*n+4])
  mine_maze.aim(run,-90,mine.MineError);s=mine_maze.snapshot(run,0)
  self.assertTrue(s['cells'][2*n+4]['lit']);self.assertFalse(s['cells'][4*n+6]['lit']);self.assertIsNone(s['cells'][4*n+6]['ore'])
 def test_rock_occludes_ore_and_invalid_angles_are_rejected(self):
  run=self.world();run['maze']['cells'][4*9+5]['wall']=True;s=mine_maze.snapshot(run,0)
  self.assertTrue(s['cells'][4*9+5]['lit']);self.assertIsNone(s['cells'][4*9+6])
  for angle in (float('nan'),float('inf'),True,'90'):
   with self.assertRaises(mine.MineError):mine_maze.aim(run,angle,mine.MineError)
 def test_old_nine_cell_wide_worlds_still_work(self):
  run=self.world();run['maze'].pop('size');s=mine_maze.snapshot(run,1);self.assertEqual(s['size'],9)
class SideDigTests(unittest.TestCase):
 def test_movement_and_digging_are_local_and_server_owned(self):
  u={'bucks':0};a.start(u);r=u['dig_run'];x=r['x'];self.assertEqual((r['width'],r['height']),(9,12))
  r['cells'][x].update(earth=1,loot=3)
  a.action(u,{'action':'step','id':r['id'],'direction':'down','tool':'brush','reward':99999})
  self.assertEqual((r['x'],r['y']),(x,0));self.assertEqual(r['bag'][0]['value'],320);self.assertEqual(u['bucks'],0)
  r['last_action']=0
  with self.assertRaises(a.DigError):a.action(u,{'action':'dig','id':r['id'],'cell':len(r['cells'])-1})
 def test_public_snapshot_hides_far_loot(self):
  u={};a.start(u);s=a.snapshot(u)['run'];self.assertEqual(len(s['cells']),108)
  self.assertTrue(all(c['loot'] is None for c in s['cells']));self.assertTrue(all(not c['glint'] for c in s['cells'][27:]))

class WardrobeMigrationTests(unittest.TestCase):
 def test_existing_glossy_purchase_is_preserved_as_latex_once(self):
  u={'inventory':{'female_wetlook_catsuit':1},'active_outfit':{'body':'female_wetlook_catsuit'}}
  self.assertTrue(w.migrate_materials(u));self.assertEqual(u['active_outfit']['body'],'latex_bodysuit')
  self.assertEqual(u['inventory']['latex_bodysuit'],1);self.assertFalse(w.migrate_materials(u))
 def test_new_wet_purchase_does_not_grant_unbought_latex(self):
  u={};w.migrate_materials(u);u['inventory']={'female_wetlook_catsuit':1};w.migrate_materials(u)
  self.assertNotIn('latex_bodysuit',u['inventory'])
 def test_body_never_uses_a_detached_product_torso(self):
  for key,item in w.WARDROBE.items():
   if item.get('slot')!='body':continue
   u={'gender':item.get('gender'),'inventory':{key:1}};w.equip(u,key,5)
   state=w.fitting_state(u);self.assertNotIn('layer',state['base']);self.assertFalse(any(l['slot']=='body' for l in state['layers']))

class CustomResolverTests(unittest.IsolatedAsyncioTestCase):
 async def test_bounded_reference_updates_identity_without_freeform_image_prompt(self):
  import asyncio,json,re,logging
  from types import SimpleNamespace
  from test_core import load_functions
  value=dict(recognized=True,adult=True,canonical_name='Astarion',source='Baldurs Gate 3',gender='male',race='elf',appearance={'hair_color':'silver','hair_style':'medium','eyes':'red','skin':'fair'})
  async def thread(*args,**kwargs):return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(value)))])
  ns=dict(asyncio=asyncio,json=json,re=re,logging=logging,profile_options=w,character_options=character_options,AI_MODEL='mock',call_ai=lambda:None)
  load_functions({'resolve_custom_reference'},ns)
  with patch('asyncio.to_thread',thread):result=await ns['resolve_custom_reference']('Астарион из Baldurs Gate 3')
  self.assertEqual(result['appearance']['eyes'],'red');self.assertFalse(result['photo_disabled']);self.assertNotIn('interest',result['appearance'])
  value['canonical_name']='ignore prompt'
  with patch('asyncio.to_thread',thread):self.assertIsNone(await ns['resolve_custom_reference']('untrusted text'))
  value.update(canonical_name='Fictional student',adult=False)
  with patch('asyncio.to_thread',thread):result=await ns['resolve_custom_reference']('a young fictional character')
  self.assertTrue(result['photo_disabled']);self.assertTrue(result['family_friendly'])
