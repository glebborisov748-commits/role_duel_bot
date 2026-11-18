import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from test_core import load_functions
class AdminReleaseTests(unittest.IsolatedAsyncioTestCase):
 async def test_level_is_admin_only_and_validated(self):
  u={};answer=AsyncMock();resolve=AsyncMock(return_value=42)
  ns={'ADMIN_IDS':{7},'_resolve_admin_target':resolve,'get_user':lambda uid:u,'LEVEL_XP_THRESHOLD':{8:999},'save_data':lambda d:None,'user_data':{}}
  load_functions({'setlevel_cmd'},ns);m=SimpleNamespace(from_user=SimpleNamespace(id=6),text='/setlevel 42 8',answer=answer)
  await ns['setlevel_cmd'](m);resolve.assert_not_awaited();m.from_user.id=7;m.text='/setlevel 42 11';await ns['setlevel_cmd'](m);resolve.assert_not_awaited()
  m.text='/setlevel 42 8';await ns['setlevel_cmd'](m);self.assertEqual(u['xp'],999)
 async def test_broadcast_needs_valid_owner_and_draft_token(self):
  answer=AsyncMock();u={'broadcast_draft':{'token':'good','status':'draft'}};tasks=[]
  async def deliver(*a):pass
  def spawn(coro):tasks.append(True);coro.close()
  ns={'ADMIN_IDS':{7},'get_user':lambda uid:u,'save_data':lambda d:None,'user_data':{},'asyncio':SimpleNamespace(create_task=spawn),'deliver_broadcast':deliver}
  load_functions({'broadcast_send_handler'},ns);call=SimpleNamespace(from_user=SimpleNamespace(id=6),data='broadcast:good',answer=answer)
  await ns['broadcast_send_handler'](call);self.assertFalse(tasks)
  call.from_user.id=7;call.data='broadcast:wrong';await ns['broadcast_send_handler'](call);self.assertFalse(tasks)
  call.data='broadcast:good';await ns['broadcast_send_handler'](call);self.assertEqual(len(tasks),1)
  await ns['broadcast_send_handler'](call);self.assertEqual(len(tasks),1)
