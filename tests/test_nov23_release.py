import hashlib,random,unittest
from datetime import datetime,timedelta
from unittest.mock import patch
import deployment,profile_options as w,fandom_catalog
from test_core import load_functions,literal

class CalendarOfferTests(unittest.TestCase):
 def setUp(self):
  self.day=datetime(2026,11,23,13,0)
  self.ns=dict(local_today=lambda:self.day.date(),local_now=lambda:self.day,datetime=datetime,timedelta=timedelta,hashlib=hashlib,random=random,EXCHANGE_ROTATION=literal('EXCHANGE_ROTATION'),BUCKS_EXCHANGE=literal('BUCKS_EXCHANGE'),gt=lambda *a:'not_today',spend_bucks=lambda u,n:False)
  load_functions({'exchange_period','exchange_today','exchange_reset_seconds','exchange_ready_in','exchange_left','buy_exchange'},self.ns)
 def test_global_period_and_single_offer(self):
  n=self.ns;key=n['exchange_today']();u={};self.assertTrue(n['exchange_left'](u,key))
  for other in n['BUCKS_EXCHANGE']:
   if other!=key:self.assertFalse(n['exchange_left'](u,other));self.assertFalse(n['buy_exchange'](u,other)[0])
  u['exchange_period_bought']=n['exchange_period']();self.assertFalse(n['exchange_left'](u,key))
  self.assertGreater(n['exchange_ready_in'](u,key),0)
  self.day+=timedelta(days=2);self.assertTrue(n['exchange_left'](u,n['exchange_today']()))
 def test_calendar_reset_not_personal_cooldown(self):
  n=self.ns;u={'exchange_cooldowns':{k:datetime.now().isoformat() for k in n['BUCKS_EXCHANGE']}}
  self.assertEqual(n['exchange_ready_in'](u,n['exchange_today']()),0)
  self.assertLessEqual(n['exchange_reset_seconds'](),48*3600)
 def test_rotation_can_reach_every_product(self):
  seen=set()
  for d in range(200):self.day=datetime(2026,1,1)+timedelta(days=d*2);seen.add(self.ns['exchange_today']())
  self.assertEqual(seen,set(self.ns['BUCKS_EXCHANGE']))

 def test_strip_prompt_omits_move_symbols(self):
  ns={};load_functions({'play_round_facts'},ns)
  facts=ns['play_round_facts']({},dict(mode='strip',last={'mine':'rock','theirs':'scissors','outcome':'win'}))
  self.assertIn('одеждой',facts)
  for word in ('rock','scissors','камень','ножницы'):self.assertNotIn(word,facts)

class StagingTests(unittest.TestCase):
 def env(self):return dict(RD_DEPLOYMENT='staging',STAGING_BOT_TOKEN='test:token',BOT_TOKEN='production:token',STAGING_WEBAPP_URL='https://test.example.com',WEBAPP_URL='https://live.example.com',STAGING_DATA_DIR='/tmp/rd-unit-staging',DATA_DIR='/tmp/rd-production')
 def test_production_unchanged(self):
  e={'BOT_TOKEN':'production:token'};self.assertFalse(deployment.configure(e));self.assertEqual(e,{'BOT_TOKEN':'production:token'})
 def test_separate_secrets_and_storage(self):
  e=self.env();self.assertTrue(deployment.configure(e));self.assertEqual(e['BOT_TOKEN'],'test:token');self.assertEqual(e['DATA_DIR'],'/tmp/rd-unit-staging')
 def test_fail_closed_without_isolation(self):
  for key,value in [('STAGING_BOT_TOKEN',''),('STAGING_BOT_TOKEN','production:token'),('STAGING_WEBAPP_URL','https://live.example.com'),('STAGING_DATA_DIR','/tmp/rd-production')]:
   e=self.env();e[key]=value
   with self.subTest(key=key,value=value),self.assertRaises(ValueError):deployment.configure(e)

