import unittest
from pathlib import Path
import profile_options as w

class WardrobeGenderTests(unittest.TestCase):
 def test_cross_gender_clothes_rejected_without_losing_inventory(self):
  for gender,key in [('male','dress'),('male','stockings'),('male','police_female'),('female','police_male')]:
   u={'gender':gender,'inventory':{key:1},'active_outfit':{'body':key}}
   with self.subTest(gender=gender,item=key):
    self.assertFalse(w.gender_matches(u,key))
    self.assertEqual(w.active_outfit(u),{})
    with self.assertRaises(ValueError):w.equip(u,key,10)
    self.assertEqual(u['inventory'],{key:1})
 def test_unisex_clothes_and_generated_preview_exist_for_both_genders(self):
  assets=Path(__file__).resolve().parents[1]
  for gender in ('male','female'):
   for key in ('tracksuit','pajamas','shirt','trousers','hat'):
    u={'gender':gender,'inventory':{key:1}}
    w.equip(u,key,10)
    self.assertTrue((assets/w.fitting_preview(u).lstrip('/')).is_file())
   for index in range(18):self.assertTrue((assets/'assets'/f'fitting_{gender}_{index}.webp').is_file())
