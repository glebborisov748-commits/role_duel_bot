"""Support ordering, persistence and delivery regressions without live Telegram."""
import copy,json,logging,unittest
from unittest.mock import patch,AsyncMock
from types import SimpleNamespace
from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton
import support_queue as q
from test_core import load_functions

class QueueTests(unittest.TestCase):
 def test_priority_fifo_and_merge(self):
  s={}
  with patch('support_queue.time.time',return_value=100):a=q.submit(s,1,'first')
  with patch('support_queue.time.time',return_value=101):b=q.submit(s,2,'subscriber',True)
  with patch('support_queue.time.time',return_value=102):c=q.submit(s,3,'subscriber2',True);again=q.submit(s,1,'more')
  with patch('support_queue.time.time',return_value=103):
   self.assertIs(a,again);self.assertEqual(len(q.active(s)),3);self.assertEqual([t['id'] for t in q.active(s)],[b['id'],c['id'],a['id']]);self.assertEqual(a['messages'],['first','more']);self.assertEqual(q.snapshot(s,1)['position'],3)
 def test_old_free_ticket_does_not_starve(self):
  s={}
  with patch('support_queue.time.time',return_value=100):a=q.submit(s,1,'old')
  with patch('support_queue.time.time',return_value=90000):
   q.submit(s,2,'new',True);self.assertEqual(q.active(s)[0],a)
 def test_claim_owner_fifo_resolution(self):
  s={};a=q.submit(s,1,'a');b=q.submit(s,2,'b')
  self.assertFalse(q.claim(s,b['id'],5));self.assertTrue(q.claim(s,a['id'],5));self.assertFalse(q.claim(s,a['id'],6));self.assertFalse(q.resolve(s,a['id'],6));self.assertTrue(q.resolve(s,a['id'],5));self.assertIsNone(q.snapshot(s,1));self.assertEqual(q.snapshot(s,2)['position'],1)
 def test_persistence_and_repeat_after_resolution(self):
  s={};a=q.submit(s,1,'a');s=json.loads(json.dumps(s));self.assertTrue(q.claim(s,a['id'],5));self.assertTrue(q.resolve(s,a['id'],5));b=q.submit(s,1,'new');self.assertNotEqual(a['id'],b['id'])
 def test_equal_timestamps_preserve_submission_order(self):
  s={}
  with patch('support_queue.time.time',return_value=100):
   for uid in range(12):q.submit(s,uid,'help')
   self.assertEqual([t['user_id'] for t in q.active(s)],list(range(12)))
 def test_priority_changes_follow_subscription_and_preserve_fifo(self):
  s={};a=q.submit(s,1,'first');b=q.submit(s,2,'second')
  self.assertTrue(q.refresh_priorities(s,lambda uid:uid==2));self.assertEqual(q.active(s)[0],b)
  self.assertFalse(q.refresh_priorities(s,lambda uid:uid==2))
  self.assertTrue(q.refresh_priorities(s,lambda uid:False));self.assertEqual(q.active(s)[0],a)
 def test_refresh_preserves_claimed_and_unknown_priority(self):
  s={};a=q.submit(s,1,'first',True);b=q.submit(s,2,'second');self.assertTrue(q.claim(s,a['id'],5))
  q.refresh_priorities(s,lambda uid:None if uid==1 else True)
  self.assertTrue(a['priority']);self.assertEqual(q.active(s)[0],a)
 def test_reopen_is_owned_once_and_rejoins_tail(self):
  s={};a=q.submit(s,1,'first');q.claim(s,a['id'],5);q.resolve(s,a['id'],5);b=q.submit(s,2,'other')
  self.assertIsNone(q.reopen(s,a['id'],3));r=q.reopen(s,a['id'],1);self.assertNotEqual(r['id'],a['id']);self.assertEqual(q.snapshot(s,1)['position'],2);self.assertIn('first',r['messages'][0]);self.assertIsNone(q.reopen(s,a['id'],1));self.assertEqual(len(q.active(s)),2)
 def test_reopen_merges_existing_active_request(self):
  s={};a=q.submit(s,1,'first');q.claim(s,a['id'],5);q.resolve(s,a['id'],5);b=q.submit(s,1,'second')
  r=q.reopen(s,a['id'],1,True);self.assertEqual(r['id'],b['id']);self.assertEqual(len(q.active(s)),1);self.assertTrue(r['priority'])
 def test_message_limit(self):
  s={}
  for i in range(30):t=q.submit(s,1,'x'*4000)
  self.assertEqual(len(t['messages']),20);self.assertEqual(len(t['messages'][0]),3000)

