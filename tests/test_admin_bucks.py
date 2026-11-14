import types
import unittest
from test_core import load_functions

class AdminBucksTests(unittest.IsolatedAsyncioTestCase):
    async def test_admin_only_and_positive_amount(self):
        calls=[];answers=[]
        async def answer(text):answers.append(text)
        async def resolve(message,target):return 42
        async def grant(message,user_id,args):calls.append((user_id,args))
        ns={'ADMIN_IDS':[7],'_resolve_admin_target':resolve,'_grant_to':grant}
        load_functions({'givebucks_cmd'},ns)
        message=types.SimpleNamespace(from_user=types.SimpleNamespace(id=8),text='/givebucks @friend 5000',answer=answer)
        await ns['givebucks_cmd'](message);self.assertFalse(calls)
        message.from_user.id=7;message.text='/givebucks @friend -5'
        await ns['givebucks_cmd'](message);self.assertFalse(calls)
        message.text='/givebucks @friend 5000'
        await ns['givebucks_cmd'](message)
        self.assertEqual(calls,[(42,['/grant','@friend','bucks','5000'])])
        message.text='/givebucks 42 10000000'
        await ns['givebucks_cmd'](message)
        self.assertEqual(calls[-1],(42,['/grant','42','bucks','10000000']))
