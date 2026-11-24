import unittest,copy
import farm_upgrade as f
class FertilizerTests(unittest.TestCase):
 def test_purchase_is_single_stock_and_does_not_start_refill(self):
  u={};self.assertTrue(f.grant(u,now=100));self.assertFalse(f.grant(u,now=100000));self.assertTrue(f.snapshot(u,now=100000)['owned']);self.assertEqual(f.snapshot(u,now=100000)['ready_in'],0)
 def test_one_plant_half_time_use_starts_two_hour_refill(self):
  u={};f.grant(u,now=100);p={'crop':'mango','growth_bonus_seconds':0};self.assertEqual(f.apply(u,p,600,now=200),300);self.assertTrue(p['fertilized']);self.assertEqual(f.snapshot(u,now=200)['ready_in'],7200);self.assertFalse(f.grant(u,now=7399));self.assertTrue(f.grant(u,now=7400));self.assertFalse(f.apply(u,p,300,now=7400));self.assertTrue(f.snapshot(u,now=7400)['owned'])
 def test_no_charge_on_empty_ready_already_boosted_or_no_stock(self):
  u={};f.grant(u,now=100)
  for plot,left in [(None,100),({'fertilized':True},100),({},0),({},float('nan'))]:
   before=copy.deepcopy(u);self.assertFalse(f.apply(u,plot,left,now=101));self.assertEqual(u,before)
  self.assertFalse(f.apply({}, {},100,now=100))
 def test_new_crops_are_bounded_and_price_above_all_beds(self):
  self.assertGreater(f.PRICE,1500);self.assertEqual(f.STARS,5)
  for c in f.NEW_CROPS.values():self.assertGreater(c['grow_hours'],0);self.assertLess((c['base_payout']+4*c['water_bonus'])/c['grow_hours'],200)
