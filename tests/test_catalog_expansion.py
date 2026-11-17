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
 def test_every_new_item_is_catalog_only_and_cannot_displace_current_outfit(self):
  new={k:v for k,v in wardrobe.WARDROBE.items() if v.get('catalog_only')}
  self.assertEqual(len(new),22)
  user={'inventory':{k:1 for k in wardrobe.WARDROBE},'active_outfit':{'body':'dress','shoes':'heels'}}
  before=dict(user['active_outfit'])
  for key,item in new.items():
   with self.subTest(item=key):
    self.assertIn(item['slot'],wardrobe.SLOTS)
    self.assertTrue(all(item.get(lang) for lang in ('name','ru','de')))
    self.assertIs(type(item['price']),int);self.assertGreater(item['price'],0)
    self.assertTrue(item['tags']);self.assertEqual(item['fact'],'')
    with self.assertRaises(ValueError):wardrobe.equip(user,key,10)
    self.assertEqual(user['active_outfit'],before)
 def test_new_tags_never_enter_photos_even_if_old_client_supplies_active_slot(self):
  for key,item in wardrobe.WARDROBE.items():
   if not item.get('catalog_only'):continue
   user={'inventory':{key:1},'active_outfit':{item['slot']:key}}
   for level in (1,5,10):
    self.assertEqual(wardrobe.clothing_facts(user,level),'an opaque casual shirt and full-length trousers')
 def test_existing_outfits_keep_their_photo_behavior(self):
  user={'inventory':{'tracksuit':1,'latex_bodysuit':1}}
  wardrobe.equip(user,'tracksuit',5)
  self.assertIn('comfortable opaque matching tracksuit',wardrobe.clothing_facts(user,5))
  wardrobe.equip(user,'latex_bodysuit',5)
  self.assertIn('opaque full-length high-neck',wardrobe.clothing_facts(user,5))
