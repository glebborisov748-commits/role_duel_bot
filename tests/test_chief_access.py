"""Chief-only mutations and rotation bypass must not leak to regular admins."""
import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock
import work_rotation
from test_core import load_functions

class ChiefAccessTests(unittest.IsolatedAsyncioTestCase):
 def test_only_chief_bypasses_rotation(self):
  today=date(2026,11,18)
  ns={'MAIN_ADMIN_ID':7287815074,'local_today':lambda:today}
  load_functions({'work_is_open'},ns)
  closed=next(job for job in work_rotation.JOBS if job not in work_rotation.active(today))
  for uid in (5255398262,8078585678,5507779506,42,None):
   self.assertFalse(ns['work_is_open'](closed,{'_telegram_id':uid}))
  self.assertTrue(ns['work_is_open'](closed,{'_telegram_id':7287815074}))
  self.assertFalse(ns['work_is_open']('forged',{'_telegram_id':7287815074}))
  self.assertTrue(ns['work_is_open']('farm',{}))
  regular=work_rotation.state(today,123)
  chief=work_rotation.state(today,123,bypass=True)
  self.assertEqual(len(regular['active']),3)
  self.assertEqual(set(chief['active']),set(work_rotation.JOBS))
  self.assertTrue(chief['bypass'])
 async def test_regular_admin_cannot_use_mutating_commands(self):
  names={'reset_all_cmd','maintenance_cmd','reset_me_cmd','grant_cmd','givebucks_cmd','giveenergizers_cmd','giveaway_all_cmd','revoke_subscription_cmd','setlevel_cmd','broadcast_cmd','cancel_broadcast_cmd','_grant_to'}
  ns={'MAIN_ADMIN_ID':7287815074,'ADMIN_IDS':[7287815074,5255398262],'maintenance_mode':False}
  load_functions(names,ns)
  message=SimpleNamespace(from_user=SimpleNamespace(id=5255398262),answer=AsyncMock(),text='/grant 5255398262 elite')
  for name in names:
   with self.subTest(command=name):
    if name=='_grant_to':await ns[name](message,5255398262,['/grant','self','elite'])
    else:await ns[name](message)
  self.assertFalse(ns['maintenance_mode'])
 async def test_regular_admin_cannot_confirm_destructive_callbacks(self):
  ns={'MAIN_ADMIN_ID':7287815074,'ADMIN_IDS':[7287815074,5255398262]}
  load_functions({'reset_all_confirm','broadcast_send_handler'},ns)
  call=SimpleNamespace(from_user=SimpleNamespace(id=5255398262),answer=AsyncMock())
  await ns['reset_all_confirm'](call)
  await ns['broadcast_send_handler'](call)
  self.assertEqual(call.answer.await_count,2)
