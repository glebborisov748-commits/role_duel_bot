import unittest
from datetime import datetime,timedelta
from unittest.mock import patch
import premium_rules,photo_wallet,mine,mine_maze,archaeology,companion_initiative

class PremiumRuleTests(unittest.TestCase):
 def test_upgrade_preserves_term_and_prices_week_and_month_independently(self):
  now=datetime(2026,11,19,12)
  for term in (7,30):
   u={'subscription':{'active':True,'level':'pro','term_days':term,'expires_at':(now+timedelta(days=term)).isoformat()}}
   q=premium_rules.upgrade(u,now);self.assertEqual(q['stars'],125 if term==7 else 375);self.assertEqual(q['expires_at'],u['subscription']['expires_at'])
   u['subscription']['level']='super_pro';self.assertEqual(premium_rules.upgrade(u,now)['target'],'elite')
   u['subscription']['level']='elite';self.assertIsNone(premium_rules.upgrade(u,now))
 def test_long_existing_term_is_not_upgraded_at_a_single_month_price(self):
  now=datetime(2026,11,19);u={'subscription':{'active':True,'level':'pro','term_days':30,'expires_at':(now+timedelta(days=60)).isoformat()}}
  self.assertEqual(premium_rules.upgrade(u,now)['stars'],750)
 def test_photo_packs_discount_volume_and_keep_old_receipts(self):
  self.assertEqual([x[0] for x in photo_wallet.PACKS.values()],[3,8,20])
  ratios=[price/n for n,price in photo_wallet.PACKS.values()]
  self.assertGreater(ratios[0],ratios[1]);self.assertGreater(ratios[1],ratios[2])
  self.assertEqual(photo_wallet.ALL_PACKS['photo_1'],(1,10))
 def test_portrait_credit_cannot_be_used_as_a_chat_photo(self):
  u={};photo_wallet.ensure(u);u['photo_credits']=0;u['portrait_credits']=1
  self.assertFalse(photo_wallet.reserve(u,'chat'))
  self.assertTrue(photo_wallet.reserve_portrait(u));self.assertFalse(photo_wallet.reserve_portrait(u))
  self.assertEqual(u['portrait_credits'],0);photo_wallet.finish(u,'avatar',True)
  self.assertEqual(u['portrait_credits'],1);self.assertEqual(photo_wallet.balance(u),0)
 def test_only_active_elite_can_disable_initiative(self):
  u={'history':[{'role':'user','content':'Привет'}],'last_activity':(datetime.now()-timedelta(hours=7)).isoformat(),'initiative_enabled':False,'notifications_muted':True}
  local=datetime.now().replace(hour=12)
  for tier in ('pro','super_pro',None):
   u['subscription']={'active':True,'level':tier,'expires_at':(datetime.now()+timedelta(days=1)).isoformat()}
   self.assertTrue(companion_initiative.due(u,local))
  u['subscription']['level']='elite';self.assertFalse(companion_initiative.due(u,local))

class NewWorkTests(unittest.TestCase):
 def test_maze_is_connected_and_public_snapshot_hides_undiscovered_ore(self):
  u={};mine.start(u);m=u['mine_run']['maze'];size=mine_maze.SIZE;queue=[(1,1)];seen=set(queue)
  for x,y in queue:
   for dx,dy in mine_maze.DIRECTIONS.values():
    nx,ny=x+dx,y+dy
    if 0<=nx<size and 0<=ny<size and not m['cells'][ny*size+nx]['wall'] and (nx,ny) not in seen:seen.add((nx,ny));queue.append((nx,ny))
  self.assertIn((size-2,size-2),seen)
  public=mine.snapshot(u)['run']['maze'];self.assertTrue(any(c is None for c in public['cells']))
  self.assertTrue(all('ore' not in c or c['ore'] is None for c in public['cells'] if c and not c['lit']))
 def test_maze_mining_and_haul_are_server_owned_and_once_only(self):
  u={};mine.start(u);run=u['mine_run'];cell=run['maze']['cells'][mine_maze.SIZE+1];cell.update(ore=3,left=1)
  with patch.object(mine.time,'time',return_value=100):mine.action(u,{'action':'excavate','id':run['id']})
  self.assertEqual(run['bag'][0]['key'],'gold');self.assertIsNone(cell['ore'])
  with patch.object(mine.time,'time',return_value=101):
   with self.assertRaises(mine.MineError):mine.action(u,{'action':'excavate','id':run['id']})
  amount,count=mine.action(u,{'action':'haul','id':run['id']});self.assertEqual((amount,count),(220,1))
  with self.assertRaises(mine.MineError):mine.action(u,{'action':'haul','id':run['id']})
 def test_archaeology_requires_removing_top_soil(self):
  u={};archaeology.start(u);run=u['dig_run']
  with self.assertRaises(archaeology.DigError):archaeology.action(u,{'action':'dig','id':run['id'],'cell':24})
  self.assertEqual(run['actions'],0)
