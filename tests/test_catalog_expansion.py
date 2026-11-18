"""Catalog metadata must not silently become new image-generation instructions."""
import unittest
import profile_options as wardrobe

class CatalogExpansionTests(unittest.TestCase):
 def test_requested_prices_slots_and_tags(self):
  expected={
   'crop_top':(300,'top','crop top'), 'oversized_shirt':(400,'top','oversized shirt'),
   'denim_shorts':(300,'bottom','denim shorts'), 'pencil_skirt':(500,'bottom','pencil skirt'),
   'qipao':(1000,'body','qipao, chinese dress'), 'tracksuit':(600,'body','tracksuit'),
   'cap':(200,'head','cap'), 'cat_ears_headband':(400,'head','cat ears headband'),
   'maid_outfit':(1500,'body','maid outfit, apron'), 'nurse_outfit':(1500,'body','nurse outfit'),
   'latex_bodysuit':(2000,'body','latex bodysuit'), 'lace_panties':(800,'bottom','lace panties'),
   'collar_leash':(600,'neck','choker, collar'), 'garter_stockings':(900,'legs','stockings, garter belt'),
  }
  for key,value in expected.items():
   with self.subTest(item=key):
    item=wardrobe.WARDROBE[key]
    self.assertEqual((item['price'],item['slot'],item['tags']),value)
 def test_male_collection_and_both_uniform_cuts(self):
  for key in ('business_suit','sportswear','casual_outfit','leather_jacket','stripper_outfit','boxer_outfit'):
   self.assertEqual(wardrobe.WARDROBE[key]['gender'],'male')
  for uniform in ('police','firefighter'):
   for gender in ('male','female'):
    item=wardrobe.WARDROBE[uniform+'_'+gender]
    self.assertEqual(item['gender'],gender);self.assertTrue(item['adult'])
  self.assertEqual(wardrobe.WARDROBE['leather_jacket']['slot'],'outerwear')
 def test_new_wearables_have_art_and_enforce_ownership_and_level(self):
  from pathlib import Path
  self.assertEqual(len(wardrobe.OUTFIT_FACTS),22)
  for key,fact in wardrobe.OUTFIT_FACTS.items():
   item=wardrobe.WARDROBE[key];self.assertFalse(item['catalog_only']);self.assertTrue(fact)
   self.assertTrue(Path('assets/'+item['image']+'.webp').is_file())
   with self.assertRaises(ValueError):wardrobe.equip({},key,10)
   u={'inventory':{key:1}}
   if item['adult']:
    with self.assertRaises(ValueError):wardrobe.equip(u,key,4)
   wardrobe.equip(u,key,5);self.assertIn(fact,wardrobe.clothing_facts(u,5))
 def test_existing_outfits_keep_their_photo_behavior(self):
  user={'inventory':{'tracksuit':1,'latex_bodysuit':1}}
  wardrobe.equip(user,'tracksuit',5)
  self.assertIn('comfortable opaque matching tracksuit',wardrobe.clothing_facts(user,5))
  wardrobe.equip(user,'latex_bodysuit',5)
  self.assertIn('opaque full-length high-neck',wardrobe.clothing_facts(user,5))
