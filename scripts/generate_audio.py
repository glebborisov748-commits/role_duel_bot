import wave,random,math,struct
from pathlib import Path
random.seed(31);rate=24000

def make(kind,duration):
 n=int(rate*duration);out=[0.]*n
 def burst(start,dur,amp,freq=0,noise=0,decay=6,sweep=0):
  count=int(dur*rate);offset=int(start*rate)
  for j in range(count):
   i=offset+j
   if i>=n:break
   t=j/rate;env=min(1,j/24)*math.exp(-decay*j/count)
   out[i]+=amp*env*(math.sin(2*math.pi*(freq*t+sweep*t*t/2))*(1-noise)+random.uniform(-1,1)*noise)
 if kind=='key':burst(0,.05,.25,1800,.8,12);burst(.012,.06,.15,180,.2,8)
 elif kind=='tick':burst(0,.06,.3,900,.9,14);burst(.005,.08,.18,280,.2,10)
 elif kind=='start':
  for j in range(5):burst(j*.045,.07,.15,250+j*95,.5,10)
 elif kind=='win':
  for j,f in enumerate([523,659,784]):burst(j*.09,.24,.18,f,.03,4)
 elif kind in ('impact','explosion','loss'):
  burst(0,.28,.4,85,.8,6,sweep=-100);burst(.01,.25,.15,65,.1,4)
 elif kind in ('water','soda'):
  for j in range(14):burst(.035*j,.10,.12,280+random.random()*500,.15,5,sweep=-2200)
  if kind=='soda':
   for j in range(120):burst(random.random()*.9,.015,.025+random.random()*.05,1700+random.random()*2000,.85,5)
 elif kind in ('eat','crunch'):
  for j in range(3):
   for k in range(9):burst(j*.23+k*.008,.035,.13,400+random.random()*1500,.95,8)
 elif kind=='drop':burst(0,.16,.18,1100,.03,6,sweep=-4500)
 else:burst(0,.10,.12,660,.02,6);burst(.08,.13,.10,880,.02,6)
 peak=max(max(map(abs,out)),.4);data=b''.join(struct.pack('<h',int(max(-1,min(1,x/peak*.65))*32767)) for x in out)
 with wave.open('assets/audio/'+kind+'.wav','wb') as f:f.setparams((1,2,rate,0,'NONE','not compressed'));f.writeframes(data)
for k,d in [('key',.12),('tick',.12),('start',.35),('win',.6),('impact',.4),('explosion',.4),('loss',.4),('water',.7),('soda',1),('eat',.8),('crunch',.8),('drop',.25),('deliver',.3)]:make(k,d)
