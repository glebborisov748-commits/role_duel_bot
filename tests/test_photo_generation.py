import asyncio
import unittest
from unittest.mock import patch
import photo_generation
from test_core import load_functions
from datetime import datetime
from types import SimpleNamespace


class PhotoFlowTests(unittest.IsolatedAsyncioTestCase):
    def namespace(self, plan):
        async def thread(*args, **kwargs):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=plan))])
        ns=dict(asyncio=asyncio,datetime=datetime,json=__import__('json'),
                ENERGY_MAX=150,LOOKS={},get_intimacy_level=lambda u:1,AI_MODEL='mock',call_ai=lambda:None,
                PHOTO_ENERGY_COST=40,photo_generation=photo_generation,
                save_data=lambda d:None,user_data={},logging=__import__('logging'))
        load_functions({'app_photo_generate'},ns)
        return ns,thread

    async def test_failure_refunds_energy_and_clears_pending(self):
        ns,thread=self.namespace('{"allowed":true,"prompt":"adult in a suit"}')
        async def fail(prompt):raise RuntimeError('provider failed')
        user={'energy':150,'app_pending':'now','photo_pending':True}
        with patch('asyncio.to_thread',thread),patch.object(photo_generation,'generate',fail):
            await ns['app_photo_generate'](1,user,'a portrait')
        self.assertEqual(user['energy'],150)
        self.assertNotIn('photo_reserved',user)
        self.assertNotIn('photo_pending',user)
        self.assertIsNone(user['app_pending'])
        self.assertTrue(user['app_notices'])

    async def test_refusal_never_submits_or_charges(self):
        ns,thread=self.namespace('{"allowed":false,"prompt":""}')
        user={'energy':150,'history':[],'photo_pending':True}
        with patch('asyncio.to_thread',thread),patch.object(photo_generation,'generate') as gen:
            await ns['app_photo_generate'](1,user,'request')
        gen.assert_not_called()
        self.assertEqual(user['energy'],150)
        self.assertEqual(len(user['history']),1)

    async def test_success_persists_photo_and_charges_once(self):
        import tempfile,os,json,logging
        ns,thread=self.namespace('{"allowed":true,"prompt":"adult in a suit"}')
        async def image(prompt):return b'\xff\xd8\xfftest','jpg'
        user={'energy':150,'history':[],'photo_pending':True}
        with tempfile.TemporaryDirectory() as directory:
            ns.update(os=os,AVATAR_DIR=directory)
            with patch('asyncio.to_thread',thread),patch.object(photo_generation,'generate',image):
                await ns['app_photo_generate'](1,user,'a portrait')
            self.assertEqual(user['energy'],110)
            self.assertEqual(len(os.listdir(directory)),1)
            self.assertRegex(user['history'][0]['photo'],r'^/avatars/[0-9a-f]{24}\.jpg$')
            self.assertNotIn('photo_reserved',user)
