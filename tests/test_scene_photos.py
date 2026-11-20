import asyncio
import json
import logging
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from datetime import datetime
import scene_photos,profile_options
import photo_generation
from test_core import load_functions


class ScenePhotoTests(unittest.IsolatedAsyncioTestCase):
    def namespace(self):
        ns=dict(profile_options=profile_options,get_intimacy_level=lambda u:1,asyncio=asyncio,os=os,datetime=datetime,json=json,logging=logging,
                ENERGY_MAX=150,photo_appearance=lambda u:'adult with brown hair',LOOKS={'test':{'en':'blue eyes, brown hair'}},AI_MODEL='mock',call_ai=lambda:None,
                scene_photos=scene_photos,photo_generation=photo_generation,user_data={},save_data=lambda d:None)
        load_functions({'generate_scene_photo','refund_scene_photo','app_hot_generate'},ns)
        scene={'text':'A quiet evening in a cafe.','photo_id':'job','photo_status':'pending'}
        user={'look':'test','gender':'female','energy':110,'scene_photo_job':{'id':'job','reserved':40},'last_hot_scene':scene}
        async def thread(*args,**kw):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"setting":"cafe","lighting":"evening"}'))])
        return ns,user,scene,thread

    def test_only_allowlisted_background_details_enter_image_prompt(self):
        prompt=scene_photos.portrait_prompt('brown hair','female',json.dumps({'setting':'INJECTED','lighting':'INJECTED','prompt':'INJECTED'}))
        self.assertNotIn('INJECTED',prompt)
        self.assertIn('opaque casual outfit',prompt)
        self.assertNotIn('fully clothed',prompt)
        self.assertIn('simple neutral backdrop',prompt)
        self.assertIn('brown hair',prompt)

    async def test_one_photo_attached_to_scene_without_chat_message(self):
        ns,user,scene,thread=self.namespace();calls=[]
        async def image(prompt,**kwargs):calls.append(prompt);return b'\xff\xd8\xfftest','jpg'
        with tempfile.TemporaryDirectory() as directory:
            ns['AVATAR_DIR']=directory
            with patch('asyncio.to_thread',thread),patch.object(photo_generation,'generate',image):
                await ns['generate_scene_photo'](user,scene,'job')
            self.assertEqual(len(calls),1)
            self.assertIn('cozy cafe',calls[0]);self.assertNotIn(scene['text'],calls[0])
            self.assertEqual(scene['photo_status'],'ready')
            self.assertRegex(scene['photo'],r'^/avatars/[0-9a-f]{24}\.jpg$')
            self.assertEqual(len(os.listdir(directory)),1)
            self.assertEqual(user['energy'],110)
            self.assertNotIn('scene_photo_job',user)
            self.assertNotIn('history',user)

    async def test_provider_failure_preserves_text_and_refunds_once(self):
        ns,user,scene,thread=self.namespace()
        async def fail(prompt,**kwargs):raise RuntimeError('provider failure')
        with patch('asyncio.to_thread',thread),patch.object(photo_generation,'generate',fail):
            await ns['generate_scene_photo'](user,scene,'job')
        self.assertEqual(user['energy'],150)
        self.assertEqual(scene['text'],'A quiet evening in a cafe.')
        self.assertEqual(scene['photo_status'],'error')
        self.assertFalse(ns['refund_scene_photo'](user,'job'))
        self.assertEqual(user['energy'],150)

    async def test_stale_scene_never_gets_photo_attached_to_new_scene(self):
        ns,user,scene,thread=self.namespace()
        async def replaced(prompt,**kwargs):
            user['last_hot_scene']={'text':'A different scene.'}
            return b'\xff\xd8\xfftest','jpg'
        with patch('asyncio.to_thread',thread),patch.object(photo_generation,'generate',replaced):
            await ns['generate_scene_photo'](user,scene,'job')
        self.assertEqual(user['energy'],150)
        self.assertNotIn('photo',user['last_hot_scene'])

    async def test_text_is_available_while_photo_is_still_pending(self):
        ns,user,scene,thread=self.namespace();park=asyncio.Event();tasks=[]
        async def core(account,**kw):return scene
        async def photo(*args):await park.wait()
        def spawn(coro):
            task=asyncio.create_task(coro);tasks.append(task);return task
        ns.update(intim_scene_core=core,generate_scene_photo=photo,
                  asyncio=SimpleNamespace(create_task=spawn),refund_intim_scene=lambda *a:None,at=lambda u,k:k)
        user['hot_pending']='now'
        await ns['app_hot_generate'](1,user,'paid',photo_job_id='job')
        self.assertIsNone(user['hot_pending'])
        self.assertEqual(scene['photo_status'],'pending')
        self.assertEqual(scene['text'],'A quiet evening in a cafe.')
        self.assertEqual(len(tasks),1)
        park.set();await asyncio.gather(*tasks)

    async def test_text_generation_failure_refunds_both_reservations(self):
        ns,user,scene,thread=self.namespace();refunds=[]
        async def fail(*args,**kw):raise RuntimeError('text failure')
        ns.update(intim_scene_core=fail,refund_intim_scene=lambda u,k:refunds.append(k),at=lambda u,k:k)
        await ns['app_hot_generate'](1,user,'paid',photo_job_id='job')
        self.assertEqual(refunds,['paid']);self.assertEqual(user['energy'],150)
        self.assertIsNone(user['hot_pending'])

