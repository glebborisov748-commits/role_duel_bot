import unittest,time
from datetime import date,timedelta
from unittest.mock import patch
import mine,work_rotation,daily_quests,profile_options as wardrobe
class RotationTests(unittest.TestCase):
 def test_three_shared_jobs_and_farm_always(self):
  day=date(2026,11,18)
  for offset in range(40):
   d=day+timedelta(days=offset);jobs=work_rotation.active(d)
   self.assertEqual(len(set(jobs)),3);self.assertNotIn('farm',jobs);self.assertTrue(work_rotation.is_open('farm',d))
   self.assertEqual(jobs,work_rotation.active(d))
  even=day if day.toordinal()%2==0 else day+timedelta(days=1)
  self.assertEqual(set(work_rotation.active(even))|set(work_rotation.active(even+timedelta(days=1))),set(work_rotation.JOBS))
 def test_quests_follow_schedule_and_keep_valid_progress(self):
  day=date(2026,11,18);u={'quest_seed':'fixed'}
  daily_quests.ensure(u,day.isoformat(),allowed_events=work_rotation.events(day))
  self.assertTrue(all(daily_quests.BY_ID[i['id']][1] in work_rotation.events(day) for i in u['daily_quests']['items']))
  u['daily_quests']={'day':day.isoformat(),'items':[{'id':'chat4','progress':3,'claimed':False},{'id':'courier10','progress':2,'claimed':False}]}
  daily_quests.ensure(u,day.isoformat(),allowed_events={'chat','share','mine'})
  self.assertIn({'id':'chat4','progress':3,'claimed':False},u['daily_quests']['items']);self.assertFalse(any(i['id']=='courier10' for i in u['daily_quests']['items']))
class MineTests(unittest.TestCase):
 def test_once_only_haul_and_client_amount_ignored(self):
  u={'bucks':1000};mine.start(u);run=u['mine_run'];run['bag']=[{'key':'gold','name':'Gold','value':220}]
  body={'action':'haul','id':run['id'],'amount':100000};self.assertEqual(mine.action(u,body),(220,1));self.assertEqual(u['bucks'],1000)
  with self.assertRaises(mine.MineError):mine.action(u,body)
  with self.assertRaises(mine.MineError):mine.start(u)
 def test_gas_collapse_and_tools_survive_restart(self):
  u={'mine_rank':2};mine.start(u);r=u['mine_run'];r['gas']=95;r['bag']=[{'key':'coal','name':'Coal','value':18}]*4
  mine.action(u,{'action':'strike','id':r['id'],'vein':0});self.assertTrue(r['closed']);self.assertTrue(r['collapsed']);self.assertEqual(len(r['bag']),2)
  import json
  copy=json.loads(json.dumps(u));self.assertEqual(mine.snapshot(copy)['run']['bag_value'],36);self.assertEqual(copy['mine_rank'],2)
 def test_vent_cooldown_route_choice_and_upgrade_price(self):
  u={'bucks':600};mine.action(u,{'action':'upgrade','price':0});self.assertEqual(u['bucks'],0);mine.start(u);r=u['mine_run']
  r['veins'][0].update(left=8,hardness=8);mine.action(u,{'action':'strike','id':r['id'],'vein':0})
  r['last']=0
  with self.assertRaises(mine.MineError):mine.action(u,{'action':'strike','id':r['id'],'vein':1})
  r['last']=0;mine.action(u,{'action':'vent','id':r['id']});self.assertLess(r['gas'],10)
  with self.assertRaises(mine.MineError):mine.action(u,{'action':'strike','id':r['id'],'vein':0})
class OccupancyTests(unittest.TestCase):
 def user(self):return {'inventory':{key:1 for key in wardrobe.WARDROBE}}
 def test_dress_only_head_shoes_jewelry_free(self):
  u=self.user();wardrobe.equip(u,'dress',5)
  self.assertEqual(set(wardrobe.SLOTS)-set(wardrobe.slot_locks(u))-{'body'},{'head','shoes','neck'})
  for key in ('hat','heels','scarf'):wardrobe.equip(u,key,5)
  for key in ('shirt','trousers','stockings','leather_jacket'):
   with self.assertRaises(ValueError):wardrobe.equip(u,key,5)
 def test_police_occupies_all_and_clears_old_layers(self):
  u=self.user()
  for key in ('shirt','trousers','heels','hat','scarf'):wardrobe.equip(u,key,5)
  wardrobe.equip(u,'police_male',5);self.assertEqual(wardrobe.active_outfit(u),{'body':'police_male'})
  self.assertEqual(set(wardrobe.slot_locks(u)),set(wardrobe.SLOTS)-{'body'})
  with self.assertRaises(ValueError):wardrobe.equip(u,'hat',5)
  wardrobe.equip(u,None,5,'body');self.assertEqual(wardrobe.slot_locks(u),{});wardrobe.equip(u,'hat',5)
 def test_legacy_conflicts_never_feed_generation_or_delete_inventory(self):
  u=self.user();u['active_outfit']={'body':'police_female','head':'hat','shoes':'heels','top':'shirt'}
  before=dict(u['inventory']);self.assertEqual(wardrobe.active_outfit(u),{'body':'police_female'});self.assertNotIn('heeled',wardrobe.clothing_facts(u,5));self.assertEqual(u['inventory'],before)

class WholeOutfitRulesTests(unittest.TestCase):
 def test_every_full_outfit_blocks_separate_upper_lower_and_stockings(self):
  for key,item in wardrobe.WARDROBE.items():
   if item['slot']!='body' or item.get('catalog_only'):continue
   with self.subTest(outfit=key):
    u={'inventory':{k:1 for k in wardrobe.WARDROBE}};wardrobe.equip(u,key,5)
    for other in ('shirt','trousers','stockings','garter_stockings','leather_jacket'):
     with self.assertRaises(ValueError):wardrobe.equip(u,other,5)
    wardrobe.equip(u,None,5,'body');wardrobe.equip(u,'stockings',5)
 def test_future_full_items_have_safe_default_even_without_metadata(self):
  from unittest.mock import patch
  item=dict(wardrobe.WARDROBE['pajamas'],ru='Юката',fact='an opaque yukata');item.pop('occupies',None)
  with patch.dict(wardrobe.WARDROBE,{'test_yukata':item}):
   self.assertTrue(wardrobe.FULL_OUTFIT_SLOTS<=wardrobe.occupied_slots('test_yukata'))
   u={'inventory':{'test_yukata':1,'stockings':1}};wardrobe.equip(u,'test_yukata',5)
   with self.assertRaises(ValueError):wardrobe.equip(u,'stockings',5)
 def test_built_in_accessories_reserve_their_slots(self):
  self.assertIn('head',wardrobe.occupied_slots('bunny_outfit'))
  for key in ('business_suit','stripper_outfit'):self.assertIn('neck',wardrobe.occupied_slots(key))
