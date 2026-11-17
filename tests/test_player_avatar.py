import asyncio,unittest,json,tempfile,os,secrets,logging
from datetime import datetime
from unittest.mock import patch,AsyncMock
from types import SimpleNamespace
import player_avatar,photo_generation,character_options
from test_core import load_functions

class PlayerAvatarTests(unittest.TestCase):
 def test_validation_distinguishes_player_from_companion(self):
  value=player_avatar.validate({'gender':'male','world':'anime','name':'Me','race':'elf','appearance':{'hair_color':'silver'}})
  self.assertEqual(value['appearance']['hair_style'],'short')
  self.assertNotIn('interest',value['appearance'])
  self.assertIn('adult man',player_avatar.facts(value));self.assertIn('silver',player_avatar.facts(value))
  for body in ({'gender':'child','world':'anime'},{'gender':'male','world':'x'},{'gender':'female','world':'anime','race':[]},{'gender':'male','world':'anime','name':['x']}):
   with self.assertRaises(ValueError):player_avatar.validate(body)
 def test_selfie_preserves_visible_features_instead_of_defaults(self):
  photo={'gender':'female','appearance':{'hair_color':'brown'},'avatar':'abc.jpg'}
  self.assertIn('exact visible face',player_avatar.facts(photo))
  self.assertNotIn('brown hair',player_avatar.facts(photo))
  photo['use_photo_appearance']=False
  self.assertIn('brown',player_avatar.facts(photo))
 def test_pair_prompt_never_inherits_solo_or_opposite_gender_negatives(self):
  man={'gender':'male','appearance':{'hair_color':'silver'},'race':'human'}
  woman={'gender':'female','world':'anime','appearance':{'hair_color':'black'},'race':'human'}
  prompt=player_avatar.couple_prompt(man,woman,'a gentle mutual kiss')
  self.assertIn('EXACTLY TWO',prompt);self.assertIn('Reference image 1 is the PLAYER',prompt);self.assertIn('Reference image 2 is the COMPANION',prompt)
  self.assertIn('adult man',prompt);self.assertIn('adult woman',prompt);self.assertNotIn('solo',prompt)
  self.assertIn('Keep clothes on',prompt)

