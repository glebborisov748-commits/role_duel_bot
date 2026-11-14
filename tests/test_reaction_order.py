import asyncio
import copy
import types
import unittest
from test_core import load_functions

class ReactionOrderTests(unittest.IsolatedAsyncioTestCase):
    async def test_reaction_persists_before_answer(self):
        user={'app_pending':'now','history':[{'role':'user','content':'Hello'}]}
        snapshots=[]
        async def thread(*args,**kw):
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='Hi (радость)'))])
        async def delay(seconds):
            self.assertGreaterEqual(seconds,1.5)
            self.assertEqual(user['history'][-1]['role'],'user')
            self.assertEqual(user['history'][-1]['reaction'],'😊')
        ns=dict(asyncio=types.SimpleNamespace(to_thread=thread,sleep=delay),build_prompt=lambda u:'prompt',
                clean_chat_reply=lambda text,user:text,call_ai=None,AI_MODEL='test',extract_reaction_from_answer=lambda t:('😊','Hi'),
                random=types.SimpleNamespace(random=lambda:0),save_data=lambda d:snapshots.append(copy.deepcopy(user)),
                user_data={},get_history_limit=lambda u:20,datetime=__import__('datetime').datetime,
                apply_activity_stat_cost=lambda *a:None,ENERGY_COST_MESSAGE=1,SATIETY_COST_MESSAGE=1,WATER_COST_MESSAGE=1)
        load_functions({'ai_chat_answer'},ns)
        await ns['ai_chat_answer'](user)
        self.assertEqual(len(snapshots[0]['history']),1)
        self.assertEqual(snapshots[-1]['history'][-1]['content'],'Hi')
