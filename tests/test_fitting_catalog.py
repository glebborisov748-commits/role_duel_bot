"""Complete wearable coverage and free, inventory-gated mannequin previews."""
import math,unittest
from pathlib import Path
import fitting_looks as looks
import mannequin_catalog as catalog
import profile_options as wardrobe

ROOT=Path(__file__).resolve().parents[1]
class CatalogTests(unittest.TestCase):
 def test_complete_gender_coverage_and_registered_images(self):
  expected={(g,k) for k,item in wardrobe.WARDROBE.items() if item.get('slot') for g in ('female','male') if item.get('gender','unisex') in ('unisex',g)}
  self.assertEqual(set(catalog.VIEWS),expected)
  for g,k in expected:
   self.assertEqual(wardrobe.catalog_image(k,g),wardrobe.WARDROBE[k]['image']);self.assertNotIn('fitting_catalog_',wardrobe.catalog_image(k,g));self.assertTrue((ROOT/'assets'/(wardrobe.catalog_image(k,g)+'.webp')).is_file())
   path=ROOT/catalog.image(g,k).lstrip('/')
   self.assertGreater(path.stat().st_size,128);self.assertEqual(path.read_bytes()[8:12],b'WEBP')
   self.assertIn(path.name,wardrobe.FITTING_ANCHORS)
  for gender in ('female','male'):self.assertTrue((ROOT/catalog.base(gender).lstrip('/')).is_file())
 def test_every_single_item_has_its_whole_view_without_spending(self):
  for (g,k),row in catalog.VIEWS.items():
   u=dict(gender=g,inventory={k:1},bucks=123,photo_credits=2,energy=80)
   wardrobe.equip(u,k,5);self.assertEqual(wardrobe.fitting_state(u),dict(base=catalog.image(g,k),layers=[]),(g,k))
   self.assertEqual((u['bucks'],u['photo_credits'],u['energy']),(123,2,80))
 def test_new_looks_require_ownership_and_respect_age_level(self):
  for key,look in looks.LOOKS.items():
   if not key.startswith('catalog_'):continue
   u={'gender':look['gender'],'inventory':{}}
   with self.assertRaises(ValueError):looks.equip(u,key,5)
   self.assertNotIn('active_outfit',u)
   u['inventory']={k:1 for k in look['slots'].values()}
   if any(wardrobe.WARDROBE[k]['adult'] for k in look['slots'].values()):
    with self.assertRaises(ValueError):looks.equip(u,key,0)
   looks.equip(u,key,5);self.assertEqual(wardrobe.fitting_state(u)['base'],look['image'])
 def test_arbitrary_layers_have_anatomy_transforms_and_no_duplicate_body(self):
  for gender,body in [('female','dress'),('male','casual_outfit')]:
   u={'gender':gender,'inventory':{k:1 for k in wardrobe.WARDROBE}}
   for k in (body,'cap','round_glasses','silver_chain','wristwatch'):wardrobe.equip(u,k,5)
   preview=wardrobe.fitting_state(u);self.assertEqual(preview['base'],catalog.image(gender,body))
   self.assertEqual({l['slot'] for l in preview['layers']},{'head','face','neck','wrist'})
   for layer in preview['layers']:
    self.assertTrue((ROOT/layer['url'].lstrip('/')).is_file())
    for field in ('offset_x','offset_y','scale','origin_y'):self.assertTrue(math.isfinite(layer[field]))
 def test_equipping_a_catalog_accessory_preserves_current_clothes(self):
  u={'gender':'female','inventory':{'dress':1,'cap':1}}
  wardrobe.equip(u,'dress',5);looks.equip(u,'catalog_female_cap',5)
  self.assertEqual(wardrobe.active_outfit(u),{'body':'dress','head':'cap'})
 def test_owned_groups_only_expose_allowed_items(self):
  u={'gender':'female','inventory':{'cap':1,'cotton_tshirt':1}}
  choices=looks.choices(u,'ru',0);owned=[l for l in choices if l['owned']]
  self.assertEqual({l['group'] for l in owned},{'hats','clothes'})
  self.assertTrue(all(not l['adult'] for l in choices))