class AvatarEndpointTests(unittest.IsolatedAsyncioTestCase):
 async def test_initial_creation_free_subsequent_changes_require_super(self):
  user={};body={'gender':'male','world':'anime','appearance':{},'race':'human'}
  async def request(_):return 1,user,body,None
  ns={'_app_request':request,'get_subscription_level':lambda u:u.get('tier'),'_app_reply':lambda u,ok=True,error=None:{'ok':ok,'error':error},'player_avatar':player_avatar,'save_data':lambda d:None,'user_data':{},'at':lambda *a:'wait'}
  load_functions({'api_player_avatar_handler'},ns)
  self.assertTrue((await ns['api_player_avatar_handler'](None))['ok'])
  old=json.dumps(user)
  body['appearance']={'hair_color':'red'}
  self.assertFalse((await ns['api_player_avatar_handler'](None))['ok']);self.assertEqual(json.dumps(user),old)
  user['tier']='pro';self.assertFalse((await ns['api_player_avatar_handler'](None))['ok'])
  user['tier']='super_pro';self.assertTrue((await ns['api_player_avatar_handler'](None))['ok'])
  self.assertEqual(user['player_avatar']['appearance']['hair_color'],'red')
 async def test_companion_edit_and_legacy_route_cannot_bypass_gate(self):
  user={'tier':'pro','appearance':{'hair_color':'black'}}
  async def request(_):return 1,user,{},None
  ns={'_play_request':request,'get_subscription_level':lambda u:u['tier'],'_app_reply':lambda u,ok=True,error=None:{'ok':ok},'character_options':character_options}
  load_functions({'api_app_appearance_handler','api_app_look_handler'},ns)
  for name in ('api_app_appearance_handler','api_app_look_handler'):
   self.assertFalse((await ns[name](None))['ok']);self.assertEqual(user['appearance'],{'hair_color':'black'})
 async def test_upload_requires_consent_and_does_not_generate(self):
  user={};body={'gender':'male','world':'anime','appearance':{},'image':'data:image/jpeg;base64,xyz'}
  async def request(_):return 1,user,body,None
  store=unittest.mock.Mock(return_value=None)
  ns={'_app_request':request,'get_subscription_level':lambda u:None,'_app_reply':lambda u,ok=True,error=None:{'ok':ok},'player_avatar':player_avatar,'save_avatar':store,'save_data':lambda d:None,'user_data':{}}
  load_functions({'api_player_avatar_handler'},ns)
  self.assertFalse((await ns['api_player_avatar_handler'](None))['ok']);store.assert_not_called()
 async def test_pair_uses_one_job_no_hidden_portraits_and_refunds_failure(self):
  user={'energy':150,'world':'anime','gender':'female','appearance':{},'player_avatar':{'gender':'male','world':'anime','appearance':{}},'history':[],'photo_pending':True}
  images=AsyncMock(return_value=(b'\xff\xd8\xfftest','jpg'));gen=AsyncMock(side_effect=AssertionError('No hidden image-gen jobs'))
  ns={'asyncio':asyncio,'datetime':datetime,'WEBAPP_URL':'https://bot.example','PHOTO_ENERGY_COST':40,'ENERGY_MAX':150,'save_data':lambda d:None,'user_data':{},'character_options':character_options,'player_avatar':player_avatar,'photo_generation':SimpleNamespace(edit=images,generate=gen),'os':os,'secrets':secrets,'logging':logging}
  load_functions({'identity_source_url','ensure_identity_reference','app_couple_photo_generate'},ns)
  with tempfile.TemporaryDirectory() as directory:
   ns['AVATAR_DIR']=os.path.join(directory,'not-created-yet')
   await ns['app_couple_photo_generate'](1,user,'a gentle hug')
   self.assertEqual(user['energy'],110);self.assertEqual(images.await_count,1);gen.assert_not_called()
   refs=images.call_args.args[1];self.assertEqual(len(refs),2);self.assertNotEqual(refs[0],refs[1]);self.assertTrue(all(r.startswith('https://bot.example/assets/') for r in refs))
   images.side_effect=RuntimeError('provider failed');user['photo_pending']=True
   await ns['app_couple_photo_generate'](1,user,'a gentle kiss')
   self.assertEqual(user['energy'],110);self.assertNotIn('photo_pending',user);self.assertNotIn('photo_reserved',user)
   user['energy']=40;images.side_effect=None
   await ns['app_couple_photo_generate'](1,user,'a gentle hug')
   self.assertEqual(user['energy'],0);self.assertTrue(user['sleep_until'])
   user['energy']=100;images.side_effect=asyncio.CancelledError()
   with self.assertRaises(asyncio.CancelledError):await ns['app_couple_photo_generate'](1,user,'a gentle hug')
   self.assertEqual(user['energy'],100);self.assertNotIn('photo_reserved',user)

class PairProviderTests(unittest.IsolatedAsyncioTestCase):
 async def test_edit_contract_preserves_order_and_never_injects_solo(self):
  import httpx
  calls=[]
  async def handler(request):
   calls.append(request)
   if request.method=='POST':return httpx.Response(200,json={'taskId':'test'})
   if '/tasks/' in str(request.url):return httpx.Response(200,json={'ready':True,'status':'END_SUCCESS','result':{'taskResult':[{'url':'https://result.example/photo'}]}})
   return httpx.Response(200,content=b'\xff\xd8\xffresult')
  original=httpx.AsyncClient
  async def no_sleep(*a):pass
  refs=['https://bot.example/avatars/player.jpg','https://bot.example/avatars/companion.jpg']
  with patch.object(photo_generation,'token',return_value='test'),patch.object(photo_generation.httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(handler),**kw)),patch.object(photo_generation.asyncio,'sleep',no_sleep):
   raw,ext=await photo_generation.edit('Two clothed adults hugging',refs)
  payload=json.loads(calls[0].content)
  self.assertTrue(str(calls[0].url).endswith('/image-edit/tasks'));self.assertEqual(payload['sourceImageFileIds'],refs)
  self.assertEqual(payload['imageCount'],1);self.assertNotIn('negativePrompt',payload);self.assertNotIn('style',payload)
  self.assertNotIn('authorization',calls[-1].headers);self.assertEqual(ext,'jpg')