class DeliveryTests(unittest.IsolatedAsyncioTestCase):
 def setup_ns(self):
  self.settings={};self.sent=[]
  bot=SimpleNamespace(send_message=AsyncMock(return_value=SimpleNamespace(message_id=123)))
  ns=dict(InlineKeyboardMarkup=InlineKeyboardMarkup,InlineKeyboardButton=InlineKeyboardButton,support_queue=q,user_data={'__settings__':self.settings},SUPPORT_ADMIN_IDS=[5],SUPPORT_REPLY_IN_FLIGHT=set(),bot=bot,logging=logging,save_data=lambda d:self.sent.append(copy.deepcopy(d)),get_subscription_level=lambda u:u.get('tier'),get_user=lambda uid:{'lang':'ru'},get_text=lambda u,k,**v:v.get('text','reply'))
  load_functions({'_support_settings','refresh_support_priorities','support_snapshot','_support_threads','support_status_text','submit_support','support_admin_reply'},ns)
  return ns
 async def test_app_snapshot_refreshes_subscription_and_saves_only_changes(self):
  ns=self.setup_ns();q.submit(self.settings,1,'first');q.submit(self.settings,2,'second')
  ns['user_data'].update({'1':{},'2':{'tier':'super_pro'}})
  self.assertEqual(ns['support_snapshot'](2)['position'],1);self.assertTrue(self.sent)
  count=len(self.sent);ns['support_snapshot'](2);self.assertEqual(len(self.sent),count)
  ns['user_data']['2']['tier']=None;self.assertEqual(ns['support_snapshot'](1)['position'],1)
 async def test_failed_notification_keeps_durable_ticket(self):
  ns=self.setup_ns();ns['bot'].send_message.side_effect=RuntimeError('offline')
  text=await ns['submit_support'](1,{'lang':'ru'},'help')
  self.assertIn('1',text);self.assertEqual(q.snapshot(self.settings,1)['position'],1);self.assertTrue(self.sent)
 async def test_failed_reply_stays_open_successful_reply_closes(self):
  ns=self.setup_ns();await ns['submit_support'](1,{'lang':'ru'},'help')
  message=SimpleNamespace(from_user=SimpleNamespace(id=5),reply_to_message=SimpleNamespace(message_id=123),text='answer',answer=AsyncMock())
  ns['bot'].send_message.side_effect=RuntimeError('offline');await ns['support_admin_reply'](message)
  self.assertEqual(q.snapshot(self.settings,1)['status'],'in_progress');self.assertFalse(ns['SUPPORT_REPLY_IN_FLIGHT'])
  ns['bot'].send_message.side_effect=None;await ns['support_admin_reply'](message)
  self.assertIsNone(q.snapshot(self.settings,1));self.assertFalse(ns['SUPPORT_REPLY_IN_FLIGHT'])
 async def test_other_admin_cannot_skip_queue(self):
  ns=self.setup_ns();q.submit(self.settings,2,'older');await ns['submit_support'](1,{'lang':'ru'},'new')
  ns['bot'].send_message.reset_mock();message=SimpleNamespace(from_user=SimpleNamespace(id=5),reply_to_message=SimpleNamespace(message_id=123),text='answer',answer=AsyncMock());await ns['support_admin_reply'](message)
  ns['bot'].send_message.assert_not_awaited();self.assertEqual(q.snapshot(self.settings,1)['status'],'waiting')
