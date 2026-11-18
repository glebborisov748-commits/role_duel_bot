import unittest,time
from unittest.mock import patch
import archaeology as a
class ArchaeologyTests(unittest.TestCase):
 def test_hidden_loot_and_no_client_reward(self):
  u={'bucks':10000};a.start(u);state=a.snapshot(u)
  self.assertEqual(len(state['run']['cells']),25);self.assertTrue(all(c['loot'] is None for c in state['run']['cells']))
  with self.assertRaises(a.DigError):a.action(u,{'action':'dig','id':'forged','cell':0,'reward':99999})
  self.assertEqual(u['bucks'],10000)
 def test_cashout_once_and_collection(self):
  u={};a.start(u);r=u['dig_run'];r['bag']=[{'key':'relic','name':'test','value':320,'condition':100}]
  body={'action':'cashout','id':r['id']};self.assertEqual(a.action(u,body),320);self.assertEqual(u['dig_collection']['relic'],1)
  with self.assertRaises(a.DigError):a.action(u,body)
  with self.assertRaises(a.DigError):a.start(u)
 def test_tools_damage_and_brush_preserves(self):
  for tool,condition in [('brush',100),('pick',40)]:
   u={};a.start(u);r=u['dig_run'];r['cells'][0]={'earth':1,'loot':3,'found':False}
   a.action(u,{'action':'dig','id':r['id'],'cell':0,'tool':tool});self.assertEqual(r['bag'][0]['condition'],condition)
   with self.assertRaises(a.DigError):a.action(u,{'action':'dig','id':r['id'],'cell':1,'tool':tool})
 def test_buy_tools_and_upgrade_validation(self):
  u={'bucks':500};a.action(u,{'action':'tool_upgrade'});self.assertEqual(u['bucks'],0);self.assertEqual(u['dig_tool_rank'],1)
  with self.assertRaises(a.DigError):a.action(u,{'action':'tool_upgrade'})
  a.start(u);r=u['dig_run']
  with self.assertRaises(a.DigError):a.action(u,{'action':'upgrade','id':r['id'],'upgrade':'luck'})
  r['choice']=list(a.UPGRADES);a.action(u,{'action':'upgrade','id':r['id'],'upgrade':'area'});self.assertEqual(r['depth'],2)
