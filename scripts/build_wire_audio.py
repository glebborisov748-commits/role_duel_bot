"""Mechanical connector contact from the existing CC0 switch, plus a short original arc."""
import math,random,wave,array
from build_game_audio import RATE,write,OUT
with wave.open(str(OUT/'unlock.wav')) as recording:
 data=array.array('h',recording.readframes(recording.getnframes()));contact=[n/32768 for n in data]
for number,suffix in enumerate('abc'):
 rng=random.Random(17220+number);duration=.16+number*.012;samples=[]
 for i in range(round(duration*RATE)):
  t=i/RATE;record=contact[min(len(contact)-1,int(i*(1+number*.035)))]*.8
  gate=max(0,1-t/.065)**2;arc=.04*math.sin(2*math.pi*(1800*t-3800*t*t))*gate
  crackle=rng.uniform(-1,1)*.025*gate if t<.018 else 0
  samples.append(record+arc+crackle)
 write('wire'+suffix,samples)
