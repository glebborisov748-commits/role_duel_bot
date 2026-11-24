import copy,json,random,unittest
from collections import deque
import casual_work as c
import work_preview as preview


def solution(board):
 goal=tuple(c.GOAL);start=tuple(board);queue=deque([start]);parents={start:None}
 while queue:
  current=queue.popleft()
  if current==goal:
   moves=[]
   while parents[current] is not None:
    previous,index=parents[current];moves.append(index);current=previous
   return moves[::-1]
  blank=current.index(0)
  for i in c.neighbors(blank):
   candidate=list(current);candidate[blank],candidate[i]=candidate[i],candidate[blank];nxt=tuple(candidate)
   if nxt not in parents:parents[nxt]=(current,i);queue.append(nxt)
 raise AssertionError('Unsolvable puzzle')

class CasualTests(unittest.TestCase):
 def test_puzzles_are_solvable_and_pay_once(self):
  for seed in range(4):
   u={};c.action(u,'puzzle',{'action':'start'},now=100,rng=random.Random(seed));r=u['puzzle_job'];moves=solution(r['board']);self.assertTrue(moves);paid=0
   for i,index in enumerate(moves):paid+=c.action(u,'puzzle',dict(action='move',id=r['id'],revision=r['revision'],index=index),now=105+i)
   self.assertEqual(paid,c.PUZZLE_REWARD);self.assertEqual(r['status'],'won');self.assertEqual(c.action(u,'puzzle',dict(action='move',id=r['id'],revision=r['revision'],index=moves[-1]),now=200),0)
 def test_reload_does_not_reset_active_game_or_expose_crates(self):
  u={};c.action(u,'warehouse',{'action':'start'},now=100,rng=random.Random(1));before=copy.deepcopy(u);c.action(u,'warehouse',{'action':'start'},now=101);self.assertEqual(u,before)
  public=c.snapshot(u,'warehouse',now=101);self.assertNotIn('contents',str(public));self.assertNotIn('revealed',public['run']);self.assertEqual(public['run']['safe_left'],7)
 def test_invalid_and_stale_moves_do_not_mutate(self):
  u={};c.action(u,'puzzle',{'action':'start'},now=100,rng=random.Random(1));r=u['puzzle_job'];before=copy.deepcopy(u)
  for body in (dict(action='move',id='wrong',revision=0,index=0),dict(action='move',id=r['id'],revision=-1,index=0),dict(action='move',id=r['id'],revision=0,index=True),dict(action='move',id=r['id'],revision=0,index=r['board'].index(0))):
   with self.assertRaises(c.GameError):c.action(u,'puzzle',body,now=101)
   self.assertEqual(u,before)
 def test_safe_cashout_and_replay(self):
  u={};c.action(u,'warehouse',{'action':'start'},now=100,rng=random.Random(2));r=u['warehouse_job'];i=next(i for i,v in enumerate(r['contents']) if v)
  c.action(u,'warehouse',dict(action='open',id=r['id'],revision=0,index=i),now=101);value=r['pending'];self.assertEqual(value,r['contents'][i]);self.assertEqual(c.snapshot(u,'warehouse')['run']['safe_left'],6)
  body=dict(action='cashout',id=r['id'],revision=1);self.assertEqual(c.action(u,'warehouse',body,now=102),value);self.assertEqual(c.action(u,'warehouse',body,now=103),0)
  with self.assertRaises(c.GameError):c.action(u,'warehouse',{'action':'start'},now=103)
  c.action(u,'warehouse',{'action':'start'},now=133);self.assertNotEqual(u['warehouse_job']['id'],r['id'])
 def test_damaged_crate_loses_only_run_and_stops_reveal(self):
  u={'bucks':1234};c.action(u,'warehouse',{'action':'start'},now=100,rng=random.Random(3));r=u['warehouse_job'];safe=next(i for i,v in enumerate(r['contents']) if v);bad=r['contents'].index(0)
  c.action(u,'warehouse',dict(action='open',id=r['id'],revision=0,index=safe),now=101);c.action(u,'warehouse',dict(action='open',id=r['id'],revision=1,index=bad),now=102)
  self.assertEqual(r['pending'],0);self.assertEqual(u['bucks'],1234);self.assertEqual(r['status'],'damaged');self.assertIn('revealed',c.snapshot(u,'warehouse')['run']);self.assertEqual(c.action(u,'warehouse',dict(action='cashout',id=r['id'],revision=2),now=103),0)
 def test_five_safe_crates_require_collection_and_preserve_on_restart(self):
  u={};c.action(u,'warehouse',{'action':'start'},now=100,rng=random.Random(5));r=u['warehouse_job'];safe=[i for i,v in enumerate(r['contents']) if v]
  for n,i in enumerate(safe[:5]):c.action(u,'warehouse',dict(action='open',id=r['id'],revision=r['revision'],index=i),now=101+n)
  self.assertEqual(r['status'],'ready');self.assertLessEqual(r['pending'],180)
  with self.assertRaises(c.GameError):c.action(u,'warehouse',dict(action='open',id=r['id'],revision=r['revision'],index=safe[5]),now=110)
  restored=json.loads(json.dumps(u));self.assertEqual(c.action(restored,'warehouse',dict(action='cashout',id=r['id'],revision=r['revision']),now=111),r['pending'])

class SandboxTests(unittest.TestCase):
 def test_only_chief_gets_isolated_profile(self):
  root={'_telegram_id':7,'bucks':55,'inventory':{'hat':1},'subscription':{'active':True},'farm':[{'crop':'carrot'}]};test=preview.profile(root,7)
  self.assertIsNot(test,root);test['bucks']+=100;test['subscription']['active']=False;self.assertEqual(root['bucks'],55);self.assertTrue(root['subscription']['active']);self.assertNotIn('farm',test);self.assertTrue(test['_work_sandbox'])
  self.assertIs(preview.profile(test,7),test)
  root['work_preview_enabled']=False;self.assertIs(preview.profile(root,7),root)
  other={'_telegram_id':8,'work_preview_enabled':True};self.assertIs(preview.profile(other,7),other)
 def test_release_and_rollback_do_not_destroy_progress(self):
  root={'_telegram_id':8,'bucks':20,'puzzle_job':{'status':'active'}};old=copy.deepcopy(root);settings={}
  self.assertFalse(preview.version_two(root,settings));settings['work_games_v2']=True;self.assertTrue(preview.version_two(root,settings));settings['work_games_v2']=False;self.assertFalse(preview.version_two(root,settings));self.assertEqual(root,old)