class WardrobeNov23Tests(unittest.TestCase):
 def test_starter_grant_once_and_no_auto_equip(self):
  u={'inventory':{'dress':1}};self.assertTrue(w.seed_starter_clothes(u));self.assertEqual(u['inventory'],{'dress':1,'cotton_tshirt':1,'cap':1});self.assertEqual(w.active_outfit(u),{});self.assertFalse(w.seed_starter_clothes(u))
 def test_base_clothing_replaced_by_slot(self):
  u={'gender':'female','inventory':{'denim_shorts':1,'cotton_tshirt':1}}
  self.assertIn('white tank top',w.clothing_facts(u,5));self.assertIn('white shorts',w.clothing_facts(u,5))
  w.equip(u,'denim_shorts',5);fact=w.clothing_facts(u,5);self.assertIn('white tank top',fact);self.assertNotIn('white shorts',fact)
  self.assertIn('nov23_denim_female',w.fitting_state(u)['base'])
  w.equip(u,'cotton_tshirt',5);self.assertNotIn('white tank top',w.clothing_facts(u,5));self.assertNotIn('white shorts',w.clothing_facts(u,5))
 def test_male_base_is_white_tshirt_and_shorts(self):
  fact=w.clothing_facts({'gender':'male'},1);self.assertIn('white shorts',fact);self.assertNotIn('tank top',fact);self.assertIn('white T-shirt',fact)
 def test_police_replaces_existing_keys(self):
  for g in ('female','male'):
   key='police_'+g;self.assertIn('latex',w.WARDROBE[key]['fact']);self.assertIn('nov23_police_',w.body_preview(key,g))
 def test_toys_no_photo_or_equip(self):
  self.assertEqual(w.TOYS_LEVEL,9)
  for k in w.TOYS:
   self.assertFalse(w.WARDROBE[k]['fact']);self.assertIsNone(w.WARDROBE[k]['slot'])
   with self.assertRaises(ValueError):w.equip({'inventory':{k:1}},k,10)
 def test_species_ui_hides_legacy_without_breaking_saved_values(self):
  keys={v['key'] for v in w.choices(w.RACES,'ru')};self.assertNotIn('android',keys);self.assertNotIn('animatronic',keys);self.assertNotIn('dragonborn',keys);self.assertEqual(w.validate_race('android'),'android')
 def test_pronouns_when_name_missing(self):
  self.assertEqual(fandom_catalog.character_name({'gender':'female'}),'Она');self.assertEqual(fandom_catalog.character_name({'gender':'male'}),'Он');self.assertEqual(fandom_catalog.character_name({'char_name':'Аля'}),'Аля')

class AdminNov23Tests(unittest.IsolatedAsyncioTestCase):
 async def test_staging_invoice_guard_blocks_before_telegram(self):
  from types import SimpleNamespace
  from unittest.mock import AsyncMock
  ns={'STAGING_MODE':True};load_functions({'staging_payment_guard'},ns);send=AsyncMock(return_value='ok')
  with self.assertRaises(RuntimeError):await ns['staging_payment_guard'](send,None,SimpleNamespace(__api_method__='createInvoiceLink'))
  send.assert_not_awaited();self.assertEqual(await ns['staging_payment_guard'](send,None,SimpleNamespace(__api_method__='getMe')),'ok')
 async def test_admin_help_is_role_specific(self):
  from types import SimpleNamespace
  from unittest.mock import AsyncMock
  ns={'MAIN_ADMIN_ID':7,'ADMIN_IDS':{7,8}};load_functions({'admin_help_cmd'},ns)
  for uid in (1,8,7):
   reply=AsyncMock();await ns['admin_help_cmd'](SimpleNamespace(from_user=SimpleNamespace(id=uid),answer=reply))
   if uid==1:reply.assert_not_awaited()
   else:self.assertEqual('/giveenergizers' in reply.call_args.args[0],uid==7)
