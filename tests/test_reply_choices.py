import unittest
from test_core import load_functions
class StarterTests(unittest.TestCase):
 def setUp(self):
  self.ns={};load_functions({'serialize_reply_choices'},self.ns)
 def test_starters_only_before_first_user_message(self):
  u={'lang':'ru','style':'shy','history':[]}
  choices=self.ns['serialize_reply_choices'](u);self.assertEqual(len(choices),4);self.assertEqual(choices,self.ns['serialize_reply_choices'](u))
  self.assertFalse(any('мир' in c for c in choices))
  u['history'].append({'role':'user','content':'Привет'});self.assertEqual(self.ns['serialize_reply_choices'](u),[])
 def test_seed_and_personality_change_starters(self):
  a={'lang':'ru','style':'warm','starter_seed':1};b={'lang':'ru','style':'aggressive','starter_seed':2}
  self.assertNotEqual(self.ns['serialize_reply_choices'](a),self.ns['serialize_reply_choices'](b))
