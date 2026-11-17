import unittest,types,asyncio,json,os,tempfile,secrets,logging
from datetime import datetime,timedelta
from unittest.mock import AsyncMock,patch
import profile_options as wardrobe,character_options,photo_context,photo_generation,scene_photos
from test_core import load_functions

class OutfitTests(unittest.TestCase):
 def user(self):return {'inventory':{k:1 for k in wardrobe.WARDROBE},'preferences':{}}
 def test_combining_and_mutually_exclusive_slots(self):
  u=self.user()
  for key in ('dress','stockings','heels','hat'):wardrobe.equip(u,key,5)
  self.assertEqual(wardrobe.active_outfit(u),{'body':'dress','legs':'stockings','shoes':'heels','head':'hat'})
  prompt=wardrobe.clothing_facts(u,1)
  for word in ('dress','stockings','heeled shoes'):self.assertIn(word,prompt)
  wardrobe.equip(u,'shirt',5);self.assertNotIn('body',u['active_outfit'])
  wardrobe.equip(u,'trousers',5);self.assertEqual(u['active_outfit']['top'],'shirt')
  wardrobe.equip(u,'pajamas',5);self.assertNotIn('top',u['active_outfit']);self.assertNotIn('bottom',u['active_outfit'])
  wardrobe.equip(u,None,5,'shoes');self.assertNotIn('shoes',u['active_outfit'])
 def test_adult_gate_ownership_and_prompt_fallback(self):
  u=self.user()
  with self.assertRaises(ValueError):wardrobe.equip(u,'bunny_outfit',4)
  wardrobe.equip(u,'bunny_outfit',5)
  self.assertNotIn('rabbit',wardrobe.clothing_facts(u,4))
  self.assertIn('rabbit',wardrobe.clothing_facts(u,5))
  for level in (1,5,10):
   self.assertNotIn('explicit',wardrobe.clothing_facts(u,level));self.assertNotIn('nude',wardrobe.clothing_facts(u,level))
  with self.assertRaises(ValueError):wardrobe.equip(u,'vibrator',10)
  u['inventory'].pop('heels')
  with self.assertRaises(ValueError):wardrobe.equip(u,'heels',10)
  with self.assertRaises(ValueError):wardrobe.equip(u,[],10)
 def test_new_preferences_independent_and_strict(self):
  a=wardrobe.defaults();b=wardrobe.defaults();a['biting']=True
  self.assertFalse(b['biting']);self.assertEqual(len(b),8)
  with self.assertRaises(ValueError):wardrobe.validate_preferences({'biting':'yes'})
 def test_presets_are_facts_and_keep_red_hair(self):
  preset=next(p for p in character_options.creation_presets('ru','female') if p['key']=='red')
  self.assertNotIn('image',preset);self.assertEqual(preset['appearance']['hair_color'],'red')
  self.assertIn('copper-red ginger',character_options.identity(preset|{'gender':'female'}))
 def test_context_is_recent_dialogue_not_gift_or_photo_cards(self):
  u={'history':[{'role':'user','content':'Кафе'},{'role':'assistant','content':'Подарок','card':{}},{'role':'assistant','content':'📷','photo':'url'}]}
  self.assertEqual(photo_context.recent(u)[0]['text'],'Кафе')
  for level in (1,5,10):
   instruction=photo_context.instruction({},level,'red hair')
   self.assertIn('red hair',instruction);self.assertIn('most recent',instruction)
   self.assertIn('Do not depict sexual activity or nudity',instruction)
 def test_scene_realism_and_invalid_environment_fallback(self):
  prompt=scene_photos.portrait_prompt('red hair','female','not JSON',world='realism')
  self.assertIn('realistic photograph',prompt);self.assertNotIn('anime',prompt)
  self.assertIn('photo studio',prompt);self.assertNotIn('not JSON',prompt)

class PaidAvatarTests(unittest.IsolatedAsyncioTestCase):
 async def test_success_failure_cancellation_credit_and_stale_recovery(self):
  gen=AsyncMock(return_value=(b'\xff\xd8\xffmock','jpg'));now=datetime.now().isoformat()
  ns={'photo_generation':types.SimpleNamespace(generate=gen,error_code=photo_generation.error_code),'photo_context':photo_context,'photo_appearance':lambda u:'red hair',
      'get_intimacy_level':lambda u:1,'asyncio':asyncio,'datetime':datetime,'os':os,'secrets':secrets,'logging':logging,'user_data':{},'save_data':lambda d:None}
  load_functions({'generate_profile_avatar','avatar_unstick'},ns)
  user={'gender':'female','avatar_credits':0,'avatar_job':{'id':'a','started':now},'history':[]}
  with tempfile.TemporaryDirectory() as directory:
   ns['AVATAR_DIR']=directory
   await ns['generate_profile_avatar'](user,'a')
   self.assertTrue(user['avatar_generated']);self.assertEqual(user['avatar'],user['avatar_fullbody'])
   self.assertEqual(gen.await_count,1);self.assertEqual(user['avatar_credits'],0)
   user['avatar_job']={'id':'b','started':now};gen.side_effect=RuntimeError('failure')
   await ns['generate_profile_avatar'](user,'b');self.assertEqual(user['avatar_credits'],1)
   await ns['generate_profile_avatar'](user,'b');self.assertEqual(user['avatar_credits'],1)
   user['avatar_job']={'id':'c','started':now};gen.side_effect=asyncio.CancelledError()
   with self.assertRaises(asyncio.CancelledError):await ns['generate_profile_avatar'](user,'c')
   self.assertEqual(user['avatar_credits'],2)
   user['avatar_job']={'id':'d','started':(datetime.now()-timedelta(minutes=8)).isoformat()}
   ns['avatar_unstick'](user);ns['avatar_unstick'](user);self.assertEqual(user['avatar_credits'],3)
 async def test_no_credit_no_job_and_only_one_reserved(self):
  u={'avatar_credits':0};tasks=[]
  async def request(_):return 1,u,{},None
  def spawn(coro):tasks.append(coro)
  ns={'_play_request':request,'avatar_unstick':lambda u:None,'photo_generation':types.SimpleNamespace(token=lambda:'test'),'_app_reply':lambda u,ok=True,error=None:{'ok':ok},'at':lambda *a:'wait','secrets':secrets,'datetime':datetime,'asyncio':types.SimpleNamespace(create_task=spawn),'generate_profile_avatar':AsyncMock(),'save_data':lambda d:None,'user_data':{}}
  load_functions({'api_profile_avatar_generate_handler'},ns)
  self.assertFalse((await ns['api_profile_avatar_generate_handler'](None))['ok']);self.assertFalse(tasks)
  u['avatar_credits']=1;self.assertTrue((await ns['api_profile_avatar_generate_handler'](None))['ok'])
  self.assertEqual(u['avatar_credits'],0);self.assertEqual(len(tasks),1)
  self.assertFalse((await ns['api_profile_avatar_generate_handler'](None))['ok']);self.assertEqual(len(tasks),1)
  tasks[0].close()