class ScenePhotoReservationTests(unittest.IsolatedAsyncioTestCase):
    def namespace(self):
        user={'world':'anime','energy':150,'intim_scenes':2}
        body={'type':'test','location':'any','dominant':'any','photo':True}
        consumed=[];scheduled=[]
        async def request(r):return 1,user,body,None
        async def job(*a,**kw):pass
        def spawn(coro):scheduled.append(True);coro.close()
        def consume(u):consumed.append(True);u['intim_scenes']-=1;return 'paid'
        ns=dict(_play_request=request,serialize_hot=lambda u:None,photo_generation=SimpleNamespace(token=lambda:'fake'),
            PHOTO_ENERGY_COST=40,consume_intim_scene=consume,datetime=datetime,secrets=__import__('secrets'),
            INTIM_SCENES={'test':{}},INTIM_DOMINANTS={'any':{}},intim_compatible_locations=lambda t:['any'],
            web=SimpleNamespace(json_response=lambda x:x),save_data=lambda d:None,user_data={},get_text=lambda u,k:k,
            serialize_app_state=lambda u:dict(u),asyncio=SimpleNamespace(create_task=spawn),app_hot_generate=job,at=lambda u,k:k)
        load_functions({'api_app_hot_start_handler'},ns)
        return ns,user,body,consumed,scheduled
    async def test_one_reservation_and_no_double_click_charge(self):
        ns,u,body,consumed,jobs=self.namespace()
        self.assertTrue((await ns['api_app_hot_start_handler'](None))['ok'])
        self.assertEqual(u['energy'],150);self.assertEqual(u['intim_scenes'],1)
        self.assertEqual(len(jobs),1)
        self.assertFalse((await ns['api_app_hot_start_handler'](None))['ok'])
        self.assertEqual(u['energy'],150);self.assertEqual(len(consumed),1)
    async def test_insufficient_energy_does_not_consume_scene(self):
        ns,u,body,consumed,jobs=self.namespace();u['energy']=39;u.update(photo_wallet_version=1,photo_credits=0,photo_trial_granted=True)
        self.assertFalse((await ns['api_app_hot_start_handler'](None))['ok'])
        self.assertFalse(consumed);self.assertFalse(jobs);self.assertEqual(u['energy'],39)
    async def test_photo_opt_out_preserves_energy(self):
        ns,u,body,consumed,jobs=self.namespace();body['photo']=False
        self.assertTrue((await ns['api_app_hot_start_handler'](None))['ok'])
        self.assertEqual(u['energy'],150);self.assertNotIn('scene_photo_job',u)
