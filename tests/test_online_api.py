import copy
import time
import unittest
import online_games
from test_core import load_functions,literal

class OnlineAPITests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.users={'1':{'bucks':1000,'lang':'ru'},'2':{'bucks':1000,'lang':'ru'},'3':{'bucks':1000,'lang':'ru'}}
        self.store={};self.uid='1';self.body={};self.saved=0
        async def request(r):return int(self.uid),self.users[self.uid],self.body,None
        def save(d):self.saved+=1
        self.ns=dict(ONLINE_SKINS=literal("ONLINE_SKINS"),copy=copy,re=__import__('re'),online_games=online_games,time=time,
            datetime=__import__('datetime').datetime,user_data=self.users,online_store=lambda:self.store,
            online_adult_allowed=lambda u:bool(u.get('adult')),logging=__import__('logging'),
            save_data=save,_play_request=request,_BOT_USERNAME={'v':'testbot'},
            web=type('Web',(),{'json_response':staticmethod(lambda b:b)}))
        load_functions({'api_online_handler'},self.ns)
    async def call(self,uid,**body):
        self.uid=uid;self.body=body;return await self.ns['api_online_handler'](None)
    async def test_stake_consent_validation_and_membership(self):
        result=await self.call('1',action='start',game='connect4',kind='friend',bet=100)
        code=result['state']['room']['id']
        bad=await self.call('2',action='join',code=code,bet=0)
        self.assertFalse(bad['ok']);self.assertEqual(self.users['2']['bucks'],1000)
        result=await self.call('2',action='join',code=code,bet=100)
        self.assertTrue(result['ok'])
        bad=await self.call('3',action='move',room=code,seq=0,move={'column':0})
        self.assertEqual(bad['error'],'not_member')
        self.assertEqual(self.users['3']['bucks'],1000)
    async def test_adult_confirmed_by_both_and_entitlement_checked(self):
        bad=await self.call('1',action='start',game='rps18',kind='friend',adult=True,bet=0)
        self.assertEqual(bad['error'],'adult_required')
        self.users['1']['adult']=True
        created=await self.call('1',action='start',game='rps18',kind='friend',adult=True,bet=0)
        code=created['state']['room']['id']
        bad=await self.call('2',action='join',code=code,adult=True,bet=0)
        self.assertEqual(bad['error'],'adult_required')
        self.users['2']['adult']=True
        bad=await self.call('2',action='join',code=code,adult=False,bet=0)
        self.assertEqual(bad['error'],'adult_required')
        self.assertTrue((await self.call('2',action='join',code=code,adult=True,bet=0))['ok'])
    async def test_failed_disk_write_rolls_back_escrow_and_room(self):
        def fail(d):raise OSError('disk full')
        self.ns['save_data']=fail
        response=await self.call('1',action='start',game='dice',kind='friend',bet=500)
        self.assertEqual(response['error'],'save_failed')
        self.assertEqual(self.users['1']['bucks'],1000)
        self.assertFalse(self.store)
        self.assertNotIn('online_room',self.users['1'])
    async def test_invalid_move_cannot_stall_an_expired_game(self):
        result=await self.call('1',action='start',game='chess',kind='friend',bet=100)
        code=result['state']['room']['id']
        await self.call('2',action='join',code=code,bet=100)
        self.store[code]['deadline']=time.time()-1
        await self.call('1',action='move',room=code,seq=0,move={'move':'illegal'})
        self.assertEqual(self.store[code]['winner'],1)
        self.assertEqual(self.users['2']['bucks'],1100)
        await self.call('2',action='state')
        self.assertEqual(self.users['2']['bucks'],1100)
