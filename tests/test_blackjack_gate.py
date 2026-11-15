import unittest
from test_core import load_functions

class BlackjackRetirementTests(unittest.TestCase):
    def test_unresolved_stake_refunded_once(self):
        ns={};load_functions({'retire_blackjack'},ns)
        u={'bucks':100,'play':{'mode':'bj','phase':'turn','bet':500}}
        self.assertTrue(ns['retire_blackjack'](u));self.assertEqual(u['bucks'],600)
        self.assertFalse(ns['retire_blackjack'](u));self.assertEqual(u['bucks'],600)

    def test_settled_stake_not_refunded(self):
        ns={};load_functions({'retire_blackjack'},ns)
        u={'bucks':100,'play':{'mode':'bj','phase':'done','bet':500}}
        ns['retire_blackjack'](u);self.assertEqual(u['bucks'],100)
