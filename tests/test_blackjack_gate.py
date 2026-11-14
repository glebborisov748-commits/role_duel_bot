import unittest
from test_core import load_functions

class BlackjackGateTests(unittest.IsolatedAsyncioTestCase):
    async def test_quiet_flag_does_not_bypass_sleep(self):
        spent=[]
        user={'sleep_until':'now','bucks':1000,'bj_talk':False}
        ns={'BJ_BETS':[50],'games_gate_error':lambda u:'asleep' if u.get('sleep_until') else None,
            '_play_reply':lambda u,ok=True,error=None:{'ok':ok,'error':error},
            'spend_bucks':lambda u,b:spent.append(b)}
        load_functions({'play_bj_start'},ns)
        result=await ns['play_bj_start'](1,user,{'bet':50,'talk':False})
        self.assertFalse(result['ok']);self.assertEqual(result['error'],'asleep')
        self.assertEqual(spent,[])
        self.assertTrue(user['bj_talk'])
