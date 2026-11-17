"""Original short electrical contact: a snap, bright arc fizz and a clean cut-off."""
import math,random
from build_game_audio import RATE,write
for number,suffix in enumerate('abc'):
 rng=random.Random(17110+number);duration=.19+number*.018;low=0.;spark=0.;samples=[]
 for i in range(round(duration*RATE)):
  t=i/RATE;n=rng.uniform(-1,1);low+=.09*(n-low);high=n-low
  if rng.random()<.003:spark=rng.uniform(.15,.38)
  spark*=.77
  envelope=min(1,t/.0015)*max(0,1-t/duration)**1.8
  contact=math.exp(-t*270)*math.sin(2*math.pi*2700*t)*.32
  arc=high*.23*(.65+.35*math.sin(2*math.pi*(170+number*31)*t)**2)
  samples.append((arc+spark)*envelope+contact)
 write('wire'+suffix,samples)
