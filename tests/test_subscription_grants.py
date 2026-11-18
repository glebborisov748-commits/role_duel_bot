import unittest
from datetime import datetime,timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock
import photo_wallet
from test_core import load_functions

class SubscriptionGrantTests(unittest.IsolatedAsyncioTestCase):
 def test_command_shared_grant_adds_quota_once(self):
  ns={'datetime':datetime,'timedelta':timedelta,'SUBSCRIPTION_LEVEL_RANK':{'pro':1,'super_pro':2,'elite':3}}
  load_functions({'grant_subscription_days'},ns)
  user={'subscription':{}}
  ns['grant_subscription_days'](user,'pro',7)
  self.assertEqual(photo_wallet.balance(user),11)
  expiry=user['subscription']['expires_at']
  self.assertEqual(photo_wallet.balance(user),11)
  ns['grant_subscription_days'](user,'elite',30)
  self.assertEqual(photo_wallet.balance(user),211)
  self.assertGreater(user['subscription']['expires_at'],expiry)
 def test_old_admin_grant_repaired_once_without_replenishing_spent_quota(self):
  user={'photo_wallet_version':1,'photo_credits':0,'granted_sub_at':datetime.now().isoformat(),'subscription':{'active':True,'level':'super_pro','expires_at':(datetime.now()+timedelta(days=15,seconds=1)).isoformat()}}
  self.assertEqual(photo_wallet.balance(user),45)
  user['photo_grants']=[]
  self.assertEqual(photo_wallet.balance(user),0)
  self.assertEqual(photo_wallet.balance(user),0)
 def test_existing_paid_or_reserved_accounts_not_topped_up_by_repair(self):
  for extra in ({'ever_subscribed':True},{'photo_reservations':{'avatar':{'started':'x'}}}):
   user={'photo_wallet_version':1,'photo_credits':0,'granted_sub_at':datetime.now().isoformat(),'subscription':{'active':True,'level':'pro','expires_at':(datetime.now()+timedelta(days=30)).isoformat()},**extra}
   self.assertEqual(photo_wallet.balance(user),0)
 async def test_notes_and_edits_do_not_request_generation(self):
  user={};generate=AsyncMock()
  ns={'APP_MODE':True,'get_user':lambda uid:user,'generate_and_reply':generate}
  load_functions({'handle_message','handle_edited_message'},ns)
  message=SimpleNamespace(from_user=SimpleNamespace(id=42),text='Заметка себе',answer=AsyncMock())
  await ns['handle_message'](message)
  await ns['handle_edited_message'](message)
  generate.assert_not_awaited();message.answer.assert_not_awaited()
 async def test_maintenance_reason_persists_and_clears(self):
  saved=[];data={}
  ns={'MAIN_ADMIN_ID':7,'maintenance_mode':False,'user_data':data,'save_data':lambda d:saved.append(True),'get_text':lambda u,key:data['__settings__'].get('maintenance_reason','')}
  load_functions({'maintenance_cmd'},ns)
  message=SimpleNamespace(from_user=SimpleNamespace(id=7),text='/tehwork on Обновляем магазин и оплату',answer=AsyncMock())
  await ns['maintenance_cmd'](message)
  self.assertTrue(ns['maintenance_mode'])
  self.assertEqual(data['__settings__']['maintenance_reason'],'Обновляем магазин и оплату')
  message.text='/tehwork off';await ns['maintenance_cmd'](message)
  self.assertFalse(ns['maintenance_mode']);self.assertNotIn('maintenance_reason',data['__settings__'])
