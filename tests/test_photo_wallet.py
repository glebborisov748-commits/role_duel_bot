import unittest
from datetime import datetime,timedelta
import photo_wallet as w
class WalletTests(unittest.TestCase):
 def test_migrate_trial_and_legacy_credit_once(self):
  u={'avatar_credits':2};self.assertEqual(w.balance(u),3);self.assertEqual(w.balance(u),3);self.assertNotIn('avatar_credits',u)
 def test_reserve_commit_refund_are_idempotent(self):
  u={};self.assertTrue(w.reserve(u,'a'));self.assertFalse(w.reserve(u,'a'));self.assertEqual(w.balance(u),0)
  self.assertTrue(w.finish(u,'a',True));self.assertFalse(w.finish(u,'a',True));self.assertEqual(w.balance(u),1)
  self.assertTrue(w.reserve(u,'b'));self.assertTrue(w.finish(u,'b'));self.assertEqual(w.balance(u),0)
 def test_expiring_first_and_paid_never_expire(self):
  u={};w.ensure(u);w.grant(u,3,(datetime.now()+timedelta(days=1)).isoformat());w.reserve(u,'a')
  self.assertEqual(u['photo_credits'],1);w.finish(u,'a');self.assertEqual(w.balance(u),3)
  for g in u['photo_grants']:g['expires_at']='2000-01-01'
  self.assertEqual(w.balance(u),1)
 def test_failure_after_expiry_is_still_refundable(self):
  u={};w.ensure(u);u['photo_credits']=0;w.grant(u,1,(datetime.now()+timedelta(seconds=1)).isoformat());w.reserve(u,'a')
  self.assertEqual(w.balance(u),0);w.finish(u,'a',True);self.assertEqual(w.balance(u),1)
 def test_existing_subscription_prorated_once(self):
  u={'subscription':{'active':True,'level':'pro','expires_at':(datetime.now()+timedelta(days=15,seconds=5)).isoformat()}}
  self.assertEqual(w.balance(u),23);self.assertEqual(w.balance(u),23)
 def test_restart_refunds_avatar_once_without_extra_legacy_credit(self):
  u={};w.ensure(u);w.reserve(u,'avatar');u['avatar_job']={'id':'job'};w.recover(u)
  self.assertEqual(w.balance(u),1);self.assertNotIn('avatar_credits',u);w.recover(u);self.assertEqual(w.balance(u),1)
 def test_restart_preserves_old_paid_avatar_and_trial(self):
  u={'avatar_credits':0,'avatar_job':{'id':'old'}};w.recover(u);self.assertEqual(w.balance(u),2);w.recover(u);self.assertEqual(w.balance(u),2)
