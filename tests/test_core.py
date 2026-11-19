import asyncio
"""Regression checks without bot credentials or network calls.

Load selected functions from the actual application AST, avoiding live Bot startup.
"""
import ast
import asyncio
import copy
import json
import logging
import os
from pathlib import Path
import random
import secrets
import tempfile
import types
import unittest
from datetime import datetime, timedelta

SOURCE = Path(__file__).resolve().parents[1] / 'app.py'
TREE = ast.parse(SOURCE.read_text())


def load_functions(names, namespace):
    namespace.setdefault("work_rotation", __import__("work_rotation"))
    namespace.setdefault("premium_rules", __import__("premium_rules"))
    namespace.setdefault("get_display_style",lambda u:u.get("style","warm"))
    namespace.setdefault("photo_wallet", __import__("photo_wallet"))
    namespace.setdefault("companion_initiative", __import__("companion_initiative"))
    for node in TREE.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            node = copy.deepcopy(node)
            node.decorator_list = []
            for arg in node.args.args:
                arg.annotation = None
            node.returns = None
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace


def literal(name):
    node = next(n for n in TREE.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name)
    return ast.literal_eval(node.value)


class CoreTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.saved = []
        self.ns = dict(secrets=secrets, datetime=datetime, timedelta=timedelta,
                       local_today=lambda: datetime(2026, 11, 13).date(),
                       get_subscription_level=lambda u: u.get('tier'),
                       save_data=lambda d: self.saved.append(copy.deepcopy(d)), user_data={},
                       REFERRAL_INVITER_BUCKS=2000, REFERRAL_INVITER_ENERGIZERS=1,
                       REFERRAL_INVITER_SCENES=2, REFERRAL_INVITEE_BUCKS=1500,
                       LANG_BUTTONS={'ru': '', 'en': '', 'de': ''},
                       APP_MESSAGE_MAX_LEN=2000,
                       app_unstick=lambda u: None,
                       _app_reply=lambda u, ok=True, error=None: dict(ok=ok, error=error, state=copy.deepcopy(u)))
        load_functions({'award_referral', 'ensure_message_ids', 'relationship_state', 'update_relationship',
                        'api_app_message_handler',
                        'api_app_settings_handler', 'energizer_pack_saving'}, self.ns)

    def test_referral_only_after_registration_and_only_once(self):
        inviter = {'personality_ready': True}
        invitee = {'referred_by': '1', 'referral_pending': True}
        self.ns['user_data'].update({'1': inviter, '2': invitee})
        award = self.ns['award_referral']
        self.assertFalse(award(invitee))
        invitee['personality_ready'] = True
        self.assertTrue(award(invitee))
        self.assertFalse(award(invitee))
        self.assertEqual((inviter['bucks'], inviter['energizers'], inviter['intim_scenes']), (2000, 1, 2))
        self.assertEqual(invitee['bucks'], 1500)
        self.assertEqual(inviter['referral_count'], 1)

    def test_unknown_inviter_does_not_create_phantom_account(self):
        self.assertFalse(self.ns['award_referral']({'referred_by': 'fake', 'referral_pending': True, 'personality_ready': True}))
        self.assertEqual(self.ns['user_data'], {})

    def test_message_ids_survive_trimming(self):
        user = {'history': [{'role': 'user', 'content': 'a'}, {'role': 'assistant', 'content': 'b'}]}
        self.ns['ensure_message_ids'](user)
        identity = user['history'][1]['id']
        user['history'].pop(0)
        self.ns['ensure_message_ids'](user)
        self.assertEqual(user['history'][0]['id'], identity)

    def test_relationship_not_farmed_by_spam_or_purchases(self):
        user = {}
        gain = self.ns['update_relationship']
        gain(user, 'ок', False)
        self.assertEqual(self.ns['relationship_state'](user)['trust'], 0)
        for _ in range(10):
            gain(user, 'Сегодня я прочитал интересную книгу', False)
        self.assertEqual(self.ns['relationship_state'](user)['trust'], 1)
        user['bucks'] = 1000000
        self.assertEqual(self.ns['relationship_state'](user)['trust'], 1)

    def test_pack_saving_ignores_coupon(self):
        self.ns.update(ENERGIZER_LIST_STARS={'energizer_2': 18, 'energizer_6': 50},
                       ENERGIZER_PACKS={'energizer_2': {'amount': 2}, 'energizer_6': {'amount': 6}})
        calculate = self.ns['energizer_pack_saving']
        self.assertEqual(calculate('energizer_6'), calculate('energizer_6', {'coupon': {'discount': .9}}))
        self.assertEqual(calculate('energizer_2'), 0)

    async def request_for(self, user, body):
        async def request(_): return 1, user, body, None
        self.ns['_play_request'] = self.ns['_app_request'] = request

    async def test_cannot_edit_assistant_or_another_history(self):
        user = {'history': [{'id': 'a', 'role': 'assistant', 'content': 'reply'}]}
        await self.request_for(user, {'id': 'a', 'action': 'edit', 'text': 'forged'})
        self.assertFalse((await self.ns['api_app_message_handler'](None))['ok'])
        await self.request_for(user, {'id': 'other-user-id', 'action': 'delete'})
        self.assertFalse((await self.ns['api_app_message_handler'](None))['ok'])
        self.assertEqual(user['history'][0]['content'], 'reply')

    async def test_premium_reaction_requires_subscription(self):
        user={'history':[{'id':'a','role':'assistant','content':'Hi'}]}
        await self.request_for(user, {'id':'a','action':'react','emoji':'💖'})
        self.ns['at']=lambda u,k:k
        self.assertFalse((await self.ns['api_app_message_handler'](None))['ok'])
        self.assertNotIn('user_reaction',user['history'][0])
        for tier in ('pro','super_pro','elite'):
            user['tier']=tier
            await self.ns['api_app_message_handler'](None)
            self.assertEqual(user['history'][0]['user_reaction'],'💖')
            self.assertTrue(user['history'][0]['reaction_animated'])
            await self.ns['api_app_message_handler'](None)
            self.assertIsNone(user['history'][0]['user_reaction'])

    async def test_expired_subscription_can_remove_old_premium_reaction(self):
        user={'history':[{'id':'a','role':'assistant','content':'Hi','user_reaction':'💖','reaction_animated':True}]}
        self.ns['at']=lambda u,k:k
        await self.request_for(user,{'id':'a','action':'react','emoji':'💖'})
        self.assertTrue((await self.ns['api_app_message_handler'](None))['ok'])
        self.assertIsNone(user['history'][0]['user_reaction'])

    async def test_edit_delete_and_reaction_toggle(self):
        user = {'history': [{'id': 'u', 'role': 'user', 'content': 'old'}, {'id': 'a', 'role': 'assistant', 'content': 'reply'}]}
        generated=[]
        async def regenerate(uid, account):
            generated.append([dict(m) for m in account['history']])
            account['history'].append({'id':'a','role':'assistant','content':'new reply'})
            account['app_pending']=None
        self.ns.update(asyncio=asyncio,app_generate=regenerate)
        await self.request_for(user, {'id':'u','action':'edit','text':'new'})
        self.assertTrue((await self.ns['api_app_message_handler'](None))['ok'])
        self.assertEqual(len(user['history']),1)
        self.assertTrue(user['history'][0]['edited'])
        await asyncio.sleep(0)
        self.assertEqual(generated[0][0]['content'],'new')
        self.assertEqual(len(generated[0]),1)
        await self.request_for(user, {'id': 'a', 'action': 'react', 'emoji': '❤️'})
        await self.ns['api_app_message_handler'](None)
        self.assertEqual(user['history'][1]['user_reaction'], '❤️')
        await self.ns['api_app_message_handler'](None)
        self.assertIsNone(user['history'][1]['user_reaction'])
        await self.request_for(user, {'id': 'u', 'action': 'delete'})
        await self.ns['api_app_message_handler'](None)
        self.assertEqual(user['history'], [])
        self.assertEqual(user['reply_choices'], {})

    async def test_generation_blocks_history_mutation(self):
        user = {'app_pending': 'now', 'history': [{'id': 'u', 'role': 'user', 'content': 'old'}]}
        await self.request_for(user, {'id': 'u', 'action': 'delete'})
        self.assertFalse((await self.ns['api_app_message_handler'](None))['ok'])
        self.assertEqual(len(user['history']), 1)


    async def test_settings_validation(self):
        user = {'lang': 'ru', 'scene': 'phone'}
        await self.request_for(user, {'lang': 'xx'})
        self.assertFalse((await self.ns['api_app_settings_handler'](None))['ok'])
        self.assertEqual(user['lang'], 'ru')
        await self.request_for(user, {'lang': 'en', 'scene': 'live', 'tour_seen': True})
        self.assertTrue((await self.ns['api_app_settings_handler'](None))['ok'])
        self.assertEqual((user['lang'], user['scene'], user['tour_seen']), ('en', 'live', True))

    def test_exact_bucks_pack_prices(self):
        products = literal('PRODUCTS')
        self.assertEqual([(literal('BUCKS_PACKS')[key], products[key]['stars']) for key in literal('BUCKS_PACKS')], [(5000, 10), (15000, 18), (50000, 35)])

    def test_wheel_energy_probability_reduced(self):
        prizes = literal('SPIN_PRIZES')
        chance = sum(p['weight'] for p in prizes if p['type'] == 'energizers') / sum(p['weight'] for p in prizes)
        self.assertLess(chance, .02)

    async def test_delete_discards_later_context(self):
        user = {'history': [
            {'id':'old','role':'assistant','content':'Earlier'},
            {'id':'u','role':'user','content':'secret'},
            {'id':'a','role':'assistant','content':'I remember secret'},
            {'id':'u2','role':'user','content':'Continue'},
            {'id':'a2','role':'assistant','content':'Still secret'}],
            'reply_choices': {'items':['secret']}, 'location':'secret place'}
        await self.request_for(user, {'id':'u','action':'delete'})
        await self.ns['api_app_message_handler'](None)
        self.assertEqual([m['id'] for m in user['history']],['old'])
        self.assertEqual(user['reply_choices'],{})
        self.assertEqual(user['location'],'unknown')


if __name__ == '__main__':
    unittest.main()
