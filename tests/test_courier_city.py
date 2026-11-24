import copy,json,math,random,unittest
import courier_city as c

class CityTests(unittest.TestCase):
 def setup_run(self):
  self.u={};self.r=c.start(self.u,now=100,rng=random.Random(1));self.r.update(events=[],generated_to=10000);self.r['delivery']['s']=10000;self.now=100
 def step(self,seconds=.5,**controls):
  self.now+=seconds;return c.step(self.u,dict(id=self.r['id'],revision=self.r['revision'],**controls),now=self.now,rng=random.Random(9))
 def test_acceleration_four_lanes_and_no_steering_at_rest(self):
  self.setup_run();self.step(steer=1,target_speed=0);self.assertEqual(self.r['lane'],1)
  self.step(target_speed=40);self.assertGreater(self.r['speed'],0)
  self.step(steer=1);self.step(steer=1);self.assertEqual(self.r['lane'],3)
  self.step(steer=-1);self.step(steer=-1);self.step(steer=-1);self.assertEqual(self.r['lane'],0)
 def test_invalid_controls_are_nonmutating_and_client_distance_is_ignored(self):
  self.setup_run();before=copy.deepcopy(self.u)
  for values in (dict(target_speed=True),dict(target_speed=math.inf),dict(target_speed=61),dict(steer=True),dict(steer=3),dict(brake='yes')):
   with self.assertRaises(c.CourierError):c.step(self.u,dict(id=self.r['id'],revision=0,**values),now=101)
   self.assertEqual(self.u,before)
  self.step(seconds=1000,target_speed=60,distance=100000,tip=999999);self.assertLess(self.r['distance'],2)
 def test_red_stop_line_and_green_restart(self):
  self.setup_run();self.r.update(speed=30,target_speed=30,distance=60);self.r['events']=[dict(id='light',kind='intersection',s=70,offset=0,done=False)]
  money=self.step();self.assertEqual(money['penalty'],80);self.assertLess(self.r['distance'],62);self.assertEqual(self.r['speed'],0)
  self.assertEqual(self.step(target_speed=40)['penalty'],0)
  self.r.update(elapsed=12,speed=30,target_speed=30);self.step();self.assertTrue(self.r['events'][0]['done'])
 def test_pedestrians_yield_but_empty_crossing_is_clear(self):
  for people in (True,False):
   self.setup_run();self.r.update(speed=30,target_speed=30,distance=60);self.r['events']=[dict(id='cross',kind='crossing',s=70,people=people,done=False)]
   money=self.step();self.assertEqual(money['penalty'],60 if people else 0)
   if people:self.assertEqual(self.r['speed'],0)
 def test_hazards_have_different_effects_and_bump_is_safe_slowly(self):
  for kind in ('puddle','bump','barrier','pothole'):
   self.setup_run();self.r.update(speed=40,target_speed=40,distance=68);self.r['events']=[dict(id='hazard',kind=kind,s=70,lane=1,done=False)]
   money=self.step()
   if kind=='puddle':self.assertGreater(self.r['wet_until'],0);self.assertEqual(self.r['integrity'],100);self.assertEqual(money['penalty'],0)
   if kind=='bump':self.assertEqual(self.r['integrity'],88);self.assertLess(self.r['speed'],25);self.assertEqual(money['penalty'],0)
   if kind=='barrier':self.assertEqual(self.r['speed'],0);self.assertEqual(money['penalty'],100)
   if kind=='pothole':self.assertGreater(self.r['steer_until'],0);self.assertGreater(self.r['slow_until'],0)
  self.setup_run();self.r.update(speed=20,target_speed=20,distance=68);self.r['events']=[dict(id='b',kind='bump',s=70,lane=1,done=False)];self.step();self.assertEqual(self.r['integrity'],100)
 def test_wet_braking_is_longer_and_excess_speed_costs_once(self):
  distances=[]
  for wet in (False,True):
   self.setup_run();self.r.update(speed=50,target_speed=50,wet_until=20 if wet else 0);self.step(brake=True);distances.append(self.r['distance'])
  self.assertGreater(distances[1],distances[0])
  self.setup_run();self.r.update(speed=60,target_speed=60,limit=30);penalty=0
  for _ in range(8):penalty+=self.step(target_speed=60)['penalty']
  self.assertEqual(penalty,35)
 def test_delivery_requires_lane_and_stop_and_finances_cannot_replay(self):
  self.setup_run();self.r['delivery'].update(s=0,lane=3,base=220);self.r['distance']=0
  for _ in range(4):self.assertEqual(self.step()['base'],0)
  self.r['lane']=3;first=self.step();self.assertEqual(first['base'],0);revision=self.r['revision'];second=self.step();self.assertEqual(second['base'],220)
  with self.assertRaises(c.CourierError):c.step(self.u,dict(id=self.r['id'],revision=revision),now=self.now+.1)
  self.assertEqual(self.r['delivered'],1);self.assertGreater(self.r['delivery']['s'],300)
 def test_rare_tips_are_server_rolled_and_demo_is_sandbox_only(self):
  class Roll:
   def __init__(self,n):self.n=n
   def random(self):return self.n
  self.assertEqual([c._tip(Roll(v)) for v in (.005,.02,.08,.5)],[400,160,70,0])
  with self.assertRaises(c.CourierError):c.scenario({},'tips',now=100)
  u={'_work_sandbox':True};r=c.scenario(u,'tips',now=100);r.update(distance=70,lane=3,speed=0,target_speed=0,hold=.7)
  money=c.step(u,dict(id=r['id'],revision=0),now=100.5);self.assertEqual(money['tip'],400)
 def test_reload_is_persistent_and_does_not_advance_offline_time(self):
  self.setup_run();self.step(target_speed=40);old_distance=self.r['distance'];u=json.loads(json.dumps(self.u));r=c.start(u,now=999);self.assertEqual(r['distance'],old_distance);self.assertEqual(r['elapsed'],self.r['elapsed']);self.assertNotIn('seed',c.snapshot(u))
 def test_address_lane_not_obstructed_and_course_is_bounded(self):
  u={};r=c.start(u,now=100,rng=random.Random(1))
  for e in r['events']:
   if e.get('lane')==r['delivery']['lane']:self.assertGreaterEqual(abs(e['s']-r['delivery']['s']),30)
  for _ in range(25):r['distance']+=400;c._fill_route(r)
  self.assertLess(len(r['events']),30)
