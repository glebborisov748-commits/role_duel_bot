import copy
import json
import re
import unittest
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
import daily_quests
from test_core import load_functions

class DailyQuestTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.now=datetime(2026,11,14,12)
        self.body={}
        self.user={'quest_seed':'test-seed','bucks':10,'energy':20,'tier':None,'channel_quest_completed':True}
        self.ns=dict(work_rotation=SimpleNamespace(events=lambda day:{q[1] for q in daily_quests.CATALOG}),CHANNEL_URL='https://t.me/duel_dev_channel',daily_quests=daily_quests,datetime=datetime,timedelta=timedelta,re=re,
            local_today=lambda:self.now.date(),local_now=lambda:self.now,BOT_TZ=timezone(timedelta(hours=3)),
            has_active_subscription=lambda u:u.get('tier') in ('pro','super_pro','elite'),
            get_subscription_level=lambda u:u.get('tier'),ENERGY_MAX=150,
            user_data={},save_data=lambda d:None,at=lambda u,k:k,
            _app_reply=lambda u,ok=True,error=None:{'ok':ok,'error':error})
        async def request(r):return 1,self.user,self.body,None
        self.ns['_play_request']=request
        load_functions({'daily_reset_timestamp','ensure_quests','quest_event','daily_quest_state',
            'api_app_task_handler','conversation_mode_rule','clean_chat_reply','consume_free_spin',
            '_reset_daily_quota_if_needed','free_spins_allowed','free_spins_left'},self.ns)

    def force(self, quest_id, progress=100):
        self.user['daily_quests']={'day':self.now.date().isoformat(),'items':[
            {'id':quest_id,'progress':progress,'claimed':False},
            {'id':'water2' if quest_id!='water2' else 'hack3','progress':0,'claimed':False}]}
        self.body={'day':self.now.date().isoformat(),'id':quest_id}

    def test_selection_survives_reload_and_has_two_different_events(self):
        state=self.ns['daily_quest_state'](self.user)
        self.assertEqual(len(state['items']),2)
        self.assertEqual(len({q['event'] for q in state['items']}),2)
        restored=json.loads(json.dumps(self.user))
        self.assertFalse(daily_quests.ensure(restored,self.now.date().isoformat()))
        self.assertEqual(restored,self.user)

    def test_new_day_resets_progress_and_claims(self):
        self.force('hack3');self.user['daily_quests']['items'][0]['claimed']=True
        self.now+=timedelta(days=1)
        self.ns['ensure_quests'](self.user)
        self.assertTrue(all(not q['claimed'] and q['progress']==0 for q in self.user['daily_quests']['items']))
        self.assertEqual(self.user['daily_quests']['day'],'2026-11-15')

    async def test_free_user_can_claim_once(self):
        self.force('hack3',2)
        self.assertFalse((await self.ns['api_app_task_handler'](None))['ok'])
        self.ns['quest_event'](self.user,'hack')
        self.assertTrue((await self.ns['api_app_task_handler'](None))['ok'])
        self.assertEqual(self.user['bucks'],310)
        self.assertFalse((await self.ns['api_app_task_handler'](None))['ok'])
        self.assertEqual(self.user['bucks'],310)

    async def test_all_subscription_tiers_double_only_bucks(self):
        for tier in ('pro','super_pro','elite'):
            self.user['tier']=tier;self.user['bucks']=0;self.force('hack3')
            self.assertTrue((await self.ns['api_app_task_handler'](None))['ok'])
            self.assertEqual(self.user['bucks'],600)
            self.force('chat8');self.user['intim_scenes']=0
            await self.ns['api_app_task_handler'](None)
            self.assertEqual(self.user['intim_scenes'],1)
            self.force('hack5');self.user['energizers']=0
            await self.ns['api_app_task_handler'](None)
            self.assertEqual(self.user['energizers'],1)

    async def test_energy_reward_waits_for_full_capacity_and_wakes(self):
        self.force('catch20');self.user.update(energy=150,sleep_until='now')
        self.assertFalse((await self.ns['api_app_task_handler'](None))['ok'])
        self.assertFalse(self.user['daily_quests']['items'][0]['claimed'])
        self.user['energy']=111
        self.assertFalse((await self.ns['api_app_task_handler'](None))['ok'])
        self.user['energy']=110
        self.assertTrue((await self.ns['api_app_task_handler'](None))['ok'])
        self.assertEqual(self.user['energy'],150)
        self.assertIsNone(self.user['sleep_until'])
        self.assertFalse((await self.ns['api_app_task_handler'](None))['ok'])
    async def test_stale_claim_rejected_after_moscow_midnight(self):
        self.force('hack3');self.now=datetime(2026,11,14,23,59)
        reset=self.ns['daily_reset_timestamp']()
        self.assertEqual(reset,int(datetime(2026,11,15,tzinfo=timezone(timedelta(hours=3))).timestamp()))
        self.now+=timedelta(minutes=2)
        self.assertFalse((await self.ns['api_app_task_handler'](None))['ok'])
        self.assertEqual(self.user['bucks'],10)
        self.assertEqual(self.user['daily_quests']['day'],'2026-11-15')

    def test_only_matching_event_progresses(self):
        self.force('courier20',0)
        self.ns['quest_event'](self.user,'catch')
        self.assertEqual(self.user['daily_quests']['items'][0]['progress'],0)
        self.ns['quest_event'](self.user,'courier')
        self.assertEqual(self.user['daily_quests']['items'][0]['progress'],1)

    def test_daily_spins_reset_preserves_bonus(self):
        self.ns.update(FREE_SPINS_PER_DAY={None:1,'pro':2},FREE_DAILY_BUCKS=0,
            _maybe_escalate_illness=lambda u:None,_maybe_get_sick=lambda u:None)
        self.user.update(last_daily_reset='2026-11-13',free_spins_used=1,bonus_spins=3)
        self.assertEqual(self.ns['free_spins_left'](self.user),4)
        self.ns['consume_free_spin'](self.user)
        self.assertEqual((self.user['free_spins_used'],self.user['bonus_spins']),(1,3))
        self.ns['consume_free_spin'](self.user)
        self.assertEqual(self.user['bonus_spins'],2)

    def test_phone_strips_actions_but_roleplay_keeps_them(self):
        clean=self.ns['clean_chat_reply']
        self.assertEqual(clean('*улыбаюсь* Привет!',{'scene':'phone'}),'Привет!')
        self.assertEqual(clean('*улыбаюсь* Привет!',{'scene':'live'}),'*Персонаж улыбается*\n\nПривет!')
