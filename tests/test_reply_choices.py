"""Offline regression checks for optional reply suggestions."""
import asyncio
import hashlib
import json
import logging
import types
import unittest
from test_core import load_functions

class ReplyChoicesTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ns=dict(hashlib=hashlib,json=json,asyncio=asyncio,logging=logging,
                     is_asleep=lambda u:False,AI_MODEL='test',user_data={},save_data=lambda d:None)
        load_functions({'reply_choices_key','serialize_reply_choices','parse_reply_choices','generate_reply_choices'},self.ns)
        self.user={'lang':'ru','scene':'phone','history':[]}

    def test_four_starters_and_pending(self):
        ru=self.ns['serialize_reply_choices'](self.user)
        self.assertEqual(len(set(ru)),4)
        self.user['lang']='en'
        self.assertNotEqual(ru,self.ns['serialize_reply_choices'](self.user))
        self.assertEqual(self.user['history'],[])
        self.user['app_pending']='now'
        self.assertEqual(self.ns['serialize_reply_choices'](self.user),[])

    def test_validation(self):
        parse=self.ns['parse_reply_choices']
        for raw in ('bad','{}','["one"]','["one","one","two","three"]','[1,2,3,4]'):
            self.assertEqual(parse(raw),[])
        self.assertEqual(parse('["one","two","three","four"]'),['one','two','three','four'])

    def test_history_and_language_invalidate(self):
        self.user['history']=[{'role':'assistant','content':'How was your trip?'}]
        key=self.ns['reply_choices_key'](self.user)
        self.user['reply_choices']={'key':key,'items':['one','two','three','four']}
        self.assertEqual(len(self.ns['serialize_reply_choices'](self.user)),4)
        self.user['history'][0]['content']='A different question'
        self.assertEqual(self.ns['serialize_reply_choices'](self.user),[])
        self.user['history'][0]['content']='How was your trip?'
        self.user['lang']='en'
        self.assertEqual(self.ns['serialize_reply_choices'](self.user),[])

    async def test_context_and_stale_result(self):
        self.user['history']=[{'role':'assistant','content':'Where do you hike?'}]
        calls=[]
        def call(*args,**kwargs):
            calls.append(kwargs)
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='["Near my home.","Do you enjoy hiking?","Shall we plan a walk?","Tell me about your favourite trail."]'))])
        self.ns['call_ai']=call
        await self.ns['generate_reply_choices'](self.user,self.ns['reply_choices_key'](self.user))
        self.assertEqual(len(self.ns['serialize_reply_choices'](self.user)),4)
        self.assertEqual(len(self.user['history']),1)
        self.assertIn('Where do you hike?',calls[0]['messages'][1]['content'])
        old_key=self.ns['reply_choices_key'](self.user)
        self.user.pop('reply_choices')
        self.user['history'].append({'role':'user','content':'New message'})
        await self.ns['generate_reply_choices'](self.user,old_key)
        self.assertNotIn('reply_choices',self.user)
